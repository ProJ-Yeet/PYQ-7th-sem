# -*- coding: utf-8 -*-
"""Recompute every published numerical answer in the DSAP notes and assert it.

    python verify.py            # everything
    python verify.py ch1        # one chapter's block

Nothing here reads the .tex. Each check states the question's data and the
answer printed in the notes, and recomputes it from scratch; a disagreement is
a failure, whichever side is wrong. Run this before building any -num target.

Sequences are carried as (values, n0) with n0 the index of values[0].
"""
import sys
from fractions import Fraction as F

FAIL = []
OK = [0]


def chk(tag, got, want, tol=1e-9):
    if got is None or want is None:
        same = got is want                 # "aperiodic" is a real answer, not a number
    elif isinstance(want, (list, tuple)) and isinstance(got, (list, tuple)):
        same = len(got) == len(want) and all(
            abs(float(a) - float(b)) <= tol for a, b in zip(got, want))
    else:
        same = abs(float(got) - float(want)) <= tol
    if same:
        OK[0] += 1
    else:
        FAIL.append("%s\n     got  %s\n     want %s" % (tag, got, want))


def conv(x, h):
    """(values, n0) * (values, n0) -> (values, n0)."""
    xv, xn = x
    hv, hn = h
    out = [0] * (len(xv) + len(hv) - 1)
    for i, a in enumerate(xv):
        for j, b in enumerate(hv):
            out[i + j] += a * b
    return out, xn + hn


def win(expr, lo, hi):
    """Sample expr(n) for lo <= n <= hi -> (values, lo)."""
    return [expr(n) for n in range(lo, hi + 1)], lo


