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
             "It cuts twice, giving the two standard solutions:")
    o.append("  " + B + "begin{itemize}")
    o.append("    " + B + "item \\textbf{Solution A}: $y_a = %s$, so stub 1 must add "
             "$b_1 = %.3f - (%.3f) = %+.3f$."
             % (cx(a["ya"]), a["ya"].imag, y1.imag, a["b1"]))
    o.append("    " + B + "item \\textbf{Solution B}: $y_a' = %s$, so $b_1' = %+.3f$."
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

    # ------------------------------------------------------------ figure
    sc = SmithChart(size=5.2, mode="y", title=None)
    sc.unit_circle(at=118)
    sc.spacing_circle(sp, label="spacing", at=118)
    sc.g_circle(y1.real, label="$g=%.2f$" % y1.real, at=200)
    sc.swr_circle(a["ya"], label="SWR", at=-62)
    sc.pt(zn, "$z_L$", color=SUB, dx=-0.05, dy=-0.05, ha="right", va="top")
    if d1 > 0:
        sc.pt(yn, "$y_L$", color=SUB, dx=-0.05, ha="right", ms=3.6)
        sc.walk(yn, d1, color=SUB, label="$%s$" % lam(d1))
    sc.pt(y1, "$y_1$", color=MKC, dx=-0.05, ha="right")
    sc.along_g(y1, a["ya"], label="$%+.2f$" % a["b1"])
    sc.pt(a["ya"], "$y_a$", color=GD)
    sc.walk(a["ya"], sp, color=ACC, label="$%s$" % spname)
    sc.pt(a["y2"], "$y_2$", color=ACC, dy=-0.06, va="top")
    sc.rim_walk(a["b2"], k, label="$" + B + "ell_2$")
    sc.note("solution A: $" + B + "ell_1 = %s$, $" % lam(a["l1"]) + B +
            "ell_2 = %s$, %s stubs $%s$ apart" % (lam(a["l2"]), k, spname))
    fig = "c2num_p%02d.png" % pr["n"]
    sc.save(fig)
    return o, fig


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
        out.append(B + "figC{%s}{%.2f" % (fig, pr.get("figw", 0.55)) + B + "textwidth}")
        out.append("{" + B + "footnotesize" + B + "color{sub} Problem %d --- "
                   "Smith chart construction. Arcs are numbered in the order of the "
                   "steps above.}" % pr["n"])
        if pr.get("micro"):
            # replay: every value the layout draws must be printed in this problem
            ms = "c2num_p%02d_ms.png" % pr["n"]
            text = chr(10).join(body)
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
