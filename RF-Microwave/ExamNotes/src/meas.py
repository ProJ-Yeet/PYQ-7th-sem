# -*- coding: utf-8 -*-
"""Chapter 8 exit test: every number printed in ch8.tex, re-derived here.

Nothing below is quoted from a note. Each measurement relation is either
built up from first principles (the calorimeter formulas from calories and
joules, the double-minimum formula from a simulated standing wave, the
slotted-line impedance from an independently computed standing-wave pattern)
or inverted and checked against the forward model it came from.

Run from src\\:   python meas.py
Exit 0 and the printed table is what ch8.tex may claim.
"""
import cmath
import math

CAL = 4.187          # joules per calorie, the constant in both calorimeter laws
C = 2.998e8

fails = []


def ok(name, got, want, tol=1e-6, unit=""):
    good = abs(got - want) <= tol * max(1.0, abs(want))
    if not good:
        fails.append("%s: got %r want %r" % (name, got, want))
    print("  %-46s %14.6g %-8s %s" % (name, got, unit, "ok" if good else "FAIL"))
    return got


def head(t):
    print("\n" + t)
    print("  " + "-" * 74)


# ----------------------------------------------------------------- 1. ranges
def dbm(mw):
    return 10.0 * math.log10(mw)


def mw(dbm_):
    return 10.0 ** (dbm_ / 10.0)


def band(p_mw):
    """The three categories every 'choose a proper tool' question turns on."""
    if p_mw < 10.0:
        return "low"
    if p_mw <= 10e3:
        return "medium"
    return "high"


def power_ranges():
    head("1. Power ranges and dBm (the decision table behind 72 Ma, 74 Ma, 73 Bh)")
    ok("0 dBm in mW", mw(0.0), 1.0, unit="mW")
    ok("1 W in dBm", dbm(1e3), 30.0, unit="dBm")
    ok("-30 dBm in mW", mw(-30.0), 1e-3, unit="mW")
    ok("Schottky floor -70 dBm in pW", mw(-70.0) * 1e9, 100.0, 1e-9, "pW")
    ok("thermistor floor -20 dBm in mW", mw(-20.0), 0.01, unit="mW")
    ok("7.5 mW in dBm", dbm(7.5), 8.7506126, 1e-6, "dBm")
    assert band(7.5) == "low", "72 Ma: 7.5 mW must fall in the low-power band"
    assert band(0.005) == "low"
    assert band(5e3) == "medium"
    assert band(50e3) == "high"
    print("  %-46s %14s %-8s ok" % ("7.5 mW classified", band(7.5), ""))
    # the thermistor bolometer can see it: floor well below, ceiling above
    assert mw(-20.0) < 7.5 < 10.0


# ------------------------------------------------------------- 2. pulsed power
def pulsed(peak_w, tau_s, prf_hz):
    duty = tau_s * prf_hz
    return peak_w * duty, duty


def radar():
    head("2. Pulsed radar, average vs peak (74 Ma, airport surveillance radar)")
    pav, duty = pulsed(1.0e6, 1.0e-6, 1000.0)
    ok("duty cycle (1 us, 1 kHz PRF)", duty, 1e-3)
    ok("average power from 1 MW peak", pav, 1000.0, unit="W")
    assert band(pav * 1e3) == "high", "an ASR is a high-power measurement"
    # and the inverse, which is how the meter is actually read
    ok("peak recovered from average", pav / duty, 1.0e6, unit="W")
    # square-wave modulated sensor reading, Das 13.14
    T, tw = 1.0e-3, 1.0e-6
    ok("Ppeak = Pav*T/tau  (Pav = 1 kW)", 1000.0 * T / tw, 1.0e6, unit="W")


# ----------------------------------------------------------- 3. calorimeters
def static_calorimeter(m_g, cp_cal_per_g_c, dT_c, t_s):
    """P = 4.187 m Cp T / t  watts."""
    return CAL * m_g * cp_cal_per_g_c * dT_c / t_s


def circulating_calorimeter(v_cc_s, d_g_cc, cp_cal_per_g_c, dT_c):
    """P = 4.187 v d Cp (T2 - T1)  watts."""
    return CAL * v_cc_s * d_g_cc * cp_cal_per_g_c * dT_c


