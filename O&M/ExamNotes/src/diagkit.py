# -*- coding: utf-8 -*-
"""Generated diagrams for the O&M notes, drawn in the notes' own palette and face.

Used only where no local source (Adhikari, AJ Sir, ioenotes, S.K. Joshi) or credited
web figure has the picture: process flows, org trees, cycles, hubs, pyramids, grids.
A source figure, when one exists, is always cropped instead (figs.py).

Every primitive takes plain data and returns nothing; it saves a PNG into figs/.
Width is in inches: 3.3 fits one \\sbs column, 6.9 the full text width.
"""
import os
import glob
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Wedge, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
DPI = 220

# the preamble's colours
INK, SUB, ACC, ACCL = "#16202A", "#6B7785", "#2563A8", "#D6E4F5"
MKC, MKL, GD, GDL = "#C2410C", "#FDEBD9", "#15803D", "#DCFCE7"
PIN, PINL, RULE, ROW = "#6D28D9", "#EDE4FB", "#DEE3E8", "#F4F7FA"
TONES = [(ACC, ACCL), (GD, GDL), (MKC, MKL), (PIN, PINL), (SUB, ROW)]


def _fonts():
    pats = [os.path.expanduser(r"~\AppData\Local\TectonicProject\Tectonic\cache\bundles\data\*\Lato-%s.ttf" % w)
            for w in ("Regular", "Bold")]
    fam = None
    for p in pats:
        for f in glob.glob(p)[:1]:
            font_manager.fontManager.addfont(f)
            fam = "Lato"
    plt.rcParams["font.family"] = fam or "DejaVu Sans"
    plt.rcParams["font.size"] = 8.5


_fonts()


def _wrap(s, n):
    return "\n".join(textwrap.wrap(s, n, break_long_words=False)) if s else ""


def _box(ax, x, y, w, h, fc, ec, lw=1.0, r=0.06):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=%g" % r,
                                fc=fc, ec=ec, lw=lw, zorder=2))


def _arrow(ax, a, b, color=SUB, lw=1.1, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=9, lw=lw,
                                 color=color, zorder=1,
                                 connectionstyle="arc3,rad=%g" % rad))


def _save(fig, name):
    os.makedirs(FIGS, exist_ok=True)
    fig.savefig(os.path.join(FIGS, name), dpi=DPI, bbox_inches="tight", pad_inches=0.04,
                facecolor="white")
    plt.close(fig)
    print("ok", name)


