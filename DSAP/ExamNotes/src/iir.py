# -*- coding: utf-8 -*-
"""IIR filter design solver for DSAP chapter 6.

    python iir.py            # self-tests, then every PYQ design

Everything the chapter 6 notes print is produced here: Butterworth and
Chebyshev order and cut-off, the analog poles, H(s) as a cascade of real
quadratic sections, H(z) by bilinear transformation or impulse invariance,
and the digital-domain spectral transformations.

Conventions, stated once because the sources disagree:

  * Attenuation in dB is POSITIVE: alpha = -20 log10 |H|.  A paper saying
    "maximum deviation 1 dB below 0 dB gain" means alpha_p = 1; a paper
    giving a gain 0.89125 means alpha_p = -20 log10 (0.89125) = 1 dB; a
    paper giving a ripple delta_p = 0.11 means the passband edge gain is
    1 - 0.11 = 0.89, so alpha_p = 1.0122 dB.  All three are the same spec.

  * Bilinear pre-warping uses Omega = (2/T) tan(w/2).  The 2/T then cancels
    exactly when the transformation is applied back, so H(z) NEVER depends
    on T for a spec given in normalised w.  bilinear_T_cancels() proves it.

  * Impulse invariance uses the linear map Omega = w/T and
    H(z) = sum_k  A_k / (1 - e^{p_k T} z^-1)          (Proakis, h[n]=h_a(nT))
    Oppenheim instead sets h[n] = T h_a(nT) and so carries an extra factor
    T.  With T = 1 s, which is 8 of the 11 impulse-invariance papers, the
    two are identical.  scale_T=True selects the Oppenheim form.
"""
import cmath
import math

FAIL = []
OK = [0]


def chk(tag, got, want, tol=1e-6):
    if isinstance(want, (list, tuple)):
        same = len(got) == len(want) and all(
            abs(complex(a) - complex(b)) <= tol for a, b in zip(got, want))
    else:
        same = abs(complex(got) - complex(want)) <= tol
    if same:
        OK[0] += 1
    else:
        FAIL.append("%s\n     got  %s\n     want %s" % (tag, got, want))


# ----------------------------------------------------------------- specs ---
def alpha_from_gain(g):
    """Passband/stopband gain -> attenuation in dB (positive)."""
    return -20.0 * math.log10(g)


def alpha_from_ripple(d, band):
    """Ripple delta -> attenuation in dB.  In the passband the edge gain is
    1-delta; in the stopband it is delta itself."""
    return alpha_from_gain(1.0 - d) if band == "pass" else alpha_from_gain(d)


def w_from_hz(f, fs):
    """Frequency in Hz -> digital frequency in rad/sample."""
    return 2.0 * math.pi * f / fs


# ------------------------------------------------------------ polynomials ---
def pmul(a, b):
    out = [0j] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0j) + (b[i] if i < len(b) else 0j)
            for i in range(n)]


def pscale(a, k):
    return [k * x for x in a]


def ppow(a, n):
    out = [1 + 0j]
    for _ in range(n):
        out = pmul(out, a)
    return out


def preal(a):
    """Drop numerically-zero imaginary parts; the coefficients of a real
    filter are real because its poles come in conjugate pairs."""
    return [x.real for x in a]


def from_roots(roots):
    """Monic polynomial in s with the given roots, ascending powers."""
    out = [1 + 0j]
    for r in roots:
        out = pmul(out, [-r, 1 + 0j])
    return out


def peval(p, x):
    acc = 0j
    for c in reversed(p):
        acc = acc * x + c
    return acc


def pnorm(p):
    """Divide through by the leading (highest-power) coefficient."""
    lead = p[-1]
    return [c / lead for c in p]


def trim(p, tol=1e-12):
    while len(p) > 1 and abs(p[-1]) < tol:
        p = p[:-1]
    return p


# ------------------------------------------------------------ Butterworth ---
def check_nyquist(wp, ws):
    """A digital band edge above pi does not exist: it has already aliased.
    70 Bh prints a 170 Hz stopband edge against a 256 Hz sampling rate,
    whose Nyquist limit is 128 Hz, so its spec cannot be met by any filter.
    Raising here rather than returning a negative pre-warped Omega."""
    for tag, w in (("passband", wp), ("stopband", ws)):
        if w >= math.pi:
            raise ValueError(
                "%s edge w = %.4f rad/sample exceeds pi: above Nyquist" %
                (tag, w))


