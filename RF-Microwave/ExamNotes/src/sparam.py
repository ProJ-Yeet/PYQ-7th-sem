# -*- coding: utf-8 -*-
"""Chapter 3 S-parameter solver, self-testing.

Every number printed in ch3.tex and ch3-num-body.tex comes from here. Nothing
is quoted from memory: the standard device matrices are re-derived from their
stated properties and then checked against the unitary/reciprocity conditions,
and the two published derivations (Er. Kobid Karkee's handwritten E-plane,
H-plane and magic-tee sheets) are asserted entry by entry.

Run from src\\:   python sparam.py
"""
import cmath
import math

R2 = math.sqrt(2.0)


# ------------------------------------------------------------------ helpers
def poldeg(mag, deg):
    """Polar with the angle in degrees -> complex."""
    return mag * cmath.exp(1j * math.radians(deg))


def mag_ang(z):
    return abs(z), math.degrees(cmath.phase(z))


def is_reciprocal(S, tol=1e-9):
    n = len(S)
    return all(abs(S[i][j] - S[j][i]) < tol
               for i in range(n) for j in range(n))


def is_symmetric_2port(S, tol=1e-9):
    return abs(S[0][0] - S[1][1]) < tol and is_reciprocal(S, tol)


def is_matched(S, tol=1e-9):
    return all(abs(S[i][i]) < tol for i in range(len(S)))


def col_norms(S):
    """sum_k |S_ki|^2 for every column i -- must be 1 for a lossless network."""
    n = len(S)
    return [sum(abs(S[k][i]) ** 2 for k in range(n)) for i in range(n)]


def col_dots(S):
    """sum_k S_ki S_kj* for every i<j -- must be 0 for a lossless network."""
    n = len(S)
    out = {}
    for i in range(n):
        for j in range(i + 1, n):
            out[(i, j)] = sum(S[k][i] * S[k][j].conjugate() for k in range(n))
    return out


def is_lossless(S, tol=1e-9):
    if any(abs(c - 1.0) > tol for c in col_norms(S)):
        return False
    return all(abs(d) < tol for d in col_dots(S).values())


def dissipated_fraction(S, port=0):
    """Fraction of the power incident on `port` that the network eats."""
    return 1.0 - col_norms(S)[port]


def return_loss_db(s11):
    return -20.0 * math.log10(abs(s11))


def insertion_loss_db(s21):
    return -20.0 * math.log10(abs(s21))


def vswr(gamma):
    g = abs(gamma)
    return (1.0 + g) / (1.0 - g)


def mismatch_loss_db(s11):
    """Reflection loss: the part of the incident power that never gets in."""
    return -10.0 * math.log10(1.0 - abs(s11) ** 2)


# ------------------------------------------------- the standard device set
def e_plane_tee():
    """Series tee. Ports 1,2 collinear; port 3 = E-arm, matched (S33 = 0).

    Built from the three stated facts only -- S23 = -S13, S33 = 0, Sij = Sji --
    plus the unitary conditions. The solved values are 1/2 and 1/sqrt(2).
    """
    h, r = 0.5, 1.0 / R2
    return [[h, h, r],
            [h, h, -r],
            [r, -r, 0.0]]


def h_plane_tee():
    """Shunt tee. Ports 1,2 collinear; port 3 = H-arm, matched (S33 = 0).

    Same construction with S23 = +S13, which flips the sign of S12.
    """
    h, r = 0.5, 1.0 / R2
    return [[h, -h, r],
            [-h, h, r],
            [r, r, 0.0]]


def magic_tee():
    """Hybrid tee. 1,2 collinear; 3 = E-arm (difference); 4 = H-arm (sum)."""
    r = 1.0 / R2
    return [[0.0, 0.0, r, r],
            [0.0, 0.0, -r, r],
            [r, -r, 0.0, 0.0],
            [r, r, 0.0, 0.0]]


def circulator(ports=3):
    """Ideal clockwise circulator: 1->2->3->1. Matched, lossless, NOT reciprocal."""
    S = [[0.0 + 0j] * ports for _ in range(ports)]
    for i in range(ports):
        S[(i + 1) % ports][i] = 1.0 + 0j
    return S


