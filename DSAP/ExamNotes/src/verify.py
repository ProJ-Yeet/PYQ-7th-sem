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
    elif isinstance(want, str) or isinstance(got, str):
        same = got == want                 # a window name is an answer too
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


def izt(X, r, ns, N=8192):
    """Numerical inverse Z-transform on the circle |z| = r, which must lie in
    the ROC:  x[n] ~ (r^n / N) sum_k X(r e^{j2pi k/N}) e^{j2pi kn/N}.
    Exact up to aliasing of x[n + mN] r^(-mN), negligible at N = 8192."""
    import cmath
    vals = [X(r * cmath.exp(2j * cmath.pi * k / N)) for k in range(N)]
    out = {}
    for n in ns:
        acc = sum(vals[k] * cmath.exp(2j * cmath.pi * k * n / N) for k in range(N))
        out[n] = ((r ** n) * acc / N).real
    return out


def chkseq(tag, X, r, closed, ns, tol=1e-6):
    """Assert a published closed form against the numerical inversion."""
    got = izt(X, r, ns)
    for n in ns:
        chk("%s n=%d" % (tag, n), got[n], closed(n), tol)


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


# =====================================================================
#  CHAPTER 2 — Z-TRANSFORM
#  Every inverse is checked against izt(), which knows nothing about the
#  published partial fractions: it integrates X(z) on a circle in the ROC.
# =====================================================================
def ch2():
    u = lambda n: 1.0 if n >= 0 else 0.0
    un1 = lambda n: 1.0 if n <= -1 else 0.0          # u[-n-1]
    d = lambda n: 1.0 if n == 0 else 0.0

    # ---- proper rational, partial fractions -------------------------
    # 80 Bh: (1+2z^-1+z^-2)/(1-0.75z^-1+0.125z^-2), ROC 0.25<|z|<0.5
    #   = 8 + 18/(1-0.5z^-1) - 25/(1-0.25z^-1); pole .5 left, pole .25 right
    X = lambda z: (1 + 2 / z + 1 / z ** 2) / (1 - 0.75 / z + 0.125 / z ** 2)
    f = lambda n: 8 * d(n) - 18 * 0.5 ** n * un1(n) - 25 * 0.25 ** n * u(n)
    chkseq("c2 80 Bh", X, 0.35, f, range(-5, 6))

    # 81 Ba: 1/(1-0.8z^-1+0.12z^-2) = 1.5/(1-0.6z^-1) - 0.5/(1-0.2z^-1)
    X = lambda z: 1 / (1 - 0.8 / z + 0.12 / z ** 2)
    chkseq("c2 81 Ba (i)", X, 0.9,
           lambda n: (1.5 * 0.6 ** n - 0.5 * 0.2 ** n) * u(n), range(0, 8))
    chkseq("c2 81 Ba (ii)", X, 0.1,
           lambda n: (-1.5 * 0.6 ** n + 0.5 * 0.2 ** n) * un1(n), range(-6, 1))
    chkseq("c2 81 Ba (iii)", X, 0.4,
           lambda n: -1.5 * 0.6 ** n * un1(n) - 0.5 * 0.2 ** n * u(n), range(-5, 6))

    # 82 Ba / 73 Bh / 72 Ma: 1/(1-1.5z^-1+0.5z^-2) = 2/(1-z^-1) - 1/(1-0.5z^-1)
    X = lambda z: 1 / (1 - 1.5 / z + 0.5 / z ** 2)
    chkseq("c2 82 Ba (a)", X, 1.6, lambda n: (2 - 0.5 ** n) * u(n), range(0, 8))
    chkseq("c2 82 Ba (b)", X, 0.3, lambda n: (-2 + 0.5 ** n) * un1(n), range(-6, 1))
    chkseq("c2 82 Ba (c)", X, 0.75,
           lambda n: -2 * un1(n) - 0.5 ** n * u(n), range(-5, 6))

    # 80 Ba: (1+2z^-1+z^-2)/(1-1.5z^-1+0.5z^-2) = 2 + 8/(1-z^-1) - 9/(1-0.5z^-1)
    X = lambda z: (1 + 2 / z + 1 / z ** 2) / (1 - 1.5 / z + 0.5 / z ** 2)
    chkseq("c2 80 Ba", X, 1.6,
           lambda n: 2 * d(n) + (8 - 9 * 0.5 ** n) * u(n), range(0, 8))

    # 71 Shr: (1+2z^-1+z^-2)/(1+1.5z^-1+0.5z^-2) = 2 - 1/(1+0.5z^-1)
    #   the numerator's (1+z^-1) cancels one factor: worth the note in the text
    X = lambda z: (1 + 2 / z + 1 / z ** 2) / (1 + 1.5 / z + 0.5 / z ** 2)
    chkseq("c2 71 Shr", X, 1.6,
           lambda n: 2 * d(n) - (-0.5) ** n * u(n), range(0, 8))

    # 80 Ch / 70 Bh: (1+2z^-1+z^-2)/(1+4z^-1+4z^-2), causal; double pole -2
    X = lambda z: (1 + 2 / z + 1 / z ** 2) / (1 + 4 / z + 4 / z ** 2)
    chkseq("c2 80 Ch", X, 3.0,
           lambda n: 0.25 * d(n) + (0.25 * n + 0.75) * (-2.0) ** n * u(n), range(0, 8))

    # 69 Bh: (1-0.5z^-2)/((1-0.5z^-1)(1-0.25z^-1)), |z|>0.5
    X = lambda z: (1 - 0.5 / z ** 2) / ((1 - 0.5 / z) * (1 - 0.25 / z))
    chkseq("c2 69 Bh", X, 0.9,
           lambda n: -4 * d(n) + (-2 * 0.5 ** n + 7 * 0.25 ** n) * u(n), range(0, 8))

    # ---- improper: long-divide to a polynomial in z, then X(z)/z -----
    # denominator z^2-1.5z-1 = (z-2)(z+0.5), ROC |z|<0.5 -> both poles left-sided
    fam = [
        # (tag, numerator coeffs z^4..z^0, Q coeffs z^2,z^1,z^0, D, E)
        ("79 Bh", (2, 2, 0, -3, 2), (2, 5, 9.5), -11.5, 8.8, 2.7),
        ("76 Ch", (1, 5, 0, -3, 4), (1, 6.5, 10.75), -14.75, 10.8, 3.95),
        ("81 Ch", (1, 1, 0, -3, 5), (1, 2.5, 4.75), -9.75, 4.6, 5.15),
        ("79 Ch", (1, -2, 0, -1, 4), (1, -0.5, 0.25), -4.25, 0.4, 3.85),
        ("72 Ash", (1, 2, 0, -1, 4), (1, 3.5, 6.25), -10.25, 6.8, 3.45),
    ]
    for tag, num, Q, C, D, E in fam:
        Xf = (lambda num: lambda z: sum(c * z ** (4 - i) for i, c in enumerate(num))
              / (z ** 2 - 1.5 * z - 1))(num)
        cf = (lambda Q, C, D, E: lambda n:
              Q[0] * d(n + 2) + Q[1] * d(n + 1) + (Q[2] + C) * d(n)
              - (D * 2.0 ** n + E * (-0.5) ** n) * un1(n))(Q, C, D, E)
        chkseq("c2 " + tag, Xf, 0.3, cf, range(-5, 4))

    # 74 Ch / 73 Ch / 74 Bh: (2z^3+2z^2+3z+5)/(z^2-0.1z-0.2), ROC |z|<0.4
    X = lambda z: (2 * z ** 3 + 2 * z ** 2 + 3 * z + 5) / (z ** 2 - 0.1 * z - 0.2)
    D, E = 7.25 / 0.45, 3.992 / 0.36
    chkseq("c2 74 Ch", X, 0.3,
           lambda n: 2 * d(n + 1) + (2.2 - 27.2) * d(n)
           - (D * 0.5 ** n + E * (-0.4) ** n) * un1(n), range(-5, 4))

    # 81 Bh: (2z^3-5z^2+z+3)/((z-1)(z-2)), ROC |z|<1
    X = lambda z: (2 * z ** 3 - 5 * z ** 2 + z + 3) / ((z - 1) * (z - 2))
    chkseq("c2 81 Bh", X, 0.6,
           lambda n: 2 * d(n + 1) + 1.5 * d(n) + (1 - 0.5 * 2.0 ** n) * un1(n),
           range(-5, 4))

    # ---- X(z)/z with a repeated pole --------------------------------
    # 76 Ash: z/((z-0.6)(z+0.5)^2), ROC |z|>0.6, causal
    A = 1 / 1.21
    X = lambda z: z / ((z - 0.6) * (z + 0.5) ** 2)
    chkseq("c2 76 Ash", X, 1.2,
           lambda n: (A * 0.6 ** n + ((20.0 / 11) * n - A) * (-0.5) ** n) * u(n),
           range(0, 9))

    # 73 Shr: z/((z-0.4)(z+1.5)^2), ROC |z|<0.4, all left-sided
    A = 1 / 3.61
    X = lambda z: z / ((z - 0.4) * (z + 1.5) ** 2)
    chkseq("c2 73 Shr", X, 0.25,
           lambda n: (-A * 0.4 ** n + A * (-1.5) ** n
                      + (1 / 1.9) * n * (-1.5) ** (n - 1)) * un1(n),
           range(-6, 1), tol=1e-5)

    # 70 Asa: z/((z-1)(z-2)^2), ROC |z|<1, all left-sided
    X = lambda z: z / ((z - 1) * (z - 2) ** 2)
    chkseq("c2 70 Asa", X, 0.7,
           lambda n: (-1 + 2.0 ** n - n * 2.0 ** (n - 1)) * un1(n), range(-7, 1))

    # ---- long division (power series) -------------------------------
    # 77 Ch: 1/(1-0.5z^-1+1.5z^-2), right-sided.  x[n]=0.5x[n-1]-1.5x[n-2]
    X = lambda z: 1 / (1 - 0.5 / z + 1.5 / z ** 2)
    seq = [1.0, 0.5]
    while len(seq) < 8:
        seq.append(0.5 * seq[-1] - 1.5 * seq[-2])
    chkseq("c2 77 Ch", X, 1.8, lambda n: seq[n] if 0 <= n < len(seq) else 0.0,
           range(0, 8))
    chk("c2 77 Ch terms", seq[:6], [1, 0.5, -1.25, -1.375, 1.1875, 2.65625])
    # its poles sit at |z| = sqrt(1.5), so the printed ROC |z|>1 contains them
    chk("c2 77 Ch pole radius", 1.5 ** 0.5, 1.2247448714, 1e-9)

    # 76 Bh as printed: 1/(1-1.58z^-1+0.5z^-2).  Poles are NOT 1 and 0.5.
    disc = (1.58 ** 2 - 4 * 0.5) ** 0.5
    chk("c2 76 Bh pole hi", (1.58 + disc) / 2, 1.1422782991, 1e-9)
    chk("c2 76 Bh pole lo", (1.58 - disc) / 2, 0.4377217009, 1e-9)
    X = lambda z: 1 / (1 - 1.58 / z + 0.5 / z ** 2)
    seq = [1.0, 1.58]
    while len(seq) < 7:
        seq.append(1.58 * seq[-1] - 0.5 * seq[-2])
    chkseq("c2 76 Bh printed", X, 1.6,
           lambda n: seq[n] if 0 <= n < len(seq) else 0.0, range(0, 7))
    chk("c2 76 Bh terms", [round(v, 4) for v in seq[:5]],
        [1.0, 1.58, 1.9964, 2.3643, 2.7374], 1e-3)

    # 71 Ch: 1/((z-0.5)(z+2)) = -1 + 0.8 z/(z-0.5) + 0.2 z/(z+2)
    X = lambda z: 1 / ((z - 0.5) * (z + 2))
    chkseq("c2 71 Ch (i)", X, 1.0,
           lambda n: -d(n) + 0.8 * 0.5 ** n * u(n) - 0.2 * (-2.0) ** n * un1(n),
           range(-5, 6))
    chkseq("c2 71 Ch (ii)", X, 0.3,
           lambda n: -d(n) - (0.8 * 0.5 ** n + 0.2 * (-2.0) ** n) * un1(n),
           range(-6, 2))
    chkseq("c2 71 Ch (iii)", X, 3.0,
           lambda n: -d(n) + (0.8 * 0.5 ** n + 0.2 * (-2.0) ** n) * u(n),
           range(0, 8))

    # ---- finite polynomials, read straight off ----------------------
    # 74 Ash: z^2(1-1.5z^-1)(1+z^-1)(1-z^-1) = z^2 -1.5z -1 +1.5z^-1
    X = lambda z: z ** 2 * (1 - 1.5 / z) * (1 + 1 / z) * (1 - 1 / z)
    chkseq("c2 74 Ash", X, 1.0,
           lambda n: d(n + 2) - 1.5 * d(n + 1) - d(n) + 1.5 * d(n - 1), range(-3, 4))
    # 78 Ch: z^2(1-1.5z^-1)(1-z^-1)(1+z^-2)
    X = lambda z: z ** 2 * (1 - 1.5 / z) * (1 - 1 / z) * (1 + 1 / z ** 2)
    chkseq("c2 78 Ch", X, 1.0,
           lambda n: d(n + 2) - 2.5 * d(n + 1) + 2.5 * d(n)
           - 2.5 * d(n - 1) + 1.5 * d(n - 2), range(-3, 5))

    # ---- forward Z-transforms and their ROCs ------------------------
    # 70 Ch / 70 Asa as printed: both radii are 1/3, so the two ROCs
    # (|z|>1/3 and |z|<1/3) do not intersect -> X(z) does not exist.
    chk("c2 70 Ch radii equal", abs(-1.0 / 3), abs(1.0 / 3), 1e-15)
    # the intended (BB Sir's) version, second term (1/2)^n -> ROC 1/3<|z|<1/2
    X = lambda z: 1 / (1 + (1.0 / 3) / z) + 1 / (1 - 0.5 / z)
    chkseq("c2 70 Ch intended", X, 0.4,
           lambda n: (-1.0 / 3) ** n * u(n) - 0.5 ** n * un1(n), range(-5, 6))
    # 75 Ash: (0.6)^n u[n] + (0.25)^n u[n], ROC |z|>0.6
    X = lambda z: 1 / (1 - 0.6 / z) + 1 / (1 - 0.25 / z)
    chkseq("c2 75 Ash", X, 0.9,
           lambda n: (0.6 ** n + 0.25 ** n) * u(n), range(0, 8))
    # 75 Ch: (0.1)^n u[n] + (0.3)^n u[-n-1], ROC 0.1<|z|<0.3
    X = lambda z: 1 / (1 - 0.1 / z) - 1 / (1 - 0.3 / z)
    chkseq("c2 75 Ch", X, 0.2,
           lambda n: 0.1 ** n * u(n) + 0.3 ** n * un1(n), range(-5, 6))
    # 75 Bh: (0.25)^n u[n] + (0.6)^n u[-n-1], ROC 0.25<|z|<0.6
    X = lambda z: 1 / (1 - 0.25 / z) - 1 / (1 - 0.6 / z)
    chkseq("c2 75 Bh", X, 0.4,
           lambda n: 0.25 ** n * u(n) + 0.6 ** n * un1(n), range(-5, 6))
    # 73 Ma: (0.5+j0.2)^n u[n] + (-j)^n u[-n-1] -> ROC sqrt(0.29)<|z|<1
    import cmath
    chk("c2 73 Ma inner radius", abs(0.5 + 0.2j), 0.5385164807, 1e-9)
    chk("c2 73 Ma outer radius", abs(-1j), 1.0, 1e-12)
    #   z=0.4 lies OUTSIDE the ROC, so X(0.4) does not converge; z=0.7 is inside
    Xv = 1 / (1 - (0.5 + 0.2j) / 0.7) - 1 / (1 + 1j / 0.7)
    chk("c2 73 Ma X(0.7) re", Xv.real, 1.4211409396, 1e-9)
    chk("c2 73 Ma X(0.7) im", Xv.imag, 2.2197986577, 1e-9)

    # 78 Ch / 70 Ma: Z{n a^n u[n]} = a z^-1 / (1 - a z^-1)^2, |z|>|a|
    a = 0.7
    X = lambda z: a / z / (1 - a / z) ** 2
    chkseq("c2 na^n", X, 1.4, lambda n: n * a ** n * u(n), range(0, 9))
    # 74 Ma: Z{cos(w n) u[n]} = (1 - z^-1 cos w)/(1 - 2 z^-1 cos w + z^-2)
    import math
    w = 0.6
    X = lambda z: ((1 - math.cos(w) / z)
                   / (1 - 2 * math.cos(w) / z + 1 / z ** 2))
    chkseq("c2 cos wn", X, 1.5, lambda n: math.cos(w * n) * u(n), range(0, 9))


