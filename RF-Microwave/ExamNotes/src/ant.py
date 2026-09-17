# -*- coding: utf-8 -*-
"""Chapter 7 exit test: radiation zones, exposure limits, SAR, propagation.

Every number printed in ch7.tex and ch7-num-body.tex comes from here, and
each block asserts what it prints. Run from src\\:   python ant.py

What it checks:
  * the three-zone boundaries (Balanis): R1 = 0.62 sqrt(D^3/lambda),
    R2 = 2 D^2 / lambda, for every PYQ antenna and both deck examples
  * the VALIDITY of those formulas: they assume D well above lambda. For
    D < lambda they give an R2 below lambda/2pi, i.e. a "far field" inside
    the reactive field of the antenna -- the deck's 150 MHz example and the
    82 Ba quarter-wave question both fall here
  * the FCC (OET-65) and ICNIRP-1998 power-density limits as functions of f,
    and the compliance distance R = sqrt(EIRP / (4 pi S_limit))
  * SAR = sigma E^2 / rho, and SAR = c dT/dt
  * photon energy at microwave frequencies vs the ionisation threshold
  * free-space path loss, radio horizon, dish gain and beamwidth
"""
import math

C = 3e8
H_PLANCK = 6.62607015e-34
Q_E = 1.602176634e-19


def close(a, b, tol=5e-3):
    """Relative tolerance check that also works near zero."""
    return abs(a - b) <= tol * max(1.0, abs(b))


# ---------------------------------------------------------------- zones
def zones(D, f=None, lam=None):
    lam = lam if lam is not None else C / f
    r1 = 0.62 * math.sqrt(D ** 3 / lam)
    r2 = 2 * D ** 2 / lam
    return lam, r1, r2


def small_antenna(lam):
    """Boundaries used when D is not large compared with lambda."""
    return lam / (2 * math.pi), 2 * lam


def valid(D, lam):
    """The three-zone formulas need D > lambda (so that R2 > lambda/2pi etc.)."""
    return D > lam


def show_zones(tag, D, f=None, lam=None):
    lam, r1, r2 = zones(D, f, lam)
    ok = valid(D, lam)
    print("%-26s lambda=%.4f m  D=%.4f m  R1=%.4f m  R2=%.4f m  %s"
          % (tag, lam, D, r1, r2, "valid (D > lambda)" if ok else "D < lambda: formulas invalid"))
    if not ok:
        a, b = small_antenna(lam)
        print("%-26s   small-antenna rule: reactive < lambda/2pi = %.4f m, far field > 2 lambda = %.4f m"
              % ("", a, b))
    return lam, r1, r2


def test_zones():
    print("=== radiation zones ===")
    # deck example 1: microwave oven, D = 0.5 m, 2.45 GHz, deck rounds lambda to 0.1224
    lam, r1, r2 = show_zones("deck oven (lambda 0.1224)", 0.5, lam=0.1224)
    assert close(r1, 0.6266, 1e-3) and close(r2, 4.085, 1e-3)
    lam, r1, r2 = show_zones("oven exact", 0.5, f=2.45e9)
    assert close(lam, 0.12245, 1e-3) and close(r1, 0.6264, 1e-3) and close(r2, 4.083, 1e-3)
    assert valid(0.5, lam)

    # deck example 2: 150 MHz, D = 0.5 m -- the deck prints 0.155 and 0.25
    lam, r1, r2 = show_zones("deck 150 MHz", 0.5, f=150e6)
    assert close(lam, 2.0) and close(r1, 0.155, 1e-2) and close(r2, 0.25)
    assert not valid(0.5, lam)
    # its "far field" starts inside the reactive region of a small antenna
    assert r2 < lam / (2 * math.pi)

    # 81 Bh: BTS at 2600 MHz, antenna 0.5 m
    lam, r1, r2 = show_zones("81 Bh BTS 2600 MHz", 0.5, f=2600e6)
    assert close(lam, 0.11538, 1e-3) and close(r1, 0.6453, 1e-3) and close(r2, 4.333, 1e-3)
    assert valid(0.5, lam)

    # 82 Ba: quarter-wave antennas at 900 and 1800 MHz
    out = {}
    for f in (900e6, 1800e6):
        lam = C / f
        lam, r1, r2 = show_zones("82 Ba %d MHz, D = lambda/4" % (f / 1e6), lam / 4, f=f)
        # closed forms: R1 = 0.62 lambda/8, R2 = lambda/8
        assert close(r1, 0.62 * lam / 8) and close(r2, lam / 8)
        assert not valid(lam / 4, lam)
        assert r2 < lam / (2 * math.pi)          # the formulas collapse
        out[f] = (lam, r1, r2) + small_antenna(lam)
    a, b = out[900e6], out[1800e6]
    for x, y in zip(a, b):
        assert close(x / y, 2.0)                 # every boundary halves at 1800 MHz
    assert close(a[0], 0.3333, 1e-3) and close(a[1], 0.02583, 1e-3) and close(a[2], 0.04167, 1e-3)
    assert close(a[3], 0.05305, 1e-3) and close(a[4], 0.6667, 1e-3)
    assert close(b[1], 0.01292, 1e-3) and close(b[2], 0.02083, 1e-3) and close(b[3], 0.02653, 1e-3)

    # break-even size where R2 = lambda/2pi: D = lambda / (2 sqrt(pi)) ~ 0.28 lambda
    d = 1 / (2 * math.sqrt(math.pi))
    assert close(2 * d ** 2, 1 / (2 * math.pi))
    print("R2 = lambda/2pi when D = %.3f lambda" % d)


