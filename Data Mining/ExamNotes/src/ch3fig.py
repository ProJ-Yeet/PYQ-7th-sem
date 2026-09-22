# -*- coding: utf-8 -*-
"""Draw the step-by-step solution under every chapter-3 numerical in ch3-num.tex.

ID3 (1.1-1.3): the finished tree, every internal node carrying the rows that
reach it, its class counts, its entropy, the gain of the winning attribute
and of the runner-up; leaves coloured by class. 1.4 asks for the root only:
entropy, gain ranking and the root with its branches, as panels.

Everything else is drawn one panel per step, each with a TECHNIQUE chip
naming the move (Gini, binary split, prior, class count, product, Laplace,
Gaussian, distance, k nearest, vote, read the axes, diagonal, actual total,
predicted total, chain rule...), the decisive step framed KEY STEP, and a
technique index at the top of the chapter.

Exit test is replay. Every tree is regrown by ID3 from the table the paper
prints, and each node's winning and runner-up gain must be printed in that
problem's text (to the notes' own rounding: H&K truncates 0.2467 to 0.246,
so a printed value within 0.0015 counts, and that printed value is what the
figure shows). Every Naive-Bayes, k-NN, Gini, confusion-matrix number a panel
shows is recomputed from the data and must be printed in its problem.

    python ch3fig.py            regenerate every figure and its block in ch3-num.tex
    python ch3fig.py --report   run the checks only
"""
import math
import os
import re
import sys
from collections import Counter

import stepkit as K
from stepkit import BS

TEX = os.path.join(K.HERE, "ch3-num.tex")
PREFIX = "ch3fig"

T = K.Techs([
    ("ENT", "entropy", "Info $= -\\sum p\\log_2 p$ of the class counts at a node."),
    ("GAIN", "gain", "Info before minus weighted Info after the split; the largest wins."),
    ("PURE", "pure branch", "A partition holding one class has Info (or Gini) 0 and becomes a leaf."),
    ("GINI", "Gini", "$1-\\sum p^2$: the impurity Gini-based trees minimise."),
    ("BIN", "binary split", "Gini splits in two: group the values into two subsets, try each grouping."),
    ("PRIOR", "prior", "$P(C)$ = class count / all tuples."),
    ("LIKE", "class count", "$P(x_k|C)$ = tuples of class $C$ with that value / tuples of class $C$."),
    ("ZERO", "Laplace", "A zero count wipes out the product: add 1 to each count, $k$ to the total."),
    ("GAUSS", "Gaussian", "A continuous attribute: fit $\\mu,\\sigma$ per class, read the density at $x$."),
    ("PROD", "product", "Naive independence: multiply the per-attribute probabilities."),
    ("MAX", "largest wins", "Compare the candidates; the largest score is the answer."),
    ("DIST", "distance", "Euclidean distance from the query to every training tuple."),
    ("KNN", "k nearest", "Sort the distances and keep the $k$ smallest."),
    ("VOTE", "majority vote", "The class most common among the $k$ nearest is the prediction."),
    ("AXES", "read the axes", "Find which axis is Actual before naming TP, FN, FP, TN. Papers flip it."),
    ("TALLY", "tally", "Compare actual and predicted position by position and count each outcome."),
    ("DIAG", "diagonal", "Accuracy uses the diagonal (TP + TN) over everything."),
    ("OFFD", "off-diagonal", "Error rate uses the off-diagonal (FP + FN) over everything."),
    ("ACT", "actual total", "TPR, specificity and FPR divide by an ACTUAL class total, $P$ or $N$."),
    ("PRED", "predicted total", "Precision divides by the PREDICTED-positive total, TP + FP."),
    ("SUM", "weighted sum", "A neuron adds its weighted inputs, $net = \\sum w_i x_i$."),
    ("SIG", "sigmoid", "$\\sigma(z) = 1/(1+e^{-z})$, and $\\sigma' = \\sigma(1-\\sigma)$."),
    ("CHAIN", "chain rule", "Multiply the local derivatives along the one path from the loss to the weight."),
])

CAPTION = {"c3s_index": "The moves every chapter-3 numerical below is built from"}


def printed(sec, x, label, tol=0.0015):
    """The number the problem prints for x (within tol), as printed."""
    best = None
    for m in re.finditer(r"(?<![\d.])\d+\.\d+", sec):
        v = float(m.group(0))
        if abs(v - x) <= tol and (best is None or (abs(v - x), -len(m.group(0)))
                < (abs(float(best) - x), -len(best))):
            best = m.group(0)
    if best is None:
        sys.exit("%s: %.4f is not printed in the problem" % (label, x))
    return best


# =====================================================================
#  ID3
# =====================================================================
def H(labels):
    n = len(labels)
    return -sum(v / n * math.log2(v / n) for v in Counter(labels).values() if v) if n else 0.0


def gain(rows, a):
    parts = {}
    for r in rows:
        parts.setdefault(r[a], []).append(r)
    ia = sum(len(p) / len(rows) * H([r[-1] for r in p]) for p in parts.values())
    return H([r[-1] for r in rows]) - ia


def id3(rows, attrs, ids, path=()):
    labels = [r[-1] for r in rows]
    nd = dict(ids=ids, lab=labels, h=H(labels), path=path)
    if nd["h"] < 1e-12:
        nd["leaf"] = labels[0]
        return nd
    gs = sorted(((round(gain(rows, a), 9), -attrs.index(a), a) for a in attrs), reverse=True)
    best, second = gs[0][2], gs[1][2]
    nd.update(attr=best, g=gs[0][0], second=second, g2=gs[1][0],
              tie=abs(gs[0][0] - gs[1][0]) < 1e-9)
    kids = []
    for v in dict.fromkeys(r[best] for r in rows):
        sel = [i for i, r in enumerate(rows) if r[best] == v]
        kids.append((v, id3([rows[i] for i in sel], [a for a in attrs if a != best],
                            [ids[i] for i in sel], path + ((best, v),))))
    nd["kids"] = kids
    return nd


def nodes(nd):
    yield nd
    for _, k in nd.get("kids", []):
        yield from nodes(k)


SLOTW, LEVELH = 2.45, 2.0


def layout(nd, depth, cur):
    nd["y"] = -depth * LEVELH
    if "leaf" in nd:
        nd["x"] = cur[0] * SLOTW
        cur[0] += 1
        return
    for _, k in nd["kids"]:
        layout(k, depth + 1, cur)
    xs = [k["x"] for _, k in nd["kids"]]
    nd["x"] = (min(xs) + max(xs)) / 2