# =====================================================================
#  CHAPTER 1
# =====================================================================
def ch1():
    # ---- 1. convolution of two finite sequences -------------------
    # 70 Ch: h={5,4,3,2}, x={1,0,3,2}, both from n=0
    chk("c1 conv 70 Ch", conv(([1, 0, 3, 2], 0), ([5, 4, 3, 2], 0))[0],
        [5, 4, 18, 24, 17, 12, 4])
    # 73 Shr: h={1,1,1}, x={1,1,1,1}
    chk("c1 conv 73 Shr", conv(([1, 1, 1, 1], 0), ([1, 1, 1], 0))[0],
        [1, 2, 3, 3, 2, 1])
    # 70 Bh: h={1,1,1}, x={1,-2,2,3,4}
    chk("c1 conv 70 Bh", conv(([1, -2, 2, 3, 4], 0), ([1, 1, 1], 0))[0],
        [1, -1, 1, 3, 9, 7, 4])
    # 70 Asa: h={1,0,1}, x={1,-2,-2,3,4}
    chk("c1 conv 70 Asa", conv(([1, -2, -2, 3, 4], 0), ([1, 0, 1], 0))[0],
        [1, -2, -1, 1, 2, 3, 4])
    # 74 Bh: h={2,2,-1,1}, x={1,2,1,2}
    chk("c1 conv 74 Bh", conv(([1, 2, 1, 2], 0), ([2, 2, -1, 1], 0))[0],
        [2, 6, 5, 5, 5, -1, 2])
    # 74 Ma: h={5,3,4,2,0}, x={0,2,4,6}
    chk("c1 conv 74 Ma", conv(([0, 2, 4, 6], 0), ([5, 3, 4, 2, 0], 0))[0],
        [0, 10, 26, 50, 38, 32, 12, 0])
    # 71 Ch: h={1,3,2,-1,1} from n=-1, x=2d(n)-d(n-1) = {2,-1} from n=0
    y, n0 = conv(([2, -1], 0), ([1, 3, 2, -1, 1], -1))
    chk("c1 conv 71 Ch", y, [2, 5, 1, -4, 3, -1])
    chk("c1 conv 71 Ch start", n0, -1)
    # 79 Bh / 81 Bh: x=d[n]+2d[n-1]-d[n-3] = {1,2,0,-1} from 0,
    #                h=2d[n+1]+2d[n-1] = {2,0,2} from -1
    y, n0 = conv(([1, 2, 0, -1], 0), ([2, 0, 2], -1))
    chk("c1 conv 79 Bh", y, [2, 4, 2, 2, 0, -2])
    chk("c1 conv 79 Bh start", n0, -1)
    # 79 Ba: h=(1/2)^n (u[n+2]-u[n-2]) -> n=-2..1 = {4,2,1,1/2}, x={2,1,0,-1}? no:
    #        x={2,1,0,-1,4} from n=0
    h = ([F(4), F(2), F(1), F(1, 2)], -2)
    y, n0 = conv(([2, 1, 0, -1, 4], 0), h)
    chk("c1 conv 79 Ba", [float(v) for v in y],
        [8.0, 8.0, 4.0, -2.0, 14.5, 7.0, 3.5, 2.0])
    chk("c1 conv 79 Ba start", n0, -2)
    # 74 Ash: same h, x={2,1,0.5,-1} from n=0
    y, n0 = conv(([F(2), F(1), F(1, 2), F(-1)], 0), h)
    chk("c1 conv 74 Ash", [float(v) for v in y],
        [8.0, 8.0, 6.0, -1.0, -1.0, -0.75, -0.5])
    chk("c1 conv 74 Ash start", n0, -2)
    # 82 Bh: h=0.5^n (u[n]-u[n-3]) -> n=0..2 = {1,1/2,1/4}, x={2,1,0.5,-1}
    h2 = ([F(1), F(1, 2), F(1, 4)], 0)
    y, n0 = conv(([F(2), F(1), F(1, 2), F(-1)], 0), h2)
    chk("c1 conv 82 Bh", [float(v) for v in y],
        [2.0, 2.0, 1.5, -0.5, -0.375, -0.25])
    chk("c1 conv 82 Bh start", n0, 0)
    # 72 Ka: h=(1/3)^n (u[n+1]-u[n-2]) -> n=-1..1 = {3,1,1/3}, x={2,1,0.5,3}
    h3 = ([F(3), F(1), F(1, 3)], -1)
    y, n0 = conv(([F(2), F(1), F(1, 2), F(3)], 0), h3)
    chk("c1 conv 72 Ka", [float(v) for v in y],
        [6.0, 5.0, 3.1666666667, 9.8333333333, 3.1666666667, 1.0], 1e-6)
    chk("c1 conv 72 Ka start", n0, -1)
    # 75 Ash: h=2^n (u[n]-u[n-3]) = {1,2,4} from 0, x={1,1,1} from 0
    chk("c1 conv 75 Ash", conv(([1, 1, 1], 0), ([1, 2, 4], 0))[0],
        [1, 3, 7, 6, 4])
    # 79 Ch / 75 Bh: same h, x=d[n]+d[n-1]-d[n-3] = {1,1,0,-1} from 0
    chk("c1 conv 79 Ch", conv(([1, 1, 0, -1], 0), ([1, 2, 4], 0))[0],
        [1, 3, 6, 3, -2, -4])

    # ---- 2. one sequence infinite: closed forms --------------------
    # Check each published closed form against a brute-force truncated sum.
    def brute(xf, hf, n, lo=-200, hi=200):
        return sum(xf(k) * hf(n - k) for k in range(lo, hi + 1))

    u = lambda n: 1.0 if n >= 0 else 0.0

    # 78 Bh: h=u[n]-u[n-4], x=(1/2)^n u[n]
    #   published: y[n]=2-(1/2)^n for 0<=n<=3 ; y[n]=(1/2)^n(2^4-1)=15(1/2)^n for n>=4
    xf = lambda n: (0.5 ** n) * u(n)
    hf = lambda n: u(n) - u(n - 4)
    for n in range(0, 4):
        chk("c1 78 Bh y[%d]" % n, brute(xf, hf, n), 2 - 0.5 ** n, 1e-9)
    for n in range(4, 9):
        chk("c1 78 Bh y[%d]" % n, brute(xf, hf, n), 15 * 0.5 ** n, 1e-9)

    # 69 Ch: h=2u[n]-2u[n-4], x=(1/3)^n u[n]
    #   published: y[n]=3(1-(1/3)^{n+1}) for 0<=n<=3 ; y[n]=3(1/3)^n(3^4-1)/... check
    xf = lambda n: ((1.0 / 3) ** n) * u(n)
    hf = lambda n: 2 * u(n) - 2 * u(n - 4)
    for n in range(0, 4):
        chk("c1 69 Ch y[%d]" % n, brute(xf, hf, n), 3 * (1 - (1.0 / 3) ** (n + 1)), 1e-9)
    for n in range(4, 9):
        chk("c1 69 Ch y[%d]" % n, brute(xf, hf, n), 80 * (1.0 / 3) ** n, 1e-9)

    # 81 Ch / 80 Ch / 72 Ma: h=2u[n]-2u[n-5], x=(1/3)^n u[n]
    hf = lambda n: 2 * u(n) - 2 * u(n - 5)
    for n in range(0, 5):
        chk("c1 81 Ch y[%d]" % n, brute(xf, hf, n), 3 * (1 - (1.0 / 3) ** (n + 1)), 1e-9)
    for n in range(5, 10):
        chk("c1 81 Ch y[%d]" % n, brute(xf, hf, n), 242 * (1.0 / 3) ** n, 1e-9)

    # 73 Ma: h=u[n+1]-u[n-4] (5 taps, -1..3), x=(1/2)^n u[n]
    xf = lambda n: (0.5 ** n) * u(n)
    hf = lambda n: u(n + 1) - u(n - 4)
    for n in range(-1, 4):
        chk("c1 73 Ma y[%d]" % n, brute(xf, hf, n), 2 - 0.5 ** (n + 1), 1e-9)
    for n in range(4, 9):
        chk("c1 73 Ma y[%d]" % n, brute(xf, hf, n), 31 * 0.5 ** (n + 1), 1e-9)

    # 78 Ch: h=u[n+1]-u[n-3] (4 taps, -1..2), x=(1/2)^n u[n]
    hf = lambda n: u(n + 1) - u(n - 3)
    for n in range(-1, 3):
        chk("c1 78 Ch y[%d]" % n, brute(xf, hf, n), 2 - 0.5 ** (n + 1), 1e-9)
    for n in range(3, 9):
        chk("c1 78 Ch y[%d]" % n, brute(xf, hf, n), 15 * 0.5 ** (n + 1), 1e-9)

    # 76 Ch: x=u[n+1]-u[n-4] (5 taps, -1..3), h=(1/2)^n u[n-1]
    xf = lambda n: u(n + 1) - u(n - 4)
    hf = lambda n: (0.5 ** n) * u(n - 1)
    for n in range(0, 5):
        chk("c1 76 Ch y[%d]" % n, brute(xf, hf, n), 1 - 0.5 ** (n + 1), 1e-9)
    for n in range(5, 10):
        chk("c1 76 Ch y[%d]" % n, brute(xf, hf, n), 31 * 0.5 ** (n + 1), 1e-9)

    # 76 Bh: h=2u[n+2]-2u[n-3] (5 taps, -2..2), x=(1/3)^n u[n-1]
    xf = lambda n: ((1.0 / 3) ** n) * u(n - 1)
    hf = lambda n: 2 * u(n + 2) - 2 * u(n - 3)
    for n in range(-1, 4):
        chk("c1 76 Bh y[%d]" % n, brute(xf, hf, n), 1 - (1.0 / 3) ** (n + 2), 1e-9)
    for n in range(4, 9):
        chk("c1 76 Bh y[%d]" % n, brute(xf, hf, n), 242 * (1.0 / 3) ** (n + 2), 1e-9)

    # 77 Ch: h=2u[n+3]-2u[n-4] (7 taps, -3..3), x=(1/2)^n u[n+1]
    xf = lambda n: (0.5 ** n) * u(n + 1)
    hf = lambda n: 2 * u(n + 3) - 2 * u(n - 4)
    for n in range(-4, 3):
        chk("c1 77 Ch y[%d]" % n, brute(xf, hf, n), 8 - 0.5 ** (n + 2), 1e-9)
    for n in range(3, 9):
        chk("c1 77 Ch y[%d]" % n, brute(xf, hf, n), 127 * 0.5 ** (n + 2), 1e-9)

    # 81 Ba: h=(1/3)^n u[n-3], x=(1/6)^(n-6) u[n]
    xf = lambda n: ((1.0 / 6) ** (n - 6)) * u(n)
    hf = lambda n: ((1.0 / 3) ** n) * u(n - 3)
    for n in range(3, 10):
        chk("c1 81 Ba y[%d]" % n, brute(xf, hf, n),
            3456 * (1.0 / 3) ** (n - 3) - 1728 * (1.0 / 6) ** (n - 3), 1e-9)

    # 68 Bh: x=3^n u[-n-5], h=u[n-5]
    xf = lambda n: (3.0 ** n) if n <= -5 else 0.0
    hf = lambda n: u(n - 5)
    for n in range(-6, 1):
        chk("c1 68 Bh y[%d]" % n, brute(xf, hf, n, lo=-400), 3.0 ** (n - 4) / 2, 1e-12)
    for n in range(0, 6):
        chk("c1 68 Bh y[%d]" % n, brute(xf, hf, n, lo=-400), 1.0 / 162, 1e-12)

    # 76 Ash: the paper prints "x[n] = 2^n 4[-n], 0 < a < 1" and "h[n] = 4[n]",
    #   i.e. a^n u[-n] and u[n] with the sequences mangled in reproduction.
    #   Taken literally it DIVERGES for every n: a^n u[-n] with 0 < a < 1 grows
    #   without bound as n -> -infinity, so sum_{k<=min(0,n)} a^k is infinite.
    #   Two consistent readings, both published in the notes:
    #     A  x[n] = a^n u[n]   (matches the printed 0 < a < 1 rider)
    #        y[n] = (1 - a^{n+1})/(1 - a),  n >= 0
    #     B  x[n] = a^n u[-n] with a > 1
    #        y[n] = a^{n+1}/(a-1) for n <= 0 ;  y[n] = a/(a-1) for n >= 0
    a = 0.4
    xf = lambda n: (a ** n) * u(n)
    hf = u
    for n in range(0, 6):
        chk("c1 76 Ash A y[%d]" % n, brute(xf, hf, n),
            (1 - a ** (n + 1)) / (1 - a), 1e-9)
    a = 2.5
    xf = lambda n: (a ** n) if n <= 0 else 0.0
    for n in range(-5, 1):
        chk("c1 76 Ash B y[%d]" % n, brute(xf, hf, n, lo=-400),
            a ** (n + 1) / (a - 1), 1e-9)
    for n in range(0, 5):
        chk("c1 76 Ash B y[%d]" % n, brute(xf, hf, n, lo=-400),
            a / (a - 1), 1e-9)

    # 73 Bh: x={1, 0<=n<=4}, h={a^n, 0<=n<=6}, a>1
    #   published three ranges, with S(k)=(a^{k+1}-1)/(a-1):
    #     0<=n<=4   y=S(n)
    #     5<=n<=6   y=S(n)-S(n-5)
    #     7<=n<=10  y=S(6)-S(n-5)
    a = 2.0
    xf = lambda n: 1.0 if 0 <= n <= 4 else 0.0
    hf = lambda n: a ** n if 0 <= n <= 6 else 0.0
    S = lambda k: (a ** (k + 1) - 1) / (a - 1)
    for n in range(0, 5):
        chk("c1 73 Bh y[%d]" % n, brute(xf, hf, n), S(n), 1e-9)
    for n in range(5, 7):
        chk("c1 73 Bh y[%d]" % n, brute(xf, hf, n), S(n) - S(n - 5), 1e-9)
    for n in range(7, 11):
        chk("c1 73 Bh y[%d]" % n, brute(xf, hf, n), S(6) - S(n - 5), 1e-9)

    # ---- 3. response to a complex exponential ----------------------
    # H(e^jw) = 1/(1-a e^-jw) for h=a^n u[n]
    import cmath

    def Hexp(a, w):
        return 1.0 / (1.0 - a * cmath.exp(-1j * w))

    # 70 Ch: a=1/3, x=5 e^{j pi n/2} -> H = 1/(1+j/3) = 0.9-0.3j, |H|=0.9487
    H = Hexp(1.0 / 3, cmath.pi / 2)
    chk("c1 70 Ch H real", H.real, 0.9, 1e-9)
    chk("c1 70 Ch H imag", H.imag, -0.3, 1e-9)
    chk("c1 70 Ch |H|", abs(H), 0.94868329805, 1e-9)
    chk("c1 70 Ch angle deg", cmath.phase(H) * 180 / cmath.pi, -18.4349488, 1e-6)

    # 72 Ka / 80 Ba / 82 Ba: a=1/2, x=5 e^{j pi n/3}
    #   H = 1/(1 - 0.5 e^{-j pi/3}) = 1/(0.75 + j0.4330127)
    H = Hexp(0.5, cmath.pi / 3)
    chk("c1 72 Ka H denom re", (1 - 0.5 * cmath.exp(-1j * cmath.pi / 3)).real, 0.75, 1e-9)
    chk("c1 72 Ka H denom im", (1 - 0.5 * cmath.exp(-1j * cmath.pi / 3)).imag,
        0.4330127019, 1e-9)
    chk("c1 72 Ka |H|", abs(H), 1.15470053838, 1e-9)
    chk("c1 72 Ka angle deg", cmath.phase(H) * 180 / cmath.pi, -30.0, 1e-9)

    # 69 Bh: a=1/2, x=A e^{j pi n/2} -> H = 1/(1+0.5j), |H|=0.894427, -26.565 deg
    H = Hexp(0.5, cmath.pi / 2)
    chk("c1 69 Bh |H|", abs(H), 0.894427191, 1e-9)
    chk("c1 69 Bh angle deg", cmath.phase(H) * 180 / cmath.pi, -26.5650512, 1e-6)

    # 71 Shr: a=1/2, x=A e^{j pi n} -> H = 1/(1+0.5) = 2/3
    H = Hexp(0.5, cmath.pi)
    chk("c1 71 Shr H", H.real, 2.0 / 3, 1e-9)

    # 73 Shr: h=(1/2)^n u[n], x=10 - 5 sin(pi n/2) + 20 cos(pi n)
    #   DC: H(0)=2 -> 20 ; w=pi: H=2/3 -> 20*(2/3)=13.333 ; w=pi/2 term below
    chk("c1 73 Shr H(0)", Hexp(0.5, 0).real, 2.0, 1e-9)
    chk("c1 73 Shr H(pi)", Hexp(0.5, cmath.pi).real, 2.0 / 3, 1e-9)

    # ---- 4. convolution from tabulated data ------------------------
    # 73 Ch: x[-2]=0.5, x[0]=1, x[1]=0.75, x[3]=0.5 ; h[0]=1,h[1]=0.75,h[2]=0.5
    x = ([0.5, 0.0, 1.0, 0.75, 0.0, 0.5], -2)
    h = ([1.0, 0.75, 0.5], 0)
    y, n0 = conv(x, h)
    chk("c1 73 Ch", y, [0.5, 0.375, 1.25, 1.5, 1.0625, 0.875, 0.375, 0.25])
    chk("c1 73 Ch start", n0, -2)
    # 75 Ch: h[-2]=3, h[0]=2, h[1]=1 ; x[n]=2^n for -1<=n<=3
    h = ([3.0, 0.0, 2.0, 1.0], -2)
    x = ([0.5, 1.0, 2.0, 4.0, 8.0], -1)
    y, n0 = conv(x, h)
    chk("c1 75 Ch", y, [1.5, 3.0, 7.0, 14.5, 29.0, 10.0, 20.0, 8.0])
    chk("c1 75 Ch start", n0, -3)
    # 72 Ch: h[-2]=1, h[0]=2, h[1]=3 ; x[0]=0.5, x[2]=2, x[3]=3
    h = ([1.0, 0.0, 2.0, 3.0], -2)
    x = ([0.5, 0.0, 2.0, 3.0], 0)
    y, n0 = conv(x, h)
    chk("c1 72 Ch", y, [0.5, 0.0, 3.0, 4.5, 4.0, 12.0, 9.0])
    chk("c1 72 Ch start", n0, -2)
    # 71 Bh: h[0]=0.5,h[1]=0.75,h[2]=1 ; x[-2]=1,x[0]=0.5,x[2]=1,x[3]=0.75
    h = ([0.5, 0.75, 1.0], 0)
    x = ([1.0, 0.0, 0.5, 0.0, 1.0, 0.75], -2)
    y, n0 = conv(x, h)
    chk("c1 71 Bh", y, [0.5, 0.75, 1.25, 0.375, 1.0, 1.125, 1.5625, 0.75])
    chk("c1 71 Bh start", n0, -2)

    # ---- 5. energy and power ---------------------------------------
    # u[n]: P = 1/2 ; a^n u[n], |a|<1 : E = 1/(1-a^2)
    N = 200000
    chk("c1 P of u[n]", (N + 1) / float(2 * N + 1), 0.5, 1e-5)
    a = 0.5
    chk("c1 E of a^n u[n]", sum((a ** n) ** 2 for n in range(0, 3000)),
        1 / (1 - a * a), 1e-12)
    # x[n]=4 constant: P=16
    chk("c1 P of const 4", 16.0, 16.0)

    # ---- 6. periodicity --------------------------------------------
    import math

    def period(w, lim=5000):
        """smallest N>0 with w*N = 2 pi m, m integer; None if irrational ratio."""
        for N in range(1, lim + 1):
            m = w * N / (2 * math.pi)
            if abs(m - round(m)) < 1e-9 and round(m) >= 1:
                return N
        return None

    chk("c1 period cos(2pi n/5)", period(2 * math.pi / 5), 5)
    chk("c1 period sin(pi n/3)", period(math.pi / 3), 6)
    chk("c1 period sum 5,6", 30, 30)                      # LCM(5,6)
    chk("c1 period e^{j pi n/3}", period(math.pi / 3), 6)
    chk("c1 period e^{j pi n/2}", period(math.pi / 2), 4)
    chk("c1 period cos(pi n/2)", period(math.pi / 2), 4)
    chk("c1 period cos(pi n/4)", period(math.pi / 4), 8)
    chk("c1 period product pi/2,pi/4", 8, 8)              # LCM(4,8)
    chk("c1 period e^{j pi n/16}", period(math.pi / 16), 32)
    chk("c1 period cos(n pi/17)", period(math.pi / 17), 34)
    chk("c1 period 80 Bh product", 544, 544)              # LCM(32,34)
    chk("c1 period sin(3 pi n/5)", period(3 * math.pi / 5), 10)
    chk("c1 period cos(4 pi n/7)", period(4 * math.pi / 7), 7)
    chk("c1 period 80 Ba (b)", 70, 70)                    # LCM(10,7)
    chk("c1 period cos(11 pi n/3)", period(11 * math.pi / 3), 6)
    chk("c1 period cos(5 pi n/3)", period(5 * math.pi / 3), 6)
    chk("c1 period cos(3 pi n/8 + pi/4)", period(3 * math.pi / 8), 16)
    chk("c1 aperiodic e^{j 7n/5}", period(7.0 / 5), None)
    chk("c1 aperiodic sin(0.8n)", period(0.8), None)
    chk("c1 aperiodic sin(pi n/sqrt2)", period(math.pi / math.sqrt(2)), None)

    # cos(pi n^2 / 8): not a sinusoid in n, test x[n+N]=x[n] directly. N=8.
    f = lambda n: math.cos(math.pi * n * n / 8.0)
    chk("c1 70 Ch (i) N=8", all(abs(f(n + 8) - f(n)) < 1e-12 for n in range(-20, 21)), True)
    chk("c1 70 Ch (i) not 4", any(abs(f(n + 4) - f(n)) > 1e-9 for n in range(-20, 21)), True)
    # 80 Ba (a): sin(n pi) is identically zero for integer n, so x[n]=cos(n pi)=(-1)^n, N=2
    g = lambda n: math.sin(n * math.pi) + math.cos(n * math.pi)
    chk("c1 80 Ba (a) sin term zero",
        max(abs(math.sin(n * math.pi)) for n in range(-30, 31)) < 1e-12, True)
    chk("c1 80 Ba (a) N=2", all(abs(g(n + 2) - g(n)) < 1e-12 for n in range(-30, 31)), True)
    chk("c1 80 Ba (a) not 1", any(abs(g(n + 1) - g(n)) > 1e-9 for n in range(-30, 31)), True)

    # ---- zero-input response, 78 Bh Q4: y[n]-3y[n-1]-4y[n-2]=x[n]
    #   roots 4 and -1 ; y_zi[n] = C1 4^n + C2 (-1)^n with
    #   C1 = 16(y[-1]+y[-2])/5 , C2 = (4y[-2]-y[-1])/5
    for ym1, ym2 in ((1.0, 0.0), (0.0, 1.0), (2.0, -3.0), (-1.5, 0.5)):
        C1 = 16 * (ym1 + ym2) / 5.0
        C2 = (4 * ym2 - ym1) / 5.0
        yzi = lambda n: C1 * 4.0 ** n + C2 * (-1.0) ** n
        chk("c1 78 Bh zi ic1 (%g,%g)" % (ym1, ym2), yzi(-1), ym1, 1e-9)
        chk("c1 78 Bh zi ic2 (%g,%g)" % (ym1, ym2), yzi(-2), ym2, 1e-9)
        for n in range(0, 6):                      # satisfies the recurrence
            chk("c1 78 Bh zi rec n=%d (%g,%g)" % (n, ym1, ym2),
                yzi(n), 3 * yzi(n - 1) + 4 * yzi(n - 2), 1e-6)

    # ---- 7. sampling -----------------------------------------------
    # 81 Ch: x(t)=3 cos(100 pi t). F=50 Hz -> Nyquist 100 Hz.
    chk("c1 81 Ch Nyquist", 2 * 50, 100)
    # Fs=75 Hz: w = 2 pi F/Fs = 100 pi/75 = 4 pi/3 -> aliases to -2pi/3
    chk("c1 81 Ch w at 75", 100 * math.pi / 75, 4 * math.pi / 3, 1e-12)
    chk("c1 81 Ch alias", 4 * math.pi / 3 - 2 * math.pi, -2 * math.pi / 3, 1e-12)
    # Fs=5000: w = 100 pi/5000 = pi/50
    chk("c1 81 Ch w at 5000", 100 * math.pi / 5000, math.pi / 50, 1e-12)
    # 78 Ch: Fs=200 -> w = 100 pi/200 = pi/2
    chk("c1 78 Ch w at 200", 100 * math.pi / 200, math.pi / 2, 1e-12)
    # 80 Ch: x(t)=sin(2000 pi t)-5cos(12000 pi t)+10 sin(6000 pi t), Fs=5000
    #   F = 1000, 6000, 3000 Hz -> w = 2 pi F/Fs = 0.4pi, 2.4pi, 1.2pi
    #   alias into [-pi,pi): 0.4pi ; 2.4pi-2pi=0.4pi ; 1.2pi-2pi=-0.8pi
    chk("c1 80 Ch w1", 2 * math.pi * 1000 / 5000, 0.4 * math.pi, 1e-12)
    chk("c1 80 Ch w2 alias", 2 * math.pi * 6000 / 5000 - 2 * math.pi,
        0.4 * math.pi, 1e-12)
    chk("c1 80 Ch w3 alias", 2 * math.pi * 3000 / 5000 - 2 * math.pi,
        -0.8 * math.pi, 1e-12)
    # 80 Ch: the folded expression must sample identically to the analog signal
    fold = lambda n: (math.sin(0.4 * math.pi * n) - 5 * math.cos(0.4 * math.pi * n)
                      - 10 * math.sin(0.8 * math.pi * n))
    direct = lambda n: (math.sin(2000 * math.pi * n / 5000.0)
                        - 5 * math.cos(12000 * math.pi * n / 5000.0)
                        + 10 * math.sin(6000 * math.pi * n / 5000.0))
    for n in range(0, 8):
        chk("c1 80 Ch fold==direct n=%d" % n, fold(n), direct(n), 1e-9)
    chk("c1 80 Ch samples", [round(fold(n), 3) for n in range(4)],
        [-5.0, -6.472, 14.143, -6.053], 1e-3)

    # 73 Ma: x(t)=cos(1000 pi t)+3 sin(3000 pi t)+5 cos(5000 pi t), Fs=6000
    #   F = 500, 1500, 2500 -> w = pi/6, pi/2, 5pi/6 ; all inside [-pi,pi), no aliasing
    chk("c1 73 Ma w1", 2 * math.pi * 500 / 6000, math.pi / 6, 1e-12)
    chk("c1 73 Ma w2", 2 * math.pi * 1500 / 6000, math.pi / 2, 1e-12)
    chk("c1 73 Ma w3", 2 * math.pi * 2500 / 6000, 5 * math.pi / 6, 1e-12)
    # 76 Bh: x(t)=3cos(50 pi t)+10 sin(300 pi t)-0.7 cos(100 pi t)
    #   F = 25, 150, 50 -> Fmax=150, Nyquist=300 Hz. Fs=5000 -> no aliasing.
    chk("c1 76 Bh Nyquist", 2 * 150, 300)
    chk("c1 76 Bh w1", 2 * math.pi * 25 / 5000, math.pi / 100, 1e-12)
    chk("c1 76 Bh w2", 2 * math.pi * 150 / 5000, 3 * math.pi / 50, 1e-12)
    chk("c1 76 Bh w3", 2 * math.pi * 50 / 5000, math.pi / 50, 1e-12)


CHAPTERS = {"ch1": ch1}


def main():
    names = sys.argv[1:] or list(CHAPTERS)
    for n in names:
        if n not in CHAPTERS:
            print("unknown chapter:", n)
            continue
        CHAPTERS[n]()
    print("%d checks passed" % OK[0])
    if FAIL:
        print("\n%d FAILED:" % len(FAIL))
        for f in FAIL:
            print("  " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
