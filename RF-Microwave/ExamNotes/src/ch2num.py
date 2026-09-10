# -*- coding: utf-8 -*-
"""Generate the Chapter 2 numerical companion: ch2-num-body.tex + its figures.

Every solved problem is emitted from the SAME solver that draws its chart, so
the numbers in the prose and the numbers in the figure cannot drift apart.
The chart construction is written out step by step -- which circle to draw,
which arc to follow, what to read off the rim -- because that is what the
exam actually marks.

Run from src\\:   python ch2num.py
"""
import cmath
import io
import math
import os

import rf
import smith
from smith import SmithChart, ACC, MKC, SUB, GD, PIN

B = chr(92)          # never write a backslash through a shell heredoc
HERE = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------ formatting
def cx(z, unit="", nd=2):
    """Format a complex number the way the papers print it."""
    z = complex(z)
    re, im = z.real, z.imag
    if abs(im) < 5e-4:
        return ("%.*f%s" % (nd, re, unit))
    return "%.*f %s j%.*f%s" % (nd, re, "+" if im >= 0 else "-", nd, abs(im), unit)


def pol(z, nd=3):
    """Polar form with a degree sign that survives LaTeX (never a bare U+00B0)."""
    r, a = abs(z), math.degrees(cmath.phase(z))
    return "%.*f" % (nd, r) + B + "angle " + "%.1f^" % a + B + "circ"


def lam(x, nd=3):
    return "%.*f" % (nd, x) + B + "lambda"


def esc(s):
    return s.replace("&", B + "&").replace("%", B + "%")


