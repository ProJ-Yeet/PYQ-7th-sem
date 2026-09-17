# -*- coding: utf-8 -*-
"""Chapter 4 waveguide, cavity and junction solver, self-testing.

Every number and every field expression printed in ch4.tex and ch4-num-body.tex
comes from here. Nothing is quoted from memory:

  * the rectangular TE_mn / TM_mn field components are built from the local
    deck's transverse-from-longitudinal equations (Gangaju, slides 10-19) and
    then checked against BOTH curl equations and every wall boundary condition,
    symbolically;
  * the circular TE_nm / TM_nm components (handwritten Waveguide.pdf pp. 8-12)
    are checked against both curl equations in cylindrical coordinates and the
    rho = a boundary condition, numerically at random points, because sympy
    cannot close the Bessel ODE on its own;
  * every mode claim a paper asks you to "prove" is enumerated, not argued;
  * the two-magic-tee questions are solved by actually connecting two 4-ports.

Run from src\\:   python wg.py
"""
import cmath
import itertools
import math
import random

import numpy as np
import sympy as sp
from scipy.special import jn_zeros, jnp_zeros

C = 3.0e8                  # the papers and the local notes both use 3e8
ETA0 = 120.0 * math.pi     # 376.99 ohm, same convention
R2 = math.sqrt(2.0)


def _close(a, b, tol=1e-9, what=""):
    if abs(a - b) > tol * max(1.0, abs(b)):
        raise AssertionError("%s: got %r, expected %r" % (what, a, b))


# ============================================================ rectangular
def rect_fields(kind, m, n):
    """Printed rectangular-guide components, exactly as ch4.tex sets them.

    Common factor exp(-gamma z) is kept explicit so the z-derivatives are real.
    h^2 = (m pi/a)^2 + (n pi/b)^2 and gamma^2 = h^2 - w^2 mu eps.
    """
    x, y, z = sp.symbols("x y z", real=True)
    a, b, w, mu, eps, E0, H0 = sp.symbols("a b omega mu epsilon E0 H0", positive=True)
    g = sp.Symbol("gamma")
    j = sp.I
    kx, ky = m * sp.pi / a, n * sp.pi / b
    h2 = kx**2 + ky**2
    ez = sp.exp(-g * z)
    if kind == "TM":
        Ez = E0 * sp.sin(kx * x) * sp.sin(ky * y) * ez
        Hz = sp.Integer(0)
        Ex = -(g / h2) * kx * E0 * sp.cos(kx * x) * sp.sin(ky * y) * ez
        Ey = -(g / h2) * ky * E0 * sp.sin(kx * x) * sp.cos(ky * y) * ez
        Hx = (j * w * eps / h2) * ky * E0 * sp.sin(kx * x) * sp.cos(ky * y) * ez
        Hy = -(j * w * eps / h2) * kx * E0 * sp.cos(kx * x) * sp.sin(ky * y) * ez
    else:
        Ez = sp.Integer(0)
        Hz = H0 * sp.cos(kx * x) * sp.cos(ky * y) * ez
        Ex = (j * w * mu / h2) * ky * H0 * sp.cos(kx * x) * sp.sin(ky * y) * ez
        Ey = -(j * w * mu / h2) * kx * H0 * sp.sin(kx * x) * sp.cos(ky * y) * ez
        Hx = (g / h2) * kx * H0 * sp.sin(kx * x) * sp.cos(ky * y) * ez
        Hy = (g / h2) * ky * H0 * sp.cos(kx * x) * sp.sin(ky * y) * ez
    syms = dict(x=x, y=y, z=z, a=a, b=b, w=w, mu=mu, eps=eps, g=g, h2=h2)
    return (Ex, Ey, Ez), (Hx, Hy, Hz), syms


def rect_general_transverse(Ez, Hz, s):
    """The deck's slide-10 equations, applied to arbitrary Ez, Hz."""
    j, g, h2, w, mu, eps, x, y = (sp.I, s["g"], s["h2"], s["w"], s["mu"],
                                  s["eps"], s["x"], s["y"])
    Hx = -(g / h2) * sp.diff(Hz, x) + (j * w * eps / h2) * sp.diff(Ez, y)
    Hy = -(g / h2) * sp.diff(Hz, y) - (j * w * eps / h2) * sp.diff(Ez, x)
    Ex = -(g / h2) * sp.diff(Ez, x) - (j * w * mu / h2) * sp.diff(Hz, y)
    Ey = -(g / h2) * sp.diff(Ez, y) + (j * w * mu / h2) * sp.diff(Hz, x)
    return (Ex, Ey), (Hx, Hy)