# ---------------------------------------------------------------- limits
def fcc_limit_mw_cm2(f_mhz, public=True):
    """FCC OET-65 Table 1 MPE, power density in mW/cm^2 (300 kHz to 100 GHz)."""
    if public:
        if f_mhz < 1.34:
            return 100.0
        if f_mhz < 30:
            return 180.0 / f_mhz ** 2
        if f_mhz < 300:
            return 0.2
        if f_mhz < 1500:
            return f_mhz / 1500.0
        return 1.0
    if f_mhz < 3:
        return 100.0
    if f_mhz < 30:
        return 900.0 / f_mhz ** 2
    if f_mhz < 300:
        return 1.0
    if f_mhz < 1500:
        return f_mhz / 300.0
    return 5.0


def icnirp98_w_m2(f_mhz, public=True):
    """ICNIRP 1998 reference levels, equivalent plane-wave power density, W/m^2 (10 MHz-300 GHz)."""
    if public:
        if f_mhz < 400:
            return 2.0
        if f_mhz < 2000:
            return f_mhz / 200.0
        return 10.0
    if f_mhz < 400:
        return 10.0
    if f_mhz < 2000:
        return f_mhz / 40.0
    return 50.0


def compliance_distance(eirp_w, s_w_m2):
    return math.sqrt(eirp_w / (4 * math.pi * s_w_m2))


def test_limits():
    print("=== exposure limits ===")
    for f in (900, 1800, 2450, 2600):
        pub, occ = fcc_limit_mw_cm2(f), fcc_limit_mw_cm2(f, False)
        ip, io = icnirp98_w_m2(f), icnirp98_w_m2(f, False)
        print("f=%5d MHz  FCC public %.2f mW/cm2 (%.1f W/m2)  occupational %.2f  |  ICNIRP public %.1f W/m2  occupational %.1f"
              % (f, pub, pub * 10, occ, ip, io))
    assert close(fcc_limit_mw_cm2(900), 0.6) and close(fcc_limit_mw_cm2(1800), 1.0)
    assert close(fcc_limit_mw_cm2(900, False), 3.0) and close(fcc_limit_mw_cm2(1800, False), 5.0)
    assert close(icnirp98_w_m2(900), 4.5) and close(icnirp98_w_m2(1800), 9.0)
    assert close(icnirp98_w_m2(2600), 10.0)
    # occupational is 5x the public level in both schemes above 300 MHz
    for f in (500, 900, 1800, 2600, 10000):
        assert close(fcc_limit_mw_cm2(f, False) / fcc_limit_mw_cm2(f), 5.0)
        assert close(icnirp98_w_m2(f, False) / icnirp98_w_m2(f), 5.0)
    # 1 mW/cm^2 = 10 W/m^2
    assert close(1e-3 / 1e-4, 10.0)

    # 81 Bh second reading: an assumed BTS sector, 20 W into a 17 dBi panel
    p, g_db = 20.0, 17.0
    eirp = p * 10 ** (g_db / 10)
    r_pub = compliance_distance(eirp, icnirp98_w_m2(2600))
    r_occ = compliance_distance(eirp, icnirp98_w_m2(2600, False))
    print("81 Bh check: EIRP %.0f W  ->  public compliance distance %.2f m, occupational %.2f m"
          % (eirp, r_pub, r_occ))
    assert close(eirp, 1002.4, 1e-3) and close(r_pub, 2.824, 1e-3) and close(r_occ, 1.263, 1e-3)
    # the zone answer (far field beyond 4.33 m) is the more conservative one
    assert r_pub < zones(0.5, 2600e6)[2]
    # power density at the far-field boundary
    s = eirp / (4 * math.pi * zones(0.5, 2600e6)[2] ** 2)
    print("   power density at R2 = 4.33 m: %.2f W/m2 (limit 10)" % s)
    assert close(s, 4.249, 1e-3)