def tree_fig(name, rows, names, classes, sec, show=None):
    show = show or {}
    t = id3(rows, list(range(len(names))), list(range(1, len(rows) + 1)))
    for nd in nodes(t):
        if "leaf" in nd:
            continue
        where = "%s at %s" % (name, nd["path"] or "root")
        nd["gs"] = printed(sec, nd["g"], where + " winning gain")
        nd["g2s"] = printed(sec, nd["g2"], where + " runner-up gain")
        nd["hs"] = printed(sec, nd["h"], where + " entropy")
        if nd["tie"] and "tie" not in sec:
            sys.exit("%s: the tie at %s is not flagged in the text" % (name, nd["path"]))
    layout(t, 0, [0])
    L = [BS + "begin{tikzpicture}"]
    cnt = [0]
    style = {c: "leaf" + "BCD"[i] for i, c in enumerate(classes)}

    def counts(nd):
        c = Counter(nd["lab"])
        return r"\,$\cdot$\,".join("%d %s" % (c[k], show.get(k, k)) for k in classes if c[k])

    def emit(nd):
        cnt[0] += 1
        nd["tag"] = "n%d" % cnt[0]
        who = "all %d rows" % len(nd["ids"]) if not nd["path"] else \
            ("row " if len(nd["ids"]) == 1 else "rows ") + ", ".join(map(str, nd["ids"]))
        if "leaf" in nd:
            txt = r"{\scriptsize\bfseries %s}\\%s\\%s" % (show.get(nd["leaf"], nd["leaf"]),
                                                        who, counts(nd))
            st = style[nd["leaf"]]
        else:
            tie = r" \textbf{tie}" if nd["tie"] else ""
            txt = (r"{\scriptsize\bfseries\color{acc} split on %s}\\%s\\%s\quad \textit{H} = %s\\"
                   r"\textbf{Gain %s}\; {\color{sub}(next: %s %s%s)}"
                   % (names[nd["attr"]], who, counts(nd), nd["hs"], nd["gs"],
                      names[nd["second"]], nd["g2s"], tie))
            st = "inode"
        L.append(r"\node[%s] (%s) at (%.3f,%.3f) {%s};" % (st, nd["tag"], nd["x"], nd["y"], txt))
        for v, k in nd.get("kids", []):
            emit(k)
            L.append(r"\draw[edge] (%s.south) -- node[elab] {%s} (%s.north);"
                     % (nd["tag"], show.get(v, v), k["tag"]))

    emit(t)
    L.append(BS + "end{tikzpicture}")
    return K.single("\n".join(L)), t


# =====================================================================
#  Small drawing helpers
# =====================================================================
FILL = ["cA", "cB", "cC", "cD"]


def sbar(x, y, w, parts, h=0.30, lab=True):
    """Stacked horizontal bar: parts = [(count, colour, text)]."""
    tot = sum(p[0] for p in parts) or 1
    L, cx = [], x
    for c, col, txt in parts:
        if not c:
            continue
        dw = w * c / tot
        L.append(r"\fill[%sL, draw=%s, line width=0.4pt] (%.3f,%.3f) rectangle (%.3f,%.3f);"
                 % (col, col, cx, y, cx + dw, y + h))
        if lab:
            L.append(r"\node[font=\tiny\bfseries, text=%s, inner sep=0pt] at (%.3f,%.3f) {%s};"
                     % (col, cx + dw / 2, y + h / 2, txt))
        cx += dw
    return L


def hbar(x, y, w, frac, col, txt, h=0.22, bold=False):
    L = [r"\draw[ruleL] (%.3f,%.3f) rectangle (%.3f,%.3f);" % (x, y, x + w, y + h)]
    if frac > 0:
        L.append(r"\fill[%s] (%.3f,%.3f) rectangle (%.3f,%.3f);"
                 % (col, x, y, x + max(w * frac, 0.02), y + h))
    L.append(r"\node[font=\tiny%s, anchor=west, inner sep=1pt] at (%.3f,%.3f) {%s};"
             % (r"\bfseries" if bold else "", x + w + 0.04, y + h / 2, txt))
    return L


def txt(x, y, s, w=None, style="eqn"):
    if w:
        return r"\node[%s, text width=%.2fcm] at (%.3f,%.3f) {%s};" % (style, w, x, y, s)
    return r"\node[%s] at (%.3f,%.3f) {%s};" % (style, x, y, s)


# =====================================================================
#  1.4 root only, and Gini
# =====================================================================
def fig_root14(sec):
    rows = [("Male", "0", "Cheap", "Low", "Bus"), ("Male", "1", "Cheap", "Medium", "Bus"),
            ("Female", "1", "Cheap", "Medium", "Train"), ("Female", "0", "Cheap", "Low", "Bus"),
            ("Male", "1", "Cheap", "Medium", "Bus"), ("Male", "0", "Standard", "High", "Train"),
            ("Female", "1", "Standard", "Medium", "Train"), ("Female", "1", "Expensive", "High", "Car"),
            ("Male", "2", "Expensive", "Medium", "Car"), ("Female", "2", "Expensive", "High", "Car")]
    names = ["Gender", "Car ownership", "Travel cost", "Income level"]
    cls = ["Bus", "Train", "Car"]
    col = dict(zip(cls, FILL))
    h = H([r[-1] for r in rows])
    hs = printed(sec, h, "1.4 Info(D)")
    g = {n: gain(rows, i) for i, n in enumerate(names)}
    order = sorted(names, key=lambda n: -g[n])
    if order[0] != "Travel cost":
        sys.exit("1.4: the root is not Travel cost")
    gs = {n: printed(sec, g[n], "1.4 gain " + n) for n in names}
    c = Counter(r[-1] for r in rows)
    fig, W = "1.4", 5.0
    p1 = K.panel(T, fig, 1, "Entropy of the whole set", ["ENT"],
                 sbar(0, 1.05, W, [(c[k], col[k], "%s %d" % (k, c[k])) for k in cls])
                 + [txt(0, 0.75, r"$Info(D) = -\tfrac{4}{10}\log_2\tfrac{4}{10}"
                                 r" - 2\cdot\tfrac{3}{10}\log_2\tfrac{3}{10} = \mathbf{%s}$" % hs, W)],
                 W, 2.0)
    body = []
    gmax = max(g.values())
    for i, n in enumerate(order):
        body += hbar(0, 1.12 - i * 0.30, 3.3, g[n] / gmax, "mkc" if i == 0 else "acc!55",
                     "%s %s" % (n, gs[n]), bold=(i == 0))
    body.append(txt(0, 0.12, r"Car ownership and Income level \textbf{tie} at %s." % gs["Car ownership"], W,
                    "note"))
    p2 = K.panel(T, fig, 2, "Gain of every attribute", ["GAIN"], body, W, 2.0, key=True)
    body = [r"\node[inode, text width=2.2cm] (r) at (2.5,1.08) {\textbf{Travel cost}\\Gain %s};"
            % gs["Travel cost"]]
    for j, v in enumerate(["Cheap", "Standard", "Expensive"]):
        sub = [r for r in rows if r[2] == v]
        cc = Counter(r[-1] for r in sub)
        pure = len(cc) == 1
        lab = "(%s)" % ",".join(str(cc[k]) for k in cls)
        st = ("leaf" + "BCD"[cls.index(sub[0][-1])]) if pure else "inode"
        body.append(r"\node[%s, text width=1.35cm] (b%d) at (%.2f,0.30) {\textbf{%s}\\%s %s};"
                    % (st, j, 0.8 + j * 1.7, v, lab, r"\mk{pure}" if pure else "mixed"))
        body.append(r"\draw[edge] (r.south) -- (b%d.north);" % j)
    p3 = K.panel(T, fig, 3, "Root and its branches", ["PURE"], body, W, 2.0)
    need(sec, "1.4", "(Bus, Train, Car)")
    return K.grid([p1, p2, p3], 3)


