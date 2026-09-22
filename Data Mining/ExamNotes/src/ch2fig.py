# -*- coding: utf-8 -*-
"""Draw the step-by-step solution under every chapter-2 numerical in ch2-num.tex.

One panel per step, a TECHNIQUE chip naming the move on each (map the range,
centre on the mean, pick j from the max, equal-depth bins, block split, trace
check, component product, cancel magnitude, tally the pairs, split the
attributes, roll-up, dice, cumulative frequency...), the decisive step
framed KEY STEP, and a technique index at the top of the chapter.

Exit test is replay: every value a panel shows is recomputed here from the
problem data and must be printed in that problem's text in ch2-num.tex.

    python ch2fig.py            regenerate every figure and its block in ch2-num.tex
    python ch2fig.py --report   run the checks only
"""
import math
import os
import sys
from collections import Counter

import stepkit as K
from stepkit import BS

TEX = os.path.join(K.HERE, "ch2-num.tex")
PREFIX = "ch2fig"

T = K.Techs([
    ("RANGE", "map the range", "Min-max: slide min to new\\_min and stretch max to new\\_max; order and gaps kept."),
    ("MEAN", "centre on mean", "Z-score: subtract the mean, divide by $\\sigma$; the result counts standard deviations."),
    ("JPICK", "pick j from max", "Decimal scaling: the smallest $j$ with $\\max|v|/10^j$ STRICTLY below 1."),
    ("DEPTH", "equal-depth bins", "Sort, then cut into bins holding the same COUNT (depth), not the same range."),
    ("BMEAN", "bin mean", "Replace every value by its bin's mean."),
    ("BOUND", "bin boundary", "Replace every value by the nearer of its bin's min and max."),
    ("WIDTH", "equal-width bins", "Cut the range into equal intervals: $W = (\\max-\\min)/N$; counts differ."),
    ("BLOCK", "block split", "A row and column of zeros decouple: solve each block alone."),
    ("CHAR", "characteristic eq.", "$|\\Sigma - \\lambda I| = 0$ gives the eigenvalues."),
    ("TRACE", "trace check", "The eigenvalues must add up to the trace (sum of the diagonal)."),
    ("EVEC", "eigenvector", "Solve $(\\Sigma-\\lambda I)v = 0$ from one row, then scale to unit length."),
    ("PROP", "share of variance", "$\\lambda_i / \\sum\\lambda$: how much of the spread each component keeps."),
    ("DIFF", "differences", "Subtract attribute by attribute first; every distance is built from these."),
    ("EUC", "Euclidean", "$\\sqrt{\\sum d_k^2}$: the straight line ($r=2$)."),
    ("MAN", "Manhattan", "$\\sum|d_k|$: along the grid ($r=1$)."),
    ("SUP", "supremum", "$\\max|d_k|$: the single largest difference ($r\\to\\infty$)."),
    ("SYM", "fill by symmetry", "A distance matrix has a zero diagonal and is symmetric: compute the lower triangle only."),
    ("DOT", "dot product", "Multiply component by component and add."),
    ("NORM", "length", "$\\lVert d\\rVert = \\sqrt{\\sum d_k^2}$ for each vector."),
    ("COS", "divide", "$\\cos = $ dot / (product of lengths): the angle, magnitude cancelled."),
    ("TALLY", "tally the pairs", "Count $M_{11}, M_{10}, M_{01}, M_{00}$ position by position."),
    ("SPLIT", "split attributes", "Decide which attributes are asymmetric (a shared 0 means nothing) and which symmetric."),
    ("JAC", "Jaccard", "$M_{11}/(M_{11}+M_{10}+M_{01})$: 0-0 matches ignored."),
    ("SMC", "SMC", "$(M_{11}+M_{00})/$all: 0-0 matches count."),
    ("DSYM", "symmetric $d$", "$(M_{10}+M_{01})/$all $= 1-$SMC."),
    ("ROLL", "roll-up", "Climb a dimension's hierarchy to a coarser level."),
    ("ALL", "roll-up to all", "A dimension the question never mentions is summed away."),
    ("DICE", "dice", "Restrict two or more dimensions at once."),
    ("SLICE", "slice", "Restrict exactly one dimension."),
    ("CUM", "cumulative freq.", "Run the frequencies up to find the interval holding the $N/2$-th value."),
    ("INTERP", "interpolate", "Assume values spread evenly inside the interval and walk in proportionally."),
    ("EMP", "empirical rule", "mean $-$ mode $\\approx 3$(mean $-$ median)."),
    ("QPOS", "quartile position", "$Q_k$ sits at position $k(n+1)/4$; interpolate between neighbours."),
    ("FENCE", "1.5 IQR fences", "Outside $Q_1 - 1.5\\,IQR$ or $Q_3 + 1.5\\,IQR$ is a suspected outlier."),
])

CAPTION = {"c2s_index": "The moves every chapter-2 numerical below is built from"}
W, HH = 4.1, 2.3          # standard panel; drawing area is y in [0, HH-0.62]


def need(sec, label, *s):
    K.need(sec, label, *s)


def txt(x, y, s, w=None, style="eqn"):
    if w:
        return r"\node[%s, text width=%.2fcm] at (%.3f,%.3f) {%s};" % (style, w, x, y, s)
    return r"\node[%s] at (%.3f,%.3f) {%s};" % (style, x, y, s)


def nline(y, lo, hi, pts, ticks, w=W, x0=0.1, col="cA", lab_above=True, hl=None, unit=""):
    """Number line at height y mapping lo..hi onto x0..x0+w-0.2."""
    span = w - 0.2

    def X(v):
        return x0 + (v - lo) / (hi - lo) * span

    L = [r"\draw[sub, line width=0.5pt] (%.3f,%.3f) -- (%.3f,%.3f);" % (x0, y, x0 + span, y)]
    # tick labels go on the side of the line away from the point labels
    tk_anchor, tk_y = ("north", y - 0.05) if lab_above else ("south", y + 0.05)
    for t in ticks:
        L.append(r"\draw[sub] (%.3f,%.3f) -- (%.3f,%.3f);" % (X(t), y - 0.04, X(t), y + 0.04))
        L.append(r"\node[font=\tiny, text=sub, anchor=%s, inner sep=1pt] at (%.3f,%.3f) {%s%s};"
                 % (tk_anchor, X(t), tk_y, fmt(t), unit))
    for v, lab, c in pts:
        L.append(r"\node[dot, minimum size=1.5mm, fill=%s] at (%.3f,%.3f) {};" % (c or col, X(v), y))
        if lab:
            L.append(r"\node[font=\tiny\bfseries, text=%s, anchor=%s, inner sep=1pt] at (%.3f,%.3f) {%s};"
                     % (c or col, "south" if lab_above else "north", X(v), y + (0.05 if lab_above else -0.05),
                        lab))
    if hl:
        a, b = hl
        L.append(r"\fill[mkc, opacity=0.18] (%.3f,%.3f) rectangle (%.3f,%.3f);" % (X(a), y - 0.1, X(b), y + 0.1))
    return L, X


def fmt(v):
    if isinstance(v, str):
        return v
    if abs(v - round(v)) < 1e-9:
        return "%d" % round(v)
    return ("%.3f" % v).rstrip("0")


def cells(x, y, vals, cw=0.34, ch=0.3, fills=None, bold=False, font=r"\tiny"):
    L = []
    for i, v in enumerate(vals):
        f = (fills or {}).get(i)
        st = "cell" if not f else "cell, fill=%sL, draw=%s" % (f, f)
        L.append(r"\node[%s, minimum width=%.2fcm, minimum height=%.2fcm, font=%s%s] at (%.3f,%.3f) {%s};"
                 % (st, cw - 0.03, ch - 0.03, font, r"\bfseries" if bold else "", x + cw * (i + 0.5), y, v))
    return L


