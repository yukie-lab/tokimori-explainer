"""Manim scenes for the explainer video (Manim Community Edition 0.22).

Each scene reads the clip lengths in build/timing.json. A beat starts with
self.beat() and ends with self.done(), which waits until the line and a short
pause have played. The real start time of every beat is written to
build/marks/<scene>.json, and tools/assemble.py places the clips there, so the
voice stays in step with the picture even if an animation runs long.

The wormhole, the clocks, the orbits, the curves and the positions of the roots
are drawings. Only the numbers that the narration says, and the numbers written
on the bar charts, come from the paper (Maeda 2026, version 1.0).

Render one scene:  manim render -r 1920,1080 --fps 30 tools/video.py S1
"""
import json
import math
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
TIMING = json.loads((BUILD / "timing.json").read_text(encoding="utf-8"))
GAP = 0.45  # pause after each line, in seconds

config.background_color = "#0e1014"
FONT = "CMU Serif"

C_M1 = "#58C4DD"      # mouth 1 (the slower clock)
C_M2 = "#FF9F43"      # mouth 2
C_THROAT = "#C58AE6"  # the throat
C_OUT = "#A3A9B1"     # the outside
C_FLOW = "#F4D345"    # energy flow, fermions
C_LIGHT = "#FFE9A8"   # light
C_KEY = "#F4D345"     # key statements
C_OK = "#83C167"      # holds / below 1
C_BAD = "#FC6255"     # fails / reaches 1
C_DIM = "#A3A9B1"
C_FAINT = "#5B616A"

TOP = 3.25            # y of scene headings; the bottom of the frame stays free for subtitles

M1 = np.array([-4.0, -0.6, 0.0])   # mouth 1 in the standard drawing
M2 = np.array([4.0, -0.6, 0.0])    # mouth 2


def T(s, size=34, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def M(s, size=34, color=WHITE, **kw):
    return MarkupText(s, font=FONT, font_size=size, color=color, **kw)


def head(s):
    return T(s, 40).move_to([0, TOP, 0])


def glow(point, color, r=0.12, layers=4, spread=0.8, alpha=0.07):
    g = VGroup()
    for i in range(layers, 0, -1):
        g.add(Dot(point, radius=r * (1 + spread * i), color=color, fill_opacity=alpha))
    g.add(Dot(point, radius=r, color=color))
    return g


def note(s):
    """Small grey note in the top right corner (the bottom is kept free for subtitles)."""
    return T(s, 22, C_FAINT).to_corner(UR, buff=0.35)


def check(size=0.35, color=C_OK):
    p = VMobject(color=color, stroke_width=6)
    p.set_points_as_corners([[-0.5, 0, 0], [-0.15, -0.38, 0], [0.55, 0.45, 0]])
    return p.scale(size / 0.9)


def cross(size=0.3, color=C_BAD):
    a = Line([-1, -1, 0], [1, 1, 0], color=color, stroke_width=6)
    b = Line([-1, 1, 0], [1, -1, 0], color=color, stroke_width=6)
    return VGroup(a, b).scale(size / 2)


def box(mob, color=C_DIM, buff=0.22, r=0.12):
    return SurroundingRectangle(mob, color=color, buff=buff, corner_radius=r, stroke_width=2)


# ---------------------------------------------------------------- drawings (not data)

def mouth(p, color, r=0.42):
    g = VGroup()
    for i in range(4, 0, -1):
        g.add(Circle(radius=r * (1 + 0.22 * i), color=color, stroke_width=0, fill_color=color, fill_opacity=0.05))
    g.add(Circle(radius=r, color=color, stroke_width=4, fill_color="#05070a", fill_opacity=1))
    return g.move_to(p)


def throat_path(a=M1, b=M2, height=2.6):
    """The throat: a long arc above the two mouths."""
    mid = (a + b) / 2 + np.array([0, height, 0])
    return VMobject().set_points_smoothly([a + UP * 0.4, a + np.array([0.6, 1.6, 0]), mid,
                                           b + np.array([-0.6, 1.6, 0]), b + UP * 0.4])


def outside_path(a=M1, b=M2):
    return Line(b + LEFT * 0.45, a + RIGHT * 0.45)


def tube(path, color=C_THROAT, width=26, opacity=0.22):
    t = path.copy().set_stroke(color, width=width, opacity=opacity)
    core = path.copy().set_stroke(color, width=3, opacity=0.9)
    return VGroup(t, core)


def wormhole(height=2.6, labels=True):
    """Two mouths, the throat above, the outside below (a drawing)."""
    th = throat_path(height=height)
    g = VGroup()
    g.throat = tube(th)
    g.throat_path = th
    g.out_path = outside_path()
    g.outside = DashedLine(M2 + LEFT * 0.45, M1 + RIGHT * 0.45, color=C_OUT, dash_length=0.12, stroke_width=3)
    g.m1 = mouth(M1, C_M1)
    g.m2 = mouth(M2, C_M2)
    g.add(g.throat, g.outside, g.m1, g.m2)
    if labels:
        g.l1 = T("mouth 1", 26, C_M1).next_to(g.m1, DOWN, buff=0.3)
        g.l2 = T("mouth 2", 26, C_M2).next_to(g.m2, DOWN, buff=0.3)
        g.lt = T("throat", 26, C_THROAT).move_to(th.point_from_proportion(0.5) + UP * 0.45)
        g.lo = T("outside", 26, C_OUT).move_to((M1 + M2) / 2 + DOWN * 0.38)
        g.add(g.l1, g.l2, g.lt, g.lo)
    return g


class Clock(VGroup):
    """A clock face whose hand follows a time tracker at a given rate."""

    def __init__(self, center, tracker, rate=1.0, color=WHITE, r=0.42, **kw):
        super().__init__(**kw)
        self.r = r
        face = Circle(radius=r, color=color, stroke_width=3, fill_color="#05070a", fill_opacity=1).move_to(center)
        ticks = VGroup(*[Line(center + r * 0.78 * np.array([math.sin(a), math.cos(a), 0]),
                              center + r * 0.95 * np.array([math.sin(a), math.cos(a), 0]),
                              color=color, stroke_width=2) for a in np.linspace(0, TAU, 12, endpoint=False)])
        self.face, self.ticks = face, ticks
        self.rate = rate
        self.tracker = tracker
        self.hand = Line(center, center + UP * r * 0.75, color=color, stroke_width=4)
        self.add(face, ticks, self.hand)
        self.hand.add_updater(self._turn)

    def _turn(self, m):
        c = self.face.get_center()
        a = TAU * self.rate * self.tracker.get_value() / 4.0
        m.put_start_and_end_on(c, c + self.r * 0.75 * np.array([math.sin(a), math.cos(a), 0]))


def well(x, depth=1.2, width=1.4, y0=-1.5):
    """A dip that stands for a well of gravity (a drawing)."""
    def f(t):
        xx = x + t * 2.4
        return [xx, y0 - depth * math.exp(-(t * 2.4 / width) ** 2 * 2.2), 0]
    return ParametricFunction(f, t_range=[-1, 1, 0.01], color=C_FAINT, stroke_width=3)


def smooth_step(x):
    x = min(max(x, 0.0), 1.0)
    return x ** 4 * (35 - 84 * x + 70 * x ** 2 - 20 * x ** 3)


def bar_row(values, labels, color, x0, y0, scale, width=0.55, gap=1.25, fmt="{:.3f}", size=24):
    g = VGroup()
    for i, (v, lab) in enumerate(zip(values, labels)):
        x = x0 + i * gap
        b = Rectangle(width=width, height=max(v * scale, 0.02), color=color, fill_color=color, fill_opacity=0.85,
                      stroke_width=0)
        b.move_to([x, y0 + v * scale / 2, 0])
        t = T(fmt.format(v), size, WHITE).next_to(b, UP, buff=0.12)
        l = T(lab, size, C_DIM).move_to([x, y0 - 0.35, 0])
        g.add(VGroup(b, t, l))
    return g


class Beats(Scene):
    SID = None

    def setup(self):
        self.lines = TIMING[self.SID]
        self.k = -1
        self.marks = []
        self._note = None

    def set_note(self, s):
        """Show one small note in the corner; a new note replaces the old one, None removes it."""
        if self._note is not None:
            self.remove(self._note)
            self._note = None
        if s:
            self._note = note(s)
            self.add(self._note)

    def beat(self):
        self.k += 1
        self.t0 = self.renderer.time
        self.marks.append(round(self.t0, 4))

    def done(self, extra=0.0):
        end = self.t0 + self.lines[self.k]["dur"] + GAP + extra
        rem = end - self.renderer.time
        if rem < -0.05:
            print(f"[{self.SID} line {self.lines[self.k]['id']}] picture runs {-rem:.2f} s past the line")
        if rem > 1 / 30:
            self.wait(rem)

    def tear_down(self):
        assert len(self.marks) == len(self.lines), (self.SID, len(self.marks), len(self.lines))
        out = BUILD / "marks"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{self.SID}.json").write_text(
            json.dumps({"marks": self.marks, "end": round(self.renderer.time, 4)}), encoding="utf-8")

    def fade_all(self, run_time=0.6):
        mobs = [m for m in self.mobjects]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        for m in mobs:
            m.clear_updaters()
        self._note = None