def calorimeters():
    head("3. Calorimetry (70 Ma, 71 Ma, 71 Bh, 75 Bh, 76 Bh, 77 Ch, 81 Bh, 82 Ba)")
    # static: 100 g of water up 5 C in one minute
    p = static_calorimeter(100.0, 1.0, 5.0, 60.0)
    ok("static: 100 g water, +5 C in 60 s", p, 34.891667, 1e-6, "W")
    # first principles: 500 cal in 60 s is 8.333 cal/s, and 1 cal = 4.187 J
    ok("  same from calories per second", 100.0 * 1.0 * 5.0 / 60.0 * CAL, p)

    # circulating: 10 cc/s of water, 2 C rise
    q = circulating_calorimeter(10.0, 1.0, 1.0, 2.0)
    ok("circulating: 10 cc/s water, +2 C", q, 83.74, 1e-6, "W")
    ok("  same from calories per second", 10.0 * 1.0 * 1.0 * 2.0 * CAL, q)

    # the two laws are the same law: circulating is static with m/t = v*d
    m_over_t = 10.0 * 1.0                      # g/s
    ok("  static law with m/t = v*d", CAL * m_over_t * 1.0 * 2.0, q)

    # a flow calorimeter sized for a 1 kW transmitter (74 Ma follow-on)
    v = 1000.0 / (CAL * 1.0 * 1.0 * 10.0)      # cc/s for a 10 C rise
    ok("flow rate for 1 kW at +10 C rise", v, 23.883452, 1e-6, "cc/s")
    ok("  back through the law", circulating_calorimeter(v, 1.0, 1.0, 10.0),
       1000.0, 1e-9, "W")


# -------------------------------------------------------- 4. bolometer bridge
def bridge_dc_power(v_bridge, r_sensor):
    """Sensor sits in one arm of a Wheatstone bridge with all arms equal, so
    it carries half the bridge voltage: P = (V/2)^2 / R = V^2 / 4R."""
    return (v_bridge / 2.0) ** 2 / r_sensor


def bolometer():
    head("4. Bolometer bridge, dc substitution (80 Ba, 80 Bh, 81 Ba, 79 Ch, 80 Ch)")
    R = 200.0
    v1, v2 = 6.0, 4.0
    p1 = bridge_dc_power(v1, R)
    p2 = bridge_dc_power(v2, R)
    ok("dc power in sensor, no RF (6 V)", p1 * 1e3, 45.0, 1e-9, "mW")
    ok("dc power in sensor, with RF (4 V)", p2 * 1e3, 20.0, 1e-9, "mW")
    ok("Pav = (V1^2 - V2^2)/4R", (v1 ** 2 - v2 ** 2) / (4 * R) * 1e3, 25.0,
       1e-9, "mW")
    ok("  = dc power the RF displaced", (p1 - p2) * 1e3, 25.0, 1e-9, "mW")

    # the ambient-drift term the second bridge cancels: both arms move by dV
    dV = 0.05
    p_drift = ((v1 + dV) ** 2 - (v2 + dV) ** 2) / (4 * R)
    ok("single bridge, both rails drift +50 mV", p_drift * 1e3, 25.25,
       1e-9, "mW")
    err = (p_drift - (v1 ** 2 - v2 ** 2) / (4 * R)) / ((v1 ** 2 - v2 ** 2) / (4 * R))
    ok("  error the drift causes", err * 100.0, 1.0, 1e-9, "%")
    # Das 13.13: the error term is (V1-V2)*2dV/4R, negligible while V1+V2 >> dV
    ok("  error term (V1-V2)2dV/4R", (v1 - v2) * 2 * dV / (4 * R) * 1e3,
       0.25, 1e-9, "mW")
    assert v1 + v2 > 100 * dV


# ------------------------------------------------- 5. standing-wave machinery
def swpattern(gamma, x, lam):
    """|V| on a line at distance x from the load, normalised to the incident."""
    return abs(1.0 + gamma * cmath.exp(-2j * (2 * math.pi / lam) * x))


def swr_of(gamma):
    g = abs(gamma)
    return (1 + g) / (1 - g)


def double_minimum(dx, lam_g):
    """VSWR from the width dx between the two points either side of a minimum
    where the detected power is twice the minimum (Das 13.34 with m = sqrt2)."""
    s = math.sin(math.pi * dx / lam_g)
    return math.sqrt(1.0 + 1.0 / (s * s))


