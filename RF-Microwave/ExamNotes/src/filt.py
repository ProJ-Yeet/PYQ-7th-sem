# -*- coding: utf-8 -*-
"""Chapter 6 filter solver and microstrip layout drawer, self-testing.

Every filter number and layout in ch6.tex and ch6-num-body.tex comes from here:

  * Butterworth and Chebyshev low-pass prototype values g_k from their closed
    forms, checked against the deck's N = 6 list and Pozar's printed
    0.5 dB and 3 dB equal-ripple tables;
  * order selection from the insertion-loss formula, checked against the
    deck's stepped-impedance example (and it shows N = 5 already clears 20 dB);
  * impedance / frequency scaling and the LPF -> HPF / BPF transformations,
    checked by evaluating the scaled ladder's |S21| at cut-off (-3 dB for
    Butterworth) by ABCD multiplication;
  * stepped-impedance microstrip realisation (beta l = g R0 / Zh, g Zl / R0),
    checked against the deck's section table (11.8, 33.8, 44.3, 46.1,
    32.4, 12.3 degrees; W = 11.3 / 0.428 mm);
  * to-scale layout drawings of the microstrip filters the papers ask for,
    generated from those computed dimensions.

Run from src\\:   python filt.py
"""
import cmath
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import rf

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
C0 = 3.0e8
SUB = "#6B7785"
ACC = "#2563A8"
MKC = "#C2410C"
GD = "#15803D"
CU = "#D97706"


def _close(a, b, tol=1e-3, what=""):
    if abs(a - b) > tol * max(1.0, abs(b)):
        raise AssertionError("%s: got %r, expected %r" % (what, a, b))


# ============================================================ prototypes
def butterworth(N):
    return [2 * math.sin((2 * k - 1) * math.pi / (2 * N)) for k in range(1, N + 1)] + [1.0]


def chebyshev(N, ripple_db):
    beta = math.log(1 / math.tanh(ripple_db / 17.37))
    gam = math.sinh(beta / (2 * N))
    a = [math.sin((2 * k - 1) * math.pi / (2 * N)) for k in range(1, N + 1)]
    b = [gam ** 2 + math.sin(k * math.pi / N) ** 2 for k in range(1, N + 1)]
    g = [2 * a[0] / gam]
    for k in range(2, N + 1):
        g.append(4 * a[k - 2] * a[k - 1] / (b[k - 2] * g[k - 2]))
    g.append(1.0 if N % 2 else 1 / math.tanh(beta / 4) ** 2)
    return g


def il_butter_db(w_over_wc, N):
    return 10 * math.log10(1 + w_over_wc ** (2 * N))


def order_butter(w_over_wc, atten_db):
    N = 1
    while il_butter_db(w_over_wc, N) < atten_db:
        N += 1
    return N


# ============================================================ ladder analysis
def abcd_series(Z):
    return [[1, Z], [0, 1]]


def abcd_shunt(Y):
    return [[1, 0], [Y, 1]]


def mul(A, B):
    return [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]]


def s21_db(elements, f, R0=50.0):
    """elements: list of ('sL'|'sC'|'pL'|'pC'|'sLC'|'pLC', value(s)) in ohm / henry / farad."""
    w = 2 * math.pi * f
    M = [[1, 0], [0, 1]]
    for kind, v in elements:
        if kind == "sL":
            M = mul(M, abcd_series(1j * w * v))
        elif kind == "sC":
            M = mul(M, abcd_series(1 / (1j * w * v)))
        elif kind == "pL":
            M = mul(M, abcd_shunt(1 / (1j * w * v)))
        elif kind == "pC":
            M = mul(M, abcd_shunt(1j * w * v))
        elif kind == "sLC":
            L, C = v
            M = mul(M, abcd_series(1j * w * L + 1 / (1j * w * C)))
        elif kind == "pLC":
            L, C = v
            M = mul(M, abcd_shunt(1j * w * C + 1 / (1j * w * L)))
    A, B, Cc, D = M[0][0], M[0][1], M[1][0], M[1][1]
    s21 = 2 / (A + B / R0 + Cc * R0 + D)
    return 20 * math.log10(abs(s21))


def lpf_elements(g, R0, fc, first="C"):
    wc = 2 * math.pi * fc
    out = []
    shunt = first == "C"
    for gk in g[:-1]:
        if shunt:
            out.append(("pC", gk / (R0 * wc)))
        else:
            out.append(("sL", R0 * gk / wc))
        shunt = not shunt
    return out


