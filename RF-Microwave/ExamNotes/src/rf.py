# -*- coding: utf-8 -*-
"""Transmission-line and stub-matching solver for the RF exam notes.

Everything is exact and numerical: no chart reading, no closed-form
formula quoted from memory. The Smith chart is a nomogram for these
same equations, so the numbers here are what a perfectly drawn chart
would give -- which is how the solved problems in ch2-num.tex are
checked against the readings printed in the lecture decks.

Conventions (the ones the IOE papers and KK Sir's notes use):
  * normalised impedance  z = Z/Z0,  admittance  y = Y/Y0 = 1/z
  * Gamma(d) = Gamma_L * exp(-j*2*beta*d)   moving TOWARD THE GENERATOR
  * distances are in wavelengths; the chart's WTG scale is
    wtg(Gamma) = angle measured clockwise from the open-circuit point
    (Gamma = +1), divided by 4*pi, so one full turn is 0.5 lambda.
"""
import cmath
import math

TWO_PI = 2.0 * math.pi


# --------------------------------------------------------------- basics
def gamma_of(z):
    """Reflection coefficient of a normalised impedance."""
    return (z - 1.0) / (z + 1.0)


def z_of(gamma):
    """Normalised impedance of a reflection coefficient."""
    return (1.0 + gamma) / (1.0 - gamma)


def y_of(gamma):
    """Normalised admittance of a reflection coefficient.

    Note the sign: y = 1/z means Gamma_y = -Gamma_z, which is the half
    turn of the chart that the admittance overlay performs for you.
    """
    return (1.0 - gamma) / (1.0 + gamma)


def move(gamma, d):
    """Rotate d wavelengths toward the generator (clockwise)."""
    return gamma * cmath.exp(-1j * 2.0 * TWO_PI * d)


def vswr(gamma):
    g = abs(gamma)
    return float("inf") if g >= 1.0 - 1e-12 else (1.0 + g) / (1.0 - g)


def wtg(gamma):
    """Wavelengths-toward-generator scale reading, in [0, 0.5)."""
    ang = cmath.phase(gamma)
    return ((-ang) / (2.0 * TWO_PI)) % 0.5


def z_in(zl, d):
    """Normalised input impedance d wavelengths back from load zl."""
    return z_of(move(gamma_of(zl), d))


# ------------------------------------------------------------ stub length
def stub_length(b, kind):
    """Length in wavelengths of a stub presenting normalised susceptance b.

    open  stub:  y = +j tan(beta l)
    short stub:  y = -j cot(beta l)
    """
    if kind == "open":
        l = math.atan(b) / TWO_PI
    elif kind == "short":
        l = math.atan2(-1.0, b) / TWO_PI if b != 0 else 0.25
    else:
        raise ValueError("kind must be 'open' or 'short'")
    return l % 0.5


def stub_susceptance(l, kind):
    """Inverse of stub_length -- used to check a length back."""
    if kind == "open":
        return math.tan(TWO_PI * l)
    return -1.0 / math.tan(TWO_PI * l)


# ---------------------------------------------------------- single stub
def single_stub(zl, kind="short", series=False):
    """Shunt (or series) single-stub tuner. Returns both solutions.

    Shunt: walk toward the generator until Re(y) = 1, then cancel the
    residual susceptance with the stub.
    Series: walk until Re(z) = 1 and cancel the residual reactance.
    """
    gl = gamma_of(zl)
    r = abs(gl)
    if r < 1e-12:
        return []                       # already matched

    # Re(y) = 1 on the g = 1 circle, |Gamma - (-1/2)| = 1/2 -- and by the
    # z/y duality Re(z) = 1 is the same circle mirrored about the origin.
    # Intersect it with the constant-|Gamma| circle of this load.
    #   |Gamma| = r  and  |Gamma - c| = 1/2  with c = -1/2 (y) or +1/2 (z)
    # => cos(theta - phase(c)) = r   (after expanding, for |c| = 1/2)
    if r > 1.0 - 1e-12:
        return []
    base = 0.0 if series else math.pi   # phase of the circle centre
    da = math.acos(r)

    out = []
    for sgn in (+1, -1):
        theta = base + sgn * da         # target angle of Gamma
        d = ((cmath.phase(gl) - theta) / (2.0 * TWO_PI)) % 0.5
        g = move(gl, d)
        if series:
            # a SERIES stub is specified by its reactance, not susceptance:
            #   open stub  z = -j cot(beta l);  short stub  z = +j tan(beta l)
            zd = z_of(g)
            x = zd.imag                 # stub must present -x
            l = (math.atan2(1.0, x) / TWO_PI) % 0.5 if kind == "open" \
                else (math.atan(-x) / TWO_PI) % 0.5
            out.append({"d": d, "l": l, "y_or_z": zd, "cancel": -x})
        else:
            yd = y_of(g)
            b = yd.imag                 # stub must present -b
            out.append({"d": d, "l": stub_length(-b, kind), "y_or_z": yd,
                        "cancel": -b})
    out.sort(key=lambda s: s["d"])
    return out


