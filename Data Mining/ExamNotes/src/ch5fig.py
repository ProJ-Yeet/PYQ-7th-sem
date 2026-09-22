# -*- coding: utf-8 -*-
"""Draw the step-by-step solution under every chapter-5 numerical in ch5-num.tex.

K-means: one scatter per iteration, points coloured by the cluster they are
assigned to, each centroid drawn where it was (hollow) and where the update
moves it (filled, with an arrow). Agglomerative clustering: the distance
matrix after every merge, its smallest entry lit, the merged row recomputed
by MIN or MAX. DBSCAN: epsilon circles, then the point types, then the
clusters. Every panel carries a TECHNIQUE chip; the decisive step is framed
KEY STEP; a technique index opens the chapter.

Exit test is replay. K-means is rerun from the seeds the notes state (with
their tie rule), and every centroid it produces, and the iteration count,
must be printed. The merges are replayed with the notes' linkage and tie
order and every merge height must be printed. DBSCAN neighbourhood counts
and point types are recomputed and must match the table.

    python ch5fig.py            regenerate every figure and its block in ch5-num.tex
    python ch5fig.py --report   run the checks only
"""
import math
import os
import re
import sys

import stepkit as K

TEX = os.path.join(K.HERE, "ch5-num.tex")
PREFIX = "ch5fig"

T = K.Techs([
    ("SEED", "seed rule", "State the seeds; with one given, take the point farthest from it."),
    ("ASSIGN", "assign nearest", "Each point joins the centroid it is nearest to."),
    ("TIE", "tie-break", "Equal distances: name a rule and apply it; say which way the point went."),
    ("MEANC", "move to mean", "Each centroid moves to the mean of its members."),
    ("CONV", "unchanged = done", "An iteration that reassigns nothing proves convergence."),
    ("MANH", "Manhattan", "$|dx| + |dy|$ instead of the straight line."),
    ("SSE", "SSE", "Sum of squared distances to each point's own centroid: what K-means minimises."),
    ("MIN", "smallest entry", "Merge the two clusters with the smallest distance; that value is the bar height."),
    ("SINGLE", "MIN update", "Single link: the merged row takes the smaller of the two old rows."),
    ("COMPL", "MAX update", "Complete link: the merged row takes the larger of the two old rows."),
    ("EPS", "$\\varepsilon$-neighbourhood", "Count the points within $\\varepsilon$, the point itself included, $d \\le \\varepsilon$."),
    ("CORE", "core / noise", "Count $\\ge$ MinPts is core; not core and near no core point is noise."),
    ("LINK", "connect cores", "Cores within $\\varepsilon$ of each other form one cluster; borders attach."),
])

CAPTION = {"c5s_index": "The moves every chapter-5 numerical below is built from"}
COLS = ["cA", "cB", "cC", "cD"]


def txt(x, y, s, w=None, style="eqn"):
    if w:
        return r"\node[%s, text width=%.2fcm] at (%.3f,%.3f) {%s};" % (style, w, x, y, s)
    return r"\node[%s] at (%.3f,%.3f) {%s};" % (style, x, y, s)


def printed(sec, x, label, tol=0.0015):
    for m in re.finditer(r"(?<![\d.])\d+(?:\.\d+)?", sec):
        if abs(float(m.group(0)) - x) <= tol:
            return m.group(0)
    sys.exit("%s: %.4f is not printed in the problem" % (label, x))


# =====================================================================
#  K-means
# =====================================================================
def kmeans(P, C, dist, tie_last=False, maxit=10, stop=None):
    """[(centroids used, assignment, new centroids, tie points)] until unchanged (or stop iters)."""
    out = []
    prev = None
    for it in range(maxit):
        asg, ties = [], []
        for p in P:
            d = [dist(p, c) for c in C]
            m = min(d)
            idx = [i for i, v in enumerate(d) if abs(v - m) < 1e-9]
            if len(idx) > 1:
                ties.append(p)
            asg.append(idx[-1] if tie_last else idx[0])
        new = []
        for k in range(len(C)):
            mem = [p for p, a in zip(P, asg) if a == k]
            new.append(tuple(sum(v) / len(mem) for v in zip(*mem)) if mem else C[k])
        out.append((list(C), asg, new, ties))
        if asg == prev or (stop and it + 1 == stop):
            break
        prev = asg
        C = new
    return out


