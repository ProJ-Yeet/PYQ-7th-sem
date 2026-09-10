# -*- coding: utf-8 -*-
"""Smith chart renderer for the RF exam-notes numerical companion.

The point of this module is that every solved problem in ch2-num.tex shows
the CONSTRUCTION, not just the answer: the load plotted, the SWR circle,
the walk along it to the g = 1 circle, the susceptance added along a
constant-g circle, and the stub length stepped off round the rim. A
student reproducing the problem by hand should be able to follow the
figure arc by arc.

Chart coordinates: a normalised value v (impedance OR admittance -- the
Y-chart is the Z-chart relabelled) sits at

        p(v) = (v - 1) / (v + 1)

and moving d wavelengths toward the generator is a CLOCKWISE rotation of
2*beta*d = 4*pi*d.

Two conventions here are easy to get backwards, and both were checked
against the readings printed in Er. Gangaju's Chapter-2 deck:

  * the WTG scale reads 0.000 at p = -1 and increases CLOCKWISE, so
    wtg = (pi - angle(p)) / (4*pi) mod 0.5. On the deck's single-stub
    problem z_L = 0.3 + j0.2 reads 0.034 and y_L, half a turn away,
    reads 0.284 -- which is the number the deck prints.

  * on an ADMITTANCE chart the terminations swap ends: y = 0 is the open
    circuit and sits at p = -1, while y = infinity is the short circuit
    at p = +1. That is the mirror of the impedance chart, and it is what
    fixes the stub length stepped off round the rim.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, FancyArrowPatch

TWO_PI = 2.0 * math.pi

# palette lifted from preamble.tex so the figures sit inside the notes
INK = "#16202A"
SUB = "#6B7785"
ACC = "#2563A8"
MKC = "#C2410C"
GD = "#15803D"
PIN = "#6D28D9"
GRID = "#C8D2DC"
GRIDF = "#E4EAF0"          # fainter grid, for the half-step circles


def p(v):
    """Chart position of a normalised value."""
    v = complex(v)
    return (v - 1.0) / (v + 1.0)


def val(pt):
    """Inverse of p()."""
    return (1.0 + pt) / (1.0 - pt)


def wtg(pt):
    """Wavelengths-toward-generator reading of a chart point.

    Zero at p = -1, increasing clockwise; one full turn is 0.5 lambda.
    """
    return ((math.pi - math.atan2(pt.imag, pt.real)) / (2.0 * TWO_PI)) % 0.5


def wtg_angle(d):
    """Chart angle, in radians, of the WTG scale reading d."""
    return math.pi - 2.0 * TWO_PI * d


def rot(pt, d):
    """Rotate d wavelengths toward the generator (clockwise)."""
    a = -2.0 * TWO_PI * d
    return pt * complex(math.cos(a), math.sin(a))


class SmithChart(object):
    # constant-resistance / conductance circles
    R_MAIN = [0.0, 0.2, 0.5, 1.0, 2.0, 5.0]
    R_FINE = [0.1, 0.3, 0.4, 0.6, 0.8, 1.5, 3.0, 10.0]
    # constant-reactance / susceptance arcs
    X_MAIN = [0.2, 0.5, 1.0, 2.0, 5.0]
    X_FINE = [0.1, 0.3, 0.4, 0.6, 0.8, 1.5, 3.0, 10.0]

    def __init__(self, size=7.2, mode="y", title=None):
        self.mode = mode                       # 'y' -> label g/b, 'z' -> r/x
        self.fig, self.ax = plt.subplots(figsize=(size, size))
        self.ax.set_aspect("equal")
        self.ax.set_xlim(-1.34, 1.34)
        self.ax.set_ylim(-1.30, 1.30)
        self.ax.axis("off")
        if title:
            self.ax.set_title(title, color=INK, fontsize=11, pad=2)
        self._grid()
        self._rim()

    # ------------------------------------------------------------- grid
    def _clip(self, patch):
        patch.set_clip_path(Circle((0, 0), 1.0, transform=self.ax.transData))
        return patch

    def _r_circle(self, r, mirror=False, **kw):
        s = -1.0 if mirror else 1.0
        c = Circle((s * r / (1.0 + r), 0.0), 1.0 / (1.0 + r), fill=False, **kw)
        self.ax.add_patch(self._clip(c))

    def _x_arc(self, x, mirror=False, **kw):
        s = -1.0 if mirror else 1.0
        if x == 0:
            self.ax.plot([-1, 1], [0, 0], **kw)
            return
        cy, rad = 1.0 / x, abs(1.0 / x)
        a = Arc((s * 1.0, s * cy), 2 * rad, 2 * rad, theta1=0, theta2=360, **kw)
        self.ax.add_patch(self._clip(a))

    def y_overlay(self, color="#B45309"):
        """Superimpose the admittance grid, i.e. the impedance grid turned
        through 180 degrees. Chart + overlay together = immittance chart."""
        thin = dict(lw=0.32, color=color, alpha=0.30, zorder=2, mirror=True)
        main = dict(lw=0.55, color=color, alpha=0.55, zorder=2, mirror=True)
        for r in self.R_FINE:
            self._r_circle(r, **thin)
        for x in self.X_FINE:
            self._x_arc(x, **thin)
            self._x_arc(-x, **thin)
        for r in self.R_MAIN:
            self._r_circle(r, **main)
        for x in self.X_MAIN:
            self._x_arc(x, **main)
            self._x_arc(-x, **main)

    def _grid(self):
        thin = dict(lw=0.35, color=GRIDF, zorder=1)
        main = dict(lw=0.6, color=GRID, zorder=1)
        for r in self.R_FINE:
            self._r_circle(r, **thin)
        for x in self.X_FINE:
            self._x_arc(x, **thin)
            self._x_arc(-x, **thin)
        for r in self.R_MAIN:
            self._r_circle(r, **main)
        self._x_arc(0, lw=0.6, color=GRID, zorder=1)
        for x in self.X_MAIN:
            self._x_arc(x, **main)
            self._x_arc(-x, **main)
        self.ax.add_patch(Circle((0, 0), 1.0, fill=False, lw=1.0,
                                 color=SUB, zorder=3))
        # label the main constant-r/g circles along the real axis
        lab = "g" if self.mode == "y" else "r"
        for r in [0.2, 0.5, 1.0, 2.0, 5.0]:
            self.ax.text(p(r).real, -0.028, ("%g" % r), color=SUB,
                         fontsize=5.6, ha="center", va="top", zorder=4)
        self.ax.text(-1.0, -0.028, lab + "=0", color=SUB, fontsize=5.6,
                     ha="left", va="top", zorder=4)

    def oc_angle(self):
        """Chart angle of the open-circuit termination."""
        return math.pi if self.mode == "y" else 0.0

    def sc_angle(self):
        return 0.0 if self.mode == "y" else math.pi

    def _rim(self):
        """Wavelengths-toward-generator scale: 0.000 at p = -1, clockwise."""
        for k in range(50):
            d = k * 0.01
            a = wtg_angle(d)
            r0 = 1.005
            r1 = 1.055 if k % 5 == 0 else 1.028
            self.ax.plot([r0 * math.cos(a), r1 * math.cos(a)],
                         [r0 * math.sin(a), r1 * math.sin(a)],
                         lw=0.5, color=SUB, zorder=3)
            if k % 5 == 0:
                self.ax.text(1.10 * math.cos(a), 1.10 * math.sin(a),
                             "%.2f" % d, color=SUB, fontsize=5.2,
                             ha="center", va="center", zorder=4,
                             rotation=math.degrees(a) - 90)
        self.ax.text(0, 1.235, "wavelengths toward generator  " + r"$\rightarrow$",
                     color=SUB, fontsize=6.2, ha="center", va="center")
        for ang, txt in ((self.oc_angle(), "o.c."), (self.sc_angle(), "s.c.")):
            self.ax.text(1.075 * math.cos(ang), 0.052, txt, color=SUB,
                         fontsize=6, ha="center", va="bottom")

    # --------------------------------------------------------- overlays
    def _clabel(self, cx, cy, rad, ang, text, color):
        """Put a short label on a circle, at angle `ang` degrees from its
        own centre, nudged outward so it clears the curve."""
        a = math.radians(ang)
        self.ax.text(cx + (rad + 0.045) * math.cos(a),
                     cy + (rad + 0.045) * math.sin(a), text, color=color,
                     fontsize=6.5, ha="center", va="center", zorder=11,
                     bbox=dict(boxstyle="round,pad=0.13", fc="white",
                               ec="none", alpha=0.82))

    def swr_circle(self, v, color=SUB, label=None, ls=":", at=-55):
        """Constant-|Gamma| circle through a value (the SWR circle)."""
        rad = abs(p(v))
        self.ax.add_patch(Circle((0, 0), rad, fill=False, lw=1.0,
                                 color=color, ls=ls, zorder=5))
        if label:
            self._clabel(0, 0, rad, at, label, color)
        return rad

    def unit_circle(self, color=GD, label="$g=1$", ls="--", at=105):
        """The g = 1 (or r = 1) matching circle: centre +1/2, radius 1/2.

        Same geometry on either chart -- p() maps a value the same way
        whether it is called an impedance or an admittance.
        """
        self.ax.add_patch(Circle((0.5, 0.0), 0.5, fill=False, lw=1.1,
                                 color=color, ls=ls, zorder=5))
        if label:
            self._clabel(0.5, 0.0, 0.5, at, label, color)

    def spacing_circle(self, d, color=PIN, label="spacing", ls="--", at=90):
        """g = 1 circle rotated d wavelengths TOWARD THE LOAD.

        A point landing on this circle is carried onto g = 1 by d
        wavelengths of line -- this is the double-stub 'spacing circle'.
        """
        a = +2.0 * TWO_PI * d                  # toward the load = anticlockwise
        cx, cy = 0.5 * math.cos(a), 0.5 * math.sin(a)
        self.ax.add_patch(Circle((cx, cy), 0.5, fill=False, lw=1.1,
                                 color=color, ls=ls, zorder=5))
        if label:
            self._clabel(cx, cy, 0.5, at, label, color)

    def g_circle(self, g, color=MKC, ls=(0, (4, 2)), label=None, at=150):
        """Highlight one constant-conductance circle -- the track a shunt
        stub moves the point along."""
        self._r_circle(g, lw=0.9, color=color, ls=ls, zorder=4)
        if label:
            self._clabel(g / (1.0 + g), 0.0, 1.0 / (1.0 + g), at, label, color)

    # ----------------------------------------------------------- points
    def pt(self, v, label, color=MKC, dx=0.045, dy=0.045, ha="left",
           va="bottom", ms=4.6):
        q = p(v)
        self.ax.plot([q.real], [q.imag], "o", ms=ms, color=color,
                     mec="white", mew=0.7, zorder=9)
        if label:
            self.ax.text(q.real + dx, q.imag + dy, label, color=color,
                         fontsize=7.2, ha=ha, va=va, zorder=10,
                         bbox=dict(boxstyle="round,pad=0.13", fc="white",
                                   ec="none", alpha=0.72))
        return q

    # ------------------------------------------------------------- arcs
    def walk(self, v_from, d, color=ACC, lw=1.6, label=None, shrink=0.0):
        """Arc along the constant-|Gamma| circle, d wavelengths toward
        the generator, with an arrowhead at the far end."""
        q0 = p(v_from)
        rad = abs(q0)
        a0 = math.degrees(math.atan2(q0.imag, q0.real))
        a1 = a0 - 360.0 * 2.0 * d
        self.ax.add_patch(Arc((0, 0), 2 * rad, 2 * rad, theta1=min(a0, a1),
                              theta2=max(a0, a1), lw=lw, color=color,
                              zorder=7))
        # arrowhead
        am = math.radians(a1 + (2.0 if a1 < a0 else -2.0))
        ah = math.radians(a1)
        self.ax.add_patch(FancyArrowPatch(
            (rad * math.cos(am), rad * math.sin(am)),
            (rad * math.cos(ah), rad * math.sin(ah)),
            arrowstyle="-|>", mutation_scale=11, color=color, lw=0,
            zorder=8))
        if label:
            amid = math.radians((a0 + a1) / 2.0)
            self.ax.text((rad + 0.055) * math.cos(amid),
                         (rad + 0.055) * math.sin(amid), label, color=color,
                         fontsize=6.8, ha="center", va="center", zorder=10,
                         bbox=dict(boxstyle="round,pad=0.12", fc="white",
                                   ec="none", alpha=0.8))
        return rot(q0, d)

    def along_g(self, v_from, v_to, color=MKC, lw=1.5, label=None):
        """Arc along a constant-conductance circle: what a shunt stub does."""
        g = complex(v_from).real
        cx, rad = g / (1.0 + g), 1.0 / (1.0 + g)
        q0, q1 = p(v_from), p(v_to)
        a0 = math.degrees(math.atan2(q0.imag, q0.real - cx))
        a1 = math.degrees(math.atan2(q1.imag, q1.real - cx))
        if abs(a1 - a0) > 180:                 # take the short way round
            a0 += 360.0 if a0 < a1 else -360.0
        self.ax.add_patch(Arc((cx, 0), 2 * rad, 2 * rad, theta1=min(a0, a1),
                              theta2=max(a0, a1), lw=lw, color=color,
                              ls="-", zorder=7))
        am = math.radians(a1 + (1.6 if a1 < a0 else -1.6))
        ah = math.radians(a1)
        self.ax.add_patch(FancyArrowPatch(
            (cx + rad * math.cos(am), rad * math.sin(am)),
            (cx + rad * math.cos(ah), rad * math.sin(ah)),
            arrowstyle="-|>", mutation_scale=10, color=color, lw=0, zorder=8))
        if label:
            amid = math.radians((a0 + a1) / 2.0)
            self.ax.text(cx + (rad + 0.05) * math.cos(amid),
                         (rad + 0.05) * math.sin(amid), label, color=color,
                         fontsize=6.8, ha="center", va="center", zorder=10,
                         bbox=dict(boxstyle="round,pad=0.12", fc="white",
                                   ec="none", alpha=0.8))

    def rim_walk(self, b, kind, color=PIN, label=None, r=1.075):
        """Step a stub length off round the rim, from the s.c./o.c. point
        to the susceptance b. This is how the stub length is read."""
        start = self.oc_angle() if kind == "open" else self.sc_angle()
        end = math.atan2(p(complex(0, b)).imag, p(complex(0, b)).real)
        a0, a1 = math.degrees(start), math.degrees(end)
        while a1 > a0:
            a1 -= 360.0                                 # clockwise = toward gen
        self.ax.add_patch(Arc((0, 0), 2 * r, 2 * r, theta1=a1, theta2=a0,
                              lw=1.5, color=color, zorder=7))
        am = math.radians(a1 + 2.0)
        ah = math.radians(a1)
        self.ax.add_patch(FancyArrowPatch(
            (r * math.cos(am), r * math.sin(am)),
            (r * math.cos(ah), r * math.sin(ah)),
            arrowstyle="-|>", mutation_scale=11, color=color, lw=0, zorder=8))
        if label:
            amid = math.radians((a0 + a1) / 2.0)
            self.ax.text((r + 0.075) * math.cos(amid),
                         (r + 0.075) * math.sin(amid), label, color=color,
                         fontsize=6.8, ha="center", va="center", zorder=10,
                         bbox=dict(boxstyle="round,pad=0.12", fc="white",
                                   ec="none", alpha=0.85))

    def note(self, text, y=-1.235):
        self.ax.text(0, y, text, color=SUB, fontsize=6.4, ha="center",
                     va="center")

    # ------------------------------------------------------------- save
    def save(self, name, folder=None):
        folder = folder or os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "figs")
        if not os.path.isdir(folder):
            os.makedirs(folder)
        path = os.path.join(folder, name)
        self.fig.savefig(path, dpi=210, bbox_inches="tight",
                         pad_inches=0.02, transparent=True)
        plt.close(self.fig)
        return path


if __name__ == "__main__":
    # smoke test: Gangaju double-stub P1, ZL = 60 - j80 on 50 ohm,
    # open stubs, lambda/8 apart, first stub at the load.
    import rf
    zl = (60 - 80j) / 50.0
    yl = 1.0 / zl
    sol = rf.double_stub(zl, 0.125, "open", 0.0)[0]

    # ---- geometry checks: the drawing must agree with the algebra ----
    def near(a, b, tol=1e-9):
        assert abs(a - b) < tol, "%r != %r" % (a, b)

    # the deck reads z_L = 0.3 + j0.2 at 0.034 and y_L at 0.284
    near(wtg(p(0.3 + 0.2j)), 0.03436, 1e-4)
    near(wtg(p(1.0 / (0.3 + 0.2j))), 0.28436, 1e-4)
    # y_a sits on the spacing circle (g = 1 rotated lambda/8 toward load)
    ctr = 0.5 * complex(math.cos(2 * TWO_PI * 0.125), math.sin(2 * TWO_PI * 0.125))
    near(abs(p(sol["ya"]) - ctr), 0.5, 1e-9)
    # y_2 sits on the g = 1 circle, centre +1/2
    near(abs(p(sol["y2"]) - 0.5), 0.5, 1e-9)
    # o.c. of an admittance chart is at p = -1, s.c. at p = +1
    near(p(0.0).real, -1.0)
    # stepping the stub length round the rim spans exactly l2
    a_oc, a_b2 = math.pi, math.atan2(p(1j * sol["b2"]).imag,
                                     p(1j * sol["b2"]).real)
    near(((a_oc - a_b2) % TWO_PI) / (2.0 * TWO_PI), sol["l2"], 1e-9)
    print("geometry checks pass")

    sc = SmithChart(title="Double-stub tuner  $z_L = 1.2 - j1.6$, "
                          "open stubs, $d = \\lambda/8$")
    sc.unit_circle(at=118)
    sc.spacing_circle(0.125, label="spacing", at=118)
    sc.g_circle(yl.real, label="$g=%.2f$" % yl.real, at=196)
    sc.swr_circle(sol["ya"], label="SWR", at=-60)
    sc.pt(zl, "$z_L$", color=SUB, dx=-0.05, dy=-0.05, ha="right", va="top")
    sc.pt(yl, "$y_L$", color=MKC, dx=-0.05, ha="right")
    sc.pt(sol["ya"], "$y_a$", color=GD)
    sc.pt(sol["y2"], "$y_2$", color=ACC, dy=-0.06, va="top")
    sc.along_g(yl, sol["ya"], label="$+jb_1$")
    sc.walk(sol["ya"], 0.125, label="$\\lambda/8$")
    sc.rim_walk(sol["b2"], "open", label="$\\ell_2$")
    sc.note("$b_1 = %+.3f$, $\\ell_1 = %.3f\\lambda$   $\\cdot$   "
            "$b_2 = %+.3f$, $\\ell_2 = %.3f\\lambda$"
            % (sol["b1"], sol["l1"], sol["b2"], sol["l2"]))
    print("wrote", sc.save("_smoke_doublestub.png"))