def butter_order(wp, ws, ap, asb, T=1.0, method="bilinear", warp=True):
    """Return (N_exact, N, Op, Os) for the given digital spec.

    warp=False keeps the analog edges as given and skips pre-warping, which
    is the only way to read a paper whose edges lie outside Nyquist."""
    if method == "bilinear" and warp:
        check_nyquist(wp, ws)
        Op = (2.0 / T) * math.tan(wp / 2.0)
        Os = (2.0 / T) * math.tan(ws / 2.0)
    else:                                        # impulse invariance, or raw
        Op, Os = wp / T, ws / T
    num = math.log10((10 ** (0.1 * asb) - 1.0) / (10 ** (0.1 * ap) - 1.0))
    Nx = num / (2.0 * math.log10(Os / Op))
    return Nx, int(math.ceil(Nx - 1e-12)), Op, Os


def butter_wc(Op, ap, N, Os=None, asb=None, edge="pass"):
    """3 dB cut-off.  edge='pass' meets the passband exactly (the local
    convention and every paper's expected answer); edge='stop' meets the
    stopband exactly, which is the other admissible choice."""
    if edge == "pass":
        return Op / (10 ** (0.1 * ap) - 1.0) ** (1.0 / (2 * N))
    return Os / (10 ** (0.1 * asb) - 1.0) ** (1.0 / (2 * N))


def butter_poles(Oc, N):
    """The N left-half-plane poles, ordered by increasing angle."""
    return [Oc * cmath.exp(1j * math.pi * (N + 2 * k + 1) / (2 * N))
            for k in range(N)]


def butter_Hs(Oc, N):
    """(num, den) of H(s) = Oc^N / prod(s - s_k), ascending powers of s."""
    den = preal(from_roots(butter_poles(Oc, N)))
    return [Oc ** N], den


def sections(poles):
    """Group conjugate poles into real quadratic factors; a lone real pole
    stays linear.  Returns a list of ascending-power real polynomials."""
    left = list(poles)
    out = []
    while left:
        p = left.pop(0)
        if abs(p.imag) < 1e-9:
            out.append([-p.real, 1.0])
            continue
        mate = min(range(len(left)), key=lambda i: abs(left[i] - p.conjugate()))
        q = left.pop(mate)
        out.append([(p * q).real, -(p + q).real, 1.0])
    return out


# -------------------------------------------------------------- Chebyshev ---
def cheb_order(wp, ws, ap, asb, T=1.0, method="bilinear"):
    if method == "bilinear":
        Op = (2.0 / T) * math.tan(wp / 2.0)
        Os = (2.0 / T) * math.tan(ws / 2.0)
    else:
        Op, Os = wp / T, ws / T
    g = math.sqrt((10 ** (0.1 * asb) - 1.0) / (10 ** (0.1 * ap) - 1.0))
    Nx = math.acosh(g) / math.acosh(Os / Op)
    return Nx, int(math.ceil(Nx - 1e-12)), Op, Os


def cheb_eps(ap):
    return math.sqrt(10 ** (0.1 * ap) - 1.0)


def cheb_ab(eps, N):
    """Semi-minor and semi-major axis factors a and b of the pole ellipse."""
    alpha = 1.0 / eps + math.sqrt(1.0 + 1.0 / eps ** 2)
    a = 0.5 * (alpha ** (1.0 / N) - alpha ** (-1.0 / N))
    b = 0.5 * (alpha ** (1.0 / N) + alpha ** (-1.0 / N))
    return alpha, a, b


def cheb_poles(Oc, eps, N):
    _, a, b = cheb_ab(eps, N)
    out = []
    for k in range(N):
        th = math.pi * (2 * k + 1) / (2 * N)
        out.append(complex(-a * Oc * math.sin(th), b * Oc * math.cos(th)))
    return out


def cheb_Hs(Oc, eps, N):
    """(num, den) of the type-I Chebyshev H(s).  The gain is fixed by
    |H(0)| = 1 for N odd and 1/sqrt(1+eps^2) for N even, which is the
    defining property of the equiripple passband."""
    poles = cheb_poles(Oc, eps, N)
    den = preal(from_roots(poles))
    K = den[0]                                   # prod(-s_k), the s^0 term
    if N % 2 == 0:
        K /= math.sqrt(1.0 + eps ** 2)
    return [K], den


