# -*- coding: utf-8 -*-
"""Stub-matching emitters and the driver for the Ch2 numerical companion.

Layout choice: the steps flow full width and the chart follows as a centred
figure. A \\sbs pair is an UNBREAKABLE box, so putting a page of steps in one
would force whole problems onto fresh pages and leave huge gaps.

Run from src\\:   python ch2gen.py
"""
import cmath
import io
import math
import os

import ch2num as C
import msfig
import stubfig
from PIL import Image
import rf
import smith
from ch2num import B, cx, pol, lam, step, head, given_block, norm_steps, \
    smatrix_block, micro_block, resolve, emit_read
from smith import SmithChart, ACC, MKC, SUB, GD, PIN

HERE = os.path.dirname(os.path.abspath(__file__))
TERM = {"short": "short-circuit point ($y=\\infty$, the right of the chart)",
        "open": "open-circuit point ($y=0$, the left of the chart)"}


def _stub_kinds(pr):
    return ["short", "open"] if pr["stub"] == "both" else [pr["stub"]]


# --------------------------------------------------------------- single stub
def emit_ss(pr):
    zn, yn, z0 = pr["zn"], pr["yn"], pr["z0"]
    gl = rf.gamma_of(zn)
    kinds = _stub_kinds(pr)
    sols = rf.single_stub(zn, kinds[0])

    o = head(pr, "Single-stub shunt tuner")
    o += given_block(pr)
    o += norm_steps(pr)

    o.append(step("Step 3 --- walk to the $g=1$ circle"))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item Swing the SWR circle (radius $|" + B +
             "Gamma_L| = %.3f$) through $y_L$." % abs(gl))
    o.append("  " + B + "item Rotate \\textbf{clockwise} (toward the generator) to each "
             "intersection with the \\textbf{$g=1$ circle}. There are always two:")
    o.append("  " + B + "begin{itemize}")
    for i, s in enumerate(sols):
        a = round(smith.wtg(smith.p(s["y_or_z"])), 3)
        b = round(smith.wtg(smith.p(yn)), 3)
        # clockwise from y_L; past the 0.5 mark the WTG scale restarts at 0
        arith = ("%.3f - %.3f" % (a, b) if a >= b else
                 "(0.500 - %.3f) + %.3f" % (b, a))
        eq = "=" if abs(((a - b) % 0.5) - round(s["d"], 3)) < 5e-4 else B + "approx"
        o.append("    " + B + "item $y_%d = %s$ at $%s$ WTG, so $d_%d = %s %s %s$."
                 % (i + 1, cx(s["y_or_z"]), lam(a), i + 1, arith, eq, lam(s["d"])))
    o.append("  " + B + "end{itemize}")
    o.append("  " + B + "item Only the \\emph{susceptance} is left to cancel: the "
             "conductance is already 1.")
    o.append(B + "end{itemize}")

    o.append(step("Step 4 --- read each stub length off the rim"))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item The stub must present the negative of the residual "
             "susceptance. Start at the stub's own termination and run "
             "\\textbf{clockwise round the rim} until you reach that value; the arc, "
             "read on the WTG scale, is the length.")
    for k in kinds:
        ss = rf.single_stub(zn, k)
        o.append("  " + B + "item \\textbf{%s-circuited stub} --- start at the %s:"
                 % (k.capitalize(), TERM[k]))
        o.append("  " + B + "begin{itemize}")
        for i, s in enumerate(ss):
            o.append("    " + B + "item needs $b = %+.3f$, giving $" % s["cancel"] +
                     B + "ell_%d = %s$." % (i + 1, lam(s["l"])))
        o.append("  " + B + "end{itemize}")
    o.append(B + "end{itemize}")

    # answer table
    o.append(step("Answer"))
    o.append(B + "begin{tabularx}{" + B + "linewidth}{@{}L{2.6cm}X X@{}}")
    o.append(B + "toprule")
    o.append(B + "hrow " + B + "thead{Quantity} & " + B + "thead{Solution 1} & "
             + B + "thead{Solution 2} " + B + B)
    o.append(B + "midrule")
    o.append(B + "textbf{Stub distance $d$} & $%s$ & $%s$ " % (
        lam(sols[0]["d"]), lam(sols[1]["d"])) + B + B)
    o.append(B + "textbf{Line admittance} & $%s$ & $%s$ " % (
        cx(sols[0]["y_or_z"]), cx(sols[1]["y_or_z"])) + B + B)
    for k in kinds:
        ss = rf.single_stub(zn, k)
        o.append(B + "textbf{%s stub $" % k.capitalize() + B + "ell$} & $%s$ & $%s$ "
                 % (lam(ss[0]["l"]), lam(ss[1]["l"])) + B + B)
    o.append(B + "bottomrule")
    o.append(B + "end{tabularx}")
    o.append("")
    o.append(B + "lead{Which to build} Solution 1 puts the stub closer to the load "
             "($%s$ against $%s$), so the high-VSWR section is shorter: lower loss and "
             "wider bandwidth. Prefer it unless the layout forbids it."
             % (lam(sols[0]["d"]), lam(sols[1]["d"])))

    if pr.get("smat"):
        o += smatrix_block(pr, gl)
    if pr.get("micro"):
        o += micro_block(pr, [("d", sols[0]["d"]),
                              (B + "ell_1", rf.single_stub(zn, kinds[0])[0]["l"])])

    # ------------------------------------------------------------ figure
    s = sols[0]
    k = kinds[0]
    sc = SmithChart(size=5.2, mode="y", title=None)
    sc.unit_circle(at=118)
    sc.swr_circle(yn, label="SWR", at=-62)
    sc.pt(zn, "$z_L$", color=SUB, dx=-0.05, dy=-0.05, ha="right", va="top")
    sc.pt(yn, "$y_L$", color=MKC, dx=-0.05, ha="right")
    sc.walk(yn, s["d"], color=ACC, label="$d=%s$" % lam(s["d"]))
    sc.pt(s["y_or_z"], "$y_1=%s$" % cx(s["y_or_z"]), color=GD)
    sc.rim_walk(s["cancel"], k, label="$" + B + "ell_1$")
    sc.note("solution 1: $d = %s$, $%s$ stub $" % (lam(s["d"]), k)
            + B + "ell = %s$" % lam(rf.single_stub(zn, k)[0]["l"]))
    fig = "c2num_p%02d.png" % pr["n"]
    sc.save(fig)
    return o, fig


