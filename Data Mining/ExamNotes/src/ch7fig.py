# -*- coding: utf-8 -*-
"""Draw the step-by-step solution under the chapter-7 numerical in ch7-num.tex.

The PageRank question is really about reading the graph: which links leave a
page (the divisor) and which arrive (the sum). The panels draw the graph with
out-degrees on it, then the five iterations as four climbing lines, then the
two things worth saying in the exam: the ORDER settles at iteration 3 while
the values are still rising, and the exact fixed point sums to N.

Exit test is replay: the iteration table, the fixed point and the normalised
variant are recomputed here and must match the numbers the notes print.

    python ch7fig.py            regenerate every figure and its block in ch7-num.tex
    python ch7fig.py --report   run the checks only
"""
import decimal
import os
import sys

import stepkit as K

TEX = os.path.join(K.HERE, "ch7-num.tex")
PREFIX = "ch7fig"

T = K.Techs([
    ("LINKS", "outlinks vs inlinks", "Outlinks give the divisor $C$; inlinks say which terms to add."),
    ("SPLIT", "split a rank", "A page's rank is shared equally among the pages it links to."),
    ("SYNC", "use the old values", "Compute every page from the PREVIOUS iteration, then substitute together."),
    ("NOIN", "no inlinks", "A page nothing points at stays at $1-d$ for ever."),
    ("ORDER", "order before value", "The ranking settles long before the numbers stop moving."),
    ("SUMN", "sum check", "In this form the converged ranks add up to $N$."),
    ("NORMF", "normalised form", "$\\frac{1-d}{N}$ instead of $1-d$: the same ordering, ranks summing to 1."),
])

CAPTION = {"c7s_index": "The moves the chapter-7 numerical below is built from"}
COLS = ["cA", "cB", "cC", "cD"]
OUT = {"A": ["B", "C"], "B": ["C"], "C": ["A"], "D": ["C"]}
PAGES = ["A", "B", "C", "D"]


def txt(x, y, s, w=None, style="eqn"):
    if w:
        return r"\node[%s, text width=%.2fcm] at (%.3f,%.3f) {%s};" % (style, w, x, y, s)
    return r"\node[%s] at (%.3f,%.3f) {%s};" % (style, x, y, s)


def iterate(pr, d=0.85, base=None, places=None):
    """One pass. places=4 reproduces the table, which carries each row rounded.

    Done in Decimal: in float, 0.15 + 0.85(0.351) lands at 0.44834999..., which
    rounds to 0.4483, while the table's exact 0.44835 is printed 0.4484.
    """
    D = decimal.Decimal
    dd = D(str(d))
    base = (1 - dd) if base is None else D(str(base))
    new = {}
    for p in PAGES:
        s = sum((D(str(pr[q])) / len(OUT[q]) for q in PAGES if p in OUT[q]), D(0))
        v = base + dd * s
        new[p] = float(v.quantize(D("1." + "0" * places), rounding=decimal.ROUND_HALF_UP)) if places \
            else float(v)
    return new