# ------------------------------------------------- s-plane to z-plane maps ---
def bilinear(num, den, T=1.0):
    """H(s) -> H(z), returning (b, a) in ascending powers of z^-1.

    With s = c(1-x)/(1+x), x = z^-1 and c = 2/T, a polynomial p of degree n
    becomes  sum_i p_i c^i (1-x)^i (1+x)^(n-i)  after both sides are
    multiplied by (1+x)^n.  Numerator and denominator are padded to the
    same degree so the same (1+x)^n clears from both."""
    c = 2.0 / T
    n = max(len(num), len(den)) - 1

    def sub(p):
        acc = [0j]
        for i, coef in enumerate(p):
            acc = padd(acc, pscale(pmul(ppow([1, -1], i), ppow([1, 1], n - i)),
                                   coef * c ** i))
        return acc

    b, a = sub(num), sub(den)
    k = a[0]
    return preal(pscale(b, 1.0 / k)), preal(pscale(a, 1.0 / k))


def residues(num, den):
    """Partial-fraction residues A_k of num(s)/den(s) at the simple poles of
    den:  A_k = num(p_k) / den'(p_k)."""
    poles = roots(den)
    dden = [i * den[i] for i in range(1, len(den))]
    return poles, [peval(num, p) / peval(dden, p) for p in poles]


def impulse_invariance(num, den, T=1.0, scale_T=False):
    """H(s) -> (b, a) of H(z) = sum_k (T?) A_k / (1 - e^{p_k T} z^-1)."""
    poles, A = residues(num, den)
    zp = [cmath.exp(p * T) for p in poles]
    if scale_T:
        A = [T * a for a in A]
    a = [1 + 0j]
    for p in zp:
        a = pmul(a, [1 + 0j, -p])
    b = [0j] * len(zp)
    for k, (ak, pk) in enumerate(zip(A, zp)):
        term = [1 + 0j]
        for j, pj in enumerate(zp):
            if j != k:
                term = pmul(term, [1 + 0j, -pj])
        b = padd(b, pscale(term, ak))
    return preal(trim(b)), preal(a)


def roots(p):
    """Roots of an ascending-power polynomial."""
    p = trim([complex(c) for c in p])
    n = len(p) - 1
    if n == 0:
        return []
    try:
        import numpy as _np
        z = list(_np.roots(list(reversed(pnorm(p)))))
    except ImportError:                          # Aberth-Ehrlich fallback
        q = pnorm(p)
        dq = [i * q[i] for i in range(1, len(q))]
        z = [cmath.exp(2j * cmath.pi * k / n) * (0.4 + 0.9j) for k in range(n)]
        for _ in range(2000):
            new = []
            for i in range(n):
                num = peval(q, z[i])
                den = peval(dq, z[i])
                if abs(den) < 1e-300:
                    new.append(z[i])
                    continue
                w = num / den
                s_ = sum(1.0 / (z[i] - z[j]) for j in range(n) if j != i)
                new.append(z[i] - w / (1.0 - w * s_))
            if max(abs(a - b) for a, b in zip(z, new)) < 1e-15:
                z = new
                break
            z = new
    return sorted(z, key=lambda c: (round(c.real, 9), c.imag))


def zroots(p):
    """Roots in z of a polynomial written in ascending powers of z^-1.
    A root x of p is z = 1/x, because the polynomial variable IS z^-1."""
    return [1.0 / r for r in roots(p)]


def zsections(p):
    """Cascade factors of a polynomial written in ascending powers of z^-1,
    each returned in the SAME z^-1 form: [1, c1, c2] means
    1 + c1 z^-1 + c2 z^-2.  A conjugate pole pair z = p, p* contributes
    1 - 2Re(p) z^-1 + |p|^2 z^-2, so the middle coefficient is MINUS the
    sum of the roots, not plus it.  Getting that sign backwards is the easy
    mistake, so check_cascade() multiplies the factors back out."""
    out = []
    for sec in sections(zroots(p)):
        if len(sec) == 2:                       # z - r  ->  1 - r z^-1
            out.append([1.0, sec[0]])          # (z - r) -> (1 - r z^-1)
        else:                                   # z^2 + b z + c
            out.append([1.0, sec[1], sec[0]])
    return out


def check_cascade(p, secs):
    """Product of the z^-1 cascade factors, scaled to match p[0]."""
    acc = [1.0 + 0j]
    for sec in secs:
        acc = pmul(acc, sec)
    return preal(pscale(acc, p[0] / acc[0].real))


# --------------------------------------------- digital spectral transforms ---
def lp_to_lp(wp, wpn):
    return math.sin((wp - wpn) / 2.0) / math.sin((wp + wpn) / 2.0)


def lp_to_hp(wp, wpn):
    return -math.cos((wp + wpn) / 2.0) / math.cos((wp - wpn) / 2.0)


