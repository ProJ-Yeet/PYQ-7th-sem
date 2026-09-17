# -*- coding: utf-8 -*-
"""Chapter 5 microwave-tube checks, self-testing.

Chapter 5 sets no numerical PYQ, but its theory makes quantitative claims that a
note can get wrong: where bunching peaks, why a reflex klystron needs n + 3/4
cycles, what the magnetron's cut-off field is, how slow a helix makes the wave.
Each is checked here by simulating electrons, not by quoting the textbook result:

  * two-cavity klystron: electrons leave a gap with sinusoidal velocity
    modulation, drift ballistically, and the fundamental of the arrival current
    is measured -> it must equal 2 J1(X) and peak at X = 1.841;
  * reflex klystron: electrons are turned round by a linear retarding field
    (round-trip time proportional to entry velocity) and the power they return
    to the gap is measured -> positive, and largest, at n + 3/4 cycles;
  * cylindrical magnetron: electron trajectories are integrated in the radial
    log-potential plus axial B, and the grazing field is found by bisection ->
    it must match the Hull cut-off formula;
  * helix slow-wave velocity and the beam voltage that synchronises with it.

Run from src\\:   python tubes.py
"""
import cmath
import math
import random

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from scipy.special import j1

E_CH = 1.602176634e-19
M_E = 9.1093837015e-31
C = 3.0e8


def _close(a, b, tol=1e-6, what=""):
    if abs(a - b) > tol * max(1.0, abs(b)):
        raise AssertionError("%s: got %r, expected %r" % (what, a, b))


# ============================================================ transit time
def test_transit_time():
    # deck p7: 1 ns is 0.001 cycle at 1 MHz and a whole cycle at 1000 MHz
    tau = 1e-9
    _close(tau * 1e6, 0.001, what="1 MHz")
    _close(tau * 1e9, 1.0, what="1000 MHz")
    # electron speed after 100 V, and the transit time over a 1 mm gap
    v = math.sqrt(2 * E_CH * 100 / M_E)
    t = 1e-3 / (v / 2)       # uniform acceleration from rest: mean speed v/2
    return dict(v100=v, t1mm=t, cycles_at_1GHz=t * 1e9)


# ============================================================ klystron
def fundamental_ratio(X, n=20000, m=1e-3):
    """|I1|/I0 from a ballistic simulation with bunching parameter X.

    Small modulation depth m, drift angle theta0 = X/m. Each electron leaves at
    phase phi uniformly, speed v0(1 + m sin phi), arrives at phase
    phi + theta0/(1 + m sin phi). The fundamental of the arrival current is
    2 <exp(-j * arrival phase)>.
    """
    theta0 = X / m
    s = 0j
    for k in range(n):
        phi = 2 * math.pi * (k + 0.5) / n
        arr = phi + theta0 / (1 + m * math.sin(phi))
        s += cmath.exp(-1j * arr)
    return abs(2 * s / n)


def test_klystron():
    for X in (0.5, 1.0, 1.841, 2.5, 3.0):
        _close(fundamental_ratio(X), 2 * j1(X), tol=3e-3, what="I1 at X=%.3f" % X)
    r = minimize_scalar(lambda x: -j1(x), bounds=(1, 3), method="bounded")
    Xopt = r.x
    _close(Xopt, 1.8412, tol=1e-4, what="X_opt")
    peak = 2 * j1(Xopt)
    # efficiency = (1/2)(I1/I0)(V2/V0), V2 at most V0 -> 58 %
    eta_max = 0.5 * peak
    _close(eta_max, 0.5819, tol=1e-3, what="klystron efficiency")
    return dict(Xopt=Xopt, peak=peak, eta=eta_max)


# ============================================================ reflex klystron
def reflex_power(theta0, X=1.0, n=4000):
    """Average power the returning beam gives the gap, per unit (e beta V1 I0).

    Outgoing speed v0(1 + m sin phi); in a linear retarding field the round-trip
    time is proportional to speed, so the return phase is
    phi + theta0 (1 + m sin phi) = phi + theta0 + X sin phi.
    The gap voltage V1 sin(wt) ACCELERATES outgoing electrons, so it
    DECELERATES returning ones: each gives up e beta V1 sin(return phase).
    """
    s = 0.0
    for k in range(n):
        phi = 2 * math.pi * (k + 0.5) / n
        s += math.sin(phi + theta0 + X * math.sin(phi))
    return s / n


def test_reflex():
    X = 1.2
    # analytic: <sin(phi + theta0 + X sin phi)> = -J1(X) sin(theta0)
    for th in (0.3, 2.0, 4.0, 5.5):
        _close(reflex_power(th, X), -j1(X) * math.sin(th), tol=1e-6, what="reflex th=%.1f" % th)
    # scan theta0 over one cycle beyond n = 1: best at 2*pi*(1 + 3/4)
    grid = [2 * math.pi * (1 + k / 400.0) for k in range(400)]
    best = max(grid, key=lambda t: reflex_power(t, X, n=600))
    cycles = best / (2 * math.pi)
    _close(cycles, 1.75, tol=4e-3, what="optimum transit cycles")
    # and it takes power (negative) at n + 1/4
    assert reflex_power(2 * math.pi * 1.25, X) < 0
    # maximum efficiency for mode n: 2 X' J1(X') / (2 pi n + 3 pi / 2), X' J1 max at 2.405
    r = minimize_scalar(lambda x: -x * j1(x), bounds=(1, 4), method="bounded")
    Xp = r.x
    # d/dX [X J1(X)] = X J0(X) = 0 -> first zero of J0, 2.4048 (Liao rounds to 2.408)
    _close(Xp, 2.4048, tol=1e-4, what="X' opt")
    effs = [2 * Xp * j1(Xp) / (2 * math.pi * nn + 1.5 * math.pi) for nn in (0, 1, 2)]
    _close(effs[1], 0.2278, tol=2e-3, what="deck's 22.78 % is the n = 1 mode")
    return dict(cycles=cycles, Xp=Xp, effs=effs)