def _canvas(w_in, h_in, xmax, ymax):
    fig = plt.figure(figsize=(w_in, h_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    return fig, ax


def _label(ax, x, y, head, body, wrap_h, wrap_b, color=INK, fs=8.5, numbered=None):
    t = _wrap(head, wrap_h)
    if numbered is not None:
        t = "%s. %s" % (numbered, t)
    if body:
        ax.text(x, y, t, ha="center", va="bottom", color=color, fontsize=fs,
                fontweight="bold", zorder=3, linespacing=1.1)
        ax.text(x, y - 0.02, _wrap(body, wrap_b), ha="center", va="top", color=INK,
                fontsize=fs - 1.3, zorder=3, linespacing=1.15)
    else:
        ax.text(x, y, t, ha="center", va="center", color=color, fontsize=fs,
                fontweight="bold", zorder=3, linespacing=1.1)


# ---------------------------------------------------------------- flow
def flow(name, steps, width=3.3, horizontal=False, box_h=None, tone=0, numbered=True,
         title=None, loop_back=None, wrap=None):
    """steps: list of (head, body). A chain of rounded boxes joined by arrows.

    loop_back=(i, j, label) draws a return arrow from step i to step j (0-based).
    """
    n = len(steps)
    ec, fc = TONES[tone]
    if horizontal:
        # laid out in real inches so fonts and boxes stay in proportion
        gap = 0.22
        bw = (width - (n - 1) * gap) / n
        cw_h = max(7, int(bw * 72 / (7.8 * 0.6)))       # chars per line, head
        cw_b = max(9, int(bw * 72 / (6.6 * 0.58)))       # chars per line, body
        heads = [_wrap(h, min(wrap or 99, cw_h)) for h, _ in steps]
        bodies = [_wrap(b, cw_b) if b else "" for _, b in steps]
        lh_h, lh_b = 7.8 * 1.18 / 72, 6.6 * 1.2 / 72
        NL = chr(10)
        bh = max(0.19 + (hd.count(NL) + 1) * lh_h + (bd.count(NL) + 1 if bd else 0) * lh_b
                 + 0.1 for hd, bd in zip(heads, bodies))
        top_pad = 0.22 if title else 0.03
        bot_pad = 0.3 if loop_back else 0.03
        W, H = width, bh + top_pad + bot_pad
        fig, ax = _canvas(W, H, W, H)
        y = bot_pad + bh / 2
        for i in range(n):
            x = bw / 2 + i * (bw + gap)
            _box(ax, x, y, bw, bh, fc, ec, r=0.05)
            ax.add_patch(FancyBboxPatch((x - bw / 2, y + bh / 2 - 0.15), bw, 0.15,
                                        boxstyle="round,pad=0,rounding_size=0.05",
                                        fc=ec, ec=ec, lw=1.0, zorder=2))
            ax.text(x, y + bh / 2 - 0.075, str(i + 1) if numbered else "", ha="center",
                    va="center", color="white", fontsize=7.2, fontweight="bold", zorder=3)
            ax.text(x, y + bh / 2 - 0.2, heads[i], ha="center", va="top", color=ec,
                    fontsize=7.8, fontweight="bold", zorder=3, linespacing=1.05)
            if bodies[i]:
                yb = y + bh / 2 - 0.2 - (heads[i].count(NL) + 1) * lh_h - 0.03
                ax.text(x, yb, bodies[i], ha="center", va="top", color=INK, fontsize=6.6,
                        zorder=3, linespacing=1.12)
            if i < n - 1:
                _arrow(ax, (x + bw / 2 + 0.02, y), (x + bw / 2 + gap - 0.02, y))
        if loop_back:
            i, j, lab = loop_back
            xi = bw / 2 + i * (bw + gap)
            xj = bw / 2 + j * (bw + gap)
            yb = y - bh / 2 - 0.02
            ax.add_patch(FancyArrowPatch((xi, yb), (xj, yb), arrowstyle="-|>",
                                         mutation_scale=9, lw=1.0, color=MKC,
                                         connectionstyle="bar,fraction=-0.12", zorder=1))
            ax.text((xi + xj) / 2, 0.06, lab, ha="center", va="center", color=MKC,
                    fontsize=6.8, fontweight="bold")
        if title:
            ax.text(W / 2, H - 0.1, title, ha="center", va="center", color=SUB,
                    fontsize=8, fontweight="bold")
    else:
        bw = 1.0
        bh = box_h or 0.16
        gap = max(0.05, 0.45 * bh)
        H = n * bh + (n - 1) * gap + (0.1 if title else 0.02)
        W = bw + (0.3 if loop_back else 0.04)
        fig, ax = _canvas(width, width * H / W, W, H)
        x = bw / 2 + 0.02
        top = H - (0.1 if title else 0.01)
        for i, (h, b) in enumerate(steps):
            y = top - bh / 2 - i * (bh + gap)
            _box(ax, x, y, bw, bh, fc, ec, r=min(0.06, bh * 0.35))
            ax.add_patch(Circle((x - bw / 2 + 0.09, y), min(0.055, bh * 0.4), fc=ec, ec=ec,
                                zorder=3))
            ax.text(x - bw / 2 + 0.09, y, str(i + 1) if numbered else "", ha="center",
                    va="center", color="white", fontsize=6.8, fontweight="bold", zorder=4)
            tx = x - bw / 2 + 0.18
            if b:
                ax.text(tx, y + 0.012, h, ha="left", va="bottom", color=ec, fontsize=8,
                        fontweight="bold", zorder=3)
                ax.text(tx, y - 0.005, _wrap(b, wrap or 62), ha="left", va="top", color=INK,
                        fontsize=6.9, zorder=3, linespacing=1.12)
            else:
                ax.text(tx, y, h, ha="left", va="center", color=ec, fontsize=8,
                        fontweight="bold", zorder=3)
            if i < n - 1:
                _arrow(ax, (x, y - bh / 2 - 0.005), (x, y - bh / 2 - gap + 0.005))
        if loop_back:
            i, j, lab = loop_back
            yi = top - bh / 2 - i * (bh + gap)
            yj = top - bh / 2 - j * (bh + gap)
            ax.add_patch(FancyArrowPatch((x + bw / 2, yi), (x + bw / 2, yj), arrowstyle="-|>",
                                         mutation_scale=9, lw=1.0, color=MKC,
                                         connectionstyle="bar,fraction=0.18", zorder=1))
            ax.text(x + bw / 2 + 0.18 * abs(yi - yj) + 0.035, (yi + yj) / 2, lab, ha="center",
                    va="center", color=MKC, fontsize=6.6, fontweight="bold", rotation=90)
        if title:
            ax.text(W / 2, H - 0.04, title, ha="center", va="center", color=SUB, fontsize=8,
                    fontweight="bold")
    _save(fig, name)


# ---------------------------------------------------------------- tree
def tree(name, root, width=6.9, box_w=None, box_h=0.36, level_gap=0.3, wrap=18, fs=7.4,
         dashed=()):
    """root = (label, [children...], tone) ; children the same shape. A top-down org chart.

    dashed: labels whose link to their parent is drawn dashed (staff / advisory links).
    """
    def leaves(nd):
        return 1 if not nd[1] else sum(leaves(c) for c in nd[1])

    def depth(nd):
        return 1 + (max(depth(c) for c in nd[1]) if nd[1] else 0)

    L, D = leaves(root), depth(root)
    bw = box_w or 0.92
    W = L * 1.0
    H = D * box_h + (D - 1) * level_gap + 0.04
    fig, ax = _canvas(width, width * H / W, W, H)

    def place(nd, x0, lvl):
        span = leaves(nd)
        x = x0 + span / 2
        y = H - 0.02 - box_h / 2 - lvl * (box_h + level_gap)
        tone = nd[2] if len(nd) > 2 else min(lvl, 4)
        ec, fc = TONES[tone]
        _box(ax, x, y, bw, box_h, fc, ec)
        ax.text(x, y, _wrap(nd[0], wrap), ha="center", va="center", color=INK, fontsize=fs,
                fontweight="bold" if lvl == 0 else "normal", zorder=3, linespacing=1.05)
        cx = x0
        kids = []
        for c in nd[1]:
            kx, ky = place(c, cx, lvl + 1)
            kids.append((kx, ky, c[0]))
            cx += leaves(c)
        if kids:
            ym = y - box_h / 2 - level_gap / 2
            ax.plot([x, x], [y - box_h / 2, ym], color=SUB, lw=0.9, zorder=1)
            ax.plot([kids[0][0], kids[-1][0]], [ym, ym], color=SUB, lw=0.9, zorder=1)
            for kx, ky, lab in kids:
                ax.plot([kx, kx], [ym, ky + box_h / 2], color=SUB, lw=0.9, zorder=1,
                        ls="--" if lab in dashed else "-")
        return x, y

    place(root, 0, 0)
    _save(fig, name)


# ---------------------------------------------------------------- hub
def hub(name, center, spokes, width=3.3, tone=0, wrap=14, ring=1.0, box=(0.62, 0.3), fs=7.2):
    """A centre concept with items round it (functions, features, elements)."""
    import math
    n = len(spokes)
    R = ring
    bw, bh = box
    W = 2 * R + bw + 0.1
    H = 2 * R + bh + 0.1
    fig, ax = _canvas(width, width * H / W, W, H)
    cx, cy = W / 2, H / 2
    ec, fc = TONES[tone]
    ax.add_patch(Circle((cx, cy), 0.36, fc=ec, ec=ec, zorder=3))
    long_word = max(len(w) for w in center.split()) > 11
    ax.text(cx, cy, _wrap(center, 11), ha="center", va="center", color="white",
            fontsize=fs - 0.8 if long_word else fs + 0.6, fontweight="bold", zorder=4,
            linespacing=1.05)
    for i, s in enumerate(spokes):
        a = math.pi / 2 - 2 * math.pi * i / n
        x, y = cx + R * math.cos(a), cy + R * 0.92 * math.sin(a)
        e2, f2 = TONES[(tone + 1 + i) % 4] if False else (ec, fc)
        ax.plot([cx + 0.36 * math.cos(a), x - (bw / 2) * math.cos(a) * 0.9],
                [cy + 0.36 * math.sin(a), y - (bh / 2) * math.sin(a) * 0.9],
                color=SUB, lw=0.9, zorder=1)
        _box(ax, x, y, bw, bh, f2, e2)
        ax.text(x, y, _wrap(s, wrap), ha="center", va="center", color=INK, fontsize=fs,
                zorder=3, linespacing=1.05)
    _save(fig, name)


# ---------------------------------------------------------------- cycle
def cycle(name, items, width=3.3, tone=0, center=None, wrap=13, R=1.0, box=(0.66, 0.3), fs=7.2):
    import math
    n = len(items)
    bw, bh = box
    W = 2 * R + bw + 0.1
    H = 2 * R * 0.9 + bh + 0.1
    fig, ax = _canvas(width, width * H / W, W, H)
    cx, cy = W / 2, H / 2
    ec, fc = TONES[tone]
    pts = []
    for i, s in enumerate(items):
        a = math.pi / 2 - 2 * math.pi * i / n
        pts.append((cx + R * math.cos(a), cy + R * 0.9 * math.sin(a), a))
    for i in range(n):
        x1, y1, a1 = pts[i]
        x2, y2, a2 = pts[(i + 1) % n]
        # shorten the chord so the arrow meets the box edges
        f = 0.3
        _arrow(ax, (x1 + (x2 - x1) * f, y1 + (y2 - y1) * f),
               (x1 + (x2 - x1) * (1 - f), y1 + (y2 - y1) * (1 - f)), color=ec, rad=-0.25)
    for i, (x, y, a) in enumerate(pts):
        _box(ax, x, y, bw, bh, fc, ec)
        ax.text(x, y, _wrap(items[i], wrap), ha="center", va="center", color=INK,
                fontsize=fs, zorder=3, linespacing=1.05)
    if center:
        ax.text(cx, cy, _wrap(center, 12), ha="center", va="center", color=ec,
                fontsize=fs + 1, fontweight="bold")
    _save(fig, name)


# ---------------------------------------------------------------- pyramid
def pyramid(name, levels, width=3.3, notes=None, fs=7.4):
    """levels top->bottom. notes: optional right-hand labels per level."""
    n = len(levels)
    W, H = (2.6 if notes else 1.6), 1.2
    fig, ax = _canvas(width, width * H / W, W, H)
    top_y, base_y, half = H - 0.02, 0.02, 0.78
    for i, lab in enumerate(levels):
        y1 = top_y - (top_y - base_y) * i / n
        y0 = top_y - (top_y - base_y) * (i + 1) / n
        w1 = half * i / n
        w0 = half * (i + 1) / n
        cx = 0.8
        ec, fc = TONES[i % 4]
        ax.add_patch(Polygon([(cx - w0, y0), (cx + w0, y0), (cx + w1, y1), (cx - w1, y1)],
                             closed=True, fc=fc, ec=ec, lw=1.0))
        ax.text(cx, (y0 + y1) / 2 - (0.02 if i == 0 else 0), _wrap(lab, 14 + 4 * i),
                ha="center", va="center", color=INK, fontsize=fs - (0.6 if i == 0 else 0),
                fontweight="bold", linespacing=1.0)
        if notes:
            ax.plot([cx + (w0 + w1) / 2 + 0.03, 1.66], [(y0 + y1) / 2] * 2, color=RULE, lw=0.8)
            ax.text(1.68, (y0 + y1) / 2, _wrap(notes[i], 26), ha="left", va="center",
                    color=INK, fontsize=fs - 1, linespacing=1.05)
    _save(fig, name)


# ---------------------------------------------------------------- grid
def grid(name, rows, cols, cells, width=3.3, row_title=None, col_title=None, tones=None,
         wrap=18, cell_h=0.5, fs=7.2):
    """A labelled matrix (2x2 and similar). cells[r][c] = (head, body)."""
    R, C = len(rows), len(cols)
    lw = 0.55
    W = lw + C * 1.0
    H = 0.3 + R * cell_h + (0.18 if col_title else 0)
    fig, ax = _canvas(width, width * H / W, W, H)
    top = H - (0.18 if col_title else 0)
    if col_title:
        ax.text(lw + C / 2, H - 0.08, col_title, ha="center", va="center", color=SUB,
                fontsize=fs, fontweight="bold")
    for c, cl in enumerate(cols):
        ax.text(lw + c + 0.5, top - 0.15, _wrap(cl, 20), ha="center", va="center", color=ACC,
                fontsize=fs, fontweight="bold")
    for r, rl in enumerate(rows):
        yc = top - 0.3 - cell_h * (r + 0.5)
        ax.text(lw - 0.05, yc, _wrap(rl, 12), ha="right", va="center", color=ACC,
                fontsize=fs, fontweight="bold", linespacing=1.05)
        for c in range(C):
            t = (tones[r][c] if tones else (r + c) % 4)
            ec, fc = TONES[t]
            _box(ax, lw + c + 0.5, yc, 0.96, cell_h - 0.05, fc, ec, r=0.04)
            h, b = cells[r][c]
            if b:
                ax.text(lw + c + 0.5, yc + 0.02, _wrap(h, wrap), ha="center", va="bottom",
                        color=ec, fontsize=fs, fontweight="bold", zorder=3)
                ax.text(lw + c + 0.5, yc - 0.0, _wrap(b, wrap + 6), ha="center", va="top",
                        color=INK, fontsize=fs - 1, zorder=3, linespacing=1.08)
            else:
                ax.text(lw + c + 0.5, yc, _wrap(h, wrap), ha="center", va="center",
                        color=INK, fontsize=fs, zorder=3)
    if row_title:
        ax.text(0.06, top - 0.3 - cell_h * R / 2, row_title, ha="center", va="center",
                color=SUB, fontsize=fs, fontweight="bold", rotation=90)
    _save(fig, name)


# ---------------------------------------------------------------- columns
def columns(name, groups, width=6.9, wrap=22, fs=7.0, head_h=0.26, item_h=0.2):
    """Side-by-side labelled stacks: groups = [(title, [items], tone), ...]."""
    C = len(groups)
    rows = max(len(g[1]) for g in groups)
    W = C * 1.0
    H = head_h + rows * item_h + 0.08
    fig, ax = _canvas(width, width * H / W, W, H)
    for c, g in enumerate(groups):
        title, items = g[0], g[1]
        ec, fc = TONES[g[2] if len(g) > 2 else c % 4]
        x = c + 0.5
        _box(ax, x, H - head_h / 2 - 0.01, 0.94, head_h - 0.03, ec, ec, r=0.04)
        ax.text(x, H - head_h / 2 - 0.01, _wrap(title, wrap), ha="center", va="center",
                color="white", fontsize=fs + 0.4, fontweight="bold", zorder=3)
        for i, it in enumerate(items):
            y = H - head_h - item_h * (i + 0.5) - 0.03
            _box(ax, x, y, 0.94, item_h - 0.035, fc, fc, r=0.03)
            ax.text(x, y, _wrap(it, wrap + 12), ha="center", va="center", color=INK,
                    fontsize=fs, zorder=3, linespacing=1.02)
    _save(fig, name)


# ---------------------------------------------------------------- fishbone
def fishbone(name, effect, causes, width=6.9, fs=6.8):
    """Cause-and-effect (Ishikawa) diagram. causes = [(category, [causes...]), ...], 4 or 6."""
    n = len(causes)
    top = causes[: (n + 1) // 2]
    bot = causes[(n + 1) // 2:]
    cols = max(len(top), len(bot))
    W, H = cols * 1.5 + 1.35, 2.3
    fig, ax = _canvas(width, width * H / W, W, H)
    sy = H / 2
    ax.annotate("", xy=(W - 1.02, sy), xytext=(0.05, sy),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=12))
    _box(ax, W - 0.52, sy, 0.98, 0.62, MKL, MKC, lw=1.2)
    ax.text(W - 0.52, sy, _wrap(effect, 16), ha="center", va="center", color=MKC,
            fontsize=fs + 1, fontweight="bold", zorder=3, linespacing=1.05)
    for row, sign in ((top, 1), (bot, -1)):
        for i, (cat, items) in enumerate(row):
            x_end = 0.4 + i * 1.5 + 1.1
            x0, y0 = x_end - 0.55, sy + sign * 0.95
            ec, fc = TONES[(i + (0 if sign > 0 else 2)) % 4]
            ax.plot([x0, x_end], [y0, sy], color=ec, lw=1.2)
            _box(ax, x0, y0 + sign * 0.1, 0.9, 0.18, ec, ec, r=0.03)
            ax.text(x0, y0 + sign * 0.1, cat, ha="center", va="center", color="white",
                    fontsize=fs, fontweight="bold", zorder=3)
            for k, it in enumerate(items):
                f = (k + 1) / (len(items) + 1)
                bx = x0 + (x_end - x0) * f
                by = y0 + (sy - y0) * f
                ax.plot([bx - 0.12, bx], [by, by], color=ec, lw=0.8)
                ax.text(bx - 0.14, by, it, ha="right", va="center", color=INK, fontsize=fs - 0.6)
    _save(fig, name)


# ---------------------------------------------------------------- gantt
def gantt(name, tasks, periods, width=6.9, fs=7.0, label_w=2.2):
    """tasks = [(label, start, end, tone)], start/end in period units (0-based, end exclusive)."""
    P = len(periods)
    rows = len(tasks)
    W = label_w + P
    H = 0.3 + rows * 0.26
    fig, ax = _canvas(width, width * H / W, W, H)
    for p, lab in enumerate(periods):
        ax.text(label_w + p + 0.5, H - 0.13, lab, ha="center", va="center", color=ACC,
                fontsize=fs, fontweight="bold")
        ax.plot([label_w + p, label_w + p], [0, H - 0.26], color=RULE, lw=0.6, zorder=0)
    for r, (lab, s, e, t) in enumerate(tasks):
        y = H - 0.3 - 0.26 * (r + 0.5)
        if r % 2 == 0:
            ax.add_patch(plt.Rectangle((0, y - 0.13), W, 0.26, fc=ROW, ec="none", zorder=0))
        ax.text(0.05, y, lab, ha="left", va="center", color=INK, fontsize=fs)
        ec, fc = TONES[t]
        _box(ax, label_w + (s + e) / 2, y, e - s - 0.08, 0.16, fc, ec, r=0.04)
    _save(fig, name)


# ---------------------------------------------------------------- chart
def chart(name, labels, values, width=3.3, kind="bar", ylabel="", highlight=(), note=None,
          fmt="%g", ylim=None, height=None, marks=None):
    """A plain single-series chart with values printed on the marks.

    marks: optional {index: text} annotations placed above a point (events)."""
    fig, ax = plt.subplots(figsize=(width, height or width * 0.58))
    x = range(len(labels))
    cols = [MKC if i in highlight else ACC for i in x]
    if kind == "bar":
        ax.bar(x, values, color=cols, width=0.62, zorder=2)
        for i, v in zip(x, values):
            ax.text(i, v, fmt % v, ha="center", va="bottom", fontsize=6.6, color=INK)
    else:
        ax.plot(list(x), values, color=ACC, lw=1.6, marker="o", ms=3.5, zorder=2)
        for i, v in zip(x, values):
            ax.text(i, v + (max(values) * 0.025), fmt % v, ha="center", va="bottom",
                    fontsize=6.4, color=MKC if i in highlight else INK)
    if marks:
        for i, t in marks.items():
            ax.axvline(i, color=MKC, lw=0.8, ls="--", zorder=1)
            ax.text(i + 0.1, (ylim or (0, max(values) * 1.15))[1] * 0.06, t, fontsize=6.2,
                    color=MKC, va="bottom", ha="left")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=6.4, rotation=0)
    ax.tick_params(axis="y", labelsize=6.4, colors=SUB)
    ax.tick_params(axis="x", colors=INK, length=0)
    ax.set_ylabel(ylabel, fontsize=7, color=SUB)
    ax.set_ylim(*(ylim or (0, max(values) * 1.15)))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(RULE)
    ax.grid(axis="y", color=RULE, lw=0.5, zorder=0)
    if note:
        fig.text(0.01, -0.02, note, fontsize=5.8, color=SUB, ha="left", va="top")
    _save(fig, name)
