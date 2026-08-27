# -*- coding: utf-8 -*-
"""Independently recompute every numerical answer published in the Wireless
exam notes, and assert it against the value actually printed in the .tex.

This is a *check*, not a source: nothing here reads a number out of the notes
and hands it back. Each answer is recomputed from the problem statement, then
compared with the printed figure.

Run:  python verify.py          (from this folder)
"""
import math
import sys

c = 3e8
FAIL = []
N_OK = 0


def chk(label, got, want, tol=None, rel=2e-3):
    """Assert a recomputed value matches the value printed in the notes."""
    global N_OK
    if tol is None:
        tol = abs(want) * rel if want else 1e-9
    ok = abs(got - want) <= tol
    if ok:
        N_OK += 1
    else:
        FAIL.append(f"{label}: recomputed {got!r} but notes print {want!r} "
                    f"(tol {tol:.3g})")


def dbm(watts):
    return 10 * math.log10(watts * 1000.0)


def watts(x_dbm):
    return 10 ** (x_dbm / 10.0) / 1000.0


def db(x):
    return 10 * math.log10(x)


def fspl(d_m, f_hz):
    return 20 * math.log10(4 * math.pi * d_m / (c / f_hz))


def erlang_b(C, A):
    inv = 1.0
    for k in range(1, C + 1):
        inv = 1.0 + inv * k / A
    return 1.0 / inv


def erlang_b_traffic(C, gos, lo=1e-9, hi=1e7):
    for _ in range(400):
        mid = (lo + hi) / 2
        if erlang_b(C, mid) < gos:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def hex_area(R):
    return 2.598 * R * R


def hata_urban(fc_mhz, hte, hre, d_km, city="medium"):
    lf = math.log10(fc_mhz)
    if city == "medium":
        a = (1.1 * lf - 0.7) * hre - (1.56 * lf - 0.8)
    elif city == "large":                       # fc > 300 MHz branch
        a = 3.2 * (math.log10(11.75 * hre)) ** 2 - 4.97
    else:
        raise ValueError(city)
    return (69.55 + 26.16 * lf - 13.82 * math.log10(hte) - a
            + (44.9 - 6.55 * math.log10(hte)) * math.log10(d_km)), a


def okumura(d_m, f_hz, hte, hre, amu, garea):
    lf = fspl(d_m, f_hz)
    ghte = 20 * math.log10(hte / 200.0)
    ghre = (10 if hre <= 3 else 20) * math.log10(hre / 3.0)
    return lf + amu - ghte - ghre - garea, lf, ghte, ghre


def pdp(powers_db, delays):
    p = [10 ** (x / 10.0) for x in powers_db]
    s = sum(p)
    mean = sum(pi * ti for pi, ti in zip(p, delays)) / s
    m2 = sum(pi * ti * ti for pi, ti in zip(p, delays)) / s
    return s, mean, m2, math.sqrt(m2 - mean * mean)


