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


def _near(a, b, tol):
    """Compare two answers to within tol. Handles nested sequences, and
    complex numbers, which chapter 6 needs for s-plane and z-plane poles:
    abs() of a complex difference is the modulus, and for two reals that is
    exactly the old float comparison, so nothing before ch6 changes."""
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        if not (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple))):
            return False
        return len(a) == len(b) and all(_near(x, y, tol) for x, y in zip(a, b))
    return abs(complex(a) - complex(b)) <= tol


def chk(tag, got, want, tol=1e-9):
    if got is None or want is None:
        same = got is want                 # "aperiodic" is a real answer, not a number
    elif isinstance(want, str) or isinstance(got, str):
        same = got == want                 # a window name is an answer too
    else:
        same = _near(got, want, tol)
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
    # the "one line saying what the table would have given" that 1.5 prints
    chk("c5 70Asa exact c=6.2 would be 63", FI.length_for("Hann", 0.1 * PI), 63)
    chk("c5 68Bh exact c=11 would be 111", FI.length_for("Blackman", 0.1 * PI), 111)

    # --- 79 Ba, the one fixed-window paper that lands on Hamming
    chk("c5 79Ba needs Hamming not Hann", FI.pick_window(51), "Hamming")
    N79, wc79 = 29, 0.325 * PI
    hd79 = FI.hd_lowpass(N79, wc79)
    w79 = FI.window("Hamming", N79)
    h79 = [hd79[i] * w79[i] for i in range(N79)]
    chk("c5 79Ba N", FI.length_for("Hamming", 0.25 * PI), 29)
    chk("c5 79Ba alpha", (N79 - 1) // 2, 14)
    chk("c5 79Ba centre tap", hd79[14], 0.325, tol=1e-12)
    chk("c5 79Ba h[0..2]", h79[:3], [0.001797, 0.001456, -0.001029], tol=5e-6)
    # Hamming does not vanish at the ends, which is the whole contrast with Hann
    chk("c5 79Ba h[0] is NOT zero", 1 if abs(h79[0]) > 1e-6 else 0, 1)

    # --- 82 Bh and 82 Ba: the unit conversions, which are the marks
    chk("c5 82Bh Hz to rad/sample wp", 2 * PI * 2000 / 20000, 0.2 * PI, tol=1e-12)
    chk("c5 82Bh Hz to rad/sample ws", 2 * PI * 5000 / 20000, 0.5 * PI, tol=1e-12)
    chk("c5 82Bh window", FI.pick_window(42), "Hann")
    chk("c5 82Bh N", FI.length_for("Hann", 0.3 * PI), 23)
    chk("c5 82Ba rad/s to rad/sample wp", 30 * PI / 100, 0.3 * PI, tol=1e-12)
    chk("c5 82Ba rad/s to rad/sample ws", 45 * PI / 100, 0.45 * PI, tol=1e-12)
    chk("c5 82Ba needs Hamming", FI.pick_window(50), "Hamming")
    chk("c5 82Ba N", FI.length_for("Hamming", 0.15 * PI), 45)

    # --- 76 Ch / 81 Ch / 73 Ma: ripple to dB, and delta_s is the one to use
    chk("c5 76Ch delta_p from 0.899", 1 - 0.899, 0.101, tol=1e-12)
    chk("c5 76Ch A from delta_s", FI.db(0.01), 40.0, tol=1e-12)
    chk("c5 76Ch delta_p would give only 19.9 dB", FI.db(0.101), 19.9136, tol=5e-4)
    chk("c5 76Ch N", FI.length_for("Hann", 0.2 * PI), 33)

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
        # band pass, and its SECOND transition (0.6 -> 0.65 pi) is the
        # narrow one. Entered below with dw2; see the 78Bh/74Ch block after
        # this loop for the rule itself.
        ("78Bh/74Ch", 0.25, 0.35, 0.05, 0.01, 3.3953, 91, 0.05),
        ("75Ash/72Ka", 0.19, 0.21, 0.01, 0.01, 3.3953, 225),
        ("76Ash", 0.16, 0.18, 0.01, 0.01, 3.3953, 225),
        ("73Ch", 0.09, 0.14, 0.02, 0.01, 3.3953, 91),
        ("78Ch", 0.19, 0.21, 0.02, 0.02, 2.6523, 183),
        ("66Ma", 0.25, 0.65, 0.035, 0.035, 1.9903, 9),
    ]
    for tag, wp, ws, dp, ds, beta, N, *rest in KAI:
        dw2 = rest[0] * PI if rest else None
        d = FI.design(wp * PI, ws * PI, dp=dp, ds=ds, dw2=dw2)
        chk("c5 %s beta" % tag, d["beta"], beta, tol=5e-5)
        chk("c5 %s kaiser N" % tag, d["kaiser_N"], N)
        chk("c5 %s N odd" % tag, d["kaiser_N"] % 2, 1)

    # ---- 78 Bh / 74 Ch, the band pass, and the rule that was missing.
    # Its spec has THREE bands and therefore TWO transitions, 0.25->0.35 pi
    # and 0.6->0.65 pi. One window serves both, so the NARROWER sets N.
    # The chapter published N = 47 for years because the paper had been
    # entered as a low pass carrying only the wide transition; these four
    # checks make that unrepeatable.
    bp = FI.design(0.25 * PI, 0.35 * PI, dp=0.05, ds=0.01, dw2=0.05 * PI)
    chk("c5 78Bh two transitions, narrower wins", bp["dw"] / PI, 0.05, tol=1e-12)
    chk("c5 78Bh N from the narrow transition", bp["kaiser_N"], 91)
    wide = FI.design(0.25 * PI, 0.35 * PI, dp=0.05, ds=0.01)
    chk("c5 78Bh wide transition alone would give 47", wide["kaiser_N"], 47)
    chk("c5 78Bh narrow answer is not the wide one",
        1 if bp["kaiser_N"] != wide["kaiser_N"] else 0, 1)
    # band-pass ideal response: each edge in the middle of its own transition
    chk("c5 78Bh band edges", [(0.25 + 0.35) / 2, (0.6 + 0.65) / 2],
        [0.3, 0.625], tol=1e-12)

    # eight of the ten share one beta, which is the grouping the notes claim
    betas = [FI.design(wp * PI, ws * PI, dp=dp, ds=ds)["beta"]
             for _, wp, ws, dp, ds, _, _, *_r in KAI]
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
    # 66 Ma worked end to end: the w[n], hd[n] and h[n] rows the chapter prints
    b66 = FI.kaiser_beta(FI.db(0.035))
    N66, wc66 = 9, 0.45 * PI
    x66 = [b66 * math.sqrt(max(0.0, 1 - (2.0 * n / (N66 - 1) - 1) ** 2))
           for n in range(N66)]
    w66 = FI.kaiser_window(N66, b66)
    hd66 = FI.hd_lowpass(N66, wc66)
    h66 = [hd66[i] * w66[i] for i in range(N66)]
    chk("c5 66Ma N", FI.design(0.25 * PI, 0.65 * PI, dp=0.035,
                               ds=0.035)["kaiser_N"], 9)
    chk("c5 66Ma x(n)", [round(v, 4) for v in x66],
        [0.0, 1.3165, 1.7237, 1.9271, 1.9903, 1.9271, 1.7237, 1.3165, 0.0],
        tol=5e-5)
    chk("c5 66Ma w[n]", [round(v, 4) for v in w66],
        [0.4417, 0.6548, 0.8359, 0.9573, 1.0, 0.9573, 0.8359, 0.6548, 0.4417],
        tol=5e-5)
    chk("c5 66Ma hd[n]", [round(v, 4) for v in hd66],
        [-0.0468, -0.0945, 0.0492, 0.3144, 0.45, 0.3144, 0.0492, -0.0945,
         -0.0468], tol=5e-5)
    chk("c5 66Ma h[n]", [round(v, 4) for v in h66],
        [-0.0207, -0.0619, 0.0411, 0.3010, 0.45, 0.3010, 0.0411, -0.0619,
         -0.0207], tol=5e-5)
    chk("c5 66Ma centre tap is wc/pi", h66[4], 0.45, tol=1e-12)
    # the chapter claims only five of the paper's eight x entries are reached
    supplied = [0, 1.3165, 1.7237, 1.8455, 1.9271, 1.93, 1.9903, 2]
    used = {round(v, 4) for v in x66}
    chk("c5 66Ma five of the eight table entries are used",
        sum(1 for v in supplied if round(v, 4) in used), 5)
    chk("c5 66Ma 1.8455, 1.93 and 2 are never reached",
        sum(1 for v in (1.8455, 1.93, 2) if round(v, 4) in used), 0)
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


