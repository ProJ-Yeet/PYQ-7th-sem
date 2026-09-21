# -*- coding: utf-8 -*-
"""Draw the dendrograms the chapter-5 hierarchical-clustering numericals ask for.

Three PYQs say "draw the dendrogram" (80 Bh single link, 80 Ba complete link,
76 Ch both). The merges are replayed here from the distance matrix the paper
prints, with the notes' own tie rule (among equal minima take the pair met
first reading the current matrix, merged clusters appended as new last rows),
and the replay is asserted against the merge list and heights ch5-num.tex
prints before anything is drawn. Each merge is numbered on the figure in the
order it happens, so the picture doubles as the step list.

    python dendfig.py
"""
import itertools
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
TEX = os.path.join(HERE, "ch5-num.tex")

INK, SUB, ACC, MKC, GRID = "#16202A", "#6B7785", "#2563A8", "#C2410C", "#DEE3E8"


def replay(labels, d, link):
    """Agglomerative clustering with the notes' tie rule. Returns merges as
    (left, right, height) where left/right are nested tuples of labels."""
    rows = [(l,) for l in labels]                 # leaves as 1-tuples
    trees = {(l,): l for l in labels}
    dist = {}
    for a, b in itertools.combinations(labels, 2):
        v = d.get((a, b), d.get((b, a)))
        dist[frozenset([(a,), (b,)])] = v
    merges = []
    while len(rows) > 1:
        best = None
        for i, j in itertools.combinations(range(len(rows)), 2):
            v = dist[frozenset([rows[i], rows[j]])]
            if best is None or v < best[0] - 1e-12:
                best = (v, i, j)
        v, i, j = best
        x, y = rows[i], rows[j]
        new = x + y
        trees[new] = (trees[x], trees[y])
        merges.append((trees[x], trees[y], v, new))
        rows = [r for k, r in enumerate(rows) if k not in (i, j)]
        for r in rows:
            a, b = dist[frozenset([x, r])], dist[frozenset([y, r])]
            dist[frozenset([new, r])] = min(a, b) if link == "single" else max(a, b)
        rows.append(new)
    return merges, trees[rows[0]]


def leaves(t):
    return [t] if isinstance(t, str) else leaves(t[0]) + leaves(t[1])


def draw(ax, merges, root, title, cut=None, fmt="%.2f", ymax=None):
    order = leaves(root)
    xpos = {l: i for i, l in enumerate(order)}
    top = {}                                     # subtree -> (x, height)
    for l in order:
        top[l] = (xpos[l], 0.0)
    for k, (a, b, h, _) in enumerate(merges, 1):
        (xa, ha), (xb, hb) = top[a], top[b]
        ax.plot([xa, xa, xb, xb], [ha, h, h, hb], color=ACC, lw=1.6,
                solid_joinstyle="miter")
        xm = (xa + xb) / 2.0
        top[(a, b)] = (xm, h)
        ax.text(xm, h, str(k), ha="center", va="bottom", fontsize=7.2, color="white",
                bbox=dict(boxstyle="circle,pad=0.18", fc=MKC, ec="none"))
        ax.text(max(xa, xb) + 0.08, h, fmt % h, ha="left", va="center", fontsize=6.6,
                color=SUB)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([o.replace("p", "$p_") + "$" if o.startswith("p") else o
                        for o in order], fontsize=8.5, color=INK)
    ax.set_xlim(-0.6, len(order) - 0.4)
    ax.set_ylim(0, ymax or merges[-1][2] * 1.18)
    ax.set_ylabel("merge height (distance)", fontsize=7.6, color=SUB)
    ax.tick_params(axis="y", labelsize=7, colors=SUB)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title(title, fontsize=9, color=INK, pad=6)
    if cut is not None:
        ax.axhline(cut, color=MKC, lw=0.9, ls=(0, (4, 2)))
        ax.text(-0.55, cut, "cut: 2 clusters", ha="left", va="bottom",
                fontsize=6.6, color=MKC)


def check(merges, want, what):
    """want: list of (members of the merged cluster as a set, height)."""
    got = [(set(leaves(a)) | set(leaves(b)), h) for a, b, h, _ in merges]
    for k, ((gs, gh), (ws, wh)) in enumerate(zip(got, want), 1):
        if gs != set(ws) or abs(gh - wh) > 1.5e-3:
            sys.exit("%s merge %d: replay gives %s at %.4f, notes print %s at %.3f"
                     % (what, k, sorted(gs), gh, sorted(ws), wh))