def euc(a, b):
    return math.dist(a, b)


def man(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def scatter(P, asg, Cold, Cnew, W, Hh, lo, hi, ties=(), labels=None):
    """TikZ for one K-means iteration inside the panel drawing area."""
    x0, y0, x1, y1 = 0.35, 0.68, W - 0.1, Hh - 0.62 - 0.12
    sx = (x1 - x0) / (hi[0] - lo[0])
    sy = (y1 - y0) / (hi[1] - lo[1])

    def M(p):
        return x0 + (p[0] - lo[0]) * sx, y0 + (p[1] - lo[1]) * sy

    L = [r"\draw[ruleL] (%.2f,%.2f) rectangle (%.2f,%.2f);" % (x0, y0, x1, y1)]
    for v in range(math.ceil(lo[0]), math.floor(hi[0]) + 1):
        L.append(r"\node[font=\tiny, text=sub, anchor=north, inner sep=0.5pt] at (%.2f,%.2f) {%d};"
                 % (M((v, lo[1]))[0], y0, v))
    for v in range(math.ceil(lo[1]), math.floor(hi[1]) + 1):
        L.append(r"\node[font=\tiny, text=sub, anchor=east, inner sep=0.5pt] at (%.2f,%.2f) {%d};"
                 % (x0, M((lo[0], v))[1], v))
    for i, (p, a) in enumerate(zip(P, asg)):
        x, y = M(p)
        tie = p in ties
        L.append(r"\node[dot, minimum size=1.7mm, fill=%s] at (%.3f,%.3f) {};" % (COLS[a], x, y))
        if tie:
            L.append(r"\node[circle, draw=mkc, line width=0.8pt, inner sep=0pt, minimum size=3.6mm]"
                     r" at (%.3f,%.3f) {};" % (x, y))
        if labels:
            L.append(r"\node[font=\tiny, text=sub, anchor=south west, inner sep=0.3pt] at (%.3f,%.3f) {%s};"
                     % (x, y, labels[i]))
    for k, (co, cn) in enumerate(zip(Cold, Cnew)):
        ax, ay = M(co)
        bx, by = M(cn)
        L.append(r"\node[draw=%s, cross out, line width=0.7pt, minimum size=2.2mm, inner sep=0pt] at (%.3f,%.3f) {};"
                 % (COLS[k], ax, ay))
        if math.hypot(bx - ax, by - ay) > 0.05:
            L.append(r"\draw[-{Stealth[length=1.4mm]}, %s, line width=0.6pt] (%.3f,%.3f) -- (%.3f,%.3f);"
                     % (COLS[k], ax, ay, bx, by))
            L.append(r"\node[draw=%s, fill=%s, cross out, line width=1.2pt, minimum size=2.4mm, inner sep=0pt]"
                     r" at (%.3f,%.3f) {};" % (COLS[k], COLS[k], bx, by))
    return L


def fmtc(c):
    return "(%s)" % ", ".join(("%.3f" % v).rstrip("0").rstrip(".") for v in c)


def kfig(fig, sec, P, seeds, dist=euc, tie_last=False, stop=None, seedtxt=None, lo=None, hi=None,
         labels=None, key="conv", W=4.1, Hh=2.9, per=4, expect_iters=None):
    run = kmeans(P, seeds, dist, tie_last, stop=stop)
    if expect_iters and len(run) != expect_iters:
        sys.exit("%s: %d iterations, notes say %d" % (fig, len(run), expect_iters))
    for i, (C, asg, new, ties) in enumerate(run):
        if i + 1 < len(run) or stop:
            for c in new:
                for v in c:
                    printed(sec, v, "%s iteration %d centroid" % (fig, i + 1), tol=6e-4)
    xs = [p[0] for p in P] + [c[0] for r in run for c in r[0] + r[2]]
    ys = [p[1] for p in P] + [c[1] for r in run for c in r[0] + r[2]]
    lo = lo or (math.floor(min(xs)), math.floor(min(ys)))
    hi = hi or (math.ceil(max(xs)), math.ceil(max(ys)))
    panels = []
    step = 1
    if seedtxt:
        panels.append(K.panel(T, fig, step, "Seeds", ["SEED"], [txt(0, Hh - 0.8, seedtxt, W)], W, Hh,
                              key=(key == "seed")))
        step += 1
    prev = None
    for i, (C, asg, new, ties) in enumerate(run):
        same = asg == prev
        tech = ["ASSIGN"] + (["TIE"] if ties else []) + (["CONV"] if same else ["MEANC"])
        if dist is man:
            tech.insert(0, "MANH")
        L = scatter(P, asg, C, C if same else new, W, Hh, lo, hi, ties, labels)
        sizes = [asg.count(k) for k in range(len(C))]
        line = ("unchanged: converged" if same else
                "new: " + ", ".join(fmtc(c) for c in new))
        if stop and i + 1 == stop and not same:
            line += r" \ \textbf{not converged}"
        L.append(txt(0, 0.26, r"%s \ {\color{sub}(%s)}" % (line, "/".join(map(str, sizes))), W, "note"))
        k = (key == "conv" and same) or (key == "tie" and ties) or (key == "last" and i == len(run) - 1)
        panels.append(K.panel(T, fig, step, "Iteration %d" % (i + 1), tech, L, W, Hh, key=bool(k)))
        step += 1
        prev = asg
    return panels, run


# =====================================================================
#  Agglomerative
# =====================================================================
def agglo(names, D, link):
    """Replay: new cluster appended last, pairs scanned row-major, strict < so the first minimum wins."""
    cl = [(n,) for n in names]
    dist = {}
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            dist[((a,), (b,))] = D[i][j]
    steps = []
    while len(cl) > 1:
        best = None
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                v = dist[(cl[i], cl[j])]
                if best is None or v < best[0] - 1e-12:
                    best = (v, i, j)
        v, i, j = best
        a, b = cl[i], cl[j]
        mat = [[dist[(x, y)] for y in cl] for x in cl]
        steps.append((list(cl), mat, (i, j), v))
        m = a + b
        rest = [c for c in cl if c not in (a, b)]
        for c in rest:
            f = min if link == "single" else max
            dist[(m, c)] = dist[(c, m)] = f(dist[(a, c)], dist[(b, c)])
        dist[(m, m)] = 0
        cl = rest + [m]
    return steps


def cname(c, sep=""):
    return c[0] if len(c) == 1 else r"\{%s\}" % sep.join(c)


def agglo_panels(fig, sec, names, D, link, heights, sub=None, keyrank=None, start=1):
    steps = agglo(names, D, link)
    hs = [s[3] for s in steps]
    if any(abs(a - b) > 6e-4 for a, b in zip(hs, heights)) or len(hs) != len(heights):
        sys.exit("%s: heights %s vs notes %s" % (fig, hs, heights))
    for h in heights:
        printed(sec, h, fig + " height", tol=6e-4)
    panels = []
    for k, (cl, mat, (i, j), v) in enumerate(steps):
        n = len(cl)
        cw = min(0.62, 3.3 / n)
        W = 0.95 + cw * n + 0.1
        W = max(W, 3.3)
        Hh = 0.62 + 0.3 + 0.28 * n + 0.72
        L = []
        top = Hh - 0.62 - 0.32
        labs = [cname(c) if sub is None else sub(c) for c in cl]
        for q, l in enumerate(labs):
            L.append(r"\node[hdr, font=\tiny] at (%.3f,%.3f) {%s};" % (0.95 + cw * (q + 0.5), top + 0.22, l))
            L.append(r"\node[hdr, font=\tiny, anchor=east] at (0.9,%.3f) {%s};" % (top - 0.28 * q, l))
        for r in range(n):
            for q in range(n):
                if q > r:
                    continue
                hot = (r, q) in ((j, i), (i, j))
                st = "hot" if hot else "cell"
                L.append(r"\node[%s, minimum width=%.2fcm, minimum height=0.25cm, font=\tiny] at (%.3f,%.3f) {%s};"
                         % (st, cw - 0.03, 0.95 + cw * (q + 0.5), top - 0.28 * r,
                            ("%.3f" % mat[r][q]).rstrip("0").rstrip(".") if r != q else "0"))
        L.append(txt(0, 0.42, r"merge %s $+$ %s at \textbf{%s}" % (labs[i], labs[j], printed(sec, v, fig, 6e-4)),
                     W, "note"))
        tech = ["MIN", "SINGLE" if link == "single" else "COMPL"] if k else ["MIN"]
        panels.append(K.panel(T, fig, start + k, "Merge %d" % (k + 1), tech, L, W, Hh,
                              key=(keyrank is not None and k == keyrank)))
    return panels


# =====================================================================
#  DBSCAN
# =====================================================================
def dbscan_fig(fig, sec, pts, eps, minpts, types_expect, W=5.0, Hh=3.1):
    names = list(pts)
    N = {a: [b for b in names if math.dist(pts[a], pts[b]) <= eps + 1e-9] for a in names}
    core = {a for a in names if len(N[a]) >= minpts}
    typ = {a: "core" if a in core else ("border" if any(b in core for b in N[a]) else "noise") for a in names}
    if typ != types_expect:
        sys.exit("%s: types %s vs notes %s" % (fig, typ, types_expect))
    xs = [p[0] for p in pts.values()]
    ys = [p[1] for p in pts.values()]
    lo = (min(xs) - 1, min(ys) - 1)
    hi = (max(xs) + 1, max(ys) + 1)
    x0, y0, x1, y1 = 0.3, 0.55, W - 0.1, Hh - 0.62 - 0.1
    s = min((x1 - x0) / (hi[0] - lo[0]), (y1 - y0) / (hi[1] - lo[1]))

    def M(p):
        return x0 + (p[0] - lo[0]) * s, y0 + (p[1] - lo[1]) * s

    # clusters of cores
    cl, seen = [], set()
    for a in names:
        if a in core and a not in seen:
            comp, stack = [], [a]
            while stack:
                u = stack.pop()
                if u in seen:
                    continue
                seen.add(u)
                comp.append(u)
                stack += [v for v in N[u] if v in core and v not in seen]
            cl.append(comp)
    col = {}
    for k, comp in enumerate(cl):
        for a in comp:
            col[a] = COLS[k]
    panels = []
    for step, (title, tech, mode) in enumerate((("Circles of radius $\\varepsilon$", ["EPS"], 0),
                                                 ("Core or noise", ["CORE"], 1),
                                                 ("Connect the cores", ["LINK"], 2)), 1):
        L = []
        for a in names:
            x, y = M(pts[a])
            if mode == 0:
                L.append(r"\draw[acc!50, fill=accL, fill opacity=0.35] (%.3f,%.3f) circle (%.3f);" % (x, y, eps * s))
        if mode == 2:
            for a in names:
                for b in N[a]:
                    if a < b and a in core and b in core:
                        (ax, ay), (bx, by) = M(pts[a]), M(pts[b])
                        L.append(r"\draw[%s, line width=1pt] (%.3f,%.3f) -- (%.3f,%.3f);" % (col[a], ax, ay, bx, by))
        for a in names:
            x, y = M(pts[a])
            if mode == 0:
                fill = "sub"
            elif mode == 1:
                fill = "gd" if typ[a] == "core" else ("pin" if typ[a] == "border" else "mkc")
            else:
                fill = col.get(a, "sub!40")
            L.append(r"\node[dot, minimum size=1.8mm, fill=%s] at (%.3f,%.3f) {};" % (fill, x, y))
            lab = a if mode == 0 else "%s\\,%d" % (a, len(N[a])) if mode == 1 else a
            L.append(r"\node[font=\tiny, anchor=south west, inner sep=0.5pt] at (%.3f,%.3f) {%s};" % (x, y, lab))
        if mode == 0:
            note = r"$\varepsilon = %s$, MinPts $= %d$, the point counts itself." % (("%g" % eps), minpts)
        elif mode == 1:
            nc = sum(1 for a in names if typ[a] == "core")
            nb = sum(1 for a in names if typ[a] == "border")
            note = (r"green core %d, purple border %d, orange noise %d (label: count)"
                    % (nc, nb, len(names) - nc - nb))
        else:
            note = r"%d cluster%s; grey = noise." % (len(cl), "" if len(cl) == 1 else "s")
        L.append(txt(0, 0.35, note, W, "note"))
        panels.append(K.panel(T, fig, step, title, tech, L, W, Hh, key=(mode == 1)))
    return panels


# =====================================================================
#  Build
# =====================================================================
def build():
    tex = open(TEX, encoding="utf-8").read()
    S = lambda a, b=None: K.section(tex, a, b)
    figs = []

    def add(name, cap, fig):
        CAPTION[name] = cap
        figs.append((name, fig))

    P = [(1, 2), (2.5, 1), (3.5, 1.5), (4, 1), (3.5, 2.5), (5, 3)]
    s = S(r"\creamq{Problems 1.1", r"\creamq{Problem 1.3}")
    p, _ = kfig("1.1/1.2", s, P, [(1, 2), (5, 3)], expect_iters=2, lo=(0, 0), hi=(6, 4),
                labels=["1", "2", "3", "4", "5", "6"],
                seedtxt=r"The two most widely separated points:\\$c_1 = p_1(1,2)$, \ $c_2 = p_6(5,3)$.")
    add("c5s_km_11", "Step by step: seeds, then each iteration (x = centroid; hollow = before, filled = after)",
        K.grid(p, 3))

    s = S(r"\creamq{Problem 1.3}", r"\creamq{Problem 1.4}")
    P = [(1, 2), (2.5, 4.5), (4, 6), (3.5, 4), (4, 5.5), (3, 6)]
    p, _ = kfig("1.3", s, P, [(1, 2), (4, 6)], expect_iters=2, lo=(0, 1), hi=(5, 7),
                seedtxt=r"$c_1 = (1,2)$, clearly isolated; \ $c_2 = (4,6)$.")
    add("c5s_km_13", "Step by step: seeds, then each iteration", K.grid(p, 3))

    s = S(r"\creamq{Problem 1.4}", r"\creamq{Problem 1.5}")
    P = [(1, 1), (1.5, 2), (3, 4), (5, 7), (3.5, 5), (4.5, 5), (3.5, 4.5)]
    p, run = kfig("1.4", s, P, [(1, 1), (5, 7)], tie_last=True, expect_iters=2, key="tie", lo=(0, 0), hi=(6, 8),
                  seedtxt=r"$c_1 = (1,1)$, $c_2 = (5,7)$: the two most widely separated points.")
    if run[0][3] != [(3, 4)]:
        sys.exit("1.4: the tie should be (3,4) alone")
    K.need(s, "1.4", r"\mk{$(3,4)$ is an exact tie}")
    add("c5s_km_14", "Step by step: the exact tie at (3,4), ringed in orange, sent to C2", K.grid(p, 3))

    s = S(r"\creamq{Problem 1.5}", r"\creamq{Problem 1.6")
    X = [(5.9, 3.2), (4.6, 2.9), (6.2, 2.8), (4.7, 3.2), (5.5, 4.2), (5.0, 3.0), (4.9, 3.1), (6.7, 3.1),
         (5.1, 3.8), (6.0, 3.0)]
    p, _ = kfig("1.5", s, X, [(6.2, 3.2), (6.6, 3.7), (6.5, 3.0)], expect_iters=3, lo=(4, 2), hi=(7, 5),
                labels=[str(i) for i in range(1, 11)], W=4.6)
    add("c5s_km_15", "Step by step: red, green, blue centres (blue, orange, green here) over three passes",
        K.grid(p, 3))

    s = S(r"\creamq{Problem 1.7}", r"\creamq{Problem 1.8}")
    P = [(1, 2), (1.5, 1), (3.5, 1.5), (4, 3), (3.5, 2.5), (6, 4)]
    p, _ = kfig("1.7", s, P, [(1, 2), (6, 4)], expect_iters=2, lo=(0, 0), hi=(7, 5),
                seedtxt=r"The two most widely separated points: $(1,2)$ and $(6,4)$.")
    add("c5s_km_17", "Step by step: seeds, then each iteration", K.grid(p, 3))

    s = S(r"\creamq{Problem 1.8}", r"\creamq{Problem 1.9}")
    P = [(2, 3), (3, 3), (6, 8), (8, 8), (7, 5)]
    far = max(P, key=lambda q: euc(q, (2, 3)))
    if far != (8, 8):
        sys.exit("1.8: farthest point")
    K.need(s, "1.8", "7.810", "6.403", "5.385")
    p, _ = kfig("1.8", s, P, [(2, 3), (8, 8)], expect_iters=2, key="seed", lo=(1, 2), hi=(9, 9),
                seedtxt=r"Only $(2,3)$ is given. Distances from it: 1.000, 6.403, \textbf{7.810}, 5.385."
                        r"\\Farthest is $(8,8)$ $\rightarrow$ $c_2 = (8,8)$.")
    add("c5s_km_18", "Step by step: choose the second seed, then iterate", K.grid(p, 3))

    # 1.9: one dimension
    s = S(r"\creamq{Problem 1.9}", r"\creamq{Problem 1.10")
    P1 = [(v,) for v in (5, 12, 18, 24, 30, 42, 48)]
    run = kmeans(P1, [(5,), (12,), (18,)], euc)
    if len(run) != 4 or [c[0] for c in run[-1][2]] != [5, 18, 40]:
        sys.exit("1.9: run")
    sse = sum((p[0] - run[-1][2][a][0]) ** 2 for p, a in zip(P1, run[-1][1]))
    K.need(s, "1.9", r"\tfrac{162}{5} = 32.4", r"\tfrac{144}{4} = 36", r"SSE = 0 + 72 + 168 = \mathbf{240}")
    if sse != 240:
        sys.exit("1.9: SSE")
    W, Hh = 4.1, 1.85
    panels = []
    prev = None
    for i, (C, asg, new, _) in enumerate(run):
        same = asg == prev
        L = []
        X0, X1 = 0.2, W - 0.15

        def Xp(v):
            return X0 + (v - 0) / 52 * (X1 - X0)

        L.append(r"\draw[sub] (%.2f,0.75) -- (%.2f,0.75);" % (X0, X1))
        for v in (0, 10, 20, 30, 40, 50):
            L.append(r"\node[font=\tiny, text=sub, anchor=north, inner sep=0.5pt] at (%.3f,0.72) {%d};" % (Xp(v), v))
        for p, a in zip(P1, asg):
            L.append(r"\node[dot, minimum size=1.7mm, fill=%s] at (%.3f,0.9) {};" % (COLS[a], Xp(p[0])))
        for k, (co, cn) in enumerate(zip(C, new)):
            L.append(r"\node[draw=%s, cross out, line width=0.7pt, minimum size=2.2mm, inner sep=0pt] at (%.3f,1.12) {};"
                     % (COLS[k], Xp(co[0])))
            if abs(cn[0] - co[0]) > 1e-9 and not same:
                L.append(r"\draw[-{Stealth[length=1.3mm]}, %s] (%.3f,1.12) -- (%.3f,1.12);" % (COLS[k], Xp(co[0]), Xp(cn[0])))
        L.append(txt(0, 0.38, ("unchanged: converged" if same else "new: " + ", ".join(
            ("%g" % c[0]) for c in new)), W, "note"))
        panels.append(K.panel(T, "1.9", i + 1, "Iteration %d" % (i + 1),
                              ["ASSIGN", "CONV" if same else "MEANC"], L, W, Hh))
        prev = asg
    L = [txt(0, 1.1, r"$\{5\}$: 0 \quad $\{12,18,24\}$: $36+0+36 = 72$\\$\{30,42,48\}$: $100+4+64 = 168$", W),
         txt(0, 0.45, r"$SSE = \mathbf{240}$", W)]
    panels.append(K.panel(T, "1.9", len(panels) + 1, "SSE", ["SSE"], L, W, Hh, key=True))
    add("c5s_km_19", "Step by step: four passes along the line (the boundaries move three times), then SSE",
        K.grid(panels, 3))

    # 1.10 Manhattan, stop at 3
    s = S(r"\creamq{Problem 1.10", r"\T{M2.")
    p, run = kfig("1.10", s, X, [(6.2, 3.2), (6.6, 3.7), (6.5, 3.0)], dist=man, stop=3, key="last",
                  lo=(4, 2), hi=(7, 5), labels=[str(i) for i in range(1, 11)], W=4.6, expect_iters=3)
    if run[-1][1] == run[-2][1]:
        sys.exit("1.10: should not have converged")
    K.need(s, "1.10", "not converged")
    add("c5s_km_110", "Step by step: Manhattan distance, three passes, still moving", K.grid(p, 3))

    # M2
    s = S(r"\creamq{Problem 2.1}", r"\creamq{Problem 2.2}")
    D = [[0, .24, .22, .37, .34, .23], [.24, 0, .15, .20, .14, .25], [.22, .15, 0, .15, .28, .11],
         [.37, .20, .15, 0, .29, .22], [.34, .14, .28, .29, 0, .39], [.23, .25, .11, .22, .39, 0]]
    sub = lambda c: c[0].replace("p", "$p_") + "$" if len(c) == 1 else r"\{%s\}" % "".join(
        x.replace("p", "") for x in c)
    p = agglo_panels("2.1", s, ["p1", "p2", "p3", "p4", "p5", "p6"], D, "single", [.11, .14, .15, .15, .22],
                     sub=sub, keyrank=2)
    add("c5s_ag_21", "Step by step: the matrix before each merge, smallest entry lit (single link)",
        K.grid(p, 5))

    s = S(r"\creamq{Problem 2.2}", r"\creamq{Problem 2.3}")
    Pt = [(0.40, 0.53), (0.22, 0.38), (0.35, 0.32), (0.26, 0.19), (0.08, 0.41), (0.45, 0.30)]
    D = [[math.dist(a, b) for b in Pt] for a in Pt]
    p = agglo_panels("2.2", s, ["p1", "p2", "p3", "p4", "p5", "p6"], D, "complete",
                     [.102, .143, .219, .342, .386], sub=sub, keyrank=2)
    add("c5s_ag_22", "Step by step: the matrix before each merge (complete link: the merged row takes the MAX)",
        K.grid(p, 5))

    s = S(r"\creamq{Problem 2.3}", r"\T{M3.")
    D = [[0, .12, .51, .84, .28, .34], [.12, 0, .25, .16, .77, .61], [.51, .25, 0, .14, .70, .93],
         [.84, .16, .14, 0, .45, .20], [.28, .77, .70, .45, 0, .67], [.34, .61, .93, .20, .67, 0]]
    sub2 = lambda c: c[0] if len(c) == 1 else r"\{%s\}" % "".join(c)
    pa = agglo_panels("2.3a", s, list("ABCDEF"), D, "single", [.12, .14, .16, .20, .28], sub=sub2, keyrank=2)
    pb = agglo_panels("2.3b", s, list("ABCDEF"), D, "complete", [.12, .14, .61, .70, .93], sub=sub2, keyrank=2)
    add("c5s_ag_23", "Step by step: (a) single link, top row; (b) complete link, bottom row",
        K.rows(pa, pb))

    # M3
    s = S(r"\creamq{Problem 3.1}", r"\creamq{Practice")
    pts = dict(zip("ABCDEFGH", [(2, 10), (2, 5), (8, 4), (5, 8), (7, 5), (6, 4), (1, 2), (4, 9)]))
    exp = dict(zip("ABCDEFGH", ["noise", "noise", "core", "core", "core", "core", "noise", "core"]))
    add("c5s_db_31", "Step by step: neighbourhoods, point types, clusters",
        K.grid(dbscan_fig("3.1", s, pts, 2, 2, exp), 3))
    s = S(r"\creamq{Practice")
    pts = dict(zip("ABCDEF", [(1, 1), (1, 2), (2, 1), (8, 8), (8, 9), (25, 25)]))
    exp = dict(zip("ABCDEF", ["core", "core", "core", "noise", "noise", "noise"]))
    add("c5s_db_pr", "Step by step: the same method with MinPts 3 (D and E are noise)",
        K.grid(dbscan_fig("Practice", s, pts, 2, 3, exp), 3))

    return [("c5s_index", T.index())] + figs


def main():
    figs = build()
    if "--report" in sys.argv:
        for n, _ in figs:
            print("ok  %s" % n)
        return
    K.render([("pre", K.preamble(T))] + figs, TEX, PREFIX, CAPTION,
             scale={"c5s_ag_21": 0.82, "c5s_ag_22": 0.82})


if __name__ == "__main__":
    main()
