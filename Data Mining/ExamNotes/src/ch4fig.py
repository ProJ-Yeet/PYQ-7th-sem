# -*- coding: utf-8 -*-
"""Draw the step-by-step solution under every chapter-4 numerical in ch4-num.tex.

Apriori: one panel per level. Every candidate is a box: kept (green, with its
count), failed on the count (grey), or pruned before counting (red dashed,
with the missing subset named). Rules: one bar per candidate rule against the
confidence threshold. FP-growth: the tree after every transaction with the
touched path in orange, then one mining panel per item with its node-links
and prefix paths lit. Lift, subsequences and subgraph joins as panels.

Every panel carries a TECHNIQUE chip naming its move; the decisive step is
framed KEY STEP; a technique index opens the chapter.

Exit test is replay. Apriori is rerun from the printed transactions and
every kept itemset must be printed with its count, every pruned candidate
named. The strong-rule count must equal the count the notes state. The
FP-tree is rebuilt from the reordered transactions the notes print, which
must themselves follow from the F-list; every conditional pattern base the
panels show must be printed. Lift, chi-square and the subsequence count are
recomputed.

    python ch4fig.py            regenerate every figure and its block in ch4-num.tex
    python ch4fig.py --report   run the checks only
"""
import itertools
import math
import os
import re
import sys
from collections import Counter

import stepkit as K
from stepkit import BS

TEX = os.path.join(K.HERE, "ch4-num.tex")
PREFIX = "ch4fig"

T = K.Techs([
    ("THR", "threshold to count", "Turn min support into a COUNT first: $\\lceil$ fraction $\\times N\\rceil$."),
    ("SCAN", "count and keep", "Count each candidate over ALL transactions; keep those $\\ge$ the min count."),
    ("JOIN", "join", "Join two frequent $(k{-}1)$-itemsets sharing their first $k{-}2$ items."),
    ("PRUNE", "prune", "Drop a candidate if any $(k{-}1)$-subset is not frequent. No scan needed."),
    ("STOP", "stop", "No candidates (or none survive): the run ends."),
    ("CONF", "confidence", "$\\sigma(l)/\\sigma(s)$: same numerator for every rule from $l$."),
    ("CUT", "threshold line", "A rule is strong when its confidence is $\\ge$ min\\_conf (equal counts)."),
    ("FLIST", "F-list", "Frequent items sorted by descending count, ties broken by a stated rule."),
    ("REORD", "reorder", "Rewrite each transaction in F-list order, dropping infrequent items."),
    ("SHARE", "share prefix", "A transaction that starts like an existing path increments its counts."),
    ("BRANCH", "new branch", "Where the prefix stops matching, a new child (or root child) is added."),
    ("LINKS", "node-links", "Follow the item's node-links to every node carrying it."),
    ("BASE", "prefix paths", "Each node's whole root path, tagged with THAT node's count: the pattern base."),
    ("CTREE", "conditional tree", "Add up the base per item, drop those below the min count, append the item."),
    ("LIFT", "lift", "$P(A\\cup B)/(P(A)P(B))$: below 1 is negative correlation, whatever the confidence."),
    ("CHI", "chi-square", "$\\sum (obs-exp)^2/exp$ over the contingency table."),
    ("SPLIT", "item splits", "Enumerate how many items come from each element, then choose them."),
    ("DEDUP", "remove duplicates", "The same sequence reached by two splits counts once."),
    ("ORDER", "keep element order", "Subsets of each element, in the original element order, never merged."),
    ("CORE", "common core", "Remove one edge from each parent so the rest is identical: the core."),
    ("ATTACH", "attach edges", "Add each parent's unique edge to the core at every legal vertex."),
    ("SYMM", "symmetry", "Placements that map onto each other by a symmetry are one candidate."),
])

CAPTION = {"c4s_index": "The moves every chapter-4 numerical below is built from"}


def txt(x, y, s, w=None, style="eqn"):
    if w:
        return r"\node[%s, text width=%.2fcm] at (%.3f,%.3f) {%s};" % (style, w, x, y, s)
    return r"\node[%s] at (%.3f,%.3f) {%s};" % (style, x, y, s)


# =====================================================================
#  Apriori
# =====================================================================
def apriori(D, minc, order=None):
    """Levels [(k, [(cand, count or None, status, why)])], status: keep/fail/pruned."""
    items = sorted({i for t in D for i in t}, key=order)
    key = order or (lambda x: x)

    def cnt(s):
        return sum(1 for t in D if set(s) <= t)

    levels = []
    L1 = []
    rows = []
    for i in items:
        c = cnt((i,))
        rows.append(((i,), c, "keep" if c >= minc else "fail", ""))
        if c >= minc:
            L1.append((i,))
    levels.append((1, rows))
    prev = L1
    k = 2
    while prev:
        cands = []
        for a, b in itertools.combinations(prev, 2):
            if a[:-1] == b[:-1]:
                cands.append(tuple(sorted(set(a) | set(b), key=key)))
        rows = []
        nxt = []
        ps = set(prev)
        for c in cands:
            miss = [s for s in itertools.combinations(c, k - 1) if s not in ps]
            if miss and k > 2:
                rows.append((c, None, "pruned", miss[0]))
                continue
            n = cnt(c)
            rows.append((c, n, "keep" if n >= minc else "fail", ""))
            if n >= minc:
                nxt.append(c)
        levels.append((k, rows))
        prev = nxt
        k += 1
    return levels


def name(s, sep=""):
    return sep.join(s)


def ap_check(sec, label, levels, fmt):
    for k, rows in levels:
        for c, n, st, why in rows:
            if st == "keep":
                K.need(sec, label, fmt(c, n))
            elif st == "pruned":
                K.need(sec, label, fmt(c, None))


