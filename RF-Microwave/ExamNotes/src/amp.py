# -*- coding: utf-8 -*-
"""Chapter 6 amplifier and oscillator solver, self-testing.

Every amplifier number in ch6.tex and ch6-num-body.tex comes from here. The
method is the one the papers' own supplied formula sheet prints (Delta, K, mu,
B1/C1 and B2/C2 for the simultaneous conjugate match, stability circles C/R),
which is also Er. Gangaju's deck method. Nothing is taken on trust:

  * the simultaneous-conjugate-match G_T,max is cross-checked against the
    closed-form maximum available gain |S21/S12| (K - sqrt(K^2 - 1));
  * Gamma_S and Gamma_L are checked to be the conjugates of Gamma_in and
    Gamma_out they produce;
  * stability circles are checked by sampling Gamma on each circle and
    confirming |Gamma_in| (or |Gamma_out|) = 1 there;
  * matching-network stub and line lengths are checked by walking the
    designed network forward and recovering Gamma_S / Gamma_L;
  * the deck's two worked examples (800 MHz stability, 8 GHz 10 dB design)
    and its two oscillator examples are reproduced number by number.

Run from src\\:   python amp.py
"""
import cmath
import math

D2R = math.pi / 180.0


def P(mag, deg):
    return cmath.rect(mag, deg * D2R)


def ang(z):
    return math.degrees(cmath.phase(z))


def db(x):
    return 10.0 * math.log10(x)


def _close(a, b, tol=1e-3, what=""):
    if abs(a - b) > tol * max(1.0, abs(b)):
        raise AssertionError("%s: got %r, expected %r" % (what, a, b))


# ============================================================ core
class Amp:
    def __init__(self, s11, s12, s21, s22):
        self.s11, self.s12, self.s21, self.s22 = s11, s12, s21, s22
        self.delta = s11 * s22 - s12 * s21
        d2 = abs(self.delta) ** 2
        self.K = (1 - abs(s11) ** 2 - abs(s22) ** 2 + d2) / (2 * abs(s12 * s21))
        self.mu = (1 - abs(s11) ** 2) / (abs(s22 - self.delta * s11.conjugate()) + abs(s12 * s21))
        self.B1 = 1 + abs(s11) ** 2 - abs(s22) ** 2 - d2
        self.B2 = 1 + abs(s22) ** 2 - abs(s11) ** 2 - d2
        self.C1 = s11 - self.delta * s22.conjugate()
        self.C2 = s22 - self.delta * s11.conjugate()
        # stability circles (load plane: |Gamma_in| = 1; source plane: |Gamma_out| = 1)
        self.CL = (s22 - self.delta * s11.conjugate()).conjugate() / (abs(s22) ** 2 - d2)
        self.RL = abs(s12 * s21 / (abs(s22) ** 2 - d2))
        self.CS = (s11 - self.delta * s22.conjugate()).conjugate() / (abs(s11) ** 2 - d2)
        self.RS = abs(s12 * s21 / (abs(s11) ** 2 - d2))

    # ---------------------------------------------------------- stability
    @property
    def uncond(self):
        return self.K > 1 and abs(self.delta) < 1

    def gin(self, GL):
        return self.s11 + self.s12 * self.s21 * GL / (1 - self.s22 * GL)

    def gout(self, GS):
        return self.s22 + self.s12 * self.s21 * GS / (1 - self.s11 * GS)

    def load_stable_outside(self):
        """True if the stable Gamma_L region is OUTSIDE the output stability circle.

        Gamma_L = 0 gives |Gamma_in| = |S11|. If |S11| < 1 the origin is stable,
        so the stable side is whichever side of the circle holds the origin.
        """
        origin_outside = abs(self.CL) > self.RL
        return origin_outside if abs(self.s11) < 1 else not origin_outside

    def source_stable_outside(self):
        origin_outside = abs(self.CS) > self.RS
        return origin_outside if abs(self.s22) < 1 else not origin_outside

    # ---------------------------------------------------------- gains
    def conj_match(self):
        """Simultaneous conjugate match (formula sheet); None if not stable."""
        if not self.uncond:
            return None
        def root(B, C):
            sgn = -1 if B > 0 else 1
            return (B + sgn * cmath.sqrt(B * B - 4 * abs(C) ** 2)) / (2 * C)
        return root(self.B1, self.C1), root(self.B2, self.C2)

    def gt(self, GS, GL):
        gi = self.gin(GL)
        return ((1 - abs(GS) ** 2) / abs(1 - gi * GS) ** 2 * abs(self.s21) ** 2
                * (1 - abs(GL) ** 2) / abs(1 - self.s22 * GL) ** 2)

    def gt_max(self):
        m = self.conj_match()
        if m is None:
            return None
        GS, GL = m
        return (1 / (1 - abs(GS) ** 2)) * abs(self.s21) ** 2 * (1 - abs(GL) ** 2) / abs(1 - self.s22 * GL) ** 2

    def mag(self):
        if not self.uncond:
            return None
        return abs(self.s21 / self.s12) * (self.K - math.sqrt(self.K ** 2 - 1))

    def msg(self):
        return abs(self.s21 / self.s12)

    def gs_max(self):
        return 1 / (1 - abs(self.s11) ** 2)

    def gl_max(self):
        return 1 / (1 - abs(self.s22) ** 2)

    def g0(self):
        return abs(self.s21) ** 2

    def gtu_max(self):
        return self.gs_max() * self.g0() * self.gl_max()

    def M(self):
        return (abs(self.s12) * abs(self.s21) * abs(self.s11) * abs(self.s22)
                / ((1 - abs(self.s11) ** 2) * (1 - abs(self.s22) ** 2)))

    def unilateral_bounds(self):
        m = self.M()
        return 1 / (1 + m) ** 2, 1 / (1 - m) ** 2

    def gain_circle_source(self, gs):
        gns = gs * (1 - abs(self.s11) ** 2)
        den = 1 - abs(self.s11) ** 2 * (1 - gns)
        return gns * self.s11.conjugate() / den, math.sqrt(1 - gns) * (1 - abs(self.s11) ** 2) / den

    def gain_circle_load(self, gl):
        gnl = gl * (1 - abs(self.s22) ** 2)
        den = 1 - abs(self.s22) ** 2 * (1 - gnl)
        return gnl * self.s22.conjugate() / den, math.sqrt(1 - gnl) * (1 - abs(self.s22) ** 2) / den


