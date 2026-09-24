# -*- coding: utf-8 -*-
"""Top-view microstrip layouts for the Ch2 problems that ask for one.

Five papers ask the candidate to "sketch the realisation in microstrip"
(P2, P7, P19, P20, P23). The Smith chart gives the design in wavelengths;
this module draws what gets etched: the W-wide main line, the stubs as
T-junctions off it, a plated via at the end of every shorted stub, and the
dimensions d, l1, l2 laid out to scale along the board.

The solution is RECOMPUTED here from the problem data (rf.single_stub,
rf.double_stub, rf.microstrip), never taken from the emitter, and layout()
returns every value it drew as the exact TeX string the notes print. The
driver asserts each one is in that problem's text, so the drawing cannot
disagree with the working above it.

Lengths run to scale. With no frequency the unit is the guide wavelength
and the strip width is drawn schematically (it is a fixed mm figure, not a
fraction of lambda); with a frequency everything, W included, is in mm.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

import rf
from smith import INK, SUB, ACC, PIN

B = chr(92)
HERE = os.path.dirname(os.path.abspath(__file__))
ER, H = 4.4, 1.6               # FR-4, the substrate micro_block assumes

CU = "#E3A857"                 # copper
CUE = "#8A5A1C"                # copper edge
SUBS = "#EAF0E4"               # FR-4, pale green
VIA = "#16202A"
TAIL = 0.30                    # main line beyond the last stub, in lambda


def _lam(v):
    return "%.3f" % v + B + "lambda"


def _panel(ax, b, u, wd, ytop, ndim):
    """Draw one board. x is measured from the load toward the generator and
    plotted leftwards (load on the right), y upward from the line centre.
    Every length argument is in lambda; u converts to drawing units."""
    left = -(b["xmax"] + TAIL) * u
    lx = wd / 2 + 0.012 * u                # load box sits flush past a stub at x = 0
    ybot = -wd / 2 - (0.05 + 0.075 * ndim) * u
    stop = (max(s["l"] for s in b["stubs"]) + 0.07) * u
    ax.add_patch(Rectangle((left - 0.03 * u, ybot), lx + 0.10 * u - left,
                           stop - ybot, fc=SUBS, ec="none", zorder=0))
    ax.add_patch(Rectangle((left, -wd / 2), lx - left, wd, fc=CU, ec=CUE,
                           lw=0.8, zorder=2))
    ax.add_patch(Rectangle((lx, -0.045 * u), 0.07 * u, 0.09 * u, fc="white",
                           ec=INK, lw=0.9, zorder=3))
    ax.text(lx + 0.035 * u, 0, "$Z_L$", color=INK, fontsize=8, ha="center",
            va="center", zorder=4)
    ax.text(left + 0.005 * u, -wd / 2 - 0.02 * u,
            "$" + B + "leftarrow$ to generator", color=SUB, fontsize=6.6,
            ha="left", va="top")
    xfar = max(s["x"] for s in b["stubs"])
    for s in b["stubs"]:
        X, L = -s["x"] * u, s["l"] * u
        ax.add_patch(Rectangle((X - wd / 2, 0), wd, L, fc=CU, ec=CUE, lw=0.8,
                               zorder=2))
        if s["kind"] == "short":
            r = min(0.42 * wd, 0.018 * u)
            ax.add_patch(Circle((X, L - r * 1.35), r, fc=VIA, ec="white",
                                lw=0.6, zorder=5))
        # length dimension beside the stub: on the left for a stub at the load
        # (the load box is on its right) and for the outer stub of a pair (so
        # the two labels never meet between the stubs)
        sgn = -1 if (s["x"] < 1e-9 or (len(b["stubs"]) > 1 and s["x"] == xfar)) else 1
        dx = sgn * (wd / 2 + 0.018 * u)
        ax.annotate("", xy=(X + dx, 0), xytext=(X + dx, L),
                    arrowprops=dict(arrowstyle="<|-|>", color=PIN, lw=0.8,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))
        ax.text(X + dx + sgn * 0.012 * u, L / 2, s["label"], color=PIN,
                fontsize=7.4, ha="left" if sgn > 0 else "right", va="center",
                zorder=6, bbox=dict(boxstyle="round,pad=0.1", fc=SUBS, ec="none"))
        tag = "via to ground" if s["kind"] == "short" else "open end"
        ax.text(X, L + 0.012 * u, tag, color=SUB, fontsize=6.4, ha="center",
                va="bottom")
    # position dimensions below the line
    for i, (x0, x1, lab) in enumerate(b["dims"]):
        y = -wd / 2 - (0.04 + 0.075 * i) * u
        ax.annotate("", xy=(-x1 * u, y), xytext=(-x0 * u, y),
                    arrowprops=dict(arrowstyle="<|-|>", color=ACC, lw=0.8,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))
        for xe in (x0, x1):
            ax.plot([-xe * u, -xe * u], [y - 0.01 * u, -wd / 2], color=ACC,
                    lw=0.5, ls=":")
        ax.text(-(x0 + x1) / 2 * u, y - 0.008 * u, lab, color=ACC,
                fontsize=7.4, ha="center", va="top")
    ax.set_title(b["title"], color=INK, fontsize=8.4, pad=3)
    ax.set_xlim(left - 0.04 * u, lx + 0.12 * u)
    ax.set_ylim(ybot - 0.01 * u, ytop + 0.01 * u)
    ax.set_aspect("equal")
    ax.axis("off")


def layout(pr, fname):
    """Draw pr's microstrip realisation; return [(what, tex)] for every value drawn."""
    zn, z0, k = pr["zn"], pr["z0"], pr["stub"]
    w, ee, _ = rf.microstrip(z0, ER, H)
    f = pr.get("f")
    lg = rf.guide_wavelength_mm(f, ee) if f else None
    drawn = [("W", "W = %.2f" % w + B + "text{ mm}"),
             ("eps_e", B + "epsilon_e = %.2f" % ee)]

    def lab(name, v, shown=None):
        # shown: the form the notes print instead of 0.xxx lambda (3 lambda/8)
        shown = shown or _lam(v)
        drawn.append((name, shown))
        if lg:
            drawn.append((name + " mm", "%.2f" % (v * lg) + B + "text{ mm}"))
            return "$%s = %s = %.2f$ mm" % (name, shown, v * lg)
        return "$%s = %s$" % (name, shown)

    boards = []
    if pr["kind"] == "ss":
        for kk in (["short", "open"] if k == "both" else [k]):
            s = rf.single_stub(zn, kk)[0]           # solution 1, as the notes build
            boards.append(dict(
                title="%s-circuited stub, solution 1" % kk.capitalize(),
                stubs=[dict(x=s["d"], l=s["l"], kind=kk,
                            label=lab(B + "ell_1", s["l"]))],
                dims=[(0.0, s["d"], lab("d", s["d"]))], xmax=s["d"]))
    else:
        sp, d1 = pr["sp"], pr.get("d1", 0.0)
        a = rf.double_stub(zn, sp, k, d1)[0]        # solution A, as the notes build
        spname = {0.375: "3" + B + "lambda/8", 0.125: B + "lambda/8"}.get(sp)
        dims = [(d1, d1 + sp, lab("d", sp, spname))]
        if d1 > 0:
            dims.insert(0, (0.0, d1, lab("d_1", d1)))
        boards.append(dict(
            title="Double stub, %s-circuited, solution A" % k,
            stubs=[dict(x=d1, l=a["l1"], kind=k, label=lab(B + "ell_1", a["l1"])),
                   dict(x=d1 + sp, l=a["l2"], kind=k, label=lab(B + "ell_2", a["l2"]))],
            dims=dims, xmax=d1 + sp))

    u = lg if lg else 1.0                   # drawing units per lambda
    wd = w if lg else 0.03                  # schematic width without a frequency
    ytop = (max(s["l"] for b in boards for s in b["stubs"]) + 0.08) * u
    ndim = max(len(b["dims"]) for b in boards)
    # size the figure from the board itself so equal aspect leaves no dead band
    ext = wd / 2 / u + 0.012 + 0.12 + 0.04       # load box and margins, lambda
    spans = [b["xmax"] + TAIL + ext for b in boards]
    yspan = ytop / u + wd / 2 / u + 0.06 + 0.075 * ndim
    ipl = 5.2                                    # inches per lambda
    fig, axs = plt.subplots(1, len(boards),
                            figsize=(ipl * sum(spans) * 1.08, ipl * yspan + 0.3),
                            gridspec_kw=dict(width_ratios=spans, wspace=0.08))
    axs = [axs] if len(boards) == 1 else list(axs)
    for ax, b in zip(axs, boards):
        _panel(ax, b, u, wd, ytop, ndim)
        # the geometry itself: every stub drawn at its own length
        strips = [q for q in ax.patches if isinstance(q, Rectangle)][3:]
        for s, q in zip(b["stubs"], strips):
            assert abs(q.get_height() - s["l"] * u) < 1e-9, "stub height drift"
            assert abs(q.get_x() + wd / 2 + s["x"] * u) < 1e-9, "stub position drift"

    note = ("FR-4, $" + B + "epsilon_r = %.1f$, $h = %.1f$ mm, $%g" % (ER, H, z0)
            + B + ",\\Omega$ strip $W = %.2f$ mm, $" % w + B +
            "epsilon_e = %.2f$" % ee)
    if lg:
        note += ", $" + B + "lambda_g = %.1f$ mm at %g GHz; to scale" % (lg, f / 1e9)
        drawn.append(("lambda_g", "%.1f" % lg + B + "text{ mm}"))
    else:
        note += "\nlengths in $" + B + "lambda_g$ and to scale; strip width not to scale"
    if any(s["kind"] == "open" for b in boards for s in b["stubs"]):
        note += "\ncut each open end $" + B + "Delta" + B + "ell = %.2f$ mm short " \
                "for fringing" % (0.3 * H)
        drawn.append(("fringe", "%.2f" % (0.3 * H) + B + "text{ mm}"))
    fig.text(0.5, 0.07, note, color=SUB, fontsize=7.0, ha="center", va="top",
             linespacing=1.4)
    fig.savefig(os.path.join(HERE, "figs", fname), dpi=210, bbox_inches="tight",
                pad_inches=0.03, transparent=True)
    plt.close(fig)
    return drawn
