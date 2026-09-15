# -*- coding: utf-8 -*-
r"""FIR filter design by windowing, for DSAP chapter 5.

    python fir.py            # self-test, then every PYQ design
    python fir.py --papers   # just the paper table

47 of the 70 questions in chapter 5 are a window design: pick a window from the
stopband attenuation, get the length from the transition width, truncate the
ideal impulse response. The remaining 23 are the Remez algorithm, which is
bookwork and needs no solver.

THE IDEAL IMPULSE RESPONSE.  Inverse DTFT of the ideal brick wall, delayed by
alpha = (N-1)/2 samples so the result is causal and linear phase:

    low pass    h_d[n] = sin(w_c (n - alpha)) / (pi (n - alpha)),  = w_c/pi at n = alpha
    high pass   delta[n - alpha] - (low pass with w_c)
    band pass   (low pass with w_2) - (low pass with w_1)

THE FIVE FIXED WINDOWS, with M = N - 1 and 0 <= n <= N-1:

    rectangular  1
    Bartlett     1 - |2n - M| / M                      (triangular)
    Hann         0.5 - 0.5 cos(2 pi n / M)
    Hamming      0.54 - 0.46 cos(2 pi n / M)
    Blackman     0.42 - 0.5 cos(2 pi n / M) + 0.08 cos(4 pi n / M)

Each window has a fixed stopband attenuation that does NOT depend on N. That is
the whole point of the table in TABLE below, and the reason Gibbs ripple cannot
be reduced by lengthening the filter: raising N narrows the transition but
leaves the ripple height alone.

KAISER is the exception: beta buys attenuation, N buys transition width, so the
two specs are decoupled. The empirical design equations are Kaiser's own:

    A = -20 log10(delta),  delta = min(delta_p, delta_s)
    beta = 0                                             A <= 21
         = 0.5842 (A-21)^0.4 + 0.07886 (A-21)            21 < A <= 50
         = 0.1102 (A - 8.7)                              A > 50
    N-1 = (A - 8) / (2.285 * delta_w)
"""
import math
import sys

FAIL = []
OK = [0]


def chk(tag, got, want, tol=1e-9):
    try:
        if isinstance(want, (list, tuple)):
            same = len(got) == len(want) and all(
                abs(a - b) <= tol for a, b in zip(got, want))
        else:
            same = abs(got - want) <= tol
    except TypeError:
        same = got == want
    if same:
        OK[0] += 1
    else:
        FAIL.append("%s\n     got  %s\n     want %s" % (tag, got, want))


# name -> (main lobe width numerator over M, peak sidelobe dB,
#          stopband attenuation dB, exact transition width numerator over M)
TABLE = [
    ("Rectangular", 4, -13, 21, 1.8),
    ("Bartlett", 8, -25, 25, 6.1),
    ("Hann", 8, -31, 44, 6.2),
    ("Hamming", 8, -41, 53, 6.6),
    ("Blackman", 12, -57, 74, 11.0),
]
ATTEN = {n: a for n, _, _, a in ((r[0], r[3], 0, 0) for r in TABLE)}
ATTEN = {r[0]: r[3] for r in TABLE}
TRANS = {r[0]: r[4] for r in TABLE}
MAIN = {r[0]: r[1] for r in TABLE}


def window(name, N):
    """The window sequence, length N, symmetric about M/2 with M = N-1."""
    M = N - 1
    out = []
    for n in range(N):
        if name == "Rectangular":
            w = 1.0
        elif name == "Bartlett":
            w = 1.0 - abs(2.0 * n - M) / M
        elif name == "Hann":
            w = 0.5 - 0.5 * math.cos(2 * math.pi * n / M)
        elif name == "Hamming":
            w = 0.54 - 0.46 * math.cos(2 * math.pi * n / M)
        elif name == "Blackman":
            w = (0.42 - 0.5 * math.cos(2 * math.pi * n / M)
                 + 0.08 * math.cos(4 * math.pi * n / M))
        else:
            raise ValueError(name)
        out.append(w)
    return out


