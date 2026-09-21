# -*- coding: utf-8 -*-
"""Draw the FP-tree after each transaction, for ch4-num Problem 3.3 (78 Bh).

The paper asks to "show for each transaction how the tree evolves". The tree is
rebuilt here from the six transactions: counts, the F-list (ties broken
alphabetically, as the notes state), each reordered transaction, the tree after
each insertion. The reordered lists are checked against the table the notes
print and the final tree against the notes' drawn tree before anything is
drawn. One panel per transaction; the path just inserted is highlighted.

    python fpfig.py
"""
import os
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch4-num.tex")
FIGS = os.path.join(HERE, "figs")
INK, SUB, ACC, ACCL, MKC, MKL = "#16202A", "#6B7785", "#2563A8", "#D6E4F5", "#C2410C", "#FDEBD9"

T = [["HotDogs", "Buns", "Ketchup"], ["HotDogs", "Buns"], ["HotDogs", "Coke", "Chips"],
     ["Chips", "Coke"], ["Chips", "Ketchup"], ["HotDogs", "Coke", "Chips"]]
ABBR = {"HotDogs": "H", "Buns": "Bu", "Ketchup": "Ke", "Coke": "Co", "Chips": "Ch"}


class Node:
    def __init__(self, item):
        self.item, self.count, self.kids = item, 0, []

    def child(self, item):
        for k in self.kids:
            if k.item == item:
                return k
        k = Node(item)
        self.kids.append(k)
        return k


def shape(n):
    return (n.item, n.count, tuple(shape(k) for k in n.kids))


def leaves(n):
    return 1 if not n.kids else sum(leaves(k) for k in n.kids)


def place(n, x0, depth, out, path=()):
    w = leaves(n)
    out.append((n, x0 + w / 2.0, -depth, path))
    cx = x0
    for k in n.kids:
        place(k, cx, depth + 1, out, path + (k.item,))
        cx += leaves(k)


def panel(ax, root, fresh, title, W=4):
    nodes = []
    place(root, (W - leaves(root)) / 2.0, 0, nodes)
    at = {id(n): (x, y) for n, x, y, _ in nodes}
    for n, x, y, path in nodes:
        for k in n.kids:
            kx, ky = at[id(k)]
            hot = path + (k.item,) == fresh[:len(path) + 1]
            ax.plot([x, kx], [y - 0.2, ky + 0.2], color=MKC if hot else SUB,
                    lw=1.4 if hot else 0.8, zorder=1)
    for n, x, y, path in nodes:
        if n.item is None:
            lab, fc, ec = "root", "white", SUB
        else:
            hot = path == fresh[:len(path)]
            lab = "%s:%d" % (ABBR[n.item], n.count)
            fc, ec = (MKL, MKC) if hot else (ACCL, ACC)
        ax.text(x, y, lab, ha="center", va="center", fontsize=8, color=INK, zorder=3,
                bbox=dict(boxstyle="round,pad=0.25", fc=fc, ec=ec, lw=0.9))
    ax.set_xlim(-0.1, W + 0.1)
    ax.set_ylim(-3.5, 0.5)
    ax.axis("off")
    ax.set_title(title, fontsize=8.5, color=INK, pad=2)


def must_print(src, text, what):
    if text not in src:
        sys.exit("ch4-num.tex does not print %s as %r" % (what, text))


def main():
    src = open(TEX, encoding="utf-8").read()
    cnt = Counter(i for t in T for i in t)
    flist = sorted(cnt, key=lambda i: (-cnt[i], i))
    must_print(src, "F-list $=$ Chips(4), HotDogs(4), Coke(3), Buns(2), Ketchup(2)", "F-list")
    assert flist == ["Chips", "HotDogs", "Coke", "Buns", "Ketchup"], flist
    root = Node(None)
    snaps = []
    for k, t in enumerate(T, 1):
        ordered = [i for i in flist if i in t]
        row = "T%d & %s" % (k, ", ".join(ABBR[i] for i in ordered))
        must_print(src, row, "reordered T%d" % k)
        n = root
        for i in ordered:
            n = n.child(i)
            n.count += 1
        snaps.append((shape(root), tuple(ordered)))
    want = (None, 0, (("HotDogs", 2, (("Buns", 2, (("Ketchup", 1, ()),)),)),
                      ("Chips", 4, (("HotDogs", 2, (("Coke", 2, ()),)), ("Coke", 1, ()),
                                    ("Ketchup", 1, ())))))
    if shape(root) != want:
        sys.exit("final tree differs from the notes' drawn tree:\n%r" % (shape(root),))
    for s in ("node{H:2} child { node{Bu:2} child { node{Ke:1} }", "node{Ch:4}",
              "node{H:2} child { node{Co:2} }", "node{Co:1}", "node{Ke:1} } };"):
        must_print(src, s, "tikz final tree node")

    def build(sh):
        n = Node(sh[0])
        n.count = sh[1]
        n.kids = [build(k) for k in sh[2]]
        return n

    fig, axes = plt.subplots(2, 3, figsize=(7.6, 4.3))
    for k, (ax, (sh, ordered)) in enumerate(zip(axes.flat, snaps), 1):
        panel(ax, build(sh), ordered,
              "after T%d: %s" % (k, ", ".join(ABBR[i] for i in ordered)))
    fig.tight_layout(pad=0.3, h_pad=0.6)
    fig.savefig(os.path.join(FIGS, "c4n_fp_78bh_steps.png"), dpi=220, bbox_inches="tight",
                pad_inches=0.03)
    plt.close(fig)
    print("fpfig: 6 panels, F-list, reorderings and final tree match ch4-num.tex")


if __name__ == "__main__":
    main()