def matrix(x, y, M, labels, cw=0.5, ch=0.3, lower=True, hot=()):
    """Symmetric distance matrix; the lower triangle drawn strong, the rest faint."""
    L = []
    n = len(M)
    for j, l in enumerate(labels):
        L.append(r"\node[hdr] at (%.3f,%.3f) {%s};" % (x + cw * (j + 1.5), y + 0.27, l))
        L.append(r"\node[hdr] at (%.3f,%.3f) {%s};" % (x + cw * 0.5, y - ch * j, l))
    for i in range(n):
        for j in range(n):
            strong = (i > j) if lower else True
            st = "hot" if (i, j) in hot else "cell"
            txtc = "ink" if strong else "sub!60"
            L.append(r"\node[%s, minimum width=%.2fcm, minimum height=%.2fcm, font=\tiny, text=%s] at (%.3f,%.3f) {%s};"
                     % (st, cw - 0.03, ch - 0.03, txtc, x + cw * (j + 1.5), y - ch * i, fmt(M[i][j])))
    return L


def grid(panels, per=4):
    return K.grid(panels, per)


# =====================================================================
#  M1 normalisation
# =====================================================================
def fig_11(sec):
    v = [200, 300, 400, 600, 1000]
    mn, mx = min(v), max(v)
    mm = [(x - mn) / (mx - mn) for x in v]
    mean = sum(v) / 5
    sd = math.sqrt(sum((x - mean) ** 2 for x in v) / 5)
    z = [(x - mean) / sd for x in v]
    need(sec, "1.1", "0.125", "0.25", "0.5", "282.84", "-1.0607", "-0.7071", "-0.3536", "+0.3536", "+1.7678",
         "0.02", "0.03", "0.04", "0.06", "0.1")
    if abs(sd - 282.84) > 0.005:
        sys.exit("1.1: sigma")
    f = "1.1"
    WW = 5.3
    body = []
    a, X = nline(1.35, 0, 1100, [(x, str(x), "cA") for x in v], [0, 500, 1000], w=WW)
    body += a
    b, Y = nline(0.75, 0, 1.1, [(m, fmt(m), "cB") for m in mm], [0, 0.5, 1], lab_above=False, w=WW)
    body += b
    for x, m in zip(v, mm):
        body.append(r"\draw[ruleL, dashed] (%.3f,1.35) -- (%.3f,0.75);" % (X(x), Y(m)))
    body.append(txt(0, 0.28, r"$v' = (v-200)/800$", WW))
    p1 = K.panel(T, f, 1, "(a) Min-max into [0,1]", ["RANGE"], body, WW, HH)
    body = []
    a, X = nline(1.35, 0, 1100, [(x, str(x), "cA") for x in v], [0, 500, 1000], w=WW)
    body += a
    body.append(r"\draw[mkc, line width=0.8pt] (%.3f,1.2) -- (%.3f,1.52);" % (X(500), X(500)))
    body.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=south] at (%.3f,1.52) {$\bar A$};" % X(500))
    b, Z = nline(0.75, -1.5, 2.0, [(q, "%.2f" % q, "cB") for q in z], [-1, 0, 1], lab_above=False, w=WW)
    body += b
    for x, q in zip(v, z):
        body.append(r"\draw[ruleL, dashed] (%.3f,1.35) -- (%.3f,0.75);" % (X(x), Z(q)))
    body.append(txt(0, 0.28, r"$\bar A = 500$, \ $\sigma = 282.84$ (population)", WW))
    p2 = K.panel(T, f, 2, "(b) Z-score", ["MEAN"], body, WW, HH)
    body = [txt(0, 1.62, r"$\max|v| = 1000$", W),
            txt(0, 1.3, r"$j=3$: \ $1000/10^3 = 1$ \ \textcolor{mkc}{\textbf{not} $<1$}", W),
            txt(0, 1.0, r"$j=4$: \ $1000/10^4 = 0.1 < 1$ \ \textcolor{gd}{\textbf{use this}}", W),
            txt(0, 0.62, r"$0.02,\ 0.03,\ 0.04,\ 0.06,\ 0.1$", W)]
    p3 = K.panel(T, f, 3, "(c) Decimal scaling", ["JPICK"], body, W, HH, key=True)
    return grid([p1, p2, p3], 3)


def fig_12(sec):
    d = [13, 15, 16, 16, 19, 20, 20, 21, 22, 22, 25, 25, 25, 25, 30, 33, 33, 35, 35, 35, 35, 36, 40, 45, 46, 52, 70]
    bins = [d[i:i + 3] for i in range(0, 27, 3)]
    means = [sum(b) / 3 for b in bins]
    for b, m in zip(bins, means):
        need(sec, "1.2", "%d/3 = %.2f" % (sum(b), m))
    f = "1.2"
    WB = 8.5
    body = []
    cw = WB / 9
    for i, (b, m) in enumerate(zip(bins, means)):
        x = cw * i
        hot = i == 8
        body.append(r"\node[cell, minimum width=%.2fcm, minimum height=0.62cm, align=center, font=\tiny%s]"
                    r" at (%.3f,1.2) {%s};" % (cw - 0.05, ", fill=mkL, draw=mkc" if hot else "",
                                               x + cw / 2, ", ".join(str(t) for t in b)))
        body.append(r"\node[font=\tiny\bfseries, text=%s] at (%.3f,0.72) {%s};"
                    % ("mkc" if hot else "acc", x + cw / 2, ("%.2f" % m).rstrip("0").rstrip(".")))
        body.append(r"\node[font=\tiny, text=sub] at (%.3f,1.63) {bin %d};" % (x + cw / 2, i + 1))
    body.append(txt(0, 0.45, r"27 values, depth 3 $\rightarrow$ \textbf{9 bins of 3}. Each value becomes its"
                             r" bin mean (blue). Bin 9: the outlier 70 is pulled down to \textbf{56}.", WB))
    p1 = K.panel(T, f, 1, "(a) Equal-depth bins of 3, then bin means", ["DEPTH", "BMEAN"], body, WB, HH, key=True)
    mean = sum(d) / 27
    need(sec, "1.2", r"\dfrac{809}{27} = 29.963", r"\dfrac{22}{57}", "0.386", "0.389", "0.35")
    body = []
    a, X = nline(1.45, 13, 70, [(35, "35", "mkc")], [13, 70], w=W, x0=0.1)
    body += a + [txt(0, 1.15, r"min-max: $(35-13)/57 = \mathbf{0.386}$", W)]
    a, Z = nline(0.62, 13, 70, [(35, "", "mkc"), (mean, r"$\bar A$", "acc")], [], w=W, x0=0.1, lab_above=False)
    body += a + [txt(0, 0.4, r"z: $(35-29.963)/12.94 = \mathbf{0.389}$", W),
                 txt(0, 0.12, r"decimal: max $70 \rightarrow j=2$, $35/100 = \mathbf{0.35}$", W)]
    p2 = K.panel(T, f, 2, "(b)-(d) Transform 35", ["RANGE", "MEAN", "JPICK"], body, W, HH)
    return K.rows([p1], [p2])