# --------------------------------------------------------------- double stub
def _free_angle(cx0, cy0, rad, busy):
    """Label angle (degrees) on a circle, as far as possible from the busy
    points, keeping the label inside the chart and off the g = 1 label."""
    best, far = 118.0, -1.0
    for k in range(0, 360, 10):
        q = complex(cx0, cy0) + (rad + 0.045) * cmath.exp(1j * math.radians(k))
        if abs(q) > 0.97:
            continue
        m = min(abs(q - bq) for bq in busy)
        if m > far:
            best, far = float(k), m
    return best


def _walk_label(v, d):
    """Where SmithChart.walk puts its label: arc midpoint, pushed outward."""
    q = smith.p(v)
    a = cmath.phase(q) - 2.0 * math.pi * d          # half of the 4 pi d sweep
    return (abs(q) + 0.055) * cmath.exp(1j * a)


def _free_offset(q, busy, r=0.075):
    """pt() keywords putting a point's label in the emptiest of 16 directions."""
    best, far = None, -1.0
    for k in range(16):
        u = cmath.exp(1j * math.pi * k / 8.0)
        c = q + (r + 0.04) * u                     # rough label centre
        if abs(c) > 1.0:
            continue
        m = min([abs(c - b) for b in busy] or [9.0])
        if m > far:
            best, far = (u, c), m
    u, c = best
    return dict(dx=r * u.real, dy=r * u.imag, centre=c,
                ha="left" if u.real > 0.35 else "right" if u.real < -0.35 else "center",
                va="bottom" if u.imag > 0.35 else "top" if u.imag < -0.35 else "center")