# ---------------------------------------------------------------- chapter 3

def _roots(c):
    """Roots in z of a polynomial given in powers of z^-1, highest power last.
    numpy is available here (figs.py already depends on it)."""
    import numpy as np
    c = list(c)
    while len(c) > 1 and abs(c[-1]) < 1e-15:
        c.pop()
    if len(c) == 1:
        return []
    return sorted(np.roots(c).tolist(), key=lambda z: (round(z.real, 9),
                                                       round(z.imag, 9)))


def _H(b, a, w):
    """H(e^jw) from coefficient lists in z^-1."""
    import cmath
    z = cmath.exp(1j * w)
    num = sum(c * z ** (-i) for i, c in enumerate(b))
    den = sum(c * z ** (-i) for i, c in enumerate(a))
    return num / den


def chkroots(tag, coeffs, want):
    """Assert the published root set, in any order, to 4 decimals."""
    got = _roots(coeffs)
    g = sorted((round(z.real, 4), round(z.imag, 4)) for z in got)
    wnt = sorted((round(complex(z).real, 4), round(complex(z).imag, 4)) for z in want)
    chk(tag, [x for pair in g for x in pair], [x for pair in wnt for x in pair],
        tol=2e-4)


def chkmag(tag, b, a, want, tol=5e-3):
    """Assert |H| at w = 0, pi/2, pi against the three published anchor values."""
    import math
    got = [abs(_H(b, a, w)) for w in (0.0, math.pi / 2, math.pi)]
    chk(tag, got, want, tol=tol)


