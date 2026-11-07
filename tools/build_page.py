"""Build index.html from tools/page.html: draw the figures, write the video transcript, fill the placeholders.

Usage: python tools/build_page.py
Reads tools/page.html, tools/narration.json and assets/video/chapters.json. Writes index.html at the site root.
Every figure has its English and Japanese labels side by side; the page shows one language at a time.
The numbers in Figures 6, 7 and 8 are the paper's (Maeda 2026, version 1.0: Sections IV and V and Table I).
Figures 1 to 5 are drawings; no position or length in them is a computed value.
"""
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
W = 640  # width of every figure in SVG units


def esc(s):
    return html.escape(s, quote=True)


def t2(x, y, en, ja, cls="", anchor="start"):
    """One label in two languages: two text elements at the same place."""
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}"{a}{c} data-l="en" lang="en">{en}</text>'
            f'<text x="{x:.1f}" y="{y:.1f}"{a}{c} data-l="ja" lang="ja">{ja}</text>')


def tip(en, ja):
    """Hover text. site.js swaps it when the language changes."""
    return f'<title data-en="{esc(en)}" data-ja="{esc(ja)}">{esc(en)}</title>'


def figure(num, h, body, cap_en, cap_ja, aria_en, aria_ja):
    return (f'<figure class="fig">\n<div class="fig-scroll"><svg viewBox="0 0 {W} {h}" role="img" '
            f'aria-label="{esc(aria_en)}" data-aria-en="{esc(aria_en)}" data-aria-ja="{esc(aria_ja)}">'
            f'{body}</svg></div>\n<figcaption><span data-l="en" lang="en"><span class="fignum">Figure {num}.</span>'
            f'{cap_en}</span><span data-l="ja" lang="ja"><span class="fignum">図 {num}</span>'
            f'{cap_ja}</span></figcaption>\n</figure>')


def arrowhead(x, y, ang, size=7, cls="head"):
    """A small filled triangle pointing in direction ang (radians, SVG coordinates)."""
    p = [(x, y),
         (x - size * math.cos(ang) + size * 0.55 * math.sin(ang), y - size * math.sin(ang) - size * 0.55 * math.cos(ang)),
         (x - size * math.cos(ang) - size * 0.55 * math.sin(ang), y - size * math.sin(ang) + size * 0.55 * math.cos(ang))]
    return f'<path class="{cls}" d="M{p[0][0]:.1f},{p[0][1]:.1f} L{p[1][0]:.1f},{p[1][1]:.1f} L{p[2][0]:.1f},{p[2][1]:.1f} Z"/>'


# ---------------------------------------------------------------- Figure 1: the model

def fig_model():
    s = []
    x1, x2, y = 130, 510, 172
    s.append(f'<path class="throat-band" d="M{x1},{y - 24} C{x1},40 {x2},40 {x2},{y - 24}"/>')
    s.append(f'<path class="throat-core" d="M{x1},{y - 24} C{x1},40 {x2},40 {x2},{y - 24}"/>')
    s.append(f'<path class="loop" d="M{x1 + 12},{y - 22} C{x1 + 16},62 {x2 - 16},62 {x2 - 12},{y - 22}"/>')
    s.append(f'<path class="loop" d="M{x2 - 12},{y + 20} H{x1 + 12}"/>')
    s.append(arrowhead(322, 84.5, 0.0, 8, "head-flow"))
    s.append(arrowhead(318, y + 20, math.pi, 8, "head-flow"))
    s.append(f'<path class="outside" d="M{x1 + 24},{y} H{x2 - 24}"/>')
    s.append(f'<circle class="m1" cx="{x1}" cy="{y}" r="22"/>')
    s.append(f'<circle class="m2" cx="{x2}" cy="{y}" r="22"/>')
    s.append(t2(x1, y + 44, "mouth 1", "口 1", "ink bold", "middle"))
    s.append(t2(x2, y + 44, "mouth 2", "口 2", "ink bold", "middle"))
    s.append(t2(320, 30, "throat (long)", "のど(長い)", "ink bold", "middle"))
    s.append(t2(320, 108, "loop of q charged fermions", "q 個の電荷を持つフェルミオンの輪", "flow-t", "middle"))
    s.append(t2(320, 126, "(their Casimir energy holds the throat open)", "(そのカシミールエネルギーがのどを開く)",
                "small", "middle"))
    s.append(t2(320, y - 8, "outside, distance d", "外、距離 d", "", "middle"))
    s.append(t2(320, 246, "drive δ: the clock of mouth 1 runs at e<tspan class=\"sup\" dy=\"-5\">−δ</tspan><tspan dy=\"5\"> </tspan>times the rate of mouth 2",
                "駆動 δ: 口 1 の時計は、口 2 の e<tspan class=\"sup\" dy=\"-5\">−δ</tspan><tspan dy=\"5\"> </tspan>倍の速さで進む", "small", "middle"))
    return figure(
        1, 260, "".join(s),
        "The model (a drawing, no values; after the paper's Figure 1). Two mouths are joined by the throat and by "
        "the outside, at a distance d. Loops of q charged fermions run through the throat and back outside. Their "
        "Casimir energy holds the throat open. The drive δ makes the clock of mouth 1 run slower than the clock of "
        "mouth 2.",
        "モデル(絵で、値はありません。論文の図 1 にならいました)。二つの口は、のどと、距離 d の外でつながっています。"
        "q 個の電荷を持つフェルミオンの輪が、のどを通って外を戻ります。そのカシミールエネルギーが、のどを開いています。"
        "駆動 δ は、口 1 の時計を、口 2 の時計より遅く進ませます。",
        "Drawing: two circles, mouth 1 and mouth 2, joined by a long arc above, the throat, and a dashed line below, "
        "the outside at distance d. A loop of fermions runs through the arc and back along the line. The drive delta "
        "makes the clock of mouth 1 slower.",
        "図: 二つの円(口 1 と口 2)が、上の長い弧(のど)と、下の破線(距離 d の外)でつながる。フェルミオンの輪が弧を通り、"
        "線に沿って戻る。駆動 δ が口 1 の時計を遅くする。")