# ============================================================ magnetron
def hull_cutoff(V0, a, b):
    return math.sqrt(8 * M_E * V0 / E_CH) / (b * (1 - a * a / (b * b)))


def reaches_anode(B, V0, a, b):
    """Integrate one electron leaving the cathode at rest; True if it hits r = b."""
    k = E_CH * V0 / (M_E * math.log(b / a))   # outward acceleration * r
    wc = E_CH * B / M_E

    def rhs(t, s):
        x, y, vx, vy = s
        r2 = x * x + y * y
        ax = k * x / r2 - wc * vy        # F = -e (E + v x B), B along +z
        ay = k * y / r2 + wc * vx
        return [vx, vy, ax, ay]

    def hit(t, s):
        return math.hypot(s[0], s[1]) - b
    hit.terminal = True
    T = 6 * math.pi / wc if B > 0 else 1e-6
    sol = solve_ivp(rhs, (0, T), [a, 0, 0, 0], events=hit, rtol=1e-10, atol=1e-14,
                    max_step=T / 4000)
    return len(sol.t_events[0]) > 0


def test_magnetron():
    V0, a, b = 10e3, 5e-3, 10e-3
    Bh = hull_cutoff(V0, a, b)
    lo, hi = 0.5 * Bh, 1.5 * Bh
    assert reaches_anode(lo, V0, a, b) and not reaches_anode(hi, V0, a, b)
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if reaches_anode(mid, V0, a, b):
            lo = mid
        else:
            hi = mid
    Bsim = 0.5 * (lo + hi)
    _close(Bsim, Bh, tol=5e-3, what="Hull cut-off by trajectory")
    # modes of an N-cavity ring: phi = 2 pi n / N; pi-mode at n = N/2
    modes = {}
    for N in (4, 6, 8):
        modes[N] = [360.0 * n / N for n in range(0, N // 2 + 1)]
        assert modes[N][-1] == 180.0
    # the PYQ phase shifts: cavities per RF wavelength along the anode = 360/phi
    per_wave = {ph: 360.0 / ph for ph in (45, 60, 90, 180)}
    return dict(Bh=Bh, Bsim=Bsim, modes=modes, per_wave=per_wave)


# ============================================================ helix
def test_helix():
    p, r = 1.0e-3, 2.0e-3          # 1 mm pitch, 2 mm radius
    exact = p / math.sqrt(p * p + (2 * math.pi * r) ** 2)
    approx = p / (2 * math.pi * r)
    _close(exact, approx, tol=0.02, what="helix slowing factor")
    vp = C * exact
    V0 = 0.5 * M_E * vp * vp / E_CH    # non-relativistic, fine below ~10 kV
    # the deck's 'beam at the velocity of light' would need infinite voltage;
    # a 1 kV beam is at 0.063 c
    v1k = math.sqrt(2 * E_CH * 1e3 / M_E)
    return dict(slow=exact, vp=vp, V0=V0, frac1k=v1k / C)


# ============================================================ LNA
def friis(stages):
    """stages: [(F_linear, G_linear)]; returns total noise factor."""
    F, G = stages[0]
    tot, g = F, G
    for Fi, Gi in stages[1:]:
        tot += (Fi - 1) / g
        g *= Gi
    return tot


def test_friis():
    db = lambda x: 10 ** (x / 10)
    lna_first = friis([(db(1.0), db(20)), (db(8.0), db(10))])
    mixer_first = friis([(db(8.0), db(10)), (db(1.0), db(20))])
    assert lna_first < mixer_first
    return dict(lna=10 * math.log10(lna_first), mixer=10 * math.log10(mixer_first))


def main():
    t = test_transit_time()
    print("transit time       ok  100 V -> v = %.3e m/s; 1 mm gap = %.2e s = %.3f cycle at 1 GHz"
          % (t["v100"], t["t1mm"], t["cycles_at_1GHz"]))
    k = test_klystron()
    print("klystron bunching  ok  simulated I1/I0 = 2J1(X); peak X = %.4f, I1/I0 = %.4f, eta_max = %.1f %%"
          % (k["Xopt"], k["peak"], 100 * k["eta"]))
    r = test_reflex()
    print("reflex klystron    ok  best transit = %.3f cycles; X' = %.3f; eta n=0,1,2 = %s"
          % (r["cycles"], r["Xp"], ", ".join("%.2f %%" % (100 * e) for e in r["effs"])))
    m = test_magnetron()
    print("magnetron          ok  Hull B_c = %.5f T, trajectory bisection = %.5f T (V0 10 kV, a 5 mm, b 10 mm)"
          % (m["Bh"], m["Bsim"]))
    print("                       cavities per RF wavelength: " +
          ", ".join("%d deg -> %.0f" % (ph, n) for ph, n in m["per_wave"].items()))
    h = test_helix()
    print("helix              ok  vp/c = %.4f, vp = %.3e m/s, synchronous beam %.0f V; 1 kV beam = %.3f c"
          % (h["slow"], h["vp"], h["V0"], h["frac1k"]))
    f = test_friis()
    print("Friis              ok  LNA first NF = %.2f dB, mixer first NF = %.2f dB" % (f["lna"], f["mixer"]))
    print("\nall self-tests passed")


if __name__ == "__main__":
    main()