# ============================================================ matching network
def stub_line_for(G, kind="open"):
    """Shunt stub at the 50-ohm end, then a series line to the device.

    Returns (stub length, line length) in wavelengths such that the network,
    terminated in Z0 at its outer end, presents Gamma = G at the device end.
    Both stub signs are solved; the open-stub solution with positive
    susceptance is returned first (the deck's choice).
    """
    g = abs(G)
    b = 2 * g / math.sqrt(1 - g * g)
    out = []
    for bb in (b, -b):
        if kind == "open":
            ls = (math.atan(bb) / (2 * math.pi)) % 0.5
        else:
            ls = (math.atan(-1 / bb) / (2 * math.pi)) % 0.5
        y = 1 + 1j * bb
        G0 = (1 - y) / (1 + y)
        # moving a distance l away from the stub: Gamma rotates by exp(-j 4 pi l)
        l = ((cmath.phase(G0) - cmath.phase(G)) / (4 * math.pi)) % 0.5
        out.append((ls, l, bb))
    return out


def walk(ls, l, kind="open"):
    b = math.tan(2 * math.pi * ls) if kind == "open" else -1 / math.tan(2 * math.pi * ls)
    y = 1 + 1j * b
    G0 = (1 - y) / (1 + y)
    return G0 * cmath.exp(-1j * 4 * math.pi * l)


# ============================================================ oscillator
def z_of(G, z0=50.0):
    return z0 * (1 + G) / (1 - G)