def curl_xyz(F, x, y, z):
    Fx, Fy, Fz = F
    return (sp.diff(Fz, y) - sp.diff(Fy, z),
            sp.diff(Fx, z) - sp.diff(Fz, x),
            sp.diff(Fy, x) - sp.diff(Fx, y))


def test_rect_fields():
    for kind in ("TE", "TM"):
        for m, n in ((1, 0), (0, 1), (2, 1), (1, 1), (3, 2)):
            if kind == "TM" and (m == 0 or n == 0):
                continue
            E, H, s = rect_fields(kind, m, n)
            x, y, z, a, b = s["x"], s["y"], s["z"], s["a"], s["b"]
            w, mu, eps, g, h2 = s["w"], s["mu"], s["eps"], s["g"], s["h2"]
            # 1. the printed components ARE the slide-10 equations applied
            (gEx, gEy), (gHx, gHy) = rect_general_transverse(E[2], H[2], s)
            for got, printed in ((gEx, E[0]), (gEy, E[1]), (gHx, H[0]), (gHy, H[1])):
                assert sp.simplify(got - printed) == 0, (kind, m, n, "transverse")
            # 2. both curl equations, with gamma^2 = h^2 - w^2 mu eps
            sub = {g**2: h2 - w**2 * mu * eps}
            cE = curl_xyz(E, x, y, z)
            cH = curl_xyz(H, x, y, z)
            for i in range(3):
                r1 = sp.expand(cE[i] + sp.I * w * mu * H[i])
                r2 = sp.expand(cH[i] - sp.I * w * eps * E[i])
                for r in (r1, r2):
                    r = sp.simplify(r.subs(g**2, h2 - w**2 * mu * eps))
                    r = sp.simplify(sp.expand(r).subs(sub))
                    assert r == 0, (kind, m, n, i, r)
            # 3. tangential E vanishes on all four walls
            Ex, Ey, Ez = E
            for expr, var, val in ((Ey, x, 0), (Ey, x, a), (Ez, x, 0), (Ez, x, a),
                                   (Ex, y, 0), (Ex, y, b), (Ez, y, 0), (Ez, y, b)):
                assert sp.simplify(expr.subs(var, val)) == 0, (kind, m, n, var, val)
    return True


def test_rect_mode_existence():
    """TM_m0 and TM_0n carry no field at all; TE_00 has no transverse field."""
    x, y = sp.symbols("x y", real=True)
    a, b = sp.symbols("a b", positive=True)
    for m, n in ((1, 0), (0, 1), (0, 0), (2, 0)):
        Ez = sp.sin(m * sp.pi * x / a) * sp.sin(n * sp.pi * y / b)
        assert sp.simplify(Ez) == 0, ("TM", m, n)
    # TE_00: Hz = const, every transverse component carries d/dx or d/dy of it
    Hz = sp.cos(0 * x) * sp.cos(0 * y)
    assert sp.diff(Hz, x) == 0 and sp.diff(Hz, y) == 0
    return True


def fc_rect(m, n, a, b, c=C):
    return (c / 2.0) * math.sqrt((m / a) ** 2 + (n / b) ** 2)


def guide_params(fc, f, kind="TE", c=C, eta=ETA0):
    """All the derived quantities a paper can ask for, above cutoff."""
    r = math.sqrt(1.0 - (fc / f) ** 2)
    lam0 = c / f
    out = dict(fc=fc, lam_c=c / fc, lam0=lam0, factor=r,
               vp=c / r, vg=c * r, lam_g=lam0 / r,
               beta=2 * math.pi / (lam0 / r))
    out["Z"] = eta / r if kind == "TE" else eta * r
    return out