def apply_map(b, a, mnum, mden):
    """Substitute z^-1 -> mnum(x)/mden(x) into H(z) = b(x)/a(x), x = z^-1."""
    n = max(len(b), len(a)) - 1

    def sub(p):
        acc = [0j]
        for i, coef in enumerate(p):
            acc = padd(acc, pscale(pmul(ppow(mnum, i), ppow(mden, n - i)), coef))
        return acc

    nb, na = sub(b), sub(a)
    k = na[0]
    return preal(pscale(nb, 1.0 / k)), preal(pscale(na, 1.0 / k))


def hp_from_lp(b, a, wp, wpn):
    """LP prototype -> HP.  z^-1 -> -(z^-1 + alpha)/(1 + alpha z^-1)."""
    al = lp_to_hp(wp, wpn)
    return apply_map(b, a, [-al, -1.0], [1.0, al]) + (al,)


def freqz(b, a, w):
    x = cmath.exp(-1j * w)
    return peval(b, x) / peval(a, x)


# ------------------------------------------------------------- self-tests ---
def bilinear_T_cancels():
    """H(z) is the same for any T when the spec is given in rad/sample."""
    wp, ws, ap, asb = 0.2 * math.pi, 0.3 * math.pi, 1.0, 15.0
    out = []
    for T in (1.0, 2.0, 0.0001):
        _, N, Op, Os = butter_order(wp, ws, ap, asb, T)
        Oc = butter_wc(Op, ap, N)
        num, den = butter_Hs(Oc, N)
        out.append(bilinear(num, den, T))
    for b, a in out[1:]:
        chk("bilinear T-independence b", b, out[0][0], 1e-9)
        chk("bilinear T-independence a", a, out[0][1], 1e-9)