def emit_ds(pr):
    zn, yn, z0 = pr["zn"], pr["yn"], pr["z0"]
    sp, k, d1 = pr["sp"], pr["stub"], pr.get("d1", 0.0)
    gl = rf.gamma_of(zn)
    sols = rf.double_stub(zn, sp, k, d1)
    a, b = sols[0], sols[1]
    y1 = a["y1"]
    spname = "3" + B + "lambda/8" if abs(sp - 0.375) < 1e-9 else (
        B + "lambda/8" if abs(sp - 0.125) < 1e-9 else lam(sp))

    o = head(pr, "Double-stub shunt tuner")
    o += given_block(pr)
    o += norm_steps(pr)

    nstep = 3
    if d1 > 0:
        o.append(step("Step %d --- walk to the first stub" % nstep))
        o.append(B + "begin{itemize}")
        o.append("  " + B + "item The first stub sits $%s$ from the load, so rotate $y_L$ "
                 "\\textbf{clockwise} that far along the SWR circle." % lam(d1))
        o.append("  " + B + "item $y_1 = %s$ at $%s$ WTG --- the admittance seen "
                 "\\emph{just before} stub 1." % (cx(y1), lam(smith.wtg(smith.p(y1)))))
        o.append(B + "end{itemize}")
        nstep += 1
    else:
        o.append(step("Step %d --- the first stub is at the load" % nstep))
        o.append(B + "begin{itemize}")
        o.append("  " + B + "item No offset is specified, so stub 1 sits at the load and "
                 "$y_1 = y_L = %s$." % cx(y1))
        o.append(B + "end{itemize}")
        nstep += 1

    o.append(step("Step %d --- draw the spacing circle" % nstep))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item Rotate the $g=1$ circle $%s$ \\textbf{toward the load} "
             "(anticlockwise). Call the result the \\textbf{spacing circle}." % spname)
    o.append("  " + B + "item Any point on it is carried \\emph{onto} $g=1$ by the $%s$ of "
             "line between the two stubs --- which is exactly what stub 1 must aim for."
             % spname)
    o.append("  " + B + "item Check the forbidden region first: matching needs "
             "$g_1 " + B + "le 1/" + B + "sin^2" + B + "beta d = %.2f$, and here "
             "$g_1 = %.3f$. " % (1.0 / math.sin(2 * math.pi * sp) ** 2, y1.real) +
             B + "checkmark")
    o.append(B + "end{itemize}")
    nstep += 1

    o.append(step("Step %d --- stub 1: slide along the constant-$g$ circle" % nstep))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item A shunt stub adds susceptance only, so the point can move "
             "\\emph{only along its own $g = %.3f$ circle}." % y1.real)
    o.append("  " + B + "item Follow that circle to where it cuts the spacing circle. "
             "It cuts twice, giving the two standard solutions (one chart each "
             "below):")
    # A is the intersection nearer the rim in every problem; the labels rely on it
    assert abs(smith.p(a["ya"])) > abs(smith.p(b["ya"])), "P%d: A is not outer" % pr["n"]
    o.append("  " + B + "begin{itemize}")
    o.append("    " + B + "item \\textbf{Solution A} (outer intersection, nearer the "
             "rim): $y_a = %s$, so stub 1 must add "
             "$b_1 = %.3f - (%.3f) = %+.3f$."
             % (cx(a["ya"]), a["ya"].imag, y1.imag, a["b1"]))
    o.append("    " + B + "item \\textbf{Solution B} (inner intersection, nearer the "
             "centre): $y_a' = %s$, so $b_1' = %+.3f$."
             % (cx(b["ya"]), b["b1"]))
    o.append("  " + B + "end{itemize}")
    o.append("  " + B + "item Read $" + B + "ell_1$ off the rim, starting at the %s: "
             "$" % TERM[k] + B + "ell_1 = %s$ (A) and $%s$ (B)."
             % (lam(a["l1"]), lam(b["l1"])))
    o.append(B + "end{itemize}")
    nstep += 1

    o.append(step("Step %d --- the $%s$ of line between the stubs" % (nstep, spname)))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item Swing a \\emph{new} SWR circle through $y_a$ and rotate "
             "\\textbf{clockwise} by $%s$." % spname)
    o.append("  " + B + "item By construction it lands on the $g=1$ circle: "
             "$y_2 = %s$ (A), $y_2' = %s$ (B)." % (cx(a["y2"]), cx(b["y2"])))
    o.append(B + "end{itemize}")
    nstep += 1

    o.append(step("Step %d --- stub 2 cancels what is left" % nstep))
    o.append(B + "begin{itemize}")
    o.append("  " + B + "item Stub 2 supplies $b_2 = %+.3f$ (A) or $%+.3f$ (B), leaving "
             "$y_{in} = 1 + j0$, i.e. $Z_{in} = Z_0 = %g" % (a["b2"], b["b2"], z0)
             + B + ",\\Omega$. Matched.")
    o.append("  " + B + "item Off the rim from the %s: $" % TERM[k] + B +
             "ell_2 = %s$ (A) and $%s$ (B)." % (lam(a["l2"]), lam(b["l2"])))
    o.append(B + "end{itemize}")

    # answer table
    o.append(step("Answer"))
    o.append(B + "begin{tabularx}{" + B + "linewidth}{@{}L{3.2cm}X X@{}}")
    o.append(B + "toprule")
    o.append(B + "hrow " + B + "thead{Quantity} & " + B + "thead{Solution A} & "
             + B + "thead{Solution B} " + B + B)
    o.append(B + "midrule")
    rows = [
        ("Stub spacing $d$", "$%s$" % spname, "$%s$" % spname),
        ("First stub from load", "$%s$" % lam(d1), "$%s$" % lam(d1)),
        ("$y$ before stub 1", "$%s$" % cx(y1), "$%s$" % cx(y1)),
        ("Stub 1 susceptance $b_1$", "$%+.3f$" % a["b1"], "$%+.3f$" % b["b1"]),
        ("\\textbf{Stub 1 length $" + B + "ell_1$}", "$%s$" % lam(a["l1"]),
         "$%s$" % lam(b["l1"])),
        ("$y$ after the spacing", "$%s$" % cx(a["y2"]), "$%s$" % cx(b["y2"])),
        ("Stub 2 susceptance $b_2$", "$%+.3f$" % a["b2"], "$%+.3f$" % b["b2"]),
        ("\\textbf{Stub 2 length $" + B + "ell_2$}", "$%s$" % lam(a["l2"]),
         "$%s$" % lam(b["l2"])),
    ]
    for nm, va, vb in rows:
        o.append("%s & %s & %s " % (nm, va, vb) + B + B)
    o.append(B + "bottomrule")
    o.append(B + "end{tabularx}")
    o.append("")
    o.append(B + "lead{Both are correct.} Quote either, but say which you chose. "
             "Solution %s uses the shorter stubs here, which is the practical pick: "
             "less line at high VSWR means lower loss and wider bandwidth."
             % ("A" if (a["l1"] + a["l2"]) <= (b["l1"] + b["l2"]) else "B"))

    if pr.get("smat"):
        o += smatrix_block(pr, gl)
    if pr.get("micro"):
        o += micro_block(pr, [(B + "ell_1", a["l1"]), (B + "ell_2", a["l2"]),
                              ("d", sp)])
    if pr.get("theory"):
        o.append(B + "lead{Theory half} The comparison of matching techniques and the "
                 "advantages of double-stub over single-stub tuning are in "
                 "$" + B + "S$2.5; the design steps and the forbidden region are in "
                 "$" + B + "S$2.7. The worked example above supplies the ``+Eg'' the "
                 "paper asks for.")

    # ----------------------------------------------------------- figures
    # one chart per intersection of the g circle with the spacing circle
    figs = []
    for s, tag, pos, prime in ((a, "A", "outer", ""), (b, "B", "inner", "'")):
        # Every label goes where nothing else is: the two intersections sit on
        # different sides of the chart, so fixed offsets collide. Fixed marks
        # first (points, arc labels), then circle labels, then point labels.
        g1 = y1.real
        pts = [smith.p(v) for v in (zn, y1, s["ya"], s["y2"])]
        if d1 > 0:
            pts.append(smith.p(yn))
        busy = list(pts)
        busy.append(_walk_label(s["ya"], sp))
        if d1 > 0:
            busy.append(_walk_label(yn, d1))
        if abs(s["b1"]) > 5e-4:
            qm = smith.p(complex(g1, (y1.imag + s["ya"].imag) / 2.0))
            cg = g1 / (1 + g1)
            busy.append(cg + (qm - cg) * (1 + 0.05 * (1 + g1)))
        busy.append((abs(smith.p(s["ya"])) + 0.045) * cmath.exp(1j * math.radians(-62)))
        at = {}
        ang = 4.0 * math.pi * sp
        for name, c0, r0 in (("unit", 0.5, 0.5),
                             ("spacing", 0.5 * cmath.exp(1j * ang), 0.5),
                             ("g", g1 / (1 + g1), 1.0 / (1 + g1))):
            at[name] = _free_angle(c0.real, c0.imag, r0, busy)
            busy.append(c0 + (r0 + 0.045) * cmath.exp(1j * math.radians(at[name])))

        def lab(v):
            q = smith.p(v)
            kw = _free_offset(q, [x for x in busy if abs(x - q) > 1e-9])
            busy.append(kw.pop("centre"))
            return kw

        sc = SmithChart(size=5.2, mode="y", title=None)
        sc.unit_circle(at=at["unit"])
        sc.spacing_circle(sp, label="spacing", at=at["spacing"])
        sc.g_circle(g1, label="$g=%.2f$" % g1, at=at["g"])
        sc.swr_circle(s["ya"], label="SWR", at=-62)
        sc.pt(zn, "$z_L$", color=SUB, **lab(zn))
        if d1 > 0:
            sc.pt(yn, "$y_L$", color=SUB, ms=3.6, **lab(yn))
            sc.walk(yn, d1, color=SUB, label="$%s$" % lam(d1))
        sc.pt(y1, "$y_1$", color=MKC, **lab(y1))
        if abs(s["b1"]) > 5e-4:                  # b1 = 0: y1 already on the circle
            sc.along_g(y1, s["ya"], label="$%+.2f$" % s["b1"])
        sc.pt(s["ya"], "$y_a%s$" % prime, color=GD, **lab(s["ya"]))
        sc.walk(s["ya"], sp, color=ACC, label="$%s$" % spname)
        sc.pt(s["y2"], "$y_2%s$" % prime, color=ACC, **lab(s["y2"]))
        sc.rim_walk(s["b2"], k, label="$" + B + "ell_2$")
        sc.note("solution %s (%s intersection): $" % (tag, pos) + B +
                "ell_1 = %s$, $" % lam(s["l1"]) + B + "ell_2 = %s$, %s stubs $%s$ "
                "apart" % (lam(s["l2"]), k, spname))
        fig = "c2num_p%02d%s.png" % (pr["n"], "" if tag == "A" else "b")
        sc.save(fig)
        figs.append((fig, "solution %s, the %s intersection of the $g = %.2f$ "
                     "circle with the spacing circle" % (tag, pos, y1.real)))
    return o, figs