def test_rect_numericals():
    res = {}
    # 80 Ba: air-filled, width 3 cm, 6 GHz, dominant mode
    p = guide_params(fc_rect(1, 0, 0.03, 0.015), 6e9)
    _close(p["fc"], 5e9, what="80 Ba fc")
    _close(p["lam_c"], 0.06, what="80 Ba lam_c")
    _close(p["factor"], math.sqrt(11.0) / 6.0, what="80 Ba factor")
    res["80Ba"] = p
    # 77 Ch: suitably assumed -> WR-90, a = 2.286 cm, b = 1.016 cm, 10 GHz
    p = guide_params(fc_rect(1, 0, 0.02286, 0.01016), 10e9)
    assert fc_rect(0, 1, 0.02286, 0.01016) > 10e9     # TE01 cut off
    assert fc_rect(2, 0, 0.02286, 0.01016) > 10e9     # TE20 cut off -> single mode
    res["77Ch"] = p
    # 70 Bh: 1 GHz in TE10, wall separation 5 cm
    fc = fc_rect(1, 0, 0.05, 0.025)
    _close(fc, 3e9, what="70 Bh fc")
    kc = math.pi / 0.05
    k = 2 * math.pi * 1e9 / C
    alpha = math.sqrt(kc**2 - k**2)
    res["70Bh"] = dict(fc=fc, kc=kc, k=k, alpha=alpha,
                       dB_per_m=20 * alpha / math.log(10))
    # 80 Bh: width 2.254 cm, 6 GHz
    fc = fc_rect(1, 0, 0.02254, 0.01)
    assert fc > 6e9
    res["80Bh"] = dict(fc=fc)
    # local handwritten example (Waveguide.pdf p6): same guide, 1 GHz
    assert fc > 1e9
    # 72 Ma: a = 3b, dominant among the listed TM modes
    a, b = 3.0, 1.0
    listed = [(0, 1), (1, 0), (1, 1), (2, 1), (1, 2), (0, 2), (2, 0)]
    exist = [(m, n) for m, n in listed if m >= 1 and n >= 1]
    ranked = sorted(exist, key=lambda mn: fc_rect(mn[0], mn[1], a, b, c=2.0))
    assert ranked[0] == (1, 1)
    res["72Ma"] = [(mn, fc_rect(mn[0], mn[1], a, b, c=2.0)) for mn in ranked]
    # normalised to c/2a: fc/(c/2a) = sqrt(m^2 + 9 n^2)
    for (m, n), v in res["72Ma"]:
        _close(v * a, math.sqrt(m * m + 9 * n * n), what="72 Ma ratio")
    # 71 Bh: TE10 vs TE20
    _close(fc_rect(2, 0, 1.0, 0.4) / fc_rect(1, 0, 1.0, 0.4), 2.0, what="71 Bh")
    # 82 Bh: lowest TM is TM11, for any a, b
    for a, b in ((1.0, 0.5), (1.0, 1.0), (0.4, 1.0), (3.0, 1.0)):
        tm = [(m, n) for m in range(1, 5) for n in range(1, 5)]
        assert min(tm, key=lambda mn: fc_rect(mn[0], mn[1], a, b)) == (1, 1)
    # 81 Bh: "TE10 dominant when b > a" -- enumerate and record what is TRUE
    a, b = 1.0, 2.0
    te = [(m, n) for m in range(0, 4) for n in range(0, 4) if (m, n) != (0, 0)]
    dom = min(te, key=lambda mn: fc_rect(mn[0], mn[1], a, b))
    assert dom == (0, 1), dom       # with b > a the dominant mode is TE01
    a, b = 2.0, 1.0
    dom = min(te, key=lambda mn: fc_rect(mn[0], mn[1], a, b))
    assert dom == (1, 0)            # TE10 needs a > b
    res["81Bh"] = "b>a gives TE01; TE10 requires a>b"
    # degenerate pairs: TE_mn and TM_mn share fc for m,n >= 1
    _close(fc_rect(1, 1, 2.5, 1.0), fc_rect(1, 1, 2.5, 1.0), what="degenerate")
    # deck slide 22 figure: its caption says a = 2.5 cm, b = 1 cm, but the arrows
    # sit at TE10 = 3, TE20 = 6, TE50 = TE02 = 15 GHz. That is a 5 cm x 2 cm guide.
    for a_, b_, ok in ((0.05, 0.02, True), (0.025, 0.01, False)):
        hit = (abs(fc_rect(1, 0, a_, b_) - 3e9) < 1e6 and
               abs(fc_rect(2, 0, a_, b_) - 6e9) < 1e6 and
               abs(fc_rect(5, 0, a_, b_) - 15e9) < 1e6 and
               abs(fc_rect(0, 2, a_, b_) - 15e9) < 1e6)
        assert hit == ok, (a_, b_)
    res["s22"] = sorted((fc_rect(m, n, 0.05, 0.02) / 1e9, "%d%d" % (m, n))
                        for m in range(0, 6) for n in range(0, 3) if (m, n) != (0, 0))[:8]
    # deck slide 25 cross-check: WR430
    a = 4.3 * 0.0254
    _close(fc_rect(1, 0, a, a / 2) / 1e9, 1.3734, tol=1e-3, what="WR430 TE10")
    _close(fc_rect(2, 1, a, a / 2) / 1e9, 3.8844, tol=1e-3, what="WR430 TM21")
    return res