# ---------------------------------------------------------------- 1. two mouths and a throat

class S1(Beats):
    SID = "s1"

    def construct(self):
        # Title card (no voice); its middle frame is the poster.
        title = T("Two clocks and a wormhole", 64)
        t2 = VGroup(T("What do quantum fields do when the clocks", 32, C_DIM),
                    T("of its two mouths are pushed apart?", 32, C_DIM)).arrange(DOWN, buff=0.12)
        t2.next_to(title, DOWN, buff=0.35)
        sub = T("A plain-language guide to a 2026 research paper", 26, C_FAINT).next_to(t2, DOWN, buff=0.6)
        card = VGroup(title, t2, sub).move_to(UP * 0.7)
        w0 = wormhole(height=1.2, labels=False).scale(0.55).move_to([0, -2.1, 0])
        self.play(FadeIn(VGroup(title, t2), shift=UP * 0.2), FadeIn(w0), run_time=1.0)
        self.play(FadeIn(sub), run_time=0.6)
        self.wait(1.6)
        self.play(FadeOut(card), FadeOut(w0), run_time=0.6)

        w = wormhole()
        # 1.1 a tunnel with two mouths
        self.beat()
        self.play(FadeIn(w.m1, scale=0.8), FadeIn(w.m2, scale=0.8), FadeIn(w.l1), FadeIn(w.l2), run_time=1.0)
        self.set_note("drawing, not to scale")
        self.done()

        # 1.2 two ways: the throat and the outside
        self.beat()
        self.play(Create(w.throat), FadeIn(w.lt), run_time=1.2)
        self.play(Create(w.outside), FadeIn(w.lo), run_time=0.8)
        d1 = glow(w.throat_path.get_start(), C_LIGHT, r=0.08)
        d2 = glow(M1 + RIGHT * 0.45, C_LIGHT, r=0.08)
        rev_out = Line(M1 + RIGHT * 0.45, M2 + LEFT * 0.45)
        self.play(MoveAlongPath(d1, w.throat_path), MoveAlongPath(d2, rev_out), run_time=2.0, rate_func=linear)
        self.play(FadeOut(d1), FadeOut(d2), run_time=0.3)
        self.done()

        # 1.3 quantum fields hold the throat open
        self.beat()
        shimmer = w.throat_path.copy().set_stroke(C_FLOW, width=8, opacity=0.0)
        self.play(shimmer.animate.set_stroke(opacity=0.55), run_time=0.8)
        qf = T("held open by quantum fields", 28, C_FLOW).move_to([0, 2.95, 0])
        self.play(FadeIn(qf), run_time=0.6)
        self.done()

        # 1.4 the question of three decades
        self.beat()
        scene = VGroup(w, shimmer, qf)
        scene.save_state()
        self.play(scene.animate.fade(0.8), run_time=0.6)
        q1 = T("Do quantum fields stop such a wormhole", 42).move_to([0, 0.9, 0])
        q2 = T("from becoming a time machine?", 42, C_KEY).next_to(q1, DOWN, buff=0.25)
        q3 = T("argued for three decades", 26, C_DIM).next_to(q2, DOWN, buff=0.4)
        self.play(FadeIn(q1, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(q2, shift=UP * 0.15), FadeIn(q3), run_time=0.8)
        self.done()

        # 1.5 the 2026 paper: push the clocks apart
        self.beat()
        self.play(FadeOut(VGroup(q1, q2, q3)), Restore(scene), run_time=0.6)
        self.remove(shimmer)
        tt = ValueTracker(0)
        c1 = Clock(M1 + UP * 1.6 + LEFT * 1.3, tt, rate=0.55, color=C_M1)
        c2 = Clock(M2 + UP * 1.6 + RIGHT * 1.3, tt, rate=1.0, color=C_M2)
        self.play(FadeIn(c1), FadeIn(c2), run_time=0.6)
        self.play(tt.animate.set_value(6), run_time=3.0, rate_func=linear)
        ask = T("A 2026 paper: what do the fields do?", 30, C_KEY).move_to([0, 2.95, 0])
        self.play(FadeOut(qf), FadeIn(ask), run_time=0.6)
        self.done()

        # 1.6 not about whether time travel is possible
        self.beat()
        n1 = T("The paper does not say whether time travel is possible.", 30, C_DIM)
        n2 = T("Everything here is about one model.", 30, C_DIM)
        ng = VGroup(n1, n2).arrange(DOWN, buff=0.15).move_to([0, -2.55, 0])
        self.play(FadeOut(VGroup(w.l1, w.l2, w.lo)), FadeIn(ng), tt.animate.set_value(9), run_time=1.0)
        self.done()
        c1.hand.clear_updaters()
        c2.hand.clear_updaters()
        self.fade_all()


# ---------------------------------------------------------------- 2. two clocks and two margins

class S2(Beats):
    SID = "s2"

    def construct(self):
        h = head("Two clocks and two margins")
        self.play(FadeIn(h), run_time=0.5)
        tt = ValueTracker(0)
        p1, p2 = np.array([-3.2, 0.2, 0]), np.array([3.2, 0.6, 0])

        # 2.1 each mouth has a clock; mouth 1 deeper in a well
        self.beat()
        m1 = mouth(p1, C_M1, r=0.36)
        m2 = mouth(p2, C_M2, r=0.36)
        l1 = T("mouth 1", 24, C_M1).next_to(m1, LEFT, buff=0.3)
        l2 = T("mouth 2", 24, C_M2).next_to(m2, RIGHT, buff=0.3)
        c1 = Clock(p1 + UP * 1.3, tt, rate=0.37, color=C_M1)
        c2 = Clock(p2 + UP * 1.3, tt, rate=1.0, color=C_M2)
        wl = well(p1[0], depth=1.3, y0=-0.9)
        wl_l = T("a well of gravity", 22, C_FAINT).move_to([p1[0], -2.55, 0])
        self.play(FadeIn(m1), FadeIn(m2), FadeIn(l1), FadeIn(l2), run_time=0.7)
        self.play(FadeIn(c1), FadeIn(c2), Create(wl), FadeIn(wl_l), m1.animate.shift(DOWN * 0.35),
                  l1.animate.shift(DOWN * 0.35), run_time=1.0)
        self.set_note("drawing")
        self.done()

        # 2.2 mouth 1's clock runs slower: the drive delta
        self.beat()
        self.play(tt.animate.set_value(4), run_time=2.2, rate_func=linear)
        slow = T("slower", 26, C_M1).next_to(c1, RIGHT, buff=0.3)
        drv = M('the drive, <span fgcolor="#F4D345">δ</span>', 34).move_to([0, 1.9, 0])
        self.play(FadeIn(slow), FadeIn(drv), tt.animate.set_value(5), run_time=0.8, rate_func=linear)
        self.done()

        # 2.3 the rate e^-delta; delta = 1 gives about 0.37
        self.beat()
        f1 = M('rate of clock 1 = e<sup>−δ</sup> × rate of clock 2', 32).move_to([2.3, -1.15, 0])
        f2 = M('δ = 1:  e<sup>−1</sup> ≈ 0.37', 32, C_KEY).next_to(f1, DOWN, buff=0.35)
        self.play(FadeIn(f1), tt.animate.set_value(7), run_time=1.0, rate_func=linear)
        self.play(FadeIn(f2), tt.animate.set_value(8), run_time=0.8, rate_func=linear)
        self.done()

        # 2.4 a time shift builds up; with no push back, at a steady rate
        self.beat()
        for c in (c1, c2):
            c.hand.clear_updaters()
        self.play(FadeOut(VGroup(m1, m2, l1, l2, c1, c2, wl, wl_l, slow, drv, f1, f2)), run_time=0.5)
        self.set_note(None)
        ax = Axes(x_range=[0, 10, 10], y_range=[0, 1, 1], x_length=7.5, y_length=3.6,
                  axis_config={"color": C_DIM, "include_ticks": False, "stroke_width": 2}).move_to([0, 0.0, 0])
        xl = T("time", 24, C_DIM).next_to(ax.x_axis, DOWN, buff=0.2)
        yl = T("time shift between the clocks", 24, C_DIM).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        line = ax.plot(lambda x: 0.09 * x, x_range=[0, 10], color=C_KEY, stroke_width=4)
        lt = T("if nothing pushed back", 26, C_KEY).move_to(ax.c2p(6.3, 0.85))
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
        self.play(Create(line), FadeIn(lt), run_time=1.6, rate_func=linear)
        self.set_note("drawing")
        self.done()
        self.play(FadeOut(VGroup(ax, xl, yl, line, lt)), run_time=0.4)
        self.set_note(None)

        # 2.5 the throat is long: light is slower through the throat
        self.beat()
        w = wormhole()
        self.play(FadeIn(w), run_time=0.7)
        d1 = glow(w.throat_path.get_start(), C_LIGHT, r=0.08)
        d2 = glow(M1 + RIGHT * 0.45, C_LIGHT, r=0.08)
        rev_out = Line(M1 + RIGHT * 0.45, M2 + LEFT * 0.45)
        self.play(MoveAlongPath(d2, rev_out), MoveAlongPath(d1, w.throat_path, rate_func=lambda t: 0.62 * t),
                  run_time=1.6, rate_func=linear)
        self.play(MoveAlongPath(d1, w.throat_path, rate_func=lambda t: 0.62 + 0.38 * t), run_time=1.0,
                  rate_func=linear)
        lng = T("the throat is long", 30, C_THROAT).move_to([0, 2.55, 0])
        self.play(FadeIn(lng), FadeOut(w.lt), run_time=0.5)
        self.done()

        # 2.6 margin A
        self.beat()
        self.play(FadeOut(lng), FadeOut(d1), FadeOut(d2), run_time=0.3)
        tl = NumberLine(x_range=[0, 4, 1], length=4.2, color=C_DIM, include_ticks=False).move_to([0, 0.55, 0])
        tl_l = T("arrival at mouth 2, by its clock", 22, C_DIM).next_to(tl, UP, buff=0.25)
        a_out = Dot(tl.n2p(0.7), color=C_OUT, radius=0.1)
        a_thr = Dot(tl.n2p(3.3), color=C_THROAT, radius=0.1)
        lo = T("outside", 20, C_OUT).next_to(a_out, DOWN, buff=0.18)
        lth = T("throat", 20, C_THROAT).next_to(a_thr, DOWN, buff=0.18)
        brace = BraceBetweenPoints(tl.n2p(0.7), tl.n2p(3.3), direction=UP, color=C_KEY).shift(UP * 0.05)
        al = T("margin A", 28, C_KEY).next_to(tl_l, UP, buff=0.15)
        self.play(FadeIn(tl), FadeIn(tl_l), run_time=0.5)
        self.play(FadeIn(a_out), FadeIn(lo), run_time=0.4)
        self.play(FadeIn(a_thr), FadeIn(lth), run_time=0.4)
        self.play(FadeOut(tl_l), FadeIn(brace), FadeIn(al), run_time=0.6)
        self.done()

        # 2.7 margin B: once around; a time shift makes it shorter in one direction
        self.beat()
        self.play(FadeOut(VGroup(tl, a_out, a_thr, lo, lth, brace, al)), run_time=0.4)
        d = glow(M1 + UP * 0.4, C_LIGHT, r=0.08)
        self.play(MoveAlongPath(d, w.throat_path), run_time=1.3, rate_func=linear)
        back = Line(M2 + LEFT * 0.45, M1 + RIGHT * 0.45)
        self.play(MoveAlongPath(d, back), run_time=0.8, rate_func=linear)
        bl = T("margin B: the time for one loop", 28, C_KEY).move_to([0, 0.75, 0])
        bl2 = T("a time shift makes the loop shorter in one direction", 24, C_DIM).next_to(bl, DOWN, buff=0.2)
        self.play(FadeIn(bl), FadeOut(d), run_time=0.5)
        self.play(FadeIn(bl2), run_time=0.5)
        self.done()

        # 2.8 the threshold for closed null curves
        self.beat()
        self.play(FadeOut(VGroup(bl, bl2)), w.animate.fade(0.75), run_time=0.4)
        t1 = M('A ≤ 0   or   B → 0', 40, C_BAD).move_to([0, 0.9, 0])
        t2 = T("a path of light could close on itself", 28).next_to(t1, DOWN, buff=0.3)
        t3 = T("the model's threshold for closed null curves", 28, C_KEY).next_to(t2, DOWN, buff=0.2)
        self.play(FadeIn(t1), run_time=0.6)
        self.play(FadeIn(t2), run_time=0.5)
        self.play(FadeIn(t3), run_time=0.5)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 3. the model

class S3(Beats):
    SID = "s3"

    def construct(self):
        h = head("The model")
        self.play(FadeIn(h), run_time=0.5)

        # 3.1 Maldacena, Milekhin and Popov (2018)
        self.beat()
        ref = T("a wormhole described by Maldacena, Milekhin and Popov (2018)", 28, C_DIM).move_to([0, 2.55, 0])
        self.play(FadeIn(ref), run_time=0.7)
        self.done()

        # 3.2 two magnetically charged black holes at a distance d
        self.beat()
        b1, b2 = M1 + UP * 0.1, M2 + UP * 0.1
        bh1 = VGroup(Circle(radius=0.55, color=C_M1, stroke_width=3, fill_color="#000000", fill_opacity=1),
                     T("+", 34, C_M1)).move_to(b1)
        bh2 = VGroup(Circle(radius=0.55, color=C_M2, stroke_width=3, fill_color="#000000", fill_opacity=1),
                     T("−", 34, C_M2)).move_to(b2)
        bl = T("black holes with opposite magnetic charges", 24, C_DIM).move_to([0, -2.5, 0])
        darr = DoubleArrow(b1 + RIGHT * 0.65 + DOWN * 1.0, b2 + LEFT * 0.65 + DOWN * 1.0, buff=0, color=C_OUT,
                           stroke_width=3, tip_length=0.2)
        dl = T("d", 30, C_OUT).next_to(darr, DOWN, buff=0.12)
        self.play(FadeIn(bh1, scale=0.8), FadeIn(bh2, scale=0.8), FadeIn(bl), run_time=0.8)
        self.play(GrowFromCenter(darr), FadeIn(dl), run_time=0.7)
        th = throat_path(b1, b2, height=2.2)
        thr = tube(th)
        self.play(Create(thr), run_time=1.2)
        self.set_note("drawing")
        self.done()

        # 3.3 fermions move along field lines that loop through the throat and back outside
        self.beat()
        loops = VGroup()
        for k, (hh, dy) in enumerate(((1.9, 0.0), (2.2, 0.12), (2.5, 0.24))):
            up = throat_path(b1 + UP * dy, b2 + UP * dy, height=hh)
            low = Line(b2 + DOWN * (0.35 + 0.12 * k), b1 + DOWN * (0.35 + 0.12 * k))
            path = VMobject()
            path.append_points(up.points)
            path.add_line_to(low.get_start())
            path.add_line_to(low.get_end())
            path.add_line_to(up.get_start())
            loops.add(path.set_stroke(C_FLOW, width=2, opacity=0.6))
        fl = T("field lines: loops through the throat and back outside", 24, C_FLOW).move_to([0, -2.5, 0])
        self.play(Create(loops), FadeOut(bl), FadeIn(fl), run_time=1.4)
        dots = VGroup(*[Dot(radius=0.06, color=C_FLOW) for _ in range(9)])
        offs = [i / 9 for i in range(9)]
        clock = ValueTracker(0)

        def mover(i):
            def f(m):
                m.move_to(loops[i % 3].point_from_proportion((offs[i] + clock.get_value()) % 1))
            return f
        for i, d in enumerate(dots):
            d.add_updater(mover(i))
        fer = T("charged fermions", 26, C_FLOW).move_to([0, 2.1 + 0.5, 0])
        self.add(dots)
        self.play(FadeOut(ref), FadeIn(fer), clock.animate.set_value(0.35), run_time=1.8, rate_func=linear)
        self.done()

        # 3.4 Casimir energy (negative) holds the throat open
        self.beat()
        cas = M('Casimir energy  <span fgcolor="#FC6255">&lt; 0</span>', 32).move_to([0, 0.8, 0])
        cas2 = T("holds the throat open", 26, C_DIM).next_to(cas, DOWN, buff=0.15)
        self.play(FadeIn(cas), FadeIn(cas2), clock.animate.set_value(0.7), run_time=1.6, rate_func=linear)
        self.done()

        # 3.5 the same fields feel the time shift
        self.beat()
        same = VGroup(T("The same fields feel", 28, C_KEY), T("a time shift between the mouths.", 28, C_KEY))
        same.arrange(DOWN, buff=0.12).move_to([0, 0.75, 0])
        self.play(FadeOut(VGroup(cas, cas2)), FadeIn(same), clock.animate.set_value(1.0), run_time=1.2,
                  rate_func=linear)
        self.done()

        # 3.6 two-dimensional gravity at linear order; loop models R1 and R2
        self.beat()
        for d in dots:
            d.clear_updaters()
        self.play(FadeOut(VGroup(same, dots, loops, fl, fer, darr, dl)), run_time=0.5)
        self.set_note(None)
        g = VGroup(bh1, bh2, thr)
        self.play(g.animate.scale(0.6).move_to([0, 1.3, 0]), run_time=0.6)
        m1 = T("throat: a simple two-dimensional theory of gravity, at linear order", 26).move_to([0, -0.5, 0])
        m2 = T("two models of the loop: R1 and R2", 26, C_DIM).next_to(m1, DOWN, buff=0.3)
        self.play(FadeIn(m1), run_time=0.6)
        self.play(FadeIn(m2), run_time=0.6)
        self.done()

        # 3.7 how the drive is produced is not modelled; switched on smoothly, and off in some runs
        self.beat()
        self.play(FadeOut(VGroup(g, m1, m2)), run_time=0.4)
        ax = Axes(x_range=[0, 10, 10], y_range=[0, 1.2, 1], x_length=8, y_length=2.4,
                  axis_config={"color": C_DIM, "include_ticks": False, "stroke_width": 2}).move_to([0, 0.4, 0])
        on = ax.plot(lambda x: smooth_step(x / 1.5), x_range=[0, 10, 0.02], color=C_KEY, stroke_width=4)
        off = ax.plot(lambda x: smooth_step(x / 1.5) - smooth_step((x - 6.0) / 1.5), x_range=[0, 10, 0.02],
                      color=C_M1, stroke_width=4)
        yl = T("drive δ", 24, C_DIM).next_to(ax, LEFT, buff=0.2)
        xl = T("time", 24, C_DIM).next_to(ax.x_axis, DOWN, buff=0.2)
        lon = T("constant drive", 22, C_KEY).move_to(ax.c2p(8.6, 1.15))
        loff = T("drive stopped", 22, C_M1).move_to(ax.c2p(8.6, 0.25))
        nm = T("How the drive is produced is not modelled.", 28, C_DIM).move_to([0, -2.1, 0])
        self.play(Create(ax), FadeIn(yl), FadeIn(xl), FadeIn(nm), run_time=0.8)
        self.play(Create(on), FadeIn(lon), run_time=1.2)
        self.play(Create(off), FadeIn(loff), run_time=1.2)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 4. the fields push back

class S4(Beats):
    SID = "s4"

    def construct(self):
        h = head("The fields push back")
        self.play(FadeIn(h), run_time=0.5)

        # 4.1 the slow limit
        self.beat()
        sl = T("slow limit: the fields keep up with every change", 28, C_DIM).move_to([0, 2.5, 0])
        self.play(FadeIn(sl), run_time=0.7)
        self.done()

        # 4.2 one way round sees a shorter loop, the other a longer loop
        self.beat()
        c = np.array([-3.6, -0.2, 0])
        loop = Circle(radius=1.35, color=C_FAINT, stroke_width=3).move_to(c)
        a1 = Arc(radius=1.6, start_angle=PI * 0.75, angle=-PI * 0.85, color=C_M2, stroke_width=6).move_arc_center_to(c)
        a1.add_tip(tip_length=0.22)
        a2 = Arc(radius=1.1, start_angle=PI * 0.25, angle=PI * 1.75, color=C_M1, stroke_width=6).move_arc_center_to(c)
        a2.add_tip(tip_length=0.22)
        s1 = M('one way: <span fgcolor="#FF9F43">L − Δ</span>  (shorter)', 26).move_to([-3.6, -2.35, 0])
        s2 = M('other way: <span fgcolor="#58C4DD">L + Δ</span>  (longer)', 26).next_to(s1, DOWN, buff=0.12)
        self.play(Create(loop), run_time=0.5)
        self.play(Create(a1), FadeIn(s1), run_time=0.8)
        self.play(Create(a2), FadeIn(s2), run_time=0.8)
        self.set_note("L: loop length, Δ: time shift")
        self.done()

        # 4.3 the difference of Casimir energies is a steady energy flow through the throat
        self.beat()
        nodes = [("time shift", [1.6, 1.5, 0]), ("energy flow\nthrough the throat", [4.2, 0.2, 0]),
                 ("mass moves\nbetween mouths", [1.6, -1.1, 0]), ("clock rates\nchange", [-0.9, 0.2, 0])]
        boxes = VGroup()
        for i, (s, p) in enumerate(nodes):
            t = T(s, 24, C_FLOW if i == 1 else WHITE, line_spacing=0.8)
            boxes.add(VGroup(box(t, C_FAINT, buff=0.15), t).move_to(p))
        # keep the cycle clear of the loop drawing
        cyc = VGroup(*boxes).shift(RIGHT * 0.9)
        arrows = VGroup(*[CurvedArrow(boxes[i].get_center(), boxes[(i + 1) % 4].get_center(), angle=-PI / 4,
                                      color=C_DIM, stroke_width=3, tip_length=0.18) for i in range(4)])
        for a, i in zip(arrows, range(4)):
            a.scale(0.55)
        self.play(FadeIn(boxes[0]), run_time=0.4)
        self.play(FadeIn(arrows[0]), FadeIn(boxes[1]), run_time=0.7)
        self.done()

        # 4.4 the flow moves mass from one mouth to the other
        self.beat()
        self.play(FadeIn(arrows[1]), FadeIn(boxes[2]), run_time=0.7)
        self.done()

        # 4.5 the clock rates change, against the drive
        self.beat()
        self.play(FadeIn(arrows[2]), FadeIn(boxes[3]), run_time=0.7)
        ag = T("against the drive", 26, C_BAD).next_to(arrows[3], UP + LEFT, buff=0.05)
        self.play(FadeIn(arrows[3]), FadeIn(ag), run_time=0.7)
        self.done()

        # 4.6 one point of balance: e^delta cancels the drive
        self.beat()
        self.play(FadeOut(VGroup(loop, a1, a2, s1, s2, sl, boxes, arrows, ag)), run_time=0.5)
        self.set_note(None)
        beam = Line([-3, 0, 0], [3, 0, 0], color=C_DIM, stroke_width=6).move_to([0, 0.4, 0])
        piv = Triangle(color=C_DIM, fill_color=C_DIM, fill_opacity=1).scale(0.25).next_to(beam, DOWN, buff=0)
        lft = M('drive: e<sup>−δ</sup>', 30, C_M1).next_to(beam.get_left(), UP, buff=0.25)
        rgt = M('throat: e<sup>δ</sup>', 30, C_THROAT).next_to(beam.get_right(), UP, buff=0.25)
        bal = T("one point of balance: they cancel exactly", 30, C_KEY).move_to([0, -1.4, 0])
        self.play(FadeIn(beam), FadeIn(piv), run_time=0.5)
        self.play(FadeIn(lft), FadeIn(rgt), run_time=0.6)
        self.play(FadeIn(bal), run_time=0.6)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 5. no settling

class S5(Beats):
    SID = "s5"

    def construct(self):
        h = head("No settling")
        self.play(FadeIn(h), run_time=0.5)
        ax = Axes(x_range=[-1.5, 1.5, 1], y_range=[-1.2, 1.2, 1], x_length=6.4, y_length=4.6,
                  axis_config={"color": C_FAINT, "include_ticks": False, "stroke_width": 2}).move_to([-2.6, -0.3, 0])
        xl = T("time shift", 22, C_DIM).next_to(ax.x_axis.get_right(), DOWN, buff=0.15)
        yl = T("state of the throat", 22, C_DIM).next_to(ax.y_axis.get_top(), RIGHT, buff=0.15)
        eq = np.array([0.0, 0.45])
        pt = Dot(ax.c2p(*eq), color=C_KEY, radius=0.09)
        pl = T("balance", 22, C_KEY).next_to(pt, RIGHT, buff=0.12)

        def orbit(center, ra, rb):
            return ParametricFunction(lambda t: ax.c2p(center[0] + ra * math.cos(t), center[1] + rb * math.sin(t)),
                                      t_range=[0, TAU], color=C_M2, stroke_width=3)

        # 5.1 swings around the point
        self.beat()
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(pt), FadeIn(pl), run_time=0.7)
        orb = orbit(eq, 1.0, 0.45)
        mover = Dot(color=WHITE, radius=0.08).move_to(orb.get_start())
        self.play(Create(orb), MoveAlongPath(mover, orb), run_time=2.0, rate_func=linear)
        self.play(MoveAlongPath(mover, orb), run_time=1.6, rate_func=linear)
        self.set_note("drawing")
        self.done()

        # 5.2 a ball in a bowl without friction
        self.beat()
        bowl = ParametricFunction(lambda t: [3.6 + t * 2.2, -0.9 + 1.3 * t * t, 0], t_range=[-1, 1, 0.01],
                                  color=C_DIM, stroke_width=4)
        bt = ValueTracker(0)
        ball = Dot(radius=0.14, color=C_M1)

        def roll(m):
            u = 0.8 * math.cos(bt.get_value())
            m.move_to([3.6 + u * 2.2, -0.9 + 1.3 * u * u + 0.14, 0])
        ball.add_updater(roll)
        bl = T("no friction", 22, C_DIM).move_to([3.6, -1.55, 0])
        self.play(Create(bowl), FadeIn(ball), FadeIn(bl), run_time=0.6)
        self.play(bt.animate.set_value(TAU * 1.5), MoveAlongPath(mover, orb), run_time=3.2, rate_func=linear)
        self.done()

        # 5.3 time-reversal; a pure swing
        self.beat()
        r1 = T("same equations when time runs backward", 26).move_to([3.4, 1.8, 0])
        r2 = T("no growth, no decay", 26, C_KEY).next_to(r1, DOWN, buff=0.2)
        self.play(FadeIn(r1), bt.animate.set_value(TAU * 2.0), run_time=1.0, rate_func=linear)
        self.play(FadeIn(r2), bt.animate.set_value(TAU * 2.5), MoveAlongPath(mover, orb), run_time=2.4,
                  rate_func=linear)
        self.done()

        # 5.4 drive switched off: a new closed path that does not come back to the start
        self.beat()
        ball.clear_updaters()
        self.play(FadeOut(VGroup(bowl, ball, bl, r1, r2)), run_time=0.4)
        start = Dot(ax.c2p(0, 0), color=WHITE, radius=0.08)
        st = T("start", 20, C_DIM).next_to(start, DOWN + LEFT, buff=0.05)
        off = T("drive switched off", 24, C_M1).move_to([3.4, 1.4, 0])
        r2 = math.sqrt(2.0)  # the new closed path around the static point passes through (1, 0.45)
        orb2 = ParametricFunction(lambda t: ax.c2p(r2 * math.cos(t + PI / 4), 0.45 * r2 * math.sin(t + PI / 4)),
                                  t_range=[0, TAU], color=C_M1, stroke_width=3)
        self.play(FadeIn(start), FadeIn(st), FadeIn(off), run_time=0.5)
        self.play(Create(orb2), run_time=1.6)
        nr = T("does not return to the start", 24).next_to(off, DOWN, buff=0.2)
        self.play(FadeIn(nr), run_time=0.5)
        self.done()

        # 5.5 caution: the swing is not slow; the limit only finds the mechanism
        self.beat()
        self.play(FadeOut(VGroup(ax, xl, yl, pt, pl, orb, orb2, mover, start, st, off, nr)), run_time=0.5)
        self.set_note(None)
        c1 = T("Caution: the slow limit needs slow changes,", 30, C_DIM).move_to([0, 0.9, 0])
        c2 = T("but the swing itself is not slow.", 30, C_DIM).next_to(c1, DOWN, buff=0.15)
        c3 = T("The paper uses the limit only to find the mechanism.", 30, C_KEY).next_to(c2, DOWN, buff=0.45)
        self.play(FadeIn(VGroup(c1, c2)), run_time=0.7)
        self.play(FadeIn(c3), run_time=0.5)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 6. with the travel time of light