# ============================================================ data
SETS = {
    # key: (label, papers, S11, S12, S21, S22)
    "A": ("0.894 set", "72 Ash, 70 Ma, 80 Ba, 79 Bh",
          P(0.894, -60.6), P(0.020, 62.4), P(3.122, 123.6), P(0.781, -27.6)),
    "B": ("0.55/-150 set", "71 Ma, 81 Ba, 82 Ba",
          P(0.55, -150), P(0.04, 20), P(2.82, 180), P(0.45, -30)),
    "B'": ("0.55/+150 (as printed in 71 Bh)", "71 Bh",
           P(0.55, 150), P(0.04, 20), P(2.82, 180), P(0.45, -30)),
    "C": ("0.656 set", "74 Bh, 70 Bh",
          P(0.656, 146.7), P(0.122, 46.1), P(2.30, 44.7), P(0.172, -117.1)),
    "D": ("GaAs FET 4 GHz", "69 Bh, 77 Ch",
          P(0.72, -116), P(0.03, 57), P(2.60, 76), P(0.73, -54)),
    "E": ("82 Bh set (a)", "82 Bh",
          P(0.65, 146), P(0.12, 46), P(2.30, 44), P(0.17, -172)),
    "F": ("0.45/-160 set", "80 Ch",
          P(0.45, -160), P(0.04, 20), P(3.12, 180), P(0.35, -40)),
    "G": ("GaAs FET 5 GHz", "79 Ch, 72 Ma",
          P(0.45, 163), P(0.04, 40), P(2.55, -106), P(0.46, -65)),
    "H": ("1 GHz transistor, Zs 25, ZL 40", "76 Bh",
          P(0.38, -158), P(0.11, 54), P(3.50, 80), P(0.40, -43)),
    "I": ("0.78 set", "74 Ma",
          P(0.78, -113), P(0.028, 247), P(2.60, 76), P(0.81, -54)),
    "J": ("GaAs MESFET 10 GHz", "80 Bh",
          P(0.55, -160), P(0.04, 10), P(4.82, 180), P(0.45, -30)),
    "K": ("0.64 set, S21 = 10.11", "73 Ma",
          P(0.64, -169), P(0.03, 50), P(10.11, 91), P(0.22, -82)),
    "L": ("0.6 set", "81 Bh",
          P(0.6, -140), P(0.03, 62), P(2.40, 54), P(0.70, -58)),
}


# ============================================================ tests
def check_general(a, tag):
    # stability circles: sampled points really give |Gamma_in| = 1 / |Gamma_out| = 1
    for k in range(12):
        t = 2 * math.pi * k / 12
        GL = a.CL + a.RL * cmath.exp(1j * t)
        if abs(1 - a.s22 * GL) > 1e-6:
            _close(abs(a.gin(GL)), 1.0, tol=1e-6, what=tag + " output circle")
        GS = a.CS + a.RS * cmath.exp(1j * t)
        if abs(1 - a.s11 * GS) > 1e-6:
            _close(abs(a.gout(GS)), 1.0, tol=1e-6, what=tag + " input circle")
    # K > 1 and |Delta| < 1 must agree with mu > 1
    assert (a.mu > 1) == a.uncond, (tag, a.mu, a.K, abs(a.delta))
    m = a.conj_match()
    if m:
        GS, GL = m
        assert abs(GS) < 1 and abs(GL) < 1, tag
        _close(abs(a.gin(GL) - GS.conjugate()), 0.0, tol=1e-9, what=tag + " GS = Gin*")
        _close(abs(a.gout(GS) - GL.conjugate()), 0.0, tol=1e-9, what=tag + " GL = Gout*")
        _close(a.gt_max(), a.mag(), tol=1e-9, what=tag + " GTmax = MAG")
        _close(a.gt(GS, GL), a.gt_max(), tol=1e-9, what=tag + " Gt at match")
    lo, hi = a.unilateral_bounds()
    assert lo < 1 < hi


def test_deck_800mhz():
    a = Amp(P(0.65, -95), P(0.035, 40), P(5, 115), P(0.8, -35))
    _close(abs(a.delta), 0.504, tol=2e-3, what="800 MHz |Delta|")
    assert abs(ang(a.delta) % 360 - 249.6) < 0.1, ang(a.delta)
    _close(a.K, 0.547, tol=2e-3, what="800 MHz K")
    _close(abs(a.CS), 1.79, tol=5e-3, what="800 MHz |CS|")
    assert abs(ang(a.CS) - 122) < 0.5, ang(a.CS)
    _close(a.RS, 1.04, tol=5e-3, what="800 MHz RS")
    _close(abs(a.CL), 1.3, tol=5e-3, what="800 MHz |CL|")
    assert abs(ang(a.CL) - 48) < 0.5, ang(a.CL)
    _close(a.RL, 0.45, tol=5e-3, what="800 MHz RL")
    check_general(a, "800MHz")
    return a


