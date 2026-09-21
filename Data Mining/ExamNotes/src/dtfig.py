# -*- coding: utf-8 -*-
"""Draw the decision trees the chapter-3 ID3 numericals ask to construct.

78 Bh (transport mode) and 82 Bh (credit risk) say "construct a decision tree";
the notes worked the gains and wrote the tree as nested bullets. This script
runs ID3 on the table the paper prints (ties broken by column order, which is
the choice the notes make and state), asserts the root gains and the whole tree
against ch3-num.tex, and only then draws it.

    python dtfig.py
"""
import math
import os
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
TEX = os.path.join(HERE, "ch3-num.tex")
INK, SUB, ACC, ACCL, GD, GDL = "#16202A", "#6B7785", "#2563A8", "#D6E4F5", "#15803D", "#DCFCE7"


def info(rows):
    c = Counter(r[-1] for r in rows)
    n = len(rows)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def gain(rows, a):
    n = len(rows)
    parts = {}
    for r in rows:
        parts.setdefault(r[a], []).append(r)
    return info(rows) - sum(len(p) / n * info(p) for p in parts.values())


def id3(rows, attrs, names):
    classes = {r[-1] for r in rows}
    if len(classes) == 1:
        return classes.pop()
    best = max(attrs, key=lambda a: (round(gain(rows, a), 9), -attrs.index(a)))
    kids = {}
    for v in dict.fromkeys(r[best] for r in rows):
        sub = [r for r in rows if r[best] == v]
        kids[v] = id3(sub, [a for a in attrs if a != best], names)
    return (names[best], kids)


# ---------------------------------------------------------------- drawing
def nleaves(t):
    return 1 if isinstance(t, str) else sum(nleaves(k) for k in t[1].values())


def layout(t, x0, depth, pos, edges, key="r"):
    w = nleaves(t)
    x = x0 + w / 2.0
    pos[key] = (x, -depth, t if isinstance(t, str) else t[0], isinstance(t, str))
    if not isinstance(t, str):
        cx = x0
        for i, (v, k) in enumerate(t[1].items()):
            ck = key + str(i)
            layout(k, cx, depth + 1, pos, edges, ck)
            edges.append((key, ck, v))
            cx += nleaves(k)


def draw(tree, name, fs=8.0, w_unit=1.25):
    pos, edges = {}, []
    layout(tree, 0, 0, pos, edges)
    W = nleaves(tree)
    D = max(-p[1] for p in pos.values())
    fig, ax = plt.subplots(figsize=(W * w_unit + 0.4, D * 1.05 + 0.9))
    for a, b, v in edges:
        xa, ya = pos[a][0], pos[a][1]
        xb, yb = pos[b][0], pos[b][1]
        ax.plot([xa, xb], [ya - 0.17, yb + 0.17], color=SUB, lw=0.9, zorder=1)
        ax.text(0.35 * xa + 0.65 * xb, 0.35 * ya + 0.65 * yb, v, ha="center", va="center",
                fontsize=fs - 1,
                color=INK, style="italic", zorder=3,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    for k, (x, y, lab, leaf) in pos.items():
        fc, ec, tc = (GDL, GD, GD) if leaf else (ACCL, ACC, INK)
        txt = lab if leaf else lab + "?"
        ax.text(x, y, txt, ha="center", va="center", fontsize=fs, color=tc,
                fontweight="bold", zorder=4,
                bbox=dict(boxstyle="round,pad=0.28", fc=fc, ec=ec, lw=0.9))
    ax.set_xlim(-0.1, W + 0.1)
    ax.set_ylim(-D - 0.45, 0.45)
    ax.axis("off")
    fig.savefig(os.path.join(FIGS, name), dpi=220, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def must_print(src, text, what):
    if text not in src:
        sys.exit("ch3-num.tex does not print %s as %r" % (what, text))


def main():
    src = open(TEX, encoding="utf-8").read()
    B = chr(92)

    # ---- 78 Bh, transport mode
    names = ["Gender", "Car ownership", "Travel cost", "Income level"]
    T = [("Male", "0", "Cheap", "Low", "Bus"), ("Male", "1", "Cheap", "Medium", "Bus"),
         ("Female", "0", "Cheap", "Low", "Bus"), ("Male", "1", "Cheap", "Medium", "Bus"),
         ("Female", "1", "Expensive", "High", "Car"), ("Male", "2", "Expensive", "Medium", "Car"),
         ("Female", "2", "Expensive", "High", "Car"), ("Female", "1", "Cheap", "Medium", "Train"),
         ("Male", "0", "Standard", "Medium", "Train"), ("Female", "1", "Standard", "Medium", "Train")]
    for a, g in ((2, "1.210"), (3, "0.695"), (1, "0.534"), (0, "0.125")):
        got = "%.3f" % gain(T, a)
        if got != g:
            sys.exit("78 Bh gain of %s: %s, notes print %s" % (names[a], got, g))
    t1 = id3(T, [0, 1, 2, 3], names)
    want1 = ("Travel cost", {"Cheap": ("Gender", {"Male": "Bus", "Female": (
        "Car ownership", {"0": "Bus", "1": "Train"})}), "Expensive": "Car", "Standard": "Train"})
    if t1 != want1:
        sys.exit("78 Bh tree differs from the notes:\n%r" % (t1,))
    must_print(src, B + "mathbf{1.210}", "78 Bh root gain")
    draw(t1, "c3n_dt_78bh.png")

    # ---- 82 Bh, credit risk (three classes)
    names2 = ["Credit history", "Debt", "Collateral", "Income"]
    L, M, H = "$0-15K", "$15-35K", "over $35K"
    R = [("bad", "high", "none", L, "high"), ("unknown", "high", "none", M, "high"),
         ("unknown", "low", "none", M, "moderate"), ("unknown", "low", "none", L, "high"),
         ("unknown", "low", "none", H, "low"), ("unknown", "low", "adequate", H, "low"),
         ("bad", "low", "none", L, "high"), ("bad", "low", "adequate", H, "moderate"),
         ("good", "low", "none", H, "low"), ("good", "high", "adequate", H, "low"),
         ("good", "high", "none", L, "high"), ("good", "high", "none", M, "moderate"),
         ("good", "high", "none", H, "low"), ("bad", "high", "none", M, "high")]
    for a, g in ((3, "0.966"), (0, "0.266"), (2, "0.206"), (1, "0.063")):
        got = "%.3f" % gain(R, a)
        if got != g:
            sys.exit("82 Bh gain of %s: %s, notes print %s" % (names2[a], got, g))
    t2 = id3(R, [0, 1, 2, 3], names2)
    want2 = ("Income", {L: "high", M: ("Credit history", {
        "unknown": ("Debt", {"high": "high", "low": "moderate"}), "bad": "high",
        "good": "moderate"}), H: ("Credit history", {"unknown": "low", "bad": "moderate",
                                                    "good": "low"})})
    if t2 != want2:
        sys.exit("82 Bh tree differs from the notes:\n%r" % (t2,))
    must_print(src, B + "mathbf{0.966}", "82 Bh root gain")
    must_print(src, "8 leaves; classifies all 14 tuples correctly", "82 Bh leaf count")
    assert nleaves(t2) == 8 and nleaves(t1) == 5
    draw(t2, "c3n_dt_82bh.png", fs=9.6, w_unit=1.2)
    print("dtfig: 2 trees, gains and structure match ch3-num.tex")


if __name__ == "__main__":
    main()