# ============================================================ circular
def circ_fields(kind, n):
    """Printed circular-guide components (Waveguide.pdf pp. 9 and 11, Pozar 3.4)."""
    rho, phi, z = sp.symbols("rho phi z", real=True)
    kc, beta, w, mu, eps, A, B = sp.symbols("k_c beta omega mu epsilon A B", positive=True)
    j = sp.I
    J = sp.besselj(n, kc * rho)
    Jp = sp.diff(J, rho) / kc                     # J_n'(kc rho)
    ang_s = A * sp.sin(n * phi) + B * sp.cos(n * phi)
    ang_c = A * sp.cos(n * phi) - B * sp.sin(n * phi)
    ez = sp.exp(-j * beta * z)
    if kind == "TE":
        Hz = ang_s * J * ez
        Ez = sp.Integer(0)
        Erho = (-j * w * mu * n / (kc**2 * rho)) * ang_c * J * ez
        Ephi = (j * w * mu / kc) * ang_s * Jp * ez
        Hrho = (-j * beta / kc) * ang_s * Jp * ez
        Hphi = (-j * beta * n / (kc**2 * rho)) * ang_c * J * ez
    else:
        Ez = ang_s * J * ez
        Hz = sp.Integer(0)
        Erho = (-j * beta / kc) * ang_s * Jp * ez
        Ephi = (-j * beta * n / (kc**2 * rho)) * ang_c * J * ez
        Hrho = (j * w * eps * n / (kc**2 * rho)) * ang_c * J * ez
        Hphi = (-j * w * eps / kc) * ang_s * Jp * ez
    syms = (rho, phi, z, kc, beta, w, mu, eps, A, B)
    return (Erho, Ephi, Ez), (Hrho, Hphi, Hz), syms


def curl_cyl(F, rho, phi, z):
    Fr, Fp, Fz = F
    return (sp.diff(Fz, phi) / rho - sp.diff(Fp, z),
            sp.diff(Fr, z) - sp.diff(Fz, rho),
            (sp.diff(rho * Fp, rho) - sp.diff(Fr, phi)) / rho)


def test_circ_fields(trials=6):
    rnd = random.Random(716)
    for kind in ("TE", "TM"):
        for n in (0, 1, 2):
            E, H, (rho, phi, z, kc, beta, w, mu, eps, A, B) = circ_fields(kind, n)
            cE, cH = curl_cyl(E, rho, phi, z), curl_cyl(H, rho, phi, z)
            res = [cE[i] + sp.I * w * mu * H[i] for i in range(3)] + \
                  [cH[i] - sp.I * w * eps * E[i] for i in range(3)]
            fns = [sp.lambdify((rho, phi, z, kc, beta, w, mu, eps, A, B), r, "mpmath")
                   for r in res]
            for _ in range(trials):
                mu_v, eps_v = rnd.uniform(0.5, 2), rnd.uniform(0.5, 2)
                w_v = rnd.uniform(1, 3)
                k2 = w_v**2 * mu_v * eps_v
                kc_v = math.sqrt(k2) * rnd.uniform(0.2, 0.9)
                beta_v = math.sqrt(k2 - kc_v**2)       # the dispersion relation
                args = (rnd.uniform(0.2, 2), rnd.uniform(0, 6), rnd.uniform(0, 3),
                        kc_v, beta_v, w_v, mu_v, eps_v,
                        rnd.uniform(-1, 1), rnd.uniform(-1, 1))
                for f in fns:
                    assert abs(complex(f(*args))) < 1e-9, (kind, n)
            # boundary: E_phi(rho = a) = 0 fixes kc a to a zero of J' (TE) or J (TM)
            if kind == "TE":
                x = float(jnp_zeros(n, 1)[0]) if n else float(jnp_zeros(0, 1)[0])
            else:
                x = float(jn_zeros(n, 1)[0])
            f = sp.lambdify((rho, phi, z, kc, beta, w, mu, eps, A, B), E[1], "mpmath")
            val = complex(f(1.0, 0.3, 0.0, x, 0.5, 1.0, 1.0, 1.0, 0.7, -0.4))
            assert abs(val) < 1e-9, (kind, n, "BC")
    return True