# ------------------------------------------------------------- problems
# kind: 'read'  = pure Smith-chart reading
#       'ss'    = single stub
#       'ds'    = double stub
# Every entry carries the paper it came from and the marks as printed.
P = [
    dict(n=1, kind="read", yr=r"\textbf{79 Ch}", marks=[10], z0=50.0,
         zl=75 + 100j, d=0.375,
         ask="A lossless $50\\,\\Omega$ line is terminated by $75+j100\\,\\Omega$. "
             "Using the Smith chart find (a) $\\Gamma_L$, (b) VSWR, (c) $Z_{in}$ at "
             "$0.375\\lambda$ from the load, (d) the shortest length of line for which "
             "the impedance is purely resistive, and (e) the value of that resistance."),

    # ---------------------------------------------------------- single stub
    dict(n=2, kind="ss", yr=r"\textbf{72 Ash}", marks=[2, 8], z0=50.0,
         zl=80 + 100j, stub="both", micro=True,
         ask="Design single-stub shunt tuning networks (short-circuited and "
             "open-circuited) for $Z_L = 80+j100\\,\\Omega$, and sketch the "
             "realisation in microstrip."),
    dict(n=3, kind="ss", yr=r"\textbf{74 Bh}", marks=[8], z0=50.0,
         gl=0.5 * cmath.exp(1j * math.radians(51)), stub="both",
         ask="A load presents $\\Gamma_L = 0.5\\angle 51^\\circ$ on a "
             "$50\\,\\Omega$ line. Design single short-circuited and "
             "open-circuited shunt stubs using the Smith chart."),
    dict(n=4, kind="ss", yr=r"\textbf{\texttt{81 Bh}}", marks=[5, 3, 2], z0=100.0,
         zl=120 - 160j, stub="short", smat=True,
         ask="A $100\\,\\Omega$ lossless line feeds a complex load "
             "$120-j160\\,\\Omega$. Give all design steps of a single matching stub "
             "with reasoning, and the S-matrix before and after matching."),
    dict(n=5, kind="ss", yr=r"\textbf{79 Ch}", marks=[10], z0=50.0,
         zl=35 - 60j, stub="short", assumed=True,
         ask="Design a single short-circuited matching stub with self-defined line "
             "and load impedances, mentioning the steps."),
    dict(n=6, kind="ss", yr=r"\textbf{76 Bh}", marks=[10], z0=50.0,
         zl=73 + 42.5j, stub="short", smat=True, assumed=True,
         ask="Design a single-stub tuner matching a lossless line to an antenna load "
             "(any assumed placement and length) and derive its S-matrix."),
    dict(n=7, kind="ss", yr=r"72 Ma", marks=[4, 4, 2], z0=75.0,
         zl=78.27 + 60.93j, stub="both", micro=True,
         ask="Design shunt short- and open-stub matching networks using the Smith "
             "chart for $Z_0 = 75\\,\\Omega$, $Z_L = 78.27+j60.93\\,\\Omega$, and "
             "sketch the physical diagram considering microstrips."),

    # ---------------------------------------------------------- double stub
    dict(n=8, kind="ds", yr=r"71 Bh", marks=[10], z0=300.0,
         zl=300 + 300j, sp=0.375, stub="short",
         ask="Design a double-stub tuner ($3\\lambda/8$ spacing) for "
             "$Z_L = 300+j300\\,\\Omega$ on a $300\\,\\Omega$ line. Include the figure."),
    dict(n=9, kind="ds", yr=r"\textbf{70 Bh}", marks=[10], z0=100.0,
         zl=80 + 180j, sp=0.375, stub="short", f=3e9,
         ask="Design a double-stub tuner ($3\\lambda/8$ spacing) for "
             "$Z_L = 80+j180\\,\\Omega$ on a $100\\,\\Omega$ line at 3 GHz, with figure."),
    dict(n=10, kind="ds", yr=r"70 Ma", marks=[10], z0=100.0,
         zl=190 + 110j, sp=0.375, stub="short", f=10e9,
         ask="Design a double-stub tuner ($3\\lambda/8$ spacing) for "
             "$Z_L = 190+j110\\,\\Omega$ on a $100\\,\\Omega$ line at 10 GHz, with figure."),
    dict(n=11, kind="ds", yr=r"73 Ma", marks=[8], z0=50.0,
         zl=40 + 70j, sp=0.375, stub="short", assumed=True,
         ask="Design a double-stub tuner for an inductive load on a "
             "$50\\,\\Omega$ line. Include the figure."),
    dict(n=12, kind="ds", yr=r"69 Bh", marks=[3, 15], z0=50.0,
         zl=75 + 75j, sp=0.375, stub="short",
         ask="Design a short-circuited double-stub tuner with $3\\lambda/8$ spacing "
             "for $Z_L = 75+j75\\,\\Omega$ on a $50\\,\\Omega$ line."),
    dict(n=13, kind="ds", yr=r"\textbf{73 Bh}", marks=[8, 2], z0=78.0,
         zl=95 + 85j, sp=0.375, stub="short", assumed=True,
         ask="Design a short-circuited double-stub tuner for a complex inductive load "
             "on a $78.0\\,\\Omega$ line, with figure."),
    dict(n=14, kind="ds", yr=r"\textbf{75 Bh}", marks=[10, 2], z0=75.0,
         zl=(0.4 + 0.85j) * 75.0, sp=0.375, stub="short",
         ask="A $75\\,\\Omega$ coaxial line feeds a load of normalised impedance "
             "$z_L = 0.4+j0.85$. Design a short-circuited double-stub tuner."),
    dict(n=15, kind="ds", yr=r"\texttt{80 Ba}", marks=[8, 2], z0=50.0,
         zl=60 - 80j, sp=0.375, stub="open", d1=0.4, smat=True,
         ask="Design a double-stub shunt tuner using open stubs, $3\\lambda/8$ apart, "
             "the first $0.4\\lambda$ from the load, for $Z_L = 60-j80\\,\\Omega$ on a "
             "$50\\,\\Omega$ line. Prepare the S-matrix."),
    dict(n=16, kind="ds", yr=r"\textbf{\texttt{80 Bh}}", marks=[8, 2], z0=75.0,
         zl=109 + 120j, sp=0.375, stub="short", smat=True,
         ask="Design a short-circuited double-stub tuner on a $75\\,\\Omega$ coaxial "
             "line for $Z_L = 109+j120\\,\\Omega$. Prepare the S-matrix."),
    dict(n=17, kind="ds", yr=r"\texttt{81 Ba}", marks=[8, 2], z0=100.0,
         gl=0.64 * cmath.exp(1j * math.radians(58)), sp=0.375, stub="short", smat=True,
         ask="A load presents $\\Gamma_L = 0.64\\angle 58^\\circ$ on a "
             "$100\\,\\Omega$ line. Design a double-stub tuner and prepare the "
             "S-matrix of the matched network."),
    dict(n=18, kind="ds", yr=r"\textbf{\texttt{79 Bh}}", marks=[8, 2], z0=50.0,
         yl_abs=0.00813 + 0.0065j, sp=0.375, stub="short", d1=0.01, smat=True,
         ask="A $50\\,\\Omega$ lossless line feeds a load of admittance "
             "$0.00813+j0.0065\\,\\mho$. Design a double-stub shunt tuner "
             "($3\\lambda/8$ spacing, first stub $0.01\\lambda$ from the load) using "
             "the Smith chart and write the S-parameters."),
    dict(n=19, kind="ds", yr=r"\textbf{\texttt{82 Bh}}", marks=[10], z0=75.0,
         gl=0.33 * cmath.exp(1j * math.radians(66)), sp=0.375, stub="open",
         smat=True, micro=True,
         ask="A broadband microstrip antenna has load reflection coefficient "
             "$0.33\\angle 66^\\circ$ on a $75\\,\\Omega$ transmission patch. Design "
             "the matching stubs and express the scattering matrix of the matched "
             "network."),
    dict(n=20, kind="ds", yr=r"\texttt{82 Ba}", marks=[10, 2, 2], z0=100.0,
         gl=0.45 * cmath.exp(1j * math.radians(60)), sp=0.375, stub="short",
         f=10e9, smat=True, micro=True,
         ask="An antenna at 10 GHz presents $\\Gamma = |0.45|\\angle 60^\\circ$ on a "
             "$100\\,\\Omega$ line. Design a double-stub tuner, sketch the physical "
             "diagram using microstrips, and give the S-matrices before and after "
             "matching."),
    dict(n=21, kind="ds", yr=r"\textbf{80 Ch}", marks=[12], z0=100.0,
         zl=110 + 110j, sp=0.375, stub="short",
         ask="Design a double-stub tuner ($3\\lambda/8$ spacing) for "
             "$Z_L = 110+j110\\,\\Omega$ on a $100\\,\\Omega$ line: find the stub "
             "lengths and the spacing."),
    dict(n=22, kind="ds", yr=r"\textbf{78 Ch}", marks=[4, 6], z0=50.0,
         zl=100 + 50j, sp=0.375, stub="short", smat=True, theory=True,
         ask="Explain the different impedance matching techniques and give the "
             "resulting S-matrix of a perfectly matched double-stub network."),
    dict(n=23, kind="ds", yr=r"\textbf{77 Ch}", marks=[2, 8], z0=50.0,
         zl=25 - 40j, sp=0.375, stub="open", smat=True, micro=True, theory=True,
         ask="Sketch a double-stub perfectly matched network using microstrip and "
             "prepare its S-matrix."),
    dict(n=24, kind="ds", yr=r"74 Ma", marks=[2, 8], z0=50.0,
         zl=30 + 40j, sp=0.375, stub="short", theory=True,
         ask="State the advantages of double-stub matching over single-stub matching, "
             "and give the steps for matching a load with a double-stub network with "
             "an example, using the provided Smith chart."),
]


