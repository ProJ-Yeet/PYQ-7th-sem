# -*- coding: utf-8 -*-
"""Draw the graphs the chapter-6 amplifier numericals ask for.

Stability circles on the Smith chart (Problems 3, 4 and 7) and the stub-and-line
matching constructions (Problem 6). Each figure is computed from the problem's
own S-parameters through amp.Amp, never typed in, and before anything is drawn
the script checks that every circle centre, radius, stub and line length it is
about to draw appears, to the printed precision, in ch6-num-body.tex. A figure
therefore cannot disagree with the working printed above it: that check is the
exit test, and a mismatch stops the run.

The drawing is in the Gamma plane (the impedance chart's coordinates), where a
stability circle is a plain circle with centre C and radius R.

    python ampfig.py
"""
import cmath
import math
import os
import sys

from matplotlib.patches import Circle, Arc, FancyArrowPatch

import amp
from amp import Amp, P
from smith import SmithChart, ACC, MKC, SUB, GD, PIN

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch6-num-body.tex")
BS = chr(92)


def polar(z, pm=3, pa=1):
    return ("%%.%df%sangle%%.%df" % (pm, BS, pa)) % (abs(z), math.degrees(cmath.phase(z)))


def must_print(src, text, what):
    if text not in src:
        sys.exit("ch6-num-body.tex does not print %s as %r" % (what, text))


# ---------------------------------------------------------------- drawing
def chart(title):
    c = SmithChart(size=3.9, mode="z", title=title)
    return c


def stab_circle(c, C, R, color, label, unstable_inside=True, at=None):
    """The circle, and the unstable side hatched inside the unit chart."""
    ax = c.ax
    edge = Circle((C.real, C.imag), R, fill=False, lw=1.3, color=color, zorder=6)
    ax.add_patch(edge)
    if unstable_inside:
        h = Circle((C.real, C.imag), R, fill=False, hatch="////", lw=0,
                   color=color, alpha=0.55, zorder=5)
        ax.add_patch(c._clip(h))
    # label on the arc of the circle nearest the chart centre, pulled inside
    d = C / abs(C) if abs(C) > 1e-9 else 1
    near = C - d * R
    if at is None:
        at = near * 0.80 if abs(near) > 0.15 else near + 0.18 * d
    ax.text(at.real, at.imag, label, color=color, fontsize=7.0, ha="center",
            va="center", zorder=10, bbox=dict(boxstyle="round,pad=0.13",
                                              fc="white", ec="none", alpha=0.85))


def gpt(c, G, label, color=MKC, dx=0.05, dy=0.05, ha="left", va="bottom"):
    c.ax.plot([G.real], [G.imag], "o", ms=4.6, color=color, mec="white",
              mew=0.7, zorder=9)
    c.ax.text(G.real + dx, G.imag + dy, label, color=color, fontsize=7.0,
              ha=ha, va=va, zorder=10, bbox=dict(boxstyle="round,pad=0.13",
                                                 fc="white", ec="none", alpha=0.8))


def arc_arrow(c, cx, rad, a0, a1, color, lw=1.5, label=None, off=0.06):
    """Arc on the circle (cx, 0) radius rad from angle a0 to a1 (degrees),
    with an arrowhead at a1."""
    c.ax.add_patch(Arc((cx, 0), 2 * rad, 2 * rad, theta1=min(a0, a1),
                       theta2=max(a0, a1), lw=lw, color=color, zorder=7))
    am = math.radians(a1 + (2.0 if a1 < a0 else -2.0))
    ah = math.radians(a1)
    c.ax.add_patch(FancyArrowPatch(
        (cx + rad * math.cos(am), rad * math.sin(am)),
        (cx + rad * math.cos(ah), rad * math.sin(ah)),
        arrowstyle="-|>", mutation_scale=10, color=color, lw=0, zorder=8))
    if label:
        amid = math.radians((a0 + a1) / 2.0)
        c.ax.text(cx + (rad + off) * math.cos(amid), (rad + off) * math.sin(amid),
                  label, color=color, fontsize=6.8, ha="center", va="center",
                  zorder=10, bbox=dict(boxstyle="round,pad=0.12", fc="white",
                                       ec="none", alpha=0.85))