# -------------------------------------------------------------------- driver
EMIT = {"read": emit_read, "ss": emit_ss, "ds": emit_ds}


def main():
    out = []
    for pr in C.P:
        resolve(pr)
        body, fig = EMIT[pr["kind"]](pr)
        out.append("%" + "=" * 70)
        out.extend(body)
        out.append("")
        text = chr(10).join(body)
        if isinstance(fig, list):
            # double stub: the two intersections side by side, A (outer) left
            out.append(B + "begin{center}")
            out.append(B + "includegraphics[width=0.495" + B + "textwidth]{figs/%s}"
                       % fig[0][0] + B + "hfill")
            out.append(B + "includegraphics[width=0.495" + B + "textwidth]{figs/%s}"
                       % fig[1][0])
            out.append(B + "end{center}")
            out.append("{" + B + "footnotesize" + B + "color{sub} Problem %d --- "
                       "Smith chart construction, left: %s; right: %s.}"
                       % (pr["n"], fig[0][1], fig[1][1]))
            fig = fig[0][0] + " + " + fig[1][0]
        else:
            out.append(B + "figC{%s}{%.2f" % (fig, pr.get("figw", 0.55)) + B +
                       "textwidth}")
            out.append("{" + B + "footnotesize" + B + "color{sub} Problem %d --- "
                       "Smith chart construction. Arcs are numbered in the order of "
                       "the steps above.}" % pr["n"])
        if pr["kind"] in ("ss", "ds"):
            # physical figures; replay: every length drawn is printed above
            ln = "c2num_p%02d_line.png" % pr["n"]
            for what, tex in stubfig.line(pr, ln):
                assert tex in text, "P%d line diagram draws %s = %r, not printed" % (
                    pr["n"], what, tex)
            out.append("")
            out.append(B + "figC{%s}{0.62" % ln + B + "textwidth}")
            out.append("{" + B + "footnotesize" + B + "color{sub} Problem %d --- "
                       "line diagram of the matched network: shunt stub%s across the "
                       "line, lengths from the answer above.}"
                       % (pr["n"], "s" if pr["kind"] == "ds" else ""))
        if pr["kind"] in ("ss", "ds") and not pr.get("micro"):
            cf = "c2num_p%02d_coax.png" % pr["n"]
            for what, tex in stubfig.coax(pr, cf):
                assert tex in text, "P%d coax section draws %s = %r, not printed" % (
                    pr["n"], what, tex)
            # print at natural size (7.13 in text width), so every section's
            # labels come out the same size however long the board is
            wpx = Image.open(os.path.join(HERE, "figs", cf)).size[0]
            ends = {"short": "a shorting plate closes each stub",
                    "open": "each stub's centre conductor stops short of an open "
                            "end",
                    "both": "shorted stub closed by a plate, open stub left open"}
            out.append("")
            out.append(B + "figC{%s}{%.2f" % (cf, min(0.92, wpx / 210.0 / 7.13))
                       + B + "textwidth}")
            out.append("{" + B + "footnotesize" + B + "color{sub} Problem %d --- "
                       "coaxial realisation, longitudinal section: each stub a coax "
                       "tee off the main line; %s.}" % (pr["n"], ends[pr["stub"]]))
        if pr.get("micro"):
            # replay: every value the layout draws must be printed in this problem
            ms = "c2num_p%02d_ms.png" % pr["n"]
            for what, tex in msfig.layout(pr, ms):
                assert tex in text, "P%d layout draws %s = %r, not printed" % (
                    pr["n"], what, tex)
            out.append("")
            out.append(B + "figC{%s}{%.2f" % (ms, 0.92 if pr["stub"] == "both" else 0.62)
                       + B + "textwidth}")
            out.append("{" + B + "footnotesize" + B + "color{sub} Problem %d --- "
                       "microstrip layout, top view: stubs as T-junctions off the "
                       "main line, dimensions from the answer above.}" % pr["n"])
        out.append("")
        out.append(B + "penalty0" + B + "vspace{2pt}")
        out.append("")
        print("  P%-3d %-5s %s" % (pr["n"], pr["kind"], fig))
    path = os.path.join(HERE, "ch2-num-body.tex")
    io.open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", path, "(%d lines)" % len(out))


if __name__ == "__main__":
    main()