def resolve(pr):
    """Fill in zl / gl / yl_abs so every problem has a normalised z_L."""
    z0 = pr["z0"]
    if "zl" in pr:
        pr["zl_ohm"] = pr["zl"]
    elif "gl" in pr:
        pr["zl_ohm"] = z0 * rf.z_of(pr["gl"])
    elif "yl_abs" in pr:
        pr["zl_ohm"] = 1.0 / pr["yl_abs"]
    pr["zn"] = pr["zl_ohm"] / z0
    pr["yn"] = 1.0 / pr["zn"]
    return pr


# ------------------------------------------------------------- emitters
def head(pr, title):
    """The question heading, tier line and verbatim-question box."""
    o = []
    o.append(B + "Q{Problem %d --- %s}{%s}" %
             (pr["n"], title, "".join(B + "m{%d}" % m for m in pr["marks"])))
    o.append("{" + B + "color{sub}" + B + "footnotesize " + B + "yr{" + pr["yr"] +
             "} " + B + "gap$" + B + "cdot$" + B + "gap $Z_0 = %g" % pr["z0"] +
             B + ",\\Omega$}".replace(B + B, B))
    o.append("")
    o.append(B + "begin{asked}{%s \\ [%s]}" %
             (pr["yr"], "+".join(str(m) for m in pr["marks"])))
    o.append(pr["ask"])
    o.append(B + "end{asked}")
    return o