def fig_pb(sec):
    lo, hi, v = 12000, 98000, 73600
    a = (v - lo) / (hi - lo)
    b = a * 2 - 1
    need(sec, "Practice B", "0.716", "0.432")
    f = "Practice B"
    WB = 6.0
    body = []
    l1, X = nline(1.45, lo, hi, [(v, r"\$73{,}600", "mkc")], [lo, hi], w=WB)
    l2, Y = nline(0.85, 0, 1, [(a, "0.716", "cB")], [0, 1], w=WB, lab_above=False)
    l3, Z = nline(0.3, -1, 1, [(b, "0.432", "cC")], [-1, 0, 1], w=WB, lab_above=False)
    body += l1 + l2 + l3
    body.append(r"\draw[ruleL, dashed] (%.3f,1.45) -- (%.3f,0.85);" % (X(v), Y(a)))
    body.append(r"\draw[ruleL, dashed] (%.3f,0.85) -- (%.3f,0.3);" % (Y(a), Z(b)))
    p1 = K.panel(T, f, 1, "The same point, two target ranges", ["RANGE"], body, WB, HH, key=True)
    return K.single(p1)


def fig_pa(sec):
    d = [4, 8, 9, 15, 21, 21, 24, 25, 26, 28, 29, 34]
    bins = [d[0:4], d[4:8], d[8:12]]
    means = [sum(b) / 4 for b in bins]
    bnd = [[b[0] if x - b[0] <= b[-1] - x else b[-1] for x in b] for b in bins]
    need(sec, "Practice A", "36/4 = 9", "91/4 = 22.75", "117/4 = 29.25", "4, 4, 4, 15", "21, 21, 25, 25",
         "26, 26, 26, 34", "counts 3, 3, 6")
    if [b for bb in bnd for b in bb] != [4, 4, 4, 15, 21, 21, 25, 25, 26, 26, 26, 34]:
        sys.exit("Practice A: boundaries")
    f = "Practice A"
    cols = ["cA", "cB", "cC"]
    body = []
    for i, b in enumerate(bins):
        body += cells(0.05 + i * 1.35, 1.35, [str(x) for x in b], cw=0.32, fills={k: cols[i] for k in range(4)})
    body.append(txt(0, 0.95, "12 values, depth 4 $\\rightarrow$ 3 bins of 4.", W))
    body.append(txt(0, 0.6, "Means: 9, 22.75, 29.25", W))
    p1 = K.panel(T, f, 1, "Equal-depth bins", ["DEPTH", "BMEAN"], body, W, HH)
    body = []
    for i, (b, nb) in enumerate(zip(bins, bnd)):
        x0 = 0.05 + i * 1.35
        body += cells(x0, 1.35, [str(x) for x in b], cw=0.32)
        body += cells(x0, 0.75, [str(x) for x in nb], cw=0.32,
                      fills={k: ("mkc" if nb[k] != b[k] else cols[i]) for k in range(4)}, bold=True)
        for k in range(4):
            body.append(r"\draw[-{Stealth[length=1mm]}, sub] (%.3f,1.2) -- (%.3f,0.9);"
                        % (x0 + 0.32 * (k + 0.5), x0 + 0.32 * (k + 0.5)))
    body.append(txt(0, 0.45, r"Each value moves to the \textbf{nearer} of its bin's min and max"
                             r" (orange = moved).", W))
    p2 = K.panel(T, f, 2, "Bin boundaries", ["BOUND"], body, W, HH, key=True)
    body = []
    a, X = nline(1.2, 4, 34, [(x, "", "cA") for x in d], [4, 14, 24, 34], w=W)
    body += a
    for lo, hi in ((4, 14), (14, 24), (24, 34)):
        body.append(r"\draw[mkc, line width=0.7pt] (%.3f,1.05) -- (%.3f,1.35);" % (X(lo), X(lo)))
    body.append(r"\draw[mkc, line width=0.7pt] (%.3f,1.05) -- (%.3f,1.35);" % (X(34), X(34)))
    body.append(txt(0, 0.62, r"$W = (34-4)/3 = 10$: $[4,14), [14,24), [24,34]$ hold \textbf{3, 3, 6}.", W))
    p3 = K.panel(T, f, 3, "Contrast: equal width", ["WIDTH"], body, W, HH)
    return grid([p1, p2, p3], 3)


# =====================================================================
#  M2 PCA
# =====================================================================
def fig_pca(sec):
    l1, l2, l3 = 3 + 2 * math.sqrt(2), 2.0, 3 - 2 * math.sqrt(2)
    tot = l1 + l2 + l3
    need(sec, "2.1", "5.8284", "0.1716", r"\lambda^2 - 6\lambda + 1 = 0", "72.86", "25.00", "2.14", "97.86",
         "(0.3827,\\ -0.9239,\\ 0)", "(0.9239,\\ 0.3827,\\ 0)")
    if abs(tot - 8) > 1e-9 or abs(100 * l1 / 8 - 72.86) > 0.005 or abs(100 * l3 / 8 - 2.14) > 0.005:
        sys.exit("2.1: eigenvalues")
    e1 = (1 / math.sqrt(1 + (1 + math.sqrt(2)) ** 2), -(1 + math.sqrt(2)) / math.sqrt(1 + (1 + math.sqrt(2)) ** 2))
    if abs(e1[0] - 0.3827) > 5e-5 or abs(e1[1] + 0.9239) > 5e-5:
        sys.exit("2.1: e1")
    f = "2.1"
    M = [["1", "-2", "0"], ["-2", "5", "0"], ["0", "0", "2"]]
    body = []
    for i in range(3):
        for j in range(3):
            blk = "cA" if (i < 2 and j < 2) else ("cB" if (i == 2 and j == 2) else None)
            st = "cell" + (", fill=%sL, draw=%s" % (blk, blk) if blk else "")
            body.append(r"\node[%s, minimum width=0.5cm, minimum height=0.34cm, font=\tiny] at (%.2f,%.2f) {$%s$};"
                        % (st, 0.6 + 0.52 * j, 1.45 - 0.36 * i, M[i][j]))
    body.append(txt(2.35, 1.55, r"2$\times$2 block\\and a 1$\times$1\\block: solve\\each alone.", 1.7, "note"))
    body.append(txt(0, 0.3, r"$1\times1$: \ $2 - \lambda = 0 \Rightarrow \lambda = 2$", W))
    p1 = K.panel(T, f, 1, "Spot the blocks", ["BLOCK"], body, W, HH)
    body = [txt(0, 1.6, r"$(1-\lambda)(5-\lambda) - 4 = 0$", W),
            txt(0, 1.3, r"$\lambda^2 - 6\lambda + 1 = 0$", W),
            txt(0, 1.0, r"$\lambda = 3 \pm 2\sqrt2$", W),
            txt(0, 0.62, r"$\lambda_1 = \mathbf{5.8284}$, \ $\lambda_2 = \mathbf{2}$, \ $\lambda_3 = \mathbf{0.1716}$", W)]
    p2 = K.panel(T, f, 2, "Eigenvalues of the 2$\\times$2", ["CHAR"], body, W, HH, key=True)
    body = []
    x = 0.05
    WB = W - 0.2
    for lam, c, lab in ((l1, "cA", "5.83"), (l2, "cB", "2"), (l3, "cC", "")):
        dw = WB * lam / 8
        body.append(r"\fill[%sL, draw=%s] (%.3f,1.1) rectangle (%.3f,1.45);" % (c, c, x, x + dw))
        if lab:
            body.append(r"\node[font=\tiny\bfseries, text=%s] at (%.3f,1.275) {%s};" % (c, x + dw / 2, lab))
        x += dw
    body.append(txt(0, 0.9, r"$5.8284 + 2 + 0.1716 = 8$", W))
    body.append(txt(0, 0.55, r"trace $= 1+5+2 = 8$ \ \textcolor{gd}{\textbf{agrees}}", W))
    p3 = K.panel(T, f, 3, "Trace check", ["TRACE"], body, W, HH)
    body = []
    o = (0.75, 0.62)
    s = 0.55
    body.append(r"\draw[ruleL] (%.2f,%.2f) -- (%.2f,%.2f);" % (o[0] - 0.6, o[1], o[0] + 0.6, o[1]))
    body.append(r"\draw[ruleL] (%.2f,%.2f) -- (%.2f,%.2f);" % (o[0], o[1] - 0.6, o[0], o[1] + 0.72))
    body.append(r"\node[font=\tiny, text=sub, anchor=west] at (%.2f,%.2f) {$x_1$};" % (o[0] + 0.6, o[1]))
    body.append(r"\node[font=\tiny, text=sub, anchor=south] at (%.2f,%.2f) {$x_2$};" % (o[0], o[1] + 0.72))
    for (vx, vy), c, lab in (((0.3827, -0.9239), "cA", r"$e_1$"), ((0.9239, 0.3827), "cC", r"$e_3$")):
        body.append(r"\draw[-{Stealth[length=1.6mm]}, %s, line width=0.9pt] (%.2f,%.2f) -- (%.2f,%.2f);"
                    % (c, o[0], o[1], o[0] + s * vx, o[1] + s * vy))
        body.append(r"\node[font=\tiny\bfseries, text=%s, anchor=west] at (%.2f,%.2f) {%s};"
                    % (c, o[0] + s * vx + 0.03, o[1] + s * vy, lab))
    for k, line in enumerate((r"$e_1 = (0.3827, -0.9239, 0)$", r"$e_3 = (0.9239, 0.3827, 0)$",
                              r"$e_2 = (0, 0, 1)$, out of the page", r"$e_1 \cdot e_3 = 0$: at right angles")):
        body.append(txt(1.95, 1.6 - 0.3 * k, line, None, "note"))
    p4 = K.panel(T, f, 4, "Eigenvectors", ["EVEC"], body, 5.0, HH)
    body = []
    x = 0.05
    for lam, c, lab in ((l1, "cA", "72.86\\%"), (l2, "cB", "25.00\\%"), (l3, "cC", "")):
        dw = WB * lam / 8
        body.append(r"\fill[%sL, draw=%s] (%.3f,1.1) rectangle (%.3f,1.45);" % (c, c, x, x + dw))
        if lab:
            body.append(r"\node[font=\tiny\bfseries, text=%s] at (%.3f,1.275) {%s};" % (c, x + dw / 2, lab))
        x += dw
    body.append(r"\draw[mkc, line width=0.8pt] (%.3f,1.0) -- (%.3f,1.55);" % (0.05 + WB * (l1 + l2) / 8,
                                                                         0.05 + WB * (l1 + l2) / 8))
    body.append(txt(0, 0.9, r"PC1 $+$ PC2 $= \mathbf{97.86\%}$; PC3 only 2.14\%.", W))
    body.append(txt(0, 0.55, r"Keep 2 components: 3 dims $\rightarrow$ 2.", W))
    p5 = K.panel(T, f, 5, "Share of variance", ["PROP"], body, W, HH)
    return K.rows([p1, p2, p3], [p4, p5])