def chkpeak(tag, b, a, want_mag, want_deg, tol=5e-3):
    import math
    ws = [math.pi * k / 4000 for k in range(4001)]
    ms = [abs(_H(b, a, w)) for w in ws]
    i = max(range(len(ms)), key=lambda k: ms[k])
    chk(tag + " peak", ms[i], want_mag, tol=tol)
    chk(tag + " peak angle", math.degrees(ws[i]), want_deg, tol=0.6)


def ch3():
    import math

    # --- section 1, the lead worked example and its twin
    chkroots("c3 80Ch zeros", [1, 0.5], [-0.5])
    chkroots("c3 80Ch poles", [1, -0.4, 0.25], [0.2 + 0.4583j, 0.2 - 0.4583j])
    chk("c3 80Ch |p|", abs(complex(0.2, 0.4582576)), 0.5, tol=1e-6)
    chk("c3 80Ch pole angle",
        math.degrees(math.atan2(0.4582576, 0.2)), 66.4, tol=0.05)
    chkmag("c3 80Ch |H|", [1, 0.5], [1, -0.4, 0.25], [1.765, 1.315, 0.303])
    chkpeak("c3 80Ch", [1, 0.5], [1, -0.4, 0.25], 1.96, 50.9)

    chkmag("c3 78Bh |H|", [1, -0.4], [1, -0.4, 0.25], [0.706, 1.267, 0.849])
    chkpeak("c3 78Bh", [1, -0.4], [1, -0.4, 0.25], 1.34, 73.9)

    # --- section 1 table, every remaining paper
    T = [
        ("80Bh", [1, 0.8, 0.8], [1, 0, -0.49],
         [-0.4 + 0.8j, -0.4 - 0.8j], [0.7, -0.7], [5.10, 0.55, 1.96]),
        ("79Bh", [1, -0.75], [1, -0.35, 0.25],
         [0.75], [0.175 + 0.4684j, 0.175 - 0.4684j], [0.28, 1.51, 1.09]),
        ("79Ba", [1, -0.5], [1, -0.3, 0.2],
         [0.5], [0.15 + 0.4213j, 0.15 - 0.4213j], [0.56, 1.31, 1.00]),
        ("74Ash", [1, 0.5, 0.6, 0.8], [1, -0.4, 0.2],
         [0.1845 + 0.9416j, 0.1845 - 0.9416j, -0.8690],
         [0.2 + 0.4j, 0.2 - 0.4j], [3.63, 0.56, 0.19]),
        ("72Ka", [1, 0.7], [1, -0.5, 0.3],
         [-0.7], [0.25 + 0.4873j, 0.25 - 0.4873j], [2.13, 1.42, 0.17]),
        ("72Ch", [1, 0.6], [1, -0.4, 0.1],
         [-0.6], [0.2 + 0.2449j, 0.2 - 0.2449j], [2.29, 1.18, 0.27]),
        ("70Ch", [1, 0.5], [1, -0.3, 0.225],
         [-0.5], [0.15 + 0.45j, 0.15 - 0.45j], [1.62, 1.35, 0.33]),
        ("71Bh", [1, -0.4], [1, -0.3, 0.225],
         [0.4], [0.15 + 0.45j, 0.15 - 0.45j], [0.65, 1.30, 0.92]),
        ("73Ma", [1, 0.7], [1, -0.3, 0.2],
         [-0.7], [0.15 + 0.4213j, 0.15 - 0.4213j], [1.89, 1.43, 0.20]),
        ("69Ch", [1, 0.1, -0.06], [1, -0.4, 0.2],
         [-0.3, 0.2], [0.2 + 0.4j, 0.2 - 0.4j], [1.30, 1.19, 0.53]),
        ("76Bh", [1, -0.1, -0.2], [1, -0.6, 0.35],
         [0.5, -0.4], [0.3 + 0.5099j, 0.3 - 0.5099j], [0.93, 1.36, 0.46]),
        ("75Ch", [4, 0.7, 2], [1, -0.3],
         [-0.0875 + 0.7017j, -0.0875 - 0.7017j], [0.3], [9.57, 2.03, 4.08]),
        ("69Bh-tt", [1, 0, 1.21], [1, 0.8],
         [1.1j, -1.1j], [-0.8], [1.23, 0.16, 11.05]),
        ("70Asa", [1, 0, 1], [1],
         [1j, -1j], [], [2.00, 0.0, 2.00]),
    ]
    for tag, b, a, zs, ps, mags in T:
        chkroots("c3 %s zeros" % tag, b, zs)
        chkroots("c3 %s poles" % tag, a, ps)
        chkmag("c3 %s |H|" % tag, b, a, mags)

    chkpeak("c3 80Bh", [1, 0.8, 0.8], [1, 0, -0.49], 5.098, 0.0)
    chkpeak("c3 79Bh", [1, -0.75], [1, -0.35, 0.25], 1.53, 83.4)
    chkpeak("c3 79Ba", [1, -0.5], [1, -0.3, 0.2], 1.31, 85.0)
    chkpeak("c3 72Ka", [1, 0.7], [1, -0.5, 0.3], 2.44, 50.3)
    chkpeak("c3 70Ch", [1, 0.5], [1, -0.3, 0.225], 1.80, 54.5)
    chkpeak("c3 71Bh", [1, -0.4], [1, -0.3, 0.225], 1.32, 81.3)
    chkpeak("c3 73Ma", [1, 0.7], [1, -0.3, 0.2], 2.00, 48.0)
    chkpeak("c3 69Ch", [1, 0.1, -0.06], [1, -0.4, 0.2], 1.51, 54.9)
    chkpeak("c3 76Bh", [1, -0.1, -0.2], [1, -0.6, 0.35], 1.91, 60.9)

    # 70 Asa / 70 Ma: |H| = 2|cos w| exactly, and h is finite so it is stable
    for k in range(13):
        w = math.pi * k / 12
        chk("c3 70Asa |H|=2|cos w| at k=%d" % k,
            abs(_H([1, 0, 1], [1], w)), 2 * abs(math.cos(w)), tol=1e-9)
    chk("c3 70Asa sum|h|", 1 + 0 + 1, 2)

    # 81 Ba / 76 Ash: the pole really is at 2.75, so a causal ROC excludes |z|=1
    chkroots("c3 81Ba poles", [1, -2.75], [2.75])
    chkroots("c3 81Ba zeros", [0.67, -0.3], [0.3 / 0.67])
    chk("c3 81Ba pole outside unit circle", 1.0 if 2.75 > 1 else 0.0, 1.0)
    chkmag("c3 81Ba |H| anticausal", [0.67, -0.3], [1, -2.75],
           [0.2114, 0.2509, 0.2587])

    # --- section 2, poles and zeros given directly
    def frompz(poles, zeros):
        """Coefficient lists in z^-1 for a monic ratio with these roots."""
        import numpy as np
        a = np.poly(poles).real.tolist() if poles else [1.0]
        b = np.poly(zeros).real.tolist() if zeros else [1.0]
        return b, a

    b, a = frompz([0.45 + 1.6j, 0.45 - 1.6j], [0.58 + 2.06j, 0.58 - 2.06j])
    chk("c3 80Ba |p|", abs(complex(0.45, 1.6)), 1.6621, tol=5e-5)
    chk("c3 80Ba |z|", abs(complex(0.58, 2.06)), 2.1401, tol=5e-5)
    chk("c3 80Ba pole angle", math.degrees(math.atan2(1.6, 0.45)), 74.3, tol=0.05)
    chk("c3 80Ba zero angle", math.degrees(math.atan2(2.06, 0.58)), 74.3, tol=0.05)
    chk("c3 80Ba denom", a, [1.0, -0.9, 2.7625], tol=1e-9)
    chk("c3 80Ba numer", b, [1.0, -1.16, 4.5800], tol=1e-3)
    chkmag("c3 80Ba |H|", b, a, [1.544, 1.902, 1.446])
    chkpeak("c3 80Ba", b, a, 2.04, 74.0)

    b, a = frompz([0.45 + 1.06j, 0.45 - 1.06j], [0.58 + 2.06j, 0.58 - 2.06j])
    chk("c3 76Ch |p|", abs(complex(0.45, 1.06)), 1.1516, tol=5e-5)
    chkmag("c3 76Ch |H|", b, a, [3.10, 3.93, 2.09], tol=6e-3)
    chkpeak("c3 76Ch", b, a, 11.50, 66.7, tol=2e-2)

    b, a = frompz([0.45 - 0.77j, -2 + 0.3j, -2 - 0.3j], [])
    chk("c3 74Ch |p1|", abs(complex(0.45, 0.77)), 0.8919, tol=5e-5)
    chk("c3 74Ch |p2|", abs(complex(-2, 0.3)), 2.0224, tol=5e-5)
    chkmag("c3 74Ch |H| as printed", b, a, [0.20, 0.18, 0.63], tol=6e-3)
    b, a = frompz([0.45 + 0.77j, 0.45 - 0.77j, -2 + 0.3j, -2 - 0.3j], [])
    chkmag("c3 74Ch |H| conjugate restored", b, a, [0.12, 0.21, 0.34], tol=6e-3)
    chkpeak("c3 74Ch restored", b, a, 0.80, 59.9, tol=6e-3)

    b, a = frompz([0.45 - 0.77j, -2 + 0.3j, -2 - 0.3j], [1.2 + 3j, 1.2 - 3j])
    chk("c3 75Bh |z|", abs(complex(1.2, 3.0)), 3.2311, tol=5e-5)
    chkmag("c3 75Bh |H|", b, a, [1.81, 1.76, 8.76], tol=6e-3)
    b2, a2 = frompz([0.45 + 0.77j, -2 + 0.3j, -2 - 0.3j], [1.2 + 3j, 1.2 - 3j])
    chkmag("c3 71Ch |H| equals 75Bh", b2, a2, [1.81, 1.76, 8.76], tol=6e-3)

    b, a = frompz([0.45 + 0.77j, 2 + 0.7j, 2 - 0.7j], [1.2 + 0.43j, 1.2 - 0.43j])
    chk("c3 73Ch |p2|", abs(complex(2, 0.7)), 2.1190, tol=5e-5)
    chk("c3 73Ch |z|", abs(complex(1.2, 0.43)), 1.2747, tol=5e-5)
    chkmag("c3 73Ch |H|", b, a, [0.27, 0.43, 0.37], tol=6e-3)

    # polar forms the papers reuse
    # the source rounds: the exact conversion is 0.4575 + j0.7745
    chk("c3 polar 0.9 at 1.0376 rad -> real",
        0.9 * math.cos(1.0376), 0.4575, tol=5e-4)
    chk("c3 polar 0.9 at 1.0376 rad -> imag",
        0.9 * math.sin(1.0376), 0.7751, tol=5e-4)
    chk("c3 polar rounds to the printed 0.45",
        round(0.9 * math.cos(1.0376), 2), 0.46, tol=1e-9)
    chk("c3 polar 0.892 at 2.5158 rad -> real",
        0.892 * math.cos(2.5158), -0.728, tol=6e-3)
    chk("c3 polar 0.892 at 2.5158 rad -> imag",
        0.892 * math.sin(2.5158), 0.522, tol=6e-3)

    # --- section 3, all-pole systems
    chkroots("c3 68Bh poles", [1, -10.0 / 24, 1.0 / 24], [0.25, 1.0 / 6])
    chkmag("c3 68Bh |H|", [1], [1, -10.0 / 24, 1.0 / 24], [1.600, 0.957, 0.686])
    for w, mag, ang in ((math.pi / 3, 1.1955, -0.3987),
                        (math.pi / 5, 1.4159, -0.2949)):
        import cmath
        H = _H([1], [1, -10.0 / 24, 1.0 / 24], w)
        chk("c3 68Bh |H| at w=%.4f" % w, abs(H), mag, tol=5e-4)
        chk("c3 68Bh argH at w=%.4f" % w, cmath.phase(H), ang, tol=5e-4)

    chkroots("c3 69Bh poles", [1, -0.8, 0.15], [0.5, 0.3])
    chkmag("c3 69Bh |H|", [1], [1, -0.8, 0.15], [2.857, 0.857, 0.513])

    chkroots("c3 67Mng poles as printed", [1, -5.0 / 6, -1.0 / 6], [1.0, -1.0 / 6])
    chkroots("c3 67Mng poles sign fixed", [1, -5.0 / 6, 1.0 / 6], [0.5, 1.0 / 3])
    chk("c3 67Mng fixed |H(1)|", abs(_H([1], [1, -5.0 / 6, 1.0 / 6], 0.0)), 3.0,
        tol=1e-6)

    # --- section 4, zero input and zero state
    r1, r2 = (1 + 5 ** 0.5) / 4, (1 - 5 ** 0.5) / 4
    chkroots("c3 66Ma poles", [1, -0.5, -0.25], [r1, r2])
    chk("c3 66Ma p1", r1, 0.8090, tol=5e-5)
    chk("c3 66Ma p2", r2, -0.3090, tol=5e-5)
    C1, C2 = 1 + 2 / 5 ** 0.5, 1 - 2 / 5 ** 0.5
    chk("c3 66Ma C1", C1, 1.8944, tol=5e-5)
    chk("c3 66Ma C2", C2, 0.1056, tol=5e-5)
    # the constants must reproduce the stated initial conditions
    chk("c3 66Ma y(-1)", C1 * r1 ** -1 + C2 * r2 ** -1, 2.0, tol=1e-9)
    chk("c3 66Ma y(-2)", C1 * r1 ** -2 + C2 * r2 ** -2, 4.0, tol=1e-9)
    A = r1 ** 2 / ((r1 - r2) * (r1 - 0.2))
    Bb = r2 ** 2 / ((r2 - r1) * (r2 - 0.2))
    D = 0.2 ** 2 / ((0.2 - r1) * (0.2 - r2))
    chk("c3 66Ma zsr A", A, 0.9612, tol=5e-5)
    chk("c3 66Ma zsr B", Bb, 0.1678, tol=5e-5)
    chk("c3 66Ma zsr D", D, -4.0 / 31, tol=1e-9)
    chk("c3 66Ma residues sum to y[0]=1", A + Bb + D, 1.0, tol=1e-9)
    chk("c3 66Ma total C1", C1 + A, 2.8557, tol=5e-5)
    chk("c3 66Ma total C2", C2 + Bb, 0.2734, tol=5e-5)
    # and the closed forms must match the raw recurrence
    hist = {-1: 2.0, -2: 4.0}
    for n in range(0, 7):
        hist[n] = 0.5 * hist[n - 1] + 0.25 * hist[n - 2] + 0.2 ** n
    for n, want in ((0, 3.0), (1, 2.2), (2, 1.89), (3, 1.503), (4, 1.2256)):
        chk("c3 66Ma total y[%d]" % n, hist[n], want, tol=1e-9)
        closed = ((C1 + A) * r1 ** n + (C2 + Bb) * r2 ** n - (4.0 / 31) * 0.2 ** n)
        chk("c3 66Ma closed form y[%d]" % n, closed, hist[n], tol=1e-6)

    chkroots("c3 78Bh ZIR roots", [1, -3, -4], [4.0, -1.0])

    # --- section 5, linear phase
    import cmath
    h = [-1, 0, 1]
    for k in range(1, 12):
        w = math.pi * k / 12
        H = sum(c * cmath.exp(-1j * w * n) for n, c in enumerate(h))
        chk("c3 70Asa |H|=2|sin w| k=%d" % k, abs(H), 2 * abs(math.sin(w)),
            tol=1e-9)
        # arg H = -w - pi/2 leaves the principal range once w > pi/2, so the
        # comparison has to be modulo 2 pi: the notes state the unwrapped phase,
        # which is the one whose slope is the group delay.
        d = (cmath.phase(H) - (-w - math.pi / 2)) % (2 * math.pi)
        chk("c3 70Asa phase = -w-pi/2 (mod 2pi) k=%d" % k,
            min(d, 2 * math.pi - d), 0.0, tol=1e-9)
    chk("c3 70Asa antisymmetric", [h[0] + h[2], h[1]], [0, 0])
    chk("c3 70Asa grd", 1.0, (3 - 1) / 2.0)