def given_block(pr):
    o = [B + "lead{Given}", B + "begin{itemize}"]
    z0, zl = pr["z0"], pr["zl_ohm"]
    if "gl" in pr:
        o.append("  " + B + "item $" + B + "Gamma_L = " + pol(pr["gl"]) + "$, $Z_0 = %g" % z0
                 + B + ",\\Omega$ $" + B + "Rightarrow$ $Z_L = Z_0(1+" + B +
                 "Gamma_L)/(1-" + B + "Gamma_L) = " + cx(zl, B + ",\\Omega") + "$.")
    elif "yl_abs" in pr:
        o.append("  " + B + "item $Y_L = " + cx(pr["yl_abs"], B + ",\\mho", 5) +
                 "$ $" + B + "Rightarrow$ $Z_L = 1/Y_L = " + cx(zl, B + ",\\Omega") + "$.")
    else:
        o.append("  " + B + "item $Z_L = " + cx(zl, B + ",\\Omega") +
                 "$, $Z_0 = %g" % z0 + B + ",\\Omega$.")
    if pr.get("assumed"):
        o.append("  " + B + "item " + B + "added{} The paper leaves the values to the "
                 "candidate; $Z_L = " + cx(zl, B + ",\\Omega") + "$ on a $%g" % z0 +
                 B + ",\\Omega$ line is assumed here. Any complex load works --- "
                 "the method is what earns the marks.")
    if pr.get("f"):
        o.append("  " + B + "item $f = %g" % (pr["f"] / 1e9) + B + "text{ GHz}$ "
                 "$" + B + "Rightarrow$ $" + B + "lambda_0 = c/f = %.1f" % (
                     299.792458 / (pr["f"] / 1e9)) + B + "text{ mm}$.")
    o.append(B + "end{itemize}")
    return o


def step(txt):
    return B + "lead{" + txt + "}"


def norm_steps(pr):
    """Steps 1-2, shared by every problem: normalise and go to admittance."""
    zn, yn = pr["zn"], pr["yn"]
    o = []
    o.append(step("Step 1 --- normalise and plot $z_L$"))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item $z_L = Z_L/Z_0 = " + cx(pr["zl_ohm"]) + "$ over $%g" % pr["z0"]
             + "$ $=" + cx(zn) + "$.")
    o.append("  " + B + "item Plot it where the $r = %.2f$ circle cuts the $x = %+.2f$ arc; "
             "it reads $%s$ on the WTG scale."
             % (zn.real, zn.imag, lam(smith.wtg(smith.p(zn)))))
    o.append("  " + B + "item $" + B + "Gamma_L = (z_L-1)/(z_L+1) = " + pol(rf.gamma_of(zn))
             + "$, so $|" + B + "Gamma_L| = %.3f$ sets the SWR-circle radius and "
             % abs(rf.gamma_of(zn)) + "$S = %.2f$." % rf.vswr(rf.gamma_of(zn)))
    o.append(B + "end{itemize}")
    o.append(step("Step 2 --- convert to admittance"))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item Draw the diameter through $z_L$ and read the opposite "
             "intersection --- a $" + B + "lambda/4$ half-turn. On an immittance chart "
             "read the amber grid in place and skip this step.")
    o.append("  " + B + "item $y_L = 1/z_L = " + cx(yn) + "$, at $%s$ on the WTG scale "
             "(exactly $0.25" % lam(smith.wtg(smith.p(yn))) + B + "lambda$ from $z_L$).")
    o.append(B + "end{itemize}")
    return o