# =====================================================================
#  CHAPTER 2
# =====================================================================
def ch2():
    # --- P1.1  SIR 15 dB, n = 4 -------------------------------------
    sir = 10 ** 1.5
    chk("c2 p1.1 SIR linear", sir, 31.6228)
    for name, i0, q_want, n_want in (("omni", 6, 3.7114, 4.5915),
                                     ("120", 2, 2.8201, 2.6509),
                                     ("60", 1, 2.3714, 1.8745)):
        q = (i0 * sir) ** 0.25
        chk(f"c2 p1.1 Q {name}", q, q_want)
        chk(f"c2 p1.1 N {name}", q * q / 3, n_want)

    # --- P1.2  SIR 15 dB, n = 3 -------------------------------------
    for name, i0, q_want, n_want in (("omni", 6, 5.7462, 11.0064),
                                     ("120", 2, 3.9842, 5.2913),
                                     ("60", 1, 3.1623, 3.3333)):
        q = (i0 * sir) ** (1 / 3)
        chk(f"c2 p1.2 Q {name}", q, q_want)
        chk(f"c2 p1.2 N {name}", q * q / 3, n_want)

    # --- P1.3  AMPS 18 dB, n = 4 ------------------------------------
    q = (6 * 10 ** 1.8) ** 0.25
    chk("c2 p1.3 Q", q, 4.4110)
    chk("c2 p1.3 N", q * q / 3, 6.4857)

    # --- P1.4  exact vs approximate SIR for N = 7 -------------------
    Q = math.sqrt(21)
    chk("c2 p1.4 Q", Q, 4.5826)
    approx = Q ** 4 / 6
    chk("c2 p1.4 approx S/I", approx, 73.50, tol=0.05)
    chk("c2 p1.4 approx dB", db(approx), 18.66, tol=0.02)
    exact = 1.0 / (2 * (Q - 1) ** -4 + 2 * (Q + 1) ** -4 + 2 * Q ** -4)
    chk("c2 p1.4 exact S/I", exact, 53.376)
    chk("c2 p1.4 exact dB", db(exact), 17.27, tol=0.02)

    # --- P2  20 MHz spectrum ----------------------------------------
    total = 20e6 / (2 * 25e3)
    chk("c2 p2 duplex channels", total, 400)
    chk("c2 p2 N=4", total / 4, 100)
    chk("c2 p2 N=7", math.floor(total / 7), 57)
    chk("c2 p2 N=12", math.floor(total / 12), 33)

    # --- P3  co-channel distance from area --------------------------
    R = math.sqrt(23 / 2.598)
    chk("c2 p3 R", R, 2.9754)
    chk("c2 p3 D", math.sqrt(21) * R, 13.635)
    chk("c2 p3 circle variant", math.sqrt(23 / math.pi) * math.sqrt(21), 12.397)

    # --- P4  2 million residents ------------------------------------
    Au = 2 * 3 / 60.0
    chk("c2 p4 Au", Au, 0.1)
    chk("c2 p4 ErlangB C=19 2%", erlang_b_traffic(19, 0.02), 12.333)
    chk("c2 p4 users/cell", 12.0 / Au, 120)
    chk("c2 p4 total", 120 * 394, 47280)
    chk("c2 p4 penetration %", 100 * 47280 / 2e6, 2.364)
    chk("c2 p4 exact users/cell", 12.333 / Au, 123.33, tol=0.02)
    chk("c2 p4 exact total", (12.333 / Au) * 394, 48592, tol=5)
    chk("c2 p4 exact penetration", 100 * (12.333 / Au) * 394 / 2e6, 2.430, tol=0.002)

    # --- P5  1 and 5 channels ---------------------------------------
    Au = 3 * 5 / 60.0
    chk("c2 p5 Au", Au, 0.25)
    chk("c2 p5 ErlangB C=1 1%", erlang_b_traffic(1, 0.01), 0.010, tol=2e-4)
    chk("c2 p5 ErlangB C=5 1%", erlang_b_traffic(5, 0.01), 1.36, tol=5e-3)
    chk("c2 p5 users C=1", 0.010 / Au, 0.04)
    chk("c2 p5 users C=5", 1.36 / Au, 5.44)
    chk("c2 p5 floor C=5", math.floor(1.36 / Au), 5)
    A = 10 * Au
    chk("c2 p5 doubled A", A, 2.5)
    terms = [A ** k / math.factorial(k) for k in range(6)]
    for k, want in enumerate([1, 2.5, 3.125, 2.6042, 1.6276, 0.8138]):
        chk(f"c2 p5 term k={k}", terms[k], want, tol=5e-4)
    chk("c2 p5 sum", sum(terms), 11.6706, tol=1e-3)
    chk("c2 p5 GOS", 100 * erlang_b(5, A), 6.97, tol=0.02)

    # --- P6  1500 km^2 city -----------------------------------------
    ac = hex_area(1.387)
    chk("c2 p6 area/cell", ac, 4.998)
    chk("c2 p6 cells", 1500 / ac, 300.12, tol=0.02)
    chk("c2 p6 total channels", 28.5e6 / 25e3, 1140)
    chk("c2 p6 channels/cell", 1140 / 12, 95)
    chk("c2 p6 ErlangB C=95 2%", erlang_b_traffic(95, 0.02), 83.13, tol=0.02)
    chk("c2 p6 users/cell", 84 / 0.03, 2800)
    chk("c2 p6 total users", 2800 * 300, 840000)
    chk("c2 p6 mobiles/channel", 2800 / 95, 29.47)
    chk("c2 p6 max simultaneous", 95 * 300, 28500)

    # --- P7  32 cells -----------------------------------------------
    ac = hex_area(1.6)
    chk("c2 p7 area/cell", ac, 6.6509)
    chk("c2 p7 total area", 32 * ac, 212.83, tol=0.02)
    chk("c2 p7 channels/cell", 336 / 7, 48)
    chk("c2 p7 simultaneous", 48 * 32, 1536)

    # --- P8  trunking loss ------------------------------------------
    Au = 1 * 2 / 60.0
    chk("c2 p8 Au", Au, 0.0333, tol=1e-4)
    chk("c2 p8 ErlangB C=57 1%", erlang_b_traffic(57, 0.01), 44.2, tol=0.05)
    chk("c2 p8 channels/sector", 57 // 6, 9)
    chk("c2 p8 ErlangB C=9 1%", erlang_b_traffic(9, 0.01), 3.783, tol=2e-3)
    chk("c2 p8 sectored total", 6 * 3.783, 22.698)
    chk("c2 p8 users omni", 44.2 / Au, 1326, tol=1)
    chk("c2 p8 users sectored", 22.698 / Au, 681, tol=1)
    chk("c2 p8 loss E", 44.2 - 22.698, 21.50, tol=0.01)
    chk("c2 p8 loss %", 100 * (44.2 - 22.698) / 44.2, 48.65, tol=0.02)

    # --- P9  416 channels -------------------------------------------
    chk("c2 p9 voice channels", 416 - 21, 395)
    chk("c2 p9 per cell", 395 / 9, 43.89, tol=0.01)
    chk("c2 p9 ErlangB C=44 2%", erlang_b_traffic(44, 0.02), 34.683, tol=2e-3)
    chk("c2 p9 calls/min", 34.683 / 3, 11.561)
    chk("c2 p9 calls/hour", 34.683 / 3 * 60, 694, tol=0.5)
    Q9 = math.sqrt(27)
    chk("c2 p9 Q", Q9, 5.1962)
    chk("c2 p9 S/I", Q9 ** 4 / 6, 121.5, tol=0.05)
    chk("c2 p9 S/I dB", db(Q9 ** 4 / 6), 20.85, tol=0.02)

    # --- P10  cell splitting power ----------------------------------
    chk("c2 p10 ratio", 0.5 ** 4, 0.0625)
    chk("c2 p10 dB", db(0.5 ** 4), -12.04, tol=0.02)

    # --- Erlang B reference table -----------------------------------
    table = {
        1:  (0.005, 0.010, 0.020, 0.053),
        2:  (0.105, 0.153, 0.223, 0.381),
        3:  (0.349, 0.455, 0.602, 0.899),
        4:  (0.701, 0.869, 1.092, 1.525),
        5:  (1.132, 1.361, 1.657, 2.219),
        9:  (3.333, 3.783, 4.345, 5.370),
        10: (3.961, 4.461, 5.084, 6.216),
        19: (10.331, 11.230, 12.333, 14.315),
        20: (11.092, 12.031, 13.182, 15.249),
        44: (30.797, 32.543, 34.682, 38.557),
        54: (39.474, 41.505, 43.997, 48.536),
        57: (42.109, 44.222, 46.816, 51.548),
        95: (76.325, 79.368, 83.133, 90.123),
    }
    for C, row in table.items():
        for gos, want in zip((0.005, 0.01, 0.02, 0.05), row):
            chk(f"c2 table C={C} gos={gos}", erlang_b_traffic(C, gos), want,
                tol=max(6e-4, abs(want) * 5e-4))


# =====================================================================
#  CHAPTER 3
# =====================================================================
def ch3():
    # --- P1  free space, 50 W, 10 km, 900 MHz -----------------------
    lam = c / 900e6
    chk("c3 p1 lambda", lam, 0.3333, tol=5e-4)
    Pr = 50 * 1 * 2 * lam ** 2 / ((4 * math.pi) ** 2 * (1e4) ** 2)
    chk("c3 p1 Pr W", Pr, 7.0362e-10)
    chk("c3 p1 Pr dBm", dbm(Pr), -61.53, tol=0.02)
    chk("c3 p1 Pr dBW", db(Pr), -91.53, tol=0.02)
    Pd = 50 / (4 * math.pi * (1e4) ** 2)
    chk("c3 p1 Pd", Pd, 3.9789e-8)
    E = math.sqrt(Pd * 377)
    chk("c3 p1 E", E, 3.873e-3)
    Ae = 2 * lam ** 2 / (4 * math.pi)
    chk("c3 p1 Ae", Ae, 0.017684)
    chk("c3 p1 Pd*Ae", Pd * Ae, 7.036e-10)
    Vrms = math.sqrt(Pr * 50)
    chk("c3 p1 Vrms", Vrms, 1.8757e-4)
    chk("c3 p1 Vrms uV", Vrms * 1e6, 187.57, tol=0.02)
    chk("c3 p1 Vant uV", 2 * Vrms * 1e6, 375.13, tol=0.05)

    # --- P2  165 W, 325 MHz, 15 km ----------------------------------
    chk("c3 p2 Pt dBm", dbm(165), 52.17, tol=0.02)
    pl = 32.44 + 20 * math.log10(325) + 20 * math.log10(15)
    chk("c3 p2 20log325", 20 * math.log10(325), 50.24, tol=0.02)
    chk("c3 p2 20log15", 20 * math.log10(15), 23.52, tol=0.02)
    chk("c3 p2 PL", pl, 106.20, tol=0.02)
    chk("c3 p2 PL exact", fspl(15e3, 325e6), 106.20, tol=0.02)
    pr = dbm(165) + 12 + 6 - pl
    chk("c3 p2 Pr dBm", pr, -36.03, tol=0.02)
    chk("c3 p2 Pr nW", watts(pr) * 1e9, 249.7, tol=0.5)

    # --- P3  link budget --------------------------------------------
    chk("c3 p3 Pt dBm", dbm(10), 40.00, tol=0.01)
    chk("c3 p3 coax", 20 * 3 / 100.0, 0.60)
    pl = 32.44 + 20 * math.log10(250) + 20 * math.log10(25)
    chk("c3 p3 20log250", 20 * math.log10(250), 47.96, tol=0.02)
    chk("c3 p3 20log25", 20 * math.log10(25), 27.96, tol=0.02)
    chk("c3 p3 PL", pl, 108.36, tol=0.02)
    pr = 40.0 - 0.6 + 9 - pl + 4 - 0.2
    chk("c3 p3 Pr dBm", pr, -56.16, tol=0.02)
    chk("c3 p3 Pr nW", watts(pr) * 1e9, 2.42, tol=0.02)

    # --- P4  coverage range -----------------------------------------
    chk("c3 p4 Pt dBm", dbm(150), 51.76, tol=0.02)
    plmax = dbm(150) + 104
    chk("c3 p4 PLmax", plmax, 155.76, tol=0.02)
    chk("c3 p4 log d", (plmax - 15) / 40, 3.519, tol=1e-3)
    chk("c3 p4 d m", 10 ** ((plmax - 15) / 40), 3304, tol=3)

    # --- P5  monopole + two-ray --------------------------------------
    chk("c3 p5 length", lam / 4, 0.0833, tol=5e-4)
    Gr = 10 ** 0.255
    chk("c3 p5 Gr", Gr, 1.7989)
    Ae = Gr * lam ** 2 / (4 * math.pi)
    chk("c3 p5 Ae", Ae, 0.0159, tol=2e-4)
    Etot = 2 * 1.0 / 5000 * (2 * math.pi * 50 * 1.5) / (lam * 5000)
    chk("c3 p5 Etot", Etot, 1.131e-4)
    Pr = Etot ** 2 / 377 * Ae
    chk("c3 p5 Pr", Pr, 5.397e-13)
    chk("c3 p5 Pr dBm", dbm(Pr), -92.68, tol=0.02)
    chk("c3 p5 dc", 4 * math.pi * 50 * 1.5 / lam, 2827, tol=3)

    # --- P6  cordless -------------------------------------------------
    lam52 = c / 52e6
    chk("c3 p6 lambda", lam52, 5.769, tol=1e-3)
    chk("c3 p6 PL", 20 * math.log10(4 * math.pi * 50 / lam52), 40.74, tol=0.02)
    chk("c3 p6 PL alt", 32.44 + 20 * math.log10(52) + 20 * math.log10(0.05),
        40.74, tol=0.02)

    # --- P7  dBm / dBW ------------------------------------------------
    chk("c3 p7 dBm", dbm(50), 46.99, tol=0.02)
    chk("c3 p7 dBW", db(50), 16.99, tol=0.02)
    P100 = 50 * lam ** 2 / ((4 * math.pi) ** 2 * 100 ** 2)
    chk("c3 p7 Pr 100 m W", P100, 3.5181e-6)
    chk("c3 p7 Pr 100 m dBm", dbm(P100), -24.54, tol=0.02)
    P10k = 50 * lam ** 2 / ((4 * math.pi) ** 2 * 1e4 ** 2)
    chk("c3 p7 Pr 10 km W", P10k, 3.5181e-10)
    chk("c3 p7 Pr 10 km dBm", dbm(P10k), -64.54, tol=0.02)

    # --- P8  far field ------------------------------------------------
    chk("c3 p8 df", 2 * 1 ** 2 / lam, 6.0, tol=0.01)

    # --- P9  Okumura forward ------------------------------------------
    L50, lf, ghte, ghre = okumura(50e3, 900e6, 100, 10, 43, 9)
    chk("c3 p9 Lf", lf, 125.51, tol=0.02)
    chk("c3 p9 Lf alt", 32.44 + 20 * math.log10(900) + 20 * math.log10(50),
        125.50, tol=0.03)
    chk("c3 p9 G(hte)", ghte, -6.02, tol=0.02)
    chk("c3 p9 G(hre)", ghre, 10.46, tol=0.02)
    chk("c3 p9 L50", L50, 155.07, tol=0.02)
    chk("c3 p9 EIRP dBm", dbm(1000), 60.0, tol=0.01)
    pr = 60 - L50 + 10
    chk("c3 p9 Pr dBm", pr, -85.07, tol=0.02)
    chk("c3 p9 Pr pW", watts(pr) * 1e12, 3.11, tol=0.02)

    # --- P10  Okumura reverse -----------------------------------------
    ghte = 20 * math.log10(40 / 200.0)
    ghre = 10 * math.log10(2 / 3.0)
    chk("c3 p10 G(hte)", ghte, -13.98, tol=0.02)
    chk("c3 p10 G(hre)", ghre, -1.76, tol=0.02)
    lf = 167 - 34 + ghte + ghre + 0
    chk("c3 p10 Lf", lf, 117.26, tol=0.02)
    lam21 = c / 2.1e9
    chk("c3 p10 lambda", lam21, 0.1429, tol=2e-4)
    d = lam21 / (4 * math.pi) * 10 ** (lf / 20)
    chk("c3 p10 d m", d, 8292, tol=8)
    chk("c3 p10 back-check", 32.44 + 20 * math.log10(2100) + 20 * math.log10(d / 1000),
        117.26, tol=0.03)

    # --- P11  Hata medium city ----------------------------------------
    L50, a = hata_urban(950, 45, 5, 10, "medium")
    chk("c3 p11 a(hre)", a, 9.032, tol=2e-3)
    chk("c3 p11 L50", L50, 149.64, tol=0.02)
    lf950 = math.log10(950)
    chk("c3 p11 term 26.16 log fc", 26.16 * lf950, 77.897, tol=2e-3)
    chk("c3 p11 term -13.82 log hte", -13.82 * math.log10(45), -22.847, tol=2e-3)
    chk("c3 p11 term slope", (44.9 - 6.55 * math.log10(45)) * 1.0, 34.072, tol=3e-3)
    plfs = 32.44 + 20 * math.log10(950) + 20 * math.log10(10)
    chk("c3 p11 PLfs", plfs, 112.00, tol=0.02)
    chk("c3 p11 excess", L50 - plfs, 37.64, tol=0.03)

    # --- P12  Hata reverse (cell radius) ------------------------------
    lf900 = math.log10(900)
    a = (1.1 * lf900 - 0.7) * 1 - (1.56 * lf900 - 0.8)
    chk("c3 p12 a(hre)", a, -1.259, tol=2e-3)
    plmax = dbm(50) + 91
    chk("c3 p12 Pt dBm", dbm(50), 46.99, tol=0.02)
    chk("c3 p12 PLmax", plmax, 137.99, tol=0.02)
    A = 69.55 + 26.16 * lf900 - 13.82 * math.log10(30) - a
    B = 44.9 - 6.55 * math.log10(30)
    chk("c3 p12 A", A, 127.678, tol=3e-3)
    chk("c3 p12 B", B, 35.225, tol=2e-3)
    chk("c3 p12 log d", (plmax - A) / B, 0.29274, tol=2e-4)
    d = 10 ** ((plmax - A) / B)
    chk("c3 p12 d km", d, 1.962, tol=2e-3)
    chk("c3 p12 hex area", hex_area(d), 10.00, tol=0.02)
    chk("c3 p12 circle area", math.pi * d * d, 12.10, tol=0.02)

    # --- P13  Hata large city -----------------------------------------
    L50, a = hata_urban(900, 100, 2, 4, "large")
    chk("c3 p13 a(hre)", a, 1.045, tol=2e-3)
    chk("c3 p13 L50", L50, 137.29, tol=0.02)
    chk("c3 p13 term 26.16 log fc", 26.16 * lf900, 77.281, tol=2e-3)
    chk("c3 p13 term slope", (44.9 - 6.55 * 2) * math.log10(4), 19.147, tol=3e-3)

    # --- P14  two-ray vs free space -----------------------------------
    lam800 = c / 800e6
    chk("c3 p14 lambda", lam800, 0.375, tol=1e-4)
    dc = 4 * math.pi * 30 * 2 / lam800
    chk("c3 p14 dc", dc, 2011, tol=2)
    pl2 = 40 * math.log10(1e4) - 20 * math.log10(30) - 20 * math.log10(2)
    chk("c3 p14 PL 2-ray", pl2, 124.44, tol=0.02)
    plfs = 32.44 + 20 * math.log10(800) + 20 * math.log10(10)
    chk("c3 p14 PL fs", plfs, 110.50, tol=0.02)
    chk("c3 p14 difference", pl2 - plfs, 13.94, tol=0.02)

    # --- P15  reverse-link distance -----------------------------------
    plmax = 15 + 20 - 3 + 5 - 3 + 80 - 10
    chk("c3 p15 PLmax rev", plmax, 104)
    chk("c3 p15 PLmax fwd", 20 + 5 - 3 + 20 - 3 + 75 - 10, 104)
    lf = plmax - 43 + (-6.02) + 10.46 + 9
    chk("c3 p15 Lf", lf, 74.44, tol=0.03)
    d = lam / (4 * math.pi) * 10 ** (lf / 20)
    chk("c3 p15 d m", d, 139.8, tol=0.5)

    # --- P16  2.4 GHz feasibility -------------------------------------
    lam24 = c / 2.4e9
    chk("c3 p16 lambda", lam24, 0.125, tol=1e-4)
    lf10 = 32.44 + 20 * math.log10(2400) + 20 * math.log10(10)
    chk("c3 p16 Lf", lf10, 120.05, tol=0.02)
    L50 = lf10 + 20 - (-6.02) - 10.46 - 13
    chk("c3 p16 L50", L50, 122.61, tol=0.03)
    fwd = 20 + 5 - 3 + 20 - 3 - L50
    rev = 15 + 20 - 3 + 5 - 3 - L50
    chk("c3 p16 fwd Pr", fwd, -83.61, tol=0.03)
    chk("c3 p16 rev Pr", rev, -88.61, tol=0.03)
    chk("c3 p16 fwd margin", fwd + 75, -8.61, tol=0.03)
    chk("c3 p16 rev margin", rev + 80, -8.61, tol=0.03)
    lfmax = (L50 - 8.61) - 20 + (-6.02) + 10.46 + 13
    chk("c3 p16 Lf max", lfmax, 111.44, tol=0.05)
    chk("c3 p16 workable d km",
        lam24 / (4 * math.pi) * 10 ** (lfmax / 20) / 1000, 3.71, tol=0.02)

    # --- P17.1  70 Ma PDP ---------------------------------------------
    s, mean, m2, rms = pdp([-10, 0], [1, 2])
    chk("c3 p17.1 sum P", s, 1.1)
    chk("c3 p17.1 sum Pt", mean * s, 2.1)
    chk("c3 p17.1 sum Pt2", m2 * s, 4.1)
    chk("c3 p17.1 mean", mean, 1.909, tol=1e-3)
    chk("c3 p17.1 m2", m2, 3.727, tol=1e-3)
    chk("c3 p17.1 sigma", rms, 0.287, tol=1e-3)
    chk("c3 p17.1 Bc90 kHz", 1 / (50 * rms * 1e-6) / 1e3, 69.6, tol=0.15)
    chk("c3 p17.1 Bc50 kHz", 1 / (5 * rms * 1e-6) / 1e3, 695.7, tol=1.5)

    # --- P17.2  75 Bh PDP ---------------------------------------------
    s, mean, m2, rms = pdp([0, 0, -10, -20], [0, 50, 75, 100])
    chk("c3 p17.2 sum P", s, 2.11)
    chk("c3 p17.2 sum Pt", mean * s, 58.5)
    chk("c3 p17.2 sum Pt2", m2 * s, 3162.5)
    chk("c3 p17.2 mean", mean, 27.725, tol=2e-3)
    chk("c3 p17.2 m2", m2, 1498.82, tol=0.02)
    chk("c3 p17.2 mean^2", mean ** 2, 768.68, tol=0.02)
    chk("c3 p17.2 sigma", rms, 27.02, tol=0.01)
    chk("c3 p17.2 Ts us", 10 * rms, 270.2, tol=0.1)
    chk("c3 p17.2 Rs ksym", 1 / (10 * rms * 1e-6) / 1e3, 3.70, tol=0.01)

    # --- P17.3  71 Ma PDP ---------------------------------------------
    s, mean, m2, rms = pdp([0, -10, -20, -23], [0, 100, 200, 400])
    chk("c3 p17.3 sum P", s, 1.1150, tol=1e-4)
    chk("c3 p17.3 sum Pt", mean * s, 14.005, tol=5e-3)
    chk("c3 p17.3 sum Pt2", m2 * s, 2201.6, tol=1.0)
    chk("c3 p17.3 mean", mean, 12.560, tol=5e-3)
    chk("c3 p17.3 m2", m2, 1974.78, tol=0.5)
    chk("c3 p17.3 sigma", rms, 42.63, tol=0.02)
    chk("c3 p17.3 Bc90 kHz", 1 / (50 * rms * 1e-9) / 1e3, 469.2, tol=0.5)
    chk("c3 p17.3 Bc50 MHz", 1 / (5 * rms * 1e-9) / 1e6, 4.69, tol=0.01)
    assert 30e3 < 1 / (50 * rms * 1e-9), "AMPS should be flat"
    assert 200e3 < 1 / (50 * rms * 1e-9), "GSM strictly flat on Bc90"
    chk("c3 p17.3 GSM margin factor", (1 / (50 * rms * 1e-9)) / 200e3, 2.3, tol=0.05)

    # --- P17.4  81 Bh PDP ---------------------------------------------
    s, mean, m2, rms = pdp([-20, -10, -10, 0], [0, 1, 2, 5])
    chk("c3 p17.4 sum P", s, 1.21)
    chk("c3 p17.4 sum Pt", mean * s, 5.30)
    chk("c3 p17.4 sum Pt2", m2 * s, 25.50)
    chk("c3 p17.4 mean", mean, 4.380, tol=1e-3)
    chk("c3 p17.4 m2", m2, 21.074, tol=2e-3)
    chk("c3 p17.4 mean^2", mean ** 2, 19.183, tol=3e-3)
    chk("c3 p17.4 sigma", rms, 1.375, tol=1e-3)
    chk("c3 p17.4 Bc50 Hz", 1 / (5 * rms), 0.1455, tol=5e-4)
    chk("c3 p17.4 Bc50 kHz (us reading)", 1 / (5 * rms * 1e-6) / 1e3, 145.5, tol=0.5)

    # --- P18  Doppler --------------------------------------------------
    v = 70 * 1000 / 3600
    chk("c3 p18 v", v, 19.444, tol=2e-3)
    fm = v / lam
    chk("c3 p18 fm", fm, 58.33, tol=0.02)
    chk("c3 p18 Tc ms", 0.423 / fm * 1000, 7.25, tol=0.01)


# =====================================================================
#  CHAPTER 5
# =====================================================================
def ch5():
    # --- P1  optimum weights -------------------------------------------
    det = 1 * 1 - 0.5 * 0.5
    chk("c5 p1 det R", det, 0.75)
    inv = [[1 / det, -0.5 / det], [-0.5 / det, 1 / det]]
    chk("c5 p1 Rinv 00", inv[0][0], 1.3333, tol=5e-4)
    chk("c5 p1 Rinv 01", inv[0][1], -0.6667, tol=5e-4)
    w0 = inv[0][0] * 0.8 + inv[0][1] * 0.5
    w1 = inv[1][0] * 0.8 + inv[1][1] * 0.5
    chk("c5 p1 w0", w0, 0.7333, tol=5e-4)
    chk("c5 p1 w1", w1, 0.1333, tol=5e-4)
    chk("c5 p1 pTw", 0.8 * w0 + 0.5 * w1, 0.6533, tol=5e-4)
    chk("c5 p1 xi_min", 1 - (0.8 * w0 + 0.5 * w1), 0.3467, tol=5e-4)

    # --- P2  selection diversity ---------------------------------------
    ratio = 10 ** 1.0 / 10 ** 2.0
    chk("c5 p2 ratio", ratio, 0.1)
    base = 1 - math.exp(-ratio)
    chk("c5 p2 base", base, 0.09516, tol=1e-5)
    for M, want in ((1, 9.516e-2), (2, 9.056e-3), (4, 8.201e-5), (5, 7.804e-6)):
        chk(f"c5 p2 outage M={M}", base ** M, want)
    harm = [sum(1 / k for k in range(1, M + 1)) for M in range(1, 6)]
    for M, want in zip(range(1, 6), (1.0, 1.5, 1.8333, 2.0833, 2.2833)):
        chk(f"c5 p2 harmonic M={M}", harm[M - 1], want, tol=5e-4)
    chk("c5 p2 mean SNR M=5", 100 * 2.2833, 228.33, tol=0.02)
    chk("c5 p2 mean SNR dB", db(100 * harm[4]), 23.59, tol=0.02)
    for M, want in ((2, 1.76), (3, 2.63), (4, 3.19), (5, 3.59)):
        chk(f"c5 p2 gain dB M={M}", db(harm[M - 1]), want, tol=0.02)
    # MRC
    chk("c5 p2 MRC mean dB", db(5 * 100), 26.99, tol=0.02)
    chk("c5 p2 MRC gain dB", db(5 * 100) - 20, 6.99, tol=0.02)
    mrc = 1 - math.exp(-ratio) * sum(ratio ** (k - 1) / math.factorial(k - 1)
                                     for k in range(1, 6))
    chk("c5 p2 MRC outage", mrc, 7.668e-8, rel=5e-3)

    # --- P3  interleaver ------------------------------------------------
    n, k, m = 15, 11, 8
    chk("c5 p3 t", (n - k) // 2, 2)
    chk("c5 p3 mn", m * n, 120)
    chk("c5 p3 mk", m * k, 88)
    chk("c5 p3 burst", m * ((n - k) // 2), 16)
    chk("c5 p3 rate", (m * k) / (m * n), 0.733, tol=1e-3)
    chk("c5 p3 delay ms", 2 * 120 / 22800.0 * 1000, 10.5, tol=0.05)

    # --- P4  equalizer sizing -------------------------------------------
    Ts = 1 / 270833.0
    chk("c5 p4 Ts us", Ts * 1e6, 3.692, tol=2e-3)
    chk("c5 p4 sigma/Ts", 5.0 / (Ts * 1e6), 1.35, tol=0.01)
    v = 70 * 1000 / 3600
    fm = v / (c / 900e6)
    chk("c5 p4 fm", fm, 58.33, tol=0.02)
    chk("c5 p4 Tc ms", 0.423 / fm * 1000, 7.25, tol=0.01)
    chk("c5 p4 retrain/s", 1 / (0.423 / fm), 138, tol=0.6)
    chk("c5 p4 GSM frames/s", 1 / 4.615e-3, 217, tol=0.6)

    # --- P5  cell-edge diversity gain -----------------------------------
    g = 10 ** 0.8
    G = 10 ** 1.5
    chk("c5 p5 gamma", g, 6.31, tol=5e-3)
    chk("c5 p5 Gamma", G, 31.62, tol=0.01)
    chk("c5 p5 ratio", g / G, 0.1995, tol=5e-4)
    p1 = 1 - math.exp(-g / G)
    chk("c5 p5 outage 1", 100 * p1, 18.1, tol=0.05)
    chk("c5 p5 outage 2", 100 * p1 ** 2, 3.27, tol=0.01)
    x = -math.log(1 - p1 ** 2)
    chk("c5 p5 required ratio", x, 0.03327, tol=1e-5)
    Gp = g / x
    chk("c5 p5 Gamma'", Gp, 189.7, tol=0.2)
    chk("c5 p5 Gamma' dB", db(Gp), 22.78, tol=0.02)
    chk("c5 p5 diversity gain", db(Gp) - 15, 7.78, tol=0.02)
    chk("c5 p5 radius factor", 10 ** (7.78 / 35), 1.67, tol=0.01)
    chk("c5 p5 area factor", (10 ** (7.78 / 35)) ** 2, 2.8, tol=0.02)


# =====================================================================
#  CHAPTER 6
# =====================================================================
def hamming_parity(bits, group):
    return sum(bits[g] for g in group) % 2


def ch6():
    G1, G2, G4 = [1, 3, 5, 7], [2, 3, 6, 7], [4, 5, 6, 7]

    # --- P1A  encode 1011 -----------------------------------------------
    w = {7: 1, 6: 0, 5: 1, 3: 1, 1: 0, 2: 0, 4: 0}
    w[1] = hamming_parity(w, [3, 5, 7])
    w[2] = hamming_parity(w, [3, 6, 7])
    w[4] = hamming_parity(w, [5, 6, 7])
    chk("c6 p1 P1", w[1], 1)
    chk("c6 p1 P2", w[2], 0)
    chk("c6 p1 P4", w[4], 0)
    code = "".join(str(w[i]) for i in range(7, 0, -1))
    assert code == "1010101", f"c6 p1A codeword {code}"

    # --- P1B  detect in 1011011 ------------------------------------------
    rx = {7: 1, 6: 0, 5: 1, 4: 1, 3: 0, 2: 1, 1: 1}
    s1 = hamming_parity(rx, G1)
    s2 = hamming_parity(rx, G2)
    s4 = hamming_parity(rx, G4)
    chk("c6 p1 syn bit P1", s1, 1)
    chk("c6 p1 syn bit P2", s2, 0)
    chk("c6 p1 syn bit P4", s4, 1)
    syn = s1 * 1 + s2 * 2 + s4 * 4
    chk("c6 p1 syndrome", syn, 5)
    rx[syn] ^= 1
    corrected = "".join(str(rx[i]) for i in range(7, 0, -1))
    assert corrected == "1001011", f"c6 p1B corrected {corrected}"
    data = f"{rx[7]}{rx[6]}{rx[5]}{rx[3]}"
    assert data == "1000", f"c6 p1B data {data}"

    # --- Hamming parameter table -----------------------------------------
    for m, n_w, k_w, r_w in ((3, 7, 4, 0.571), (4, 15, 11, 0.733),
                             (5, 31, 26, 0.839), (6, 63, 57, 0.905)):
        n = 2 ** m - 1
        k = 2 ** m - m - 1
        chk(f"c6 hamming n m={m}", n, n_w)
        chk(f"c6 hamming k m={m}", k, k_w)
        chk(f"c6 hamming rate m={m}", k / n, r_w, tol=1e-3)

    # --- P2A  convolutional encoding --------------------------------------
    msg = [1, 0, 1, 1, 0, 0]
    M1 = M2 = 0
    out = []
    for M in msg:
        out.append((M ^ M1 ^ M2, M ^ M2))
        M1, M2 = M, M1
    got = " ".join(f"{a}{b}" for a, b in out)
    assert got == "11 10 00 01 01 11", f"c6 p2A encoded {got}"
    chk("c6 p2A output bits", 2 * len(msg), 12)
    chk("c6 p2A rate with tail", 4 / 12, 1 / 3, tol=1e-9)

    # --- P2B  Viterbi decoding --------------------------------------------
    def branch(state, bit):
        m1, m2 = state
        return (bit ^ m1 ^ m2, bit ^ m2), (bit, m1)

    Y = [(1, 1), (0, 1), (1, 0)]
    paths = {(0, 0): (0, [])}
    snapshots = []
    for y in Y:
        new = {}
        for st, (metric, hist) in paths.items():
            for bit in (0, 1):
                o, ns = branch(st, bit)
                bm = (o[0] != y[0]) + (o[1] != y[1])
                cand = (metric + bm, hist + [bit])
                if ns not in new or cand[0] < new[ns][0]:
                    new[ns] = cand
        paths = new
        snapshots.append({k: v[0] for k, v in paths.items()})
    chk("c6 p2B step1 state00", snapshots[0][(0, 0)], 2)
    chk("c6 p2B step1 state10", snapshots[0][(1, 0)], 0)
    chk("c6 p2B step2 state00", snapshots[1][(0, 0)], 3)
    chk("c6 p2B step2 state01", snapshots[1][(0, 1)], 2)
    chk("c6 p2B step2 state10", snapshots[1][(1, 0)], 3)
    chk("c6 p2B step2 state11", snapshots[1][(1, 1)], 0)
    chk("c6 p2B step3 state00", snapshots[2][(0, 0)], 3)
    chk("c6 p2B step3 state01", snapshots[2][(0, 1)], 2)
    chk("c6 p2B step3 state10", snapshots[2][(1, 0)], 3)
    chk("c6 p2B step3 state11", snapshots[2][(1, 1)], 0)
    best = min(paths.items(), key=lambda kv: kv[1][0])
    assert best[1][1] == [1, 1, 1], f"c6 p2B decoded {best[1][1]}"
    chk("c6 p2B best metric", best[1][0], 0)

    # --- P3  sub-band coder -------------------------------------------------
    bands = [(225, 450, 4, 450, 1800), (450, 900, 3, 900, 2700),
             (1000, 1500, 2, 1000, 2000), (1800, 2700, 1, 1800, 1800)]
    total = 0
    for lo, hi, bits, fs_w, r_w in bands:
        fs = 2 * (hi - lo)
        chk(f"c6 p3 fs {lo}-{hi}", fs, fs_w)
        chk(f"c6 p3 rate {lo}-{hi}", fs * bits, r_w)
        total += fs * bits
    chk("c6 p3 total bps", total, 8300)
    chk("c6 p3 compression vs PCM", 64000 / total, 7.7, tol=0.05)

    # --- P4  FDMA speech coder bound ----------------------------------------
    chk("c6 p4 band MHz", 826 - 810, 16)
    traffic = 0.9 * 16e6
    chk("c6 p4 traffic MHz", traffic / 1e6, 14.4)
    ch_bw = traffic / 1150
    chk("c6 p4 channel kHz", ch_bw / 1e3, 12.52, tol=0.01)
    raw = 1.68 * ch_bw
    chk("c6 p4 raw kbps", raw / 1e3, 21.04, tol=0.01)
    chk("c6 p4 speech kbps", 0.5 * raw / 1e3, 10.52, tol=0.01)

    # --- P5  quantizer distortion --------------------------------------------
    def seg(level, lo, hi):
        # integral of (x-level)^2 * x/32 dx from lo to hi, done in closed form
        def F(x):
            return (x ** 4 / 4 - 2 * level * x ** 3 / 3 + level ** 2 * x ** 2 / 2) / 32
        return F(hi) - F(lo)

    parts = [seg(1, 0, 2), seg(3, 2, 4), seg(5, 4, 6), seg(7, 6, 8)]
    for i, want in enumerate((1 / 48, 3 / 48, 5 / 48, 7 / 48)):
        chk(f"c6 p5 segment {i}", parts[i], want, tol=1e-9)
    D = sum(parts)
    chk("c6 p5 D", D, 1 / 3, tol=1e-9)
    chk("c6 p5 D printed", D, 0.3333, tol=5e-4)
    S = (8 ** 4 / 4) / 32
    chk("c6 p5 S", S, 32)
    chk("c6 p5 SDR dB", db(S / D), 19.82, tol=0.02)
    chk("c6 p5 pdf integral", (8 ** 2 / 64), 1.0)

    # --- P7  coding gain -------------------------------------------------------
    chk("c6 p7 gain", 10.5 - 4.5, 6)
    chk("c6 p7 power factor", 10 ** 0.6, 3.98, tol=5e-3)
    chk("c6 p7 range factor", 10 ** (6 / 35), 1.48, tol=5e-3)
    chk("c6 p7 area factor", (10 ** (6 / 35)) ** 2, 2.2, tol=0.01)


# =========================================================================
#  CHAPTER 7 — MULTIPLE ACCESS
# =========================================================================
def ch7():
    # --- P1  FDMA channel count, N = (Bt - 2 Bguard) / Bc ----------------------
    def fdma(bt, bguard, bc):
        return (bt - 2 * bguard) / bc

    # 1.1  80 Ba : 25 MHz, 100 kHz guard, 200 kHz channel
    chk("c7 p1.1 usable Hz", 25e6 - 2 * 100e3, 24.8e6)
    chk("c7 p1.1 N", fdma(25e6, 100e3, 200e3), 124)
    # 1.2  79 Ch / 77 Ch : 12.8 MHz, 10 kHz guard, 30 kHz channel
    chk("c7 p1.2 usable kHz", 12800 - 2 * 10, 12780)
    chk("c7 p1.2 N", fdma(12.8e6, 10e3, 30e3), 426)
    # 1.3  78 Ch : 12.5 MHz, 10 kHz guard, 30 kHz channel  (Rappaport Ex 8.2)
    chk("c7 p1.3 usable kHz", 12500 - 2 * 10, 12480)
    chk("c7 p1.3 N", fdma(12.5e6, 10e3, 30e3), 416)
    # 1.4  inverse: Bt from N. Must round-trip back to 1.3's input.
    bt = 416 * 30e3 + 2 * 10e3
    chk("c7 p1.4 channels term", 416 * 30e3, 12.48e6)
    chk("c7 p1.4 guard term", 2 * 10e3, 20e3)
    chk("c7 p1.4 Bt MHz", bt / 1e6, 12.5)
    chk("c7 p1.4 round trip", fdma(bt, 10e3, 30e3), 416)

    # --- P2  N-TDMA users per cluster, 80 Ch ----------------------------------
    chk("c7 p2 usable kHz", 25000 - 2 * 20, 24960)
    chk("c7 p2 Nu", fdma(25e6, 20e3, 30e3), 832)
    # the guard bands cost well under 1 % of the allocation
    chk("c7 p2 no-guard bound", 25000 / 30, 833.33, tol=0.01)

    # --- P3  GSM TDMA frame efficiency, 70 Bh / 74 Ma -------------------------
    slot = 6 + 8.25 + 26 + 2 * 58
    chk("c7 p3 slot bits", slot, 156.25, tol=1e-9)
    b_T = 8 * slot
    chk("c7 p3 frame bits", b_T, 1250, tol=1e-9)
    chk("c7 p3 tail total", 8 * 6, 48)
    chk("c7 p3 guard total", 8 * 8.25, 66, tol=1e-9)
    chk("c7 p3 train total", 8 * 26, 208)
    b_OH = 8 * 6 + 8 * 8.25 + 8 * 26
    chk("c7 p3 overhead bits", b_OH, 322, tol=1e-9)
    chk("c7 p3 overhead frac", b_OH / b_T, 0.2576, tol=1e-6)
    eta = (1 - b_OH / b_T) * 100
    chk("c7 p3 efficiency %", eta, 74.24, tol=5e-3)
    # cross-check via the payload: 8 slots x 116 data bits
    chk("c7 p3 payload bits", 8 * 116, 928)
    chk("c7 p3 payload frac %", 100 * 8 * 116 / b_T, 74.24, tol=5e-3)
    # 3.3 timing, at 270.833 kbps
    Tb = 1 / 270833.0
    chk("c7 p3.3 Tb us", Tb * 1e6, 3.692, tol=1e-3)
    Tslot = slot * Tb
    chk("c7 p3.3 Tslot us", Tslot * 1e6, 576.9, tol=0.2)
    chk("c7 p3.3 Tslot ms", Tslot * 1e3, 0.577, tol=1e-3)
    Tf = 8 * Tslot
    chk("c7 p3.3 Tframe ms", Tf * 1e3, 4.615, tol=5e-3)
    chk("c7 p3.3 Tframe via bits ms", b_T * Tb * 1e3, 4.615, tol=5e-3)
    chk("c7 p3.3 frame rate", 1 / Tf, 216.7, tol=0.2)
    chk("c7 p3.3 frame rate via bits", 270833.0 / b_T, 216.7, tol=0.2)
    # 3.3 simultaneous GSM users: 25 MHz / (200 kHz / 8)
    chk("c7 p3.3 share kHz", 200 / 8, 25)
    chk("c7 p3.3 users", 25e6 / (200e3 / 8), 1000)

    # --- P4  Hadamard H8 ------------------------------------------------------
    def sylvester(n):
        H = [[1]]
        while len(H) < n:
            m = len(H)
            H = ([H[i] + H[i] for i in range(m)] +
                 [H[i] + [-v for v in H[i]] for i in range(m)])
        return H

    H2, H4, H8 = sylvester(2), sylvester(4), sylvester(8)
    chk("c7 p4 H2 order", len(H2), 2)
    chk("c7 p4 H4 order", len(H4), 4)
    chk("c7 p4 H8 order", len(H8), 8)
    # every entry is +-1
    chk("c7 p4 entries pm1", sum(1 for r in H8 for v in r if v in (1, -1)), 64)
    # the printed H8, row by row, exactly as it appears in ch7-num.tex
    printed = [
        [1,  1,  1,  1,  1,  1,  1,  1],
        [1, -1,  1, -1,  1, -1,  1, -1],
        [1,  1, -1, -1,  1,  1, -1, -1],
        [1, -1, -1,  1,  1, -1, -1,  1],
        [1,  1,  1,  1, -1, -1, -1, -1],
        [1, -1,  1, -1, -1,  1, -1,  1],
        [1,  1, -1, -1, -1, -1,  1,  1],
        [1, -1, -1,  1, -1,  1,  1, -1],
    ]
    for i in range(8):
        chk(f"c7 p4 H8 row {i+1}", sum(a * b for a, b in zip(H8[i], printed[i])), 8)
    # H4 as printed
    printed4 = [[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]]
    for i in range(4):
        chk(f"c7 p4 H4 row {i+1}", sum(a * b for a, b in zip(H4[i], printed4[i])), 4)
    # orthogonality of every distinct pair, and self-product = N
    for i in range(8):
        for j in range(8):
            want = 8 if i == j else 0
            chk(f"c7 p4 dot {i}{j}",
                sum(a * b for a, b in zip(printed[i], printed[j])), want, tol=1e-9)
    # the two checks printed in the notes
    chk("c7 p4 row2.row3 printed", sum(a * b for a, b in zip(printed[1], printed[2])), 0,
        tol=1e-9)
    chk("c7 p4 row1.row5 printed", sum(a * b for a, b in zip(printed[0], printed[4])), 0,
        tol=1e-9)
    # binary Walsh mapping: +1 -> 0, -1 -> 1; every non-zero word has N/2 ones
    walsh = [[0 if v == 1 else 1 for v in r] for r in printed]
    chk("c7 p4 W0 ones", sum(walsh[0]), 0)
    for i in range(1, 8):
        chk(f"c7 p4 W{i} ones", sum(walsh[i]), 4)
    chk("c7 p4 dmin", 8 // 2, 4)
    chk("c7 p4 k bits", math.log2(8), 3, tol=1e-9)
    # the printed binary strings
    for i, want in enumerate(["00000000", "01010101", "00110011", "01100110",
                              "00001111", "01011010", "00111100", "01101001"]):
        chk(f"c7 p4 W{i} string", int("".join(map(str, walsh[i])), 2), int(want, 2))

    # --- P5  CDMA encode / decode --------------------------------------------
    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    def add(seqs):
        return [sum(col) for col in zip(*seqs)]

    # 5.1  four stations, data 1,0,1,1
    C = {1: [1, 1, 1, 1], 2: [1, -1, 1, -1], 3: [1, 1, -1, -1], 4: [1, -1, -1, 1]}
    d = {1: 1, 2: -1, 3: 1, 4: 1}          # bit 1 -> +1, bit 0 -> -1
    # the orthogonality spot checks printed in the notes
    chk("c7 p5.1 C1.C2", dot(C[1], C[2]), 0, tol=1e-9)
    chk("c7 p5.1 C3.C4", dot(C[3], C[4]), 0, tol=1e-9)
    chk("c7 p5.1 C1.C1", dot(C[1], C[1]), 4)
    # every encoded contribution, as printed
    for k, want in {1: [1, 1, 1, 1], 2: [-1, 1, -1, 1],
                    3: [1, 1, -1, -1], 4: [1, -1, -1, 1]}.items():
        got = [d[k] * v for v in C[k]]
        chk(f"c7 p5.1 d{k}C{k}", dot(got, want), 4)
    S = add([[d[k] * v for v in C[k]] for k in C])
    chk("c7 p5.1 S", dot(S, [2, 2, -2, 2]), 16)      # S == (+2,+2,-2,+2)
    for k, s_want, bit in ((1, 4, 1), (2, -4, 0), (3, 4, 1), (4, 4, 1)):
        chk(f"c7 p5.1 sum{k}", dot(S, C[k]), s_want, tol=1e-9)
        chk(f"c7 p5.1 bit{k}", dot(S, C[k]) / 4, 1 if bit else -1, tol=1e-9)
    # the element-wise products printed in the decode table
    for k, want in {1: [2, 2, -2, 2], 2: [2, -2, -2, -2],
                    3: [2, 2, 2, -2], 4: [2, -2, 2, 2]}.items():
        got = [a * b for a, b in zip(S, C[k])]
        chk(f"c7 p5.1 prod{k}", dot(got, want), dot(want, want))

    # 5.2  three stations, B silent
    CA, CB, CC = [1, -1, -1, 1], [1, 1, 1, 1], [1, -1, 1, -1]
    S2 = add([[-1 * v for v in CA], [0 * v for v in CB], [1 * v for v in CC]])
    chk("c7 p5.2 A enc", dot([-1 * v for v in CA], [-1, 1, 1, -1]), 4)
    chk("c7 p5.2 B enc", sum(abs(v) for v in [0 * v for v in CB]), 0)
    chk("c7 p5.2 C enc", dot([1 * v for v in CC], [1, -1, 1, -1]), 4)
    chk("c7 p5.2 S", dot(S2, [0, 0, 2, -2]), 8)      # S2 == (0,0,+2,-2)
    chk("c7 p5.2 S chip1", S2[0], 0)
    chk("c7 p5.2 S chip2", S2[1], 0)
    chk("c7 p5.2 S chip3", S2[2], 2)
    chk("c7 p5.2 S chip4", S2[3], -2)
    chk("c7 p5.2 decode A", dot(S2, CA), -4, tol=1e-9)
    chk("c7 p5.2 decode B", dot(S2, CB), 0, tol=1e-9)
    chk("c7 p5.2 decode C", dot(S2, CC), 4, tol=1e-9)
    chk("c7 p5.2 A bit", dot(S2, CA) / 4, -1, tol=1e-9)
    chk("c7 p5.2 B silent", dot(S2, CB) / 4, 0, tol=1e-9)
    chk("c7 p5.2 C bit", dot(S2, CC) / 4, 1, tol=1e-9)
    for lbl, code, want in (("A", CA, [0, 0, -2, -2]), ("B", CB, [0, 0, 2, -2]),
                            ("C", CC, [0, 0, 2, 2])):
        got = [a * b for a, b in zip(S2, code)]
        chk(f"c7 p5.2 prod{lbl}", dot(got, want), dot(want, want))

    # --- P6  IS-95 CDMA capacity ---------------------------------------------
    W, R = 1.25e6, 9600.0
    pg = W / R
    chk("c7 p6 W/R", pg, 130.21, tol=0.01)
    ebno = pg / (14 - 1)
    chk("c7 p6 Eb/N0 linear", ebno, 10.02, tol=0.01)
    chk("c7 p6 Eb/N0 dB", db(ebno), 10.01, tol=0.01)
    alpha = 3 / 8
    chk("c7 p6 1/alpha", 1 / alpha, 8 / 3, tol=1e-9)
    chk("c7 p6 pg/ebno", pg / 10, 13.021, tol=1e-3)
    n_sector = 1 + (1 / alpha) * (pg / 10)
    chk("c7 p6 users/sector", n_sector, 35.72, tol=0.02)
    chk("c7 p6 users/cell", 3 * n_sector, 107.2, tol=0.1)
    chk("c7 p6 users/cell rounded", round(3 * n_sector), 107)


def main():
    for fn in (ch2, ch3, ch5, ch6, ch7):
        try:
            fn()
        except AssertionError as e:
            FAIL.append(f"{fn.__name__}: {e}")
    total = N_OK + len(FAIL)
    if FAIL:
        print(f"FAILED {len(FAIL)} of {total} checks:\n")
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print(f"all {total} checks pass")


if __name__ == "__main__":
    main()