# =====================================================================
#  M3 distances
# =====================================================================
def plane(pts, lo=(0, 0), hi=(7, 5), ox=0.25, oy=0.25, sx=0.36, sy=0.26):
    L = [r"\draw[ruleL] (%.2f,%.2f) grid[xstep=%.2f, ystep=%.2f] (%.2f,%.2f);"
         % (ox, oy, sx, sy, ox + sx * (hi[0] - lo[0]), oy + sy * (hi[1] - lo[1]))]

    def P(x, y):
        return ox + sx * (x - lo[0]), oy + sy * (y - lo[1])

    for (x, y), lab, c in pts:
        px, py = P(x, y)
        L.append(r"\node[dot, fill=%s] at (%.3f,%.3f) {};" % (c, px, py))
        L.append(r"\node[font=\tiny\bfseries, text=%s, anchor=south west, inner sep=0.5pt] at (%.3f,%.3f) {%s};"
                 % (c, px, py, lab))
    return L, P


def fig_warm(sec):
    a, b = (1, 2), (3, 5)
    need(sec, "warm-up", r"\sqrt{13} = \mathbf{3.61}", r"2+3 = \mathbf{5}", r"\max(2,3) = \mathbf{3}")
    f = "Warm-up"
    out = []
    for step, (title, tech, key) in enumerate((("Euclidean", "EUC", False), ("Manhattan", "MAN", False),
                                               ("Supremum", "SUP", True)), 1):
        body, P = plane([(a, "$x_1$", "cA"), (b, "$x_2$", "cB")], hi=(5, 6), sx=0.3, sy=0.2)
        (ax, ay), (bx, by) = P(*a), P(*b)
        if tech == "EUC":
            body.append(r"\draw[mkc, line width=1pt] (%.3f,%.3f) -- (%.3f,%.3f);" % (ax, ay, bx, by))
            t = r"$\sqrt{2^2+3^2} = \sqrt{13} = \mathbf{3.61}$"
        elif tech == "MAN":
            body.append(r"\draw[mkc, line width=1pt] (%.3f,%.3f) -- (%.3f,%.3f) -- (%.3f,%.3f);"
                        % (ax, ay, bx, ay, bx, by))
            t = r"$2 + 3 = \mathbf{5}$"
        else:
            body.append(r"\draw[ruleL, line width=1pt] (%.3f,%.3f) -- (%.3f,%.3f);" % (ax, ay, bx, ay))
            body.append(r"\draw[mkc, line width=1.2pt] (%.3f,%.3f) -- (%.3f,%.3f);" % (bx, ay, bx, by))
            t = r"$\max(2, 3) = \mathbf{3}$: the longer leg only"
        body.append(txt(1.9, 1.5, t, 2.7))
        out.append(K.panel(T, f, step, title, [tech], body, 4.7, HH, key=key))
    return grid(out, 3)


def fig_31(sec):
    P = {"P1": (6, 3), "P2": (2, 2), "P3": (3, 4)}
    names = ["P1", "P2", "P3"]
    man = [[sum(abs(a - b) for a, b in zip(P[i], P[j])) for j in names] for i in names]
    sup = [[max(abs(a - b) for a, b in zip(P[i], P[j])) for j in names] for i in names]
    need(sec, "3.1", "4+1 = 5", "3+1 = 4", "1+2 = 3", r"\max(4,1) = 4", r"\max(3,1) = 3", r"\max(1,2) = 2")
    if [man[1][0], man[2][0], man[2][1]] != [5, 4, 3] or [sup[1][0], sup[2][0], sup[2][1]] != [4, 3, 2]:
        sys.exit("3.1")
    f = "3.1"
    body, Pp = plane([(P[n], n, c) for n, c in zip(names, ["cA", "cB", "cC"])], hi=(7, 5), sx=0.4, sy=0.26)
    body.append(txt(3.05, 1.55, r"Differences\\$P_1P_2$: 4, 1\\$P_1P_3$: 3, 1\\$P_2P_3$: 1, 2", 1.1, "note"))
    p1 = K.panel(T, f, 1, "Plot, take differences", ["DIFF"], body, W, HH)
    body = matrix(0.2, 1.35, man, ["$P_1$", "$P_2$", "$P_3$"], hot={(1, 0), (2, 0), (2, 1)})
    body.append(txt(2.3, 1.45, r"$|dx| + |dy|$\\5, 4, 3", 1.7))
    body.append(txt(0, 0.35, r"Lower triangle computed, the rest mirrored; diagonal 0.", W, "note"))
    p2 = K.panel(T, f, 2, "Manhattan matrix", ["MAN", "SYM"], body, W, HH)
    body = matrix(0.2, 1.35, sup, ["$P_1$", "$P_2$", "$P_3$"], hot={(1, 0), (2, 0), (2, 1)})
    body.append(txt(2.3, 1.45, r"$\max(|dx|, |dy|)$\\4, 3, 2", 1.7))
    body.append(txt(0, 0.35, r"Each entry $\le$ its Manhattan entry: 4$\le$5, 3$\le$4, 2$\le$3.", W, "note"))
    p3 = K.panel(T, f, 3, "Supremum matrix", ["SUP", "SYM"], body, W, HH, key=True)
    return grid([p1, p2, p3], 3)