def selftest():
    pi = math.pi

    # --- Oppenheim example 7.2 / 7.3, which is also PYQ 73 Shr -------------
    wp, ws = 0.2 * pi, 0.3 * pi
    ap, asb = alpha_from_gain(0.89125), alpha_from_gain(0.17783)
    chk("alpha_p of 0.89125", ap, 1.0, 1e-4)
    chk("alpha_s of 0.17783", asb, 15.0, 1e-3)

    # impulse invariance: Omega = w, N = 5.8858 -> 6, Oc = 0.7032
    Nx, N, Op, Os = butter_order(wp, ws, ap, asb, 1.0, "invariance")
    chk("7.2 N exact", Nx, 5.8858, 1e-3)
    chk("7.2 N", N, 6)
    chk("7.2 Oc", butter_wc(Op, ap, N), 0.7032, 1e-3)
    p = butter_poles(butter_wc(Op, ap, N), N)
    chk("7.2 pole 1", p[0], -0.182 + 0.679j, 2e-3)
    chk("7.2 pole 2", p[1], -0.497 + 0.497j, 2e-3)
    chk("7.2 pole 3", p[2], -0.679 + 0.182j, 2e-3)
    num, den = butter_Hs(butter_wc(Op, ap, N), N)
    chk("7.2 gain", num[0], 0.12093, 1e-4)
    sec = sections(p)
    chk("7.2 section 1", sec[0][:2], [0.4945, 0.3640], 2e-3)
    chk("7.2 section 2", sec[1][:2], [0.4945, 0.9945], 2e-3)
    chk("7.2 section 3", sec[2][:2], [0.4945, 1.3585], 2e-3)

    # bilinear: pre-warped edges 0.64984 and 1.0191, N = 6, Oc = 0.766
    Nx, N, Op, Os = butter_order(wp, ws, ap, asb, 1.0, "bilinear")
    chk("7.3 Omega_p", Op, 0.64984, 1e-4)
    chk("7.3 Omega_s", Os, 1.0191, 1e-4)
    chk("7.3 N", N, 6)
    # Oppenheim/MATLAB buttord place the 3 dB point so the STOPBAND is met
    # exactly; the local formula places it so the PASSBAND is.  Both are
    # legal, they differ, and the published cascade below is the first.
    chk("7.3 Oc passband-exact", butter_wc(Op, ap, N), 0.72729, 1e-4)
    Oc = butter_wc(Op, ap, N, Os, asb, edge="stop")
    chk("7.3 Oc stopband-exact", Oc, 0.76627, 1e-4)
    num, den = butter_Hs(Oc, N)
    sec = sections(butter_poles(Oc, N))
    chk("7.3 section 1", sec[0][:2], [0.58716, 0.39665], 2e-3)
    chk("7.3 section 2", sec[1][:2], [0.58716, 1.0837], 2e-3)
    chk("7.3 section 3", sec[2][:2], [0.58716, 1.4803], 2e-3)
    b, a = bilinear(num, den, 1.0)
    # 0.00073798 is published; it carries MATLAB's rounded Wn = 0.76627
    chk("7.3 H(z) gain", b[0], 0.00073798, 3e-7)
    # the six zeros are all at z = -1, so b is Kd * (1+x)^6
    chk("7.3 H(z) numerator", b, [b[0] * c for c in
                                  [1, 6, 15, 20, 15, 6, 1]], 1e-9)
    ar = zroots(a)
    chk("7.3 z-pole radii", sorted(round(abs(r), 5) for r in ar),
        sorted(round(abs(v), 5) for v in
               [4.5216e-1 + 1.0510e-1j, 4.5216e-1 - 1.0510e-1j,
                5.0527e-1 + 3.2087e-1j, 5.0527e-1 - 3.2087e-1j,
                6.3430e-1 + 5.5026e-1j, 6.3430e-1 - 5.5026e-1j]), 1e-4)
    # the published cascade denominators
    dsec = sections(ar)
    got = sorted([tuple(round(v, 4) for v in s[:2]) for s in dsec])
    chk("7.3 z-section 1", list(got[0]), [0.21550, -0.90433], 2e-4)
    chk("7.3 z-section 2", list(got[1]), [0.35826, -1.0105], 2e-4)
    chk("7.3 z-section 3", list(got[2]), [0.70512, -1.2686], 2e-4)
    # specification actually met: stopband exactly, passband with margin
    chk("7.3 |H| at ws", abs(freqz(b, a, ws)), 0.17783, 5e-5)
    chk("7.3 |H| at wp >= 0.89125", max(abs(freqz(b, a, wp)), 0.89125),
        abs(freqz(b, a, wp)), 1e-12)
    # and the passband-exact cutoff meets the passband edge exactly instead
    n2, d2 = butter_Hs(butter_wc(Op, ap, N), N)
    b2, a2 = bilinear(n2, d2, 1.0)
    chk("7.3alt |H| at wp", abs(freqz(b2, a2, wp)), 0.89125, 5e-5)
    chk("7.3alt |H| at ws <= 0.17783", min(abs(freqz(b2, a2, ws)), 0.17783),
        abs(freqz(b2, a2, ws)), 1e-12)

    # impulse-invariance H(z), Proakis form with T = 1
    Nx, N, Op, Os = butter_order(wp, ws, ap, asb, 1.0, "invariance")
    num, den = butter_Hs(butter_wc(Op, ap, N), N)
    bi, ai = impulse_invariance(num, den, 1.0)
    poles, A = residues(num, den)
    # published parallel sections, first one 0.2871 - 0.4466 z^-1 over
    # 1 - 1.2971 z^-1 + 0.6949 z^-2
    pairs = []
    for k, pk in enumerate(poles):
        if pk.imag > 0:
            j = min(range(len(poles)),
                    key=lambda i: abs(poles[i] - pk.conjugate()))
            zp, zq = cmath.exp(pk), cmath.exp(poles[j])
            e0 = A[k] + A[j]
            e1 = -(A[k] * zq + A[j] * zp)
            pairs.append((e0.real, e1.real, -(zp + zq).real, (zp * zq).real))
    pairs.sort(key=lambda t: t[3], reverse=True)
    chk("7.2 parallel 1", list(pairs[0]), [0.2871, -0.4466, -1.2971, 0.6949], 2e-3)
    chk("7.2 parallel 2", list(pairs[1]), [-2.1428, 1.1455, -1.0691, 0.3699], 2e-3)
    chk("7.2 parallel 3", list(pairs[2]), [1.8557, -0.6303, -0.9972, 0.2570], 2e-3)

    # --- Chebyshev, same spec: N = 4, eps = 0.50885 -----------------------
    Nx, N, Op, Os = cheb_order(wp, ws, ap, asb, 1.0, "invariance")
    chk("cheb N", N, 4)
    eps = cheb_eps(ap)
    chk("cheb eps", eps, 0.50885, 1e-4)
    alpha, a_, b_ = cheb_ab(eps, N)
    chk("cheb alpha", alpha, 4.1702, 1e-3)
    chk("cheb a", a_, 0.3646, 1e-3)
    chk("cheb b", b_, 1.0644, 1e-3)
    cp = cheb_poles(0.2 * pi, eps, N)
    got = sorted([(round(p.real, 4), round(abs(p.imag), 4)) for p in cp])
    chk("cheb pole 1", list(got[0]), [-0.21166, 0.25593], 2e-4)
    chk("cheb pole 3", list(got[2]), [-0.087673, 0.61788], 2e-4)
    cn, cd = cheb_Hs(0.2 * pi, eps, N)
    chk("cheb gain", cn[0], 0.038286, 1e-5)
    csec = sorted([tuple(round(v, 4) for v in s[:2]) for s in sections(cp)])
    chk("cheb section 1", list(csec[0]), [0.1103, 0.4233], 2e-3)
    chk("cheb section 2", list(csec[1]), [0.3894, 0.1753], 2e-3)

    # --- digital LP -> HP, Oppenheim example 7.6 --------------------------
    chk("LP->HP alpha", lp_to_hp(0.2 * pi, 0.6 * pi), -0.38197, 1e-5)
    chk("LP->LP alpha zero", lp_to_lp(0.3 * pi, 0.3 * pi), 0.0, 1e-12)

    # a mapped filter must hit the same gain at the mapped edge
    _, N, Op, Os = butter_order(wp, ws, ap, asb, 1.0)
    num, den = butter_Hs(butter_wc(Op, ap, N), N)
    b, a = bilinear(num, den, 1.0)
    hb, ha, al = hp_from_lp(b, a, 0.2 * pi, 0.6 * pi)
    chk("HP maps the passband edge", abs(freqz(hb, ha, 0.6 * pi)),
        abs(freqz(b, a, 0.2 * pi)), 1e-6)
    chk("HP kills DC", abs(freqz(hb, ha, 0.0)), 0.0, 1e-9)

    # --- structural checks -------------------------------------------------
    # every bilinear Butterworth LPF has all its zeros at z = -1
    for wpx, wsx, apx, asx in [(0.25 * pi, 0.55 * pi, 1.0122, 13.5556),
                               (0.3 * pi, 0.4 * pi, 1.0122, 13.5556)]:
        _, N, Op, Os = butter_order(wpx, wsx, apx, asx)
        num, den = butter_Hs(butter_wc(Op, apx, N), N)
        b, a = bilinear(num, den, 1.0)
        # the numerator is exactly b[0] (1 + z^-1)^N: check the binomials,
        # which is sharper than root-finding an N-fold root
        binom = [1.0]
        for k in range(N):
            binom = [x + y for x, y in zip(binom + [0.0], [0.0] + binom)]
        chk("zeros at -1 (N=%d)" % N, b, [b[0] * c for c in binom], 1e-12)
        chk("stable (N=%d)" % N, 1 if max(abs(r) for r in zroots(a)) < 1.0
            else 0, 1)
        chk("unity DC gain (N=%d)" % N, abs(freqz(b, a, 0.0)), 1.0, 1e-9)

    # delta -> alpha round trip
    chk("delta_p 0.11", alpha_from_ripple(0.11, "pass"), 1.0122, 1e-4)
    chk("delta_s 0.21", alpha_from_ripple(0.21, "stop"), 13.5556, 1e-4)
    chk("Hz to rad", w_from_hz(1200, 8000), 0.3 * pi, 1e-12)

    bilinear_T_cancels()