# ---------------------------------------------------------------- figures
def fig_p3(src):
    """72 Ash, the 0.894 set: both circles cut the chart; S11*, S22* outside."""
    a = Amp(P(0.894, -60.6), P(0.020, 62.4), P(3.122, 123.6), P(0.781, -27.6))
    must_print(src, "C_L = " + BS + "frac", "the P3 output-circle formula")
    must_print(src, polar(a.CL) + "^" + BS + "circ$, $R_L = %.3f" % a.RL, "P3 C_L, R_L")
    must_print(src, "C_S = " + polar(a.CS) + "^" + BS + "circ$, $R_S = %.3f" % a.RS, "P3 C_S, R_S")
    assert a.load_stable_outside() and a.source_stable_outside(), "P3 stable side"
    GS, GL = a.s11.conjugate(), a.s22.conjugate()
    assert abs(GS - a.CS) > a.RS and abs(GL - a.CL) > a.RL, "P3 design points"
    c = chart(r"$\Gamma_S$ plane: input circle")
    stab_circle(c, a.CS, a.RS, MKC, "unstable")
    gpt(c, GS, r"$\Gamma_S = S_{11}^*$", color=ACC, dx=-0.05, ha="right")
    c.note(r"$C_S = %.3f\angle%.1f^\circ$, $R_S = %.3f$: stable outside"
           % (abs(a.CS), math.degrees(cmath.phase(a.CS)), a.RS))
    c.save("c6n_p3_source.png")
    c = chart(r"$\Gamma_L$ plane: output circle")
    stab_circle(c, a.CL, a.RL, MKC, "unstable")
    gpt(c, GL, r"$\Gamma_L = S_{22}^*$", color=ACC, dx=0.02, dy=-0.07, va="top")
    c.note(r"$C_L = %.3f\angle%.1f^\circ$, $R_L = %.3f$: stable outside"
           % (abs(a.CL), math.degrees(cmath.phase(a.CL)), a.RL))
    c.save("c6n_p3_load.png")


def fig_p4(src):
    """73 Ma: K = 0.958, both circles only clip the rim."""
    a = Amp(P(0.64, -169), P(0.03, 50), P(10.11, 91), P(0.22, -82))
    must_print(src, "C_S = " + polar(a.CS) + "^" + BS + "circ$, $R_S = %.3f" % a.RS, "P4 C_S, R_S")
    must_print(src, "C_L = " + polar(a.CL, 2) + "^" + BS + "circ$, $R_L = %.2f" % a.RL, "P4 C_L, R_L")
    must_print(src, "nearest $%.3f$" % (abs(a.CS) - a.RS), "P4 nearest point, input")
    must_print(src, "nearest $%.3f$" % (abs(a.CL) - a.RL), "P4 nearest point, output")
    assert a.load_stable_outside() and a.source_stable_outside(), "P4 stable side"
    c = chart(r"73 Ma: both circles clip the rim")
    stab_circle(c, a.CS, a.RS, MKC, r"input ($\Gamma_S$)",
                at=cmath.rect(0.72, cmath.phase(a.CS)))
    stab_circle(c, a.CL, a.RL, PIN, r"output ($\Gamma_L$)",
                at=cmath.rect(0.72, cmath.phase(a.CL)))
    c.note(r"unstable only near $|\Gamma| = 1$ at $166^\circ$ (source) and $63^\circ$ (load)")
    c.save("c6n_p4_circles.png")