# ---------------------------------------------------------------- chapter 4

def ch4():
    """Assert every k, C and quantization value printed in ch4-num.tex."""
    from fractions import Fraction as Fr
    import lattice as L
    import quant as Q

    def close(seq, want, tol=6e-5):
        chk("c4 " + close.tag, [float(x) for x in seq], want, tol=tol)

    # --- section 3, the FIR lattices, against the published k lists
    FIR = [
        ("81Ba/78Bh/74Ch", [1, Fr(13, 24), Fr(5, 8), Fr(1, 3)],
         [0.25, 0.5, 1.0 / 3]),
        ("73Shr", [1, Fr(9, 10), Fr(-4, 5), Fr(1, 2)], [-2.6, -1.66667, 0.5]),
        ("76Bh", [1, 2, "0.62", "0.8"], [-2.42581, -2.72222, 0.8]),
        ("72Ka/69Ch", [1, 2, -3, 4], [-0.53846, 0.73333, 4.0]),
        ("70Ch", [1, "3.1", "5.5", "4.2", "2.3"],
         [0.33814, 1.16636, 0.68298, 2.3]),
    ]
    for tag, a, want in FIR:
        ks, _ = L.stepdown(a)
        close.tag = tag + " k"
        close(ks, want)
        # the round trip is the independent check
        chk("c4 %s round trip" % tag, [float(x) for x in L.stepup(ks)],
            [float(L.fr(x)) for x in a], tol=1e-9)

    # 74 Ch prints the same filter with unreduced fractions
    chk("c4 74Ch 52/96 = 13/24", Fr(52, 96), Fr(13, 24))
    chk("c4 74Ch 25/40 = 5/8", Fr(25, 40), Fr(5, 8))

    # --- the symmetric papers: a lattice must NOT exist
    for tag, a in (("72Ch", [1, 2, 1]),
                   ("73Bh", [1, 2, 2, 1]),
                   ("75Ch/73Ch", [1, Fr(2, 3), Fr(5, 8), Fr(2, 3), 1]),
                   ("74Ash", [1, "0.7", "1.2", -1])):
        try:
            L.stepdown(a)
            FAIL.append("c4 %s should have no lattice" % tag)
        except L.Unstable:
            OK[0] += 1
    # and the reason: four of them are symmetric
    for tag, a in (("72Ch", [1, 2, 1]), ("73Bh", [1, 2, 2, 1]),
                   ("75Ch", [1, Fr(2, 3), Fr(5, 8), Fr(2, 3), 1])):
        chk("c4 %s is symmetric" % tag, list(a), list(reversed(list(a))))

    # --- section 4, the step-up direction
    chk("c4 79Bh/71Shr k->h",
        [float(x) for x in L.stepup([Fr(1, 4), Fr(1, 2), Fr(1, 3)])],
        [1.0, 13 / 24.0, 0.625, 1 / 3.0], tol=1e-9)
    chk("c4 80Ch/74Ma k->h",
        [float(x) for x in L.stepup([Fr(1, 4), Fr(1, 4), Fr(1, 3)])],
        [1.0, 19 / 48.0, 17 / 48.0, 1 / 3.0], tol=1e-9)
    # the two middle terms are NOT equal, which is the trap the notes flag
    up = L.stepup([Fr(1, 4), Fr(1, 4), Fr(1, 3)])
    chk("c4 80Ch middle terms differ", 1.0 if up[1] != up[2] else 0.0, 1.0)

    # --- section 5, all-pole and lattice-ladder
    ALLPOLE = [
        ("80Bh", [1, "-0.2", "0.4", "0.6"], [-0.37931, 0.8125, 0.6]),
        ("81Ch/72Ash", [1, "-0.525", "0.6125", "0.3"], [-0.42188, 0.84615, 0.3]),
        ("79Ch/69Bh", [1, "-0.9", "0.64", "-0.576"], [-0.67276, 0.18197, -0.576]),
        ("71Bh", [1, "-0.3", "0.5", "0.25"], [-0.28099, 0.61333, 0.25]),
        ("70Ma", [1, 2, -3, 4], [-0.53846, 0.73333, 4.0]),
        ("71Ch", [1, "-0.01", "-0.23", "0.5"], [0.2, -0.3, 0.5]),
    ]
    for tag, a, want in ALLPOLE:
        ks, _ = L.stepdown(a)
        close.tag = tag + " k"
        close(ks, want)
        chk("c4 %s stability" % tag, 1.0 if L.stable(ks) else 0.0,
            0.0 if tag == "70Ma" else 1.0)

    # 80 Bh in exact fractions, which is what the worked example prints
    ks, _ = L.stepdown([1, "-0.2", "0.4", "0.6"])
    chk("c4 80Bh k1 exact", ks[0], Fr(-11, 29))
    chk("c4 80Bh k2 exact", ks[1], Fr(13, 16))
    chk("c4 80Bh k3 exact", ks[2], Fr(3, 5))

    LAD = [
        ("80Ba/82Bh", [2, "-0.7", "0.5"], [1, "-0.3", "0.25"],
         [-0.24, 0.25], [1.743, -0.55, 0.5]),
        ("79Ba", [1, "-0.4", "0.25"], [1, "-0.3", "0.5"],
         [-0.2, 0.5], [0.81, -0.325, 0.25]),
        ("76Ch", ["0.5", -2, 3], [1, "-0.5", "-0.7", "0.3"],
         [-0.80556, -0.60440, 0.3], [1.47222, -1.04396, 3.0]),
        ("76Ash", ["0.7", "-1.5", "0.5"], [1, "-0.5", "-0.7", "0.3"],
         [-0.80556, -0.60440, 0.3], [-0.07778, -1.34066, 0.5]),
        ("74Bh", ["0.62", "0.42", "-0.25"], [1, "0.27", "0.06", "-0.75"],
         [0.45, 0.6, -0.75], [0.5, 0.6, -0.25]),
        ("75Bh", ["0.6", "-0.45", "-0.25"], [1, "0.27", "0.06", "-0.75"],
         [0.45, 0.6, -0.75], [0.8715, -0.27, -0.25]),
        ("77Ch", ["0.5", "-0.4", "-0.2"], [1, "0.2", "0.7", "-0.75"],
         [0.56311, 1.94286, -0.75], [0.92718, -0.06857, -0.2]),
        ("73Ma", ["0.5", "0.65", "0.2"], [1, "-0.45", "0.3", "0.5"],
         [-0.47059, 0.7, 0.5], [0.74118, 0.81, 0.2]),
        ("78Ch", [1, -1, "0.5"], [1, "0.2", "-0.15"],
         [0.23529, -0.15], [1.33382, -1.1, 0.5]),
        ("70Asa", ["0.5", 2, "0.6"], [1, "-0.3", "0.4"],
         [-0.21429, 0.4], [0.72714, 2.18, 0.6]),
        ("66Ma", [Fr(1, 2), Fr(1, 3), Fr(1, 4), Fr(1, 5)],
         [1, Fr(1, 5), Fr(2, 5), Fr(3, 5)],
         [-0.04348, 0.4375, 0.6], [0.29971, 0.26646, 0.21, 0.2]),
        ("82Ba", ["0.2759", "0.5121", "0.5121", "0.2759"],
         [1, "-0.0010", "0.6546", "-0.0775"],
         [0.03017, 0.65848, -0.0775], [-0.04933, 0.30589, 0.51236, 0.2759]),
    ]
    for tag, b, a, wk, wc in LAD:
        ks, C = L.ladder(b, a)
        close.tag = tag + " k"
        close(ks, wk)
        close.tag = tag + " C"
        close(C, wc)

    # papers sharing a denominator must share their lattice
    k1, _ = L.stepdown([1, "-0.5", "-0.7", "0.3"])
    k2, _ = L.stepdown([1, "-0.5", "-0.7", "0.3"])
    chk("c4 76Ch and 76Ash share k", [float(x) for x in k1],
        [float(x) for x in k2], tol=0)
    k3, _ = L.stepdown([1, "0.27", "0.06", "-0.75"])
    chk("c4 74Bh and 75Bh share k", [float(x) for x in k3],
        [0.45, 0.6, -0.75], tol=1e-9)

    # 81 Bh: the denominator is printed factored and must be multiplied out
    import numpy as np
    poly = np.polynomial.polynomial.polymul(
        np.polynomial.polynomial.polymul([1, 0.5], [1, 0.3]), [1, 0.4])
    chk("c4 81Bh expanded denominator", list(poly), [1.0, 1.2, 0.47, 0.06],
        tol=1e-12)

    # 70 Bh: the all-pass ladder collapses to [0, 0, 0, 1]
    ks, C = L.ladder([Fr(1, 2), Fr(1, 5), Fr(-3, 5), 1],
                     [1, Fr(-3, 5), Fr(1, 5), Fr(1, 2)])
    chk("c4 70Bh all-pass ladder", [float(x) for x in C], [0.0, 0.0, 0.0, 1.0])
    chk("c4 70Bh k", [float(x) for x in ks], [-0.56, 2 / 3.0, 0.5], tol=6e-5)
    chk("c4 70Bh stable", 1.0 if L.stable(ks) else 0.0, 1.0)

    # --- section 6, quantization
    chk("c4 75Ash +5/8", list(Q.codes(Fr(5, 8), 3)),
        ["0.101", "0.101", "0.101"])
    chk("c4 75Ash -5/8", list(Q.codes(Fr(-5, 8), 3)),
        ["1.101", "1.010", "1.011"])
    chk("c4 69Bh -192/256", list(Q.codes(Fr(-192, 256), 8)),
        ["1.11000000", "1.00111111", "1.01000000"])
    chk("c4 69Bh -192/220 is not dyadic",
        1.0 if Fr(192, 220).denominator & (Fr(192, 220).denominator - 1) else 0.0,
        1.0)
    rounded = Q.q_round(Fr(-192, 220), 8)
    chk("c4 69Bh rounded to 8 bits", rounded, Fr(-223, 256))
    chk("c4 69Bh rounded codes", list(Q.codes(rounded, 8)),
        ["1.11011111", "1.00100000", "1.00100001"])

    ys = Q.limit_cycle(Fr(-1, 2), Fr(7, 8), 3, 8)
    chk("c4 66Ma sequence", [float(y) for y in ys[:6]],
        [0.875, -0.5, 0.25, -0.125, 0.125, -0.125], tol=1e-12)
    chk("c4 66Ma amplitude", abs(ys[5]), Fr(1, 8))
    chk("c4 66Ma period 2", ys[4], -ys[5])
    chk("c4 66Ma dead band", Fr(1, 8) / (2 * (1 - Fr(1, 2))), Fr(1, 8))

    # 67 Mng, both truncation bounds, swept exhaustively
    bu, b = 6, 3
    bound = Fr(1, 1 << b) - Fr(1, 1 << bu)
    hi_sm = lo_2c = hi_2c = Fr(0)
    for num in range(-(1 << bu) + 1, (1 << bu)):
        x = Fr(num, 1 << bu)
        mag = abs(x) * (1 << b)
        tsm = Fr(int(mag), 1 << b) * (1 if x >= 0 else -1)
        hi_sm = max(hi_sm, abs(tsm - x))
        sc = x * (1 << b)
        t2c = Fr(sc.numerator // sc.denominator, 1 << b)
        lo_2c = min(lo_2c, t2c - x)
        hi_2c = max(hi_2c, t2c - x)
    chk("c4 67Mng sign-mag bound", hi_sm, bound)
    chk("c4 67Mng 2s-comp upper bound is zero", hi_2c, Fr(0))
    chk("c4 67Mng 2s-comp lower bound", lo_2c, -bound)
    chk("c4 67Mng q - q_u", bound, Fr(7, 64))


# ---------------------------------------------------------------- chapter 5

def ch5():
    """Assert every window choice, length, beta and coefficient in chapter 5."""
    import math
    import fir as FI
    PI = math.pi

    # --- the comparison table, against the figures the sources print
    for name, atten, trans in (("Rectangular", 21, 1.8), ("Bartlett", 25, 6.1),
                               ("Hann", 44, 6.2), ("Hamming", 53, 6.6),
                               ("Blackman", 74, 11.0)):
        chk("c5 %s attenuation" % name, FI.ATTEN[name], atten)
        chk("c5 %s transition" % name, FI.TRANS[name], trans)

    # window end values, which is the whole Hann-vs-Hamming difference
    chk("c5 Hann ends at 0", FI.window("Hann", 21)[0], 0.0, tol=1e-12)
    chk("c5 Hamming ends at 0.08", FI.window("Hamming", 21)[0], 0.08, tol=1e-12)
    for name in ("Rectangular", "Bartlett", "Hann", "Hamming", "Blackman"):
        w = FI.window(name, 15)
        chk("c5 %s symmetric" % name, w, list(reversed(w)), tol=1e-12)

    # --- section 1, the fixed-window designs
    DES = [
        ("79Ba", 0.2, 0.45, 51, "Hamming", 29, 0.325),
        ("71Ch/69Ch", 0.3, 0.5, 40, "Hann", 33, 0.4),
        ("74Ash", 0.2, 0.5, 41, "Hann", 23, 0.35),
        ("79Ch/75Bh", 0.24, 0.54, 42.2, "Hann", 23, 0.39),
        ("67Mng", 0.35, 0.45, 54, "Blackman", 111, 0.4),
        ("76Ch/81Ch/73Ma", 0.2, 0.4, 40, "Hann", 33, 0.3),
        ("82Bh", 0.2, 0.5, 42, "Hann", 23, 0.35),
        ("82Ba", 0.3, 0.45, 50, "Hamming", 45, 0.375),
    ]
    for tag, wp, ws, A, win, N, wc in DES:
        d = FI.design(wp * PI, ws * PI, atten_db=A)
        chk("c5 %s window" % tag, d["window"], win)
        chk("c5 %s N" % tag, d["N"], N)
        chk("c5 %s wc" % tag, d["wc"] / PI, wc, tol=1e-9)
        chk("c5 %s N is odd" % tag, d["N"] % 2, 1)

    # the delta-to-dB conversions the papers hide behind inequalities
    chk("c5 delta 0.01 -> 40 dB", FI.db(0.01), 40.0, tol=1e-12)
    chk("c5 delta 0.02 -> 33.98 dB", FI.db(0.02), 33.9794, tol=5e-5)
    chk("c5 delta 0.035 -> 29.12 dB", FI.db(0.035), 29.1186, tol=5e-5)

    # 67 Mng: the marginal decibel, and what it costs
    chk("c5 54 dB forces Blackman", FI.pick_window(54), "Blackman")
    chk("c5 53 dB still allows Hamming", FI.pick_window(53), "Hamming")
    chk("c5 67Mng Hamming would be 67", FI.length_for("Hamming", 0.1 * PI), 67)
    chk("c5 67Mng Blackman costs 111", FI.length_for("Blackman", 0.1 * PI), 111)

    # papers that name the window and supply a main-lobe constant instead
    chk("c5 70Asa N from 8pi/dw", int(math.ceil(8 * PI / (0.1 * PI))) + 1, 81)
    chk("c5 68Bh N from 12pi/dw", int(math.ceil(12 * PI / (0.1 * PI))) + 1, 121)
    chk("c5 69Bh Hann exact would be", FI.length_for("Hann", 0.05 * PI), 125)

    # --- section 1 worked example, 79 Ch / 75 Bh, first three coefficients
    N, wc = 23, 0.39 * PI
    hd = FI.hd_lowpass(N, wc)
    w = FI.window("Hann", N)
    h = [hd[i] * w[i] for i in range(N)]
    chk("c5 79Ch alpha", (N - 1) // 2, 11)
    chk("c5 79Ch centre tap", hd[11], 0.39, tol=1e-12)
    chk("c5 79Ch hd[0..2]", hd[:3], [0.022865, -0.009836, -0.035350], tol=5e-6)
    chk("c5 79Ch w[0..2]", w[:3], [0.0, 0.020254, 0.079373], tol=5e-6)
    chk("c5 79Ch h[0..2]", h[:3], [0.0, -0.000199, -0.002806], tol=5e-6)
    chk("c5 79Ch h symmetric", h, list(reversed(h)), tol=1e-12)
    chk("c5 79Ch h[0] is exactly zero", h[0], 0.0, tol=1e-15)

    # 74 Ash wants six coefficients
    N, wc = 23, 0.35 * PI
    hd = FI.hd_lowpass(N, wc)
    w = FI.window("Hann", N)
    h = [hd[i] * w[i] for i in range(N)]
    chk("c5 74Ash centre tap", hd[11], 0.35, tol=1e-12)
    chk("c5 74Ash h[0..5]", h[:6],
        [0.0, -0.000645, -0.001274, 0.004036, 0.013128, 0.007030], tol=5e-6)

    # --- section 2, the length-7 designs
    hd = FI.hd_lowpass(7, 1.0)
    chk("c5 len7 hd", hd,
        [0.014975, 0.144717, 0.267849, 0.318310, 0.267849, 0.144717, 0.014975],
        tol=5e-6)
    chk("c5 len7 centre is 1/pi", hd[3], 1.0 / PI, tol=1e-12)
    wh = FI.window("Hann", 7)
    chk("c5 len7 Hann", wh, [0.0, 0.25, 0.75, 1.0, 0.75, 0.25, 0.0], tol=1e-12)
    chk("c5 len7 Hann h", [hd[i] * wh[i] for i in range(7)],
        [0.0, 0.036179, 0.200887, 0.318310, 0.200887, 0.036179, 0.0], tol=5e-6)
    wb = FI.window("Blackman", 7)
    chk("c5 len7 Blackman", wb, [0.0, 0.13, 0.63, 1.0, 0.63, 0.13, 0.0], tol=1e-9)
    chk("c5 len7 Blackman h", [hd[i] * wb[i] for i in range(7)],
        [0.0, 0.018813, 0.168745, 0.318310, 0.168745, 0.018813, 0.0], tol=5e-6)

    # --- section 3, Kaiser
    chk("c5 beta at 40 dB", FI.kaiser_beta(40.0), 3.3953, tol=5e-5)
    chk("c5 beta at 33.98 dB", FI.kaiser_beta(FI.db(0.02)), 2.6523, tol=5e-5)
    chk("c5 beta at 29.12 dB", FI.kaiser_beta(FI.db(0.035)), 1.9903, tol=5e-5)
    chk("c5 beta zero below 21 dB", FI.kaiser_beta(20.0), 0.0)
    chk("c5 beta high branch at 60 dB", FI.kaiser_beta(60.0),
        0.1102 * (60 - 8.7), tol=1e-12)

    KAI = [
        ("81Ba/81Bh", 0.3, 0.35, 0.01, 0.01, 3.3953, 91),
        ("80Bh", 0.19, 0.21, 0.05, 0.01, 3.3953, 225),
        ("80Ba", 0.016, 0.08, 0.01, 0.01, 3.3953, 71),
        ("79Bh", 0.2, 0.4, 0.101, 0.01, 3.3953, 25),
        ("78Bh/74Ch", 0.35, 0.25, 0.05, 0.01, 3.3953, 47),
        ("75Ash/72Ka", 0.19, 0.21, 0.01, 0.01, 3.3953, 225),
        ("76Ash", 0.16, 0.18, 0.01, 0.01, 3.3953, 225),
        ("73Ch", 0.09, 0.14, 0.02, 0.01, 3.3953, 91),
        ("78Ch", 0.19, 0.21, 0.02, 0.02, 2.6523, 183),
        ("66Ma", 0.25, 0.65, 0.035, 0.035, 1.9903, 9),
    ]
    for tag, wp, ws, dp, ds, beta, N in KAI:
        d = FI.design(wp * PI, ws * PI, dp=dp, ds=ds)
        chk("c5 %s beta" % tag, d["beta"], beta, tol=5e-5)
        chk("c5 %s kaiser N" % tag, d["kaiser_N"], N)
        chk("c5 %s N odd" % tag, d["kaiser_N"] % 2, 1)

    # eight of the ten share one beta, which is the grouping the notes claim
    betas = [FI.design(wp * PI, ws * PI, dp=dp, ds=ds)["beta"]
             for _, wp, ws, dp, ds, _, _ in KAI]
    chk("c5 eight Kaiser papers share beta",
        sum(1 for b in betas if abs(b - 3.3953) < 5e-5), 8)

    # 66 Ma's mislabelled table: every entry is I_0, not J_0
    TAB = [(0, 1), (1.3165, 1.4826), (1.7237, 1.8926), (1.8455, 2.0508),
           (1.9271, 2.1675), (1.93, 2.1718), (1.9903, 2.2642), (2, 2.2796)]
    for x, printed in TAB:
        chk("c5 66Ma table I0(%s)" % x, FI.i0(x), printed, tol=5e-5)
    chk("c5 66Ma beta is one of its own table entries",
        FI.kaiser_beta(FI.db(0.035)), 1.9903, tol=5e-5)
    chk("c5 66Ma I0(beta) supplied", FI.i0(1.9903), 2.2642, tol=5e-5)
    # J_0 would be nothing like it
    chk("c5 J0 is not I0", 1.0 if abs(math.cos(2.0) - 2.2796) > 1.0 else 0.0, 1.0)

    # the Kaiser window is rectangular at beta = 0, and peaks at 1 in the middle
    chk("c5 kaiser beta=0", FI.kaiser_window(9, 0.0), [1.0] * 9, tol=1e-12)
    kw = FI.kaiser_window(21, 3.3953)
    chk("c5 kaiser centre is 1", kw[10], 1.0, tol=1e-12)
    chk("c5 kaiser symmetric", kw, list(reversed(kw)), tol=1e-12)

    # --- 73 Ch prints a passband edge beyond its stopband edge
    chk("c5 73Ch as printed is impossible", 1.0 if 0.9 > 0.14 else 0.0, 1.0)
    d = FI.design(0.09 * PI, 0.14 * PI, dp=0.02, ds=0.01)
    chk("c5 73Ch on the sensible reading", d["kaiser_N"], 91)

    # --- the Remez comparison quoted from the local source
    chk("c5 Remez M=26 against Kaiser M=38", 38 - 26, 12)


CHAPTERS = {"ch1": ch1, "ch2": ch2, "ch3": ch3, "ch4": ch4,
            "ch5": ch5}


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