def ap_figure(fig, sec, D, minc, fmt, short=None, thr=None, per=3, keylevel=None, W=5.4):
    """fmt(c, n) = how the notes print itemset c (n None: bare name)."""
    levels = apriori(D, minc)
    ap_check(sec, fig, levels, fmt)
    short = short or (lambda c: "".join(c))
    panels = []
    step = 1
    if thr:
        body = [txt(0, 1.3, thr, W)]
        panels.append(K.panel(T, fig, step, "Min support as a count", ["THR"], body, W, 1.9))
        step += 1
    if keylevel is None:
        keylevel = next((k for k, rows in levels if any(r[2] == "pruned" for r in rows)), None)
        if keylevel is None:
            keylevel = levels[-1][0]
    for k, rows in levels:
        bw = max(0.55, 0.16 * max(len(short(c)) for c, _, _, _ in rows) + 0.3) if rows else 0.6
        per_row = max(1, int((W - 0.05) // (bw + 0.08)))
        nrows = max(1, math.ceil(len(rows) / per_row))
        pr = [r for r in rows if r[2] == "pruned"]
        extra = 0.5 if pr else 0
        Hh = 0.62 + 0.3 + nrows * 0.46 + 0.32 + extra
        body = []
        top = Hh - 0.62 - 0.18
        for i, (c, n, st, why) in enumerate(rows):
            r, q = divmod(i, per_row)
            x = 0.02 + q * (bw + 0.08) + bw / 2
            y = top - r * 0.46
            if st == "keep":
                style = "draw=gd, fill=gdL, line width=0.6pt"
                lab = r"\textbf{%s}\,{\color{gd}%d}" % (short(c), n)
            elif st == "fail":
                style = "draw=ruleL, fill=rowL, text=sub"
                lab = r"%s\,%d" % (short(c), n)
            else:
                style = "draw=mkc, dashed, fill=white, text=mkc"
                lab = short(c)
            body.append(r"\node[%s, rounded corners=1.5pt, minimum width=%.2fcm, minimum height=0.34cm,"
                        r" inner sep=1pt, font=\tiny] at (%.3f,%.3f) {%s};" % (style, bw, x, y, lab))
        keep = [c for c, n, st, _ in rows if st == "keep"]
        if not rows:
            summary = r"$C_%d = \emptyset$: no two itemsets share a prefix." % k
        elif keep:
            summary = r"$L_%d$: %d kept of %d" % (k, len(keep), len(rows))
        else:
            summary = r"$L_%d = \emptyset$: \textbf{nothing survives}" % k
        if pr:
            body.append(txt(0, 0.78, r"pruned (dashed): " + ", ".join(
                r"%s ($%s\notin L_%d$)" % (short(c), short(w), k - 1) for c, _, _, w in pr[:4])
                + (r", \dots" if len(pr) > 4 else ""), W, "note"))
        body.append(txt(0, 0.26, summary, W))
        tech = ["SCAN"] if k == 1 else ["JOIN"] if not rows else (["JOIN", "PRUNE", "SCAN"] if pr else ["JOIN", "SCAN"])
        if not keep:
            tech.append("STOP")
        title = (r"$C_1 \rightarrow L_1$, min count %d" % minc) if k == 1 else r"$C_%d \rightarrow L_%d$" % (k, k)
        panels.append(K.panel(T, fig, step, title, tech, body, W, Hh, key=(k == keylevel)))
        step += 1
        if keep and not any(True for kk, _ in levels if kk == k + 1):
            pass
    # a closing stop panel when the last level produced survivors but no candidates follow
    if levels[-1][1] and any(r[2] == "keep" for r in levels[-1][1]):
        k = levels[-1][0] + 1
        body = [txt(0, 0.62, r"$C_%d = \emptyset$: fewer than two $L_%d$ itemsets share a prefix."
                    % (k, k - 1), W)]
        panels.append(K.panel(T, fig, step, "Stop", ["STOP"], body, W, 1.4))
    return panels, levels


def rules_panel(fig, step, sec, D, itemsets, minconf, expect, phrase, short=None, W=None, key=False,
                title=None, form=None):
    """Bars of confidence for every rule out of the given frequent itemsets."""
    short = short or (lambda c: "".join(c))

    def cnt(s):
        return sum(1 for t in D if set(s) <= t)

    rows = []
    for l in itemsets:
        sl = cnt(l)
        for r in range(1, len(l)):
            for s in itertools.combinations(l, r):
                if form and not form(s, l):
                    continue
                rest = tuple(x for x in l if x not in s)
                rows.append((short(s), short(rest), sl / cnt(s), sl, cnt(s)))
    strong = sum(1 for r in rows if r[2] >= minconf - 1e-9)
    if strong != expect:
        sys.exit("%s: %d strong rules, notes say %d" % (fig, strong, expect))
    K.need(sec, fig, phrase)
    n = len(rows)
    cols = 1 if n <= 8 else 2
    per = math.ceil(n / cols)
    W = W or (4.6 if cols == 1 else 9.0)
    cw = W / cols
    lab_w = 1.55 if max(len(a) + len(b) for a, b, _, _, _ in rows) < 12 else 2.1
    barw = cw - lab_w - 0.75
    Hh = 0.62 + 0.25 + per * 0.24 + 0.45
    body = []
    top = Hh - 0.62 - 0.2
    for i, (a, b, c, sl, ss) in enumerate(rows):
        q, r = divmod(i, per)
        x0 = q * cw
        y = top - r * 0.24
        ok = c >= minconf - 1e-9
        body.append(r"\node[font=\tiny, anchor=east, inner sep=0.5pt] at (%.3f,%.3f) {%s$\Rightarrow$%s};"
                    % (x0 + lab_w, y, a, b))
        body.append(r"\fill[%s] (%.3f,%.3f) rectangle (%.3f,%.3f);"
                    % ("gd!70" if ok else "sub!35", x0 + lab_w + 0.05, y - 0.08, x0 + lab_w + 0.05 + barw * c, y + 0.08))
        body.append(r"\node[font=\tiny%s, anchor=west, inner sep=0.5pt] at (%.3f,%.3f) {%d/%d};"
                    % (r"\bfseries" if ok else "", x0 + lab_w + 0.1 + barw, y, sl, ss))
    for q in range(cols):
        xc = q * cw + lab_w + 0.05 + barw * minconf
        body.append(r"\draw[mkc, dashed, line width=0.6pt] (%.3f,%.3f) -- (%.3f,%.3f);"
                    % (xc, top + 0.16, xc, top - (per - 1) * 0.24 - 0.14))
    body.append(r"\node[font=\tiny\bfseries, text=mkc, anchor=south] at (%.3f,%.3f) {min conf %s};"
                % (lab_w + 0.05 + barw * minconf, top + 0.14, ("%.3f" % minconf).rstrip("0").rstrip(".")))
    body.append(txt(0, 0.3, r"\textbf{%d strong} of %d candidate rules (green)." % (strong, n), W))
    return K.panel(T, fig, step, title or "Every rule against min conf", ["CONF", "CUT"], body, W, Hh, key=key)


# =====================================================================
#  FP-tree
# =====================================================================
class Node(object):
    def __init__(self, item, parent):
        self.item, self.parent, self.count, self.kids = item, parent, 0, []

    def child(self, item):
        for k in self.kids:
            if k.item == item:
                return k
        return None


def fp_build(trans, upto=None):
    root = Node(None, None)
    touched = []
    for t in trans[:upto]:
        cur = root
        path = []
        for it in t:
            nx = cur.child(it)
            if nx is None:
                nx = Node(it, cur)
                cur.kids.append(nx)
            nx.count += 1
            path.append(nx)
            cur = nx
        touched = path
    return root, touched


def leaves(n):
    return 1 if not n.kids else sum(leaves(k) for k in n.kids)


def fp_layout(n, depth, cur, sx, sy):
    n.y = -depth * sy
    if not n.kids:
        n.x = cur[0] * sx
        cur[0] += 1
        return
    for k in n.kids:
        fp_layout(k, depth + 1, cur, sx, sy)
    n.x = (n.kids[0].x + n.kids[-1].x) / 2


def fp_tikz(root, hot=(), lit=(), sx=0.62, sy=0.5, ox=0.0, oy=0.0, abbr=None):
    """TikZ lines for a tree; hot nodes orange (touched), lit nodes blue (node-links)."""
    abbr = abbr or {}
    fp_layout(root, 0, [0], sx, sy)
    L = []

    def walk(n):
        for k in n.kids:
            e = "mkc, line width=0.9pt" if (k in hot) else "sub!70, line width=0.5pt"
            L.append(r"\draw[%s] (%.3f,%.3f) -- (%.3f,%.3f);" % (e, ox + n.x, oy + n.y - 0.1, ox + k.x, oy + k.y + 0.1))
            walk(k)

    walk(root)

    def nodes(n):
        if n.item is None:
            st = "draw=sub, fill=white, text=sub"
            lab = "root"
        else:
            st = ("draw=mkc, fill=mkL, line width=0.7pt" if n in hot else
                  "draw=acc, fill=accL, line width=0.7pt" if n in lit else "draw=sub!60, fill=white")
            lab = "%s:%d" % (abbr.get(n.item, n.item), n.count)
        L.append(r"\node[%s, rounded corners=1.5pt, inner sep=1pt, minimum height=0.3cm, font=\tiny]"
                 r" at (%.3f,%.3f) {%s};" % (st, ox + n.x, oy + n.y, lab))
        for k in n.kids:
            nodes(k)

    nodes(root)
    return L, leaves(root)


def depth(n):
    return 0 if not n.kids else 1 + max(depth(k) for k in n.kids)


def fp_evolution(fig, sec, trans, names, reord_fmt, abbr=None, per=3):
    """One panel per transaction: the tree after it, the touched path in orange."""
    for tid, t in zip(names, trans):
        K.need(sec, fig, reord_fmt(tid, t))
    panels = []
    final, _ = fp_build(trans)
    sx = 0.62
    W = max(3.2, leaves(final) * sx + 0.3)
    Hh = 0.62 + 0.25 + (depth(final) + 1) * 0.5 + 0.35
    for i, (tid, t) in enumerate(zip(names, trans), 1):
        root, touched = fp_build(trans, i)
        prev, _ = fp_build(trans, i - 1)
        # new branch if the transaction created any node
        created = sum(1 for n in touched if n.count == 1)
        tech = ["BRANCH"] if created else ["SHARE"]
        if created and created < len(t):
            tech = ["SHARE", "BRANCH"]
        L, _ = fp_tikz(root, hot=set(touched), sx=sx, ox=0.15 + 0.0, oy=Hh - 0.62 - 0.35, abbr=abbr)
        L.append(txt(0, 0.28, "%s: %s" % (tid, ", ".join(abbr.get(x, x) if abbr else x for x in t)), W, "note"))
        panels.append(K.panel(T, fig, i, "After %s" % tid, tech, L, W, Hh, key=False))
    return panels, final


def cond_base(root, item):
    """[(path items, count)] for every node labelled item."""
    out = []

    def walk(n):
        for k in n.kids:
            if k.item == item:
                p = []
                a = k.parent
                while a.item is not None:
                    p.append(a.item)
                    a = a.parent
                out.append((list(reversed(p)), k.count, k))
            walk(k)

    walk(root)
    return out


def fp_mining(fig, sec, final, flist, minc, base_fmt, abbr=None, start=1, keyitem=None, extra=None):
    panels = []
    sx = 0.62
    W = max(4.6, leaves(final) * sx + 0.3)
    Hh = 0.62 + 0.25 + (depth(final) + 1) * 0.5 + 0.95
    for j, it in enumerate(reversed(flist)):
        base = cond_base(final, it)
        nodes_it = [b[2] for b in base]
        onpath = set()
        for _, _, n in base:
            a = n.parent
            while a.item is not None:
                onpath.add(a)
                a = a.parent
        txt_base = [base_fmt(p, c) for p, c, _ in base if p]
        for s in txt_base:
            K.need(sec, fig + " " + it, s)
        tot = Counter()
        for p, c, _ in base:
            for x in p:
                tot[x] += c
        keep = [x for x in flist if tot[x] >= minc]
        L, _ = fp_tikz(final, hot=set(nodes_it), lit=onpath, sx=sx, ox=0.15, oy=Hh - 0.62 - 0.35, abbr=abbr)
        a = (abbr or {}).get
        bs = "; ".join(r"\{%s\}:%d" % (",".join(a(x, x) for x in p), c) for p, c, _ in base if p) or "none"
        tt = ", ".join("%s:%d" % (a(x, x), tot[x]) for x in flist if tot[x]) or "--"
        kp = ", ".join("%s:%d" % (a(x, x), tot[x]) for x in keep) or r"\textbf{nothing}"
        L.append(txt(0, 0.95, r"base: %s" % bs, W, "note"))
        L.append(txt(0, 0.62, r"totals: %s $\rightarrow$ keep %s" % (tt, kp), W, "note"))
        panels.append(K.panel(T, fig, start + j, "Mine %s" % a(it, it),
                              ["LINKS", "BASE", "CTREE"], L, W, Hh, key=(it == keyitem)))
    return panels


# =====================================================================
#  Build
# =====================================================================
def arrange(p, r=None, per=3):
    rows = [p[i:i + per] for i in range(0, len(p), per)]
    if r is not None:
        rows.append([r])
    return K.rows(*rows)


def sets(lines):
    return [set(x.strip() for x in re.split(r"[,\s]+", l) if x.strip()) for l in lines]


def build():
    tex = open(TEX, encoding="utf-8").read()
    S = lambda a, b=None: K.section(tex, a, b)
    figs = []

    def add(name, cap, fig):
        CAPTION[name] = cap
        figs.append((name, fig))

    comma = lambda c, n: ("%s(%d)" % ("".join(c), n)) if n is not None else "".join(c)

    # ---- 1.1
    s = S(r"\creamq{Problem 1.1}", r"\creamq{Problem 1.2}")
    D = sets(["F A C D G I M P N", "A B C D F L M O P", "B F H V J O P", "B C K S A V",
              "L A F C E P M N V", "I B A P S M", "F A C I B P"])
    p, lv = ap_figure("1.1", s, D, 4, comma, per=3)
    top = [c for k, rows in lv for c, n, st, _ in rows if st == "keep" and k == max(kk for kk, _ in lv)]
    r = rules_panel("1.1", len(p) + 1, s, D, [("A", "C", "F", "P")], 0.8, 12, "12 of the 14 rules are strong")
    add("c4s_ap_11", "Step by step: Apriori level by level, then the 14 rules", arrange(p, r))

    # ---- 1.2
    s = S(r"\creamq{Problem 1.2}", r"\creamq{Problem 1.3}")
    D = sets(["A C D", "B C E", "A B C E", "B E"])
    p, _ = ap_figure("1.2", s, D, 2, comma)
    add("c4s_ap_12", "Step by step: Apriori level by level", arrange(p))

    # ---- 1.3
    s = S(r"\creamq{Problem 1.3}", r"\creamq{Problems 1.4")
    D = [set(x) for x in ["ACD", "BD", "ABCE", "BDF"]]
    p, _ = ap_figure("1.3", s, D, 2, lambda c, n: comma(c, n) if n is not None else "".join(c),
                     thr=r"4 transactions $\times$ 50\% $= $ \textbf{2}")
    add("c4s_ap_13", "Step by step: Apriori level by level", arrange(p))

    # ---- 1.4 / 1.5
    s = S(r"\creamq{Problems 1.4", r"\creamq{Problem 1.6}")
    D = sets(["M1 M2 M5", "M2 M4", "M2 M3", "M1 M2 M4", "M1 M3", "M2 M3", "M1 M3", "M1 M2 M3 M5",
              "M1 M2 M3"])
    fmt14 = lambda c, n: ("%s & T" % c[0]) if len(c) == 1 else comma(c, n)
    p, lv = ap_figure("1.4/1.5", s, D, 2, fmt14, thr=r"$2/9$ of 9 $=$ \textbf{2}; \ 20\% of 9 $= 1.8 \rightarrow$ \textbf{2}")
    add("c4s_ap_14", "Step by step: Apriori level by level (both papers)", arrange(p))
    freq = [c for k, rows in lv for c, n, st, _ in rows if st == "keep" and k >= 2]
    three = [c for c in freq if len(c) == 3]
    r14 = rules_panel("1.4", 1, s, D, three, 7 / 9, 2, "2 strong rules", title=r"1.4: $X \wedge Y \Rightarrow Z$ only",
                      short=lambda c: r"$\wedge$".join(c), form=lambda s_, l: len(s_) == 2, key=True)
    r15 = rules_panel("1.5", 2, s, D, freq, 0.8, 6, "6 strong rules", title="1.5: all 24 rules",
                      short=lambda c: r"$\wedge$".join(c))
    add("c4s_rules_14", "Step by step: the rules for each paper's threshold", K.grid([r14, r15], 2))

    # ---- 1.6
    s = S(r"\creamq{Problem 1.6}", r"\creamq{Problem 1.7}")
    D = sets(["A B", "A D", "A C", "B E", "B D E", "A E C"])
    p, _ = ap_figure("1.6", s, D, 3, comma, thr=r"6 transactions $\times$ 50\% $=$ \textbf{3}", keylevel=2)
    r = rules_panel("1.6", len(p) + 1, s, D, [("A", "C"), ("B", "E")], 0.8, 1, "One rule survives",
                         title="Relaxed to count 2: the rules")
    add("c4s_ap_16", "Step by step: nothing frequent at 50\\%, then the relaxed run", arrange(p, r))

    # ---- 1.7
    s = S(r"\creamq{Problem 1.7}", r"\creamq{Problem 1.8}")
    D = sets(["A B C D E F", "B C D E F G", "A D E H", "A D F I J", "B D E K"])
    p, lv = ap_figure("1.7", s, D, 3, comma, thr=r"5 transactions $\times$ 60\% $=$ \textbf{3}")
    freq = [c for k, rows in lv for c, n, st, _ in rows if st == "keep" and k >= 2]
    r = rules_panel("1.7", len(p) + 1, s, D, freq, 0.8, 9, "9 strong rules")
    add("c4s_ap_17", "Step by step: Apriori level by level, then the 16 rules", arrange(p, r))

    # ---- 1.8
    s = S(r"\creamq{Problem 1.8}", r"\creamq{Problem 1.9}")
    D = sets(["MILK BREAD CAKE", "BUTTER BREAD EGG", "MILK BUTTER BREAD EGG", "BUTTER EGG"])
    ab = {"MILK": "MI", "BREAD": "BR", "BUTTER": "BU", "EGG": "EG", "CAKE": "CA"}
    sh = lambda c: ",".join(ab[x] for x in c)

    def f18(c, n):
        if len(c) == 1:
            return "%s(%d)" % (c[0], n)
        if n is None:
            return ", ".join(c)
        if len(c) == 2:
            tids = ", ".join(str(i + 1) for i, t in enumerate(D) if set(c) <= t)
            return "%s & %s & %d" % (", ".join(c), tids, n)
        return ", ".join(c)
    p, lv = ap_figure("1.8", s, D, 2, f18, short=sh, thr=r"4 transactions $\times$ 50\% $=$ \textbf{2}")
    freq = [c for k, rows in lv for c, n, st, _ in rows if st == "keep" and k >= 2]
    r = rules_panel("1.8", len(p) + 1, s, D, freq, 0.65, 14, "All 14 rules are strong", short=sh)
    add("c4s_ap_18", "Step by step: Apriori level by level, then the 14 rules", arrange(p, r))

    # ---- 1.9
    s = S(r"\creamq{Problem 1.9}", r"\creamq{Problem 1.10}")
    D = sets(["A B C", "A C", "A D", "B E F"])
    p, lv = ap_figure("1.9", s, D, 2, comma, thr=r"50\% of 4 $=$ \textbf{2}; \ min conf $= 0.50$", keylevel=2)
    r = rules_panel("1.9", len(p) + 1, s, D, [("A", "C")], 0.5, 2, "Both are strong")
    add("c4s_ap_19", "Step by step: Apriori level by level, then the two rules", arrange(p, r))

    # ---- 1.10
    s = S(r"\creamq{Problem 1.10}", r"\T{M2.")
    rows = {"T2": "A2 A4 A8", "T3": "A4 A5 A7", "T4": "A3", "T5": "A5 A6 A7", "T6": "A2 A3 A4",
            "T7": "A2 A6 A7 A9", "T8": "A5"}
    D = sets(list(rows.values()))

    def f110(c, n):
        if len(c) == 1:
            return c[0]
        if n is None:
            return ",".join(c)
        return r"\text{%s}(%d)" % ("".join(c), n)
    p, lv = ap_figure("1.10", s, D, 2, f110, short=lambda c: ",".join(c),
                      thr=r"20\% of 7 $= 1.4$, a count cannot be fractional $\rightarrow$ \textbf{2}", keylevel=3)
    freq = [c for k, rows_ in lv for c, n, st, _ in rows_ if st == "keep" and k >= 2]
    r = rules_panel("1.10", len(p) + 1, s, D, freq, 0.0, 6, "6 rules in total", short=lambda c: ",".join(c),
                         title="(b) Every rule, at any threshold")
    add("c4s_ap_110", "Step by step: Apriori level by level, then (b) the six rules", arrange(p, r))

    # ---- M2 worked example
    s = S(r"\creamq{Worked example}", r"\T{M3.")
    D = sets(["M O N K E Y", "D O N K E Y", "M A K E", "M U C K Y", "C O K I E"])
    add("c4s_rules_m2", "Step by step: the six rules from {K, E, O}",
        K.single(rules_panel("M2", 1, s, D, [("K", "E", "O")], 0.8, 3,
                             "Every rule with \\textbf{O} in the antecedent succeeds",
                             short=lambda c: ",".join(c), key=True)))

    # ---- FP 3.1
    s = S(r"\creamq{Problem 3.1}", r"\creamq{Problem 3.2}")
    fl = ["K", "E", "M", "O", "Y"]
    D = sets(["M O N K E Y", "D O N K E Y", "M A K E", "M U C K Y", "C O K I E"])
    cnt = Counter(i for t in D for i in t)
    if [x for x in sorted((i for i in cnt if cnt[i] >= 3), key=lambda i: (-cnt[i], i))] != fl:
        sys.exit("3.1 F-list")
    tr = [[x for x in fl if x in t] for t in D]
    names = ["T100", "T200", "T300", "T400", "T500"]
    ev, final = fp_evolution("3.1", s, tr, names,
                             lambda tid, t: r"%s $\rightarrow$ %s" % (tid, ", ".join(t)))
    mine = fp_mining("3.1", s, final, fl, 3, lambda p_, c: r"\{%s\}:%d" % (",".join(p_), c),
                     start=1, keyitem="Y")
    add("c4s_fp_31", "Step by step: the FP-tree after each transaction", K.grid(ev, 5))
    add("c4s_mine_31", "Step by step: mining each item, least frequent first", K.grid(mine, 3))
    freq31 = [("K", "E"), ("K", "M"), ("K", "O"), ("E", "O"), ("K", "Y"), ("K", "E", "O")]
    add("c4s_rules_31", "Step by step: the 16 rules against 80\\%",
        K.single(rules_panel("3.1", 1, s, D, freq31, 0.8, 9, "9 strong", short=lambda c: ",".join(c))))

    # ---- FP 3.2
    s = S(r"\creamq{Problem 3.2}", r"\creamq{Problem 3.3}")
    fl = ["f", "c", "a", "b", "m", "p"]
    D = sets(["f a c d g i m p", "a b c f l m o", "b f h j o w", "b c k s p", "a f c e l p m n"])
    cnt = Counter(i for t in D for i in t)
    if sorted(fl, key=lambda i: -cnt[i]) != fl or any(cnt[i] >= 3 for i in cnt if i not in fl):
        sys.exit("3.2 F-list")
    tr = [[x for x in fl if x in t] for t in D]
    ev, final = fp_evolution("3.2", s, tr, ["01", "02", "03", "04", "05"],
                             lambda tid, t: r"%s $\rightarrow$ %s" % (tid, ", ".join(t)))
    add("c4s_fp_32", "Step by step: the FP-tree after each transaction", K.grid(ev, 5))

    # ---- FP 3.3
    s = S(r"\creamq{Problem 3.3}", r"\creamq{Problem 3.4}")
    ab = {"Chips": "Ch", "HotDogs": "H", "Coke": "Co", "Buns": "Bu", "Ketchup": "Ke"}
    fl = ["Chips", "HotDogs", "Coke", "Buns", "Ketchup"]
    D = sets(["HotDogs Buns Ketchup", "HotDogs Buns", "HotDogs Coke Chips", "Chips Coke", "Chips Ketchup",
              "HotDogs Coke Chips"])
    cnt = Counter(i for t in D for i in t)
    if sorted(fl, key=lambda i: (-cnt[i], i)) != fl:
        sys.exit("3.3 F-list")
    tr = [[x for x in fl if x in t] for t in D]
    names = ["T%d" % i for i in range(1, 7)]
    ev, final = fp_evolution("3.3", s, tr, names,
                             lambda tid, t: r"%s & %s" % (tid, ", ".join(ab[x] for x in t)), abbr=ab)
    ev = [e for e in ev]
    mine = fp_mining("3.3", s, final, fl, 2,
                     lambda p_, c: r"\{%s\}:%d" % (", ".join(ab[x] for x in p_), c), abbr=ab, keyitem="Coke")
    add("c4s_fp_33", "Step by step: the FP-tree after each transaction (orange = the path it touches)",
        K.grid(ev, 3))
    add("c4s_mine_33", "Step by step: mining each item, least frequent first", K.grid(mine, 3))

    # ---- FP 3.4
    s = S(r"\creamq{Problem 3.4}", r"\T{M4.")
    ab = {"Earphone": "E", "Laptop": "L", "Mobile": "Mo", "Camera": "Ca", "Pen drive": "Pd"}
    fl = ["Earphone", "Laptop", "Mobile", "Camera", "Pen drive"]
    raw = [["Camera", "Laptop", "Pen drive"], ["Laptop", "Pen drive"], ["Laptop", "Mobile", "Earphone"],
           ["Earphone", "Mobile"], ["Camera", "Earphone"], ["Laptop", "Mobile", "Earphone"]]
    cnt = Counter(i for t in raw for i in t)
    if sorted(fl, key=lambda i: (-cnt[i], i)) != fl:
        sys.exit("3.4 F-list")
    tr = [[x for x in fl if x in t] for t in raw]
    ev, final = fp_evolution("3.4", s, tr, names,
                             lambda tid, t: r"& %s \\" % ", ".join(ab[x] for x in t), abbr=ab)
    add("c4s_fp_34", "Step by step: the FP-tree after each transaction (orange = the path it touches)",
        K.grid(ev, 3))

    # ---- 4.1 lift
    s = S(r"\creamq{Problem 4.1}", r"\T{M5.")
    N, g, v, gv = 10000, 6000, 7500, 4000
    lift = (gv / N) / ((g / N) * (v / N))
    obs = [[gv, v - gv], [g - gv, N - g - v + gv]]
    exp = [[g * v / N, (N - g) * v / N], [g * (N - v) / N, (N - g) * (N - v) / N]]
    chi = sum((obs[i][j] - exp[i][j]) ** 2 / exp[i][j] for i in range(2) for j in range(2))
    K.need(s, "4.1", r"\mathbf{0.89}", r"\mathbf{555.6}", r"\mathbf{66.7\%}", r"\mathbf{75\%}")
    if abs(lift - 0.8889) > 1e-4 or abs(chi - 555.56) > 0.01:
        sys.exit("4.1")
    W = 4.1
    p1 = K.panel(T, "4.1", 1, "Support and confidence pass", ["CONF"],
                 [txt(0, 1.5, r"sup $= 4000/10000 = \mathbf{40\%}$ (over 30\%)", W),
                  txt(0, 1.15, r"conf $= 4000/6000 = \mathbf{66.7\%}$ (over 60\%)", W),
                  txt(0, 0.7, r"By these two measures the rule \textit{game $\Rightarrow$ video} is strong.", W,
                      "note")], W, 2.3)
    body = [r"\fill[cAL, draw=cA] (0.1,1.2) rectangle (%.3f,1.45);" % (0.1 + 3.6 * 0.75),
            r"\node[font=\tiny\bfseries, text=cA] at (1.45,1.325) {P(video) 75\%};",
            r"\fill[cBL, draw=cB] (0.1,0.8) rectangle (%.3f,1.05);" % (0.1 + 3.6 * 0.667),
            r"\node[font=\tiny\bfseries, text=cB] at (1.3,0.925) {P(video$|$game) 66.7\%};",
            txt(0, 0.6, r"Buying a game \textbf{lowers} the chance of a video.", W, "note")]
    p2 = K.panel(T, "4.1", 2, "Compare with the base rate", ["CONF"], body, W, 2.3)
    p3 = K.panel(T, "4.1", 3, "Lift", ["LIFT"],
                 [txt(0, 1.5, r"$\dfrac{0.40}{0.60 \times 0.75} = \dfrac{0.40}{0.45} = \mathbf{0.89}$", W),
                  txt(0, 0.8, r"$< 1$: \textbf{negatively} correlated, despite 66.7\% confidence.", W)],
                 W, 2.3, key=True)
    body = []
    for i, rl in enumerate(["video", r"$\overline{\text{video}}$"]):
        body.append(r"\node[hdr, anchor=east] at (0.95,%.2f) {%s};" % (1.3 - 0.4 * i, rl))
        for j in range(2):
            hot = i == 0 and j == 0
            body.append(r"\node[%s, minimum width=1.3cm, minimum height=0.34cm, font=\tiny] at (%.2f,%.2f)"
                        r" {%d \textit{(%d)}};" % ("hot" if hot else "cell", 1.65 + 1.35 * j, 1.3 - 0.4 * i,
                                                   obs[i][j], exp[i][j]))
    for j, cl in enumerate(["game", r"$\overline{\text{game}}$"]):
        body.append(r"\node[hdr] at (%.2f,1.6) {%s};" % (1.65 + 1.35 * j, cl))
    body.append(txt(0, 0.62, r"obs \textit{(exp)}; $\chi^2 = 55.6 + 83.3 + 166.7 + 250 = \mathbf{555.6}$;"
                             r" obs $<$ exp for both: negative.", W))
    p4 = K.panel(T, "4.1", 4, "Chi-square", ["CHI"], body, W, 2.3)
    add("c4s_step_41", "Step by step: why a 66.7\\% rule is misleading", K.grid([p1, p2, p3, p4], 4))

    # ---- 5.1 subsequences
    s = S(r"\creamq{Problem 5.1}", r"\creamq{Problem 5.2}")
    E = [(1, 3), (2,), (2, 3), (4,)]
    seen, sel, splits = set(), 0, []
    for split in itertools.product(*[range(len(e) + 1) for e in E]):
        if sum(split) != 4:
            continue
        ways = [list(itertools.combinations(e, k)) for e, k in zip(E, split)]
        prod = list(itertools.product(*ways))
        splits.append((split, len(prod)))
        for choice in prod:
            sel += 1
            seen.add(tuple(c for c in choice if c))
    if sel != 15 or len(seen) != 14:
        sys.exit("5.1: %d selections, %d distinct" % (sel, len(seen)))
    K.need(s, "5.1", r"2+1+1+2+2+4+2+1 = \mathbf{15}", r"\textbf{14 distinct 4-subsequences}")
    splits.sort(key=lambda t: t[0], reverse=True)
    W = 5.6
    body = [r"\node[font=\tiny, text=sub] at (%.2f,1.9) {$e_%d$ $\{%s\}$};" % (0.45 + 0.75 * i, i + 1,
                                                                            ",".join(map(str, e)))
            for i, e in enumerate(E)]
    body.append(r"\node[font=\tiny, text=sub] at (3.55,1.9) {ways};")
    for r, (sp, w) in enumerate(splits):
        y = 1.62 - r * 0.19
        for i, k in enumerate(sp):
            body.append(r"\node[font=\tiny%s] at (%.2f,%.2f) {%d};" % (r"\bfseries" if k else r"\color{sub!60}",
                                                                     0.45 + 0.75 * i, y, k))
        body.append(r"\node[font=\tiny\bfseries, text=acc] at (3.55,%.2f) {%d};" % (y, w))
    body.append(txt(3.95, 1.5, r"$\binom{2}{a}\binom{1}{b}\binom{2}{c}\binom{1}{d}$ per split;"
                               r" total \textbf{15}", 1.6, "note"))
    p1 = K.panel(T, "5.1", 1, "Splits $(a,b,c,d)$ summing to 4", ["SPLIT"], body, W, 2.75)
    body = [txt(0, 1.9, r"$\langle\{1,3\}\{2\}\{4\}\rangle$ arises twice:", W),
            txt(0, 1.55, r"$(2,1,0,1)$: the 2 from $e_2$ \quad $(2,0,1,1)$: the 2 from $e_3$", W),
            txt(0, 1.1, r"$e_2$ and $e_3$ share the item 2, so the same sequence is reached twice.", W,
                "note"),
            txt(0, 0.6, r"$15 - 1 = $ \textbf{14 distinct} 4-subsequences.", W)]
    p2 = K.panel(T, "5.1", 2, "Remove the duplicate", ["DEDUP"], body, W, 2.75, key=True)
    add("c4s_step_51", "Step by step: enumerate by split, then remove the duplicate", K.grid([p1, p2], 2))

    # ---- 5.2
    s = S(r"\creamq{Problem 5.2}", r"\T{M6.")
    E = [(2, 3, 5), (6, 7, 8), (9, 1), (7, 4)]
    ex = [[(2,), (6,), (), ()], [(3, 5), (7,), (9,), ()], [(2, 3), (6, 7), (1,), (4,)],
          [(5,), (8,), (9, 1), (7,)]]
    for e in ex:
        K.need(s, "5.2", r"\langle" + "".join(r"\{%s\}" % ",".join(map(str, x)) for x in e if x) + r"\rangle")
    W = 8.2
    body = []
    for r, e in enumerate(ex):
        y = 1.7 - r * 0.36
        x = 0.1
        for el, pick in zip(E, e):
            for it in el:
                on = it in pick
                body.append(r"\node[cell, minimum width=0.3cm, minimum height=0.26cm, font=\tiny%s] at (%.2f,%.2f) {%d};"
                            % (r"\bfseries, fill=gdL, draw=gd" if on else r", text=sub!50", x + 0.16, y, it))
                x += 0.32
            x += 0.18
        body.append(txt(x + 0.1, y + 0.1, r"$\langle" + "".join(r"\{%s\}" % ",".join(map(str, p_)) for p_ in e if p_)
                        + r"\rangle$", None))
    body.append(txt(0, 0.3, r"Green = kept. Each pick is a subset of its own element, in element order.", W, "note"))
    add("c4s_step_52", "Step by step: four order-preserving picks",
        K.single(K.panel(T, "5.2", 1, "Pick within each element", ["ORDER"], body, W, 2.4, key=True)))

    # ---- 6.1 subgraphs
    s = S(r"\creamq{Problem 6.1}")
    K.need(s, "6.1", "Core $=$ 4-cycle of $a$'s $+$ one pendant $b$", r"2 candidate sub-graphs")

    def graph(ox, pend, hl=(), dash=()):
        P = {"a1": (0.7, 1.05), "a2": (1.45, 1.05), "a3": (1.45, 0.4), "a4": (0.7, 0.4)}
        L = []
        cyc = [("a1", "a2"), ("a2", "a3"), ("a3", "a4"), ("a4", "a1")]
        spots = {"a1": (0.05, 1.05), "a4": (0.05, 0.4), "a2": (2.1, 1.05), "a3": (2.1, 0.4),
                 "a4b": (0.7, -0.2), "a2b": (1.45, 1.65)}
        for a_, b_ in cyc:
            L.append(r"\draw[ink, line width=0.6pt] (%.2f,%.2f) -- (%.2f,%.2f);"
                     % (ox + P[a_][0], P[a_][1], ox + P[b_][0], P[b_][1]))
        for k, (lab, at, spot) in enumerate(pend):
            q = spots[spot]
            st = "mkc, line width=1.1pt" if k in hl else ("sub, dashed" if k in dash else "ink, line width=0.6pt")
            L.append(r"\draw[%s] (%.2f,%.2f) -- (%.2f,%.2f);" % (st, ox + P[at][0], P[at][1], ox + q[0], q[1]))
            L.append(r"\node[circle, draw=%s, fill=white, inner sep=0pt, minimum size=3.2mm, font=\tiny] at (%.2f,%.2f) {$%s$};"
                     % ("mkc" if k in hl else "ink", ox + q[0], q[1], lab))
        for v, (x, y) in P.items():
            L.append(r"\node[circle, draw=ink, fill=white, inner sep=0pt, minimum size=3.2mm, font=\tiny] at (%.2f,%.2f) {$a$};"
                     % (ox + x, y))
        return L

    W = 5.0
    body = graph(0.1, [("b", "a1", "a1")]) + [
        txt(2.6, 1.5, r"4-cycle of $a$ $+$ pendant $b$ on $A_1$:\\5 edges $= k-1$.\\"
                      r"$G_1$ adds $a{-}b$, $G_2$ adds $a{-}c$,\\each on a neighbour of $A_1$.", 2.4, "note")]
    p1 = K.panel(T, "6.1", 1, "The common core", ["CORE"], body, W, 2.6)
    body = graph(0.1, [("b", "a1", "a1"), ("b", "a4", "a4"), ("c", "a4", "a4b")], hl=(1, 2)) + \
        [txt(2.6, 1.5, r"\textbf{Candidate I}: both new pendants on the same neighbour ($A_4$).\\"
                       r"$(A_2,A_2) \cong (A_4,A_4)$", 2.35, "note")]
    p2 = K.panel(T, "6.1", 2, "Same neighbour", ["ATTACH", "SYMM"], body, W, 2.6)
    body = graph(0.1, [("b", "a1", "a1"), ("b", "a4", "a4"), ("c", "a2", "a2")], hl=(1, 2)) + \
        [txt(2.6, 1.5, r"\textbf{Candidate II}: the new pendants on the two different neighbours.\\"
                       r"$(A_2,A_4) \cong (A_4,A_2)$", 2.35, "note")]
    p3 = K.panel(T, "6.1", 3, "Different neighbours", ["ATTACH", "SYMM"], body, W, 2.6, key=True)
    add("c4s_step_61", "Step by step: the core, then the two ways to attach (7 vertices, 7 edges each)",
        K.grid([p1, p2, p3], 3))

    return [("c4s_index", T.index())] + figs


def main():
    figs = build()
    if "--report" in sys.argv:
        for n, _ in figs:
            print("ok  %s" % n)
        return
    K.render([("pre", K.preamble(T))] + figs, TEX, PREFIX, CAPTION, scale={"c4s_index": 0.78, "c4s_ap_18": 0.8})


if __name__ == "__main__":
    main()
