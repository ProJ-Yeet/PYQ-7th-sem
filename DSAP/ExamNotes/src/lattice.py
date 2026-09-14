# -*- coding: utf-8 -*-
r"""Lattice and lattice-ladder structures, solved exactly, for DSAP chapter 4.

    python lattice.py              # self-test, then every PYQ system
    python lattice.py --papers     # just the paper table

42 of the 68 questions in chapter 4 are this one calculation, so it is worth a
solver rather than 42 hand derivations. Everything is exact rational arithmetic
(Fraction): the step-down recursion divides by 1 - k^2, and a decimal answer
drifts visibly by the third stage.

THE TWO RECURSIONS

Direct form to lattice, the "step-down". Given
    A_m(z) = 1 + a_m(1) z^-1 + ... + a_m(m) z^-m
the last coefficient is the reflection coefficient, and the rest come from
folding the polynomial against its own reverse:

    k_m = a_m(m)
    a_{m-1}(i) = [ a_m(i) - k_m a_m(m-i) ] / (1 - k_m^2),   i = 1 .. m-1

Run it from m = N down to m = 1 and read off k_N, ..., k_1.

Lattice to direct form, the "step-up", is the same relation rearranged:

    a_m(i) = a_{m-1}(i) + k_m a_{m-1}(m-i),   a_m(m) = k_m

LADDER COEFFICIENTS, for a pole-zero H(z) = B(z)/A(z)

    C_m = b_m - sum_{i=m+1}^{M} C_i a_i(i-m),   m = M, M-1, ..., 0

where a_i(.) are the coefficients of the i-th order polynomial the step-down
produced on its way past. For an all-pole system B(z) = b_0, so C_0 = b_0 and
every other C is zero.

STABILITY.  |k_m| < 1 for every m. That is the Schur-Cohn test in disguise: a
step-down producing |k| >= 1 means a root on or outside the unit circle. The
recursion divides by 1 - k_m^2, so |k_m| = 1 exactly does not merely signal
instability, it breaks the conversion; the code reports that rather than
dividing by zero.
"""
import sys
from fractions import Fraction as F

FAIL = []
OK = [0]


def chk(tag, got, want):
    same = (list(got) == list(want)) if isinstance(want, (list, tuple)) \
        else (got == want)
    if same:
        OK[0] += 1
    else:
        FAIL.append("%s\n     got  %s\n     want %s" % (tag, got, want))


def fr(x):
    """Anything the papers print -> an exact Fraction."""
    if isinstance(x, F):
        return x
    if isinstance(x, tuple):            # (num, den)
        return F(x[0], x[1])
    if isinstance(x, int):
        return F(x)
    return F(str(x))                    # a float literal, read as written


class Unstable(Exception):
    pass


def stepdown(a):
    """a = [1, a(1), ..., a(N)] -> (ks, levels).

    ks[m-1] is k_m. levels[m] is the coefficient list of A_m(z), so levels[N]
    is the input and levels[0] is [1]. The ladder recursion needs the levels,
    which is why they come back too."""
    a = [fr(x) for x in a]
    assert a[0] == 1, "A(z) must be monic in z^0"
    N = len(a) - 1
    levels = [None] * (N + 1)
    levels[N] = a[:]
    ks = [None] * N
    cur = a[:]
    for m in range(N, 0, -1):
        km = cur[m]
        ks[m - 1] = km
        if abs(km) == 1:
            raise Unstable("|k_%d| = 1 exactly, the step-down divides by zero" % m)
        if m == 1:
            levels[0] = [F(1)]
            break
        d = 1 - km * km
        nxt = [F(1)] + [(cur[i] - km * cur[m - i]) / d for i in range(1, m)]
        levels[m - 1] = nxt
        cur = nxt
    return ks, levels


def stepup(ks):
    """[k_1 .. k_N] -> [1, a(1), ..., a(N)]."""
    ks = [fr(k) for k in ks]
    cur = [F(1)]
    for m in range(1, len(ks) + 1):
        km = ks[m - 1]
        nxt = [F(1)] + [cur[i] + km * cur[m - i] for i in range(1, m)] + [km]
        cur = nxt
    return cur


def ladder(b, a):
    """b = [b_0 .. b_M], a = [1, a(1) .. a(N)] -> (ks, Cs).

    Cs[m] is C_m, lowest index first. Requires M <= N."""
    b = [fr(x) for x in b]
    ks, levels = stepdown(a)
    M = len(b) - 1
    assert M <= len(a) - 1, "numerator degree exceeds denominator degree"
    C = [F(0)] * (M + 1)
    for m in range(M, -1, -1):
        s = F(0)
        for i in range(m + 1, M + 1):
            s += C[i] * levels[i][i - m]
        C[m] = b[m] - s
    return ks, C


def stable(ks):
    return all(abs(k) < 1 for k in ks)