# ---------------------------------------------------------- double stub
def double_stub(zl, spacing=0.125, kind="short", d1=0.0):
    """Double-stub shunt tuner, stubs `spacing` wavelengths apart.

    d1 is the distance from the load to the FIRST stub (0 = at the load).
    Returns both solutions, or [] when the load falls in the forbidden
    region (g > 1/sin^2(beta*spacing) after walking d1).
    """
    y1 = y_of(move(gamma_of(zl), d1))   # admittance seen just before stub 1
    g1, bl = y1.real, y1.imag
    t = math.tan(TWO_PI * spacing)

    # Stub 1 only moves the point along its own g = g1 circle, to y_a =
    # g1 + jB. The spacing of line then transforms it as
    #     y2 = (y_a + jt) / (1 + j t y_a),
    # and expanding Re(y2) = 1 gives
    #     Re(y2) = g1 (1 + t^2) / [ (1 - tB)^2 + t^2 g1^2 ] = 1
    #  => (1 - tB)^2 = g1 (1 + t^2) - g1^2 t^2 = disc
    #  => B = ( 1 -/+ sqrt(disc) ) / t
    # Graphically that is the intersection of the g = g1 circle with the
    # g = 1 circle rotated `spacing` toward the LOAD (the spacing circle).
    disc = g1 * (1.0 + t * t) - g1 * g1 * t * t
    if disc < 0:
        # g1 > 1/sin^2(beta*spacing): the forbidden region of this tuner
        return []

    out = []
    for sgn in (+1, -1):
        B = (1.0 + sgn * math.sqrt(disc)) / t
        b1 = B - bl                             # susceptance stub 1 adds
        ya = complex(g1, B)                     # on the spacing circle
        y2 = y_of(move(gamma_of(1.0 / ya), spacing))   # back onto g = 1
        b2 = -y2.imag                           # stub 2 cancels it
        out.append({"b1": b1, "l1": stub_length(b1, kind),
                    "y1": y1, "ya": ya, "y2": y2,
                    "b2": b2, "l2": stub_length(b2, kind),
                    "d1": d1, "spacing": spacing, "kind": kind,
                    "swr1": vswr(gamma_of(1.0 / ya))})
    return out


# ------------------------------------------------------------ microstrip
def microstrip(z0, er, h_mm):
    """Hammerstad synthesis: strip width w and guide wavelength factor.

    Returns (w_mm, eps_eff, w_over_h).
    """
    a = z0 / 60.0 * math.sqrt((er + 1.0) / 2.0) \
        + (er - 1.0) / (er + 1.0) * (0.23 + 0.11 / er)
    b = 377.0 * math.pi / (2.0 * z0 * math.sqrt(er))
    woh = 8.0 * math.exp(a) / (math.exp(2.0 * a) - 2.0)
    if woh > 2.0:
        woh = 2.0 / math.pi * (b - 1.0 - math.log(2.0 * b - 1.0)
                               + (er - 1.0) / (2.0 * er)
                               * (math.log(b - 1.0) + 0.39 - 0.61 / er))
    eeff = (er + 1.0) / 2.0 + (er - 1.0) / 2.0 / math.sqrt(1.0 + 12.0 / woh)
    return woh * h_mm, eeff, woh


def guide_wavelength_mm(f_hz, eeff):
    return 299.792458e6 / f_hz / math.sqrt(eeff) * 1000.0


# ------------------------------------------------------------------ self-test
if __name__ == "__main__":
    def close(a, b, tol=0.012):
        return abs(a - b) <= tol

    print("=== single stub, Pozar 5.2 / Gangaju P1: zL = 0.3+j0.2, open ===")
    for s in single_stub(0.3 + 0.2j, "open"):
        print("   d=%.4f l=%.4f  y=%.3f%+.3fj" %
              (s["d"], s["l"], s["y_or_z"].real, s["y_or_z"].imag))
    print("   deck: d1=0.045 l1=0.146 | d2=0.386 l2=0.354")

    print("=== single stub, Gangaju P2: ZL=100+j50 on 50 ohm, short ===")
    for s in single_stub((100 + 50j) / 50.0, "short"):
        print("   d=%.4f l=%.4f" % (s["d"], s["l"]))
    print("   deck: d1=0.199 l1=0.125 | d2=0.376 l2=0.375")

    print("=== double stub P1: ZL=60-j80 on 50, open, lambda/8, d1=0 ===")
    for s in double_stub((60 - 80j) / 50.0, 0.125, "open", 0.0):
        print("   ya=%.3f%+.3fj b1=%+.3f l1=%.4f | y2=%.3f%+.3fj b2=%+.3f l2=%.4f"
              % (s["ya"].real, s["ya"].imag, s["b1"], s["l1"],
                 s["y2"].real, s["y2"].imag, s["b2"], s["l2"]))
    print("   deck: b1=+1.3 l1=0.146 b2=+3.3 l2=0.232 | b1=-0.11 l1=0.482 b2=-1.3 l2=0.354")

    print("=== double stub P2: ZL=100+j100 on 50, short, 3lambda/8, d1=0.4 ===")
    for s in double_stub((100 + 100j) / 50.0, 0.375, "short", 0.4):
        print("   y1=%.3f%+.3fj b1=%+.3f l1=%.4f | y2=%.3f%+.3fj b2=%+.3f l2=%.4f"
              % (s["y1"].real, s["y1"].imag, s["b1"], s["l1"],
                 s["y2"].real, s["y2"].imag, s["b2"], s["l2"]))
    print("   deck: y1'=0.55-j1.08 b1=+0.97 l1=0.373 b2=+0.61 l2=0.337")
    print("         b1'=-0.8 l1'=0.143 b2'=-2.5 l2'=0.061")