# ---------------------------------------------------------------- SAR
def test_sar():
    print("=== SAR ===")
    # typical muscle at 900 MHz (Gabriel 1996): sigma ~ 0.94 S/m, rho ~ 1040 kg/m^3
    sigma, rho = 0.94, 1040.0
    for e in (10.0, 30.0, 61.4):
        print("E_rms = %5.1f V/m -> SAR = %.4f W/kg" % (e, sigma * e ** 2 / rho))
    assert close(sigma * 10 ** 2 / rho, 0.0904, 1e-3)
    # field that gives the 0.08 W/kg whole-body public limit in this tissue
    e_lim = math.sqrt(0.08 * rho / sigma)
    print("E for 0.08 W/kg: %.2f V/m" % e_lim)
    assert close(e_lim, 9.41, 1e-3)
    # tiers: threshold 4 W/kg -> occupational /10 -> public /5 more
    assert close(4.0 / 10, 0.4) and close(0.4 / 5, 0.08)
    # heating rate with no cooling: dT/dt = SAR / c, c ~ 3500 J/(kg K)
    rate = 4.0 / 3500.0
    print("4 W/kg with no heat loss: %.2e K/s -> 1 K in %.0f s (%.1f min)" % (rate, 1 / rate, 1 / rate / 60))
    assert close(1 / rate, 875.0)


# ---------------------------------------------------------------- ionising?
def test_photon():
    print("=== photon energy ===")
    for f in (900e6, 2.45e9, 60e9, 300e9):
        ev = H_PLANCK * f / Q_E
        print("f = %8.3g Hz  ->  %.3e eV" % (f, ev))
    ev = H_PLANCK * 2.45e9 / Q_E
    assert close(ev, 1.013e-5, 1e-3)
    # ionisation needs ~ 10 eV (hydrogen 13.6 eV): a factor of about a million
    assert 12.0 / ev > 1e6
    print("2.45 GHz photon is %.1e times too weak to ionise (12 eV)" % (12.0 / ev))


# ---------------------------------------------------------------- propagation
def fspl_db(d_m, f_hz):
    return 20 * math.log10(4 * math.pi * d_m * f_hz / C)


def test_propagation():
    print("=== propagation and antennas ===")
    # FSPL shortcut: 32.44 + 20 log d_km + 20 log f_MHz (c = 2.998e8 gives 32.45)
    for d_km, f_mhz in ((1, 900), (50, 6000), (36000, 4000)):
        full = fspl_db(d_km * 1e3, f_mhz * 1e6)
        short = 32.44 + 20 * math.log10(d_km) + 20 * math.log10(f_mhz)
        print("FSPL %6d km @ %5d MHz = %.2f dB (shortcut %.2f)" % (d_km, f_mhz, full, short))
        assert abs(full - short) < 0.05
    assert close(fspl_db(50e3, 6e9), 141.98, 1e-3)

    # radio horizon with k = 4/3 earth: d = sqrt(2 k R h), R = 6371 km -> 4.12 sqrt(h) km
    k, r = 4.0 / 3.0, 6371e3
    d = math.sqrt(2 * k * r * 30) / 1e3
    print("radio horizon of a 30 m mast: %.2f km (4.12 sqrt h = %.2f)" % (d, 4.12 * math.sqrt(30)))
    assert close(d, 4.12 * math.sqrt(30), 2e-3)
    # LOS range between two masts of 30 m and 50 m
    los = 4.12 * (math.sqrt(30) + math.sqrt(50))
    print("LOS range, 30 m and 50 m masts: %.1f km" % los)
    assert close(los, 51.7, 2e-3)

    # first Fresnel zone radius at mid-path: r1 = sqrt(lambda d1 d2 / (d1 + d2))
    lam, d1, d2 = C / 6e9, 25e3, 25e3
    r1 = math.sqrt(lam * d1 * d2 / (d1 + d2))
    print("first Fresnel radius, 50 km hop @ 6 GHz, mid-path: %.2f m (60%% clearance %.2f m)" % (r1, 0.6 * r1))
    assert close(r1, 25.00, 1e-3)

    # parabolic dish: G = eta (pi D / lambda)^2, HPBW ~ 70 lambda / D degrees
    D, f, eta = 1.2, 12e9, 0.55
    lam = C / f
    g = eta * (math.pi * D / lam) ** 2
    print("1.2 m dish @ 12 GHz, eta 0.55: G = %.0f = %.1f dBi, HPBW = %.2f deg"
          % (g, 10 * math.log10(g), 70 * lam / D))
    assert close(10 * math.log10(g), 40.97, 1e-3) and close(70 * lam / D, 1.458, 1e-3)
    # gain from effective aperture: G = 4 pi A_e / lambda^2 with A_e = eta pi D^2/4
    ae = eta * math.pi * D ** 2 / 4
    assert close(4 * math.pi * ae / lam ** 2, g)

    # Friis link: Pr = Pt Gt Gr (lambda / 4 pi d)^2
    pt, gt, gr, d = 1.0, 10 ** 3.0, 10 ** 3.0, 50e3
    lam = C / 6e9
    pr = pt * gt * gr * (lam / (4 * math.pi * d)) ** 2
    pr_dbm = 10 * math.log10(pr / 1e-3)
    print("Friis: 1 W, 30 dBi each end, 50 km @ 6 GHz -> Pr = %.2f dBm" % pr_dbm)
    assert close(pr_dbm, 30 + 30 + 30 - fspl_db(d, 6e9), 1e-6)


def main():
    test_zones()
    test_limits()
    test_sar()
    test_photon()
    test_propagation()
    print("\nall ant.py checks pass")


if __name__ == "__main__":
    main()