# ------------------------------------------------------------------ report ---
def fmt(p, var="z^-1"):
    out = []
    for i, c in enumerate(p):
        if abs(c) < 1e-12:
            continue
        s = "%+.5g" % c
        if i:
            s += " %s^%d" % (var, i) if i > 1 else " %s" % var
        out.append(s)
    return " ".join(out) if out else "0"


BILINEAR_BUTTER = [
    ("80 Bh, 81 Bh", 0.5, 0.75, alpha_from_gain(0.9), alpha_from_gain(0.2), 1.0),
    ("81 Ba", 0.35, 0.70, alpha_from_gain(0.6), alpha_from_gain(0.1), 0.1),
    ("75 Ch, 70 Ch, 82 Ba", 0.2, 0.6, alpha_from_gain(0.8),
     alpha_from_gain(0.2), 1.0),
    ("78 Ch", 0.22, 0.58, alpha_from_gain(0.82), alpha_from_gain(0.18), 1.0),
    ("73 Ch", 0.5, 0.75, alpha_from_gain(0.707), alpha_from_gain(0.2), 1.0),
    ("73 Shr", 0.2, 0.3, alpha_from_gain(0.89125), alpha_from_gain(0.17783), 1.0),
    ("80 Ba", 0.26, 0.58, 0.99, 14.99, 2.0),
    ("79 Ba", 0.24, 0.57, 0.98, 14.95, 2.0),
    ("79 Ch, 72 Ash", 0.24, 0.57, 1.0, 14.9, 2.0),
    ("73 Bh", 0.25, 0.59, 0.99, 14.85, 2.0),
    ("71 Bh", 0.25, 0.55, 1.0, 15.0, 2.0),
    ("72 Ka", 0.25, 0.45, 1.0, 15.0, 1.0),
    ("71 Shr", 0.2, 0.4, 1.0, 15.0, 1.0),
    ("77 Ch", 0.2, 0.3, 1.0, 15.0, 1.0),
    ("73 Ma", 0.2, 0.5, 0.98, 20.0, 1.0),
    ("79 Bh, 71 Ch, 69 Ch", 0.25, 0.55, alpha_from_ripple(0.11, "pass"),
     alpha_from_ripple(0.21, "stop"), 2.0),
    ("76 Ash", 0.22, 0.54, alpha_from_ripple(0.11, "pass"),
     alpha_from_ripple(0.22, "stop"), 2.0),
    ("74 Ash", 0.27, 0.58, alpha_from_ripple(0.11, "pass"),
     alpha_from_ripple(0.21, "stop"), 2.0),
    ("66 Ma", 0.3, 0.4, alpha_from_ripple(0.11, "pass"),
     alpha_from_ripple(0.21, "stop"), 1.0),
    ("68 Bh", 0.25, 0.45, alpha_from_ripple(0.17, "pass"),
     alpha_from_ripple(0.27, "stop"), 1.0),
    ("75 Ash, 74 Bh", 0.15, 0.6, 0.7, 14.0, 1.0),
    ("76 Bh", 0.2, 0.3, 1.0, 15.0, 1.0),
    ("76 Ch", 1200 / 4000.0, 2500 / 4000.0, 1.0, 40.0, 1.0),
    ("82 Bh", 350 / 2500.0, 1000 / 2500.0, 3.0, 10.0, 1.0),
]