# ---------------------------------------------------------------- Figure 2: the two margins

def fig_margins():
    s = []
    # margin A
    s.append(t2(30, 28, "Margin A", "ゆとり A", "ink bold"))
    s.append('<path class="axis" d="M40,112 H290"/>')
    s.append(arrowhead(296, 112, 0.0, 7, "head-axis"))
    s.append(t2(40, 136, "arrival time at mouth 2, by its own clock", "口 2 に着く時刻(口 2 の時計で)", "small"))
    s.append('<circle class="dot-out" cx="90" cy="112" r="6"/>')
    s.append('<circle class="dot-thr" cx="240" cy="112" r="6"/>')
    s.append(t2(90, 98, "via the outside", "外を通る光", "small", "middle"))
    s.append(t2(240, 98, "via the throat", "のどを通る光", "small", "middle"))
    s.append('<path class="brace" d="M90,72 V64 H240 V72"/>')
    s.append(t2(165, 56, "A", "A", "ink bold", "middle"))
    s.append(t2(40, 168, "In this model A > 0: the throat is slower.", "このモデルでは A > 0。のどの方が遅い。", ""))
    # margin B
    cx, cy = 480, 96
    s.append(t2(350, 28, "Margin B", "ゆとり B", "ink bold"))
    s.append(f'<ellipse class="arc-m1" cx="{cx}" cy="{cy}" rx="112" ry="46"/>')
    s.append(arrowhead(cx - 4, cy - 46, math.pi, 8, "head-m1"))
    s.append(f'<ellipse class="arc-m2" cx="{cx}" cy="{cy}" rx="84" ry="28"/>')
    s.append(arrowhead(cx + 4, cy - 28, 0.0, 8, "head-m2"))
    s.append(t2(cx, cy + 4, "throat + outside", "のど + 外", "small", "middle"))
    s.append(t2(350, 166, "one way round: L − Δ (shorter)", "一方の向き: L − Δ(短い)", "small m2t"))
    s.append(t2(350, 184, "other way round: L + Δ (longer)", "逆の向き: L + Δ(長い)", "small m1t"))
    s.append(t2(350, 210, "B = the shorter loop time, L − |Δ|", "B = 短い方のひと回りの時間、L − |Δ|", ""))
    s.append(t2(350, 228, "(L: loop length, Δ: time shift)", "(L: 輪の長さ、Δ: 時間のずれ)", "small"))
    s.append('<path class="rule" d="M20,250 H620"/>')
    s.append(t2(320, 276, "If A ≤ 0 or B → 0, a path of light could close on itself:",
                "A ≤ 0 か B → 0 になると、光の道が自分自身に閉じうる。", "ink", "middle"))
    s.append(t2(320, 296, "the model's threshold for closed null curves.", "これがモデルの「閉じた光的曲線のしきい」。",
                "ink bold", "middle"))
    return figure(
        2, 310, "".join(s),
        "The two margins that the paper watches (a drawing). Margin A: how much later light arrives at a mouth "
        "through the throat than through the outside, by the clocks of the mouths (the smaller of the two "
        "directions). Margin B: the shorter of the two times that light needs to go once around the loop. A time "
        "shift Δ makes one of them shorter.",
        "論文が見張る二つのゆとり(絵)。ゆとり A: 口の時計で測って、のどを通った光が、外を通った光よりどれだけ遅れて口に着くか"
        "(二つの向きのうち小さい方)。ゆとり B: 光が輪をひと回りする二つの時間のうち、短い方。時間のずれ Δ は、その一方を短くします。",
        "Left: a time line at mouth 2 with two dots, light via the outside first and light via the throat later; the "
        "gap is margin A. Right: a loop with two arrows, one way L minus delta, shorter, and the other way L plus "
        "delta, longer; B is the shorter time. Bottom: if A is at most zero or B goes to zero, a path of light could "
        "close on itself.",
        "左: 口 2 の時刻の線に二つの点。外を通る光が先に、のどを通る光が後に着く。その差がゆとり A。右: 二つの矢印のある輪。"
        "一方の向きは L − Δ で短く、逆の向きは L + Δ で長い。B は短い方の時間。下: A ≤ 0 か B → 0 なら、光の道が閉じうる。")