def must_print(src, text, what):
    if text not in src:
        sys.exit("ch5-num.tex does not print %s as %r" % (what, text))


def save(fig, name):
    fig.savefig(os.path.join(FIGS, name), dpi=220, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def main():
    src = open(TEX, encoding="utf-8").read()

    # ---- 80 Bh: distance matrix given, single link, the tie at 0.15
    lab = ["p1", "p2", "p3", "p4", "p5", "p6"]
    M = {("p1", "p2"): .24, ("p1", "p3"): .22, ("p1", "p4"): .37, ("p1", "p5"): .34,
         ("p1", "p6"): .23, ("p2", "p3"): .15, ("p2", "p4"): .20, ("p2", "p5"): .14,
         ("p2", "p6"): .25, ("p3", "p4"): .15, ("p3", "p5"): .28, ("p3", "p6"): .11,
         ("p4", "p5"): .29, ("p4", "p6"): .22, ("p5", "p6"): .39}
    m1, r1 = replay(lab, M, "single")
    check(m1, [({"p3", "p6"}, .11), ({"p2", "p5"}, .14), ({"p3", "p4", "p6"}, .15),
               ({"p2", "p3", "p4", "p5", "p6"}, .15), (set(lab), .22)], "80 Bh")
    must_print(src, "Dendrogram heights: " + chr(92) + "mk{0.11, 0.14, 0.15, 0.15, 0.22}", "80 Bh heights")
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    draw(ax, m1, r1, "80 Bh: single link", cut=0.185)
    save(fig, "c5n_dend_80bh.png")

    # ---- 80 Ba: coordinates given, Euclidean, complete link
    co = {"p1": (0.40, 0.53), "p2": (0.22, 0.38), "p3": (0.35, 0.32),
          "p4": (0.26, 0.19), "p5": (0.08, 0.41), "p6": (0.45, 0.30)}
    M2 = {(a, b): math.dist(co[a], co[b]) for a, b in itertools.combinations(lab, 2)}
    m2, r2 = replay(lab, M2, "complete")
    check(m2, [({"p3", "p6"}, .102), ({"p2", "p5"}, .143), ({"p3", "p4", "p6"}, .219),
               ({"p1", "p2", "p5"}, .342), (set(lab), .386)], "80 Ba")
    must_print(src, "Heights " + chr(92) + "mk{0.102, 0.143, 0.219, 0.342, 0.386}", "80 Ba heights")
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    draw(ax, m2, r2, "80 Ba: complete link", cut=0.364, fmt="%.3f")
    save(fig, "c5n_dend_80ba.png")

    # ---- 76 Ch: one matrix, both linkages, drawn to the same scale
    labA = ["A", "B", "C", "D", "E", "F"]
    M3 = {("A", "B"): .12, ("A", "C"): .51, ("A", "D"): .84, ("A", "E"): .28, ("A", "F"): .34,
          ("B", "C"): .25, ("B", "D"): .16, ("B", "E"): .77, ("B", "F"): .61,
          ("C", "D"): .14, ("C", "E"): .70, ("C", "F"): .93,
          ("D", "E"): .45, ("D", "F"): .20, ("E", "F"): .67}
    ms, rs = replay(labA, M3, "single")
    mc, rc = replay(labA, M3, "complete")
    check(ms, [({"A", "B"}, .12), ({"C", "D"}, .14), ({"A", "B", "C", "D"}, .16),
               ({"A", "B", "C", "D", "F"}, .20), (set(labA), .28)], "76 Ch single")
    check(mc, [({"A", "B"}, .12), ({"C", "D"}, .14), ({"A", "B", "F"}, .61),
               ({"C", "D", "E"}, .70), (set(labA), .93)], "76 Ch complete")
    must_print(src, "Heights: " + chr(92) + "mk{0.12, 0.14, 0.16, 0.20, 0.28}", "76 Ch single")
    must_print(src, "Heights: " + chr(92) + "mk{0.12, 0.14, 0.61, 0.70, 0.93}", "76 Ch complete")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.6), sharey=True)
    draw(a1, ms, rs, "76 Ch (a): single link", ymax=1.05)
    draw(a2, mc, rc, "76 Ch (b): complete link", ymax=1.05)
    a2.set_ylabel("")
    save(fig, "c5n_dend_76ch.png")
    print("dendfig: 3 figures, every merge and height matches ch5-num.tex")


if __name__ == "__main__":
    main()