class S6(Beats):
    SID = "s6"

    def construct(self):
        h = head("With the travel time of light")
        self.play(FadeIn(h), run_time=0.5)

        # 6.1 add the crossing time
        self.beat()
        w = wormhole(labels=False).scale(0.7).move_to([0, -0.2, 0])
        self.play(FadeIn(w), run_time=0.5)
        d = glow(w.throat_path.get_start(), C_LIGHT, r=0.07)
        self.play(MoveAlongPath(d, w.throat_path), run_time=1.8, rate_func=linear)
        self.play(FadeOut(d), run_time=0.2)
        self.done()

        # 6.2 modes and roots: off the line grows or dies away
        self.beat()
        self.play(FadeOut(w), run_time=0.4)
        plane = Rectangle(width=6.0, height=5.0, stroke_width=0).move_to([-3.2, -0.2, 0])
        vline = Line(plane.get_top(), plane.get_bottom(), color=WHITE, stroke_width=3)
        hline = Line(plane.get_left(), plane.get_right(), color=C_FAINT, stroke_width=2)
        left = T("dies away", 24, C_OK).move_to(plane.get_center() + LEFT * 1.9 + UP * 2.0)
        right = T("grows", 24, C_BAD).move_to(plane.get_center() + RIGHT * 1.9 + UP * 2.0)
        self.play(Create(vline), Create(hline), FadeIn(left), FadeIn(right), run_time=0.8)
        c0 = plane.get_center()
        sample = VGroup(Dot(c0 + np.array([-1.6, 1.0, 0]), color=C_OK, radius=0.09),
                        Dot(c0 + np.array([1.4, -0.8, 0]), color=C_BAD, radius=0.09))
        each = T("each dot: one root", 24, C_DIM).move_to([3.7, 0.3, 0])
        self.play(FadeIn(sample), FadeIn(each), run_time=0.5)
        self.set_note("drawing")
        self.done()

        # 6.3 28 roots in each of 12 cases, all on the line; three from the method
        self.beat()
        self.play(FadeOut(sample), FadeOut(left), FadeOut(right), FadeOut(each), run_time=0.3)
        ys = np.linspace(-2.25, 2.25, 25)
        roots = VGroup(*[Dot(c0 + np.array([0, y, 0]), color=C_KEY, radius=0.065) for y in ys])
        art = VGroup(*[Dot(c0 + np.array([0, y, 0]), color=C_FAINT, radius=0.1) for y in (0.0, 0.52, -0.52)])
        for a in art:
            a.set_fill(opacity=0).set_stroke(C_DIM, width=3)
        self.play(LaggedStart(*[FadeIn(r, scale=0.5) for r in roots], lag_ratio=0.05), run_time=1.6)
        self.play(FadeIn(art), run_time=0.5)
        t1 = T("28 roots in each of 12 cases:", 28).move_to([3.7, 1.6, 0])
        t2 = T("all exactly on the line", 28, C_KEY).next_to(t1, DOWN, buff=0.15)
        t3 = T("○  3 come from the method itself", 24, C_DIM).next_to(t2, DOWN, buff=0.35)
        self.play(FadeIn(t1), FadeIn(t2), run_time=0.6)
        self.play(FadeIn(t3), run_time=0.5)
        self.done()

        # 6.4 exact checks; no counted mode decays or grows
        self.beat()
        ck = check()
        e1 = T("exact checks (interval arithmetic)", 24)
        VGroup(ck, e1).arrange(RIGHT, buff=0.2).move_to([3.7, -0.5, 0])
        e2 = T("no counted mode decays or grows", 28, C_KEY).move_to([3.7, -1.15, 0])
        self.play(Create(ck), FadeIn(e1), run_time=0.7)
        self.play(FadeIn(e2), run_time=0.5)
        self.done()

        # 6.5 after the drive stops: the slow swing goes to the boost root
        self.beat()
        self.play(FadeOut(VGroup(t1, t2, t3, ck, e1, e2)), run_time=0.4)
        b = Circle(radius=0.2, color=C_M1, stroke_width=4).move_to(art[1])
        bt1 = T("after the drive stops:", 26, C_DIM).move_to([3.7, 1.3, 0])
        bt2 = T("the slow swing → a boost", 30, C_M1).next_to(bt1, DOWN, buff=0.2)
        bt3 = T("(a change of viewpoint inside the throat)", 24, C_DIM).next_to(bt2, DOWN, buff=0.15)
        path = Arrow(c0 + np.array([0.9, 1.6, 0]), b.get_center() + RIGHT * 0.22, color=C_M1, buff=0.05,
                     stroke_width=3, tip_length=0.18)
        self.play(Create(b), GrowArrow(path), FadeIn(bt1), run_time=0.7)
        self.play(FadeIn(bt2), FadeIn(bt3), run_time=0.6)
        self.done()

        # 6.6 not claimed as a physical mode
        self.beat()
        nc = T("not claimed as a physical mode", 30, C_KEY).next_to(bt3, DOWN, buff=0.45)
        self.play(FadeIn(nc), run_time=0.6)
        self.done()
        self.play(FadeOut(VGroup(vline, hline, roots, art, b, path, bt1, bt2, bt3, nc)), run_time=0.5)
        self.set_note(None)

        # 6.7 the full equations: drives 0.001, 0.01, 0.1; 18 runs
        self.beat()
        ax = Axes(x_range=[0, 10, 10], y_range=[0, 0.6, 1], x_length=9.0, y_length=1.9,
                  axis_config={"color": C_DIM, "include_ticks": False, "stroke_width": 2}).move_to([0, 1.15, 0])
        rng = np.random.default_rng(5)
        jit = rng.uniform(0.6, 1.0, 400)

        def shift(x):
            # a drawing of |time shift| / δ: a peak while switching on and off, a small swing after
            base = 0.035 + 0.02 * math.sin(7.0 * x) * jit[int(x * 39) % 400]
            peak = 0.42 * math.exp(-((x - 0.25) / 0.18) ** 2) + 0.42 * math.exp(-((x - 3.2) / 0.18) ** 2)
            return abs(base) + peak
        cur = ax.plot(shift, x_range=[0, 10, 0.01], color=C_M2, stroke_width=2.5)
        yl = T("|time shift| ÷ δ", 22, C_DIM).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        dr = T("drives 0.001, 0.01, 0.1  ·  18 runs", 26).next_to(ax, UP, buff=0.1).align_to(ax, RIGHT)
        half = DashedLine(ax.c2p(0, 0.5), ax.c2p(10, 0.5), color=C_FAINT, stroke_width=2)
        hl = T("0.5", 20, C_FAINT).next_to(half, RIGHT, buff=0.15)
        self.play(FadeIn(dr), Create(ax), FadeIn(yl), Create(half), FadeIn(hl), run_time=0.7)
        self.play(Create(cur), run_time=2.2, rate_func=linear)
        self.set_note("drawing")
        self.done()

        # 6.8 margins stay positive for 50 swings
        self.beat()
        ax2 = Axes(x_range=[0, 10, 10], y_range=[0, 4, 4], x_length=9.0, y_length=1.6,
                   axis_config={"color": C_DIM, "include_ticks": False, "stroke_width": 2}).move_to([0, -1.0, 0])
        ca = ax2.plot(lambda x: 3.0 - 0.04 * math.sin(5 * x), x_range=[0, 10, 0.02], color=C_KEY, stroke_width=3)
        cb = ax2.plot(lambda x: 2.1 + 0.04 * math.cos(5 * x), x_range=[0, 10, 0.02], color=C_LIGHT, stroke_width=3)
        la = T("A", 24, C_KEY).next_to(ca, LEFT, buff=0.15)
        lb = T("B", 24, C_LIGHT).next_to(cb, LEFT, buff=0.15)
        z = DashedLine(ax2.c2p(0, 0), ax2.c2p(10, 0), color=C_BAD, stroke_width=2)
        zl = T("0", 22, C_BAD).next_to(z, LEFT, buff=0.15)
        pos = T("both stay positive for 50 swings", 26, C_OK).next_to(ax2, DOWN, buff=0.2)
        self.play(Create(ax2), Create(z), FadeIn(zl), run_time=0.5)
        self.play(Create(ca), Create(cb), FadeIn(la), FadeIn(lb), run_time=1.4)
        self.play(FadeIn(pos), run_time=0.4)
        self.done()

        # 6.9 at most 0.4-0.5 times delta, while switching; a swing remains
        self.beat()
        pk = T("at most 0.4–0.5 × δ, while switching", 22, C_M2)
        pk.move_to(ax.c2p(4.2, 0.4), aligned_edge=LEFT)
        ar1 = Arrow(pk.get_left(), ax.c2p(3.3, 0.44), color=C_M2, buff=0.08, stroke_width=3, tip_length=0.14)
        rm = T("a swing remains", 22, C_M2).move_to(ax.c2p(7.8, 0.2))
        self.play(FadeIn(pk), GrowArrow(ar1), run_time=0.6)
        self.play(FadeIn(rm), run_time=0.5)
        self.done()

        # 6.10 for the two smallest drives this says little
        self.beat()
        self.play(FadeOut(VGroup(ax, cur, yl, pk, ar1, rm, ax2, ca, cb, la, lb, z, zl, pos, dr, half, hl)), run_time=0.5)
        self.set_note(None)
        w1 = T("For the two smallest drives, this says little:", 30, C_KEY).move_to([0, 0.8, 0])
        w2 = T("even with no push back, the shift would not reach", 28).next_to(w1, DOWN, buff=0.35)
        w3 = T("the threshold in the same time (in all but one case).", 28).next_to(w2, DOWN, buff=0.12)
        self.play(FadeIn(w1), run_time=0.6)
        self.play(FadeIn(VGroup(w2, w3)), run_time=0.6)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 7. larger drives