def bars(x, y, vals, labels, w, h=0.55, col="cA", hl=None):
    """Signed or unsigned vertical bars, baseline at y."""
    L = []
    mx = max(abs(v) for v in vals) or 1
    bw = w / len(vals)
    for i, (v, lab) in enumerate(zip(vals, labels)):
        c = "mkc" if hl is not None and i == hl else col
        hh = h * abs(v) / mx
        y0, y1 = (y, y + hh) if v >= 0 else (y - hh, y)
        L.append(r"\fill[%s!70] (%.3f,%.3f) rectangle (%.3f,%.3f);" % (c, x + bw * i + 0.06, y0, x + bw * (i + 1) - 0.06, y1))
        L.append(r"\node[font=\tiny\bfseries, anchor=%s, inner sep=0.8pt] at (%.3f,%.3f) {%s};"
                 % ("south" if v >= 0 else "north", x + bw * (i + 0.5), y1 if v >= 0 else y0, fmt(v)))
        L.append(r"\node[font=\tiny, text=sub, anchor=%s, inner sep=0.8pt] at (%.3f,%.3f) {%s};"
                 % ("north" if v >= 0 else "south", x + bw * (i + 0.5), y - 0.02 if v >= 0 else y + 0.02, lab))
    L.append(r"\draw[sub] (%.3f,%.3f) -- (%.3f,%.3f);" % (x, y, x + w, y))
    return L


def fig_32(sec):
    O = {1: (4, 56, 7, 10), 3: (7, 58, 6, 9), 4: (9, 55, 7, 12)}
    d13 = [a - b for a, b in zip(O[1], O[3])]
    d14 = [a - b for a, b in zip(O[1], O[4])]
    e13, e14 = math.sqrt(sum(x * x for x in d13)), math.sqrt(sum(x * x for x in d14))
    need(sec, "3.2", "(-3,-2,1,1)", "(-5,1,0,-2)", "3.873", "5.477")
    if ("%.3f" % e13, "%.3f" % e14) != ("3.873", "5.477"):
        sys.exit("3.2")
    f = "3.2"
    lab = ["Size", "Wt", "Col", "Taste"]
    body = bars(0.1, 0.95, d13, lab, 1.8) + bars(2.2, 0.95, d14, lab, 1.8, col="cB")
    body.append(txt(0.3, 1.72, r"$O_1 - O_3$", None, "note"))
    body.append(txt(2.4, 1.72, r"$O_1 - O_4$", None, "note"))
    p1 = K.panel(T, f, 1, "Differences", ["DIFF"], body, W, HH)
    body = [txt(0, 1.6, r"$d(O_1,O_3) = \sqrt{9+4+1+1} = \sqrt{15} = \mathbf{3.873}$", 5.2),
            txt(0, 1.2, r"$d(O_1,O_4) = \sqrt{25+1+0+4} = \sqrt{30} = \mathbf{5.477}$", 5.2),
            txt(0, 0.75, r"Object 1 is closer to 3 than to 4.", 5.2),
            txt(0, 0.4, r"Square, add, root: the size gap of 5 dominates $d(O_1,O_4)$.", 5.2, "note")]
    p2 = K.panel(T, f, 2, "Square, sum, root", ["EUC"], body, 5.2, HH, key=True)
    return grid([p1, p2], 2)


# =====================================================================
#  M4 cosine
# =====================================================================
def fig_cos(fig, sec, a, b, names, dot_s, na_s, nb_s, cos_s, dims=None):
    prods = [x * y for x, y in zip(a, b)]
    dot = sum(prods)
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    c = dot / (na * nb)
    need(sec, fig, dot_s, na_s, nb_s, cos_s)
    if abs(float(cos_s) - c) > 5e-5:
        sys.exit("%s: cos %.5f vs %s" % (fig, c, cos_s))
    dims = dims or [str(i + 1) for i in range(len(a))]
    hl = prods.index(max(prods)) if max(prods) > 0.6 * dot else None
    body = bars(0.1, 0.72, prods, dims, W - 0.3, h=0.7, hl=hl)
    body.append(txt(0, 0.4, r"$%s \cdot %s = %s$%s" % (names[0], names[1], fmt(dot),
                                                      r" \ (one term dominates)" if hl is not None else ""), W))
    p1 = K.panel(T, fig, 1, "Dot product, term by term", ["DOT"], body, W, HH)
    body = [txt(0, 1.55, r"$\lVert %s\rVert = %s$" % (names[0], na_s.split("= ")[-1]), W),
            txt(0, 1.2, r"$\lVert %s\rVert = %s$" % (names[1], nb_s.split("= ")[-1]), W),
            txt(0, 0.8, r"Square every component, add, root.", W, "note")]
    p2 = K.panel(T, fig, 2, "Lengths", ["NORM"], body, W, HH)
    ang = math.degrees(math.acos(min(1, c)))
    body = [r"\draw[-{Stealth[length=1.6mm]}, cA, line width=0.9pt] (0.3,0.35) -- (1.5,0.35);",
            r"\draw[-{Stealth[length=1.6mm]}, cB, line width=0.9pt] (0.3,0.35) -- (%.3f,%.3f);"
            % (0.3 + 1.2 * math.cos(math.radians(ang)), 0.35 + 1.2 * math.sin(math.radians(ang))),
            r"\draw[mkc] (0.75,0.35) arc (0:%.1f:0.45);" % ang,
            r"\node[font=\tiny\bfseries, text=mkc, anchor=north west] at (0.3,%.3f) {angle $%.1f^\circ$};"
            % (0.25, ang),
            txt(1.8, 1.5, r"$\cos = \dfrac{%s}{%s \times %s}$\\[2pt]$= \mathbf{%s}$" %
                (fmt(dot), na_s.split("= ")[-1], nb_s.split("= ")[-1], cos_s),
                2.2)]
    p3 = K.panel(T, fig, 3, "Divide: the angle", ["COS"], body, W, HH, key=True)
    return grid([p1, p2, p3], 3)


# =====================================================================
#  M5 binary
# =====================================================================
CATC = {"11": "cC", "00": "cA", "10": "cB", "01": "cD"}