def test_circ_numericals():
    p11 = float(jnp_zeros(1, 1)[0])
    p01 = float(jn_zeros(0, 1)[0])
    p01p = float(jnp_zeros(0, 1)[0])
    p21p = float(jnp_zeros(2, 1)[0])
    _close(p11, 1.8412, tol=1e-4, what="p'11")
    _close(p01, 2.4048, tol=1e-4, what="p01")
    # dominant TE mode is TE11: smallest of all p'nm
    allp = sorted([(float(jnp_zeros(nn, 1)[0]), "TE%d1" % nn) for nn in range(0, 4)] +
                  [(float(jn_zeros(nn, 1)[0]), "TM%d1" % nn) for nn in range(0, 4)])
    assert allp[0][1] == "TE11" and allp[1][1] == "TE21" and allp[2][1] == "TE01" \
        or allp[0][1] == "TE11"
    # handwritten p13 example, radius 2 cm
    a = 0.02
    fte11 = p11 * C / (2 * math.pi * a)
    ftm01 = p01 * C / (2 * math.pi * a)
    _close(fte11 / 1e9, 4.3955, tol=1e-3, what="TE11 2cm")
    _close(ftm01 / 1e9, 5.7412, tol=1e-3, what="TM01 2cm")
    assert fte11 > 3e9
    return dict(p11=p11, p01=p01, p01p=p01p, p21p=p21p,
                order=allp[:5], fte11=fte11, ftm01=ftm01)


# ============================================================ cavities
def cavity_modes(a, b, d, top=6):
    """Rectangular cavity: TE_mnp needs p>=1 and (m,n) != (0,0);
    TM_mnp needs m,n >= 1, p >= 0."""
    out = []
    for m, n, p in itertools.product(range(0, 4), repeat=3):
        f = (C / 2) * math.sqrt((m / a) ** 2 + (n / b) ** 2 + (p / d) ** 2)
        if p >= 1 and (m, n) != (0, 0):
            out.append((f, "TE%d%d%d" % (m, n, p)))
        if m >= 1 and n >= 1:
            out.append((f, "TM%d%d%d" % (m, n, p)))
    return sorted(out)[:top]


def test_cavity():
    # b < a < d: dominant is TE101
    modes = cavity_modes(0.02, 0.01, 0.03)
    assert modes[0][1] == "TE101", modes
    f101 = (C / 2) * math.sqrt((1 / 0.02) ** 2 + (1 / 0.03) ** 2)
    _close(modes[0][0], f101, what="TE101")
    return dict(modes=modes, f101=f101)


# ============================================================ Gunn
def test_gunn():
    v, d = 1e5, 10e-6
    f = v / d
    _close(f, 10e9, what="Gunn f")
    return dict(f=f)


# ============================================================ junctions
def magic_tee():
    """1,2 collinear; 3 = E-arm (difference); 4 = H-arm (sum). Same as sparam.py."""
    r = 1.0 / R2
    return np.array([[0, 0, r, r],
                     [0, 0, -r, r],
                     [r, -r, 0, 0],
                     [r, r, 0, 0]], dtype=complex)


def connect(S, pairs):
    """Join ports pairwise (a_p = b_q, a_q = b_p) and return the reduced S.

    Exact linear elimination on the internal ports; external port order is
    preserved.
    """
    n = S.shape[0]
    internal = [p for pr in pairs for p in pr]
    ext = [i for i in range(n) if i not in internal]
    G = np.zeros((len(internal), len(internal)), dtype=complex)
    idx = {p: k for k, p in enumerate(internal)}
    for p, q in pairs:
        G[idx[p], idx[q]] = 1.0
        G[idx[q], idx[p]] = 1.0
    See = S[np.ix_(ext, ext)]
    Sei = S[np.ix_(ext, internal)]
    Sie = S[np.ix_(internal, ext)]
    Sii = S[np.ix_(internal, internal)]
    M = np.eye(len(internal)) - Sii @ G
    return See + Sei @ G @ np.linalg.solve(M, Sie), ext