def need(sec, label, *s):
    K.need(sec, label, *s)


def fig_gini(sec):
    fig, W, Hh = "Gini", 3.9, 2.25
    y, n = 9, 5
    g0 = 1 - (y / 14) ** 2 - (n / 14) ** 2
    s0 = printed(sec, g0, "Gini(D)")
    p1 = K.panel(T, fig, 1, "Gini of the whole set", ["GINI"],
                 sbar(0, 1.25, W, [(9, "cA", "Yes 9"), (5, "cB", "No 5")])
                 + [txt(0, 0.95, r"$1 - (\tfrac{9}{14})^2 - (\tfrac{5}{14})^2 = \mathbf{%s}$" % s0, W)],
                 W, Hh)

    def split(step, title, d1, d2, l1, l2, key, tech):
        gi = [1 - (a / (a + b)) ** 2 - (b / (a + b)) ** 2 for a, b in (d1, d2)]
        ga = sum((a + b) / 14 * g for (a, b), g in zip((d1, d2), gi))
        dg = g0 - ga
        s = [printed(sec, gi[0], title + " D1"), "%s" % ("0" if gi[1] < 1e-9 else printed(sec, gi[1], title + " D2")),
             printed(sec, ga, title + " Gini_A"), printed(sec, dg, title + " drop")]
        body = [txt(0, 1.58, l1, W, "note")]
        body += sbar(0, 1.08, W * 0.7 * (sum(d1) / 14), [(d1[0], "cA", str(d1[0])), (d1[1], "cB", str(d1[1]))],
                     h=0.26)
        body.append(txt(W * 0.7 * sum(d1) / 14 + 0.05, 1.30, "%s" % s[0], None, "eqn"))
        body.append(txt(0, 0.98, l2, W, "note"))
        body += sbar(0, 0.50, W * 0.7 * (sum(d2) / 14), [(d2[0], "cA", str(d2[0])), (d2[1], "cB", str(d2[1]))],
                     h=0.26)
        body.append(txt(W * 0.7 * sum(d2) / 14 + 0.05, 0.72, "%s%s" % (s[1], r" \textcolor{mkc}{pure}"
                                                                      if gi[1] < 1e-9 else ""), None, "eqn"))
        body.append(txt(0, 0.36, r"$Gini_A = %s$, \ $\Delta = \mathbf{%s}$" % (s[2], s[3]), W))
        return K.panel(T, fig, step, title, tech, body, W, Hh, key=key), dg, s[3]

    p2, d_inc, s_inc = split(2, "Income", (7, 3), (2, 2), r"\{low, medium\}: 10 tuples",
                             r"\{high\}: 4 tuples", False, ["BIN"])
    p3, d_age, s_age = split(3, "Age", (5, 5), (4, 0), r"\{youth, senior\}: 10 tuples",
                             r"\{middle\_aged\}: 4 tuples", True, ["BIN", "PURE"])
    body = hbar(0, 1.0, 2.4, d_inc / d_age, "acc!55", r"Income $\Delta$ %s" % s_inc) + \
        hbar(0, 0.62, 2.4, 1.0, "mkc", r"Age $\Delta$ %s" % s_age, bold=True) + \
        [txt(0, 0.34, r"\textbf{Age} is chosen, as by information gain.", W)]
    p4 = K.panel(T, fig, 4, "Largest drop wins", ["MAX"], body, W, Hh)
    return K.grid([p1, p2, p3, p4], 4)


# =====================================================================
#  Naive Bayes
# =====================================================================
def fig_nb31(sec):
    fig, W, Hh = "3.1", 3.9, 2.55
    need(sec, "3.1", "0.643", "0.357")
    p1 = K.panel(T, fig, 1, "Priors", ["PRIOR"],
                 sbar(0, 1.5, W, [(9, "cA", "Yes 9"), (5, "cB", "No 5")])
                 + [txt(0, 1.2, r"$P(\text{Yes}) = 9/14 = 0.643$\\$P(\text{No}) = 5/14 = 0.357$", W)],
                 W, Hh)
    L = [("age = youth", 2, 9, 3, 5), ("income = med", 4, 9, 2, 5),
         ("student = yes", 6, 9, 1, 5), ("credit = fair", 6, 9, 2, 5)]
    body = [txt(1.55, 1.83, r"\textbf{$|$Yes}", None, "note"), txt(2.75, 1.83, r"\textbf{$|$No}", None, "note")]
    py, pn = 1.0, 1.0
    for i, (a, ky, ny, kn, nn) in enumerate(L):
        yy = 1.45 - i * 0.36
        body.append(txt(0, yy + 0.17, a, None, "note"))
        body += hbar(1.55, yy, 0.55, ky / ny, "cA", "%d/%d" % (ky, ny), h=0.18)
        body += hbar(2.75, yy, 0.55, kn / nn, "cB", "%d/%d" % (kn, nn), h=0.18)
        need(sec, "3.1", "%d/%d=%s" % (ky, ny, "%.3f" % (ky / ny)), "%d/%d=%s" % (kn, nn, "%.3f" % (kn / nn)))
        py *= round(ky / ny, 3)
        pn *= round(kn / nn, 3)
    p2 = K.panel(T, fig, 2, "Count within each class", ["LIKE"], body, W, Hh)
    sy, sn = printed(sec, py, "P(X|Yes)", 1e-4), printed(sec, pn, "P(X|No)", 5e-5)
    body = [txt(0, 1.8, r"$P(X|\text{Yes}) = 0.222\cdot0.444\cdot0.667\cdot0.667$", W),
            txt(0, 1.45, r"$= \mathbf{%s}$" % sy, W),
            txt(0, 1.05, r"$P(X|\text{No}) = 0.600\cdot0.400\cdot0.200\cdot0.400$", W),
            txt(0, 0.70, r"$= \mathbf{%s}$" % sn, W),
            txt(0, 0.32, r"Attributes treated as independent given the class.", W, "note")]
    p3 = K.panel(T, fig, 3, "Multiply", ["PROD"], body, W, Hh)
    fy, fn = float(sy) * 9 / 14, float(sn) * 5 / 14
    ty, tn = printed(sec, fy, "score Yes", 5e-4), printed(sec, fn, "score No", 5e-4)
    body = hbar(0, 1.45, 2.3, 1.0, "cA", r"Yes: %s" % ty, h=0.26, bold=True) + \
        hbar(0, 1.05, 2.3, fn / fy, "cB", r"No: %s" % tn, h=0.26) + \
        [txt(0, 0.72, r"$\times P(C)$, then compare. $P(X)$ cancels.", W, "note"),
         txt(0, 0.38, r"\textbf{buys\_computer = Yes}", W)]
    p4 = K.panel(T, fig, 4, "Times the prior, compare", ["MAX"], body, W, Hh, key=True)
    return K.grid([p1, p2, p3, p4], 4)