def tally_panel(fig, step, title, p, q, pn, qn, key=False, tech=("TALLY",), heads=None, w=W, extra=None):
    cat = [str(a) + str(b) for a, b in zip(p, q)]
    cw = min(0.45, (w - 0.95) / len(p))
    x0 = 0.9
    body = []
    if heads:
        for i, h in enumerate(heads):
            body.append(r"\node[font=\tiny, text=sub] at (%.3f,1.5) {%s};" % (x0 + cw * (i + 0.5), h))
    body += [r"\node[font=\tiny, text=sub, anchor=east] at (%.2f,1.28) {%s};" % (x0 - 0.05, pn),
             r"\node[font=\tiny, text=sub, anchor=east] at (%.2f,1.0) {%s};" % (x0 - 0.05, qn),
             r"\node[font=\tiny, text=sub, anchor=east] at (%.2f,0.72) {pair};" % (x0 - 0.05)]
    body += cells(x0, 1.28, [str(x) for x in p], cw=cw, ch=0.26)
    body += cells(x0, 1.0, [str(x) for x in q], cw=cw, ch=0.26)
    body += cells(x0, 0.72, [c for c in cat], cw=cw, ch=0.26, fills={i: CATC[c] for i, c in enumerate(cat)},
                  bold=True)
    cc = Counter(cat)
    body.append(txt(0, 0.5, r"$M_{11}{=}%d$ \ $M_{10}{=}%d$ \ $M_{01}{=}%d$ \ $M_{00}{=}%d$"
                    % (cc["11"], cc["10"], cc["01"], cc["00"]), w))
    if extra:
        body.append(txt(0, 0.24, extra, w))
    return K.panel(T, fig, step, title, list(tech), body, w, HH, key=key), cc


def fig_51(sec):
    P = [0, 0, 1, 1, 0, 1]
    Q = [1, 1, 1, 1, 0, 1]
    f = "5.1"
    p1, c = tally_panel(f, 1, "Tally position by position", P, Q, "$P$", "$Q$", key=True)
    j = c["11"] / (c["11"] + c["10"] + c["01"])
    s = (c["11"] + c["00"]) / 6
    need(sec, f, r"J = \mathbf{0.6}", r"SMC = \mathbf{0.667}", "M_{11} = 3", "M_{01} = 2", "M_{00} = 1")
    if abs(j - 0.6) > 1e-9 or abs(s - 0.6667) > 1e-4:
        sys.exit("5.1")
    body = [txt(0, 1.55, r"$J = \dfrac{M_{11}}{M_{11}+M_{10}+M_{01}} = \dfrac{3}{5} = \mathbf{0.6}$", W),
            txt(0, 0.9, r"The single 0-0 (position 5) is \textbf{left out}.", W, "note")]
    p2 = K.panel(T, f, 2, "Jaccard", ["JAC"], body, W, HH)
    body = [txt(0, 1.55, r"$SMC = \dfrac{M_{11}+M_{00}}{6} = \dfrac{4}{6} = \mathbf{0.667}$", W),
            txt(0, 0.9, r"The 0-0 counts as agreement, so SMC $>$ J.", W, "note")]
    p3 = K.panel(T, f, 3, "SMC", ["SMC"], body, W, HH)
    return grid([p1, p2, p3], 3)


def fig_52(sec):
    f = "5.2"
    rows = {"Ram": ("M", "Black", "Gray", "P", "N", "P", "N"),
            "Laxmi": ("F", "Blue", "Black", "P", "P", "N", "N"),
            "Shyam": ("M", "Blue", "Gray", "N", "P", "N", "P")}
    enc = {k: [1 if x == "P" else 0 for x in v[3:]] for k, v in rows.items()}
    need(sec, f, "Ram $=(1,0,1,0)$", "Laxmi $=(1,1,0,0)$", "Shyam $=(0,1,0,1)$")
    if enc["Ram"] != [1, 0, 1, 0] or enc["Laxmi"] != [1, 1, 0, 0] or enc["Shyam"] != [0, 1, 0, 1]:
        sys.exit("5.2 encoding")
    body = [r"\fill[cBL, draw=cB] (0,0.72) rectangle (1.75,1.64);",
            r"\fill[cAL, draw=cA] (1.9,0.72) rectangle (4.05,1.64);",
            txt(0.06, 1.58, r"\textbf{symmetric}\\Gender, Eye, Hair\\both states count", 1.65),
            txt(1.96, 1.58, r"\textbf{asymmetric}\\Test-1, Test-2,\\Fever, Cough\\shared N = no info", 2.05),
            txt(0, 0.45, r"P $\rightarrow$ 1, N $\rightarrow$ 0 on the tests.", W)]
    p1 = K.panel(T, f, 1, "Split the attributes", ["SPLIT"], body, W, HH, key=True)
    hd = ["T1", "T2", "Fev", "Cou"]
    p2, c = tally_panel(f, 2, "(i) Jaccard(Ram, Laxmi)", enc["Ram"], enc["Laxmi"], "Ram", "Laxmi",
                        tech=("TALLY", "JAC"), heads=hd, extra=r"$J = 1/(1+1+1) = \mathbf{0.333}$")
    need(sec, f, r"J = \mathbf{0.333}", r"d = \mathbf{0.667}", r"SMC = \mathbf{0}")
    sym = {k: [1 if v[0] == "M" else 0, 1 if v[1] == "Black" else 0, 1 if v[2] == "Gray" else 0]
           for k, v in rows.items()}
    p3, c3 = tally_panel(f, 3, "(ii) $d$(Laxmi, Shyam), symmetric", sym["Laxmi"], sym["Shyam"], "Laxmi", "Shyam",
                         tech=("TALLY", "DSYM"), heads=["Gen", "Eye", "Hair"],
                         extra=r"$d = (0+2)/3 = \mathbf{0.667}$")
    if (c3["10"] + c3["01"]) / 3 != 2 / 3:
        sys.exit("5.2 d")
    p4, c4 = tally_panel(f, 4, "(iii) SMC(Ram, Shyam)", enc["Ram"], enc["Shyam"], "Ram", "Shyam",
                         tech=("TALLY", "SMC"), heads=hd, extra=r"$SMC = (0+0)/4 = \mathbf{0}$")
    return grid([p1, p2, p3, p4], 4)


# =====================================================================
#  M6 OLAP
# =====================================================================
def olap_fig(fig, dims, steps, keystep):
    """dims: [(name, [levels bottom..top])]; steps: [(title, tech, {dim: level or ('=', value)})]."""
    nd = len(dims)
    out = []
    # each panel shows the state AFTER its own step
    cur = {d: lv[0] for d, lv in dims}
    fixed = {}
    for k, (title, tech, change) in enumerate(steps, 1):
        for d, v in change.items():
            if isinstance(v, tuple):
                fixed[d] = v[1]
            else:
                cur[d] = v
        body = []
        for i, (d, lv) in enumerate(dims):
            x = 0.05 + 0.78 * i
            body.append(r"\node[font=\tiny\bfseries, text=ink] at (%.3f,1.62) {%s};" % (x + 0.36, d))
            for j, l in enumerate(lv):
                y = 0.42 + 0.22 * j
                on = cur[d] == l
                chg = d in change and not isinstance(change[d], tuple)
                st = ("hot" if chg else "cell, fill=accL, draw=acc") if on else "cell, text=sub!70"
                body.append(r"\node[%s, minimum width=0.74cm, minimum height=0.19cm, font=\tiny] at (%.3f,%.3f) {%s};"
                            % (st, x + 0.36, y, l))
            if d in fixed:
                hotf = d in change and isinstance(change[d], tuple)
                body.append(r"\node[font=\tiny\bfseries, text=white, fill=%s, rounded corners=1pt, inner sep=0.8pt,"
                            r" text width=0.72cm, align=center] at (%.3f,0.16) {%s};"
                            % ("mkc" if hotf else "sub", x + 0.36, fixed[d]))
        out.append(K.panel(T, fig, k, title, tech, body, 0.1 + 0.78 * nd, 2.3, key=(k == keystep)))
    return out


