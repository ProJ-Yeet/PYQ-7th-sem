# -*- coding: utf-8 -*-
"""Draw the boxplot that ch2-num Problem 7.4 (e) describes in words.

Recomputes the interpolated quartiles, fences and the largest non-outlier from
the 12 salaries, checks each against the values the notes print, then draws
the box, whiskers, fences and the lone outlier to scale.

    python boxfig.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch2-num.tex")
FIGS = os.path.join(HERE, "figs")
INK, SUB, ACC, ACCL, MKC = "#16202A", "#6B7785", "#2563A8", "#D6E4F5", "#C2410C"


def q(data, k):
    pos = k * (len(data) + 1) / 4
    lo = int(pos)
    return data[lo - 1] + (pos - lo) * (data[lo] - data[lo - 1])


def main():
    src = open(TEX, encoding="utf-8").read()
    d = [30, 36, 47, 50, 52, 52, 56, 60, 63, 70, 70, 110]
    q1, q2, q3 = q(d, 1), q(d, 2), q(d, 3)
    iqr = q3 - q1
    lo_f, hi_f = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    wl = min(x for x in d if x >= lo_f)
    wh = max(x for x in d if x <= hi_f)
    out = [x for x in d if x < lo_f or x > hi_f]
    for text in (r"\mathbf{30,\ 47.75,\ 54,\ 68.25,\ 110}",
                 "$47.75 - 1.5(20.5) = 17.0$", "$68.25 + 1.5(20.5) = 99.0$",
                 "whiskers to 30 and to the largest non-outlier (70)"):
        if text not in src:
            sys.exit("ch2-num.tex does not print %r" % text)
    assert (q1, q2, q3, lo_f, hi_f, wl, wh, out) == (47.75, 54.0, 68.25, 17.0, 99.0, 30, 70, [110])

    fig, ax = plt.subplots(figsize=(5.2, 1.35))
    y, h = 0.0, 0.5
    ax.add_patch(plt.Rectangle((q1, y - h / 2), iqr, h, fc=ACCL, ec=ACC, lw=1.2))
    ax.plot([q2, q2], [y - h / 2, y + h / 2], color=ACC, lw=2.0)
    for a, b in ((wl, q1), (q3, wh)):
        ax.plot([a, b], [y, y], color=ACC, lw=1.1)
    for w in (wl, wh):
        ax.plot([w, w], [y - h / 4, y + h / 4], color=ACC, lw=1.1)
    for f in (lo_f, hi_f):
        ax.axvline(f, color=SUB, lw=0.8, ls=(0, (3, 2)))
    ax.plot(out, [y] * len(out), "o", ms=6, mfc="white", mec=MKC, mew=1.5)
    for x, lab in ((wl, "min 30"), (q2, "median 54"), (wh, "max non-outlier 70"),
                   (110, "outlier 110")):
        ax.text(x, y + h / 2 + 0.08, lab, ha="left" if x == wh else "center", va="bottom",
                fontsize=6.8, color=MKC if x == 110 else INK)
    for x, lab in ((q1, "$Q_1$ 47.75"), (q3, "$Q_3$ 68.25")):
        ax.text(x, y - h / 2 - 0.08, lab, ha="center", va="top", fontsize=6.8, color=INK)
    ax.text(lo_f + 1, 0.72, "fence 17", ha="left", va="top", fontsize=6.4, color=SUB)
    ax.text(hi_f - 1, 0.72, "fence 99", ha="right", va="top", fontsize=6.4, color=SUB)
    ax.set_xlim(10, 118)
    ax.set_ylim(-0.75, 0.8)
    ax.set_yticks([])
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", labelsize=7, colors=SUB)
    ax.set_xlabel("salary (\\$1000s)", fontsize=7, color=SUB)
    fig.savefig(os.path.join(FIGS, "c2n_boxplot_74.png"), dpi=220, bbox_inches="tight",
                pad_inches=0.03)
    plt.close(fig)
    print("boxfig: boxplot written, five-number summary and fences match ch2-num.tex")


if __name__ == "__main__":
    main()