# 70 Bh cannot go in the table above: 170 Hz against a 256 Hz sampling rate
# is past the 128 Hz Nyquist limit, so tan(w/2) turns negative and there is
# no digital spec to pre-warp.  Reported separately, both readings.
DEFECTIVE = [("70 Bh", 120.0, 170.0, 1.0, 16.0, 256.0)]

INVARIANCE_BUTTER = [
    ("78 Bh, 72 Ch", 200 / 2500.0, 500 / 2500.0, 5.0, 12.0, 1 / 5000.0),
    ("81 Ch, 80 Ch, 69 Bh", 0.25, 0.55, 0.5, 15.0, 1.0),
    ("70 Asa", 0.2, 0.35, 0.5, 15.0, 1.0),
    ("74 Ch", 0.15, 0.6, 0.7, 14.0, 1.0),
]

CHEBYSHEV = [
    ("72 Ma", 0.2, 0.5, alpha_from_gain(0.707), alpha_from_gain(0.1), 1.0),
    ("74 Ma", 0.2, 0.3, 1.0, 15.0, 1.0),
    ("70 Ma", 0.25, 0.55, 1.01, 13.55, 2.0),
]


def report():
    pi = math.pi
    print("=" * 74)
    print("BILINEAR - BUTTERWORTH   (%d papers)" % len(BILINEAR_BUTTER))
    print("=" * 74)
    print("%-22s %7s %7s %8s %8s %3s %9s" %
          ("papers", "wp/pi", "ws/pi", "alpha_p", "alpha_s", "N", "Omega_c"))
    for name, wp, ws, ap, asb, T in BILINEAR_BUTTER:
        Nx, N, Op, Os = butter_order(wp * pi, ws * pi, ap, asb, T)
        Oc = butter_wc(Op, ap, N)
        print("%-22s %7.4g %7.4g %8.4f %8.4f %3d %9.5f   (N exact %.4f)" %
              (name, wp, ws, ap, asb, N, Oc, Nx))
    print()
    for name, wp, ws, ap, asb, T in BILINEAR_BUTTER:
        _, N, Op, Os = butter_order(wp * pi, ws * pi, ap, asb, T)
        Oc = butter_wc(Op, ap, N)
        num, den = butter_Hs(Oc, N)
        b, a = bilinear(num, den, T)
        print("%-22s N=%d  H(z) = [%s] / [%s]" % (name, N, fmt(b), fmt(a)))
    print()
    print("-" * 74)
    print("DEFECTIVE: stopband edge above Nyquist")
    for name, fp, fsb, ap, asb, fs in DEFECTIVE:
        wp, ws = w_from_hz(fp, fs), w_from_hz(fsb, fs)
        print("%-22s fp=%g Hz fs_edge=%g Hz Fs=%g Hz -> wp=%.4fpi ws=%.4fpi"
              % (name, fp, fsb, fs, wp / pi, ws / pi))
        try:
            butter_order(wp, ws, ap, asb, 1.0 / fs)
        except ValueError as e:
            print("%-22s   as printed: %s" % ("", e))
        # the only workable reading: analog edges, no pre-warping
        Nx, N, Op, Os = butter_order(2 * pi * fp, 2 * pi * fsb, ap, asb,
                                     1.0, "bilinear", warp=False)
        Oc = butter_wc(Op, ap, N)
        num, den = butter_Hs(Oc, N)
        b, a = bilinear(num, den, 1.0 / fs)
        print("%-22s   analog reading: Op=%.4g Os=%.4g N=%d (exact %.4f) "
              "Oc=%.5g" % ("", Op, Os, N, Nx, Oc))
        print("%-22s   H(z) = [%s] / [%s]" % ("", fmt(b), fmt(a)))
    print()
    print("=" * 74)
    print("IMPULSE INVARIANCE - BUTTERWORTH   (%d papers)" % len(INVARIANCE_BUTTER))
    print("=" * 74)
    for name, wp, ws, ap, asb, T in INVARIANCE_BUTTER:
        Nx, N, Op, Os = butter_order(wp * pi, ws * pi, ap, asb, T, "invariance")
        Oc = butter_wc(Op, ap, N)
        num, den = butter_Hs(Oc, N)
        b, a = impulse_invariance(num, den, T)
        print("%-22s Op=%.5g Os=%.5g N=%d (exact %.4f) Oc=%.5g" %
              (name, Op, Os, N, Nx, Oc))
        print("%-22s   poles s = %s" %
              ("", ", ".join("%.4f%+.4fj" % (p.real, p.imag)
                             for p in butter_poles(Oc, N))))
        print("%-22s   H(z) = [%s] / [%s]" % ("", fmt(b), fmt(a)))
    print()
    print("=" * 74)
    print("BILINEAR - CHEBYSHEV   (%d papers)" % len(CHEBYSHEV))
    print("=" * 74)
    for name, wp, ws, ap, asb, T in CHEBYSHEV:
        Nx, N, Op, Os = cheb_order(wp * pi, ws * pi, ap, asb, T)
        eps = cheb_eps(ap)
        alpha, a_, b_ = cheb_ab(eps, N)
        num, den = cheb_Hs(Op, eps, N)
        bz, az = bilinear(num, den, T)
        print("%-22s Op=%.5g Os=%.5g eps=%.5f N=%d (exact %.4f)" %
              (name, Op, Os, eps, N, Nx))
        print("%-22s   alpha=%.4f a=%.4f b=%.4f  poles %s" %
              ("", alpha, a_, b_,
               ", ".join("%.4f%+.4fj" % (p.real, p.imag)
                         for p in cheb_poles(Op, eps, N))))
        print("%-22s   H(s) = %.6g / [%s]" % ("", num[0], fmt(den, "s")))
        print("%-22s   H(z) = [%s] / [%s]" % ("", fmt(bz), fmt(az)))
    print()
    print("=" * 74)
    print("SPECTRAL TRANSFORMATION")
    print("=" * 74)
    print("79 Bh, 71 Ch, 69 Ch   LP 0.25pi -> HP 0.45pi : alpha = %.5f" %
          lp_to_hp(0.25 * pi, 0.45 * pi))
    b, a = [0.1, 0.4], [1.0, -0.6, 0.1]
    hb, ha, al = hp_from_lp(b, a, 0.2575 * pi, 0.3567 * pi)
    print("70 Ch                 LP 0.2575pi -> HP 0.3567pi : alpha = %.5f" % al)
    print("%-22s   H(z) = [%s] / [%s]" % ("", fmt(hb), fmt(ha)))
    print("%-22s   |H_lp(0.2575pi)| = %.6f, |H_hp(0.3567pi)| = %.6f" %
          ("", abs(freqz(b, a, 0.2575 * pi)), abs(freqz(hb, ha, 0.3567 * pi))))


if __name__ == "__main__":
    selftest()
    if FAIL:
        print("SELF-TEST FAILURES (%d of %d)" % (len(FAIL), len(FAIL) + OK[0]))
        for f in FAIL:
            print("  " + f)
        raise SystemExit(1)
    print("iir.py self-tests: %d/%d pass\n" % (OK[0], OK[0]))
    report()
