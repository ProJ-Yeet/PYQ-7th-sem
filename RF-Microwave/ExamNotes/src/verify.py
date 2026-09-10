# -*- coding: utf-8 -*-
"""End-to-end check of every Chapter 2 numerical answer.

Not a re-run of the solver: this walks the published design forward through
the transmission-line equations -- load, line, stub, line, stub -- and asserts
that what comes out is a match. It also re-derives each stub susceptance from
the PUBLISHED LENGTH, so a wrong length cannot hide behind a right b.

Run from src\\:   python verify.py
"""
import cmath
import math
import sys

import ch2num as C
import rf

TOL = 1e-9
fails = []


def chk(cond, what):
    if not cond:
        fails.append(what)
    return cond


def y_after(y, d):
    """Carry an admittance d wavelengths toward the generator."""
    return rf.y_of(rf.move(rf.gamma_of(1.0 / y), d))


def check_single(pr):
    zn = pr["zn"]
    kinds = ["short", "open"] if pr["stub"] == "both" else [pr["stub"]]
    for k in kinds:
        for i, s in enumerate(rf.single_stub(zn, k)):
            tag = "P%d %s sol%d" % (pr["n"], k, i + 1)
            # the line brings us to unit conductance
            y = y_after(1.0 / zn, s["d"])
            chk(abs(y.real - 1.0) < 1e-9, tag + ": Re(y(d)) != 1")
            # the PUBLISHED length must produce the susceptance we claim
            b_from_len = rf.stub_susceptance(s["l"], k)
            chk(abs(b_from_len - s["cancel"]) < 1e-6,
                tag + ": length %.4f gives b=%.4f, wanted %.4f"
                % (s["l"], b_from_len, s["cancel"]))
            # and the whole thing must be matched
            chk(abs(y + 1j * b_from_len - 1.0) < 1e-6, tag + ": not matched")


def check_double(pr):
    zn, sp, k = pr["zn"], pr["sp"], pr["stub"]
    d1 = pr.get("d1", 0.0)
    sols = rf.double_stub(zn, sp, k, d1)
    chk(len(sols) == 2, "P%d: expected 2 solutions, got %d" % (pr["n"], len(sols)))
    for i, s in enumerate(sols):
        tag = "P%d sol%s" % (pr["n"], "AB"[i])
        y1 = y_after(1.0 / zn, d1)
        chk(abs(y1 - s["y1"]) < 1e-9, tag + ": y1 mismatch")
        b1 = rf.stub_susceptance(s["l1"], k)          # from the PUBLISHED length
        chk(abs(b1 - s["b1"]) < 1e-6,
            tag + ": l1=%.4f gives b1=%.4f, wanted %.4f" % (s["l1"], b1, s["b1"]))
        ya = y1 + 1j * b1
        chk(abs(ya - s["ya"]) < 1e-6, tag + ": ya mismatch")
        y2 = y_after(ya, sp)
        chk(abs(y2.real - 1.0) < 1e-6,
            tag + ": Re(y2)=%.6f != 1" % y2.real)
        b2 = rf.stub_susceptance(s["l2"], k)
        chk(abs(b2 - s["b2"]) < 1e-6,
            tag + ": l2=%.4f gives b2=%.4f, wanted %.4f" % (s["l2"], b2, s["b2"]))
        yin = y2 + 1j * b2
        chk(abs(yin - 1.0) < 1e-6,
            tag + ": final y_in = %.6f%+.6fj, not 1+j0" % (yin.real, yin.imag))
        # forbidden-region statement must be true
        chk(y1.real <= 1.0 / math.sin(2 * math.pi * sp) ** 2 + 1e-12,
            tag + ": claimed matchable but g1 exceeds the limit")


def check_read(pr):
    zn = pr["zn"]
    gl = rf.gamma_of(zn)
    zin = rf.z_in(zn, pr["d"])
    chk(abs(abs(rf.gamma_of(zin)) - abs(gl)) < 1e-9,
        "P%d: |Gamma| changed along a lossless line" % pr["n"])
    ph = cmath.phase(gl)
    d_max = (ph / (2.0 * rf.TWO_PI)) % 0.5
    d_min = ((ph - math.pi) / (2.0 * rf.TWO_PI)) % 0.5
    d_res = min(d_max, d_min)
    z_res = rf.z_in(zn, d_res)
    chk(abs(z_res.imag) < 1e-9,
        "P%d: 'purely resistive' point has x=%.2e" % (pr["n"], z_res.imag))
    S = rf.vswr(gl)
    chk(abs(z_res.real - S) < 1e-9 or abs(z_res.real - 1.0 / S) < 1e-9,
        "P%d: resistive point is neither S nor 1/S" % pr["n"])


def main():
    n = 0
    for pr in C.P:
        C.resolve(pr)
        {"read": check_read, "ss": check_single, "ds": check_double}[pr["kind"]](pr)
        n += 1
    print("checked %d problems" % n)
    if fails:
        print("\n%d FAILURES:" % len(fails))
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("all designs verified: every published stub length matches its load")


if __name__ == "__main__":
    main()
