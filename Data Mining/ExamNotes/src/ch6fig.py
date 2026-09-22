# -*- coding: utf-8 -*-
"""Draw the step-by-step solution under every chapter-6 numerical in ch6-num.tex.

The base rate fallacy is a picture argument: a population bar split 99 to 1,
the same two error rates applied to each part, and the alarm bar that comes
out half false. Practice A repeats it with anomalies ten times rarer, where
the alarm bar collapses to 9 %. Practice B draws the DB(r, pi) test as
circles of radius r with the neighbour count under each point.

Exit test is replay: every count and rate a panel shows is recomputed from
the probabilities the question gives and must be printed in the problem.

    python ch6fig.py            regenerate every figure and its block in ch6-num.tex
    python ch6fig.py --report   run the checks only
"""
import math
import os
import sys

import stepkit as K

TEX = os.path.join(K.HERE, "ch6-num.tex")
PREFIX = "ch6fig"

T = K.Techs([
    ("POP", "round population", "Invent a round population and count objects; no formula to misremember."),
    ("RATES", "apply both rates", "Detection rate hits the anomalies, false alarm rate hits the much larger normal group."),
    ("BAYES", "read the alarm bar", "$P(I|A)$ = true alarms / all alarms, which is what an analyst sees."),
    ("BASE", "base rate moved", "Same detector, rarer anomalies: only the prior changed, and $P(I|A)$ collapses."),
    ("RADIUS", "count within $r$", "Count the objects within $r$, the point itself included."),
    ("PI", "compare with $\\pi$", "Outlier when that count over $|D|$ is at most $\\pi$."),
    ("KNN", "$k$-NN cross-check", "With $k = \\lceil \\pi|D|\\rceil$, outlier iff the $k$-th neighbour is farther than $r$."),
])

CAPTION = {"c6s_index": "The moves every chapter-6 numerical below is built from"}


def txt(x, y, s, w=None, style="eqn"):
    if w:
        return r"\node[%s, text width=%.2fcm] at (%.3f,%.3f) {%s};" % (style, w, x, y, s)
    return r"\node[%s] at (%.3f,%.3f) {%s};" % (style, x, y, s)


def bar(x, y, w, h, parts):
    """parts = [(share, colour, label)] drawn left to right."""
    L, cx = [], x
    tot = sum(p[0] for p in parts) or 1
    for v, c, lab in parts:
        dw = w * v / tot
        L.append(r"\fill[%sL, draw=%s, line width=0.5pt] (%.3f,%.3f) rectangle (%.3f,%.3f);" % (c, c, cx, y, cx + dw, y + h))
        if lab and dw > 0.6:
            L.append(r"\node[font=\tiny\bfseries, text=%s] at (%.3f,%.3f) {%s};" % (c, cx + dw / 2, y + h / 2, lab))
        elif lab:
            # a sliver too narrow for its label: set it above the bar
            L.append(r"\node[font=\tiny\bfseries, text=%s, anchor=south, inner sep=1pt] at (%.3f,%.3f) {%s};"
                     % (c, cx + dw / 2, y + h, lab))
        cx += dw
    return L


def fallacy(fig, sec, N, prior, dr, far, pia_s, W=4.4, Hh=2.5):
    an = round(N * prior)
    no = N - an
    tp = round(dr * an)
    fp = round(far * no)
    pia = tp / (tp + fp)
    for v in (an, no, tp, fp):
        # the notes write thousands both ways: 9,900 and 9801
        forms = {str(v), "{:,}".format(v), "{:,}".format(v).replace(",", "{,}")}
        if not any(f in K.flat(sec) for f in forms):
            sys.exit("%s: none of %s is printed" % (fig, sorted(forms)))
    K.need(sec, fig, pia_s)
    if abs(pia - float(pia_s)) > 5e-4:
        sys.exit("%s: P(I|A) %.4f vs %s" % (fig, pia, pia_s))
    b = bar(0.1, 1.25, W - 0.3, 0.42, [(no, "cA", "normal %s" % "{:,}".format(no)),
                                       (an, "cB", "%d" % an)])
    b.append(txt(0, 0.95, r"A population of %s: %s normal, \textbf{%d} anomalous."
                 % ("{:,}".format(N).replace(",", "{,}"), "{:,}".format(no).replace(",", "{,}"), an), W, "note"))
    p1 = K.panel(T, fig, 1, "Take a round population", ["POP"], b, W, Hh)
    body = []
    for i, (lab, tot, hit, col, note) in enumerate((("anomalous %d" % an, an, tp, "cB",
                                                     r"detection rate %g" % dr),
                                                    ("normal %s" % "{:,}".format(no).replace(",", "{,}"), no, fp, "cA",
                                                     r"false alarm rate %g" % far))):
        y = 1.35 - i * 0.55
        body += bar(0.1, y, max(0.9, (W - 0.3) * (tot / N) ** 0.35), 0.34, [(1, col, lab)])
        body.append(txt(0, y - 0.04, r"$\rightarrow$ \textbf{%d} alarms \ {\color{sub}(%s)}" % (hit, note), W))
    p2 = K.panel(T, fig, 2, "Apply the two rates", ["RATES"], body, W, Hh)
    b = bar(0.1, 1.3, W - 0.3, 0.42, [(tp, "cB", "true %d" % tp), (fp, "cA", "false %d" % fp)])
    b.append(txt(0, 0.95, r"$P(I|A) = \dfrac{%d}{%d + %d} = \mathbf{%s}$" % (tp, tp, fp, pia_s), W))
    b.append(txt(0, 0.45, r"Only %s\,\%% of alarms are real, from a detector that is 99\,\%% right both ways."
                 % ("{:.0f}".format(pia * 100)), W, "note"))
    p3 = K.panel(T, fig, 3, "The alarms an analyst sees", ["BAYES", "BASE"], b, W, Hh, key=True)
    return [p1, p2, p3]