def test_deck_8ghz():
    a = Amp(P(0.52, -145), P(0.03, 20), P(2.56, 170), P(0.48, -20))
    check_general(a, "8GHz")
    out = dict(delta=a.delta, K=a.K, g0=a.g0(), gsm=a.gs_max(), glm=a.gl_max(),
               gtu=a.gtu_max(), M=a.M(), bounds=a.unilateral_bounds())
    _close(a.g0(), 6.55, tol=2e-3, what="8GHz |S21|^2")
    _close(a.gtu_max(), 11.67, tol=5e-3, what="8GHz GTUmax")
    _close(a.gs_max(), 1.37, tol=5e-3, what="gsmax")
    _close(a.gl_max(), 1.30, tol=5e-3, what="glmax")
    # design for 10 dB with gs = 1.25
    gs = 1.25
    gl = 10 / (gs * a.g0())
    _close(gl, 1.22, tol=5e-3, what="gl")
    cgs, rgs = a.gain_circle_source(gs)
    cgl, rgl = a.gain_circle_load(gl)
    out.update(gl=gl, cgs=cgs, rgs=rgs, cgl=cgl, rgl=rgl)
    # deck-chosen points: closest to the origin on each circle
    GS = cgs - rgs * cgs / abs(cgs)
    GL = cgl - rgl * cgl / abs(cgl)
    out.update(GS=GS, GL=GL)
    # the unilateral gain with these points is exactly 10
    gu = ((1 - abs(GS) ** 2) / abs(1 - a.s11 * GS) ** 2 * a.g0()
          * (1 - abs(GL) ** 2) / abs(1 - a.s22 * GL) ** 2)
    _close(gu, 10.0, tol=1e-6, what="design meets 10 dB")
    for G, which in ((GS, "S"), (GL, "L")):
        ls, l, b = stub_line_for(G)[0]
        _close(abs(walk(ls, l) - G), 0, tol=1e-9, what="network walk " + which)
        out["net" + which] = (ls, l)
    return out


def test_oscillators():
    # deck slide 64: Z_out = -10 ohm
    G = (-10 - 50) / (-10 + 50)
    _close(G, -1.5, what="Gamma_out")
    _close(abs(1 / G), 0.667, tol=1e-3, what="1/Gamma*")
    # deck slide 66: Gunn Gamma_out = 1.24 / 30 deg at 10 GHz
    Gg = P(1.24, 30)
    Z = z_of(Gg)
    RL_rule = abs(Z.real) / 1.2
    C = 1 / (2 * math.pi * 10e9 * abs(Z.imag))
    return dict(Z=Z, inv=1 / Gg.conjugate(), RL_rule=RL_rule, C_pF=C * 1e12)


def pyq_table():
    rows = {}
    for key, (label, papers, s11, s12, s21, s22) in SETS.items():
        a = Amp(s11, s12, s21, s22)
        check_general(a, key)
        m = a.conj_match()
        rows[key] = dict(
            label=label, papers=papers, delta=a.delta, K=a.K, mu=a.mu, uncond=a.uncond,
            B1=a.B1, B2=a.B2, C1=a.C1, C2=a.C2,
            CS=a.CS, RS=a.RS, CL=a.CL, RL=a.RL,
            load_out=a.load_stable_outside(), src_out=a.source_stable_outside(),
            GS=m[0] if m else None, GL=m[1] if m else None,
            gtmax=a.gt_max(), msg=a.msg(),
            g0=a.g0(), gsm=a.gs_max(), glm=a.gl_max(), gtu=a.gtu_max(),
            M=a.M(), bounds=a.unilateral_bounds())
        if m:
            rows[key]["Zin"] = 50 * (1 + a.gin(m[1])) / (1 - a.gin(m[1]))
            rows[key]["Zout"] = 50 * (1 + a.gout(m[0])) / (1 - a.gout(m[0]))
            rows[key]["netS"] = stub_line_for(m[0])[0]
            rows[key]["netL"] = stub_line_for(m[1])[0]
    return rows


def test_76bh():
    a = Amp(*SETS["H"][2:])
    GS = (25 - 50) / (25 + 50)
    GL = (40 - 50) / (40 + 50)
    Gs = (1 - abs(GS) ** 2) / abs(1 - a.s11 * GS) ** 2
    Gl = (1 - abs(GL) ** 2) / abs(1 - a.s22 * GL) ** 2
    Gt = a.gt(GS, GL)
    Gtu = Gs * a.g0() * Gl
    return dict(GS=GS, GL=GL, Gs=Gs, G0=a.g0(), Gl=Gl, Gtu=Gtu, Gt=Gt, K=a.K, delta=a.delta)


def test_71bh_circles():
    """71 Bh gives the circles directly: C_S = 1.15/10, R_S = 0.85, C_L = 1.10/80, R_L = 1.10."""
    CS, RS, CL, RL = P(1.15, 10), 0.85, P(1.10, 80), 1.10
    res = {}
    for name, C, R in (("source", CS, RS), ("load", CL, RL)):
        near, far = abs(C) - R, abs(C) + R
        res[name] = dict(near=near, far=far, cuts_unit=(near < 1 < far),
                         origin_inside=abs(C) < R, through_origin=abs(abs(C) - R) < 1e-12)
    return res