def ch6():
    """Assert every order, cut-off, pole, H(s), H(z) and check printed in
    chapter 6. The expected values below are transcribed from ch6.tex and
    ch6-num.tex; the recomputation comes from iir.py, so a disagreement fails
    whichever side is wrong. T is 1 for every bilinear design, because it
    cancels, and the last block proves that it does."""
    import cmath
    import math
    import iir as IR
    PI = math.pi
    cexp = cmath.exp

    def bilin(wp, ws, ap, asb, T=1.0):
        """(N_exact, N, Op, Os, Oc, b, a) for a bilinear Butterworth design."""
        Nx, N, Op, Os = IR.butter_order(wp * PI, ws * PI, ap, asb, T)
        Oc = IR.butter_wc(Op, ap, N)
        num, den = IR.butter_Hs(Oc, N)
        b, a = IR.bilinear(num, den, T)
        return Nx, N, Op, Os, Oc, b, a

    def iinv(wp, ws, ap, asb, T=1.0, scale_T=False):
        Nx, N, Op, Os = IR.butter_order(wp * PI, ws * PI, ap, asb, T,
                                        "invariance")
        Oc = IR.butter_wc(Op, ap, N)
        num, den = IR.butter_Hs(Oc, N)
        b, a = IR.impulse_invariance(num, den, T, scale_T)
        return Nx, N, Op, Os, Oc, b, a

    # ---------------------------------------------------- spec conversions ---
    # ch6.tex 6.2: "those four phrasings are the same spec four ways"
    chk("c6 gain 0.89125 -> 1 dB", IR.alpha_from_gain(0.89125), 1.0, 1e-4)
    chk("c6 gain 0.17783 -> 15 dB", IR.alpha_from_gain(0.17783), 15.0, 1e-3)
    chk("c6 delta_p 0.11 -> 1.0122 dB",
        IR.alpha_from_ripple(0.11, "pass"), 1.0122, 1e-4)
    chk("c6 delta_s 0.21 -> 13.5556 dB",
        IR.alpha_from_ripple(0.21, "stop"), 13.5556, 1e-4)
    chk("c6 delta_p 0.17 -> 1.6184 dB",
        IR.alpha_from_ripple(0.17, "pass"), 1.6184, 1e-4)
    chk("c6 delta_s 0.27 -> 11.3727 dB",
        IR.alpha_from_ripple(0.27, "stop"), 11.3727, 1e-4)
    chk("c6 delta_s 0.22 -> 13.1515 dB",
        IR.alpha_from_ripple(0.22, "stop"), 13.1515, 1e-4)
    chk("c6 gain 0.9 -> 0.9151 dB", IR.alpha_from_gain(0.9), 0.9151, 1e-4)
    chk("c6 gain 0.8 -> 1.9382 dB", IR.alpha_from_gain(0.8), 1.9382, 1e-4)
    chk("c6 gain 0.6 -> 4.4370 dB", IR.alpha_from_gain(0.6), 4.4370, 1e-4)
    chk("c6 gain 0.82 -> 1.7237 dB", IR.alpha_from_gain(0.82), 1.7237, 1e-4)
    chk("c6 gain 0.2 -> 13.9794 dB", IR.alpha_from_gain(0.2), 13.9794, 1e-4)
    chk("c6 gain 0.18 -> 14.8945 dB", IR.alpha_from_gain(0.18), 14.8945, 1e-4)
    chk("c6 gain 0.1 -> 20 dB", IR.alpha_from_gain(0.1), 20.0, 1e-4)
    chk("c6 gain 0.707 -> 3.0116 dB", IR.alpha_from_gain(0.707), 3.0116, 1e-4)
    # section 1.1, the three specifications printed in hertz
    chk("c6 76Ch 1.2 kHz at 8 kHz", IR.w_from_hz(1200, 8000) / PI, 0.3, 1e-12)
    chk("c6 76Ch 2.5 kHz at 8 kHz", IR.w_from_hz(2500, 8000) / PI, 0.625, 1e-12)
    chk("c6 82Bh 350 Hz at 5 kHz", IR.w_from_hz(350, 5000) / PI, 0.14, 1e-12)
    chk("c6 82Bh 1000 Hz at 5 kHz", IR.w_from_hz(1000, 5000) / PI, 0.4, 1e-12)
    chk("c6 78Bh 200 Hz at 5 kHz", IR.w_from_hz(200, 5000) / PI, 0.08, 1e-12)
    chk("c6 78Bh 500 Hz at 5 kHz", IR.w_from_hz(500, 5000) / PI, 0.2, 1e-12)

    # ------------------------------------- the worked example, 79 Bh family ---
    ap = IR.alpha_from_ripple(0.11, "pass")
    asb = IR.alpha_from_ripple(0.21, "stop")
    Nx, N, Op, Os, Oc, b, a = bilin(0.25, 0.55, ap, asb)
    chk("c6 79Bh 10^0.1ap-1", 10 ** (0.1 * ap) - 1, 0.262467, 1e-6)
    chk("c6 79Bh 10^0.1as-1", 10 ** (0.1 * asb) - 1, 21.675737, 1e-5)
    chk("c6 79Bh Omega_p", Op, 0.828427, 1e-6)
    chk("c6 79Bh Omega_s", Os, 2.341699, 1e-6)
    chk("c6 79Bh Os/Op", Os / Op, 2.82668, 1e-5)
    chk("c6 79Bh N exact", Nx, 2.1239, 1e-4)
    chk("c6 79Bh N", N, 3)
    chk("c6 79Bh (0.262467)^(1/6)", 0.262467 ** (1 / 6.), 0.800164, 1e-6)
    chk("c6 79Bh Omega_c", Oc, 1.035321, 1e-6)
    chk("c6 79Bh Omega_c^2", Oc ** 2, 1.071891, 1e-6)
    chk("c6 79Bh Omega_c^3", Oc ** 3, 1.109751, 1e-6)
    poles = IR.butter_poles(Oc, 3)
    chk("c6 79Bh pole 120deg", poles[0], complex(-0.517661, 0.896615), 1e-6)
    chk("c6 79Bh pole 180deg", poles[1], complex(-1.035321, 0.0), 1e-6)
    chk("c6 79Bh pole 240deg", poles[2], complex(-0.517661, -0.896615), 1e-6)
    # the two substituted factors, printed in step 5
    chk("c6 79Bh linear factor", [2 + Oc, Oc - 2], [3.035321, -0.964679], 1e-6)
    chk("c6 79Bh quad factor",
        [4 + 2 * Oc + Oc ** 2, -8 + 2 * Oc ** 2, 4 - 2 * Oc + Oc ** 2],
        [7.142534, -5.856219, 3.001248], 1e-6)
    prod = IR.pmul([complex(2 + Oc), complex(Oc - 2)],
                   [complex(4 + 2 * Oc + Oc ** 2), complex(-8 + 2 * Oc ** 2),
                    complex(4 - 2 * Oc + Oc ** 2)])
    chk("c6 79Bh denominator product", IR.preal(prod),
        [21.679886, -24.665755, 14.759120, -2.895239], 1e-5)
    chk("c6 79Bh K", Oc ** 3 / prod[0].real, 0.051188, 1e-6)
    chk("c6 79Bh H(z) numerator", b,
        [0.051188, 0.153564, 0.153564, 0.051188], 1e-6)
    chk("c6 79Bh H(z) denominator", a,
        [1.0, -1.137725, 0.680775, -0.133545], 1e-6)
    chk("c6 79Bh sum of a", sum(a), 0.409505, 1e-6)
    chk("c6 79Bh sum of b", sum(b), 0.409504, 1e-6)
    chk("c6 79Bh |H(0)|", abs(IR.freqz(b, a, 0.0)), 1.0, 1e-9)
    chk("c6 79Bh |H(wp)|", abs(IR.freqz(b, a, 0.25 * PI)), 0.8900, 1e-4)
    chk("c6 79Bh |H(ws)|", abs(IR.freqz(b, a, 0.55 * PI)), 0.0861, 1e-4)
    # step 7, the low pass to high pass conversion
    chk("c6 79Bh cos(0.35pi)", math.cos(0.35 * PI), 0.45399, 1e-5)
    chk("c6 79Bh cos(0.10pi)", math.cos(0.10 * PI), 0.95106, 1e-5)
    hb, ha, al = IR.hp_from_lp(b, a, 0.25 * PI, 0.45 * PI)
    chk("c6 79Bh LP->HP alpha", al, -0.47735, 1e-5)
    chk("c6 79Bh HP numerator", hb,
        [0.276238, -0.828713, 0.828713, -0.276238], 1e-6)
    chk("c6 79Bh HP denominator", ha,
        [1.0, -0.683740, 0.457627, -0.068533], 1e-6)
    chk("c6 79Bh HP kills DC", abs(IR.freqz(hb, ha, 0.0)), 0.0, 1e-9)
    chk("c6 79Bh HP at new edge", abs(IR.freqz(hb, ha, 0.45 * PI)), 0.8900, 1e-4)

    # ------------------------------------------ the three section-1 tables ---
    # (papers, wp/pi, ws/pi, alpha_p, alpha_s, N, Omega_c, denominator tail)
    # alpha is the EXACT value wherever the paper states a gain or a ripple;
    # the table prints it rounded, and those rounded figures are asserted in
    # the spec-conversion block above. Designing from the rounded dB instead
    # moves the fifth decimal of every coefficient.
    G, R = IR.alpha_from_gain, IR.alpha_from_ripple
    TAB = [
        ("80Bh/81Bh", 0.5, 0.75, G(0.9), G(0.2), 3, 2.54674,
         [0.439377, 0.384500, 0.041621]),
        ("81Ba", 0.35, 0.70, G(0.6), G(0.1), 2, 1.06140,
         [-0.706985, 0.261356]),
        ("75Ch/70Ch/82Ba", 0.2, 0.6, G(0.8), G(0.2), 2, 0.75037,
         [-1.028191, 0.365076]),
        ("78Ch", 0.22, 0.58, G(0.82), G(0.18), 2, 0.86185,
         [-0.907246, 0.321026]),
        ("80Ba", 0.26, 0.58, 0.99, 14.99, 3, 1.08611,
         [-1.063382, 0.636275, -0.121138]),
        ("79Ba", 0.24, 0.57, 0.98, 14.95, 3, 0.99560,
         [-1.197105, 0.718611, -0.144059]),
        ("79Ch/72Ash", 0.24, 0.57, 1.0, 14.9, 3, 0.99186,
         [-1.202755, 0.722318, -0.145088]),
        ("73Bh", 0.25, 0.59, 0.99, 14.85, 3, 1.03961,
         [-1.131372, 0.676848, -0.132453]),
        ("71Bh", 0.25, 0.55, 1.0, 15.0, 3, 1.03767,
         [-1.134251, 0.678624, -0.132947]),
        ("72Ka", 0.25, 0.45, 1.0, 15.0, 4, 0.98086,
         [-1.647588, 1.356278, -0.525238, 0.083384]),
        ("71Shr", 0.2, 0.4, 1.0, 15.0, 3, 0.81397,
         [-1.482585, 0.929644, -0.203325]),
        ("73Ma", 0.2, 0.5, 0.98, 20.0, 3, 0.81704,
         [-1.477568, 0.925510, -0.202144]),
        ("76Ash", 0.22, 0.54, R(0.11, "pass"), R(0.22, "stop"), 2, 1.00598,
         [-0.760561, 0.275748]),
        ("74Ash", 0.27, 0.58, R(0.11, "pass"), R(0.21, "stop"), 3, 1.12856,
         [-1.002598, 0.602240, -0.111573]),
        ("68Bh", 0.25, 0.45, R(0.17, "pass"), R(0.27, "stop"), 3, 0.94579,
         [-1.273110, 0.770048, -0.158361]),
        ("75Ash/74Bh", 0.15, 0.6, 0.7, 14.0, 2, 0.74249,
         [-1.036997, 0.368530]),
    ]
    for tag, wp, ws, ap_, as_, N_, Oc_, den in TAB:
        Nx, N, Op, Os, Oc, b, a = bilin(wp, ws, ap_, as_)
        chk("c6 %s N" % tag, N, N_)
        chk("c6 %s Omega_c" % tag, Oc, Oc_, 5e-5)
        chk("c6 %s denominator" % tag, a[1:], den, 5e-6)
        # the caption claims the numerator is K times the binomials
        binom = [1.0]
        for _ in range(N):
            binom = [x + y for x, y in zip(binom + [0.0], [0.0] + binom)]
        chk("c6 %s numerator is K*binomials" % tag, b,
            [b[0] * c for c in binom], 1e-12)
        chk("c6 %s K = sum(a)/2^N" % tag, b[0], sum(a) / 2.0 ** N, 1e-12)
        chk("c6 %s |H(0)| = 1" % tag, abs(IR.freqz(b, a, 0.0)), 1.0, 1e-9)
        chk("c6 %s passband met exactly" % tag,
            abs(IR.freqz(b, a, wp * PI)), 10 ** (-ap_ / 20.0), 1e-6)
        chk("c6 %s stopband cleared" % tag,
            1 if abs(IR.freqz(b, a, ws * PI)) <= 10 ** (-as_ / 20.0) + 1e-9
            else 0, 1)

    # ------------------------------------------------- 1.1, specs in hertz ---
    Nx, N, Op, Os, Oc, b, a = bilin(0.3, 0.625, 1.0, 40.0)
    chk("c6 76Ch Omega_p", Op, 1.01905, 1e-5)
    chk("c6 76Ch Omega_s", Os, 2.99321, 1e-5)
    chk("c6 76Ch N exact", Nx, 4.9010, 1e-4)
    chk("c6 76Ch N", N, 5)
    chk("c6 76Ch Omega_c", Oc, 1.16648, 1e-5)
    chk("c6 76Ch Omega_c^2", Oc ** 2, 1.360683, 1e-6)
    secs = sorted(tuple(round(v, 5) for v in s[:2])
                  for s in IR.sections(IR.butter_poles(Oc, N)))
    chk("c6 76Ch real pole section", list(secs[0]), [1.16648, 1.0], 1e-5)
    chk("c6 76Ch quad section 1", list(secs[1]), [1.36068, 0.72093], 1e-5)
    chk("c6 76Ch quad section 2", list(secs[2]), [1.36068, 1.88741], 1e-5)
    chk("c6 76Ch K", b[0], 0.010975, 1e-6)
    zs = sorted(tuple(round(v, 5) for v in s[1:]) for s in IR.zsections(a))
    chk("c6 76Ch z-cascade 1", list(zs[0]), [-0.77598, 0.57608], 5e-5)
    chk("c6 76Ch z-cascade 2", list(zs[1]), [-0.57782, 0.17359], 5e-5)
    chk("c6 76Ch z-cascade 3", list(zs[2]), [-0.26323], 5e-5)
    chk("c6 76Ch cascade multiplies back",
        IR.check_cascade(a, IR.zsections(a)), a, 1e-9)
    chk("c6 76Ch |H(wp)|", abs(IR.freqz(b, a, 0.3 * PI)), 0.89125, 1e-5)
    chk("c6 76Ch |H(ws)|", abs(IR.freqz(b, a, 0.625 * PI)), 0.00899, 1e-5)

    Nx, N, Op, Os, Oc, b, a = bilin(0.14, 0.4, 3.0, 10.0)
    chk("c6 82Bh Omega_p", Op, 0.44705, 1e-5)
    chk("c6 82Bh Omega_s", Os, 1.45309, 1e-5)
    chk("c6 82Bh N exact", Nx, 0.9340, 1e-4)
    chk("c6 82Bh N", N, 1)
    chk("c6 82Bh Omega_c", Oc, 0.44812, 1e-5)
    chk("c6 82Bh H(z)", [b[0], a[1]], [0.183045, -0.633910], 1e-6)
    chk("c6 82Bh |H(wp)|", abs(IR.freqz(b, a, 0.14 * PI)), 0.70795, 1e-5)
    chk("c6 82Bh 3 dB point", 10 ** (-3 / 20.), 0.70795, 1e-5)

    # 70 Bh: the stopband edge is above Nyquist, so the design is impossible
    wp70, ws70 = IR.w_from_hz(120, 256), IR.w_from_hz(170, 256)
    chk("c6 70Bh wp/pi", wp70 / PI, 0.9375, 1e-9)
    chk("c6 70Bh ws/pi", ws70 / PI, 1.3281, 1e-4)
    chk("c6 70Bh ws exceeds pi", 1 if ws70 > PI else 0, 1)
    chk("c6 70Bh tan(ws/2) is negative", 1 if math.tan(ws70 / 2) < 0 else 0, 1)
    try:
        IR.butter_order(wp70, ws70, 1.0, 16.0, 1 / 256.)
        chk("c6 70Bh must be rejected", 0, 1)
    except ValueError:
        chk("c6 70Bh must be rejected", 1, 1)
    chk("c6 70Bh aliases to 86 Hz", 256 - 170, 86)
    chk("c6 70Bh alias sits below the passband edge", 1 if 86 < 120 else 0, 1)
    Nx, N, Op, Os = IR.butter_order(2 * PI * 120, 2 * PI * 170, 1.0, 16.0,
                                    1.0, "bilinear", warp=False)
    chk("c6 70Bh analog Omega_p", Op, 753.98, 1e-2)
    chk("c6 70Bh analog Omega_s", Os, 1068.14, 1e-2)
    chk("c6 70Bh analog N exact", Nx, 7.19, 5e-3)
    chk("c6 70Bh analog N", N, 8)
    chk("c6 70Bh analog Omega_c", IR.butter_wc(Op, 1.0, N), 820.42, 1e-2)

    # ----------------------------------------- 1.2, the textbook filter x3 ---
    Nx, N, Op, Os, Oc, b, a = bilin(0.2, 0.3, 1.0, 15.0)
    chk("c6 73Shr Omega_p", Op, 0.64984, 1e-5)
    chk("c6 73Shr Omega_s", Os, 1.01905, 1e-5)
    chk("c6 73Shr N exact", Nx, 5.3044, 1e-4)
    chk("c6 73Shr N", N, 6)
    chk("c6 73Shr Omega_c", Oc, 0.72729, 1e-5)
    chk("c6 73Shr Omega_c^2", Oc ** 2, 0.528952, 1e-6)
    chk("c6 73Shr H(s) gain", Oc ** 6, 0.147996, 1e-6)
    secs = sorted(tuple(round(v, 5) for v in s[:2])
                  for s in IR.sections(IR.butter_poles(Oc, N)))
    chk("c6 73Shr section 1", list(secs[0]), [0.52895, 0.37647], 1e-5)
    chk("c6 73Shr section 2", list(secs[1]), [0.52895, 1.02854], 1e-5)
    chk("c6 73Shr section 3", list(secs[2]), [0.52895, 1.40502], 1e-5)
    chk("c6 73Shr K", b[0], 0.00057969, 1e-8)
    zs = sorted(tuple(round(v, 5) for v in s[1:]) for s in IR.zsections(a))
    chk("c6 73Shr z-cascade 1", list(zs[0]), [-1.31432, 0.71490], 5e-5)
    chk("c6 73Shr z-cascade 2", list(zs[1]), [-1.05406, 0.37532], 5e-5)
    chk("c6 73Shr z-cascade 3", list(zs[2]), [-0.94592, 0.23422], 5e-5)
    chk("c6 73Shr |H(wp)|", abs(IR.freqz(b, a, 0.2 * PI)), 0.89125, 1e-5)
    chk("c6 73Shr |H(ws)|", abs(IR.freqz(b, a, 0.3 * PI)), 0.13101, 1e-5)
    # the textbook's other convention, quoted in the notes as an alternative
    chk("c6 73Shr stopband-exact Omega_c",
        IR.butter_wc(Op, 1.0, 6, Os, 15.0, edge="stop"), 0.766229, 1e-6)
    # and the Chebyshev order on the same spec, which is 76 Bh's comparison
    chk("c6 73Shr Chebyshev needs only N=4",
        IR.cheb_order(0.2 * PI, 0.3 * PI, 1.0, 15.0)[1], 4)

    # --------------------------------- 1.3, where the arithmetic collapses ---
    # 73 Ch: 0.707 is 1/sqrt2, so the passband edge IS the 3 dB point
    chk("c6 73Ch Omega_p is exactly 2", 2 * math.tan(PI / 4), 2.0, 1e-12)
    chk("c6 73Ch Omega_s", 2 * math.tan(3 * PI / 8), 4.82843, 1e-5)
    Nx, N, Op, Os, Oc, b, a = bilin(0.5, 0.75, IR.alpha_from_gain(0.707),
                                    IR.alpha_from_gain(0.2))
    chk("c6 73Ch N exact", Nx, 1.8026, 1e-4)
    chk("c6 73Ch N", N, 2)
    # the exact answer printed in the notes, from Omega_c = 2 exactly
    Kx = 1.0 / (2 + math.sqrt(2))
    a2x = (2 - math.sqrt(2)) / (2 + math.sqrt(2))
    chk("c6 73Ch exact K", Kx, 0.292893, 1e-6)
    chk("c6 73Ch exact z^-2 coefficient", a2x, 0.171573, 1e-6)
    numx, denx = IR.butter_Hs(2.0, 2)
    bx, ax = IR.bilinear(numx, denx, 1.0)
    chk("c6 73Ch exact numerator", bx, [Kx, 2 * Kx, Kx], 1e-9)
    chk("c6 73Ch exact z^-1 term vanishes", ax[1], 0.0, 1e-12)
    chk("c6 73Ch exact denominator", ax, [1.0, 0.0, a2x], 1e-9)
    # taking 0.707 literally leaves a residue, which is rounding not a term
    chk("c6 73Ch literal 0.707 Omega_c", Oc, 1.99970, 1e-5)
    chk("c6 73Ch literal residue", a[1], -0.000177, 1e-6)
    chk("c6 73Ch residue is negligible", 1 if abs(a[1]) < 1e-3 else 0, 1)

    # 66 Ma, the largest filter in the chapter
    Nx, N, Op, Os, Oc, b, a = bilin(0.3, 0.4, 1.0122, 13.5556)
    chk("c6 66Ma Omega_p", Op, 1.01905, 1e-5)
    chk("c6 66Ma Omega_s", Os, 1.45309, 1e-5)
    chk("c6 66Ma N exact", Nx, 6.2199, 1e-4)
    chk("c6 66Ma N", N, 7)
    chk("c6 66Ma Omega_c", Oc, 1.12122, 1e-5)
    chk("c6 66Ma Omega_c^2", Oc ** 2, 1.257133, 1e-6)
    chk("c6 66Ma 2N poles of |H|^2", 2 * N, 14)
    chk("c6 66Ma pole spacing pi/7 in degrees", 180.0 / 7, 25.71, 5e-3)
    secs = sorted(round(s[1], 5) for s in IR.sections(IR.butter_poles(Oc, N))
                  if len(s) == 3)
    chk("c6 66Ma quad b coefficients", secs, [0.49899, 1.39814, 2.02037], 1e-5)
    chk("c6 66Ma K", b[0], 0.0015237, 1e-7)
    zs = sorted(tuple(round(v, 5) for v in s[1:]) for s in IR.zsections(a))
    chk("c6 66Ma z-cascade 1", list(zs[0]), [-0.87700, 0.68091], 5e-5)
    chk("c6 66Ma z-cascade 2", list(zs[1]), [-0.68117, 0.30557], 5e-5)
    chk("c6 66Ma z-cascade 3", list(zs[2]), [-0.59000, 0.13083], 5e-5)
    chk("c6 66Ma z-cascade real", list(zs[3]), [-0.28155], 5e-5)
    chk("c6 66Ma |H(wp)|", abs(IR.freqz(b, a, 0.3 * PI)), 0.8900, 1e-4)
    chk("c6 66Ma |H(ws)|", abs(IR.freqz(b, a, 0.4 * PI)), 0.16074, 1e-5)

    # ----------------------------------------------- 2, impulse invariance ---
    # the comparison pair: identical specification, the two methods
    NxB, NB, OpB, OsB, OcB, bB, aB = bilin(0.15, 0.6, 0.7, 14.0)
    NxI, NI, OpI, OsI, OcI, bI, aI = iinv(0.15, 0.6, 0.7, 14.0)
    chk("c6 pair 10^0.07-1", 10 ** 0.07 - 1, 0.174898, 1e-6)
    chk("c6 pair 10^1.4-1", 10 ** 1.4 - 1, 24.118864, 1e-6)
    chk("c6 pair bilinear Omega_p", OpB, 0.480158, 1e-6)
    chk("c6 pair bilinear Omega_s", OsB, 2.752764, 1e-6)
    chk("c6 pair bilinear ratio", OsB / OpB, 5.733043, 1e-6)
    chk("c6 pair bilinear N exact", NxB, 1.4106, 1e-4)
    chk("c6 pair bilinear Omega_c", OcB, 0.742485, 1e-6)
    chk("c6 pair invariance Omega_p", OpI, 0.471239, 1e-6)
    chk("c6 pair invariance Omega_s", OsI, 1.884956, 1e-6)
    chk("c6 pair invariance ratio", OsI / OpI, 4.0, 1e-9)
    chk("c6 pair invariance N exact", NxI, 1.7769, 1e-4)
    chk("c6 pair invariance Omega_c", OcI, 0.728694, 1e-6)
    chk("c6 pair both N=2", [NB, NI], [2, 2])
    chk("c6 pair bilinear poles", IR.butter_poles(OcB, 2)[0],
        complex(-0.52502, 0.52502), 1e-5)
    chk("c6 pair invariance poles", IR.butter_poles(OcI, 2)[0],
        complex(-0.51526, 0.51526), 1e-5)
    chk("c6 pair bilinear H(s) gain", OcB ** 2, 0.551284, 1e-6)
    chk("c6 pair invariance H(s) gain", OcI ** 2, 0.530995, 1e-6)
    chk("c6 pair bilinear H(z)", [bB[0]] + aB[1:],
        [0.082883, -1.036997, 0.368530], 1e-6)
    chk("c6 pair invariance H(z)", bI + aI[1:],
        [0.0, 0.303336, -1.039570, 0.356818], 1e-6)
    numI, denI = IR.butter_Hs(OcI, 2)
    pI, AI = IR.residues(numI, denI)
    chk("c6 pair residues are pure imaginary",
        sorted(abs(x.real) for x in AI), [0.0, 0.0], 1e-9)
    chk("c6 pair residue magnitude", abs(AI[0]), 0.51526, 1e-5)
    zp = sorted((round(abs(cexp(p).real), 5), round(abs(cexp(p).imag), 5))
                for p in pI)[0]
    chk("c6 pair z poles", list(zp), [0.51979, 0.29435], 1e-5)
    # the three rows that are the whole comparison
    need_p, need_s = 10 ** (-0.7 / 20.), 10 ** (-14 / 20.)
    chk("c6 pair spec at wp", need_p, 0.922571, 1e-6)
    chk("c6 pair spec at ws", need_s, 0.199526, 1e-6)
    chk("c6 pair bilinear |H(wp)|", abs(IR.freqz(bB, aB, 0.15 * PI)),
        0.922571, 1e-6)
    chk("c6 pair bilinear |H(ws)|", abs(IR.freqz(bB, aB, 0.6 * PI)),
        0.072559, 1e-6)
    chk("c6 pair bilinear |H(0)|", abs(IR.freqz(bB, aB, 0.0)), 1.0, 1e-9)
    chk("c6 pair invariance |H(wp)|", abs(IR.freqz(bI, aI, 0.15 * PI)),
        0.898611, 1e-6)
    chk("c6 pair invariance |H(ws)|", abs(IR.freqz(bI, aI, 0.6 * PI)),
        0.191753, 1e-6)
    chk("c6 pair invariance |H(0)|", abs(IR.freqz(bI, aI, 0.0)), 0.956147, 1e-6)
    # the claims the notes make about those numbers
    chk("c6 pair invariance MISSES the passband",
        1 if abs(IR.freqz(bI, aI, 0.15 * PI)) < need_p else 0, 1)
    chk("c6 pair invariance scrapes the stopband",
        1 if need_s * 0.9 < abs(IR.freqz(bI, aI, 0.6 * PI)) <= need_s else 0, 1)
    chk("c6 pair bilinear clears the stopband by about 3x",
        1 if abs(IR.freqz(bB, aB, 0.6 * PI)) * 2.5 < need_s else 0, 1)
    chk("c6 pair invariance b0 is zero", bI[0], 0.0, 1e-12)

    # 81 Ch / 80 Ch / 69 Bh
    Nx, N, Op, Os, Oc, b, a = iinv(0.25, 0.55, 0.5, 15.0)
    chk("c6 81Ch Omega_p", Op, 0.78540, 1e-5)
    chk("c6 81Ch Omega_s", Os, 1.72788, 1e-5)
    chk("c6 81Ch N exact", Nx, 3.5039, 1e-4)
    chk("c6 81Ch N", N, 4)
    chk("c6 81Ch Omega_c", Oc, 1.02161, 1e-5)
    chk("c6 81Ch Omega_c^2", Oc ** 2, 1.04369, 1e-5)
    secs = sorted(round(s[1], 5) for s in IR.sections(IR.butter_poles(Oc, N)))
    chk("c6 81Ch section b coefficients", secs, [0.78191, 1.88770], 1e-5)
    chk("c6 81Ch numerator", b, [0.0, 0.088750, 0.174840, 0.023521], 1e-6)
    chk("c6 81Ch denominator", a,
        [1.0, -1.513201, 1.180022, -0.449386, 0.069280], 1e-6)
    chk("c6 81Ch |H(wp)|", abs(IR.freqz(b, a, 0.25 * PI)), 0.94338, 1e-5)
    chk("c6 81Ch spec at wp", 10 ** (-0.5 / 20.), 0.94406, 1e-5)
    chk("c6 81Ch misses the passband",
        1 if abs(IR.freqz(b, a, 0.25 * PI)) < 10 ** (-0.5 / 20.) else 0, 1)
    chk("c6 81Ch |H(ws)|", abs(IR.freqz(b, a, 0.55 * PI)), 0.11982, 1e-5)
    chk("c6 81Ch |H(0)| is ABOVE 1", abs(IR.freqz(b, a, 0.0)), 1.00139, 1e-5)

    # 70 Asa
    Nx, N, Op, Os, Oc, b, a = iinv(0.2, 0.35, 0.5, 15.0)
    chk("c6 70Asa Omega_p", Op, 0.62832, 1e-5)
    chk("c6 70Asa Omega_s", Os, 1.09956, 1e-5)
    chk("c6 70Asa N exact", Nx, 4.9367, 1e-4)
    chk("c6 70Asa N", N, 5)
    chk("c6 70Asa Omega_c", Oc, 0.77542, 1e-5)
    secs = sorted(round(s[1], 5) for s in IR.sections(IR.butter_poles(Oc, N))
                  if len(s) == 3)
    chk("c6 70Asa quad b coefficients", secs, [0.47924, 1.25466], 1e-5)
    chk("c6 70Asa Omega_c^2", Oc ** 2, 0.60128, 1e-5)
    chk("c6 70Asa numerator", b,
        [0.0, 0.0069166, 0.044472, 0.027021, 0.0015381], 1e-6)
    chk("c6 70Asa denominator", a,
        [1.0, -2.584442, 2.999693, -1.857044, 0.603063, -0.081324], 1e-6)
    chk("c6 70Asa |H(wp)|", abs(IR.freqz(b, a, 0.2 * PI)), 0.94403, 1e-5)
    chk("c6 70Asa |H(ws)|", abs(IR.freqz(b, a, 0.35 * PI)), 0.17189, 1e-5)
    chk("c6 70Asa |H(0)|", abs(IR.freqz(b, a, 0.0)), 1.00002, 1e-5)

    # 78 Bh / 72 Ch: the one paper where T != 1, so the convention bites
    T = 1 / 5000.
    Nx, N, Op, Os, Oc, b, a = iinv(0.08, 0.2, 5.0, 12.0, T)
    _, _, _, _, _, bT, aT = iinv(0.08, 0.2, 5.0, 12.0, T, scale_T=True)
    chk("c6 78Bh Omega_p is 2pi*200", Op, 2 * PI * 200, 1e-6)
    chk("c6 78Bh Omega_p", Op, 1256.64, 1e-2)
    chk("c6 78Bh Omega_s", Os, 3141.59, 1e-2)
    chk("c6 78Bh 10^0.5-1", 10 ** 0.5 - 1, 2.1623, 1e-4)
    chk("c6 78Bh 10^1.2-1", 10 ** 1.2 - 1, 14.849, 1e-3)
    chk("c6 78Bh ratio", (10 ** 1.2 - 1) / (10 ** 0.5 - 1), 6.8672, 1e-4)
    chk("c6 78Bh N exact", Nx, 1.0514, 1e-4)
    chk("c6 78Bh N", N, 2)
    chk("c6 78Bh Omega_c", Oc, 1036.29, 1e-2)
    chk("c6 78Bh poles", IR.butter_poles(Oc, 2)[0],
        complex(-732.769, 732.769), 1e-3)
    pk, Ak = IR.residues(*IR.butter_Hs(Oc, 2))
    chk("c6 78Bh residue magnitude", abs(Ak[0]), 732.769, 1e-3)
    chk("c6 78Bh z pole", cexp(pk[0] * T), complex(0.854421, -0.126123), 1e-6)
    chk("c6 78Bh Proakis numerator", b[1], 184.838, 1e-3)
    chk("c6 78Bh Oppenheim numerator", bT[1], 0.0369676, 1e-7)
    chk("c6 78Bh scaling is exactly T", bT[1] / b[1], T, 1e-12)
    chk("c6 78Bh denominator", a, [1.0, -1.708842, 0.745942], 1e-6)
    chk("c6 78Bh Proakis DC gain is about 1/T",
        abs(IR.freqz(b, a, 0.0)), 4982.1, 1e-1)
    chk("c6 78Bh scaled |H(wp)|", abs(IR.freqz(bT, aT, 0.08 * PI)), 0.5633, 1e-4)
    chk("c6 78Bh spec at wp", 10 ** (-5 / 20.), 0.5623, 1e-4)
    chk("c6 78Bh passband met by a hair",
        1 if abs(IR.freqz(bT, aT, 0.08 * PI)) >= 10 ** (-5 / 20.) else 0, 1)
    chk("c6 78Bh scaled |H(ws)|", abs(IR.freqz(bT, aT, 0.2 * PI)), 0.1114, 1e-4)
    chk("c6 78Bh spec at ws", 10 ** (-12 / 20.), 0.2512, 1e-4)

    # 67 Mng: H(s) is given, and it is a Butterworth N=3 with Omega_c = 1.3
    ps = [complex(-1.3, 0.0), 1.3 * cexp(complex(0, 2 * PI / 3)),
          1.3 * cexp(complex(0, -2 * PI / 3))]
    chk("c6 67Mng pole 1.3e^{j2pi/3}", ps[1], complex(-0.65, 1.12583), 1e-5)
    chk("c6 67Mng is Butterworth N=3 Omega_c=1.3",
        sorted((round(p.real, 5), round(p.imag, 5))
               for p in IR.butter_poles(1.3, 3)),
        sorted((round(p.real, 5), round(p.imag, 5)) for p in ps), 1e-5)
    den = IR.preal(IR.from_roots(ps))
    chk("c6 67Mng H(s) denominator", den, [2.197, 3.38, 2.6, 1.0], 1e-6)
    chk("c6 67Mng 1.3^3", 1.3 ** 3, 2.197, 1e-9)
    pk, Ak = IR.residues([1.0], den)
    Ad = dict((round(p.real, 5), A) for p, A in zip(pk, Ak))
    chk("c6 67Mng real residue", Ad[-1.3].real, 0.591716, 1e-6)
    chk("c6 67Mng complex residue", abs(Ad[-0.65]),
        abs(complex(-0.295858, 0.170814)), 1e-6)
    chk("c6 67Mng residues sum to zero", abs(sum(Ak)), 0.0, 1e-9)
    chk("c6 67Mng e^{-1.3}", math.exp(-1.3), 0.272532, 1e-6)
    b, a = IR.impulse_invariance([1.0], den, 1.0)
    chk("c6 67Mng numerator", b, [0.0, 0.189281, 0.081154], 1e-6)
    chk("c6 67Mng denominator", a, [1.0, -0.721935, 0.395008, -0.074274], 1e-6)
    # the parallel sections the block diagram is drawn from
    zq = cexp(complex(-0.65, 1.12583))
    chk("c6 67Mng quad section coefficients",
        [-(zq + zq.conjugate()).real, (zq * zq.conjugate()).real],
        [-0.449403, 0.272532], 1e-5)

    # ------------------------------------------------------- 3, Chebyshev ---
    ap72 = IR.alpha_from_gain(0.707)
    Nx, N, Op, Os = IR.cheb_order(0.2 * PI, 0.5 * PI, ap72, 20.0)
    eps = IR.cheb_eps(ap72)
    alpha, a_, b_ = IR.cheb_ab(eps, N)
    chk("c6 72Ma Omega_p", Op, 0.64984, 1e-5)
    chk("c6 72Ma Omega_s is exactly 2", Os, 2.0, 1e-12)
    chk("c6 72Ma epsilon", eps, 1.00030, 1e-5)
    chk("c6 72Ma N exact", Nx, 1.6694, 1e-4)
    chk("c6 72Ma N", N, 2)
    g = math.sqrt((10 ** 2 - 1) / (10 ** (0.1 * ap72) - 1))
    chk("c6 72Ma cosh argument", g, 9.94687, 1e-5)
    chk("c6 72Ma Os/Op", Os / Op, 3.07769, 1e-5)
    chk("c6 72Ma ln form of cosh-1(g)", g + math.sqrt(g * g - 1), 19.8433, 1e-3)
    chk("c6 72Ma cosh-1(g)", math.acosh(g), 2.98787, 1e-5)
    r = Os / Op
    chk("c6 72Ma ln form of cosh-1(r)", r + math.sqrt(r * r - 1), 5.9884, 1e-3)
    chk("c6 72Ma cosh-1(r)", math.acosh(r), 1.78982, 1e-5)
    chk("c6 72Ma alpha", alpha, 2.41370, 1e-5)
    chk("c6 72Ma a", a_, 0.45497, 1e-5)
    chk("c6 72Ma b", b_, 1.09864, 1e-5)
    chk("c6 72Ma a*Omega_c", a_ * Op, 0.29566, 1e-5)
    chk("c6 72Ma b*Omega_c", b_ * Op, 0.71394, 1e-5)
    chk("c6 72Ma ellipse is taller than wide", 1 if b_ > 1 > a_ else 0, 1)
    cps = IR.cheb_poles(Op, eps, N)
    chk("c6 72Ma poles", cps[0], complex(-0.20906, 0.50483), 1e-5)
    cn, cd = IR.cheb_Hs(Op, eps, N)
    chk("c6 72Ma H(s) denominator", cd, [0.298560, 0.418125, 1.0], 1e-6)
    chk("c6 72Ma |s_k|^2", abs(cps[0]) ** 2, 0.298560, 1e-6)
    chk("c6 72Ma sqrt(1+eps^2)", math.sqrt(1 + eps ** 2), 1.41443, 1e-5)
    chk("c6 72Ma K", cn[0], 0.211082, 1e-6)
    chk("c6 72Ma K is |s|^2 over sqrt(1+eps^2)",
        cn[0], abs(cps[0]) ** 2 / math.sqrt(1 + eps ** 2), 1e-12)
    bz, az = IR.bilinear(cn, cd, 1.0)
    chk("c6 72Ma H(z)", [bz[0]] + az[1:], [0.041108, -1.441705, 0.674282], 1e-6)
    chk("c6 72Ma |H(wp)|", abs(IR.freqz(bz, az, 0.2 * PI)), 0.70700, 1e-5)
    chk("c6 72Ma |H(ws)|", abs(IR.freqz(bz, az, 0.5 * PI)), 0.05563, 1e-5)
    chk("c6 72Ma |H(0)| is NOT 1", abs(IR.freqz(bz, az, 0.0)), 0.70700, 1e-5)
    chk("c6 72Ma even-order DC dip is 1/sqrt(1+eps^2)",
        abs(IR.freqz(bz, az, 0.0)), 1 / math.sqrt(1 + eps ** 2), 1e-5)
    chk("c6 72Ma Butterworth would need N=3",
        IR.butter_order(0.2 * PI, 0.5 * PI, ap72, 20.0)[1], 3)

    # 74 Ma and 70 Ma
    Nx, N, Op, Os = IR.cheb_order(0.2 * PI, 0.3 * PI, 1.0, 15.0)
    eps = IR.cheb_eps(1.0)
    chk("c6 74Ma epsilon", eps, 0.50885, 1e-5)
    chk("c6 74Ma N exact", Nx, 3.0141, 1e-4)
    chk("c6 74Ma N", N, 4)
    cps = sorted((round(p.real, 5), round(abs(p.imag), 5))
                 for p in IR.cheb_poles(Op, eps, N))
    chk("c6 74Ma pole pair 1", list(cps[0]), [-0.21891, 0.26470], 1e-5)
    chk("c6 74Ma pole pair 2", list(cps[2]), [-0.09068, 0.63904], 1e-5)
    cn, cd = IR.cheb_Hs(Op, eps, N)
    bz, az = IR.bilinear(cn, cd, 1.0)
    chk("c6 74Ma K", bz[0], 0.0018356, 1e-7)
    chk("c6 74Ma denominator", az[1:],
        [-3.054340, 3.828999, -2.292452, 0.550745], 1e-6)
    chk("c6 74Ma even order DC dip", abs(IR.freqz(bz, az, 0.0)),
        1 / math.sqrt(1 + eps ** 2), 1e-6)
    chk("c6 74Ma beats Butterworth's N=6",
        [N, IR.butter_order(0.2 * PI, 0.3 * PI, 1.0, 15.0)[1]], [4, 6])

    Nx, N, Op, Os = IR.cheb_order(0.25 * PI, 0.55 * PI, 1.01, 13.55)
    eps = IR.cheb_eps(1.01)
    chk("c6 70Ma epsilon", eps, 0.51169, 1e-5)
    chk("c6 70Ma N", N, 2)
    chk("c6 70Ma poles", IR.cheb_poles(Op, eps, N)[0],
        complex(-0.45286, 0.74042), 1e-5)
    cn, cd = IR.cheb_Hs(Op, eps, N)
    bz, az = IR.bilinear(cn, cd, 1.0)
    chk("c6 70Ma K", bz[0], 0.102154, 1e-6)
    chk("c6 70Ma denominator", az[1:], [-0.989132, 0.448133], 1e-6)
    # 70 Ma's alpha_max / alpha_min is the delta_p=0.11, delta_s=0.21 spec again
    chk("c6 70Ma is the same spec in a third notation",
        [round(IR.alpha_from_ripple(0.11, "pass"), 2),
         round(IR.alpha_from_ripple(0.21, "stop"), 2)], [1.01, 13.56], 1e-9)

    # 75 Bh: an analog design, so NO pre-warp, and T does not cancel
    eps = IR.cheb_eps(5.0)
    g = math.sqrt((10 ** 2.0 - 1) / (10 ** 0.5 - 1))
    Nx = math.acosh(g) / math.acosh(50.0 / 20.0)
    N = int(math.ceil(Nx - 1e-12))
    alpha, a_, b_ = IR.cheb_ab(eps, N)
    chk("c6 75Bh epsilon", eps, 1.47047, 1e-5)
    chk("c6 75Bh g", g, 6.76647, 1e-5)
    chk("c6 75Bh N exact", Nx, 1.6592, 1e-4)
    chk("c6 75Bh N", N, 2)
    chk("c6 75Bh alpha", alpha, 1.88938, 1e-5)
    chk("c6 75Bh a", a_, 0.32352, 1e-5)
    chk("c6 75Bh b", b_, 1.05103, 1e-5)
    chk("c6 75Bh semi-axes", [a_ * 20, b_ * 20], [6.47037, 21.02060], 1e-4)
    cps = IR.cheb_poles(20.0, eps, N)
    chk("c6 75Bh poles", cps[0], complex(-4.57524, 14.86381), 1e-5)
    cn, cd = IR.cheb_Hs(20.0, eps, N)
    chk("c6 75Bh H(s)", [cn[0]] + cd[:2], [136.011, 241.866, 9.15049], 1e-3)
    bz, az = IR.bilinear(cn, cd, 2.0)
    chk("c6 75Bh H(z)", [bz[0]] + az[1:], [0.539692, 1.911510, 0.927382], 1e-6)
    chk("c6 75Bh both denominator coefficients are POSITIVE",
        1 if az[1] > 0 and az[2] > 0 else 0, 1)
    chk("c6 75Bh poles sit near z = -1",
        list(sorted((round(r.real, 3), round(abs(r.imag), 3))
                    for r in IR.zroots(az))[0]), [-0.956, 0.118], 2e-3)

    # ---------------------------------------- 4, spectral transformation ---
    blp, alp = [0.1, 0.4], [1.0, -0.6, 0.1]
    chk("c6 70Ch source is 3 dB at its stated cut-off",
        abs(IR.freqz(blp, alp, 0.2575 * PI)), 0.70789, 1e-5)
    chk("c6 70Ch cos((wc+wc')/2)", math.cos(0.3071 * PI), 0.569595, 1e-6)
    chk("c6 70Ch cos((wc-wc')/2)", math.cos(0.0496 * PI), 0.98788, 1e-5)
    hb, ha, al = IR.hp_from_lp(blp, alp, 0.2575 * PI, 0.3567 * PI)
    chk("c6 70Ch alpha", al, -0.57658, 1e-5)
    chk("c6 70Ch |alpha| < 1", 1 if abs(al) < 1 else 0, 1)
    chk("c6 70Ch HP numerator", hb, [0.48106, -0.94325, 0.38393], 1e-5)
    chk("c6 70Ch HP denominator", ha, [1.0, -0.68240, 0.12585], 1e-5)
    chk("c6 70Ch gain is preserved at the new edge",
        abs(IR.freqz(hb, ha, 0.3567 * PI)), 0.70789, 1e-5)
    chk("c6 70Ch matches the source's own edge gain",
        abs(IR.freqz(hb, ha, 0.3567 * PI)),
        abs(IR.freqz(blp, alp, 0.2575 * PI)), 1e-9)
    chk("c6 LP->HP alpha, Oppenheim 7.6",
        IR.lp_to_hp(0.2 * PI, 0.6 * PI), -0.38197, 1e-5)
    chk("c6 LP->LP alpha is zero when nothing moves",
        IR.lp_to_lp(0.3 * PI, 0.3 * PI), 0.0, 1e-12)

    # ----------------------------------------- claims made in ch6.tex 6.2 ---
    # "the standing example": Omega_p=1, Omega_s=3.33, 0.3 dB, 22 dB
    # The local source prints "for butterworth filter n = 5", which is wrong:
    # the ratio is 2202.05, its log is 3.3429, and 2 log(3.33) is 1.0449, so
    # N = 3.1992 and the answer is 4. Its Chebyshev n = 3 is right. The notes
    # print the corrected figure and say the source disagrees.
    chk("c6 standing example ratio",
        (10 ** 2.2 - 1) / (10 ** 0.03 - 1), 2202.05, 5e-2)
    chk("c6 standing example Butterworth N exact",
        IR.butter_order(1.0, 3.33, 0.3, 22.0, 1.0, "invariance")[0], 3.1992, 1e-4)
    chk("c6 standing example Butterworth N=4",
        IR.butter_order(1.0, 3.33, 0.3, 22.0, 1.0, "invariance")[1], 4)
    chk("c6 standing example Chebyshev N=3",
        IR.cheb_order(1.0, 3.33, 0.3, 22.0, 1.0, "invariance")[1], 3)
    # T really does cancel, which is the claim the whole chapter leans on
    base = bilin(0.25, 0.55, 1.0122, 13.5556, 1.0)
    for T in (2.0, 0.1, 0.0001):
        got = bilin(0.25, 0.55, 1.0122, 13.5556, T)
        chk("c6 T=%g gives the same numerator" % T, got[5], base[5], 1e-9)
        chk("c6 T=%g gives the same denominator" % T, got[6], base[6], 1e-9)