def gauss(x, mu, sd):
    return math.exp(-(x - mu) ** 2 / (2 * sd * sd)) / (math.sqrt(2 * math.pi) * sd)


def fig_nb32(sec):
    fig, W, Hh = "3.2", 3.1, 2.55
    need(sec, "3.2", r"P(\text{No})=0.7", r"P(\text{Yes})=0.3")
    p1 = K.panel(T, fig, 1, "Priors", ["PRIOR"],
                 sbar(0, 1.5, W, [(7, "cA", "No 7"), (3, "cB", "Yes 3")])
                 + [txt(0, 1.2, r"$P(\text{No}) = 0.7$\\$P(\text{Yes}) = 0.3$", W)], W, Hh)
    body = [txt(1.45, 1.83, r"\textbf{$|$No}", None, "note"), txt(2.3, 1.83, r"\textbf{$|$Yes}", None, "note")]
    for i, (a, kn, nn, ky, ny) in enumerate([("HO = No", 4, 7, 3, 3), ("Married", 4, 7, 0, 3)]):
        yy = 1.4 - i * 0.45
        body.append(txt(0, yy + 0.19, a, None, "note"))
        body += hbar(1.45, yy, 0.4, kn / nn, "cA", "%d/%d" % (kn, nn), h=0.2)
        body += hbar(2.3, yy, 0.4, ky / ny, "cB", ("%d/%d" % (ky, ny)) + (r" \mk{0!}" if ky == 0 else ""),
                     h=0.2)
    need(sec, "3.2", "4/7 = 0.571", "3/3 = 1.0", "0/3 = 0")
    body.append(txt(0, 0.35, r"A single zero makes $P(X|\text{Yes}) = 0$ whatever else holds.", W, "note"))
    p2 = K.panel(T, fig, 2, "Categorical counts", ["LIKE"], body, W, Hh)
    lm, lh = (0 + 1) / (3 + 3), (3 + 1) / (3 + 2)
    need(sec, "3.2", r"\frac{0+1}{3+3} = 0.167", r"\frac{3+1}{3+2} = 0.8")
    body = [txt(0, 1.8, r"$P(\text{Married}|\text{Yes}) = \frac{0+1}{3+3} = \mathbf{%.3f}$" % lm, W),
            txt(0, 1.3, r"$P(\text{HO=No}|\text{Yes}) = \frac{3+1}{3+2} = \mathbf{%.1f}$" % lh, W),
            txt(0, 0.8, r"$+1$ per count, $+k$ per total ($k$ = values the attribute takes: 3, 2).", W,
                "note")]
    p3 = K.panel(T, fig, 3, "Laplace fix", ["ZERO"], body, W, Hh)
    no = [125, 100, 70, 120, 60, 220, 75]
    ye = [95, 85, 90]
    mu_n = sum(no) / 7
    sd_n = math.sqrt(sum((v - mu_n) ** 2 for v in no) / 6)
    mu_y, sd_y = sum(ye) / 3, math.sqrt(sum((v - 90) ** 2 for v in ye) / 2)
    gn, gy = gauss(120, mu_n, sd_n), gauss(120, mu_y, sd_y)
    need(sec, "3.2", r"\mu = 110", r"\sigma = 54.54", r"\mu = 90", r"\sigma = 5", "0.00719",
         r"1.2\times10^{-9}")
    if abs(mu_n - 110) > 1e-9 or abs(sd_n - 54.54) > 0.005 or abs(gn - 0.00719) > 5e-6 \
            or abs(gy / 1e-9 - 1.2) > 0.05:
        sys.exit("3.2: Gaussian recompute disagrees")
    WG = 4.4
    x0, x1 = 40.0, 240.0

    def X(v):
        return (v - x0) / (x1 - x0) * WG

    body = []
    for yb, mu, sd, col, lab in ((1.05, mu_n, sd_n, "cA", r"No: $\mu$=110, $\sigma$=54.5"),
                                 (0.25, mu_y, sd_y, "cB", r"Yes: $\mu$=90, $\sigma$=5")):
        pk = gauss(mu, mu, sd)
        pts = []
        for i in range(161):
            v = x0 + (x1 - x0) * i / 160
            pts.append("(%.3f,%.3f)" % (X(v), yb + 0.55 * gauss(v, mu, sd) / pk))
        body.append(r"\draw[%s, line width=0.8pt] plot[smooth] coordinates {%s};" % (col, " ".join(pts)))
        body.append(r"\draw[ruleL] (0,%.2f) -- (%.2f,%.2f);" % (yb, WG, yb))
        body.append(txt(WG - 1.95, yb + 0.62, lab, None, "note"))
    body.append(r"\draw[mkc, dashed, line width=0.6pt] (%.3f,0.2) -- (%.3f,1.72);" % (X(120), X(120)))
    body.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=south] at (%.3f,1.7) {\$120K};" % X(120))
    body.append(txt(X(120) + 0.05, 1.42, r"$g = 0.00719$", None, "eqn"))
    body.append(txt(X(120) + 0.05, 0.48, r"$g \approx 1.2{\times}10^{-9}$ (6$\sigma$ out)", None, "eqn"))
    for v in (60, 120, 180):
        body.append(r"\node[font=\tiny, text=sub, anchor=north, inner sep=1pt] at (%.3f,0.25) {%d};"
                    % (X(v), v))
    p4 = K.panel(T, fig, 4, "Income: a Gaussian per class", ["GAUSS"], body, WG, Hh, key=True)
    sn_, sy_ = 0.571 * 0.571 * 0.00719 * 0.7, 0.8 * 0.167 * 1.2e-9 * 0.3
    need(sec, "3.2", r"1.64\times10^{-3}", r"4.8\times10^{-11}")
    if abs(sn_ - 1.64e-3) > 5e-6 or abs(sy_ - 4.8e-11) > 1e-12:
        sys.exit("3.2: combine recompute disagrees")
    body = [txt(0, 1.8, r"No: $0.571\cdot0.571\cdot0.00719\cdot0.7$", 4.4),
            txt(0, 1.48, r"$= \mathbf{1.64\times10^{-3}}$", 4.4),
            txt(0, 1.1, r"Yes: $0.8\cdot0.167\cdot1.2{\times}10^{-9}\cdot0.3$", 4.4),
            txt(0, 0.78, r"$\approx \mathbf{4.8\times10^{-11}}$", 4.4),
            txt(0, 0.38, r"\textbf{Defaulted = No}, larger by about $10^7$.", 4.4)]
    p5 = K.panel(T, fig, 5, "Combine, compare", ["PROD", "MAX"], body, 4.4, Hh)
    return K.rows([p1, p2, p3], [p4, p5])


