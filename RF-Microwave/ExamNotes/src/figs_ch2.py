# -*- coding: utf-8 -*-
"""Chapter 2 theory figures: the blank chart and the immittance chart.

Run from src\\:   python figs_ch2.py
"""
import smith
from smith import SmithChart, ACC, MKC, SUB, GD, PIN


def blank_chart():
    """A labelled chart for the 'sketch and explain the Smith chart' asks."""
    sc = SmithChart(size=7.2, mode="z",
                    title="The Smith chart: constant-$r$ circles and "
                          "constant-$x$ arcs")
    sc.unit_circle(color=GD, label="$r=1$", at=108)
    ax = sc.ax
    ax.plot([0], [0], "o", ms=4.4, color=ACC, mec="white", mew=0.7, zorder=9)
    ax.text(0.02, 0.055, "centre: $z=1$\n(matched, $\\Gamma=0$)", color=ACC,
            fontsize=6.6, ha="center", va="bottom", zorder=10)
    for v, lab, c, dx, dy, ha, va in (
            (0.0, "$z=0$  short\n$\\Gamma=-1$", MKC, -0.03, -0.06, "left", "top"),
            (1e9, "$z=\\infty$  open\n$\\Gamma=+1$", MKC, 0.03, -0.06, "right", "top"),
            (1j, "$z=j$  (upper half:\ninductive, $+x$)", PIN, -0.05, 0.05, "right", "bottom"),
            (-1j, "$z=-j$  (lower half:\ncapacitive, $-x$)", PIN, -0.05, -0.05, "right", "top")):
        sc.pt(v, lab, color=c, dx=dx, dy=dy, ha=ha, va=va, ms=4.2)
    sc.note("every point is one normalised impedance $z=r+jx$; "
            "$|\\Gamma|$ is its distance from the centre, so one lap of the "
            "rim is $\\lambda/2$ of line")
    return sc.save("c2_smith_blank.png")


def immittance_chart():
    """Z grid plus the 180-degree-rotated Y grid -- asked in 5 papers.

    The teaching point: ONE location carries BOTH readings. A plain Smith
    chart makes you rotate a quarter wavelength to convert z to y; the
    immittance chart has that half-turn printed into the second grid.
    """
    AMB = "#B45309"
    sc = SmithChart(size=7.2, mode="z",
                    title="Immittance chart = impedance grid $+$ "
                          "admittance grid")
    sc.y_overlay(color=AMB)
    z = 0.5 + 0.7j
    y = 1.0 / z                       # 0.676 - j0.946
    q = smith.p(z)

    # one point, two readings
    sc.ax.plot([q.real], [q.imag], "o", ms=6.0, color=SUB, mec="white",
               mew=0.9, zorder=10)
    sc.ax.text(q.real - 0.055, q.imag + 0.05,
               "$z = 0.5 + j0.7$\n(blue grid)", color=ACC, fontsize=7.0,
               ha="right", va="bottom", zorder=11,
               bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none",
                         alpha=0.85))
    sc.ax.text(q.real + 0.055, q.imag - 0.05,
               "$y = 0.68 - j0.95$\n(amber grid)", color=AMB, fontsize=7.0,
               ha="left", va="top", zorder=11,
               bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none",
                         alpha=0.85))

    # where a PLAIN chart would make you go for the same y
    sc.ax.plot([q.real, -q.real], [q.imag, -q.imag], lw=0.9, color=SUB,
               ls="--", zorder=6)
    sc.ax.plot([-q.real], [-q.imag], "o", ms=4.0, color=SUB, alpha=0.55,
               zorder=7)
    sc.ax.text(-q.real + 0.05, -q.imag - 0.05,
               "on a plain chart $y$ is read\nhere, a $\\lambda/4$ turn away",
               color=SUB, fontsize=6.4, ha="left", va="top", zorder=8)
    sc.note("one location, two readings: the $\\lambda/4$ half-turn that "
            "converts $z\\to y$ is printed into the second grid, so no "
            "rotation is needed")
    return sc.save("c2_immittance.png")


if __name__ == "__main__":
    for f in (blank_chart, immittance_chart):
        print("wrote", f())