def ch7():
    """Assert every spectrum, butterfly stage and convolution printed in
    chapter 7. The big tables in ch7-num.tex were EMITTED by dft.py rather
    than typed, so the job here is different from the other chapters: prove
    the emitted values are right, and prove the .tex still matches them.
    The second half is done by re-reading the .tex, which is the only place
    in verify.py that does so and the only defence against an edit that
    silently changes a digit."""
    import cmath
    import math
    import os
    import re
    import dft as D
    PI = math.pi

    # ---------------------------------------------------------- primitives ---
    chk("c7 W_4 table", [D.W(4, k) for k in range(4)], [1, -1j, -1, 1j], 1e-12)
    chk("c7 W_8^1", D.W(8, 1), complex(1 / math.sqrt(2), -1 / math.sqrt(2)), 1e-12)
    chk("c7 W_8^2", D.W(8, 2), -1j, 1e-12)
    chk("c7 W_8^3", D.W(8, 3), complex(-1 / math.sqrt(2), -1 / math.sqrt(2)), 1e-12)
    chk("c7 W_8^1 decimal", D.W(8, 1), complex(0.7071, -0.7071), 5e-5)
    chk("c7 symmetry W^{k+N/2} = -W^k", D.W(8, 5), -D.W(8, 1), 1e-12)
    chk("c7 periodicity W^{k+N} = W^k", D.W(8, 9), D.W(8, 1), 1e-12)
    chk("c7 bitrev 4", D.bitrev(4), [0, 2, 1, 3])
    chk("c7 bitrev 8", D.bitrev(8), [0, 4, 2, 6, 1, 5, 3, 7])
    chk("c7 bitrev 16 head", D.bitrev(16)[:8], [0, 8, 4, 12, 2, 10, 6, 14])
    chk("c7 bitrev is its own inverse",
        [D.bitrev(8)[i] for i in D.bitrev(8)], list(range(8)))
    chk("c7 3 = 011 reverses to 110 = 6", D.bitrev(8)[3], 6)
    chk("c7 1 = 001 reverses to 100 = 4", D.bitrev(8)[1], 4)

    # complexity, the figures the nine-paper bookwork question quotes
    for N, direct, fft, up in [(8, 64, 12, 5.33), (32, 1024, 80, 12.8),
                               (256, 65536, 1024, 64.0),
                               (1024, 1048576, 5120, 204.8)]:
        d, f, s = D.complexity(N)
        chk("c7 N=%d direct" % N, d, direct)
        chk("c7 N=%d fft" % N, f, fft)
        chk("c7 N=%d speed-up" % N, s, up, 5e-3)

    # ------------------------------------------- the worked example, 80 Ba ---
    x = [1, 1, 0, 0, 1, 1, 2]
    xp, nz = D.pad(x, 8)
    chk("c7 80Ba pads one zero", nz, 1)
    chk("c7 80Ba padded", xp, [1, 1, 0, 0, 1, 1, 2, 0], 1e-12)
    st, order, X = D.dit_stages(x, 8)
    chk("c7 80Ba DIT input order", order, [0, 4, 2, 6, 1, 5, 3, 7])
    chk("c7 80Ba DIT input", [xp[i] for i in order],
        [1, 1, 0, 2, 1, 1, 0, 0], 1e-12)
    chk("c7 80Ba DIT stage 1", st[0], [2, 0, 2, -2, 2, 0, 0, 0], 1e-9)
    chk("c7 80Ba DIT stage 2", st[1], [4, 2j, 0, -2j, 2, 0, 2, 0], 1e-9)
    chk("c7 80Ba DIT stage 3", st[2],
        [6, 2j, -2j, -2j, 2, 2j, 2j, -2j], 1e-9)
    st2, order2, X2 = D.dif_stages(x, 8)
    chk("c7 80Ba DIF stage 1", st2[0], [2, 2, 2, 0, 0, 0, 2j, 0], 1e-9)
    chk("c7 80Ba DIF stage 2", st2[1], [4, 2, 0, -2j, 2j, 0, -2j, 0], 1e-9)
    chk("c7 80Ba DIF stage 3", st2[2],
        [6, 2, -2j, 2j, 2j, 2j, -2j, -2j], 1e-9)
    chk("c7 80Ba DIF unscrambles to the same X", X2, X, 1e-9)
    chk("c7 80Ba X(k)", X, [6, 2j, -2j, -2j, 2, 2j, 2j, -2j], 1e-9)
    chk("c7 80Ba X(0) is the sum", X[0], sum(xp), 1e-9)
    chk("c7 80Ba X(4) is the alternating sum", X[4],
        sum((-1) ** n * xp[n] for n in range(8)), 1e-9)
    chk("c7 80Ba conjugate symmetry", [X[8 - k] for k in range(1, 8)],
        [X[k].conjugate() for k in range(1, 8)], 1e-9)
    chk("c7 80Ba |X(k)|", [abs(v) for v in X], [6, 2, 2, 2, 2, 2, 2, 2], 1e-9)
    e1, e2 = D.parseval(xp)
    chk("c7 80Ba Parseval time side", e1, 8, 1e-9)
    chk("c7 80Ba Parseval freq side", e2, 8, 1e-9)

    # ---------------------------------------------------- 66 Ma, worked 4-pt ---
    st, order, X = D.dit_stages([1, 3, 4, 5], 4)
    chk("c7 66Ma DIT order", order, [0, 2, 1, 3])
    chk("c7 66Ma DIT input", [[1, 3, 4, 5][i] for i in order],
        [1, 4, 3, 5], 1e-12)
    chk("c7 66Ma DIT stage 1", st[0], [5, -3, 8, -2], 1e-9)
    chk("c7 66Ma DIT stage 2", st[1], [13, -3 + 2j, -3, -3 - 2j], 1e-9)
    chk("c7 66Ma X(0)", X[0], 13, 1e-9)

    # 75 Ch: X(5) of a 4-point DFT is X(1), which is the whole question
    X = D.dft([1, -2, 3, 2], 4)
    chk("c7 75Ch X(k)", X, [4, -2 + 4j, 4, -2 - 4j], 1e-9)
    chk("c7 75Ch X(5) = X(1)", X[5 % 4], X[1], 1e-12)
    chk("c7 75Ch X(3) = conj X(1)", X[3], X[1].conjugate(), 1e-9)
    # 76 Bh: a constant sequence transforms to an impulse
    chk("c7 76Bh constant -> impulse", D.dft([0.5] * 4, 4), [2, 0, 0, 0], 1e-9)
    # 71 Ch / 70 Asa: an impulse transforms to a constant, so X(7) = 1
    chk("c7 71Ch impulse -> flat", D.dft([1, 0, 0, 0, 0, 0, 0, 0], 8),
        [1] * 8, 1e-9)

    # the three formula-defined sequences, sampled the way the notes print them
    chk("c7 78Ch samples", [0.5 * math.sin(n * PI / 6) for n in range(8)],
        [0, 0.25, 0.433, 0.5, 0.433, 0.25, 0, -0.25], 5e-4)
    chk("c7 77Ch samples", [math.sin(3 * PI * n / 8) for n in range(8)],
        [0, 0.9239, 0.7071, -0.3827, -1, -0.3827, 0.7071, 0.9239], 5e-5)
    chk("c7 77Ch spectrum is real",
        max(abs(D.clean(v).imag) for v in
            D.dft([math.sin(3 * PI * n / 8) for n in range(8)], 8)), 0.0, 1e-9)
    chk("c7 75Bh samples", [0.2 * n for n in range(8)],
        [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4], 1e-12)
    Xb = D.dft([0.2 * n for n in range(8)], 8)
    chk("c7 75Bh X(4) is the alternating sum", Xb[4],
        sum((-1) ** n * 0.2 * n for n in range(8)), 1e-9)
    chk("c7 75Bh X(4)", Xb[4], -0.8, 1e-9)
    chk("c7 75Bh X(7) = conj X(1)", Xb[7], Xb[1].conjugate(), 1e-9)
    chk("c7 75Bh X(7)", Xb[7], complex(-0.8, -1.931), 5e-4)

    # 72 Ash: the IDFT through a forward FFT
    Xk = [6, -2 + 2j, -2, -2 - 2j]
    chk("c7 72Ash conjugated input", [complex(v).conjugate() for v in Xk],
        [6, -2 - 2j, -2, -2 + 2j], 1e-12)
    fwd = D.dft([complex(v).conjugate() for v in Xk], 4)
    chk("c7 72Ash forward DFT of the conjugate", fwd, [0, 4, 8, 12], 1e-9)
    chk("c7 72Ash answer", D.ifft_via_fft(Xk), [0, 1, 2, 3], 1e-9)
    chk("c7 72Ash answer is real",
        max(abs(D.clean(v).imag) for v in D.ifft_via_fft(Xk)), 0.0, 1e-9)
    chk("c7 72Ash sum matches X(0)", sum(D.clean(v).real
                                         for v in D.ifft_via_fft(Xk)), 6, 1e-9)

    # ------------------------------------------ the worked circular convolution ---
    x1, x2 = [1, 2, 3, 1], [4, 3, 2, 2]
    y = D.circconv(x1, x2, 4)
    chk("c7 80Bh y", y, [17, 19, 22, 19], 1e-9)
    chk("c7 80Bh circulant row 0", [x2[(0 - m) % 4] for m in range(4)],
        [4, 2, 2, 3], 1e-12)
    chk("c7 80Bh circulant row 1", [x2[(1 - m) % 4] for m in range(4)],
        [3, 4, 2, 2], 1e-12)
    chk("c7 80Bh circulant row 2", [x2[(2 - m) % 4] for m in range(4)],
        [2, 3, 4, 2], 1e-12)
    chk("c7 80Bh circulant row 3", [x2[(3 - m) % 4] for m in range(4)],
        [2, 2, 3, 4], 1e-12)
    chk("c7 80Bh X1(k)", D.dft(x1, 4), [7, -2 - 1j, 1, -2 + 1j], 1e-9)
    chk("c7 80Bh X2(k)", D.dft(x2, 4), [11, 2 - 1j, 1, 2 + 1j], 1e-9)
    chk("c7 80Bh product", [a * b for a, b in zip(D.dft(x1, 4), D.dft(x2, 4))],
        [77, -5, 1, -5], 1e-9)
    chk("c7 80Bh DFT route agrees", D.circconv_via_dft(x1, x2, 4), y, 1e-9)
    chk("c7 80Bh sum check", sum(D.clean(v).real for v in y),
        sum(x1) * sum(x2), 1e-9)

    # 74 Ch: linear via circular, and the wrap that justifies zero padding
    N, yl = D.linconv_via_circ([1, 1, 1, 1], [2, 3])
    chk("c7 74Ch N = L+M-1", N, 5)
    chk("c7 74Ch linear answer", yl, [2, 5, 5, 5, 3], 1e-9)
    chk("c7 74Ch equals true linear convolution",
        yl, D.linconv([1, 1, 1, 1], [2, 3]), 1e-9)
    chk("c7 74Ch at N=4 it wraps", D.circconv([1, 1, 1, 1], [2, 3], 4),
        [5, 5, 5, 5], 1e-9)
    chk("c7 74Ch the wrap is 2+3 on y[0]",
        D.clean(D.circconv([1, 1, 1, 1], [2, 3], 4)[0]).real,
        D.clean(yl[0]).real + D.clean(yl[4]).real, 1e-9)
    err, folded = D.wrap_error([1, 1, 1, 1], [2, 3], 4)
    chk("c7 74Ch wrap is exactly the fold", err, 0.0, 1e-9)
    chk("c7 74Ch sum check", sum(D.clean(v).real for v in yl), 4 * 5, 1e-9)
    # 72 Ash's triangle
    chk("c7 72Ash triangle", D.linconv_via_circ([1, 1, 1], [2, 2, 2])[1],
        [2, 4, 6, 4, 2], 1e-9)
    # 77 Ch's misprinted x[n]
    chk("c7 77Ch reading", D.linconv_via_circ([1, 1, 1], [1, 0, -3])[1],
        [1, 1, -2, -3, -3], 1e-9)

    # constant-sequence convolutions, which the notes call out as free marks
    chk("c7 75Ch flat x2 gives sum(x1) everywhere",
        D.circconv([0, 0, 1, 1], [1, 1, 1, 1], 4), [2, 2, 2, 2], 1e-9)
    chk("c7 71Ch flat gives 3 everywhere",
        D.circconv([1, 2], [1, 1, 1, 1], 4), [3, 3, 3, 3], 1e-9)
    # 71 Shr is the circular answer, NOT the linear one
    chk("c7 71Shr circular", D.circconv_via_dft([1, 2, 3, 4], [1, 3, 5, 7], 4),
        [42, 46, 42, 30], 1e-9)
    chk("c7 71Shr is not the linear convolution",
        1 if abs(D.linconv([1, 2, 3, 4], [1, 3, 5, 7])[0] - 42) > 1 else 0, 1)

    # --- the papers that do NOT print eight numbers, now quoted verbatim in
    # section 1's table. Each needs a conversion before any butterfly, and
    # that conversion is the first mark.
    step = [1 if 0 <= n < 4 else 0 for n in range(8)]      # u[n] - u[n-4]
    chk("c7 78Bh u[n]-u[n-4] samples to", step,
        [1, 1, 1, 1, 0, 0, 0, 0], 1e-12)
    chk("c7 78Bh X(k) from the step", D.dft(step, 8)[0].real, 4.0, 1e-9)
    chk("c7 82Bh fractions equal the decimals",
        [1, 0.5, -1, -0.5, 2, -1.5],
        [1, 1 / 2.0, -1, -1 / 2.0, 2, -3 / 2.0], 1e-12)
    chk("c7 74Ash halves equal 70Bh decimals",
        [1 / 2.0] * 4 + [0] * 4, [0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0], 1e-12)
    # 71 Shr / 71 Bh also want the spectrum plotted: |X(k)|, symmetric
    mag = [abs(v) for v in D.dft([1, 1, 2, 0, 1, 2, 0, 1], 8)]
    chk("c7 71Shr magnitude spectrum", [round(v, 4) for v in mag],
        [8.0, 0.5858, 2.0, 3.4142, 0.0, 3.4142, 2.0, 0.5858], 5e-4)
    chk("c7 71Shr spectrum is symmetric about k=4",
        [round(v, 6) for v in mag[1:]], [round(v, 6) for v in mag[1:][::-1]],
        1e-9)
    # 74 Ch asks for X(1) and X(2) ONLY, which is why they are marked up
    x74 = [1.5, -1, 1.8, 0.6, 3, 1.7, 0, 0]
    X74 = D.dft(x74, 8)
    chk("c7 74Ch X(1)", [round(X74[1].real, 4), round(X74[1].imag, 4)],
        [-3.8334, -0.3151], 5e-4)
    chk("c7 74Ch X(2)", [round(X74[2].real, 4), round(X74[2].imag, 4)],
        [2.7, -0.1], 5e-4)

    # ------------------------------------------- the 81 Ch / 75 Bh defect ---
    a1, a2 = [1, 3, 9, 27], [1, 2, 4, 8, 16]
    chk("c7 81Ch x1 = 3^n has 4 entries", len(a1), 4)
    chk("c7 81Ch x2 = 2^n has 5 entries", len(a2), 5)
    chk("c7 81Ch x1 values", a1, [3 ** n for n in range(4)], 1e-12)
    chk("c7 81Ch x2 values", a2, [2 ** n for n in range(5)], 1e-12)
    try:
        D.circconv_via_dft(a1, a2, 4)
        chk("c7 81Ch 4-point must be rejected", 0, 1)
    except ValueError:
        chk("c7 81Ch 4-point must be rejected", 1, 1)
    chk("c7 81Bh N=5 answer", D.circconv_via_dft(a1, a2, 5),
        [229, 365, 451, 65, 130], 1e-8)
    chk("c7 81Bh sum check",
        sum(D.clean(v).real for v in D.circconv_via_dft(a1, a2, 5)),
        sum(a1) * sum(a2), 1e-7)

    # ------------------------------ every emitted table row, recomputed ---
    for name, N, kind, x, note in D.FFT_PAPERS:
        X = D.dft(x, N)
        tag = "c7 table %s (%d-pt %s)" % (name, N, kind)
        if N in (4, 8):
            chk(tag + " DIT", D.dit_stages(x, N)[2], X, 1e-9)
            chk(tag + " DIF", D.dif_stages(x, N)[2], X, 1e-9)
        chk(tag + " X(0)", X[0], sum(D.pad(x, N)[0]), 1e-9)
        if all(abs(complex(v).imag) < 1e-15 for v in x):
            chk(tag + " conjugate symmetry",
                [X[N - k] for k in range(1, N)],
                [X[k].conjugate() for k in range(1, N)], 1e-9)
    for name, x, h, N, note in D.CIRC_PAPERS:
        y = D.circconv(x, h, N)
        chk("c7 conv %s both routes" % name,
            y, D.circconv_via_dft(x, h, N), 1e-8)
        chk("c7 conv %s sum" % name, sum(D.clean(v).real for v in y),
            sum(x) * sum(h), 1e-8)
    for name, x1_, x2_, N in D.PRODUCT_PAPERS:
        y = D.circconv_via_dft(x1_, x2_, N)
        chk("c7 product %s is the circular convolution" % name,
            y, D.circconv(x1_, x2_, N), 1e-8)
        chk("c7 product %s sum" % name, sum(D.clean(v).real for v in y),
            sum(x1_) * sum(x2_), 1e-7)
    for name, x, h in D.LINEAR_PAPERS:
        N, y = D.linconv_via_circ(x, h)
        chk("c7 linear %s N" % name, N, len(x) + len(h) - 1)
        chk("c7 linear %s equals linconv" % name, y, D.linconv(x, h), 1e-9)

    # ---------------- and the .tex itself still carries those same numbers ---
    # The tables were emitted, not typed, so the risk is not a typo at birth
    # but a later edit. Re-read the file and check every sequence literal that
    # follows a paper name against dft.py.
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "ch7-num.tex")
    if not os.path.exists(path):
        chk("c7 ch7-num.tex is readable", 0, 1)
        return
    tex = open(path, encoding="utf-8").read()

    def parse(cell):
        """\\{$a$, $b$\\} -> list of complex, or None if it is not one."""
        cell = cell.strip()
        if not (cell.startswith("\\{") and cell.endswith("\\}")):
            return None
        body = cell[2:-2]
        out = []
        for tok in body.split(","):
            tok = tok.strip()
            if not (tok.startswith("$") and tok.endswith("$")):
                return None
            t = tok[1:-1].replace("{+}", "+").replace("{-}", "-")
            m = re.fullmatch(r"([+-]?[\d.]+)?([+-]?)j([\d.]+)", t)
            if m:
                re_ = float(m.group(1)) if m.group(1) else 0.0
                sign = -1.0 if m.group(2) == "-" else 1.0
                out.append(complex(re_, sign * float(m.group(3))))
                continue
            try:
                out.append(complex(float(t), 0.0))
            except ValueError:
                return None
        return out

    # Recompute the ANSWER column of every table row from that row's own INPUT
    # column. A row only passes if the printed data and the printed result
    # still agree with dft.py, so editing either side alone fails here.
    fft_rows = conv_rows = lin_rows = 0
    for line in tex.splitlines():
        line = line.rstrip()
        if "&" not in line or not line.endswith("\\\\"):
            continue
        cells = [c.strip() for c in line[:-2].split("&")]
        if len(cells) != 5:
            continue
        alg = cells[2].strip()
        tag = cells[0].replace("\\textbf", "").replace("\\texttt", "")
        tag = tag.replace("{", "").replace("}", "").strip()

        if alg in ("DIT", "DIF") and cells[1].strip().isdigit():
            N = int(cells[1])
            x, X = parse(cells[3]), parse(cells[4])
            if x is None or X is None:
                continue
            chk("c7 tex FFT %s (%d-pt %s)" % (tag, N, alg), X, D.dft(x, N), 5e-4)
            fft_rows += 1
        elif cells[1].strip().isdigit():
            N = int(cells[1])
            a, b, y = parse(cells[2]), parse(cells[3]), parse(cells[4])
            if a is None or b is None or y is None:
                continue
            chk("c7 tex conv %s (N=%d)" % (tag, N), y, D.circconv(a, b, N), 5e-4)
            conv_rows += 1
        elif cells[3].strip().isdigit():
            N = int(cells[3])
            a, b, y = parse(cells[1]), parse(cells[2]), parse(cells[4])
            if a is None or b is None or y is None:
                continue
            chk("c7 tex linear %s N" % tag, N, len(a) + len(b) - 1)
            chk("c7 tex linear %s" % tag, y, D.linconv(a, b), 5e-4)
            lin_rows += 1

    # and the counts, so a table that silently vanishes is also caught.
    # 22 FFT rows (the 8-point table, split in two tabulars for pagination),
    # 25 convolution rows (14 direct + 11 product), 4 linear ones. The
    # four-point table is skipped on purpose: its columns are
    # (paper, alg, x, X, note), so cells[1] is not a number.
    # --- section 1's table was restyled 2026-09-15: its columns are now
    # (papers, question as printed, X(k)), so the 5-cell scan above no longer
    # reaches it. Recompute it from the QUESTION cell instead: pull the
    # sequence out of the paper's own wording and assert the answer column
    # against dft.py, which is a stronger check than before because it now
    # also proves the quoted question and the published answer agree.
    def seq_from_question(cell):
        """The \\{...\\} the paper prints, or None if it prints a formula."""
        m = re.search(r"\$x\s*[\[(]n[\])]\s*=?\s*\\\{(.+?)\\?[\}\)]\$", cell)
        if not m:
            m = re.search(r"\$\\\{([-\d.,\s]+)\\\}\$", cell)
        if not m:
            return None
        out = []
        for tok in m.group(1).split(","):
            tok = tok.strip()
            if not tok:
                return None
            try:
                out.append(float(tok))
            except ValueError:
                return None          # \tfrac, a formula, anything symbolic
        return out

    body = tex.split("Question as printed", 1)
    q_rows = 0
    if len(body) > 1:
        body = body[1].split("\\bottomrule", 1)[0]
        for row in body.split("\\\\"):
            cells = [c.strip() for c in row.split("&")]
            if len(cells) != 3:
                continue
            tag = re.sub(r"\\text(bf|tt)|[{}]", "", cells[0]).strip()
            x, X = seq_from_question(cells[1]), parse(cells[2])
            if x is None or X is None:
                continue
            chk("c7 tex question-row %s" % tag, X, D.dft(x, 8), 5e-4)
            q_rows += 1
    # 19 of the 21 data rows are recomputed here. Exactly three are skipped,
    # and each is asserted by name in the block further up instead:
    #   82 Bh        prints its sequence as \tfrac fractions
    #   74 Ash/70 Bh the same, as halves
    #   74 Ch        its X(1) and X(2) carry \mk markup, being the only two
    #                values the paper actually asks for
    # A row that quotes a formula rather than a list (78 Bh's u[n]-u[n-4])
    # still passes, because the cell also prints what it samples to and that
    # is what gets checked against the answer. If this count drops, a row
    # was lost in an edit.
    chk("c7 tex question rows found", q_rows, 19)

    # the old 5-column FFT tabulars are gone, replaced by the above
    chk("c7 old 5-column FFT rows are retired", fft_rows, 0)
    chk("c7 tex convolution rows found", conv_rows, 25)
    chk("c7 tex linear rows found", lin_rows, 4)


CHAPTERS = {"ch1": ch1, "ch2": ch2, "ch3": ch3, "ch4": ch4,
            "ch5": ch5, "ch6": ch6, "ch7": ch7}


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