def hd_lowpass(N, wc):
    """Ideal low-pass impulse response, delayed to alpha = (N-1)/2."""
    a = (N - 1) / 2.0
    out = []
    for n in range(N):
        m = n - a
        out.append(wc / math.pi if abs(m) < 1e-12
                   else math.sin(wc * m) / (math.pi * m))
    return out


def hd_highpass(N, wc):
    a = (N - 1) / 2.0
    lp = hd_lowpass(N, wc)
    return [(1.0 if abs(n - a) < 1e-12 else 0.0) - lp[n] for n in range(N)]


def hd_bandpass(N, w1, w2):
    lo, hi = hd_lowpass(N, w1), hd_lowpass(N, w2)
    return [hi[n] - lo[n] for n in range(N)]


def pick_window(atten_db):
    """Cheapest window whose stopband attenuation meets the spec."""
    for name, _, _, a, _ in TABLE:
        if a >= atten_db:
            return name
    return None


def length_for(name, dw):
    """Filter length N from the transition width, using the exact figure."""
    M = TRANS[name] * math.pi / dw
    N = int(math.ceil(M)) + 1
    return N if N % 2 else N + 1          # odd length keeps alpha an integer


def i0(x, terms=60):
    """Modified Bessel function of the first kind, order zero."""
    s, t = 1.0, 1.0
    for k in range(1, terms):
        t *= (x / 2.0) ** 2 / (k * k)
        s += t
        if t < 1e-18 * s:
            break
    return s


def kaiser_beta(A):
    if A <= 21:
        return 0.0
    if A <= 50:
        return 0.5842 * (A - 21) ** 0.4 + 0.07886 * (A - 21)
    return 0.1102 * (A - 8.7)


def kaiser_N(A, dw):
    """Kaiser's length estimate. Returns (M, N) with N = M+1 rounded up odd."""
    M = (A - 8) / (2.285 * dw)
    N = int(math.ceil(M)) + 1
    return M, (N if N % 2 else N + 1)


def kaiser_window(N, beta):
    M = N - 1
    d = i0(beta)
    return [i0(beta * math.sqrt(max(0.0, 1 - (2.0 * n / M - 1) ** 2))) / d
            for n in range(N)]


def db(x):
    return -20 * math.log10(x)


def design(wp, ws, atten_db=None, dp=None, ds=None, kind="lp", dw2=None):
    """One window design. Returns a dict of everything a paper can ask for.

    dw2 is the SECOND transition width of a band-pass spec. A band-pass
    filter has two of them and one window has to satisfy both, so the
    length is set by the NARROWER: a filter long enough for the wide
    transition is too short for the narrow one. 78 Bh / 74 Ch was entered
    here as a low pass carrying only its lower transition (0.1 pi), which
    hid the upper one (0.05 pi) and published N = 47 where the rule gives
    91. verify.py now asserts both the answer and the rule.
    """
    dw = abs(ws - wp)
    if dw2 is not None:
        dw = min(dw, abs(dw2))
    wc = (wp + ws) / 2.0
    if atten_db is None:
        atten_db = db(ds)
    name = pick_window(atten_db)
    out = {"dw": dw, "wc": wc, "A": atten_db, "window": name}
    if name:
        out["N"] = length_for(name, dw)
    if dp is not None and ds is not None:
        d = min(dp, ds)
        A = db(d)
        beta = kaiser_beta(A)
        Mest, N = kaiser_N(A, dw)
        out.update({"kaiser_A": A, "beta": beta, "kaiser_M": Mest,
                    "kaiser_N": N, "delta": d})
    return out