def build():
    tex = open(TEX, encoding="utf-8").read()
    S = lambda a, b=None: K.section(tex, a, b)
    s = S(r"\creamq{Problem 1.1}", r"\creamq{Practice")

    rows = [{p: 0.25 for p in PAGES}]
    for _ in range(5):
        rows.append(iterate(rows[-1], places=4))
    for r in rows[1:]:
        for p in PAGES:
            K.need(s, "1.1", "%.4f" % r[p])
    # exact fixed point
    fp = dict(rows[-1])
    for _ in range(3000):
        fp = iterate(fp)
    K.need(s, "1.1", "PR(A)=1.490", "PR(B)=0.783", "PR(C)=1.577")
    if abs(sum(fp.values()) - 4) > 1e-6 or abs(fp["A"] - 1.490) > 5e-4:
        sys.exit("1.1: fixed point %s" % fp)

    W, Hh = 4.3, 2.9
    pos = {"A": (0.55, 2.0), "B": (2.1, 2.0), "C": (2.1, 0.95), "D": (0.55, 0.95)}
    L = []
    for a, outs in OUT.items():
        for b in outs:
            (x1, y1), (x2, y2) = pos[a], pos[b]
            dx, dy = x2 - x1, y2 - y1
            n = (dx ** 2 + dy ** 2) ** 0.5
            ux, uy = dx / n * 0.26, dy / n * 0.26
            L.append(r"\draw[-{Stealth[length=1.6mm]}, sub, line width=0.7pt] (%.2f,%.2f) -- (%.2f,%.2f);"
                     % (x1 + ux, y1 + uy, x2 - ux, y2 - uy))
    for p, (x, y) in pos.items():
        L.append(r"\node[circle, draw=%s, fill=%sL, line width=0.8pt, minimum size=6.5mm, inner sep=0pt,"
                 r" font=\scriptsize\bfseries] at (%.2f,%.2f) {%s};" % (COLS[PAGES.index(p)],
                                                                       COLS[PAGES.index(p)], x, y, p))
        L.append(r"\node[font=\tiny, text=sub, anchor=north] at (%.2f,%.2f) {$C=%d$};"
                 % (x, y - 0.22, len(OUT[p])))
    L.append(txt(2.75, 2.15, r"inlinks:\\A $\leftarrow$ C\\B $\leftarrow$ A\\C $\leftarrow$ A, B, D\\"
                             r"D $\leftarrow$ \textbf{none}", 1.5, "note"))
    p1 = K.panel(T, "1.1", 1, "Read the graph", ["LINKS", "SPLIT"], L, W, Hh)

    L = [txt(0, 2.1, r"$PR(A) = 0.15 + 0.85\,PR(C)$", W),
         txt(0, 1.75, r"$PR(B) = 0.15 + 0.85\,\frac{PR(A)}{2}$", W),
         txt(0, 1.3, r"$PR(C) = 0.15 + 0.85\big(\frac{PR(A)}{2} + PR(B) + PR(D)\big)$", W),
         txt(0, 0.75, r"$PR(D) = 0.15$ \ \textbf{for ever}", W),
         txt(0, 0.4, r"$A$ is halved: it links to both B and C.", W, "note")]
    p2 = K.panel(T, "1.1", 2, "Write the four equations", ["SPLIT", "NOIN"], L, W, Hh)

    WG = 5.4
    x0, y0, x1, y1 = 0.45, 0.62, WG - 0.15, Hh - 0.62 - 0.12
    hi = 1.1

    def M(it, v):
        return x0 + it / 5 * (x1 - x0), y0 + v / hi * (y1 - y0)

    L = [r"\draw[ruleL] (%.2f,%.2f) rectangle (%.2f,%.2f);" % (x0, y0, x1, y1)]
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        L.append(r"\node[font=\tiny, text=sub, anchor=east, inner sep=1pt] at (%.2f,%.2f) {%.2f};"
                 % (x0, M(0, v)[1], v))
        L.append(r"\draw[ruleL] (%.2f,%.2f) -- (%.2f,%.2f);" % (x0, M(0, v)[1], x1, M(0, v)[1]))
    for it in range(6):
        L.append(r"\node[font=\tiny, text=sub, anchor=north, inner sep=1pt] at (%.2f,%.2f) {%d};"
                 % (M(it, 0)[0], y0, it))
    for k, p in enumerate(PAGES):
        pts = " -- ".join("(%.3f,%.3f)" % M(i, min(r[p], hi)) for i, r in enumerate(rows))
        L.append(r"\draw[%s, line width=0.8pt] %s;" % (COLS[k], pts))
        L.append(r"\node[font=\tiny\bfseries, text=%s, anchor=west, inner sep=1pt] at (%.3f,%.3f) {%s};"
                 % (COLS[k], M(5, min(rows[5][p], hi))[0] + 0.04, M(5, min(rows[5][p], hi))[1], p))
    L.append(txt(0, 0.4, r"After 5: A %.4f, B %.4f, C %.4f, D %.4f" % tuple(rows[5][p] for p in PAGES),
                 WG, "note"))
    p3 = K.panel(T, "1.1", 3, "Five iterations, all from the previous row", ["SYNC"], L, WG, Hh, key=True)

    L = []
    for i, r in enumerate(rows):
        order = " $>$ ".join(sorted(PAGES, key=lambda p: -r[p]))
        stable = i >= 3
        L.append(r"\node[font=\tiny%s, anchor=west] at (0.1,%.2f) {%d:\ %s};"
                 % (r"\bfseries, text=gd" if stable else ", text=sub", 2.05 - i * 0.28, i, order))
    L.append(txt(0, 0.5, r"The \textbf{order} stops changing at iteration 3 while the values are still"
                         r" climbing. That is why 5 iterations answer the question.", W))
    p4 = K.panel(T, "1.1", 4, "Order settles before value", ["ORDER"], L, W, Hh)

    L = [txt(0, 2.1, r"Exact fixed point:", W),
         txt(0, 1.75, r"$A\,1.490$, \ $B\,0.783$, \ $C\,1.577$, \ $D\,0.150$", W),
         txt(0, 1.3, r"$1.490 + 0.783 + 1.577 + 0.150 = \mathbf{4.00} = N$", W),
         txt(0, 0.8, r"In this (non-normalised) form the ranks always converge to the number of"
                     r" pages: that sum is the check.", W, "note")]
    p5 = K.panel(T, "1.1", 5, "Sum check", ["SUMN"], L, W, Hh)

    figs = [("c7s_step_11", K.rows([p1, p2, p3], [p4, p5]))]
    CAPTION["c7s_step_11"] = "Step by step: the graph, the equations, five iterations, and the two checks"

    # practice: normalised
    s = S(r"\creamq{Practice")
    n1 = iterate({p: 0.25 for p in PAGES}, base=0.15 / 4, places=4)
    for p in PAGES:
        K.need(s, "Practice", "%.4f" % n1[p])
    if abs(sum(n1.values()) - 1.0001) > 1e-3:
        sys.exit("Practice: sum %.4f" % sum(n1.values()))
    L = [txt(0, 2.1, r"$\frac{1-d}{N} = \frac{0.15}{4} = 0.0375$ replaces $0.15$", W),
         txt(0, 1.7, r"Iteration 1: A %.4f, B %.4f, C %.4f, D %.4f" % tuple(n1[p] for p in PAGES), W),
         txt(0, 1.25, r"Sum $= %.4f \approx 1$: the check for this form." % sum(n1.values()), W),
         txt(0, 0.8, r"Same ordering C $>$ A $>$ B $>$ D, only the scale differs. State which form"
                     r" you are using.", W, "note")]
    figs.append(("c7s_step_pr", K.single(K.panel(T, "Practice", 1, "The normalised form", ["NORMF"], L, W, Hh,
                                                 key=True))))
    CAPTION["c7s_step_pr"] = "Step by step: the same graph in the normalised form (ranks sum to 1)"
    return [("c7s_index", T.index())] + figs


def main():
    figs = build()
    if "--report" in sys.argv:
        for n, _ in figs:
            print("ok  %s" % n)
        return
    K.render([("pre", K.preamble(T))] + figs, TEX, PREFIX, CAPTION)


if __name__ == "__main__":
    main()
