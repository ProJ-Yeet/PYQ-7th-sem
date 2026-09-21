# -*- coding: utf-8 -*-
"""Draw the radiation-zone answers of the chapter-7 numericals, to scale.

Problem 1 (81 Bh BTS, and the 74 Ma / 77 Ch oven) and Problem 2 (82 Ba,
quarter-wave at 900 vs 1800 MHz) ask for zones, and two of them say "draw" or
"illustrate". Each strip is the distance axis from the antenna with the reactive,
radiating-near and far regions shaded at the boundaries computed here. Before
drawing, every boundary is formatted to the precision the notes print and looked
up in ch7-num-body.tex; a value the notes do not print stops the run.

    python zonefig.py
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch7-num-body.tex")
FIGS = os.path.join(HERE, "figs")
C = 3e8

INK, SUB = "#16202A", "#6B7785"
RED, AMB, GRN = "#FDE2DD", "#FDEBD9", "#DCFCE7"
REDE, AMBE, GRNE = "#C2410C", "#B45309", "#15803D"


def must_print(src, text, what):
    if text not in src:
        sys.exit("ch7-num-body.tex does not print %s as %r" % (what, text))


def large(f, D):
    lam = C / f
    return lam, 0.62 * math.sqrt(D ** 3 / lam), 2 * D * D / lam


def strip(ax, y, r1, r2, xmax, label, unit, fmt, extra=None, scale=1.0,
          mid="radiating near\n(Fresnel)", far="far field: safe side"):
    h = 0.62
    ax.add_patch(Rectangle((0, y), r1, h, fc=RED, ec=REDE, lw=0.6))
    ax.add_patch(Rectangle((r1, y), r2 - r1, h, fc=AMB, ec=AMBE, lw=0.6))
    ax.add_patch(Rectangle((r2, y), xmax - r2, h, fc=GRN, ec=GRNE, lw=0.6))
    ax.text(-0.012 * xmax, y + h / 2, label, ha="right", va="center", fontsize=7.4, color=INK)
    for x, col in ((r1, REDE), (r2, AMBE)):
        ax.plot([x, x], [y - 0.08, y + h + 0.08], color=col, lw=1.1)
        ax.text(x, y + h + 0.12, fmt % (x * scale) + " " + unit, ha="center", va="bottom",
                fontsize=6.8, color=col)
    if r1 > 0.1 * xmax:
        ax.text(r1 / 2, y + h / 2, "reactive", ha="center", va="center", fontsize=6.2, color=REDE)
    else:                                   # too narrow: label it underneath
        ax.text(r1, y - 0.1, "reactive", ha="left", va="top", fontsize=6.2, color=REDE)
    xm = (r1 + (extra[0] if extra else r2)) / 2
    ax.text(xm, y + h / 2, mid, ha="center", va="center", fontsize=6.2, color=AMBE,
            linespacing=0.9)
    ax.text((r2 + xmax) / 2, y + h / 2, far, ha="center", va="center",
            fontsize=6.4, color=GRNE)
    if extra:
        x, txt = extra
        ax.plot([x, x], [y, y + h], color=INK, lw=0.9, ls=(0, (2, 1.5)))
        ax.text(x, y - 0.1, txt, ha="center", va="top", fontsize=6.2, color=INK)


def axes(xmax, rows, xlabel):
    fig, ax = plt.subplots(figsize=(6.6, 0.95 + 0.95 * rows))
    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.45, rows * 1.25 - 0.2)
    ax.set_yticks([])
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(SUB)
    ax.tick_params(axis="x", colors=SUB, labelsize=7)
    ax.set_xlabel(xlabel, fontsize=7.4, color=SUB)
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(FIGS, name), dpi=220, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def main():
    src = open(TEX, encoding="utf-8").read()

    # ---------------- Problem 1: BTS 2600 MHz, and the oven, both D = 0.5 m
    lam_b, r1_b, r2_b = large(2.6e9, 0.5)
    lam_o, r1_o, r2_o = large(2.45e9, 0.5)
    must_print(src, "$%.4f$ m" % lam_b, "BTS wavelength")
    must_print(src, "$" + chr(92) + "mathbf{%.3f" % r1_b + chr(92) + " m}$", "BTS R1")
    must_print(src, "$" + chr(92) + "mathbf{%.2f" % r2_b + chr(92) + " m}$", "BTS R2")
    must_print(src, "$< %.3f$ m / $%.3f$ to $%.2f$ m" % (r1_o, r1_o, r2_o), "oven zones")
    eirp = 20 * 10 ** 1.7
    rc = math.sqrt(eirp / (4 * math.pi * 10))
    must_print(src, "= %.2f$ m" % rc, "compliance distance")
    xmax = 6.0
    fig, ax = axes(xmax, 2, "distance from the antenna (m)")
    strip(ax, 1.25, r1_b, r2_b, xmax, "81 Bh BTS\n2600 MHz, D = 0.5 m", "m", "%.3f" if r1_b < 1 else "%.2f",
          extra=(rc, "ICNIRP limit met\nbeyond %.2f m" % rc))
    strip(ax, 0.0, r1_o, r2_o, xmax, "74 Ma, 77 Ch oven\n2.45 GHz, D = 0.5 m", "m", "%.3f")
    # the second boundary of each strip is printed to 2 decimals in the notes
    for t in ax.texts:
        for v in (r2_b, r2_o):
            if t.get_text() == "%.3f m" % v:
                t.set_text("%.2f m" % v)
    save(fig, "c7n_p1_zones.png")

    # ---------------- Problem 2: quarter-wave at 900 and 1800 MHz, small-antenna rule
    rows = []
    for f in (900e6, 1800e6):
        lam = C / f
        rows.append((f, lam, lam / (2 * math.pi), 2 * lam))
    must_print(src, "$R < %.1f$ cm & $R < %.1f$ cm" % (rows[0][2] * 100, rows[1][2] * 100),
               "reactive boundaries")
    must_print(src, "$R > %.2f$ m & $R > %.2f$ m" % (rows[0][3], rows[1][3]), "far boundaries")
    xmax = 0.9
    fig, ax = axes(xmax, 2, "distance from the antenna (m)")
    for k, (f, lam, r1, r2) in enumerate(rows):
        strip(ax, 1.25 * (1 - k), r1, r2, xmax,
              "82 Ba, %d MHz\nquarter-wave" % round(f / 1e6), "cm", "%.1f", scale=100.0,
              mid="transition", far="far field")
    for t in ax.texts:                                  # far boundary printed in metres
        for (_, _, _, r2) in rows:
            if t.get_text() == "%.1f cm" % (r2 * 100):
                t.set_text("%.2f m" % r2)
    save(fig, "c7n_p2_zones.png")
    print("zonefig: 2 figures written, every boundary found in ch7-num-body.tex")


if __name__ == "__main__":
    main()