class S7(Beats):
    SID = "s7"

    def construct(self):
        h = head("Larger drives")
        self.play(FadeIn(h), run_time=0.5)

        # 7.1 drives 0.2, 0.3, 0.6 and 1; 48 runs
        self.beat()
        nl = NumberLine(x_range=[0, 1, 0.1], length=9, color=C_DIM, include_numbers=False).move_to([0, 2.0, 0])
        ticks = VGroup()
        for v in (0.2, 0.3, 0.6, 1.0):
            d = Dot(nl.n2p(v), color=C_KEY, radius=0.1)
            ticks.add(VGroup(d, T(f"{v:g}", 24, C_KEY).next_to(d, UP, buff=0.15)))
        dl = T("drive δ", 22, C_DIM).next_to(nl, LEFT, buff=0.3)
        n48 = T("48 more runs", 26, C_DIM).next_to(nl, DOWN, buff=0.35)
        self.play(Create(nl), FadeIn(dl), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in ticks], lag_ratio=0.25), FadeIn(n48), run_time=1.2)
        self.done()

        # 7.2 smallest margins: A 1.16, B 2.03
        self.beat()
        self.play(FadeOut(n48), run_time=0.3)
        base = -1.6
        zero = Line([-5.6, base, 0], [-1.0, base, 0], color=C_BAD, stroke_width=3)
        zl = T("0", 22, C_BAD).next_to(zero, LEFT, buff=0.15)
        bars = bar_row([1.16, 2.03], ["A", "B"], C_OK, -4.3, base, 0.8, width=0.8, gap=1.8, fmt="{:.2f}", size=26)
        cap = T("smallest values, in the windows fixed in advance", 22, C_DIM).move_to([-3.3, base - 0.85, 0])
        self.play(Create(zero), FadeIn(zl), run_time=0.4)
        self.play(LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in bars], lag_ratio=0.3),
                  *[FadeIn(b[1:]) for b in bars], FadeIn(cap), run_time=1.0)
        self.done()

        # 7.3 the threshold is not reached within these runs
        self.beat()
        ok = VGroup(check(), T("threshold not reached", 28, C_OK)).arrange(RIGHT, buff=0.2)
        ok2 = T("within these runs", 24, C_DIM).next_to(ok, DOWN, buff=0.12)
        VGroup(ok, ok2).move_to([-3.3, 0.95, 0])
        self.play(Create(ok[0]), FadeIn(ok[1]), FadeIn(ok2), run_time=0.7)
        self.done()

        # 7.4 the largest time shift: 0.099, 0.148, 0.277, 0.421
        self.beat()
        base2 = -1.6
        ax0 = Line([0.6, base2, 0], [6.4, base2, 0], color=C_DIM, stroke_width=2)
        bars2 = bar_row([0.099, 0.148, 0.277, 0.421], ["0.2", "0.3", "0.6", "1"], C_M2, 1.3, base2, 5.0,
                        width=0.6, gap=1.45, fmt="{:.3f}", size=22)
        t = T("largest time shift", 24, C_M2).move_to([3.5, 1.15, 0])
        xd = T("drive δ", 20, C_DIM).move_to([3.5, base2 - 0.75, 0])
        self.play(FadeIn(ax0), FadeIn(t), FadeIn(xd), run_time=0.4)
        self.play(LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in bars2], lag_ratio=0.25),
                  *[FadeIn(b[1:]) for b in bars2], run_time=1.4)
        self.done()

        # 7.5 two runs stopped early at a numerical limit
        self.beat()
        s1 = T("Two runs stopped early, at a numerical limit of the time steps.", 26, C_DIM)
        s2 = T("Nothing is said about them after that point.", 26, C_DIM)
        VGroup(s1, s2).arrange(DOWN, buff=0.12).move_to([0, 2.15, 0])
        self.play(FadeOut(VGroup(nl, ticks, dl)), run_time=0.4)
        self.play(FadeIn(VGroup(s1, s2)), run_time=0.7)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 8. is the description still valid?