def selftest():
    # the table itself, against the figures every source prints
    chk("rectangular attenuation", ATTEN["Rectangular"], 21)
    chk("hamming attenuation", ATTEN["Hamming"], 53)
    chk("blackman main lobe", MAIN["Blackman"], 12)

    # every window is symmetric, which is the linear-phase condition
    for name, _, _, _, _ in TABLE:
        w = window(name, 11)
        chk("%s symmetric" % name, w, list(reversed(w)), tol=1e-12)
    # and each has the right end and centre values
    chk("Hann ends at zero", window("Hann", 11)[0], 0.0, tol=1e-12)
    chk("Hamming ends at 0.08", window("Hamming", 11)[0], 0.08, tol=1e-12)
    chk("Hann centre is 1", window("Hann", 11)[5], 1.0, tol=1e-12)
    chk("rectangular is all ones", window("Rectangular", 7), [1.0] * 7)

    # the ideal low pass: centre tap is wc/pi, and it is symmetric
    h = hd_lowpass(7, 1.0)
    chk("hd centre tap", h[3], 1.0 / math.pi, tol=1e-12)
    chk("hd symmetric", h, list(reversed(h)), tol=1e-12)
    # a high pass plus its low pass is a pure delay
    lp, hp = hd_lowpass(9, 0.8), hd_highpass(9, 0.8)
    chk("lp + hp = delta", [lp[i] + hp[i] for i in range(9)],
        [0.0] * 4 + [1.0] + [0.0] * 4, tol=1e-12)

    # Bessel: I0(0) = 1, and a known value
    chk("I0(0)", i0(0.0), 1.0, tol=1e-15)
    chk("I0(1)", i0(1.0), 1.2660658777520084, tol=1e-12)
    chk("I0(2)", i0(2.0), 2.2795853023360673, tol=1e-12)
    # the Kaiser window is rectangular when beta = 0
    chk("kaiser beta=0 is rectangular", kaiser_window(9, 0.0), [1.0] * 9,
        tol=1e-12)

    # Kaiser's own worked example: delta = 0.01 gives A = 40 dB
    chk("A for delta=0.01", db(0.01), 40.0, tol=1e-12)
    chk("beta at A=40", kaiser_beta(40.0), 3.395320, tol=1e-5)
    chk("beta is zero below 21 dB", kaiser_beta(20.0), 0.0)

    # 66 Ma supplies a table it labels J_0(x). Every value is I_0(x): the
    # modified Bessel function, mislabelled. J_0 oscillates and never exceeds 1,
    # while these climb past 2. Checking all eight settles it.
    TAB = [(0, 1), (1.3165, 1.4826), (1.7237, 1.8926), (1.8455, 2.0508),
           (1.9271, 2.1675), (1.93, 2.1718), (1.9903, 2.2642), (2, 2.2796)]
    for x, printed in TAB:
        chk("66 Ma table I0(%s)" % x, i0(x), printed, tol=5e-5)
    chk("66 Ma J0 is not what is printed",
        1.0 if abs(math.cos(2.0) - 2.2796) > 1 else 0.0, 1.0)
    # and beta for its own spec lands exactly on one of its table entries
    chk("66 Ma beta is a table entry", kaiser_beta(db(0.035)), 1.9903,
        tol=5e-5)

    # the marginal window choice in 67 Mng: 54 dB just clears Hamming's 53
    chk("54 dB needs Blackman", pick_window(54), "Blackman")
    chk("53 dB still allows Hamming", pick_window(53), "Hamming")
    chk("Hamming would have been N=67", length_for("Hamming", 0.1 * math.pi), 67)
    chk("Blackman costs N=111", length_for("Blackman", 0.1 * math.pi), 111)

    print("%d self-tests passed" % OK[0])
    if FAIL:
        for f in FAIL:
            print("  FAIL " + f)
        sys.exit(1)


PI = math.pi

# (tag, wp, ws, stopband attenuation dB or None, dp, ds)
WINDOWED = [
    ("79 Ba", 0.2 * PI, 0.45 * PI, 51, None, None),
    ("71 Ch, 69 Ch", 0.3 * PI, 0.5 * PI, 40, None, None),
    ("74 Ash", 0.2 * PI, 0.5 * PI, 41, None, None),
    ("79 Ch, 75 Bh", 0.24 * PI, 0.54 * PI, 42.2, None, None),
    ("67 Mng", 0.35 * PI, 0.45 * PI, 54, None, None),
    ("70 Asa", 0.25 * PI, 0.35 * PI, None, None, None),
    ("69 Bh", 0.25 * PI, 0.3 * PI, None, None, None),
    ("68 Bh", 0.24 * PI, 0.34 * PI, None, None, None),
    ("76 Ch, 81 Ch, 73 Ma", 0.2 * PI, 0.4 * PI, None, 0.101, 0.01),
    # specified in Hz, converted with w = 2 pi f / fs
    ("82 Bh", 2 * PI * 2000 / 20000, 2 * PI * 5000 / 20000, 42, None, None),
    # specified in rad/s at fs = 100 Hz, converted with w = Omega / fs
    ("82 Ba", 30 * PI / 100, 45 * PI / 100, 50, None, None),
]

