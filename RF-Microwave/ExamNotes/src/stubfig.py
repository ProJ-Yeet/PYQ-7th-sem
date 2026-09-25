# -*- coding: utf-8 -*-
"""Physical figures for the Ch2 stub-matching problems.

Two drawings per problem, placed after the Smith chart:

  line(pr, fname)  the line diagram in Pozar's Fig. 5.3(a) style: a two-wire
                   main line, the shunt stub(s) as a slanted two-wire pair
                   (the top wire hops over the bottom conductor, no joint),
                   the termination drawn at the stub end, d / d_1 / l
                   dimensioned with the answer's values. Not to scale.

  coax(pr, fname)  the coaxial realisation as a longitudinal section: outer
                   conductor walls (hatched), dielectric, inner conductor,
                   each stub a coax tee off the main line, a shorting plate
                   across a shorted stub's end, an open end left bare.
                   Lengths to scale in lambda, measured from the main-line
                   axis; the coax diameter is not to scale.

Problems that ask for microstrip get line() plus msfig's board instead of
coax(). The design is RECOMPUTED here from the problem data (rf.single_stub,
rf.double_stub), never taken from the emitter, and both functions return
every length they drew as the exact TeX the notes print; the driver asserts
each one is in that problem's text.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

import rf
from smith import INK, SUB, ACC, PIN

B = chr(92)
HERE = os.path.dirname(os.path.abspath(__file__))

CU = "#E3A857"                 # copper, inner conductor
CUE = "#8A5A1C"
WALL = "#AEB8C2"               # outer conductor
WALLE = "#5B6773"
DIEL = "#F4F0E2"               # dielectric
PLATE = "#16202A"              # shorting plate


def _lam(v):
    return "%.3f" % v + B + "lambda"


def _spname(sp):
    return {0.375: "3" + B + "lambda/8", 0.125: B + "lambda/8"}.get(sp, _lam(sp))


def design(pr):
    """The stubs to draw: [boards], each {title, stubs[{x, l, kind, name}],
    dims[(x0, x1, name, tex)], xmax}. x in lambda from the load."""
    zn, k = pr["zn"], pr["stub"]
    boards = []
    if pr["kind"] == "ss":
        kinds = ["short", "open"] if k == "both" else [k]
        for kk in kinds:
            s = rf.single_stub(zn, kk)[0]           # solution 1, as the notes build
            boards.append(dict(
                title="%s-circuited stub, solution 1" % kk.capitalize(),
                stubs=[dict(x=s["d"], l=s["l"], kind=kk, name=B + "ell")],
                dims=[(0.0, s["d"], "d", _lam(s["d"]))], xmax=s["d"]))
    else:
        sp, d1 = pr["sp"], pr.get("d1", 0.0)
        a = rf.double_stub(zn, sp, k, d1)[0]        # solution A, as the notes build
        dims = [(d1, d1 + sp, "d", _spname(sp))]
        if d1 > 0:
            dims.insert(0, (0.0, d1, "d_1", _lam(d1)))
        boards.append(dict(
            title="Double stub, %s-circuited, solution A" % k,
            stubs=[dict(x=d1, l=a["l1"], kind=k, name=B + "ell_1"),
                   dict(x=d1 + sp, l=a["l2"], kind=k, name=B + "ell_2")],
            dims=dims, xmax=d1 + sp))
    return boards


# ------------------------------------------------------------ line diagram
def line(pr, fname):
    """Pozar-style two-wire line diagram. Returns [(what, tex)] drawn."""
    boards = design(pr)
    drawn = []
    lw = 1.7
    fig, ax = plt.subplots(figsize=(6.4, 2.75))
    ax.set_aspect("equal")
    ax.axis("off")

    # drawing positions (not to scale): stub 1 is the one nearest the load
    b0 = boards[0]
    st = sorted(b0["stubs"], key=lambda s: s["x"])
    ds = pr["kind"] == "ds"
    x1 = 0.0
    xs = [x1] + ([x1 - 3.6] if len(st) > 1 else [])
    at_load = st[0]["x"] < 1e-9
    xload = x1 + (0.9 if at_load else 2.6)
    xgen = xs[-1] - 2.9
    for y in (0.0, 1.0):
        ax.plot([xgen, xload], [y, y], color=INK, lw=lw, solid_capstyle="butt",
                zorder=3)
        for x in [xgen] + xs:
            ax.add_patch(Circle((x, y), 0.07, fc="white", ec=INK, lw=1.0, zorder=6))
    # load across the line end
    ax.plot([xload, xload], [1.0, 0.74], color=INK, lw=lw, zorder=3)
    ax.plot([xload, xload], [0.0, 0.26], color=INK, lw=lw, zorder=3)
    ax.add_patch(Rectangle((xload - 0.3, 0.26), 0.6, 0.48, fc="white", ec=INK,
                           lw=1.1, zorder=4))
    ax.text(xload, 0.5, "$Z_L$", color=INK, fontsize=9, ha="center", va="center",
            zorder=5)
    # characteristic impedance on each main-line section
    z0 = "$Z_0$"
    secs = xs[::-1] + [xload]                # generator section carries y_in
    for xa, xb in zip(secs[:-1], secs[1:]):
        if xb - xa > 1.2:
            ax.text((xa + xb) / 2 + 0.15, 0.5, z0, color=SUB, fontsize=8.5,
                    ha="center", va="center")
    # y_in arrow on the generator side of the last stub
    xa = xs[-1] - 0.75
    ax.plot([xa, xa], [0.22, 0.78], color=ACC, lw=0.9)
    ax.annotate("", xy=(xa + 0.45, 0.78), xytext=(xa, 0.78),
                arrowprops=dict(arrowstyle="-|>", color=ACC, lw=0.9,
                                mutation_scale=8, shrinkA=0, shrinkB=0))
    ax.text(xa - 0.08, 0.5, "$y_{in}=1+j0$", color=ACC, fontsize=7.4, ha="right",
            va="center")

    # the stubs: slanted two-wire pairs, top wire hops the bottom conductor
    u = (-0.5 / math.hypot(0.5, 1.0), -1.0 / math.hypot(0.5, 1.0))
    n = (u[1], -u[0])                         # unit normal, left and up of u
    w = 0.5 / math.hypot(0.5, 1.0)            # wire separation
    both = pr["stub"] == "both"
    for s, X in zip(st, xs):
        L = 2.2                               # below the bottom conductor
        eb = (X + u[0] * L, u[1] * L)         # bottom wire end
        et = (eb[0] + n[0] * w, eb[1] + n[1] * w)
        ax.plot([X, eb[0]], [0.0, eb[1]], color=INK, lw=lw, zorder=3)
        # top wire from (X, 1) with a gap where it crosses y = 0
        tc = 1.0 / -u[1]                      # parameter at the crossing
        g = 0.13 / -u[1]
        for t0, t1 in ((0.0, tc - g), (tc + g, None)):
            p0 = (X + u[0] * t0, 1.0 + u[1] * t0)
            p1 = et if t1 is None else (X + u[0] * t1, 1.0 + u[1] * t1)
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=INK, lw=lw, zorder=3)
        # termination
        if both:
            ax.plot([eb[0], et[0]], [eb[1], et[1]], color=INK, lw=1.2, ls="--",
                    zorder=3)
        elif s["kind"] == "short":
            ax.plot([eb[0], et[0]], [eb[1], et[1]], color=INK, lw=2.6,
                    solid_capstyle="round", zorder=3)
        for e in (eb, et):
            ax.add_patch(Circle(e, 0.07, fc="white", ec=INK, lw=1.0, zorder=6))
        mid = ((eb[0] + et[0]) / 2, (eb[1] + et[1]) / 2)
        if both:
            tag = "short or open"
        else:
            tag = "shorted" if s["kind"] == "short" else "open"
        ax.text(mid[0] + 0.05, mid[1] - 0.2, tag, color=SUB, fontsize=7.2,
                ha="center", va="top")
        zm = (X + u[0] * 1.3 - n[0] * 0.42, u[1] * 1.3 - n[1] * 0.42)
        ax.text(zm[0], zm[1], z0, color=SUB, fontsize=8, ha="center",
                va="center")
        # stub length, parallel to the stub on its outer side
        c0 = (X + u[0] * tc, 0.0)             # where the stub leaves the line
        off = 0.32
        q0 = (c0[0] + n[0] * off, c0[1] + n[1] * off)
        q1 = (et[0] + n[0] * off, et[1] + n[1] * off)
        ax.annotate("", xy=q1, xytext=q0,
                    arrowprops=dict(arrowstyle="<|-|>", color=PIN, lw=0.8,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))
        if both:
            labs = []
            for kk in ("short", "open"):
                v = rf.single_stub(pr["zn"], kk)[0]["l"]
                labs.append("%s: $%s = %s$" % (kk, s["name"], _lam(v)))
                drawn.append((kk + " stub", _lam(v)))
            lab = chr(10).join(labs)
        else:
            lab = "$%s = %s$" % (s["name"], _lam(s["l"]))
            drawn.append((s["name"], _lam(s["l"])))
        qm = ((q0[0] + q1[0]) / 2 + n[0] * 0.12, (q0[1] + q1[1]) / 2)
        ax.text(qm[0], qm[1], lab, color=PIN, fontsize=7.4, ha="right",
                va="center", linespacing=1.3)

    # position dimensions above the line
    xpos = {s["x"]: X for s, X in zip(st, xs)}
    xpos[0.0] = xpos.get(0.0, xload)
    if at_load:
        ax.text(x1, -0.18, "stub 1 at\nthe load", color=SUB, fontsize=6.6,
                ha="left", va="top", linespacing=1.1)
    for i, (a0, a1, name, tex) in enumerate(b0["dims"]):
        xa_, xb_ = xpos[a1], xpos[a0]
        y = 1.42
        ax.annotate("", xy=(xa_, y), xytext=(xb_, y),
                    arrowprops=dict(arrowstyle="<|-|>", color=ACC, lw=0.8,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))
        for xe in (xa_, xb_):
            ax.plot([xe, xe], [1.08, y + 0.1], color=ACC, lw=0.5, ls=":")
        ax.text((xa_ + xb_) / 2, y + 0.07, "$%s = %s$" % (name, tex), color=ACC,
                fontsize=7.6, ha="center", va="bottom")
        drawn.append((name, tex))
    ax.text(xgen - 0.18, 0.5, "to\ngenerator", color=SUB, fontsize=6.6,
            ha="right", va="center", linespacing=1.1)
    ax.text((xgen + xload) / 2, -2.55,
            "line diagram, not to scale; $Z_0 = %g" % pr["z0"] + B + ",\\Omega$ "
            "throughout" + ("" if not ds else ", solution A"),
            color=SUB, fontsize=7.0, ha="center", va="top")
    drawn.append(("Z0", "Z_0 = %g" % pr["z0"] + B + ",\\Omega"))
    ax.set_xlim(xgen - 2.6, xload + 0.5)
    ax.set_ylim(-2.85, 1.85)
    fig.savefig(os.path.join(HERE, "figs", fname), dpi=210, bbox_inches="tight",
                pad_inches=0.03, transparent=True)
    plt.close(fig)
    return drawn


# ------------------------------------------------------------ coaxial section
RO, RI, T = 0.022, 0.0075, 0.006          # outer radius, inner radius, wall (lambda)
TAIL = 0.16                               # main line beyond the last stub


def _box(ax, x0, y0, x1, y1, fc, ec="none", hatch=None, z=2, lw=0.6):
    ax.add_patch(Rectangle((min(x0, x1), min(y0, y1)), abs(x1 - x0), abs(y1 - y0),
                           fc=fc, ec=ec, lw=lw, hatch=hatch, zorder=z))


def _coax_panel(ax, b, ytop):
    stubs = b["stubs"]
    left = -(b["xmax"] + TAIL)
    xs = [-s["x"] for s in stubs]
    # main line: dielectric, walls with gaps where the stubs leave, inner
    _box(ax, left, -RO, 0, RO, DIEL, z=1)
    _box(ax, left, -RO - T, 0, -RO, WALL, WALLE, "////", z=2)
    cuts = sorted([(X - RO, X + RO) for X in xs])
    x = left
    for c0, c1 in cuts:
        if c0 > x:
            _box(ax, x, RO, c0, RO + T, WALL, WALLE, "////", z=2)
        x = c1
    if x < 0:
        _box(ax, x, RO, 0, RO + T, WALL, WALLE, "////", z=2)
    _box(ax, left, -RI, 0, RI, CU, CUE, z=4)
    # load across the end: inner to outer
    _box(ax, 0, -RO - T, 0.05, RO + T, "white", INK, z=5, lw=0.9)
    ax.text(0.025, 0, "$Z_L$", color=INK, fontsize=8, ha="center", va="center",
            zorder=6)
    ax.text(left + 0.003, -RO - T - 0.012, "$" + B + "leftarrow$ to generator",
            color=SUB, fontsize=6.6, ha="left", va="top")
    xfar = max(s["x"] for s in stubs)
    for s, X in zip(stubs, xs):
        L = s["l"]
        top = L if s["kind"] == "short" else L + 0.018   # open: shell runs on
        _box(ax, X - RO, RO, X + RO, top, DIEL, z=1)
        _box(ax, X - RO - T, RO, X - RO, top, WALL, WALLE, "////", z=2)
        _box(ax, X + RO, RO, X + RO + T, top, WALL, WALLE, "////", z=2)
        _box(ax, X - RI, 0, X + RI, L, CU, CUE, z=4)
        # re-cover the joint so the tee reads as one inner conductor
        _box(ax, X - RI + 0.0005, -RI + 0.0005, X + RI - 0.0005, RI - 0.0005, CU, z=4)
        if s["kind"] == "short":
            _box(ax, X - RO - T, L, X + RO + T, L + 0.012, PLATE, z=5)
            tag = "shorting plate"
            yt = L + 0.016
        else:
            tag = "open end"
            yt = top + 0.004
        ax.text(X, yt, tag, color=SUB, fontsize=6.4, ha="center", va="bottom")
        # length from the main-line axis to the stub end
        sgn = -1 if (s["x"] < 1e-9 or (len(stubs) > 1 and s["x"] == xfar)) else 1
        dx = sgn * (RO + T + 0.014)
        ax.annotate("", xy=(X + dx, 0), xytext=(X + dx, L),
                    arrowprops=dict(arrowstyle="<|-|>", color=PIN, lw=0.8,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))
        ax.text(X + dx + sgn * 0.01, max(L / 2, RO + T + 0.012), s["label"],
                color=PIN, fontsize=7.4, ha="left" if sgn > 0 else "right",
                va="center", zorder=6,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))
    for i, (x0, x1, name, tex) in enumerate(b["dims"]):
        y = -RO - T - 0.035 - 0.05 * i
        ax.annotate("", xy=(-x1, y), xytext=(-x0, y),
                    arrowprops=dict(arrowstyle="<|-|>", color=ACC, lw=0.8,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))
        for xe in (x0, x1):
            ax.plot([-xe, -xe], [y - 0.006, -RO - T], color=ACC, lw=0.5, ls=":")
        ax.text(-(x0 + x1) / 2, y - 0.006, "$%s = %s$" % (name, tex), color=ACC,
                fontsize=7.4, ha="center", va="top")
    ax.set_title(b["title"], color=INK, fontsize=8.4, pad=3)
    ybot = -RO - T - 0.035 - 0.05 * (len(b["dims"]) - 1) - 0.03
    ax.set_xlim(left - 0.01, 0.07)
    ax.set_ylim(ybot, ytop)
    ax.set_aspect("equal")
    ax.axis("off")
    return ybot


def coax(pr, fname):
    """Coaxial longitudinal section. Returns [(what, tex)] drawn."""
    boards = design(pr)
    drawn = []
    for b in boards:
        for s in b["stubs"]:
            s["label"] = "$%s = %s$" % (s["name"], _lam(s["l"]))
            drawn.append((s["name"], _lam(s["l"])))
        for d in b["dims"]:
            drawn.append((d[2], d[3]))
    ytop = max(s["l"] for b in boards for s in b["stubs"]) + 0.05
    nd = max(len(b["dims"]) for b in boards)
    spans = [b["xmax"] + TAIL + 0.08 for b in boards]
    yspan = ytop + RO + T + 0.035 + 0.05 * (nd - 1) + 0.03
    ipl = 8.0                                     # inches per lambda
    fig, axs = plt.subplots(1, len(boards),
                            figsize=(ipl * sum(spans) * 1.06, ipl * yspan + 0.35),
                            gridspec_kw=dict(width_ratios=spans, wspace=0.10))
    axs = [axs] if len(boards) == 1 else list(axs)
    for ax, b in zip(axs, boards):
        _coax_panel(ax, b, ytop)
        # geometry replay: every inner-conductor stub drawn at its own length
        inners = [q for q in ax.patches if isinstance(q, Rectangle)
                  and q.get_facecolor()[:3] == matplotlib.colors.to_rgb(CU)
                  and q.get_y() == 0]
        assert len(inners) == len(b["stubs"]), "stub count drift"
        for s in b["stubs"]:
            assert any(abs(q.get_height() - s["l"]) < 1e-12 and
                       abs(q.get_x() + RI + s["x"]) < 1e-12 for q in inners), \
                "stub %s drawn at the wrong place or length" % s["name"]
    for ax in axs:
        ax.apply_aspect()
    y0 = min(ax.get_position().y0 for ax in axs)
    fig.text(0.5, y0 - 0.01, "coaxial line, longitudinal section; lengths in $" + B +
             "lambda$ to scale from the main-line axis, diameter not to scale",
             color=SUB, fontsize=7.0, ha="center", va="top")
    fig.savefig(os.path.join(HERE, "figs", fname), dpi=210, bbox_inches="tight",
                pad_inches=0.03, transparent=True)
    plt.close(fig)
    return drawn