# ---------------------------------------------------------------- Figure 3: the mechanism

def fig_cycle():
    s = []
    boxes = [
        (320, 46, ["a time shift Δ", "between the clocks"], ["時計の間の", "時間のずれ Δ"], ""),
        (520, 150, ["a steady flow of energy", "through the throat"], ["のどを通る、", "絶えないエネルギーの流れ"], "flow"),
        (320, 254, ["the flow moves mass from", "one mouth to the other"], ["流れが、一方の口から", "もう一方へ質量を運ぶ"], ""),
        (120, 150, ["the clock rates change,", "against the drive"], ["時計の進み方が変わる。", "駆動に逆らう向き"], "bad"),
    ]
    for x, y, en, ja, kind in boxes:
        s.append(f'<rect class="cbox{(" cbox-" + kind) if kind else ""}" x="{x - 100}" y="{y - 26}" width="200" height="52" rx="8"/>')
        s.append(t2(x, y - 4, en[0], ja[0], "ink", "middle"))
        s.append(t2(x, y + 14, en[1], ja[1], "ink", "middle"))
    arcs = [((420, 40), (520, 40), (520, 122), math.pi / 2), ((520, 178), (520, 254), (422, 254), math.pi),
            ((220, 254), (120, 254), (120, 178), -math.pi / 2), ((120, 122), (120, 46), (218, 46), 0.0)]
    for (ax, ay), (qx, qy), (bx, by), ang in arcs:
        s.append(f'<path class="carrow" d="M{ax},{ay} Q{qx},{qy} {bx},{by}"/>')
        s.append(arrowhead(bx, by, ang, 8, "head-axis"))
    s.append(t2(320, 142, "one way round the loop is shorter,", "輪の一方の向きが短く、", "small", "middle"))
    s.append(t2(320, 158, "so the Casimir energies differ", "カシミールエネルギーに差が出る", "small", "middle"))
    return figure(
        3, 292, "".join(s),
        "How the fields push back, in the slow limit of the model. A time shift makes the loop shorter one way round "
        "and longer the other way, so the Casimir energies of the two directions differ. The difference is a steady "
        "flow of energy through the throat. It moves mass between the mouths, and the clock rates change against the "
        "drive. At one point of balance, the throat's clock ratio e<sup>δ</sup> cancels the drive exactly.",
        "モデルのゆっくりの極限で、場が押し返す仕組み。時間のずれがあると、輪は一方の向きに短く、逆の向きに長くなり、二つの向きの"
        "カシミールエネルギーに差が出ます。その差が、のどを通る絶えないエネルギーの流れです。流れは口の間で質量を運び、時計の進み方が"
        "駆動に逆らう向きに変わります。一つの釣り合いの点で、のどの時計の比 e<sup>δ</sup> が駆動をちょうど打ち消します。",
        "A cycle of four boxes: a time shift between the clocks; a steady flow of energy through the throat; the flow "
        "moves mass from one mouth to the other; the clock rates change, against the drive; and back to the time shift.",
        "四つの箱の輪: 時計の間の時間のずれ → のどを通る絶えないエネルギーの流れ → 流れが口の間で質量を運ぶ → 時計の進み方が"
        "駆動に逆らう向きに変わる → 時間のずれへ戻る。")


# ---------------------------------------------------------------- Figure 4: no settling