def hpf_elements(g, R0, fc, first="C"):
    """LPF prototype -> HPF: series L -> series C = 1/(R0 wc g); shunt C -> shunt L = R0/(wc g)."""
    wc = 2 * math.pi * fc
    out = []
    shunt = first == "C"
    for gk in g[:-1]:
        if shunt:
            out.append(("pL", R0 / (wc * gk)))
        else:
            out.append(("sC", 1 / (R0 * wc * gk)))
        shunt = not shunt
    return out


def bpf_elements(g, R0, f1, f2, first="L"):
    w0 = 2 * math.pi * math.sqrt(f1 * f2)
    Dl = (f2 - f1) / math.sqrt(f1 * f2)
    out = []
    series = first == "L"
    for gk in g[:-1]:
        if series:
            out.append(("sLC", (R0 * gk / (w0 * Dl), Dl / (w0 * gk * R0))))
        else:
            out.append(("pLC", (Dl * R0 / (w0 * gk), gk / (w0 * Dl * R0))))
        series = not series
    return out, w0 / (2 * math.pi), Dl


# ============================================================ stepped impedance
def stepped(g, R0=50.0, Zh=120.0, Zl=20.0, fc=2.5e9, er=4.2, h=1.58, first="C"):
    rows = []
    shunt = first == "C"
    for i, gk in enumerate(g[:-1], 1):
        if shunt:
            Z, bl = Zl, gk * Zl / R0
        else:
            Z, bl = Zh, gk * R0 / Zh
        w, eeff, _ = rf.microstrip(Z, er, h)
        lam_g = rf.guide_wavelength_mm(fc, eeff)
        rows.append(dict(sec=i, Z=Z, g=gk, bl_deg=math.degrees(bl), W=w,
                         l=math.degrees(bl) / 360.0 * lam_g, kind="C" if shunt else "L"))
        shunt = not shunt
    return rows


def open_stub_lpf(g, R0=50.0, fc=2.5e9, er=4.2, h=1.58, Zh=120.0):
    """Shunt-arm realisation: each shunt C -> open stub, lambda/8 at fc, Z = R0/g
    (Richards); each series L -> short high-Z line, beta l = g R0/Zh."""
    rows = []
    shunt = True
    for i, gk in enumerate(g[:-1], 1):
        if shunt:
            Z = R0 / gk
            w, eeff, _ = rf.microstrip(Z, er, h)
            l = rf.guide_wavelength_mm(fc, eeff) / 8
            rows.append(dict(sec=i, kind="stub", Z=Z, W=w, l=l, bl_deg=45.0, g=gk))
        else:
            bl = gk * R0 / Zh
            w, eeff, _ = rf.microstrip(Zh, er, h)
            rows.append(dict(sec=i, kind="line", Z=Zh, W=w, g=gk, bl_deg=math.degrees(bl),
                             l=math.degrees(bl) / 360 * rf.guide_wavelength_mm(fc, eeff)))
        shunt = not shunt
    return rows


# ============================================================ drawing
def _feed(ax, x, y0, W50, L=4.0):
    ax.add_patch(Rectangle((x, y0 - W50 / 2), L, W50, fc=CU, ec="black", lw=0.6))
    return x + L