# =====================================================================
#  k-NN
# =====================================================================
def fig_knn(sec):
    fig = "4.1"
    q = (7, 3.2, 4.7, 1.4)
    data = [(1, (5.1, 3.5, 1.4, 0.2), "setosa"), (2, (4.9, 3.0, 1.4, 0.2), "setosa"),
            (3, (4.7, 3.2, 1.3, 0.2), "setosa"), (4, (6.0, 2.2, 4.0, 1.0), "versicolor"),
            (5, (6.1, 2.9, 4.7, 1.4), "versicolor"), (6, (5.6, 2.9, 3.6, 1.3), "versicolor"),
            (7, (6.7, 3.1, 4.4, 1.4), "versicolor")]
    d = [(math.dist(q, v), i, c) for i, v, c in data]
    for dd, i, c in d:
        need(sec, "4.1 id %d" % i, "%.3f" % dd)
    d.sort()
    col = {"setosa": "cB", "versicolor": "cA"}
    W, Hh, SC = 5.3, 2.2, 5.1 / 4.5

    def axis(hi=None):
        L = [r"\draw[sub, -{Stealth[length=1.6mm]}] (0,0.55) -- (%.2f,0.55);" % (W + 0.05)]
        for v in range(5):
            L.append(r"\draw[sub] (%.3f,0.5) -- (%.3f,0.6);" % (v * SC, v * SC))
            L.append(r"\node[font=\tiny, text=sub, anchor=north, inner sep=1pt] at (%.3f,0.5) {%d};"
                     % (v * SC, v))
        if hi:
            L.append(r"\fill[mkL] (0,0.62) rectangle (%.3f,1.55);" % (hi * SC + 0.08))
            L.append(r"\draw[mkc, line width=0.7pt] (%.3f,0.62) -- (%.3f,1.55);" % (hi * SC + 0.08,
                                                                                 hi * SC + 0.08))
        stack = {}
        for dd, i, c in d:
            key = round(dd * SC / 0.28)
            k = stack.get(key, 0)
            stack[key] = k + 1
            yy = 0.78 + 0.3 * k
            L.append(r"\node[dot, fill=%s] at (%.3f,%.3f) {};" % (col[c], dd * SC, yy))
            L.append(r"\node[font=\tiny\bfseries, anchor=south, inner sep=1pt] at (%.3f,%.3f) {%d};"
                     % (dd * SC, yy + 0.08, i))
        L.append(r"\node[font=\tiny, text=sub, anchor=north east, inner sep=1pt] at (%.2f,0.35) {distance $d$};"
                 % W)
        return L

    leg = [r"\node[dot, fill=cA] at (0.1,0.12) {};", txt(0.22, 0.2, "versicolor", None, "note"),
           r"\node[dot, fill=cB] at (1.55,0.12) {};", txt(1.67, 0.2, "setosa", None, "note")]
    p1 = K.panel(T, fig, 1, "Distance to every tuple", ["DIST"], axis() + leg, W, Hh)
    k3 = d[:3]
    need(sec, "4.1", "Id 7, Id 5, Id 4")
    if [i for _, i, _ in k3] != [7, 5, 4]:
        sys.exit("4.1: the three nearest are not 7, 5, 4")
    p2 = K.panel(T, fig, 2, "Keep the 3 nearest", ["KNN"],
                 axis(hi=k3[-1][0]) + [txt(0, 0.22, r"$d_7 = %.3f,\ d_5 = %.3f,\ d_4 = %.3f$"
                                             % tuple(x[0] for x in k3), W)], W, Hh, key=True)
    v = Counter(c for _, _, c in k3)
    body = hbar(0, 1.2, 2.5, v["versicolor"] / 3, "cA", "versicolor %d" % v["versicolor"], h=0.26, bold=True) + \
        hbar(0, 0.8, 2.5, v["setosa"] / 3, "cB", "setosa %d" % v["setosa"], h=0.26) + \
        [txt(0, 0.45, r"\textbf{versicolor}, 3 of 3.", 3.5)]
    p3 = K.panel(T, fig, 3, "Vote", ["VOTE"], body, 3.5, Hh)
    return K.rows([p1, p2, p3])


# =====================================================================
#  Confusion matrices
# =====================================================================
MET = {
    # key: (label, numerator roles, denominator roles, chip)
    "acc": ("Accuracy", "TP TN", "TP TN FP FN", "DIAG"),
    "err": ("Error rate", "FP FN", "TP TN FP FN", "OFFD"),
    "tpr": ("TPR", "TP", "TP FN", "ACT"),
    "sens": ("Sensitivity", "TP", "TP FN", "ACT"),
    "rec": ("Sensitivity = recall", "TP", "TP FN", "ACT"),
    "spec": ("Specificity", "TN", "TN FP", "ACT"),
    "fpr": ("FPR", "FP", "FP TN", "ACT"),
    "prec": ("Precision", "TP", "TP FP", "PRED"),
}


