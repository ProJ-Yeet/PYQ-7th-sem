# -*- coding: utf-8 -*-
r"""Number representation, quantization error and limit cycles, for DSAP ch 4.

    python quant.py

Small, but the three questions it answers are each worth marks and each easy to
get subtly wrong by hand: the fixed-point codes for a fraction, the width of the
dead band, and whether a given recursive filter actually enters a limit cycle.

FIXED POINT, b bits after the binary point, value in [-1, 1).

  sign magnitude   sign bit, then the magnitude of the fraction unchanged
  1's complement   negative -> invert every magnitude bit
  2's complement   negative -> invert every bit and add 1 in the last place

QUANTIZATION ERROR, e = Q(x) - x, with step q = 2^-b.

  rounding                 -q/2 <= e <= q/2, for every representation
  truncation, sign mag.    -(q - q_u) <= e <= (q - q_u), symmetric, because
                           truncating a magnitude always shrinks |x|
  truncation, 2's comp.    -(q - q_u) <= e <= 0, one-sided, because truncating
                           a 2's complement code always moves the value DOWN

That asymmetry is what 67 Mng asks to be shown by example, and it is the whole
reason 2's complement truncation biases a filter while sign-magnitude does not.

LIMIT CYCLE. A recursive filter whose products are quantized can sit in a
self-sustaining oscillation after the input stops. For y(n) = Q{a y(n-1)} + x(n)
the dead band is the set of |y| for which Q{a y} = +-y, so the filter cannot
decay any further: |y| <= q / (2 (1 - |a|)) for rounding.
"""
import sys
from fractions import Fraction as F

FAIL = []
OK = [0]


def chk(tag, got, want):
    if got == want:
        OK[0] += 1
    else:
        FAIL.append("%s\n     got  %s\n     want %s" % (tag, got, want))


def codes(x, b):
    """(sign magnitude, 1's complement, 2's complement) of the fraction x, with
    b bits after the binary point. Returns strings with the point shown."""
    x = F(x)
    neg = x < 0
    mag = abs(x)
    scaled = mag * (1 << b)
    assert scaled == int(scaled), "%s is not exact in %d bits" % (x, b)
    n = int(scaled)
    bits = bin(n)[2:].rjust(b, "0")
    assert len(bits) <= b, "%s overflows %d bits" % (x, b)
    sm = ("1" if neg else "0") + "." + bits
    if not neg:
        return sm, sm, sm
    inv = "".join("1" if c == "0" else "0" for c in bits)
    ones = "1." + inv
    two = (1 << b) - n
    twos = "1." + bin(two)[2:].rjust(b, "0")
    return sm, ones, twos


def q_round(x, b):
    """Round to b bits after the point, ties away from zero, which is what the
    textbook worked examples use."""
    x = F(x)
    s = x * (1 << b)
    fl = s.numerator // s.denominator
    rem = s - fl
    if rem > F(1, 2) or (rem == F(1, 2) and x > 0):
        fl += 1
    elif rem == F(1, 2) and x < 0:
        pass
    return F(fl, 1 << b)


def limit_cycle(a, x0, b, n=14):
    """y(n) = Q{a y(n-1)} + x(n), x = x0 delta(n), y(-1) = 0."""
    y = F(0)
    out = []
    for k in range(n):
        drive = F(x0) if k == 0 else F(0)
        y = q_round(F(a) * y, b) + drive
        out.append(y)
    return out


def main():
    # ---- 75 Ash: 5/8 and -5/8, sign magnitude, 1's and 2's complement
    for val, want in ((F(5, 8), ("0.101", "0.101", "0.101")),
                      (F(-5, 8), ("1.101", "1.010", "1.011"))):
        got = codes(val, 3)
        chk("75 Ash %s in 3 bits" % val, got, want)
        print("%-8s  sign-mag %s   1's %s   2's %s" % ((str(val),) + got))
    print("")

    # ---- 69 Bh: -192/220 in 8 bit. It is not a dyadic fraction, so it cannot
    # be represented exactly; the question needs it rounded first.
    v = F(-192, 220)
    print("69 Bh: -192/220 = %.6f, which is NOT exact in binary" % float(v))
    for b in (8,):
        q = q_round(v, b)
        print("   rounded to %d bits: %s = %.6f" % (b, q, float(q)))
        sm, o, t = codes(q, b)
        print("   sign-magnitude %s" % sm)
        print("   1's complement %s" % o)
        print("   2's complement %s" % t)
    # the likely intended value: -0.75 = -192/256
    print("   NOTE 192/256 = 0.75 exactly, and 256 is the natural 8 bit scale.")
    alt = F(-192, 256)
    sm, o, t = codes(alt, 8)
    print("   if the paper meant -192/256 = -0.75:  sm %s   1's %s   2's %s"
          % (sm, o, t))
    chk("-192/256 two's complement", t, "1.01000000")
    print("")

    # ---- 66 Ma: does the filter enter a limit cycle, and with what period?
    print("66 Ma: y(n) = Q{-0.5 y(n-1)} + 0.875 delta(n), 3 bit rounding")
    ys = limit_cycle(F(-1, 2), F(7, 8), 3, 12)
    print("   n   y(n)")
    for n, y in enumerate(ys):
        print("   %-3d %-8s = %+.4f" % (n, y, float(y)))
    tail = ys[4:]
    period = None
    for p in (1, 2, 3, 4):
        if all(tail[i] == tail[i + p] for i in range(len(tail) - p)):
            period = p
            break
    print("   steady oscillation between %s and %s, PERIOD %s"
          % (tail[0], tail[1], period))
    chk("66 Ma enters a limit cycle", period, 2)
    chk("66 Ma amplitude", abs(tail[0]), F(1, 8))

    # dead band for rounding: |y| <= q / (2(1-|a|))
    q = F(1, 8)
    dead = q / (2 * (1 - F(1, 2)))
    print("   dead band |y| <= q/(2(1-|a|)) = %s = %.4f" % (dead, float(dead)))
    chk("66 Ma dead band", dead, F(1, 8))
    print("")

    # ---- 67 Mng: the two truncation error ranges, shown by example
    print("67 Mng: truncation error ranges, b = 3 from b_u = 6")
    bu, b = 6, 3
    worst_sm = worst_2c_lo = F(0)
    best_2c = F(0)
    for num in range(-(1 << bu) + 1, (1 << bu)):
        x = F(num, 1 << bu)
        # truncate towards zero for sign magnitude, towards -inf for 2's comp
        mag = abs(x) * (1 << b)
        tsm = F(int(mag), 1 << b) * (1 if x >= 0 else -1)
        e_sm = tsm - x
        s = x * (1 << b)
        t2c = F(s.numerator // s.denominator, 1 << b)
        e_2c = t2c - x
        worst_sm = max(worst_sm, abs(e_sm))
        worst_2c_lo = min(worst_2c_lo, e_2c)
        best_2c = max(best_2c, e_2c)
    bound = F(1, 1 << b) - F(1, 1 << bu)
    print("   |e| for sign magnitude reaches %s, bound %s" % (worst_sm, bound))
    print("   e for 2's complement runs %s to %s, bound -%s to 0"
          % (worst_2c_lo, best_2c, bound))
    chk("sign magnitude truncation is symmetric, |e| <= q - q_u",
        worst_sm, bound)
    chk("2's complement truncation is one sided, e <= 0", best_2c, F(0))
    chk("2's complement truncation reaches -(q - q_u)", worst_2c_lo, -bound)

    print("")
    print("%d checks passed" % OK[0])
    if FAIL:
        print("%d FAILED:" % len(FAIL))
        for f in FAIL:
            print("  " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