def draw_stepped(rows, name, title, W50):
    fig, ax = plt.subplots(figsize=(6.4, 2.4), dpi=200)
    x = _feed(ax, 0, 0, W50)
    ax.text(2, -W50 / 2 - 0.6, "50 $\\Omega$", ha="center", va="top", fontsize=7, color=SUB)
    for r in rows:
        w = max(r["W"], 0.35)
        ax.add_patch(Rectangle((x, -w / 2), r["l"], w, fc=CU if r["kind"] == "C" else "#FCD34D",
                               ec="black", lw=0.6))
        lab = ("%s%d\n%.0f $\\Omega$\nl=%.2f\nW=%.2f" % ("C" if r["kind"] == "C" else "L",
               r["sec"], r["Z"], r["l"], r["W"]))
        if r["kind"] == "C":
            ax.text(x + r["l"] / 2, -max(r["W"], 1.5) / 2 - 0.6, lab, ha="center", va="top", fontsize=6, color=ACC)
        else:
            ax.text(x + r["l"] / 2, max(W50, 1.5) / 2 + 0.6, lab, ha="center", va="bottom", fontsize=6, color=MKC)
        x += r["l"]
    _feed(ax, x, 0, W50)
    ax.text(x + 2, -W50 / 2 - 0.6, "50 $\\Omega$", ha="center", va="top", fontsize=7, color=SUB)
    ax.set_xlim(-1, x + 5)
    top = max(max(r["W"] for r in rows) / 2 + 1.5, 3)
    ax.set_ylim(-top - 7, top + 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8, color=SUB)
    fig.savefig(os.path.join(FIGS, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def draw_stub_lpf(rows, name, title, W50):
    fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=200)
    x = _feed(ax, 0, 0, W50)
    for i, r in enumerate(rows):
        if r["kind"] == "stub":
            stubW = max(r["W"], 0.35)
            L0 = 2.5
            ax.add_patch(Rectangle((x, -W50 / 2), L0, W50, fc=CU, ec="black", lw=0.6))
            sign = 1
            y = W50 / 2 if sign > 0 else -W50 / 2 - r["l"]
            ax.add_patch(Rectangle((x + L0 / 2 - stubW / 2, y), stubW, r["l"], fc=CU, ec="black", lw=0.6))
            ty = W50 / 2 + r["l"] + 0.4 if sign > 0 else -W50 / 2 - r["l"] - 0.4
            ax.text(x + L0 / 2 + stubW / 2 + 0.3, ty, "open stub C%d\n%.0f $\\Omega$, $\\lambda/8$\nl=%.2f W=%.2f"
                    % (r["sec"], r["Z"], r["l"], r["W"]), fontsize=6, color=ACC,
                    va="bottom" if sign > 0 else "top")
            x += L0
        else:
            w = max(r["W"], 0.35)
            ax.add_patch(Rectangle((x, -w / 2), r["l"], w, fc="#FCD34D", ec="black", lw=0.6))
            ax.text(x + r["l"] / 2, -W50 / 2 - 0.8, "L%d  %.0f $\\Omega$\nl=%.2f\nW=%.2f" % (r["sec"], r["Z"], r["l"], r["W"]),
                    ha="center", va="top", fontsize=6, color=MKC)
            x += r["l"]
    _feed(ax, x, 0, W50)
    L = max(r["l"] for r in rows if r["kind"] == "stub")
    ax.set_xlim(-1, x + 5)
    ax.set_ylim(-L - 6, L + 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8, color=SUB)
    fig.savefig(os.path.join(FIGS, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def draw_hpf(sections, name, title, W50):
    """sections: list of ('gap', C_pF) or ('short', L_nH, stub l mm, W mm)."""
    fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=200)
    x = _feed(ax, 0, 0, W50)
    for s in sections:
        if s[0] == "gap":
            ax.plot([x + 0.4, x + 0.4], [-W50, W50], color="white", lw=0)
            ax.text(x + 0.5, W50 / 2 + 0.5, "gap\n$C$=%.2f pF" % s[1], ha="center", fontsize=6, color=ACC)
            x += 1.0
            ax.add_patch(Rectangle((x, -W50 / 2), 3.0, W50, fc=CU, ec="black", lw=0.6))
            x += 3.0
        else:
            _, LnH, l, w = s
            ax.add_patch(Rectangle((x, -W50 / 2), 3.0, W50, fc=CU, ec="black", lw=0.6))
            ww = max(w, 0.35)
            ax.add_patch(Rectangle((x + 1.5 - ww / 2, -W50 / 2 - l), ww, l, fc="#FCD34D", ec="black", lw=0.6))
            ax.add_patch(plt.Circle((x + 1.5, -W50 / 2 - l - 0.4), 0.45, fc="black"))
            ax.text(x + 1.5 + 0.9, -W50 / 2 - l, "shorted stub (via)\n$L$=%.2f nH\nl=%.2f W=%.2f" % (LnH, l, w),
                    fontsize=6, color=MKC, va="bottom")
            x += 3.0
    ax.add_patch(Rectangle((x, -W50 / 2), 0.01, W50, fc=CU, ec=CU, lw=0))
    _feed(ax, x, 0, W50)
    ax.set_xlim(-1, x + 5)
    ax.set_ylim(-14, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8, color=SUB)
    fig.savefig(os.path.join(FIGS, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def draw_bpf(lres, gap_txt, name, title, W50):
    fig, ax = plt.subplots(figsize=(6.4, 1.8), dpi=200)
    x = _feed(ax, 0, 0, W50, L=6)
    x += 0.5
    ax.text(x - 0.25, W50 / 2 + 0.5, "gap", ha="center", fontsize=6, color=ACC)
    ax.add_patch(Rectangle((x, -W50 / 2), lres, W50, fc="#FCD34D", ec="black", lw=0.6))
    ax.text(x + lres / 2, -W50 / 2 - 0.6, "half-wave resonator  l = $\\lambda_g/2$ = %.1f mm at $f_0$" % lres,
            ha="center", va="top", fontsize=6, color=MKC)
    x += lres + 0.5
    ax.text(x - 0.25, W50 / 2 + 0.5, "gap", ha="center", fontsize=6, color=ACC)
    _feed(ax, x, 0, W50, L=6)
    ax.set_xlim(-1, x + 7)
    ax.set_ylim(-4, 3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title + "  " + gap_txt, fontsize=8, color=SUB)
    fig.savefig(os.path.join(FIGS, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ============================================================ tests
def test_prototypes():
    g6 = butterworth(6)
    for got, exp in zip(g6, [0.517, 1.414, 1.932, 1.932, 1.414, 0.517, 1.0]):
        _close(got, exp, tol=2e-3, what="Butterworth N=6")
    for got, exp in zip(chebyshev(3, 0.5), [1.5963, 1.0967, 1.5963, 1.0]):
        _close(got, exp, tol=1e-3, what="Chebyshev 0.5 dB N=3")
    for got, exp in zip(chebyshev(3, 3.0), [3.3487, 0.7117, 3.3487, 1.0]):
        _close(got, exp, tol=1e-3, what="Chebyshev 3 dB N=3")
    for got, exp in zip(chebyshev(4, 0.5), [1.6703, 1.1926, 2.3661, 0.8419, 1.9841]):
        _close(got, exp, tol=1e-3, what="Chebyshev 0.5 dB N=4")
    return dict(b3=butterworth(3), b5=butterworth(5), c3=chebyshev(3, 0.5), c5=chebyshev(5, 0.5))


def test_order():
    r = 4.0 / 2.5
    n = order_butter(r, 20)
    il5, il6 = il_butter_db(r, 5), il_butter_db(r, 6)
    assert n == 5 and il5 > 20 and il6 > il5
    return dict(n=n, il5=il5, il6=il6)


def test_scaled_responses():
    R0, fc = 50.0, 2.5e9
    out = {}
    for N in (3, 5):
        g = butterworth(N)
        e = lpf_elements(g, R0, fc)
        _close(s21_db(e, fc), -3.0103, tol=1e-3, what="LPF -3 dB N=%d" % N)
        assert s21_db(e, fc / 10) > -0.01 and s21_db(e, 4e9) < -9
        h = hpf_elements(g, R0, fc)
        _close(s21_db(h, fc), -3.0103, tol=1e-3, what="HPF -3 dB N=%d" % N)
        assert s21_db(h, fc * 10) > -0.01 and s21_db(h, fc / 1.6) < -9
        out[N] = dict(lpf=e, hpf=h)
    b, f0, Dl = bpf_elements(butterworth(3), R0, 2.0e9, 2.5e9)
    _close(s21_db(b, 2.0e9), -3.0103, tol=1e-3, what="BPF lower edge")
    _close(s21_db(b, 2.5e9), -3.0103, tol=1e-3, what="BPF upper edge")
    assert s21_db(b, f0) > -1e-6
    out["bpf"] = dict(el=b, f0=f0, D=Dl)
    # Chebyshev 0.5 dB N=3: exactly -ripple at cut-off
    e = lpf_elements(chebyshev(3, 0.5), R0, fc)
    _close(s21_db(e, fc), -0.5, tol=2e-3, what="Chebyshev ripple edge")
    return out


def test_stepped():
    rows = stepped(butterworth(6))
    exp_deg = [11.8, 33.8, 44.3, 46.1, 32.4, 12.3]
    for r, d in zip(rows, exp_deg):
        assert abs(r["bl_deg"] - d) < 0.1, (r, d)
    for r in rows:
        assert abs(r["W"] - (11.3 if r["Z"] == 20 else 0.428)) < 0.15, r
    exp_l = [2.05, 6.63, 7.69, 9.04, 5.63, 2.41]
    for r, l in zip(rows, exp_l):
        assert abs(r["l"] - l) < 0.12, (r, l)
    return rows


def make_figures():
    os.makedirs(FIGS, exist_ok=True)
    W50, eeff50, _ = rf.microstrip(50, 4.2, 1.58)
    b3, b5 = butterworth(3), butterworth(5)
    pi3 = stepped(b3, first="C")
    t5 = stepped(b5, first="L")
    pi5 = stepped(b5, first="C")
    draw_stepped(pi3, "c6_lay_pi3.png", "$\\pi$-section LPF (C-L-C), N = 3 (mm)", W50)
    draw_stepped(pi5, "c6_lay_pi5.png", "Double $\\pi$-section LPF (C-L-C-L-C), N = 5 (dimensions in mm)", W50)
    draw_stepped(t5, "c6_lay_t5.png", "Double-pad T-type LPF (L-C-L-C-L), N = 5: two low-Z pads (mm)", W50)
    stub4 = open_stub_lpf(butterworth(4))
    draw_stub_lpf(stub4, "c6_lay_stub.png", "Shunt-arm LPF: open stubs for shunt C, high-Z lines for series L, N = 4 (mm)", W50)
    wc = 2 * math.pi * 2.5e9
    g = b3
    # HPF pi (L-C-L) from the C-L-C prototype: shunt L = R0/(wc g), series C = 1/(R0 wc g)
    Lsh = 50 / (wc * g[0])
    Cse = 1 / (50 * wc * g[1])
    Zs = 100.0
    ws, eeffs, _ = rf.microstrip(Zs, 4.2, 1.58)
    lam = rf.guide_wavelength_mm(2.5e9, eeffs)
    ls = math.atan(wc * Lsh / Zs) / (2 * math.pi) * lam
    draw_hpf([("short", Lsh * 1e9, ls, ws), ("gap", Cse * 1e12), ("short", Lsh * 1e9, ls, ws)],
             "c6_lay_hpf.png", "HPF $\\pi$-section (shunt L - series C - shunt L), N = 3, $f_c$ = 2.5 GHz (mm)", W50)
    lam50 = rf.guide_wavelength_mm(2.25e9, eeff50)
    draw_bpf(lam50 / 2, "", "c6_lay_bpf.png",
             "Single-section series-arm BPF: gap-coupled half-wave resonator, $f_0$ = 2.25 GHz", W50)
    return dict(W50=W50, pi3=pi3, pi5=pi5, t5=t5, stub4=stub4, Lsh=Lsh, Cse=Cse, ls=ls, ws=ws, lres=lam50 / 2)


def main():
    p = test_prototypes()
    print("prototypes         ok  Butterworth N=3 %s; N=5 %s" % (["%.4f" % x for x in p["b3"]], ["%.4f" % x for x in p["b5"]]))
    print("                       Chebyshev 0.5 dB N=3 %s; N=5 %s" % (["%.4f" % x for x in p["c3"]], ["%.4f" % x for x in p["c5"]]))
    o = test_order()
    print("order selection    ok  4.0/2.5 GHz, 20 dB: N=%d (IL %.2f dB); deck/Pozar chart N=6 gives %.2f dB" % (o["n"], o["il5"], o["il6"]))
    s = test_scaled_responses()
    for N in (3, 5):
        print("scaled N=%d         ok  LPF %s" % (N, ", ".join("%s %.3g" % (k, v) for k, v in s[N]["lpf"])))
        print("                       HPF %s" % ", ".join("%s %.3g" % (k, v) for k, v in s[N]["hpf"]))
    print("BPF 2.0-2.5 GHz    ok  f0 %.4g GHz, Delta %.4f, %s" % (s["bpf"]["f0"] / 1e9, s["bpf"]["D"], s["bpf"]["el"]))
    rows = test_stepped()
    print("deck stepped table ok  " + "; ".join("%d:%.0f ohm %.1f deg W %.3f l %.2f" % (r["sec"], r["Z"], r["bl_deg"], r["W"], r["l"]) for r in rows))
    f = make_figures()
    print("layouts            ok  W50 %.2f mm" % f["W50"])
    for key in ("pi3", "pi5", "t5", "stub4"):
        print("   %-5s " % key + "; ".join("%s%d %.0f ohm %.1f deg W %.2f l %.2f" % (r.get("kind", "?"), r["sec"], r["Z"], r["bl_deg"], r["W"], r["l"]) for r in f[key]))
    print("   hpf   shunt L %.3f nH -> 100 ohm shorted stub l %.2f mm W %.2f; series C %.3f pF" % (f["Lsh"] * 1e9, f["ls"], f["ws"], f["Cse"] * 1e12))
    print("   bpf   half-wave resonator %.2f mm" % f["lres"])
    print("\nall self-tests passed")


if __name__ == "__main__":
    main()