def roles(m, rows_actual, pos):
    out = {}
    for i in range(2):
        for j in range(2):
            a, p = (i, j) if rows_actual else (j, i)
            out[(i, j)] = ("T" if a == p else "F") + ("P" if p == pos else "N")
    return out


def mini(x, y, m, rl, cl, rows_actual, pos, num=(), den=(), tags=False, title=None):
    """A 2x2 matrix as printed, at (x,y) = its top-left corner."""
    R = roles(m, rows_actual, pos)
    L = []
    cw, ch = 0.78, 0.40
    ox = x + 0.62
    if title:
        L.append(r"\node[font=\tiny\bfseries, text=ink, anchor=south west, inner sep=0pt] at (%.3f,%.3f) {%s};"
                 % (x, y + 0.28, title))
    L.append(r"\node[font=\tiny, text=sub, anchor=south, inner sep=0.5pt] at (%.3f,%.3f) {%s};"
             % (ox + cw, y + 0.27, "Actual" if not rows_actual else "Predicted"))
    for j in range(2):
        L.append(r"\node[hdr] at (%.3f,%.3f) {%s};" % (ox + cw * (j + 0.5), y + 0.12, cl[j]))
    for i in range(2):
        L.append(r"\node[hdr, anchor=east] at (%.3f,%.3f) {%s};" % (ox - 0.03, y - ch * (i + 0.5), rl[i]))
        for j in range(2):
            role = R[(i, j)]
            st = "hot" if role in num else "cell"
            extra = ", draw=acc, line width=0.9pt" if (role in den and role not in num) else ""
            lab = (r"{\tiny %s}\,%s" % (role, m[i][j])) if tags else str(m[i][j])
            L.append(r"\node[%s, minimum width=%.2fcm, minimum height=%.2fcm%s] at (%.3f,%.3f) {%s};"
                     % (st, cw - 0.04, ch - 0.04, extra, ox + cw * (j + 0.5), y - ch * (i + 0.5), lab))
    L.append(r"\node[font=\tiny, text=sub, rotate=90, anchor=south, inner sep=0.5pt] at (%.3f,%.3f) {%s};"
             % (x - 0.02, y - ch, "Actual" if rows_actual else "Pred."))
    return L


def cm_value(m, rows_actual, pos, key):
    R = roles(m, rows_actual, pos)
    v = {r: m[i][j] for (i, j), r in R.items()}
    _, nu, de, _ = MET[key]
    n = sum(v[r] for r in nu.split())
    d = sum(v[r] for r in de.split())
    return n, d, n / d if d else 0.0, v


def fig_cm(figname, sec, mats, metrics, per_row=4, lead=None):
    """mats: [(title, m, row labels, col labels, rows_actual, pos)]."""
    W = 3.35 if len(mats) == 1 else 4.9
    Hh = 2.3 if len(mats) == 1 else 2.45
    top = 1.25
    panels = []
    step = 1
    if lead:
        panels.append(lead(step))
        step += 1
    body = []
    xs = [0.12 + k * 2.45 for k in range(len(mats))]
    for (title, m, rl, cl, ra, pos), x in zip(mats, xs):
        body += mini(x, top, m, rl, cl, ra, pos, tags=True, title=title if len(mats) > 1 else None)
        _, _, _, v = cm_value(m, ra, pos, "acc")
        P, N = v["TP"] + v["FN"], v["FP"] + v["TN"]
        for sym, val in (("P", P), ("N", N)):
            if not re.search(r"(?<![A-Za-z])%s\s*=\s*(?:[\d+ ]+=\s*)?%d(?!\d)" % (sym, val), sec):
                sys.exit("%s: %s = %d is not printed" % (figname, sym, val))
        body.append(txt(x - 0.15, 0.30, r"rows \textbf{%s}: $P=%d,\ N=%d$" %
                        ("Actual" if ra else "Pred.", P, N), None, "note"))
    panels.append(K.panel(T, figname, step, "Read the axes", ["AXES"], body, W, Hh,
                          key=(lead is None)))
    step += 1
    for key in metrics:
        lab, nu, de, chip = MET[key]
        body = []
        vals = []
        for (title, m, rl, cl, ra, pos), x in zip(mats, xs):
            body += mini(x, top, m, rl, cl, ra, pos, num=nu.split(), den=de.split(),
                         title=title if len(mats) > 1 else None)
            n, d, val, _ = cm_value(m, ra, pos, key)
            s = "0" if n == 0 else printed(sec, val, "%s %s" % (figname, lab), 6e-4)
            vals.append(r"$%d/%d = \mathbf{%s}$" % (n, d, s))
        formula = {"acc": "(TP+TN)/all", "err": "(FP+FN)/all", "tpr": "TP/P", "sens": "TP/P",
                   "rec": "TP/P", "spec": "TN/N", "fpr": "FP/N", "prec": "TP/(TP+FP)"}[key]
        body.append(txt(0, 0.30, formula + r":\ \ " + r"\ \ \ ".join(vals), W))
        panels.append(K.panel(T, figname, step, lab, [chip], body, W, Hh))
        step += 1
    leg = (r"\tikz{\node[hot, minimum width=4mm, minimum height=3mm] {}; }\ numerator \quad"
           r"\tikz{\node[cell, draw=acc, line width=0.9pt, minimum width=4mm, minimum height=3mm] {};}"
           r"\ numerator $+$ these $=$ denominator")
    return K.grid(panels, per_row, legend=r"{\tiny\color{sub}" + leg + "}")