def build():
    tex = open(TEX, encoding="utf-8").read()
    S = lambda a, b=None: K.section(tex, a, b)
    figs = []

    s = S(r"\creamq{Problem 1.1}", r"\creamq{Practice A")
    figs.append(("c6s_step_11", K.grid(fallacy("1.1", s, 10000, 0.01, 0.99, 0.01, "0.50"), 3)))
    CAPTION["c6s_step_11"] = "Step by step: why a 99\\% detector leaves half its alarms false"

    s = S(r"\creamq{Practice A", r"\T{M2.")
    figs.append(("c6s_step_pa", K.grid(fallacy("Practice A", s, 100000, 0.001, 0.99, 0.01, "0.090"), 3)))
    CAPTION["c6s_step_pa"] = "Step by step: the same detector, anomalies ten times rarer"

    # Practice B: DB(r, pi)
    s = S(r"\creamq{Practice B}")
    P = {"P_1": (1, 1), "P_2": (1, 2), "P_3": (2, 1), "P_4": (2, 2), "P_5": (8, 8)}
    r, pi = 2, 0.4
    cnt = {a: sum(1 for b in P if math.dist(P[a], P[b]) <= r + 1e-9) for a in P}
    out = [a for a in P if cnt[a] / len(P) <= pi]
    if out != ["P_5"] or cnt["P_1"] != 4:
        sys.exit("Practice B: counts")
    K.need(s, "Practice B", "4/5 = 0.8", "1/5 = 0.2", "8.485", r"k=\lceil 0.4\times5\rceil = 2")
    W, Hh = 4.6, 3.0
    x0, y0 = 0.35, 0.6
    sc = min((W - 0.6) / 9.0, (Hh - 0.62 - 0.8) / 9.0)   # keep P5(8,8) inside the panel

    def M(p):
        return x0 + p[0] * sc, y0 + p[1] * sc

    panels = []
    for step, mode in enumerate((0, 1, 2), 1):
        L = []
        for a, p in P.items():
            x, y = M(p)
            if mode == 0:
                L.append(r"\draw[acc!45, fill=accL, fill opacity=0.3] (%.3f,%.3f) circle (%.3f);" % (x, y, r * sc))
        for a, p in P.items():
            x, y = M(p)
            col = "mkc" if (mode and a in out) else ("gd" if mode else "sub")
            L.append(r"\node[dot, minimum size=1.8mm, fill=%s] at (%.3f,%.3f) {};" % (col, x, y))
            # the four cluster points sit one unit apart: push each label to its own corner
            anchor = {"P_1": "north east", "P_2": "south east", "P_3": "north west",
                      "P_4": "south west", "P_5": "south west"}[a]
            L.append(r"\node[font=\tiny, anchor=%s, inner sep=1pt] at (%.3f,%.3f) {$%s$};"
                     % (anchor, x, y, a))
        if mode == 0:
            note = r"Circles of radius $r = 2$ around every point."
            tech, title = ["RADIUS"], "Count within $r$"
        elif mode == 1:
            note = (r"Counts within $r$: $P_1$--$P_4$ have \textbf{4} each, $P_5$ has \textbf{1}."
                    r" \ $\pi|D| = 0.4 \times 5 = 2$: $4/5 = 0.8 > 0.4$ normal;"
                    r" $1/5 = 0.2 \le 0.4$ \textbf{outlier}.")
            tech, title = ["PI"], "Compare with $\\pi$"
        else:
            (ax, ay), (bx, by) = M(P["P_5"]), M(P["P_4"])
            L.append(r"\draw[mkc, dashed, line width=0.7pt] (%.3f,%.3f) -- (%.3f,%.3f);" % (ax, ay, bx, by))
            L.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=west, inner sep=1pt] at (%.3f,%.3f) {8.485};"
                     % ((ax + bx) / 2, (ay + by) / 2))
            note = (r"$k = \lceil 0.4\times5\rceil = 2$: $P_5$'s 2nd nearest is $8.485 > 2$ $\rightarrow$"
                    r" outlier, the same verdict.")
            tech, title = ["KNN"], "$k$-NN cross-check"
        L.append(txt(0, 0.42, note, W, "note"))
        panels.append(K.panel(T, "Practice B", step, title, tech, L, W, Hh, key=(mode == 1)))
    figs.append(("c6s_step_pb", K.grid(panels, 3)))
    CAPTION["c6s_step_pb"] = "Step by step: the DB$(2, 0.4)$ test, and the $k$-NN form of the same test"

    return [("c6s_index", T.index())] + figs


def main():
    figs = build()
    if "--report" in sys.argv:
        for n, _ in figs:
            print("ok  %s" % n)
        return
    K.render([("pre", K.preamble(T))] + figs, TEX, PREFIX, CAPTION)


if __name__ == "__main__":
    main()