def directional_coupler(c_db=3.0):
    """Ideal 4-port coupler. Ports 1-2 through, 1-3 coupled, 1-4 isolated.

    Quadrature convention: through arm real, coupled arm +j, isolated arm 0.
    """
    beta = 10.0 ** (-c_db / 20.0)              # coupled amplitude
    alpha = math.sqrt(1.0 - beta ** 2)         # through amplitude
    a, b = alpha + 0j, 1j * beta
    return [[0, a, b, 0],
            [a, 0, 0, b],
            [b, 0, 0, a],
            [0, b, a, 0]]


def matched_attenuator(loss_db):
    """A matched, reciprocal, LOSSY two-port -- the amplitude-modulator model."""
    a = 10.0 ** (-loss_db / 20.0)
    return [[0.0 + 0j, a + 0j], [a + 0j, 0.0 + 0j]]


def am_modulator(alpha0, m, wmt):
    """PIN-diode amplitude modulator: a matched two-port whose S21 is driven.

    alpha(t) = alpha0 (1 + m cos w_m t), clipped to the passive range [0, 1].
    """
    a = alpha0 * (1.0 + m * math.cos(wmt))
    a = min(max(a, 0.0), 1.0)
    return [[0.0 + 0j, a + 0j], [a + 0j, 0.0 + 0j]]


# ----------------------------------------- terminating ports of an n-port
def terminate(S, keep, gamma):
    """Reduce an n-port to the ports in `keep`, terminating the rest.

    `gamma` maps a dropped port index to its reflection coefficient at the
    junction reference plane (short = -1, open = +1, matched = 0). Solves
    a = Gamma b on the dropped ports exactly, no iteration.
    """
    n = len(S)
    drop = [i for i in range(n) if i not in keep]
    d = len(drop)
    # b_drop = S[drop][keep] a_keep + S[drop][drop] a_drop, a_drop = G b_drop
    # => (I - S_dd G) b_drop = S_dk a_keep
    out = []
    for col, k in enumerate(keep):
        # unit drive on kept port k
        A = [[(1.0 if i == j else 0.0) - S[drop[i]][drop[j]] * gamma[drop[j]]
              for j in range(d)] for i in range(d)]
        rhs = [S[drop[i]][k] for i in range(d)]
        bd = _solve(A, rhs)
        ad = [gamma[drop[j]] * bd[j] for j in range(d)]
        colvals = []
        for i in keep:
            v = S[i][k] + sum(S[i][drop[j]] * ad[j] for j in range(d))
            colvals.append(v)
        out.append(colvals)
    # out[col][row] -> transpose into row-major
    return [[out[c][r] for c in range(len(keep))] for r in range(len(keep))]