def smatrix_block(pr, gl):
    o = [step("S-matrix before and after matching"), B + "begin{itemize}"]
    o.append("  " + B + "item \\textbf{Before} --- the bare load is a one-port, so "
             "$[S] = [" + B + "Gamma_L] = [" + pol(gl) + "]$, with $S = %.2f$."
             % rf.vswr(gl))
    o.append("  " + B + "item \\textbf{After} --- the tuner makes $Z_{in} = Z_0$, so "
             "$S_{11} = S_{22} = 0$. The network is passive and reciprocal "
             "($S_{12} = S_{21}$) and lossless, so unitarity forces $|S_{21}| = 1$:")
    o.append(B + "  \\[ [S] = " + B + "begin{bmatrix} 0 & 1 " + B + B +
             " 1 & 0 " + B + "end{bmatrix} "
             + B + "quad " + B + "text{or} " + B + "quad "
             + B + "begin{bmatrix} 0 & e^{-j" + B + "theta} " + B + B +
             " e^{-j" + B + "theta} & 0 " + B + "end{bmatrix} " + B + "]")
    o.append("  " + B + "item Keeping the $e^{-j" + B + "theta}$ records the through-path "
             "electrical length; either form earns the marks if you say which you mean.")
    o.append(B + "end{itemize}")
    return o


def micro_block(pr, lengths):
    """Convert the wavelength answers into millimetres of microstrip."""
    er, h = 4.4, 1.6
    w, ee, woh = rf.microstrip(pr["z0"], er, h)
    o = [step("Microstrip realisation"), B + "begin{itemize}"]
    o.append("  " + B + "item Take FR-4, $" + B + "epsilon_r = %.1f$, $h = %.1f" % (er, h)
             + B + "text{ mm}$. Hammerstad synthesis for $%g" % pr["z0"] + B +
             ",\\Omega$ gives $W/h = %.2f$, i.e. $W = %.2f" % (woh, w) + B +
             "text{ mm}$, with $" + B + "epsilon_e = %.2f$." % ee)
    if pr.get("f"):
        lg = rf.guide_wavelength_mm(pr["f"], ee)
        o.append("  " + B + "item $" + B + "lambda_g = " + B + "lambda_0/" + B +
                 "sqrt{" + B + "epsilon_e} = %.1f" % lg + B + "text{ mm}$ at $%g"
                 % (pr["f"] / 1e9) + B + "text{ GHz}$, so:")
        o.append("  " + B + "begin{itemize}")
        for nm, v in lengths:
            o.append("    " + B + "item $%s = %s = %.2f" % (nm, lam(v), v * lg) + B +
                     "text{ mm}$.")
        o.append("  " + B + "end{itemize}")
    else:
        o.append("  " + B + "item No frequency is given, so leave the answers in "
                 "wavelengths; multiply by $" + B + "lambda_g = " + B + "lambda_0/" +
                 B + "sqrt{" + B + "epsilon_e}$ once $f$ is fixed.")
    o.append("  " + B + "item Draw the stubs as T-junctions off the $W$-wide main line. "
             + ("Open stubs are plain truncated strips (no via needed) --- which is why "
                "open stubs are preferred in microstrip."
                if pr.get("stub") == "open" else
                "A shorted stub needs a plated via to the ground plane, drawn as a "
                "filled circle at the stub end."))
    o.append("  " + B + "item Shorten each open stub by the fringing allowance "
             "$" + B + "Delta" + B + "ell " + B + "approx 0.3h = %.2f" % (0.3 * h)
             + B + "text{ mm}$.")
    o.append(B + "end{itemize}")
    return o