def fig_seq(sec):
    act = "A A B B B A A A B B".split()
    y = "A A A A B B A A A B".split()
    cat = []
    for a, p in zip(act, y):
        cat.append(("T" if a == p else "F") + ("P" if p == "A" else "N"))
    need(sec, "5.8", " & ".join(cat))
    W, Hh = 4.9, 2.45

    def lead(step):
        body = []
        colr = {"TP": "cC", "TN": "cA", "FP": "cB", "FN": "cD"}
        for i, (a, p, c) in enumerate(zip(act, y, cat)):
            x = 0.78 + i * 0.41
            body.append(r"\node[font=\tiny\bfseries] at (%.2f,1.62) {%s};" % (x, a))
            body.append(r"\node[font=\tiny\bfseries] at (%.2f,1.34) {%s};" % (x, p))
            body.append(r"\node[cell, minimum width=3.8mm, minimum height=3.4mm, fill=%sL, draw=%s,"
                        r" font=\tiny\bfseries] at (%.2f,1.02) {%s};" % (colr[c], colr[c], x, c))
        for lab, yy in (("Actual", 1.62), ("Y", 1.34), ("Y is", 1.02)):
            body.append(r"\node[font=\tiny, text=sub, anchor=east] at (0.58,%.2f) {%s};" % (yy, lab))
        cc = Counter(cat)
        body.append(txt(0, 0.72, r"Y: $TP=%d,\ FN=%d,\ FP=%d,\ TN=%d$.\\X matches Actual at every"
                                 r" position: $TP=5,\ TN=5$." % (cc["TP"], cc["FN"], cc["FP"], cc["TN"]),
                        W))
        return K.panel(T, "5.8", step, "Tally Y (A = positive)", ["TALLY"], body, W, Hh, key=True)

    mX = [[5, 0], [0, 5]]
    mY = [[4, 1], [3, 2]]
    mats = [("Classifier X", mX, ["A", "B"], ["A", "B"], True, 0),
            ("Classifier Y", mY, ["A", "B"], ["A", "B"], True, 0)]
    return fig_cm("5.8", sec, mats, ["acc", "prec", "tpr", "fpr"], per_row=3, lead=lead)


# =====================================================================
#  ANN
# =====================================================================
def net(hl_edges=(), hl_nodes=(), labels=None):
    P = {"x1": (0.2, 2.15), "x2": (0.2, 1.45), "x3": (0.2, 0.75), "h1": (1.65, 1.85),
         "h2": (1.65, 1.05), "o": (3.0, 1.45), "E": (4.0, 1.45)}
    L = []
    E = [("x%d" % i, "h%d" % j, "w_{%d%d}" % (j, i)) for i in (1, 2, 3) for j in (1, 2)] + \
        [("h1", "o", "u_1"), ("h2", "o", "u_2"), ("o", "E", "")]
    for a, b, w in E:
        hot = (a, b) in hl_edges
        L.append(r"\draw[%s] (%.2f,%.2f) -- (%.2f,%.2f);"
                 % ("mkc, line width=1.1pt" if hot else "ruleL, line width=0.5pt",
                    P[a][0], P[a][1], P[b][0], P[b][1]))
    for n, (x, y) in P.items():
        hot = n in hl_nodes
        shape = "rectangle, rounded corners=1pt" if n == "E" else "circle"
        L.append(r"\node[%s, draw=%s, fill=%s, line width=0.6pt, inner sep=1pt, minimum size=4.2mm,"
                 r" font=\tiny\bfseries] at (%.2f,%.2f) {$%s$};"
                 % (shape, "mkc" if hot else "acc", "mkL" if hot else "accL", x, y,
                    n.replace("1", "_1").replace("2", "_2").replace("3", "_3")))
    for (x, y, s) in (labels or []):
        L.append(r"\node[font=\tiny\bfseries, text=mkc, fill=white, inner sep=0.6pt] at (%.2f,%.2f) {%s};"
                 % (x, y, s))
    return L


def fig_ann(sec):
    fig, W, Hh = "6.1", 4.3, 3.0
    need(sec, "6.1", r"h_1 = \sigma\big(w_{11}x_1 + w_{12}x_2 + w_{13}x_3\big)",
         r"\frac{\partial E}{\partial o} = \mathbf{(o-t)}",
         r"(o-t)\;o(1-o)\;u_1\;h_1(1-h_1)\;x_2")
    p1 = K.panel(T, fig, 1, "(a) Activation at $h_1$", ["SUM", "SIG"],
                 net(hl_edges=[("x1", "h1"), ("x2", "h1"), ("x3", "h1")], hl_nodes=["h1"])
                 + [txt(0, 0.44, r"$h_1 = \sigma(w_{11}x_1 + w_{12}x_2 + w_{13}x_3)$", W)], W, Hh)
    p2 = K.panel(T, fig, 2, "(b) Gradient w.r.t. $o$", ["CHAIN"],
                 net(hl_edges=[("o", "E")], hl_nodes=["o", "E"], labels=[(3.5, 1.67, "$o-t$")])
                 + [txt(0, 0.44, r"$E = \tfrac12(o-t)^2 \Rightarrow \partial E/\partial o = (o-t)$", W)],
                 W, Hh)
    p3 = K.panel(T, fig, 3, "(c) Gradient w.r.t. $w_{12}$", ["CHAIN", "SIG"],
                 net(hl_edges=[("x2", "h1"), ("h1", "o"), ("o", "E")], hl_nodes=["x2", "h1", "o", "E"],
                     labels=[(0.9, 1.83, "$x_2$"), (1.65, 2.27, "$h_1(1{-}h_1)$"), (2.35, 1.85, "$u_1$"),
                             (3.0, 1.87, "$o(1{-}o)$"), (3.5, 1.24, "$o-t$")])
                 + [txt(0, 0.44, r"$(o-t)\,o(1-o)\,u_1\,h_1(1-h_1)\,x_2$: one factor per link on the path"
                                 r" from $E$ back to $w_{12}$", W)],
                 W, Hh, key=True)
    return K.grid([p1, p2, p3], 3)