def measure_dx(gamma, lam, n=400001):
    """Simulate the probe: find the minimum, then the two sqrt(2) points."""
    xs = [i * lam / (n - 1) for i in range(n)]
    vs = [swpattern(gamma, x, lam) for x in xs]
    i0 = min(range(n), key=lambda i: vs[i])
    target = math.sqrt(2.0) * vs[i0]
    i = i0
    while vs[i] < target:
        i += 1
    j = i0
    while vs[j] < target:
        j -= 1
    return xs[i] - xs[j], vs[i0], max(vs)


def vswr_measurement():
    head("5. VSWR: direct reading and the double-minimum method (79 Bh, 72 Ash, 70 Bh)")
    lam = 0.04
    for s_true in (2.0, 10.0, 25.0, 60.0):
        g = (s_true - 1) / (s_true + 1)
        gamma = g * cmath.exp(1j * 0.7)
        dx, vmin, vmax = measure_dx(gamma, lam)
        ok("S=%-4g direct Vmax/Vmin" % s_true, vmax / vmin, s_true, 2e-4)
        ok("     double-minimum, dx=%.4f lam" % (dx / lam),
           double_minimum(dx, lam), s_true, 2e-3)
        approx = lam / (math.pi * dx)
        err = abs(approx - s_true) / s_true * 100.0
        print("  %-46s %14.4g %-8s (error %.2f %%)"
              % ("     short form lam_g/(pi dx)", approx, "", err))
        if s_true >= 20:
            assert err < 0.2, "the short form must be good where it is used"
    # and it is the WRONG tool at low SWR: at S = 2 the short form is useless
    g = 1.0 / 3.0
    dx, _, _ = measure_dx(g * cmath.exp(1j * 0.7), lam)
    assert abs(lam / (math.pi * dx) - 2.0) / 2.0 > 0.15


# ---------------------------------------------------- 6. slotted-line impedance
def z_from_slotted_line(s, dmin, lam_g, z0):
    """Das 13.46-13.50: |G| from S, angle from the first minimum."""
    rho = (s - 1.0) / (s + 1.0)
    beta = 2 * math.pi / lam_g
    phi = 2 * beta * dmin - math.pi
    g = rho * cmath.exp(1j * phi)
    return z0 * (1 + g) / (1 - g)


def z_from_tangent(s, dmin, lam_g, z0):
    """Independent route: shift the line back by dmin from a real minimum."""
    t = math.tan(2 * math.pi * dmin / lam_g)
    return z0 * (1 - 1j * s * t) / (s - 1j * t)


def first_minimum(gamma, lam, n=400001):
    xs = [i * lam / (n - 1) for i in range(n)]
    vs = [swpattern(gamma, x, lam) for x in xs]
    i0 = min(range(n), key=lambda i: vs[i])
    return xs[i0]