class S8(Beats):
    SID = "s8"

    def construct(self):
        h = head("Is the description still valid?")
        self.play(FadeIn(h), run_time=0.5)
        lo, hi = 0.03, 3.0
        x0, x1, y = -5.2, 5.2, 0.9

        def X(v):
            return x0 + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)

        # 8.1 ratios; 0.1 holds, 1 fails
        self.beat()
        axis = Line([x0, y, 0], [x1, y, 0], color=C_DIM, stroke_width=2)
        band = Rectangle(width=X(1) - X(0.1), height=1.6, stroke_width=0, fill_color=C_DIM,
                         fill_opacity=0.14).move_to([(X(1) + X(0.1)) / 2, y + 0.6, 0])
        l01 = Line([X(0.1), y - 0.1, 0], [X(0.1), y + 1.4, 0], color=C_OK, stroke_width=3)
        l1 = DashedLine([X(1), y - 0.1, 0], [X(1), y + 1.4, 0], color=C_BAD, stroke_width=3)
        t01 = T("0.1", 24, C_OK).next_to(l01, DOWN, buff=0.15)
        t1 = T("1", 24, C_BAD).next_to(l1, DOWN, buff=0.15)
        hold = T("holds", 24, C_OK).move_to([(x0 + X(0.1)) / 2, y + 1.65, 0])
        fail = T("fails", 24, C_BAD).move_to([(X(1) + x1) / 2, y + 1.65, 0])
        bandl = T("band", 22, C_DIM).move_to([(X(1) + X(0.1)) / 2, y + 1.65, 0])
        ratio = T("a ratio that must stay small (log scale)", 22, C_DIM).move_to([0, y - 0.75, 0])
        self.play(Create(axis), FadeIn(ratio), run_time=0.5)
        self.play(Create(l01), Create(l1), FadeIn(t01), FadeIn(t1), FadeIn(band), run_time=0.8)
        self.play(FadeIn(hold), FadeIn(fail), FadeIn(bandl), run_time=0.5)
        self.done()

        # 8.2 conventions, not physical thresholds
        self.beat()
        cv = T("conventions fixed before the computation, not physical thresholds", 24, C_KEY).move_to([0, 2.65, 0])
        self.play(FadeIn(cv), run_time=0.6)
        self.done()

        # 8.3 at delta = 1, S8 reaches 1 in five of six cases
        self.beat()
        self.play(FadeOut(cv), run_time=0.3)
        yy = y + 0.3
        s8 = Line([X(0.97), yy, 0], [X(1.77), yy, 0], color=C_DIM, stroke_width=10)
        s8l = VGroup(T("S8 at δ = 1:", 24, C_DIM), T("0.97 – 1.77", 24, C_DIM)).arrange(DOWN, buff=0.08,
                                                                                           aligned_edge=LEFT)
        s8l.move_to([X(1) + 0.25, y + 1.05, 0], aligned_edge=LEFT)
        s8x = cross(0.25).next_to(s8, RIGHT, buff=0.2)
        self.play(Create(s8), FadeIn(s8l), run_time=0.8)
        self.play(Create(s8x), run_time=0.4)
        self.done()

        # 8.4 S8 depends on the labelling; a boost can change it
        self.beat()
        dep = T("S8 depends on how the throat is labelled: a boost changes it", 24, C_DIM).move_to([0, -1.5, 0])
        self.play(FadeIn(dep), s8.animate.shift(LEFT * 0.6), run_time=0.8)
        self.play(s8.animate.shift(RIGHT * 0.6), run_time=0.6)
        self.done()

        # 8.5 new ratios from each mouth's own clock; a boost does not change them
        self.beat()
        nw = T("new ratios S5*, S8*, S9*: from what each mouth measures with its own clock", 24, C_OK)
        nw.move_to([0, -2.1, 0])
        nb = T("a boost does not change them", 24, C_OK).next_to(nw, DOWN, buff=0.12)
        self.play(FadeOut(dep), FadeIn(nw), FadeIn(nb), run_time=0.7)
        self.done()

        # 8.6 at delta = 1 the largest is 0.666
        self.beat()
        vals = [(0.517, "S5*"), (0.666, "S8*"), (0.343, "S9*")]
        dots = VGroup()
        for i, (v, lab) in enumerate(vals):
            d = Dot([X(v), y + 0.05 + 0.0 * i, 0], color=C_OK, radius=0.1)
            dots.add(d)
        best = T("0.666", 26, C_OK).next_to(dots[1], UP, buff=0.55)
        arr = Arrow(best.get_bottom(), dots[1].get_top(), buff=0.05, color=C_OK, stroke_width=3, tip_length=0.15)
        dl = VGroup(*[T(lab, 20, C_OK).next_to(d, DOWN, buff=0.22) for d, (v, lab) in zip(dots, vals)])
        self.play(FadeIn(dots), run_time=0.6)
        self.play(FadeIn(best), GrowArrow(arr), FadeIn(dl), run_time=0.6)
        self.done()

        # 8.7 only S2 and S3 reach 1: fixed by the number of fermions and the coupling
        self.beat()
        self.play(FadeOut(VGroup(nw, nb, s8, s8l, s8x)), run_time=0.4)
        f1 = T("A value of 1 comes only from S2 and S3:", 26).move_to([0, -1.75, 0])
        f2 = T("fixed before any drive, by the number of fermions and the coupling", 24, C_DIM)
        f2.next_to(f1, DOWN, buff=0.15)
        self.play(FadeIn(f1), run_time=0.6)
        self.play(FadeIn(f2), run_time=0.6)
        self.done()

        # 8.8 most cases undecided within the band; none reached "stops" or "does not stop"
        self.beat()
        self.play(FadeOut(VGroup(axis, band, l01, l1, t01, t1, hold, fail, bandl, ratio, dots, best, arr, dl,
                                 f1, f2)), run_time=0.5)
        rows = [("undecided within the band", "27 of 42 rows", C_DIM),
                ("not decidable semiclassically (S2 or S3 ≥ 1)", "15 of 42 rows", C_BAD),
                ("“stops” or “does not stop”", "none", C_KEY)]
        g = VGroup()
        for i, (a, b, col) in enumerate(rows):
            ta = T(a, 26).move_to([-5.6, 1.4 - i * 0.9, 0], aligned_edge=LEFT)
            tb = T(b, 26, col).move_to([4.2, 1.4 - i * 0.9, 0], aligned_edge=LEFT)
            g.add(VGroup(ta, tb))
        cap = T("verdicts at the drives 0.2 to 1, with the new ratios", 22, C_DIM).move_to([0, 2.4, 0])
        self.play(FadeIn(cap), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in g], lag_ratio=0.35), run_time=1.6)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 9. what the paper does not claim