KAISER = [
    ("81 Ba, 81 Bh", 0.3 * PI, 0.35 * PI, 0.01, 0.01),
    ("80 Bh", 0.19 * PI, 0.21 * PI, 0.05, 0.01),
    ("80 Ba", 0.016 * PI, 0.08 * PI, 0.01, 0.01),
    ("79 Bh", 0.2 * PI, 0.4 * PI, 0.101, 0.01),
    # band pass: transitions 0.25->0.35 pi and 0.6->0.65 pi. The second is
    # the narrower and therefore the one that sets N.
    ("78 Bh, 74 Ch", 0.25 * PI, 0.35 * PI, 0.05, 0.01, 0.05 * PI),
    ("75 Ash, 72 Ka", 0.19 * PI, 0.21 * PI, 0.01, 0.01),
    ("76 Ash", 0.16 * PI, 0.18 * PI, 0.01, 0.01),
    ("73 Ch", 0.09 * PI, 0.14 * PI, 0.02, 0.01),
    ("78 Ch", 0.19 * PI, 0.21 * PI, 0.02, 0.02),
    ("66 Ma", 0.25 * PI, 0.65 * PI, 0.035, 0.035),
]


def run_papers():
    print("")
    print("=" * 86)
    print("WINDOW TABLE")
    print("=" * 86)
    print("%-13s %-14s %-14s %-12s %s"
          % ("window", "main lobe", "peak sidelobe", "stopband", "transition"))
    for name, ml, sl, at, tr in TABLE:
        print("%-13s %-14s %-14s %-12s %s"
              % (name, "%d pi/M" % ml, "%d dB" % sl, "%d dB" % at,
                 "%.1f pi/M" % tr))

    print("")
    print("=" * 86)
    print("FIXED WINDOW DESIGNS")
    print("=" * 86)
    for tag, wp, ws, A, dp, ds in WINDOWED:
        if A is None and ds is not None:
            A = db(ds)
        if A is None:
            print("%-22s dw = %.4f (%.3f pi), wc = %.4f (%.3f pi)   "
                  "window named by the paper"
                  % (tag, abs(ws - wp), abs(ws - wp) / PI,
                     (wp + ws) / 2, (wp + ws) / 2 / PI))
            continue
        d = design(wp, ws, atten_db=A)
        print("%-22s A = %5.1f dB -> %-12s N = %-4d  wc = %.4f (%.3f pi)  "
              "dw = %.3f pi"
              % (tag, d["A"], d["window"], d["N"], d["wc"], d["wc"] / PI,
                 d["dw"] / PI))

    print("")
    print("=" * 86)
    print("KAISER DESIGNS")
    print("=" * 86)
    for tag, wp, ws, dp, ds, *rest in KAISER:
        d = design(wp, ws, dp=dp, ds=ds, dw2=(rest[0] if rest else None))
        print("%-16s d = %-6.3f A = %5.2f dB  beta = %-7.4f M = %7.2f -> "
              "N = %-5d wc = %.3f pi"
              % (tag, d["delta"], d["kaiser_A"], d["beta"], d["kaiser_M"],
                 d["kaiser_N"], d["wc"] / PI))

    print("")
    print("=" * 86)
    print("80 Bh / 73 Bh / 76 Bh: length 7, wc = 1 rad/sample")
    print("=" * 86)
    hd = hd_lowpass(7, 1.0)
    print("  h_d[n]      " + "  ".join("%8.5f" % x for x in hd))
    for name in ("Hann", "Blackman"):
        w = window(name, 7)
        h = [hd[i] * w[i] for i in range(7)]
        print("  %-10s  " % name + "  ".join("%8.5f" % x for x in w))
        print("  h[n]        " + "  ".join("%8.5f" % x for x in h))


def main():
    if "--papers" not in sys.argv:
        selftest()
    run_papers()


if __name__ == "__main__":
    main()