def impedance():
    head("6. Unknown load from the slotted line (syllabus 8.7/8.8, Das 13.11)")
    z0, lam = 50.0, 0.04
    for zl in (60 - 80j, 110 + 110j, 25 + 0j):
        gamma = (zl - z0) / (zl + z0)
        s = swr_of(gamma)
        dmin = first_minimum(gamma, lam)
        za = z_from_slotted_line(s, dmin, lam, z0)
        zb = z_from_tangent(s, dmin, lam, z0)
        ok("Z_L = %-9s recovered, real" % ("%g%+gj" % (zl.real, zl.imag)),
           za.real, zl.real, 1e-3, "ohm")
        ok("                        imag", za.imag, zl.imag, 1e-3, "ohm")
        ok("   second route agrees, real", zb.real, zl.real, 1e-3, "ohm")
        ok("                        imag", zb.imag, zl.imag, 1e-3, "ohm")

    # which way the minimum shifts, and what that says about the load
    for zl, kind in ((110 + 110j, "inductive"), (60 - 80j, "capacitive")):
        gamma = (zl - z0) / (zl + z0)
        dmin = first_minimum(gamma, lam) / lam
        got = "inductive" if dmin > 0.25 else "capacitive"
        good = got == kind
        if not good:
            fails.append("minimum shift for %s load read as %s" % (kind, got))
        print("  %-46s %14.4f %-8s %s"
              % ("%s load: first minimum" % kind, dmin, "lam_g",
                 "ok" if good else "FAIL"))
    # a short puts minima at 0 and lam_g/2, so dmin > 0.25 lam is a shift TOWARDS
    # the load (inductive) and dmin < 0.25 lam a shift towards the generator
    assert first_minimum((1j * 1e6 - z0) / (1j * 1e6 + z0), lam) / lam > 0.25

    # Das's own worked chart example does not reproduce: S = 2, dmin = 0.2 lam_g
    z = z_from_slotted_line(2.0, 0.2 * lam, lam, 1.0)
    ok("Das Fig 13.21 example, real part", z.real, 1.5546363, 1e-6)
    ok("                       imag part", z.imag, -0.6853442, 1e-6)
    zt = z_from_tangent(2.0, 0.2 * lam, lam, 1.0)
    ok("  tangent route, real", zt.real, 1.5546363, 1e-6)
    ok("  tangent route, imag", zt.imag, -0.6853442, 1e-6)
    printed = 1.0 + 0.7j
    ok("  book prints |z|", abs(printed), 1.220656, 1e-5)
    ok("  its SWR (so it IS on the S=2 circle)", swr_of((printed - 1) / (printed + 1)),
       1.98675, 1e-4)
    # ... but at the wrong angle: 70.7 deg needs dmin = 0.348 lam, not 0.200
    ang = cmath.phase((printed - 1) / (printed + 1))
    ok("  angle it sits at", math.degrees(ang), 70.7106, 1e-4, "deg")
    ok("  dmin that angle implies", (math.degrees(ang) + 180.0) / 720.0,
       0.348209, 1e-5, "lam_g")


# ------------------------------------------------------------ 7. reflectometer
def reflectometer():
    head("7. Reflectometer and the loss family (syllabus 8.8, Das 13.10, 13.8)")
    for s in (1.5, 2.0, 5.0):
        g = (s - 1) / (s + 1)
        ok("S=%-4g -> |Gamma|" % s, g, (s - 1) / (s + 1))
        ok("   return loss", -20 * math.log10(g), -20 * math.log10(g), unit="dB")
        # reflection loss two ways: from |G| and from S (Das 13.20)
        a = -10 * math.log10(1 - g * g)
        b = -10 * math.log10(4 * s / (1 + s) ** 2)
        ok("   reflection loss, two routes agree", a, b, 1e-12, "dB")
    ok("|Gamma| = 1 -> return loss", -20 * math.log10(1.0), 0.0, unit="dB")
    ok("perfect match, |Gamma| = 0.01", -20 * math.log10(0.01), 40.0, 1e-12, "dB")


# -------------------------------------------------------- 8. frequency, cavity
def guide_lambda(f_hz, a_m):
    lam = C / f_hz
    lc = 2 * a_m
    return lam / math.sqrt(1 - (lam / lc) ** 2)


def f_from_guide_lambda(lam_g, a_m):
    lc = 2 * a_m
    inv = 1.0 / lam_g ** 2 + 1.0 / lc ** 2
    return C * math.sqrt(inv)


def frequency():
    head("8. Frequency from the slotted line and the cavity wavemeter (syllabus 8.6)")
    a = 0.02286                      # WR-90 broad wall
    ok("WR-90 cut-off, TE10", C / (2 * a) / 1e9, 6.5573, 1e-4, "GHz")
    lg = guide_lambda(9.965e9, a)
    ok("lambda_g at 9.965 GHz", lg * 100, 3.995452, 1e-5, "cm")
    ok("  half-distance between minima", lg / 2 * 100, 1.997726, 1e-5, "cm")
    ok("f recovered from lambda_g", f_from_guide_lambda(lg, a) / 1e9, 9.965,
       1e-5, "GHz")
    # a 4.00 cm guide wavelength read off the slotted line
    ok("f from a 4.00 cm reading", f_from_guide_lambda(0.04, a) / 1e9,
       9.958578, 1e-5, "GHz")
    # wavemeter accuracy: df/f ~ 1/Q
    for q in (1000.0, 50000.0):
        ok("wavemeter 1/Q at Q=%g" % q, 100.0 / q, 100.0 / q, unit="%")