def fig_orbit():
    s = []
    ox, oy = 170, 170  # origin: no time shift, static throat
    s.append(f'<path class="axis" d="M40,{oy} H310 M{ox},206 V40"/>')
    s.append(arrowhead(316, oy, 0.0, 7, "head-axis"))
    s.append(arrowhead(ox, 34, -math.pi / 2, 7, "head-axis"))
    s.append(t2(316, oy + 20, "time shift", "時間のずれ", "small", "end"))
    s.append(t2(ox + 8, 44, "state of the throat", "のどの状態", "small"))
    cy = oy - 50
    s.append(f'<ellipse class="orbit-m2" cx="{ox}" cy="{cy}" rx="110" ry="50"/>')
    s.append(arrowhead(ox + 110, cy + 6, -math.pi / 2, 8, "head-m2"))
    s.append(f'<circle class="bal" cx="{ox}" cy="{cy}" r="5"/>')
    s.append(t2(ox + 10, cy - 8, "balance", "釣り合い", "small ink bold"))
    s.append(f'<circle class="start" cx="{ox}" cy="{oy}" r="4.5"/>')
    s.append(t2(ox - 10, oy + 18, "start", "出発点", "small", "end"))
    s.append(t2(ox, 236, "with a constant drive: a closed path", "一定の駆動: 閉じた道を回る", "ink", "middle"))
    s.append(t2(ox, 254, "around the point of balance", "釣り合いの点の周りで", "ink", "middle"))
    # what it does not do
    sx, sy = 480, 120
    pts = []
    for i in range(0, 300):
        t = i / 300 * 5.2 * math.pi
        r = 95 * math.exp(-0.23 * t)
        pts.append(f"{sx + r * math.cos(t):.1f},{sy + 0.5 * r * math.sin(t):.1f}")
    s.append(f'<polyline class="spiral" points="{" ".join(pts)}"/>')
    s.append(f'<circle class="bal-dim" cx="{sx}" cy="{sy}" r="4"/>')
    s.append(f'<path class="xmark" d="M{sx + 70},{sy - 70} l36,36 m0,-36 l-36,36"/>')
    s.append(t2(sx, 236, "settling at the point:", "点に落ち着く:", "ink", "middle"))
    s.append(t2(sx, 254, "not what the slow equations give", "ゆっくりの方程式はこうならない", "ink", "middle"))
    return figure(
        4, 268, "".join(s),
        "No settling (a drawing). Left: with a constant drive, the system starts from the static wormhole and moves "
        "on a closed path around the point of balance. Right: a path that spirals into the point would mean "
        "settling. The slow equations of the model do not give this: they do not change when time runs backward, "
        "and near the point they give a pure swing. The paper uses this slow limit only to find the mechanism.",
        "落ち着かない(絵)。左: 一定の駆動では、系は止まったワームホールから出発し、釣り合いの点の周りの閉じた道を回ります。"
        "右: 点へ渦を巻いて入る道なら、落ち着くことになります。モデルのゆっくりの方程式はこうなりません。時間を逆向きにしても"
        "変わらず、点の近くでは純粋な揺れになるからです。論文は、このゆっくりの極限を、仕組みを見つけるためだけに使います。",
        "Left: axes for time shift and state of the throat; an ellipse around the point of balance passes through "
        "the start. Right: a spiral into a point, crossed out, labelled settling, not what the slow equations give.",
        "左: 時間のずれとのどの状態の軸。釣り合いの点の周りの楕円が、出発点を通る。右: 点へ入る渦巻きに×印。"
        "「点に落ち着く: ゆっくりの方程式はこうならない」。")


# ---------------------------------------------------------------- Figure 5: roots

def fig_roots():
    s = []
    vx, top, bot, my = 200, 24, 236, 130
    s.append(f'<rect class="half-ok" x="40" y="{top}" width="{vx - 40}" height="{bot - top}"/>')
    s.append(f'<rect class="half-bad" x="{vx}" y="{top}" width="{vx - 40}" height="{bot - top}"/>')
    s.append(t2(120, top + 22, "dies away", "消えていく", "ink bold", "middle"))
    s.append(t2(280, top + 22, "grows", "育つ", "ink bold", "middle"))
    s.append(f'<path class="axis" d="M40,{my} H360"/>')
    s.append(f'<path class="vline" d="M{vx},{top} V{bot}"/>')
    for i in range(25):
        y = top + 12 + i * (bot - top - 24) / 24
        if abs(y - my) < 4 or abs(abs(y - my) - 17.7) < 4:
            continue
        s.append(f'<circle class="root" cx="{vx}" cy="{y:.1f}" r="3.6"/>')
    for dy in (-26, 0, 26):
        s.append(f'<circle class="root-art" cx="{vx}" cy="{my + dy}" r="5.5"/>')
    tx = 390
    s.append(t2(tx, 60, "In each of the 12 cases:", "12 の場合のそれぞれで:", "ink bold"))
    s.append(t2(tx, 82, "28 roots inside the counting region,", "数える範囲の中の 28 の根が、", "ink"))
    s.append(t2(tx, 100, "all exactly on the line.", "全てちょうど線の上にある。", "ink"))
    s.append(f'<circle class="root-art" cx="{tx + 6}" cy="128" r="5.5"/>')
    s.append(t2(tx + 18, 132, "3 of them come from the method", "そのうち 3 つは方法から来るもの", "small"))
    s.append(t2(tx, 168, "So no counted mode", "数えたモードは、どれも", "ink"))
    s.append(t2(tx, 186, "decays or grows.", "衰えず、育ちもしない。", "ink bold"))
    return figure(
        5, 250, "".join(s),
        "Roots of the linear problem with the travel time of light (a drawing; the positions of the dots are not "
        "computed values). A mode whose root lies to the left of the vertical line dies away; to the right, it "
        "grows. In each of the 12 cases (three loops, and drives 0, 0.001, 0.01 and 0.1), the 28 roots inside the "
        "counting region lie exactly on the line. Three of them are artefacts of the construction.",
        "光の通る時間を入れた線形の問題の根(絵。点の位置は計算した値ではありません)。根が縦の線の左にあるモードは消えていき、"
        "右にあれば育ちます。12 の場合(三つの輪と、駆動 0・0.001・0.01・0.1)のそれぞれで、数える範囲の中の 28 の根は、"
        "ちょうど線の上にあります。そのうち三つは、組み立て方から来るものです。",
        "Drawing: a vertical line with dots on it; the left half is labelled dies away, the right half grows. Three "
        "open circles near the middle come from the method. Text: in each of the 12 cases, 28 roots, all on the line.",
        "図: 縦の線の上に点が並ぶ。左半分は「消えていく」、右半分は「育つ」。中ほどの三つの白丸は方法から来るもの。"
        "文: 12 の場合のそれぞれで、28 の根が全て線の上。")