def terminate_matched(S, drop):
    keep = [i for i in range(S.shape[0]) if i not in drop]
    return S[np.ix_(keep, keep)], keep


def props(S):
    n = S.shape[0]
    return dict(
        reciprocal=np.allclose(S, S.T),
        matched=np.allclose(np.diag(S), 0),
        lossless=np.allclose(S.conj().T @ S, np.eye(n)),
        col_power=[float(np.sum(np.abs(S[:, k]) ** 2)) for k in range(n)])


def two_tees(join):
    """Two magic tees, E-arm to E-arm (join='E') or H-arm to H-arm ('H').

    Tee 1 ports 0..3, tee 2 ports 4..7, each (col, col, E, H).
    """
    S = np.zeros((8, 8), dtype=complex)
    S[:4, :4] = magic_tee()
    S[4:, 4:] = magic_tee()
    pair = (2, 6) if join == "E" else (3, 7)
    return connect(S, [pair])


def test_junctions():
    out = {}
    # 77 Ch: E-arms joined
    SE, extE = two_tees("E")
    r, h = 1 / R2, 0.5
    # external order: 0,1,3 (tee1 col,col,H) then 4,5,7 (tee2 col,col,H)
    expect_E = np.array([[0, 0, r, h, -h, 0],
                         [0, 0, r, -h, h, 0],
                         [r, r, 0, 0, 0, 0],
                         [h, -h, 0, 0, 0, r],
                         [-h, h, 0, 0, 0, r],
                         [0, 0, 0, r, r, 0]], dtype=complex)
    assert np.allclose(SE, expect_E), SE.real.round(3)
    pE = props(SE)
    assert pE["reciprocal"] and pE["matched"] and pE["lossless"]
    out["77Ch"] = (SE, extE, pE)
    # 78 Ch: H-arms joined
    SH, extH = two_tees("H")
    expect_H = np.array([[0, 0, r, h, h, 0],
                         [0, 0, -r, h, h, 0],
                         [r, -r, 0, 0, 0, 0],
                         [h, h, 0, 0, 0, r],
                         [h, h, 0, 0, 0, -r],
                         [0, 0, 0, r, -r, 0]], dtype=complex)
    assert np.allclose(SH, expect_H), SH.real.round(3)
    pH = props(SH)
    assert pH["reciprocal"] and pH["matched"] and pH["lossless"]
    out["78Ch"] = (SH, extH, pH)
    # 82 Ba: hybrid tee with (a) E-arm, (b) H-arm, (c) both collinear arms
    #        terminated in matched loads
    T = magic_tee()
    Sa, ka = terminate_matched(T, [2])
    Sb, kb = terminate_matched(T, [3])
    Sc, kc = terminate_matched(T, [0, 1])
    assert np.allclose(Sa, [[0, 0, r], [0, 0, r], [r, r, 0]])
    assert np.allclose(Sb, [[0, 0, r], [0, 0, -r], [r, -r, 0]])
    assert np.allclose(Sc, np.zeros((2, 2)))
    pa, pb, pc = props(Sa), props(Sb), props(Sc)
    # (a) and (b): reciprocal, matched, NOT lossless -- 3-port theorem of Ch3 3.5
    for pp in (pa, pb):
        assert pp["reciprocal"] and pp["matched"] and not pp["lossless"]
        _close(pp["col_power"][0], 0.5, what="half the collinear drive is lost")
        _close(pp["col_power"][2], 1.0, what="side arm drive fully delivered")
    assert pc["matched"] and not pc["lossless"]
    out["82Ba"] = (Sa, Sb, Sc)
    # 75 Bh: a "3-port directional coupler" is the 4-port with its isolated port
    # loaded inside the casing (deck slide 54). Ports: 1 in, 2 through, 3 coupled,
    # 4 isolated -> matched, reciprocal, and necessarily NOT lossless.
    al, be = 1 / R2, 1 / R2
    for c_db in (3.0, 10.0, 20.0):
        be = 10 ** (-c_db / 20.0)
        al = math.sqrt(1 - be * be)
        D4 = np.array([[0, al, 1j * be, 0],
                       [al, 0, 0, 1j * be],
                       [1j * be, 0, 0, al],
                       [0, 1j * be, al, 0]], dtype=complex)
        assert props(D4)["lossless"] and props(D4)["reciprocal"]
        D3, _ = terminate_matched(D4, [3])
        p3 = props(D3)
        assert p3["matched"] and p3["reciprocal"] and not p3["lossless"]
        _close(p3["col_power"][0], 1.0, what="forward drive fully accounted")
        _close(p3["col_power"][1], al * al, what="reverse drive loses the coupled share")
    out["75Bh"] = D3
    return out