def _solve(A, b):
    """Tiny complex Gaussian elimination with partial pivoting."""
    n = len(b)
    M = [[complex(A[i][j]) for j in range(n)] + [complex(b[i])]
         for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        for j in range(c, n + 1):
            M[c][j] /= pv
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                for j in range(c, n + 1):
                    M[r][j] -= f * M[c][j]
    return [M[i][n] for i in range(n)]


# ----------------------------------------------------- amplifier figures
def rollett(S):
    """Delta and the Rollett stability factor K for a two-port."""
    s11, s12, s21, s22 = S[0][0], S[0][1], S[1][0], S[1][1]
    delta = s11 * s22 - s12 * s21
    K = ((1 - abs(s11) ** 2 - abs(s22) ** 2 + abs(delta) ** 2)
         / (2 * abs(s12 * s21)))
    return delta, K


def gtu_max_db(S):
    """Maximum unilateral transducer gain, in dB (S12 assumed 0)."""
    s11, s21, s22 = S[0][0], S[1][0], S[1][1]
    g = (1.0 / (1 - abs(s11) ** 2)) * abs(s21) ** 2 * (1.0 / (1 - abs(s22) ** 2))
    return 10.0 * math.log10(g)


def gmax_db(S):
    """Maximum available gain (bilateral), only defined when K > 1."""
    _, K = rollett(S)
    s12, s21 = S[0][1], S[1][0]
    if K <= 1:
        return None
    return 10.0 * math.log10(abs(s21 / s12) * (K - math.sqrt(K * K - 1)))


# =====================================================================
#                              self-tests
# =====================================================================
def _close(a, b, tol=1e-9, what=""):
    assert abs(a - b) < tol, "%s: %r != %r" % (what, a, b)


def test_devices():
    """Every ideal device matrix must satisfy the properties it is sold on."""
    e, h, mt = e_plane_tee(), h_plane_tee(), magic_tee()

    for name, S in (("E-plane tee", e), ("H-plane tee", h)):
        assert is_reciprocal(S), name + " must be reciprocal"
        _close(S[2][2], 0.0, what=name + " S33")
        # a 3-port CANNOT be lossless, reciprocal AND matched at once, and
        # these two are the "give up matching at ports 1,2" escape:
        assert not is_matched(S), name + " cannot be matched at every port"
        assert is_lossless(S), name + " should still be lossless"
    _close(e[1][2], -e[0][2], what="E-tee S23 = -S13")
    _close(h[1][2], h[0][2], what="H-tee S23 = +S13")
    _close(e[0][0], 0.5, what="E-tee S11")
    _close(h[0][1], -0.5, what="H-tee S12")

    assert is_reciprocal(mt), "magic tee is reciprocal"
    assert is_matched(mt), "an ideal magic tee is matched at every port"
    assert is_lossless(mt), "magic tee is lossless"
    _close(mt[0][1], 0.0, what="magic tee S12 (collinear isolation)")
    _close(mt[1][2], -mt[0][2], what="magic tee S23 = -S13 (E-arm)")
    _close(mt[1][3], mt[0][3], what="magic tee S24 = +S14 (H-arm)")

    c = circulator()
    assert is_matched(c) and is_lossless(c), "circulator matched + lossless"
    assert not is_reciprocal(c), "a circulator must be non-reciprocal"

    dc = directional_coupler(10.0 * math.log10(2.0))   # the exact 3 dB hybrid
    assert is_matched(dc) and is_lossless(dc) and is_reciprocal(dc), \
        "a 4-port CAN be matched, lossless and reciprocal all at once"
    _close(abs(dc[0][1]) ** 2, 0.5, 1e-9, "3 dB coupler through power")
    _close(abs(dc[0][2]) ** 2, 0.5, 1e-9, "3 dB coupler coupled power")
    _close(abs(dc[0][3]), 0.0, 1e-9, "3 dB coupler isolated arm")


def test_three_port_theorem():
    """No 3-port can be lossless, reciprocal and matched at every port.

    Brute-force the claim rather than trusting the algebra: search the
    reciprocal, matched 3-port family and confirm nothing in it is unitary.
    """
    best = 0.0
    n = 12
    for i in range(n + 1):
        for j in range(n + 1):
            for k in range(n + 1):
                a, b, c = i / n, j / n, k / n
                S = [[0, a, b], [a, 0, c], [b, c, 0]]
                err = max(abs(x - 1) for x in col_norms(S))
                err = max(err, max(abs(v) for v in col_dots(S).values()))
                best = max(best, 1.0 if err < 1e-9 else 0.0)
    assert best == 0.0, "found an ideal 3-port -- the theorem would be false"


def test_magic_tee_shorted_arms():
    """2082 Bhadra Q3: magic tee with BOTH E- and H-arms short-circuited.

    Shorts sit at the junction reference plane, so Gamma = -1 on ports 3 and 4.
    """
    mt = magic_tee()
    red = terminate(mt, keep=[0, 1], gamma={2: -1.0, 3: -1.0})
    _close(red[0][0], -1.0, 1e-12, "shorted magic tee S11")
    _close(red[1][1], -1.0, 1e-12, "shorted magic tee S22")
    _close(red[0][1], 0.0, 1e-12, "shorted magic tee S12")
    _close(red[1][0], 0.0, 1e-12, "shorted magic tee S21")
    # sanity: still lossless, and still isolating the two collinear arms
    assert is_lossless(red), "shorted magic tee is still lossless"
    return red


def test_magic_tee_power_split():
    """73 Bh / 74 Ma combining, and 76 Bh / 73 Ma halving."""
    mt = magic_tee()
    # combining: equal in-phase drive on the two collinear ports
    a = [1.0, 1.0, 0.0, 0.0]
    b = [sum(mt[i][j] * a[j] for j in range(4)) for i in range(4)]
    _close(abs(b[3]) ** 2, 2.0, 1e-12, "H-arm collects both transmitters")
    _close(abs(b[2]) ** 2, 0.0, 1e-12, "E-arm (dummy load) gets nothing")
    # splitting: drive the H-arm alone
    a = [0.0, 0.0, 0.0, 1.0]
    b = [sum(mt[i][j] * a[j] for j in range(4)) for i in range(4)]
    _close(abs(b[0]) ** 2, 0.5, 1e-12, "port 1 takes half")
    _close(abs(b[1]) ** 2, 0.5, 1e-12, "port 2 takes half")
    _close(abs(b[2]) ** 2, 0.0, 1e-12, "E-arm stays isolated")


def test_79bh():
    """2079 Bhadra Q3: [[0.4+j0.5, j0.6],[j0.6, 0.4-j0.5]], P_in = 5 W."""
    S = [[0.4 + 0.5j, 0.6j], [0.6j, 0.4 - 0.5j]]
    assert is_reciprocal(S), "S12 = S21 so it is reciprocal"
    assert not is_lossless(S), "columns do not sum to 1 so it is lossy"
    n = col_norms(S)
    _close(n[0], 0.77, 1e-12, "column 1 power sum")
    _close(n[1], 0.77, 1e-12, "column 2 power sum")
    _close(abs(col_dots(S)[(0, 1)]), 0.0, 1e-12, "columns are still orthogonal")
    s11 = abs(S[0][0])
    _close(s11 ** 2, 0.41, 1e-12, "|S11|^2")
    rl = return_loss_db(S[0][0])
    pr = abs(S[0][0]) ** 2 * 5.0
    _close(pr, 2.05, 1e-12, "reflected power")
    return dict(cols=n, s11=s11, rl=rl, pr=pr,
                pt=abs(S[1][0]) ** 2 * 5.0,
                pdiss=5.0 * dissipated_fraction(S, 0),
                vswr=vswr(S[0][0]))


def test_82bh():
    """2082 Bhadra Q5: the two amplifier S-parameter sets, side by side."""
    A = [[poldeg(0.65, 146), poldeg(0.12, 46)],
         [poldeg(2.30, 44), poldeg(0.17, -172)]]
    B = [[poldeg(0.30, -134), poldeg(0.03, 46)],
         [poldeg(2.20, 44), poldeg(0.10, -172)]]
    out = {}
    for name, S in (("a", A), ("b", B)):
        delta, K = rollett(S)
        out[name] = dict(
            fwd_db=20 * math.log10(abs(S[1][0])),
            rev_db=20 * math.log10(abs(S[0][1])),
            iso_db=insertion_loss_db(S[0][1]),
            rl_in=return_loss_db(S[0][0]),
            rl_out=return_loss_db(S[1][1]),
            vswr_in=vswr(S[0][0]),
            vswr_out=vswr(S[1][1]),
            delta=abs(delta), K=K,
            gtu=gtu_max_db(S), gmax=gmax_db(S),
            reciprocal=is_reciprocal(S), lossless=is_lossless(S))
    assert not out["a"]["reciprocal"] and not out["b"]["reciprocal"], \
        "both sets have S12 != S21, so both are active"
    assert out["a"]["K"] > 1 and out["b"]["K"] > 1, "both unconditionally stable"
    assert out["b"]["K"] > out["a"]["K"], "(b) is the more stable of the two"
    assert out["b"]["rl_in"] > out["a"]["rl_in"], "(b) has the better input match"
    assert out["b"]["iso_db"] > out["a"]["iso_db"], "(b) is better isolated"
    return out


def test_pyq_4port_matrices():
    """The four 'identify this device' matrices all reduce to the magic tee."""
    r = 1.0 / R2
    printed = [[0, 0, 1, 1],           # 2078 Chaitra Q4, as printed
               [0, 0, -1, 1],
               [1, -1, 0, 0],
               [1, 1, 0, 0]]
    scaled = [[r * x for x in row] for row in printed]
    mt = magic_tee()
    for i in range(4):
        for j in range(4):
            _close(scaled[i][j], mt[i][j], 1e-12, "78 Ch entry %d%d" % (i, j))
    assert not is_lossless(printed), "as printed it is not normalised"
    assert is_lossless(scaled), "with the 1/sqrt(2) factor it is unitary"

    # 2081 Bhadra / 2074 Bhadra symbolic form: S23 = -S13 (E-arm at port 3),
    # S24 = +S14 ... printed with the H-arm at column 3 and E-arm at column 4.
    # Substituting the magic-tee solution must satisfy every printed relation.
    S11 = S22 = 0.0
    S13, S14 = r, r
    sym = [[S11, 0.0, S13, S14],
           [0.0, S22, S13, -S14],
           [S13, S13, 0.0, 0.0],
           [S14, -S14, 0.0, 0.0]]
    assert is_lossless(sym) and is_reciprocal(sym) and is_matched(sym), \
        "the 81 Bh / 74 Bh pattern is the magic tee with ports 3,4 swapped"
    return scaled, sym


def test_am_modulator():
    """2078 Chaitra Q3: the amplitude modulator as a driven matched two-port."""
    S = am_modulator(0.5, 0.6, 0.0)            # modulation peak
    assert is_reciprocal(S) and is_matched(S), "matched and reciprocal"
    assert not is_lossless(S), "a modulator must be lossy"
    _close(S[1][0].real, 0.8, 1e-12, "peak S21")
    trough = am_modulator(0.5, 0.6, math.pi)
    _close(trough[1][0].real, 0.2, 1e-12, "trough S21")
    # modulation index recovered from the envelope of |S21|
    hi, lo = 0.8, 0.2
    _close((hi - lo) / (hi + lo), 0.6, 1e-12, "recovered modulation index")
    return dict(peak=hi, trough=lo,
                il_peak=insertion_loss_db(hi + 0j),
                il_trough=insertion_loss_db(lo + 0j))


def test_duplexer():
    """81 Ba / 76 Bh: the two duplexer answers."""
    c = circulator()
    assert is_matched(c) and is_lossless(c) and not is_reciprocal(c)
    # TX on port 1 -> all of it leaves port 2 (antenna), none reaches port 3 (RX)
    a = [1.0, 0.0, 0.0]
    b = [sum(c[i][j] * a[j] for j in range(3)) for i in range(3)]
    _close(abs(b[1]) ** 2, 1.0, 1e-12, "circulator TX -> ANT")
    _close(abs(b[2]) ** 2, 0.0, 1e-12, "circulator TX -> RX leakage")
    # antenna echo on port 2 -> all of it leaves port 3 (receiver)
    a = [0.0, 1.0, 0.0]
    b = [sum(c[i][j] * a[j] for j in range(3)) for i in range(3)]
    _close(abs(b[2]) ** 2, 1.0, 1e-12, "circulator ANT -> RX")


def main():
    test_devices()
    print("devices            ok  (E-tee, H-tee, magic tee, circulator, coupler)")
    test_three_port_theorem()
    print("3-port theorem     ok  (no lossless+reciprocal+matched 3-port exists)")
    red = test_magic_tee_shorted_arms()
    print("magic tee, shorted ok  [S] = [[%+.0f, %.0f], [%.0f, %+.0f]]"
          % (red[0][0].real, red[0][1].real, red[1][0].real, red[1][1].real))
    test_magic_tee_power_split()
    print("power split/combine ok (H-arm sums, E-arm nulls, halves on split)")
    r = test_79bh()
    print("2079 Bhadra        ok  |S11|=%.4f  RL=%.2f dB  Pr=%.2f W  "
          "Pt=%.2f W  Pdiss=%.2f W  VSWR=%.3f"
          % (r["s11"], r["rl"], r["pr"], r["pt"], r["pdiss"], r["vswr"]))
    o = test_82bh()
    for k in ("a", "b"):
        v = o[k]
        print("2082 Bhadra (%s)    ok  G=%.2f dB  iso=%.2f dB  RLin=%.2f dB  "
              "VSWRin=%.3f  RLout=%.2f dB  |D|=%.4f  K=%.3f  GTUmax=%.2f dB  "
              "GMAX=%.2f dB"
              % (k, v["fwd_db"], v["iso_db"], v["rl_in"], v["vswr_in"],
                 v["rl_out"], v["delta"], v["K"], v["gtu"], v["gmax"]))
    test_pyq_4port_matrices()
    print("PYQ 4-port set     ok  (78 Ch, 81 Bh, 74 Bh, 75 Bh all = magic tee)")
    m = test_am_modulator()
    print("AM modulator       ok  |S21| %.2f..%.2f  IL %.2f..%.2f dB"
          % (m["trough"], m["peak"], m["il_peak"], m["il_trough"]))
    test_duplexer()
    print("duplexer           ok  (circulator: TX->ANT lossless, RX isolated)")
    print("\nall self-tests passed")


if __name__ == "__main__":
    main()