# ---------------------------------------------------------------- Figure 6: larger drives

def fig_large():
    s = []
    base = 200
    # margins
    s.append(t2(30, 26, "Smallest margins", "ゆとりの最小", "ink bold"))
    s.append(f'<path class="zero" d="M40,{base} H280"/>')
    s.append(t2(34, base + 4, "0", "0", "small bad-t", "end"))
    for i, (v, lab) in enumerate(((1.16, "A"), (2.03, "B"))):
        x = 90 + i * 110
        h = v * 70
        s.append(f'<g>{tip(f"{lab}: {v:.2f}", f"{lab}: {v:.2f}")}<rect class="bar-ok" x="{x}" y="{base - h:.1f}" width="56" height="{h:.1f}"/></g>')
        s.append(f'<text class="ink" x="{x + 28}" y="{base - h - 8:.1f}" text-anchor="middle">{v:.2f}</text>')
        s.append(f'<text class="ink bold" x="{x + 28}" y="{base + 18}" text-anchor="middle">{lab}</text>')
    s.append(t2(40, base + 44, "48 runs, drives 0.2 to 1,", "48 の計算、駆動 0.2〜1、", "small"))
    s.append(t2(40, base + 60, "in the windows fixed in advance", "前もって決めた区間の中", "small"))
    # largest time shift
    s.append(t2(350, 26, "Largest time shift", "時間のずれの最大", "ink bold"))
    s.append(f'<path class="axis" d="M350,{base} H620"/>')
    for i, (d, v) in enumerate(((0.2, 0.099), (0.3, 0.148), (0.6, 0.277), (1.0, 0.421))):
        x = 366 + i * 64
        h = v * 300
        s.append(f'<g>{tip(f"δ = {d:g}: {v:.3f}", f"δ = {d:g}: {v:.3f}")}<rect class="bar-m2" x="{x}" y="{base - h:.1f}" width="40" height="{h:.1f}"/></g>')
        s.append(f'<text class="ink" x="{x + 20}" y="{base - h - 8:.1f}" text-anchor="middle">{v:.3f}</text>')
        s.append(f'<text class="small" x="{x + 20}" y="{base + 18}" text-anchor="middle">{d:g}</text>')
    s.append(t2(485, base + 40, "drive δ", "駆動 δ", "small", "middle"))
    return figure(
        6, 270, "".join(s),
        "The larger drives. Left: the smallest values of the margins A and B over the 48 runs at the drives 0.2, "
        "0.3, 0.6 and 1, in the windows fixed in advance (up to the first event in runs with an event). Both stay "
        "positive, so the model does not reach its threshold for closed null curves within these runs. Right: the "
        "largest time shift at each drive. Numbers from the paper, Section V.",
        "大きな駆動。左: 駆動 0.2・0.3・0.6・1 の 48 の計算で、前もって決めた区間(出来事のあった計算では最初の出来事まで)の中の、"
        "ゆとり A と B の最小。どちらも正のままで、これらの計算の中では、モデルは閉じた光的曲線のしきいに届きません。"
        "右: 駆動ごとの時間のずれの最大。数は論文の V 節から取りました。",
        "Bar charts. Smallest margins: A 1.16, B 2.03. Largest time shift: 0.099 at drive 0.2, 0.148 at 0.3, "
        "0.277 at 0.6, 0.421 at 1.",
        "棒グラフ。ゆとりの最小: A 1.16、B 2.03。時間のずれの最大: 駆動 0.2 で 0.099、0.3 で 0.148、0.6 で 0.277、1 で 0.421。")


# ---------------------------------------------------------------- Figure 7: ratios