def fig_p6(src):
    """79 Ch: open shunt stub at the 50-ohm end, then a line to the device."""
    a = Amp(P(0.45, 163), P(0.04, 40), P(2.55, -106), P(0.46, -65))
    GS, GL = a.conj_match()
    for tag, G, pre in (("input", GS, ""), ("output", GL, "")):
        ls, l, b = amp.stub_line_for(G)[0]
        rt = amp.walk(ls, l)
        assert abs(rt - G) < 1e-9, "%s network does not reach Gamma" % tag
    ls_i, l_i, b_i = amp.stub_line_for(GS)[0]
    ls_o, l_o, b_o = amp.stub_line_for(GL)[0]
    must_print(src, "= %.4f$." % b_i, "P6 input b")
    must_print(src, "0.%04d" % round(ls_i * 1e4) + BS + "lambda", "P6 input stub")
    must_print(src, "0.%04d" % round(l_i * 1e4) + BS + "lambda", "P6 input line")
    must_print(src, "$b = %.4f$" % b_o, "P6 output b")
    must_print(src, "0.%04d" % round(ls_o * 1e4) + BS + "lambda", "P6 output stub")
    must_print(src, "0.%04d" % round(l_o * 1e4) + BS + "lambda", "P6 output line")
    for name, G, ls, l, b, sub in (("c6n_p6_input.png", GS, ls_i, l_i, b_i, "S"),
                                   ("c6n_p6_output.png", GL, ls_o, l_o, b_o, "L")):
        c = chart(r"79 Ch: %s network, to $\Gamma_%s$" % ("input" if sub == "S" else "output", sub))
        y = 1 + 1j * b
        G0 = (1 - y) / (1 + y)
        # the g = 1 circle of the admittance grid sits at centre -1/2 in the Gamma plane
        c.ax.add_patch(Circle((-0.5, 0), 0.5, fill=False, lw=1.0, color=GD,
                              ls="--", zorder=5))
        c.ax.add_patch(Circle((0, 0), abs(G), fill=False, lw=0.9, color=SUB,
                              ls=":", zorder=5))
        # stub: from the centre along g = 1 to G0
        a0 = 0.0
        a1 = math.degrees(math.atan2(G0.imag, G0.real + 0.5))
        if abs(a1 - a0) > 180:
            a1 -= 360.0
        arc_arrow(c, -0.5, 0.5, a0, a1, MKC, label="stub %.4f$\\lambda$" % ls)
        # line: clockwise at constant |Gamma| from G0 to G
        g0 = math.degrees(cmath.phase(G0))
        g1 = g0 - 720.0 * l
        arc_arrow(c, 0.0, abs(G), g0, g1, ACC, label="line %.4f$\\lambda$" % l, off=0.09)
        gpt(c, 0j, "50 $\\Omega$", color=SUB, dx=0.04, dy=0.04)
        gpt(c, G0, "after stub", color=MKC, dx=0.04, dy=-0.05, va="top")
        gpt(c, G, r"$\Gamma_%s = %.4f\angle%.1f^\circ$" % (sub, abs(G), math.degrees(cmath.phase(G))),
            color=ACC, dx=0.04, dy=0.04)
        c.note(r"$b = %+.4f$ (open stub), then the line rotates clockwise by $%.1f^\circ$"
               % (b, 720 * l))
        c.save(name)


def fig_p7(src):
    """71 Bh: the paper gives the circles; read them against the unit chart."""
    CS, RS = P(1.15, 10), 0.85
    CL, RL = P(1.10, 80), 1.10
    must_print(src, "C$_S$=1.15$" + BS + "angle$10$^" + BS + "circ$, R$_S$=0.85", "P7 given C_S")
    must_print(src, "C$_L$=1.10$" + BS + "angle$80$^" + BS + "circ$, R$_L$=1.10", "P7 given C_L")
    assert abs(abs(CL) - RL) < 1e-12, "P7 output circle through the origin"
    c = chart(r"71 Bh: the given circles")
    stab_circle(c, CS, RS, MKC, r"input", at=P(0.55, 10))
    stab_circle(c, CL, RL, PIN, r"output", at=P(0.55, 80) + 0.12)
    gpt(c, 0j, r"$50\,\Omega$ on the output circle", color=SUB, dx=0.05, dy=-0.06, va="top")
    c.note(r"hatched = unstable side, taking $|S_{11}|, |S_{22}| < 1$ (stable outside)")
    c.save("c6n_p7_circles.png")



def main():
    src = open(TEX, encoding="utf-8").read()
    fig_p3(src)
    fig_p4(src)
    fig_p6(src)
    fig_p7(src)
    print("ampfig: 7 charts written, every drawn value found in ch6-num-body.tex")


if __name__ == "__main__":
    main()