def fig_61(sec):
    need(sec, "6.1", "Roll-up} on \\emph{date} from \\texttt{date\\_key} to \\texttt{year}",
         "Roll-up} on \\emph{game} to \\texttt{all}", "Dice} with", r"2^4 = \mathbf{16}")
    dims = [("date", ["day", "month", "quarter", "year", "all"]),
            ("spectator", ["key", "status", "all"]),
            ("location", ["key", "name", "city", "province", "all"]),
            ("game", ["key", "all"])]
    steps = [("Roll-up date", ["ROLL"], {"date": "year"}),
             ("Roll-up spectator", ["ROLL"], {"spectator": "status"}),
             ("Roll-up location", ["ROLL"], {"location": "name"}),
             ("Game to all", ["ALL"], {"game": "all"}),
             ("Dice on three", ["DICE"], {"date": ("=", "2021"), "spectator": ("=", "student"),
                                          "location": ("=", "Dashrath")})]
    p = olap_fig("6.1", dims, steps, 5)
    return K.rows(p[:3], p[3:])


def fig_62(sec):
    need(sec, "6.2", "Roll-up} on \\emph{time} from \\texttt{day} to \\texttt{year}",
         "Roll-up} on \\emph{location} from \\texttt{city} to \\texttt{state}",
         "Roll-up} on \\emph{supplier} to \\texttt{all}", "Roll-up} on \\emph{product} to \\texttt{all}",
         "Slice} on \\texttt{brand", r"2^5 = \mathbf{32}")
    dims = [("time", ["day", "month", "year", "all"]),
            ("location", ["city", "state", "country", "all"]),
            ("supplier", ["supplier", "all"]),
            ("brand", ["brand", "all"]),
            ("product", ["product", "all"])]
    steps = [("Roll-up time", ["ROLL"], {"time": "year"}),
             ("Roll-up location", ["ROLL"], {"location": "state"}),
             ("Supplier, product to all", ["ALL"], {"supplier": "all", "product": "all"}),
             ("Slice on brand", ["SLICE"], {"brand": ("=", "given")})]
    p = olap_fig("6.2", dims, steps, 4)
    return K.rows(p[:2], p[2:])


# =====================================================================
#  M7 descriptive
# =====================================================================
def fig_median(fig, sec, edges, freq, unit, ans_s, scale=1):
    N = sum(freq)
    cum = [sum(freq[:i + 1]) for i in range(len(freq))]
    k = next(i for i, c in enumerate(cum) if c >= N / 2)
    below = cum[k - 1] if k else 0
    L1, width = edges[k], edges[k + 1] - edges[k]
    med = L1 + (N / 2 - below) / freq[k] * width
    need(sec, fig, ans_s)
    num = "".join(ch for ch in ans_s if ch.isdigit() or ch == ".")
    if abs(med * scale - float(num)) > 1e-6:
        sys.exit("%s: median %.4f vs %s" % (fig, med, ans_s))
    WB = 4.6
    body = []
    n = len(freq)
    bw = (WB - 0.7) / n
    for i, (fq, c) in enumerate(zip(freq, cum)):
        x = 0.6 + bw * i
        hot = i == k
        hh = 1.15 * c / N
        body.append(r"\fill[%s] (%.3f,0.35) rectangle (%.3f,%.3f);" % ("mkL" if hot else "accL", x + 0.03, x + bw - 0.03,
                                                                       0.35 + hh))
        body.append(r"\draw[%s] (%.3f,0.35) rectangle (%.3f,%.3f);" % ("mkc" if hot else "acc", x + 0.03, x + bw - 0.03,
                                                                       0.35 + hh))
        body.append(r"\node[font=\tiny\bfseries, anchor=south, inner sep=0.5pt] at (%.3f,%.3f) {%d};"
                    % (x + bw / 2, 0.35 + hh, c))
        body.append(r"\node[font=\tiny, text=sub, anchor=north, inner sep=0.8pt] at (%.3f,0.35) {%s};"
                    % (x + bw / 2, fmt(edges[i]) + unit))
    yh = 0.35 + 1.15 * 0.5
    body.append(r"\draw[mkc, dashed] (0.6,%.3f) -- (%.3f,%.3f);" % (yh, WB - 0.1, yh))
    body.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=east] at (0.58,%.3f) {$N/2$};" % yh)
    p1 = K.panel(T, fig, 1, "Cumulative freq. to $N/2 = %s$" % fmt(N / 2), ["CUM"], body, WB, 2.5, key=True)
    body = []
    x0, x1 = 0.2, 3.9
    body.append(r"\fill[mkL, draw=mkc] (%.2f,1.15) rectangle (%.2f,1.45);" % (x0, x1))
    fr = (N / 2 - below) / freq[k]
    body.append(r"\fill[mkc!45] (%.2f,1.15) rectangle (%.3f,1.45);" % (x0, x0 + (x1 - x0) * fr))
    body.append(r"\node[font=\tiny, anchor=north] at (%.2f,1.13) {%s};" % (x0, fmt(L1) + unit))
    body.append(r"\node[font=\tiny, anchor=north] at (%.2f,1.13) {%s};" % (x1, fmt(L1 + width) + unit))
    body.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=south] at (%.3f,1.45) {%s};"
                % (x0 + (x1 - x0) * fr, "median"))
    body.append(txt(0, 0.72, r"%d values before this interval; need %s more of its %d:"
                    % (below, fmt(N / 2 - below), freq[k]), 4.2))
    def full(v):
        # the table is in $1000s when scale > 1: print the equation in dollars
        return "{:,}".format(int(round(v * scale))).replace(",", "{,}") if scale > 1 else fmt(v)

    body.append(txt(0, 0.4, r"$%s + \frac{%s}{%d}\times %s = \mathbf{%s}$" % (full(L1), fmt(N / 2 - below), freq[k],
                                                                           full(width), ans_s), 4.2))
    p2 = K.panel(T, fig, 2, "Interpolate inside it", ["INTERP"], body, 4.2, 2.5)
    return grid([p1, p2], 2)


def fig_73(sec):
    need(sec, "7.3", r"3(55) - 2(60) = 165 - 120 = \mathbf{45}")
    body, X = nline(1.0, 40, 65, [(45, "mode 45", "mkc"), (55, "median 55", "cB"), (60, "mean 60", "cA")],
                    [40, 50, 60])
    body.append(txt(0, 0.55, r"mode $\approx 3(55) - 2(60) = \mathbf{45}$. Order mode $<$ median $<$ mean:"
                             r" a long right tail, \textbf{positive skew}.", W))
    return K.single(K.panel(T, "7.3", 1, "Mean, median, mode on one line", ["EMP"], body, W, HH, key=True))