def fig_ratios():
    s = []
    x0, x1, y0, y1 = 80, 600, 250, 30
    lo, hi = 0.05, 2.0

    def Y(v):
        return y0 - (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (y0 - y1)

    s.append(f'<rect class="band" x="{x0}" y="{Y(1):.1f}" width="{x1 - x0}" height="{Y(0.1) - Y(1):.1f}"/>')
    s.append(f'<path class="axis" d="M{x0},{y0} H{x1} M{x0},{y0} V{y1}"/>')
    s.append(f'<path class="line-bad" d="M{x0},{Y(1):.1f} H{x1}"/>')
    s.append(f'<path class="line-ok" d="M{x0},{Y(0.1):.1f} H{x1}"/>')
    for v in (0.05, 0.1, 0.2, 0.5, 1, 2):
        s.append(f'<text class="small" x="{x0 - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{v:g}</text>')
    s.append(t2(x1 - 4, Y(1) - 6, "1: fails", "1: 破れ", "small bad-t", "end"))
    s.append(t2(x1 - 4, Y(0.1) + 14, "0.1: holds", "0.1: 成り立つ", "small ok-t", "end"))
    s.append(t2(x1 - 4, (Y(1) + Y(0.1)) / 2 + 4, "band", "帯", "small", "end"))
    data = [(0.2, 0.1032, 0.090, 0.068), (0.3, 0.156, 0.147, 0.112), (0.6, 0.314, 0.345, 0.185),
            (1.0, 0.517, 0.666, 0.343)]
    cols = [140, 250, 360, 470]
    for cx, (d, a, b, c) in zip(cols, data):
        s.append(f'<text class="ink" x="{cx}" y="{y0 + 20}" text-anchor="middle">{d:g}</text>')
        s.append(f'<g>{tip(f"S5* (dynamical part) = {a:g}", f"S5*(動的な部分)= {a:g}")}<circle class="mk-ok" cx="{cx - 14}" cy="{Y(a):.1f}" r="5"/></g>')
        s.append(f'<g>{tip(f"S8* = {b:g}", f"S8* = {b:g}")}<rect class="mk-ok" x="{cx - 4.5}" y="{Y(b) - 4.5:.1f}" width="9" height="9"/></g>')
        yc = Y(c)
        s.append(f'<g>{tip(f"S9* = {c:g}", f"S9* = {c:g}")}<path class="mk-ok" d="M{cx + 14},{yc - 5.5:.1f} l5.5,9.5 h-11 z"/></g>')
    s.append(t2((x0 + x1) / 2, y0 + 40, "drive δ", "駆動 δ", "small", "middle"))
    # coordinate S8 at delta = 1
    cx = 530
    s.append(f'<g>{tip("coordinate S8 at δ = 1: 0.97 to 1.77", "座標の S8(δ = 1): 0.97〜1.77")}'
             f'<path class="range-bad" d="M{cx},{Y(0.97):.1f} V{Y(1.77):.1f}"/></g>')
    s.append(f'<path class="xs" d="M{cx - 5},{Y(1.77) - 5:.1f} l10,10 m0,-10 l-10,10"/>')
    s.append(t2(cx + 10, Y(1.3) + 4, "S8", "S8", "small bad-t"))
    # legend
    ly = 22
    s.append(f'<circle class="mk-ok" cx="{x0 + 14}" cy="{ly - 4}" r="5"/>')
    s.append(t2(x0 + 24, ly, "S5*", "S5*", "small"))
    s.append(f'<rect class="mk-ok" x="{x0 + 64}" y="{ly - 8.5}" width="9" height="9"/>')
    s.append(t2(x0 + 80, ly, "S8*", "S8*", "small"))
    s.append(f'<path class="mk-ok" d="M{x0 + 124},{ly - 10} l5.5,9.5 h-11 z"/>')
    s.append(t2(x0 + 134, ly, "S9*", "S9*", "small"))
    s.append(t2(x0 + 176, ly, "new ratios (a boost does not change them)", "新しい比(ブーストで変わらない)", "small ok-t"))
    s.append(t2(x0 + 176, ly + 16, "| S8 at δ = 1: the ratio that a boost can change", "| δ = 1 の S8: ブーストで変わりうる比",
                "small bad-t"))
    return figure(
        7, 300, "".join(s),
        "The largest values over each run of the three new ratios, which a boost does not change, at the four "
        "larger drives (log scale; at δ = 0.2 without the two runs that stopped early). At δ = 1 the ratio S8, which "
        "a boost can change, reaches 0.97 to 1.77 in the same windows. The lines 0.1 and 1 are conventions fixed "
        "before the computation. Numbers from the paper, Section V; the paper's Figure 3 shows every run.",
        "四つの大きな駆動での、三つの新しい比(ブーストで変わらない)の、計算ごとの最大(対数の目盛り。δ = 0.2 は早く止まった"
        "二つの計算を除く)。δ = 1 では、ブーストで変わりうる比 S8 が、同じ区間で 0.97〜1.77 に達します。0.1 と 1 の線は、"
        "計算の前に決めた約束事です。数は論文の V 節から取りました。全ての計算は論文の図 3 にあります。",
        "Dot chart on a log scale with a band from 0.1 to 1. Drive 0.2: S5* 0.1032, S8* 0.090, S9* 0.068. "
        "Drive 0.3: 0.156, 0.147, 0.112. Drive 0.6: 0.314, 0.345, 0.185. Drive 1: 0.517, 0.666, 0.343. "
        "The ratio S8 at drive 1: 0.97 to 1.77.",
        "対数の目盛りの点の図。0.1〜1 に帯。駆動 0.2: S5* 0.1032、S8* 0.090、S9* 0.068。駆動 0.3: 0.156、0.147、0.112。"
        "駆動 0.6: 0.314、0.345、0.185。駆動 1: 0.517、0.666、0.343。駆動 1 の S8: 0.97〜1.77。")


# ---------------------------------------------------------------- Figure 8: verdicts (Table I of the paper)

ROWS = [("R1, g = 0.3", "N2 N2 U B B B B", "N2 N2 U U+ U+ U+ U+"),
        ("R1, g = 1", "U B B B B B B", "U U+ U+ U+ U+ U+ U+"),
        ("R2 (d/d₀ = 10⁻²), g = 0.3", "N2 N2 N3 U U B B", "N2 N2 N3 U U U+ U+"),
        ("R2 (d/d₀ = 10⁻²), g = 1", "U B B B B B B", "U U+ U+ U+ U+ U+ U+"),
        ("R2 (d/d₀ = 1), g = 0.3", "N3 N3 N3 N3 N3 N3 N3", "N3 N3 N3 N3 N3 N3 N3"),
        ("R2 (d/d₀ = 1), g = 1", "N3 N3 N3 U U B B", "N3 N3 N3 U U U+ U+")]
QS = ["10²", "10³", "10⁴", "10⁵", "10⁶", "10⁷", "10⁸"]
VCLS = {"B": "v-b", "U": "v-u", "N": "v-n"}
VNAME = {"B": ("bounded oscillation", "有界な揺れ"), "U": ("undecided within the band", "帯の中で未決"),
         "N": ("not decidable semiclassically", "半古典では決められない")}


def fig_verdicts():
    s = []
    lx, cw, ch, gap = 168, 30, 24, 26
    px = [lx, lx + 7 * cw + gap]
    y0 = 74
    titles = [("drives 0.001, 0.01, 0.1", "駆動 0.001・0.01・0.1"), ("drives 0.2, 0.3, 0.6, 1", "駆動 0.2・0.3・0.6・1")]
    subs = [("ratios in the throat's coordinate", "のどの座標での比"), ("new ratios", "新しい比")]
    for p, (te, tj), (se, sj) in zip(px, titles, subs):
        s.append(t2(p + 3.5 * cw, 18, te, tj, "ink bold", "middle"))
        s.append(t2(p + 3.5 * cw, 34, se, sj, "small", "middle"))
        for j, q in enumerate(QS):
            s.append(f'<text class="small" x="{p + j * cw + cw / 2:.1f}" y="{y0 - 10}" text-anchor="middle">{q}</text>')
    s.append(t2(lx - 8, y0 - 10, "q →", "q →", "small", "end"))
    for i, (lab, left, right) in enumerate(ROWS):
        y = y0 + i * ch
        s.append(f'<text class="small ink" x="{lx - 8}" y="{y + 16}" text-anchor="end">{lab}</text>')
        for p, cells in zip(px, (left.split(), right.split())):
            for j, c in enumerate(cells):
                k = c[0]
                x = p + j * cw
                name_en, name_ja = VNAME[k]
                sub = c[1:].replace("+", "")
                if sub:
                    name_en += f" (S{sub} ≥ 1)"
                    name_ja += f"(S{sub} ≥ 1)"
                if c.endswith("+"):
                    name_en += "; at δ = 0.2 only by the small margin of S5*"
                    name_ja += "。δ = 0.2 では S5* のわずかな差だけによる"
                s.append(f'<g>{tip(f"{lab}, q = {QS[j]}: {name_en}", f"{lab}, q = {QS[j]}: {name_ja}")}'
                         f'<rect class="{VCLS[k]}" x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" rx="3"/></g>')
                label = {"B": "B", "U": "U", "N": "N"}[k] + ({"2": "₂", "3": "₃"}.get(sub, ""))
                s.append(f'<text class="vt" x="{x + cw / 2:.1f}" y="{y + 16.5}" text-anchor="middle">{label}'
                         f'{"†" if c.endswith("+") else ""}</text>')
    ly = y0 + 6 * ch + 26
    items = [("v-b", "B: bounded oscillation", "B: 有界な揺れ"),
             ("v-u", "U: undecided within the band", "U: 帯の中で未決"),
             ("v-n", "N₂, N₃: not decidable semiclassically (S2 or S3 ≥ 1 before any drive)",
              "N₂, N₃: 半古典では決められない(駆動の前から S2 か S3 が 1 以上)")]
    for i, (cls, en, ja) in enumerate(items):
        y = ly + i * 18
        s.append(f'<rect class="{cls}" x="40" y="{y - 11}" width="14" height="14" rx="2"/>')
        s.append(t2(62, y, en, ja, "small"))
    s.append(t2(40, ly + 3 * 18, "†: at δ = 0.2, in the band only because S5* exceeds 0.1 by 1.0–3.2 %",
                "†: δ = 0.2 では、S5* が 0.1 を 1.0〜3.2 % 超えることだけで帯に入る", "small"))
    return figure(
        8, ly + 3 * 18 + 14, "".join(s),
        "Verdicts for each loop model, coupling g and number of fermions q (the paper's Table I, redrawn). Left: the "
        "constant drives 0.001, 0.01 and 0.1, with the ratios in the throat's coordinate. Right: the drives 0.2 to 1, "
        "with the new ratios. The entries are the same at every drive of each group. No row reaches the verdicts "
        "“stops” or “does not stop”. Hover over a cell for its meaning.",
        "輪のモデル・結合 g・フェルミオンの数 q ごとの判定(論文の表 I を描き直したもの)。左: 一定の駆動 0.001・0.01・0.1 で、"
        "のどの座標での比を使ったもの。右: 駆動 0.2〜1 で、新しい比を使ったもの。各組のどの駆動でも、判定は同じです。"
        "「止まる」「止まらない」の判定に届いた行はありません。升目に重ねると意味が出ます。",
        "Two grids of 6 rows by 7 columns. Left grid, small constant drives: mostly B for large q, U and N for small "
        "q or for the loop R2 with d over d0 equal to 1. Right grid, larger drives: every B becomes U; the N cells "
        "stay N. Totals at the larger drives: 27 U, 15 N.",
        "6 行 7 列の格子が二つ。左(小さな一定の駆動): q が大きいとおもに B、q が小さいときや、d/d₀ = 1 の R2 では U や N。"
        "右(大きな駆動): B は全て U になり、N は N のまま。大きな駆動での合計は U 27、N 15。")


# ---------------------------------------------------------------- transcript and page

def clock(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def transcript(script, chapters):
    starts = {c["id"]: c["start"] for c in chapters["chapters"]}
    out = ['<ol class="chapters">']
    for sc in script["scenes"]:
        t = starts[sc["id"]]
        mm = clock(t)
        en = " ".join(line["en"] for line in sc["lines"])
        ja = "".join(line["ja"] for line in sc["lines"])
        out.append(
            f'<li><button type="button" data-seek="{t}" aria-label="Play from {mm}" data-aria-en="Play from {mm}" '
            f'data-aria-ja="{mm} から再生">{mm}</button>'
            f'<h3><span data-l="en" lang="en">{esc(sc["title"])}</span>'
            f'<span data-l="ja" lang="ja">{esc(sc["title_ja"])}</span></h3>\n'
            f'<p data-l="en" lang="en">{esc(en)}</p>\n<p data-l="ja" lang="ja">{esc(ja)}</p></li>')
    out.append("</ol>")
    return "\n".join(out)


def main():
    page = (HERE / "page.html").read_text(encoding="utf-8")
    script = json.loads((HERE / "narration.json").read_text(encoding="utf-8"))
    chapters = json.loads((ROOT / "assets" / "video" / "chapters.json").read_text(encoding="utf-8"))
    total = round(chapters["duration"])
    head, body = page.split("</head>", 1)
    fill = {
        "{{DURATION_EN}}": f"{total // 60} min {total % 60} s",
        "{{DURATION_JA}}": f"{total // 60} 分 {total % 60} 秒",
        "{{TRANSCRIPT}}": transcript(script, chapters),
        "{{FIG_MODEL}}": fig_model(),
        "{{FIG_MARGINS}}": fig_margins(),
        "{{FIG_CYCLE}}": fig_cycle(),
        "{{FIG_ORBIT}}": fig_orbit(),
        "{{FIG_ROOTS}}": fig_roots(),
        "{{FIG_LARGE}}": fig_large(),
        "{{FIG_RATIOS}}": fig_ratios(),
        "{{FIG_VERDICTS}}": fig_verdicts(),
    }
    for k, v in fill.items():
        assert k in body, k
        body = body.replace(k, v)
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", body)
    assert not left, left
    (ROOT / "index.html").write_text(head + "</head>" + body, encoding="utf-8")
    print(f"index.html {len(head + body) / 1000:.0f} kB")


if __name__ == "__main__":
    main()