class S9(Beats):
    SID = "s9"

    def construct(self):
        h = head("What the paper does not claim")
        self.add(h)
        texts = [
            ("No statement on whether time travel is possible,", "or whether the chronology protection conjecture holds."),
            ("All statements hold in one model,", "for the loops, drives and run windows that were computed."),
            ("Effects outside the model, such as radiation from the mouths,", "could take energy from the swing."),
            ("The lines 0.1 and 1 are conventions;", "the new ratios are one choice, not the only correct one."),
        ]
        rows = VGroup()
        for i, (a, b) in enumerate(texts):
            yv = 2.15 - i * 1.12
            ta = T(a, 27).move_to([-5.9, yv, 0], aligned_edge=LEFT)
            tb = T(b, 27, C_DIM).next_to(ta, DOWN, buff=0.08, aligned_edge=LEFT)
            dot = Dot([-6.3, yv, 0], radius=0.07, color=C_KEY)
            rows.add(VGroup(dot, ta, tb))
        for i in range(4):
            self.beat()
            self.play(FadeIn(rows[i], shift=RIGHT * 0.2), run_time=0.7)
            self.done()

        # 9.5 read the paper
        self.beat()
        self.play(FadeOut(rows), FadeOut(h), run_time=0.5)
        c1 = T("Maeda, Y. (2026). Response of a quantum-supported traversable wormhole", 26)
        c2 = T("to a driven time shift between its mouths (Version 1.0). Zenodo.", 26)
        c4 = T("doi:10.5281/zenodo.23917339", 32, C_KEY)
        cite = VGroup(c1, c2).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([0, 1.2, 0])
        c4.next_to(cite, DOWN, buff=0.45)
        self.play(FadeIn(cite), run_time=0.8)
        self.play(FadeIn(c4), run_time=0.5)
        self.done()

        # 9.6 made with AI, synthetic voice
        self.beat()
        e1 = T("Made with the help of AI. The voice is synthetic (Kokoro-82M).", 24, C_DIM)
        e2 = T("Animation: Manim Community Edition.  License: CC BY 4.0.", 24, C_DIM)
        end = VGroup(e1, e2).arrange(DOWN, buff=0.15).move_to([0, -1.0, 0])
        self.play(FadeIn(end), run_time=0.7)
        self.done(extra=1.2)
        self.fade_all(0.8)