def fig_74(sec):
    d = [30, 36, 47, 50, 52, 52, 56, 60, 63, 70, 70, 110]
    n = len(d)
    need(sec, "7.4", r"mean = \frac{696}{12} = \mathbf{58}", r"median = \frac{52+56}{2} = \mathbf{54}",
         r"\mathbf{47.75}", r"\mathbf{68.25}", r"\mathbf{20.5}", "17.0", "99.0")

    def q(k):
        pos = k * (n + 1) / 4
        i = int(pos)
        return d[i - 1] + (pos - i) * (d[i] - d[i - 1])

    q1, q3 = q(1), q(3)
    if (q1, q(2), q3) != (47.75, 54.0, 68.25):
        sys.exit("7.4 quartiles")
    f = "7.4"
    body = cells(0.05, 1.45, [str(x) for x in d], cw=0.335, fills={4: "cB", 5: "cB", 9: "cB", 10: "cB"})
    body.append(txt(0, 1.15, r"$\sum = 696$, mean $\mathbf{58}$; median $(52+56)/2 = \mathbf{54}$;"
                             r" modes 52 and 70 (orange): \textbf{bimodal}.", 4.1))
    p1 = K.panel(T, f, 1, "Centre", ["MEAN"], body, 4.1, HH)
    body = cells(0.05, 1.45, [str(x) for x in d], cw=0.335, fills={2: "mkc", 3: "mkc", 8: "mkc", 9: "mkc"})
    for pos, lab in ((3.25, "$Q_1$"), (6.5, "$Q_2$"), (9.75, "$Q_3$")):
        x = 0.05 + 0.335 * (pos - 0.5)
        body.append(r"\draw[-{Stealth[length=1.2mm]}, mkc, line width=0.7pt] (%.3f,1.08) -- (%.3f,1.28);" % (x, x))
        body.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=north] at (%.3f,1.08) {%s};" % (x, lab))
    body.append(txt(0, 0.72, r"$Q_1$ at 3.25: $47 + 0.25(3) = \mathbf{47.75}$\\$Q_3$ at 9.75: $63 + 0.75(7) ="
                             r" \mathbf{68.25}$; \ IQR $\mathbf{20.5}$", 4.1))
    p2 = K.panel(T, f, 2, "Quartile positions $k(n+1)/4$", ["QPOS"], body, 4.1, HH, key=True)
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    body, X = nline(1.0, 10, 115, [(x, "", "mkc" if x > hi else "cA") for x in d], [17, 99], w=4.1)
    body.append(r"\fill[gdL, opacity=0.6] (%.3f,0.9) rectangle (%.3f,1.1);" % (X(lo), X(hi)))
    for v in (lo, hi):
        body.append(r"\draw[gd, line width=0.8pt] (%.3f,0.85) -- (%.3f,1.15);" % (X(v), X(v)))
    body.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=south] at (%.3f,1.08) {110};" % X(110))
    body.append(txt(0, 0.55, r"Fences $47.75 - 30.75 = 17.0$ and $68.25 + 30.75 = 99.0$: only \textbf{110}"
                             r" is outside.", 4.1))
    p3 = K.panel(T, f, 3, "Fences", ["FENCE"], body, 4.1, HH)
    return grid([p1, p2, p3], 3)


# =====================================================================
#  Build
# =====================================================================
def build():
    tex = open(TEX, encoding="utf-8").read()
    S = lambda a, b=None: K.section(tex, a, b)
    figs = [
        ("c2s_step_11", fig_11(S(r"\creamq{Problem 1.1}", r"\creamq{Problem 1.2")),
         "Step by step: three ways to normalise the same five values"),
        ("c2s_step_12", fig_12(S(r"\creamq{Problem 1.2", r"\T{M2.")),
         "Step by step: bins of three, then the value 35 three ways"),
        ("c2s_step_21", fig_pca(S(r"\creamq{Problem 2.1}", r"\T{M3.")),
         "Step by step: eigenvalues, the check, the vectors, the variance kept"),
        ("c2s_step_warm", fig_warm(S(r"\creamq{Warm-up", r"\creamq{Problem 3.1}")),
         "Step by step: the same two points, three distances"),
        ("c2s_step_31", fig_31(S(r"\creamq{Problem 3.1}", r"\creamq{Problem 3.2}")),
         "Step by step: plot, then fill each matrix's lower triangle"),
        ("c2s_step_32", fig_32(S(r"\creamq{Problem 3.2}", r"\T{M4.")),
         "Step by step: differences, then square, sum and root"),
        ("c2s_step_41", fig_cos("4.1", S(r"\creamq{Problem 4.1}", r"\creamq{Problem 4.2}"),
                                (3, 53, 8, 11), (9, 55, 7, 12), ("O_2", "O_4"), "= 3130", r"\sqrt{3003} = 54.800",
                                r"\sqrt{3299} = 57.437", "0.9944", ["Size", "Wt", "Col", "Taste"]),
         "Step by step: cosine of objects 2 and 4 (the weight term dominates)"),
        ("c2s_step_42", fig_cos("4.2", S(r"\creamq{Problem 4.2}", r"\creamq{Problem 4.3}"),
                                (4, 1, 2, 0, 2, 0, 0), (2, 1, 3, 0, 1, 1, 1), ("d_1", "d_2"), "= 17",
                                r"\sqrt{25} = 5", r"\sqrt{17} = 4.1231", "0.8246"),
         "Step by step: cosine of the two documents"),
        ("c2s_step_43", fig_cos("4.3", S(r"\creamq{Problem 4.3}", r"\T{M5."),
                                (4, 0, 2, 0, 1), (2, 0, 0, 2, 2), ("D_1", "D_2"), "= 10",
                                r"\sqrt{21} = 4.5826", r"\sqrt{12} = 3.4641", "0.6299"),
         "Step by step: cosine of the two vectors"),
        ("c2s_step_51", fig_51(S(r"\creamq{Problem 5.1}", r"\creamq{Problem 5.2}")),
         "Step by step: tally the pairs, then Jaccard and SMC"),
        ("c2s_step_52", fig_52(S(r"\creamq{Problem 5.2}", r"\T{M6.")),
         "Step by step: decide the attribute types first, then tally each pair"),
        ("c2s_step_61", fig_61(S(r"\creamq{Problem 6.1}", r"\creamq{Problem 6.2}")),
         "Step by step: each dimension's level after every OLAP operation (orange = changed)"),
        ("c2s_step_62", fig_62(S(r"\creamq{Problem 6.2}", r"\T{M7.")),
         "Step by step: each dimension's level after every OLAP operation (orange = changed)"),
        ("c2s_step_71", fig_median("7.1", S(r"\creamq{Problem 7.1", r"\creamq{Problem 7.2"),
                                   [10, 20, 30, 40, 50, 60, 70], [8, 15, 20, 32, 18, 7], "k",
                                   r"\$42{,}187.50", scale=1000),
         "Step by step: find the median interval, then interpolate"),
        ("c2s_step_72", fig_median("7.2", S(r"\creamq{Problem 7.2", r"\creamq{Problem 7.3"),
                                   [10, 20, 30, 40, 50, 60, 70], [5, 8, 12, 20, 10, 5], "", "42.5"),
         "Step by step: find the median interval, then interpolate"),
        ("c2s_step_73", fig_73(S(r"\creamq{Problem 7.3", r"\creamq{Problem 7.4")),
         "Step by step: the three centres on one line"),
        ("c2s_step_74", fig_74(S(r"\creamq{Problem 7.4", r"\T{Extra practice")),
         "Step by step: centre, quartiles, fences"),
        ("c2s_step_pa", fig_pa(S(r"\creamq{Practice A", r"\creamq{Practice B")),
         "Step by step: equal-depth bins, boundaries, and equal width for contrast"),
        ("c2s_step_pb", fig_pb(S(r"\creamq{Practice B")),
         "Step by step: one income, mapped into two ranges"),
    ]
    out = [("c2s_index", T.index())]
    for name, fig, cap in figs:
        CAPTION[name] = cap
        out.append((name, fig))
    return out


def main():
    figs = build()
    if "--report" in sys.argv:
        for n, _ in figs:
            print("ok  %s" % n)
        return
    K.render([("pre", K.preamble(T))] + figs, TEX, PREFIX, CAPTION, scale={"c2s_index": 0.78})


if __name__ == "__main__":
    main()