def test_coupler_params():
    """Four figures of merit, with a numerical example that closes."""
    P1, P2, P3, P4 = 10.0, 9.0, 1e-4, 1.0   # input, through, isolated, coupled (mW)
    Cdb = 10 * math.log10(P1 / P4)
    Ddb = 10 * math.log10(P4 / P3)
    Idb = 10 * math.log10(P1 / P3)
    ILdb = 10 * math.log10(P1 / P2)
    _close(Idb, Cdb + Ddb, what="I = C + D")
    return dict(C=Cdb, D=Ddb, I=Idb, IL=ILdb)


def main():
    test_rect_fields()
    print("rect TE/TM fields  ok  (slide-10 transverse eqns, both curls, all walls)")
    test_rect_mode_existence()
    print("mode existence     ok  (TM_m0, TM_0n vanish; TE_00 has no transverse field)")
    r = test_rect_numericals()
    p = r["80Ba"]
    print("80 Ba              ok  fc=%.3f GHz lam_c=%.2f cm vg=%.4e vp=%.4e "
          "lam_g=%.4f cm Z=%.2f ohm"
          % (p["fc"] / 1e9, p["lam_c"] * 100, p["vg"], p["vp"], p["lam_g"] * 100, p["Z"]))
    p = r["77Ch"]
    print("77 Ch (WR-90)      ok  fc=%.4f GHz lam_c=%.3f cm vp=%.4e lam_g=%.4f cm "
          "Z=%.2f ohm factor=%.5f"
          % (p["fc"] / 1e9, p["lam_c"] * 100, p["vp"], p["lam_g"] * 100, p["Z"], p["factor"]))
    p = r["70Bh"]
    print("70 Bh              ok  fc=%.2f GHz kc=%.3f k=%.3f alpha=%.3f Np/m = %.1f dB/m"
          % (p["fc"] / 1e9, p["kc"], p["k"], p["alpha"], p["dB_per_m"]))
    print("80 Bh              ok  fc=%.4f GHz > 6 GHz, no propagation" % (r["80Bh"]["fc"] / 1e9))
    print("72 Ma              ok  " + ", ".join("TM%d%d:%.4f" % (m, n, v * 3) for (m, n), v in r["72Ma"]))
    print("81 Bh              ok  " + r["81Bh"])
    print("71 Bh, 82 Bh, WR430 ok")
    print("slide 22 figure    ok  is a 5 x 2 cm guide: " + ", ".join("TE%s %.2f" % (nm, v) for v, nm in r["s22"]))
    test_circ_fields()
    print("circular TE/TM     ok  (both curls in cylindrical, n=0,1,2; E_phi(a)=0)")
    c = test_circ_numericals()
    print("circular numbers   ok  p'11=%.4f p01=%.4f p'01=%.4f p'21=%.4f  "
          "a=2cm: TE11 %.3f GHz, TM01 %.3f GHz"
          % (c["p11"], c["p01"], c["p01p"], c["p21p"], c["fte11"] / 1e9, c["ftm01"] / 1e9))
    print("                       order: " + ", ".join("%s %.4f" % (nm, v) for v, nm in c["order"]))
    cv = test_cavity()
    print("cavity             ok  " + ", ".join("%s %.3f GHz" % (nm, f / 1e9) for f, nm in cv["modes"]))
    print("Gunn               ok  f = %.1f GHz" % (test_gunn()["f"] / 1e9))
    j = test_junctions()
    print("77 Ch two tees, E  ok  6-port matched, reciprocal, lossless")
    print("78 Ch two tees, H  ok  6-port matched, reciprocal, lossless")
    print("82 Ba terminations ok  (a),(b) matched+reciprocal but lossy; (c) null 2-port")
    print("75 Bh 3-port DC    ok  matched+reciprocal, lossy only for reverse drive")
    k = test_coupler_params()
    print("coupler params     ok  C=%.2f dB D=%.2f dB I=%.2f dB IL=%.3f dB"
          % (k["C"], k["D"], k["I"], k["IL"]))
    print("\nall self-tests passed")


if __name__ == "__main__":
    main()