def show(x):
    """A decimal always, with the exact fraction beside it when that fraction is
    small enough to be worth quoting. Exam answers get written in decimals, but
    the clean ones (1/4, 1/2, 1/3) are far easier to recognise as fractions, and
    a mixed rendering makes the table impossible to scan."""
    if x.denominator == 1:
        return str(x.numerator)
    d = "%.4f" % float(x)
    if x.denominator <= 200:
        return "%s=%d/%d" % (d, x.numerator, x.denominator)
    return d


def line(ks, Cs=None):
    out = "k = [" + ", ".join(show(k) for k in ks) + "]"
    if Cs is not None:
        out += "   C = [" + ", ".join(show(c) for c in Cs) + "]"
    out += "   " + ("STABLE" if stable(ks) else "UNSTABLE")
    return out


# --------------------------------------------------------------- self-tests

def selftest():
    # 1. step-up inverts step-down, on every all-pole system the papers ask
    for a in ([1, "-0.2", "0.4", "0.6"],
              [1, "-0.525", "0.6125", "0.3"],
              [1, "-0.9", "0.64", "-0.576"],
              [1, "-0.3", "0.5", "0.25"],
              [1, 2, -3, 4],
              [1, "-0.01", "-0.23", "0.5"]):
        ks, _ = stepdown(a)
        chk("round trip %s" % (a,), stepup(ks), [fr(x) for x in a])

    # 2. the textbook example every source uses: k = [1/4, 1/2, 1/3]
    #    must give A_3(z) = 1 + 13/24 z^-1 + 5/8 z^-2 + 1/3 z^-3
    chk("k=[1/4,1/2,1/3] -> A_3",
        stepup([F(1, 4), F(1, 2), F(1, 3)]),
        [F(1), F(13, 24), F(5, 8), F(1, 3)])

    # and back again, which is 81 Ba / 78 Bh
    ks, _ = stepdown([1, F(13, 24), F(5, 8), F(1, 3)])
    chk("A_3 -> k", ks, [F(1, 4), F(1, 2), F(1, 3)])

    # 3. the second textbook set, 80 Ch / 74 Ma
    # by hand: A_1 = [1, 1/4]; a_2(1) = 1/4 + (1/4)(1/4) = 5/16, a_2(2) = 1/4;
    # a_3(1) = 5/16 + (1/3)(1/4) = 19/48, a_3(2) = 1/4 + (1/3)(5/16) = 17/48
    chk("k=[1/4,1/4,1/3] -> A_3",
        stepup([F(1, 4), F(1, 4), F(1, 3)]),
        [F(1), F(19, 48), F(17, 48), F(1, 3)])

    # 4. an all-pole ladder has a single non-zero C, equal to b_0
    ks, C = ladder([2], [1, "-0.3", "0.25"])
    chk("all-pole ladder C", C, [F(2)])

    # 5. a pure FIR lattice: A(z) = B(z), so the ladder is trivial and the
    #    reflection coefficients are the FIR lattice coefficients
    ks, _ = stepdown([1, 2, -3, 4])
    chk("FIR k_3 is the last coefficient", ks[2], F(4))

    # 6. THE THEOREM behind five of the papers. A monic symmetric polynomial has
    #    a(N) = a(0) = 1, so k_N = 1 and the step-down divides by zero: a
    #    linear-phase FIR filter has NO lattice realisation. Symmetry is exactly
    #    the linear-phase condition h[n] = h[N-n] from chapter 3.
    for a in ([1, 2, 1],
              [1, 2, 2, 1],
              [1, F(2, 3), F(5, 8), F(2, 3), 1],
              [1, F(1, 3), F(9, 8), F(1, 3), 1]):
        chk("symmetric %s is symmetric" % (a,), a, list(reversed(a)))
        try:
            stepdown(a)
            FAIL.append("symmetric %s should have failed the step-down" % (a,))
        except Unstable:
            OK[0] += 1

    # and the converse check: breaking the symmetry makes it convertible again
    ks, _ = stepdown([1, 2, F(1, 2)])
    chk("break the symmetry and it converts", len(ks), 2)

    # 7. an all-pass H(z) = z^-N A(1/z) / A(z) puts every ladder coefficient at
    #    zero except the last, which is 1: the output is the lattice's BACKWARD
    #    path. This is 70 Bh, and it is the tidiest result in the chapter.
    a = [F(1), F(-3, 5), F(1, 5), F(1, 2)]
    ks, C = ladder(list(reversed(a)), a)
    chk("all-pass ladder is [0,...,0,1]", C, [F(0), F(0), F(0), F(1)])

    print("%d self-tests passed" % OK[0])
    if FAIL:
        for f in FAIL:
            print("  FAIL " + f)
        sys.exit(1)


# ------------------------------------------------------------ the PYQ systems