# ------------------------------------------------------ Smith-chart reading
def emit_read(pr):
    zn, z0 = pr["zn"], pr["z0"]
    gl = rf.gamma_of(zn)
    S = rf.vswr(gl)
    d = pr["d"]
    zin = rf.z_in(zn, d)

    # first purely resistive point: rotate clockwise to phase 0 (Vmax) or pi (Vmin)
    ph = cmath.phase(gl)
    d_max = (ph / (2.0 * rf.TWO_PI)) % 0.5             # to phase 0
    d_min = ((ph - math.pi) / (2.0 * rf.TWO_PI)) % 0.5  # to phase pi
    if d_max <= d_min:
        d_res, r_res, which = d_max, S, "voltage maximum"
    else:
        d_res, r_res, which = d_min, 1.0 / S, "voltage minimum"

    o = head(pr, "Smith chart reading of a mismatched line")
    o += given_block(pr)
    o += norm_steps(pr)[:6]      # step 1 only; no admittance needed here
    o.append(step("Step 2 --- draw the SWR circle and read (a) and (b)"))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item Centre the compass on the chart centre and swing a circle "
             "through $z_L$. Its radius is $|" + B + "Gamma_L| = %.3f$ of the chart "
             "radius." % abs(gl))
    o.append("  " + B + "item \\textbf{(a)} $" + B + "Gamma_L = " + pol(gl) + "$ --- read the "
             "angle on the " + B + "emph{angle of reflection coefficient} scale.")
    o.append("  " + B + "item \\textbf{(b)} The circle cuts the right-hand real axis at "
             "$r = %.2f$, and on that axis $r = S$, so $" % S + B + "boxed{S = %.2f}$." % S)
    o.append(B + "end{itemize}")
    o.append(step("Step 3 --- rotate $%s$ toward the generator for (c)" % lam(d)))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item $z_L$ reads $%s$ WTG. Add $%s$: $%.3f + %.3f = %.3f$, and since "
             "this exceeds $0.5$, subtract half a turn $" % (
                 lam(smith.wtg(smith.p(zn))), lam(d), smith.wtg(smith.p(zn)), d,
                 smith.wtg(smith.p(zn)) + d) + B + "rightarrow %.3f" % (
                 (smith.wtg(smith.p(zn)) + d) % 0.5) + B + "lambda$."
             if smith.wtg(smith.p(zn)) + d >= 0.5 else
             "  " + B + "item $z_L$ reads $%s$ WTG; add $%s$ to land at $%s$." % (
                 lam(smith.wtg(smith.p(zn))), lam(d),
                 lam((smith.wtg(smith.p(zn)) + d) % 0.5)))
    o.append("  " + B + "item Staying on the SWR circle (the radius never changes on a "
             "lossless line), read $z_{in} = " + cx(zin) + "$.")
    o.append("  " + B + "item \\textbf{(c)} $Z_{in} = Z_0 z_{in} = %g " % z0 + B + "times ("
             + cx(zin) + ") = " + B + "boxed{" + cx(zin * z0, B + ",\\Omega") + "}$.")
    o.append(B + "end{itemize}")
    o.append(step("Step 4 --- shortest purely resistive point, (d) and (e)"))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item $z$ is purely resistive wherever the SWR circle crosses the "
             "\\textbf{horizontal axis} ($x = 0$) --- which happens twice per lap, at "
             "the voltage maximum (right) and the voltage minimum (left).")
    o.append("  " + B + "item Rotating clockwise from $z_L$ at $%s$, the nearer crossing is "
             "the \\textbf{%s}." % (lam(smith.wtg(smith.p(zn))), which))
    o.append("  " + B + "item \\textbf{(d)} $" + B + "boxed{d = %s}$." % lam(d_res))
    o.append("  " + B + "item \\textbf{(e)} At a %s the normalised resistance is "
             % which + ("$r = S = %.2f$" % S if which.endswith("maximum")
                        else "$r = 1/S = %.3f$" % (1.0 / S)) +
             ", so $R = %g " % z0 + B + "times %.3f = " % r_res + B + "boxed{%.1f" % (
                 r_res * z0) + B + ",\\Omega}$.")
    o.append(B + "end{itemize}")

    # figure
    sc = SmithChart(size=5.2, mode="z", title=None)
    sc.swr_circle(zn, color=ACC, ls="-", label="$S=%.2f$" % S, at=-58)
    sc.pt(zn, "$z_L$", color=MKC, dx=-0.05, ha="right")
    sc.walk(zn, d, color=ACC, label="$%s$" % lam(d, 3))
    sc.pt(zin, "$z_{in}$", color=GD, dy=-0.06, va="top")
    sc.walk(zn, d_res, color=PIN, label="$d=%s$" % lam(d_res, 3))
    sc.pt(complex(r_res, 0.0), "purely resistive\n$r=%.2f$" % r_res, color=PIN,
          dy=-0.07, va="top")
    fig = "c2num_p%02d.png" % pr["n"]
    sc.save(fig)
    return o, fig