# =====================================================================
#  Build
# =====================================================================
def build():
    tex = open(TEX, encoding="utf-8").read()
    S = lambda a, b=None: K.section(tex, a, b)
    figs = []

    s11 = S(r"\creamq{Problem 1.1}", r"\creamq{Problem 1.2}")
    rows = [tuple(x.strip().replace("\\_", "_") for x in ln.split("&"))
            for ln in re.findall(r"(?m)^((?:Youth|Middle\\_Aged|Senior)\s*&[^\n]*?)\\\\", s11)]
    rows = [r[:4] + (r[4].strip(),) for r in rows]
    if len(rows) != 14:
        sys.exit("1.1: expected 14 table rows, read %d" % len(rows))
    f, _ = tree_fig("1.1", rows, ["Age", "Income", "Student", "Credit\\_Rating"], ["Yes", "No"], s11,
                    show={"Middle_Aged": "Middle\\_Aged"})
    figs.append(("c3s_tree_11", f))
    CAPTION["c3s_tree_11"] = "The finished tree: buys\\_computer (rows numbered 1 to 14 top to bottom)"

    s12 = S(r"\creamq{Problem 1.2}", r"\creamq{Problem 1.3}")
    rows = [tuple(x.strip() for x in ln.split("&"))
            for ln in re.findall(r"(?m)^((?:Male|Female)\s*&[^\n]*?)\\\\", s12)]
    if len(rows) != 10:
        sys.exit("1.2: expected 10 rows, read %d" % len(rows))
    f, t = tree_fig("1.2", rows, ["Gender", "Car ownership", "Travel cost", "Income level"],
                    ["Bus", "Car", "Train"], s12)
    figs.append(("c3s_tree_12", f))
    CAPTION["c3s_tree_12"] = "The finished tree: transport mode (rows numbered 1 to 10 top to bottom)"

    s13 = S(r"\creamq{Problem 1.3}", r"\creamq{Problem 1.4")
    rows = []
    for ln in re.findall(r"(?m)^(\d+\s*&[^\n]*?)\\\\", s13):
        c = [x.strip() for x in ln.split("&")]
        inc = {"\\$0 to \\$15K": "\\$0--15K", "\\$15 to \\$35K": "\\$15--35K",
               "over \\$35K": "over \\$35K"}[c[4]]
        rows.append((c[1], c[2], c[3], inc, c[5]))
    if len(rows) != 14:
        sys.exit("1.3: expected 14 rows, read %d" % len(rows))
    f, _ = tree_fig("1.3", rows, ["Credit history", "Debt", "Collateral", "Income"],
                    ["high", "moderate", "low"], s13)
    figs.append(("c3s_tree_13", f))
    CAPTION["c3s_tree_13"] = "The finished tree: credit risk (rows are the table's SN)"

    s14 = S(r"\creamq{Problem 1.4", r"\T{M2.")
    figs.append(("c3s_step_14", fig_root14(s14)))
    CAPTION["c3s_step_14"] = "Step by step: the root node, and why it wins"

    figs.append(("c3s_step_gini", fig_gini(S(r"\T{M2.", r"\T{M3."))))
    CAPTION["c3s_step_gini"] = "Step by step: Gini on two candidate binary splits"

    figs.append(("c3s_step_31", fig_nb31(S(r"\creamq{Problem 3.1}", r"\creamq{Problem 3.2}"))))
    CAPTION["c3s_step_31"] = "Step by step: Naive Bayes for X = (youth, medium, yes, fair)"
    figs.append(("c3s_step_32", fig_nb32(S(r"\creamq{Problem 3.2}", r"\T{M4."))))
    CAPTION["c3s_step_32"] = "Step by step: a zero count, the Laplace fix and a Gaussian attribute"

    figs.append(("c3s_step_41", fig_knn(S(r"\creamq{Problem 4.1}", r"\T{M5."))))
    CAPTION["c3s_step_41"] = "Step by step: 3-NN on the flower"

    A, Pd = True, False
    cms = [
        ("5.1", r"\creamq{Problem 5.1}", r"\creamq{Problem 5.2}",
         [("", [[142, 40], [98, 720]], ["Pos", "Neg"], ["Pos", "Neg"], A, 0)],
         ["acc", "sens", "prec", "spec"], "rows Actual"),
        ("5.2", r"\creamq{Problem 5.2}", r"\creamq{Problems 5.3",
         [("", [[142, 40], [98, 720]], ["C1", "C2"], ["C1", "C2"], Pd, 0)],
         ["acc", "tpr", "fpr", "prec"], "rows Predicted"),
        ("5.3/5.4", r"\creamq{Problems 5.3", r"\creamq{Problem 5.5}",
         [("75 Ash", [[21, 6], [7, 41]], ["C1", "C2"], ["C1", "C2"], A, 0),
          ("72 Ch", [[21, 6], [7, 41]], ["C1", "C2"], ["C1", "C2"], Pd, 0)],
         ["acc", "rec", "spec", "prec"], "the same four numbers, both ways round"),
        ("5.5", r"\creamq{Problem 5.5}", r"\creamq{Problem 5.6}",
         [("", [[25, 9], [4, 31]], ["C1", "C2"], ["C1", "C2"], A, 0)],
         ["acc", "sens", "spec", "prec"], "rows Actual"),
        ("5.6", r"\creamq{Problem 5.6}", r"\creamq{Problem 5.7}",
         [("", [[1050, 250], [150, 950]], ["T", "F"], ["T", "F"], Pd, 0)],
         ["err", "sens", "fpr", "spec"], "rows Predicted"),
        ("5.7", r"\creamq{Problem 5.7}", r"\creamq{Problem 5.8}",
         [("", [[20, 5], [10, 40]], ["A", "B"], ["A", "B"], A, 0)],
         ["tpr", "fpr", "prec"], "A = Yes, rows Actual"),
        ("5.9", r"\creamq{Problem 5.9}", r"\creamq{Problem 5.10",
         [("", [[50, 10], [5, 100]], ["NO", "YES"], ["NO", "YES"], A, 1)],
         ["acc", "err", "rec", "spec", "prec"], "positive = YES, the second row and column"),
        ("5.10", r"\creamq{Problem 5.10", r"\T{M6.",
         [("rows Actual", [[100, 40], [60, 300]], ["+", "$-$"], ["+", "$-$"], A, 0),
          ("rows Predicted", [[100, 40], [60, 300]], ["+", "$-$"], ["+", "$-$"], Pd, 0)],
         ["tpr", "fpr", "acc"], "both readings of the mislabelled matrix"),
    ]
    for fig, a, b, mats, mets, what in cms:
        sec = S(a, b)
        name = "c3s_cm_" + fig.replace(".", "").replace("/", "_")
        figs.append((name, fig_cm(fig, sec, mats, mets, per_row=3 if len(mats) > 1 else 5)))
        CAPTION[name] = "Step by step: read the axes, then each metric's cells (%s)" % what
    figs.append(("c3s_cm_58", fig_seq(S(r"\creamq{Problem 5.8}", r"\creamq{Problem 5.9}"))))
    CAPTION["c3s_cm_58"] = "Step by step: tally, build both matrices, then each metric"

    figs.append(("c3s_step_61", fig_ann(S(r"\creamq{Problem 6.1}"))))
    CAPTION["c3s_step_61"] = "Step by step: forward to $h_1$, then back along one path"

    figs.insert(0, ("c3s_index", T.index()))
    return figs


def main():
    figs = build()
    if "--report" in sys.argv:
        for n, _ in figs:
            print("ok  %s" % n)
        return
    K.render([("pre", K.preamble(T))] + figs, TEX, PREFIX, CAPTION,
             scale={"c3s_index": 0.78, "c3s_tree_11": 1.4, "c3s_tree_12": 1.3, "c3s_tree_13": 1.4})


if __name__ == "__main__":
    main()