ALLPOLE = [
    ("80 Bh",        [1, "-0.2", "0.4", "0.6"]),
    ("81 Ch, 72 Ash", [1, "-0.525", "0.6125", "0.3"]),
    ("79 Ch, 69 Bh", [1, "-0.9", "0.64", "-0.576"]),
    ("71 Bh",        [1, "-0.3", "0.5", "0.25"]),
    ("70 Ma",        [1, 2, -3, 4]),
    ("71 Ch",        [1, "-0.01", "-0.23", "0.5"]),
    ("75 Ch",        [1, F(2, 3), F(5, 8), F(2, 3), 1]),
]

FIR = [
    ("81 Ba, 78 Bh", [1, F(13, 24), F(5, 8), F(1, 3)]),
    ("72 Ch",        [1, 2, 1]),
    ("73 Bh",        [1, 2, 2, 1]),
    ("74 Ch",        [1, F(52, 96), F(25, 40), F(1, 3)]),
    ("74 Ash",       [1, "0.7", "1.2", -1]),
    ("73 Shr",       [2, "1.8", "-1.6", 1]),
    ("76 Bh",        [1, 2, "0.62", "0.8"]),
    ("72 Ka, 69 Ch", [1, 2, -3, 4]),
    ("70 Ch",        [1, "3.1", "5.5", "4.2", "2.3"]),
]

LADDER = [
    ("80 Ba, 82 Bh", [2, "-0.7", "0.5"], [1, "-0.3", "0.25"]),
    ("82 Ba", ["0.2759", "0.5121", "0.5121", "0.2759"],
     [1, "-0.0010", "0.6546", "-0.0775"]),
    ("79 Ba", [1, "-0.4", "0.25"], [1, "-0.3", "0.5"]),
    ("76 Ch", ["0.5", -2, 3], [1, "-0.5", "-0.7", "0.3"]),
    ("76 Ash", ["0.7", "-1.5", "0.5"], [1, "-0.5", "-0.7", "0.3"]),
    ("74 Bh", ["0.62", "0.42", "-0.25"], [1, "0.27", "0.06", "-0.75"]),
    ("75 Bh", ["0.6", "-0.45", "-0.25"], [1, "0.27", "0.06", "-0.75"]),
    ("77 Ch", ["0.5", "-0.4", "-0.2"], [1, "0.2", "0.7", "-0.75"]),
    ("73 Ma", ["0.5", "0.65", "0.2"], [1, "-0.45", "0.3", "0.5"]),
    ("78 Ch", [1, -1, "0.5"], [1, "0.2", "-0.15"]),
    ("70 Asa", ["0.5", 2, "0.6"], [1, "-0.3", "0.4"]),
    ("66 Ma", [F(1, 2), F(1, 3), F(1, 4), F(1, 5)],
     [1, F(1, 5), F(2, 5), F(3, 5)]),
    ("73 Ch", [1, F(1, 3), F(9, 8), F(4, 3), 1],
     [1, F(2, 3), F(5, 8), F(2, 3), 1]),
    ("70 Bh allpass", [1, "0.4", "-1.2", 2], [2, "-1.2", "0.4", 1]),
]


def run_papers():
    print("")
    print("=" * 78)
    print("ALL-POLE  H(z) = 1 / A(z)")
    print("=" * 78)
    for tag, a in ALLPOLE:
        try:
            ks, _ = stepdown(a)
            print("%-16s %s" % (tag, line(ks)))
        except Unstable as e:
            print("%-16s CANNOT CONVERT: %s" % (tag, e))

    print("")
    print("=" * 78)
    print("FIR  H(z) = B(z), lattice coefficients are the reflection coefficients")
    print("=" * 78)
    for tag, b in FIR:
        scale = fr(b[0])
        norm = [fr(x) / scale for x in b]
        try:
            ks, _ = stepdown(norm)
            extra = "" if scale == 1 else "   (leading %s factored out)" % show(scale)
            print("%-16s %s%s" % (tag, line(ks), extra))
        except Unstable as e:
            print("%-16s CANNOT CONVERT: %s" % (tag, e))

    print("")
    print("=" * 78)
    print("LATTICE-LADDER  H(z) = B(z) / A(z)")
    print("=" * 78)
    for tag, b, a in LADDER:
        scale = fr(a[0])
        an = [fr(x) / scale for x in a]
        bn = [fr(x) / scale for x in b]
        try:
            ks, C = ladder(bn, an)
            note = "" if scale == 1 else "   (A normalised by %s)" % show(scale)
            print("%-16s %s%s" % (tag, line(ks, C), note))
        except Unstable as e:
            print("%-16s CANNOT CONVERT: %s" % (tag, e))


def main():
    if "--papers" not in sys.argv:
        selftest()
    run_papers()


if __name__ == "__main__":
    main()