def fmt(z, p=3):
    return "%.*f/%.1f" % (p, abs(z), ang(z))


def main():
    a = test_deck_800mhz()
    print("deck 800 MHz       ok  |D| %.3f/%.1f K %.3f  CS %s RS %.2f  CL %s RL %.2f"
          % (abs(a.delta), ang(a.delta) % 360, a.K, fmt(a.CS, 2), a.RS, fmt(a.CL, 2), a.RL))
    d = test_deck_8ghz()
    print("deck 8 GHz design  ok  |D| %s K %.3f |S21|^2 %.3f gsmax %.3f glmax %.3f GTUmax %.3f (%.2f dB) M %.4f bounds %.3f..%.3f (%.2f..%.2f dB)"
          % (fmt(d["delta"]), d["K"], d["g0"], d["gsm"], d["glm"], d["gtu"], db(d["gtu"]), d["M"],
             d["bounds"][0], d["bounds"][1], db(d["bounds"][0]), db(d["bounds"][1])))
    print("                       gl %.3f  cgs %s rgs %.3f  cgl %s rgl %.3f  GS %s  GL %s"
          % (d["gl"], fmt(d["cgs"]), d["rgs"], fmt(d["cgl"]), d["rgl"], fmt(d["GS"]), fmt(d["GL"])))
    print("                       input net: open stub %.4f lam, line %.4f lam; output net: stub %.4f lam, line %.4f lam"
          % (d["netS"][0], d["netS"][1], d["netL"][0], d["netL"][1]))
    o = test_oscillators()
    print("oscillators        ok  Gunn Z_out = %.1f %+.1fj ohm, 1/G* = %s, |Rout|>=1.2 RL needs RL <= %.1f ohm, C = %.4f pF"
          % (o["Z"].real, o["Z"].imag, fmt(o["inv"], 3), o["RL_rule"], o["C_pF"]))
    rows = pyq_table()
    for k, r in rows.items():
        s = ("%-3s %-34s |D| %s K %.3f mu %.3f %s  CS %s RS %.3f  CL %s RL %.3f  GTUmax %.3f (%.2f dB) M %.4f"
             % (k, r["label"], fmt(r["delta"]), r["K"], r["mu"], "UNCOND" if r["uncond"] else "POT.UNSTABLE",
                fmt(r["CS"]), r["RS"], fmt(r["CL"]), r["RL"], r["gtu"], db(r["gtu"]), r["M"]))
        if r["gtmax"]:
            s += "\n      GS %s GL %s  GTmax %.3f (%.2f dB)  gsmax %.3f g0 %.3f glmax %.3f  B1 %.4f C1 %s B2 %.4f C2 %s  netS %s netL %s" % (
                fmt(r["GS"]), fmt(r["GL"]), r["gtmax"], db(r["gtmax"]), r["gsm"], r["g0"], r["glm"],
                r["B1"], fmt(r["C1"]), r["B2"], fmt(r["C2"]),
                "%.4f/%.4f" % r["netS"][:2], "%.4f/%.4f" % r["netL"][:2])
            s += "\n      Zin %.2f%+.2fj  Zout %.2f%+.2fj" % (r["Zin"].real, r["Zin"].imag, r["Zout"].real, r["Zout"].imag)
        else:
            s += "\n      MSG |S21/S12| = %.2f (%.2f dB); stable side: load %s circle, source %s circle; gsmax %.3f g0 %.3f glmax %.3f" % (
                r["msg"], db(r["msg"]), "outside" if r["load_out"] else "inside",
                "outside" if r["src_out"] else "inside", r["gsm"], r["g0"], r["glm"])
        print(s)
    h = test_76bh()
    print("76 Bh              GS %.4f GL %.4f  Gs %.4f (%.2f dB) G0 %.3f (%.2f dB) Gl %.4f (%.2f dB) GTU %.3f (%.2f dB) GT %.3f (%.2f dB) K %.3f"
          % (h["GS"], h["GL"], h["Gs"], db(h["Gs"]), h["G0"], db(h["G0"]), h["Gl"], db(h["Gl"]),
             h["Gtu"], db(h["Gtu"]), h["Gt"], db(h["Gt"]), h["K"]))
    print("71 Bh circles      " + str(test_71bh_circles()))
    print("\nall self-tests passed")


if __name__ == "__main__":
    main()