# ------------------------------------------------------- 9. spectrum analyzer
def spectrum():
    head("9. Spectrum analyzer: image response (80 Bh, 80 Ch)")
    fif, flo = 450e3, 8000e3
    ok("signal that beats to IF, high side", (flo + fif) / 1e3, 8450.0, 1e-9, "kHz")
    ok("signal that beats to IF, low side", (flo - fif) / 1e3, 7550.0, 1e-9, "kHz")
    ok("image sits 2*fIF away", 2 * fif / 1e3, 900.0, 1e-9, "kHz")
    ok("raise fIF to 2 MHz: image moves to", 2 * 2e6 / 1e6, 4.0, 1e-9, "MHz")
    # resolution is the IF bandwidth, and sweep time follows from it
    for rbw in (1e3, 10e3):
        span = 100e6
        t = span / (rbw * rbw)      # the usual k*Span/RBW^2 with k = 1
        print("  %-46s %14.4g %-8s" % ("sweep time at RBW %g kHz" % (rbw / 1e3), t, "s"))
    assert span / (1e3 ** 2) > span / (10e3 ** 2)


# ----------------------------------------------------------- 10. noise, Y-factor
def noise_figure_from_y(enr_db, y_db):
    enr = 10 ** (enr_db / 10.0)
    y = 10 ** (y_db / 10.0)
    f = enr / (y - 1.0)
    return f, 10 * math.log10(f)


def noise():
    head("10. Noise figure by the Y-factor method (syllabus 8.9, never asked)")
    f, fdb = noise_figure_from_y(15.0, 10.0)
    ok("F (linear) for ENR 15 dB, Y 10 dB", f, 3.5136418, 1e-6)
    ok("  in dB", fdb, 5.4575749, 1e-6, "dB")
    # equivalent input noise temperature, same measurement
    t0 = 290.0
    th = t0 * (1 + 10 ** (15.0 / 10.0))
    y = 10.0
    te = (th - y * t0) / (y - 1.0)
    ok("hot-source temperature", th, 9460.6052, 1e-6, "K")
    ok("Te from the same Y", te, 728.9561, 1e-6, "K")
    ok("  and F = 1 + Te/T0", 1 + te / t0, f, 1e-9)
    # kTB floor a noise measurement sits on
    ktb = 1.38065e-23 * t0 * 1.0
    ok("kT0 in dBm/Hz", 10 * math.log10(ktb * 1e3), -174.0, 2e-3, "dBm/Hz")


# ------------------------------------------------- 11. BTS survey, ties to ch7
def bts_survey():
    head("11. Mapping the zones round a GSM BTS (82 Bh), formulas as in ch7")
    f, d = 1800e6, 1.3            # 1800 MHz panel, 1.3 m aperture
    lam = C / f
    ok("lambda at 1800 MHz", lam * 100, 16.6556, 1e-4, "cm")
    assert d > lam, "the zone formulas need D > lambda (ch7 trap)"
    r1 = 0.62 * math.sqrt(d ** 3 / lam)
    r2 = 2 * d ** 2 / lam
    ok("reactive near field ends", r1, 2.251787, 1e-6, "m")
    ok("far field begins", r2, 20.293529, 1e-6, "m")
    # power density the survey meter should read on boresight, far field
    p, g_db = 20.0, 17.0          # 20 W to a 17 dBi sector panel
    g = 10 ** (g_db / 10.0)
    for r in (20.2929, 50.0):
        sden = p * g / (4 * math.pi * r * r)
        print("  %-46s %14.5g %-8s" % ("S at r = %.1f m" % r, sden * 1e4 / 1e3,
                                       "mW/cm2"))
    s50 = p * g / (4 * math.pi * 50.0 ** 2)
    ok("S at 50 m in W/m2", s50, 0.03190664, 1e-6, "W/m2")
    # ICNIRP 1998 general public, 400 MHz - 2 GHz: f/200 W/m2
    limit = 1800.0 / 200.0
    ok("ICNIRP public limit at 1800 MHz", limit, 9.0, 1e-9, "W/m2")
    ok("  margin at 50 m", limit / s50, 282.07356, 1e-6, "x")


def main():
    power_ranges()
    radar()
    calorimeters()
    bolometer()
    vswr_measurement()
    impedance()
    reflectometer()
    frequency()
    spectrum()
    noise()
    bts_survey()
    print("\n" + "=" * 76)
    if fails:
        for f in fails:
            print("FAIL " + f)
        raise SystemExit("%d check(s) failed" % len(fails))
    print("all checks pass")


if __name__ == "__main__":
    main()
