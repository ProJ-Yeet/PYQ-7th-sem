# -*- coding: utf-8 -*-
"""Draw the step-by-step trace under every chapter-3 numerical in ch3-num.tex.

Chapter 3's five problems are all traces: three search traces (A*, greedy,
best first) and two game-tree traces (minimax, alpha-beta). The notes already
tabulate every step; this script draws the SAME steps on the SAME graph the
paper prints, one panel per step, so the reader can see the frontier move
instead of reconstructing it from an OPEN column.

Nothing here is a redrawing of a source figure in the sense the house style
forbids: the paper's own figure stays cropped above each problem
(\\figC{c3_*.png}). These are drawings of the SOLUTION, in the same class as
ch4's resolution graphs (resgraph.py) and ch5's semantic nets (semnet.py),
and like those they are generated so they cannot disagree with the trace.

The traces are recomputed here from the graph data, not read out of the .tex,
and the module asserts each one against the expansion order the notes print
before it draws anything -- that assertion is the exit test.

    python searchfig.py            regenerate every figure and its \\includegraphics block
    python searchfig.py --report   run the traces only, print them, check them

Figures are PNGs so tools/anki_from_notes.py carries them onto the cards.
"""
import itertools
import os
import re
import subprocess
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch3-num.tex")
FIGS = os.path.join(HERE, "figs")
TECTONIC = os.path.join(HERE, "..", "..", "..", "Data Mining", "ExamNotes", "src",
                        "tectonic.exe")
BS = chr(92)
MARK = "% searchfig:"
SLOT = "% searchfig:slot "
DPI = 300
MAXPT = 515.0          # the text block, in pt


# =====================================================================
#  The problem data -- the same numbers verify.py checks
# =====================================================================
# 2081 Chaitra and 2080 Chaitra print the same graph with different
# heuristics. Undirected, as the paper draws it (no arrowheads).
C3_EDGES = {
    ("S", "A"): 6, ("S", "B"): 5, ("S", "C"): 10,
    ("A", "E"): 6, ("B", "E"): 6, ("B", "D"): 7, ("C", "D"): 6,
    ("E", "F"): 4, ("D", "F"): 6, ("F", "G"): 3,
}
C3_POS = {"S": (0.0, 0.0), "A": (1.65, 1.35), "B": (1.65, 0.0),
          "C": (1.65, -1.35), "E": (3.30, 0.95), "D": (3.30, -0.95),
          "F": (4.80, 0.0), "G": (6.10, 0.0)}
H81 = dict(S=17, A=10, B=13, C=4, D=2, E=4, F=1, G=0)
H80 = dict(S=15, A=10, B=12, C=5, D=4, E=2, F=1, G=0)

# 2076 Bhadra: a tree, the number on each edge taken as the child's estimate.
BH_KIDS = {"A": ["B", "C", "D"], "B": ["E", "F"], "D": ["G", "H"],
           "G": ["I", "J"], "C": [], "E": [], "F": [], "H": [], "I": [],
           "J": []}
BH_H = dict(A=0, B=3, C=6, D=1, E=6, F=5, G=4, H=6, I=1, J=2)
BH_POS = {"A": (3.00, 0.0), "B": (1.00, -1.15), "C": (3.00, -1.15),
          "D": (5.00, -1.15), "E": (0.25, -2.30), "F": (1.75, -2.30),
          "G": (4.25, -2.30), "H": (5.75, -2.30), "I": (3.70, -3.45),
          "J": (4.80, -3.45)}

# The two game trees. A nested list is an internal node, an int a leaf.
T79 = [[[[3, 9], [2, 7]], [[2], [5, 0]]],
       [[[2, 5], [8]], [[3, 14]]]]
T76 = [[3, 5, 10], [2, 8, 19], [2, 7, 3]]


def adj(edges=None):
    out = {}
    for (a, b), w in (edges or C3_EDGES).items():
        out.setdefault(a, []).append((b, w))
        out.setdefault(b, []).append((a, w))
    for k in out:
        out[k].sort()
    return out


# =====================================================================
#  Traces
# =====================================================================
def astar_trace(h, edges=None, start="S", goal="G"):
    """A* with reopening: a node already closed goes back on OPEN when a
    cheaper g is found for it. Both papers' heuristics are admissible but not
    consistent, so without the reopening the answer comes out 19, not 18."""
    a = adj(edges)
    seq = itertools.count()
    g = {start: 0}
    parent = {start: None}
    openl = {start: next(seq)}
    closed, steps = [], []
    while openl:
        n = min(openl, key=lambda x: (g[x] + h[x], openl[x]))
        del openl[n]
        closed.append(n)
        rec = dict(expand=n, g=g[n], f=g[n] + h[n], gen=[], repl=[], drop=[],
                   goal=(n == goal))
        if n != goal:
            for m, w in a[n]:
                ng = g[n] + w
                if m not in g:
                    g[m], parent[m] = ng, n
                    openl[m] = next(seq)
                    rec["gen"].append(m)
                elif ng < g[m]:
                    g[m], parent[m] = ng, n
                    openl[m] = next(seq)
                    rec["repl"].append(m)
                else:
                    rec["drop"].append(m)
        rec["g"] = dict(g)
        rec["parent"] = dict(parent)
        rec["closed"] = list(closed)
        rec["open"] = sorted(openl, key=lambda x: (g[x] + h[x], openl[x]))
        steps.append(rec)
        if n == goal:
            break
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return steps, list(reversed(path)), g[goal]


def greedy_trace(h, edges=None, start="S", goal="G"):
    """Greedy best first: order on h alone. Graph search -- a node already on
    OPEN or already closed is not queued a second time."""
    a = adj(edges)
    seq = itertools.count()
    parent = {start: None}
    g = {start: 0}
    openl = {start: next(seq)}
    closed, steps = [], []
    while openl:
        n = min(openl, key=lambda x: (h[x], openl[x]))
        del openl[n]
        closed.append(n)
        rec = dict(expand=n, g=g[n], f=h[n], gen=[], repl=[], drop=[],
                   goal=(n == goal))
        if n != goal:
            for m, w in a[n]:
                if m in closed or m in openl:
                    rec["drop"].append(m)
                    continue
                g[m], parent[m] = g[n] + w, n
                openl[m] = next(seq)
                rec["gen"].append(m)
        rec["g"] = dict(g)
        rec["parent"] = dict(parent)
        rec["closed"] = list(closed)
        rec["open"] = sorted(openl, key=lambda x: (h[x], openl[x]))
        steps.append(rec)
        if n == goal:
            break
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return steps, list(reversed(path)), g[goal]


def bestfirst_trace(kids, h, start="A", goal="I"):
    """Best first on the 2076 Bhadra tree: expand the OPEN node of smallest
    value, so OPEN is re-ordered after every expansion."""
    seq = itertools.count()
    parent = {start: None}
    openl = {start: next(seq)}
    closed, steps = [], []
    while openl:
        n = min(openl, key=lambda x: (h[x], openl[x]))
        del openl[n]
        closed.append(n)
        rec = dict(expand=n, gen=[], goal=(n == goal))
        if n != goal:
            for c in kids[n]:
                parent[c] = n
                openl[c] = next(seq)
                rec["gen"].append(c)
        rec["parent"] = dict(parent)
        rec["closed"] = list(closed)
        rec["open"] = sorted(openl, key=lambda x: (h[x], openl[x]))
        steps.append(rec)
        if n == goal:
            break
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return steps, list(reversed(path))


# ---------------------------------------------------------------------
#  Game trees
# ---------------------------------------------------------------------
def tree_nodes(t, nid=(), depth=0, out=None):
    """{id: (children ids, leaf value or None, depth)} keyed by path tuple."""
    out = {} if out is None else out
    if isinstance(t, int):
        out[nid] = ([], t, depth)
        return out
    kids = [nid + (i,) for i in range(len(t))]
    out[nid] = (kids, None, depth)
    for k, sub in zip(kids, t):
        tree_nodes(sub, k, depth + 1, out)
    return out


def tree_layout(nodes):
    """x by leaf order, y by depth; an internal node centres over its kids."""
    pos, k = {}, [0]

    def walk(nid):
        kids, val, depth = nodes[nid]
        if not kids:
            pos[nid] = (float(k[0]), -float(depth))
            k[0] += 1
            return pos[nid][0]
        xs = [walk(c) for c in kids]
        pos[nid] = (sum(xs) / len(xs), -float(depth))
        return pos[nid][0]

    walk(())
    return pos


def minimax_stages(nodes):
    """One snapshot per level, deepest internal level first: {id: value} grown
    a level at a time, which is the order the notes back the values up in."""
    val = {}
    for nid, (kids, v, _) in nodes.items():
        if not kids:
            val[nid] = v
    depths = sorted({d for nid, (kids, _, d) in nodes.items() if kids},
                    reverse=True)
    stages = []
    for d in depths:
        for nid, (kids, _, dd) in nodes.items():
            if kids and dd == d:
                vals = [val[c] for c in kids]
                # root is MAX, so a node at even depth maximises
                val[nid] = max(vals) if d % 2 == 0 else min(vals)
        stages.append((d, dict(val)))
    return stages


def ab_trace(nodes, checkpoint_depth):
    """Left-to-right alpha-beta, snapshotting whenever a node at
    `checkpoint_depth` finishes (those are the nodes just above the leaves,
    which is the granularity the notes' alpha-beta table uses).

    Returns (snapshots, value, pruned leaf values in cut order). A snapshot is
    (node just finished, {id: final value}, {id: (a, b)} for nodes entered,
    {pruned edge child id}, note).
    """
    val, win, cut_edges, snaps, pruned = {}, {}, set(), [], []

    def show(a, b):
        return (r"-\infty" if a == float("-inf") else "%g" % a,
                r"\infty" if b == float("inf") else "%g" % b)

    def rec(nid, a, b):
        kids, leaf, depth = nodes[nid]
        if not kids:
            val[nid] = leaf
            return leaf
        win[nid] = show(a, b)
        maxi = depth % 2 == 0
        v = float("-inf") if maxi else float("inf")
        note = ""
        for i, c in enumerate(kids):
            v = max(v, rec(c, a, b)) if maxi else min(v, rec(c, a, b))
            val[nid] = v
            if maxi:
                a = max(a, v)
                win[nid] = show(a, b)      # the window as it stands now
                if v >= b:
                    for d in kids[i + 1:]:
                        cut_edges.add(d)
                        pruned.extend(leaves_of(nodes, d))
                    note = r"cut: $%g \geq \beta$" % v
                    break
            else:
                b = min(b, v)
                win[nid] = show(a, b)
                if v <= a:
                    for d in kids[i + 1:]:
                        cut_edges.add(d)
                        pruned.extend(leaves_of(nodes, d))
                    note = r"cut: $%g \leq \alpha$" % v
                    break
        if depth == checkpoint_depth:
            snaps.append((nid, dict(val), dict(win), set(cut_edges), note))
        return v

    v = rec((), float("-inf"), float("inf"))
    snaps.append(((), dict(val), dict(win), set(cut_edges), "root"))
    return snaps, v, pruned


def leaves_of(nodes, nid):
    kids, leaf, _ = nodes[nid]
    if not kids:
        return [leaf]
    out = []
    for c in kids:
        out.extend(leaves_of(nodes, c))
    return out


# =====================================================================
#  Drawing
# =====================================================================
STYLE = r"""[x=%.3fcm, y=%.3fcm, font=\scriptsize,
  nd/.style={circle, draw=ruleL, dash pattern=on 1pt off 1pt, fill=white,
             text=sub, inner sep=0pt, minimum size=5.0mm,
             font=\scriptsize\bfseries},
  sq/.style={nd, rectangle, rounded corners=1pt},
  op/.style={draw=acc, solid, text=ink},
  cl/.style={op, fill=accL},
  cu/.style={op, draw=mkc, fill=mkL, line width=0.8pt},
  dn/.style={op, draw=gd, fill=gdL, line width=0.8pt},
  tag/.style={font=\tiny, text=sub, inner sep=0.6pt},
  wt/.style={font=\tiny, text=sub, fill=white, inner sep=0.5pt},
  ln/.style={draw=ruleL, line width=0.4pt},
  tr/.style={draw=acc, line width=0.9pt},
  sol/.style={draw=gd, line width=1.1pt},
  cx/.style={draw=mkc, line width=0.6pt, dash pattern=on 1.4pt off 1.4pt}]"""


def head(bbox, scale, title):
    x0, y0, x1, y1 = bbox
    L = [r"\begin{tikzpicture}" + STYLE % (scale, scale)]
    L.append(r"\path[use as bounding box] (%.2f,%.2f) rectangle (%.2f,%.2f);"
             % (x0, y0, x1, y1))
    L.append(r"\node[anchor=north west, font=\scriptsize\bfseries, text=acc,"
             r" inner sep=0pt, align=left] at (%.2f,%.2f) {%s};" % (x0, y1, title))
    return L


def graph_panel(title, pos, edges, rec, h, solution=None, bbox=None,
                scale=0.66, shape="nd"):
    """One expansion of a search over a graph or tree."""
    L = head(bbox, scale, title)
    g, parent = rec["g"], rec["parent"]
    closed, openl, cur = set(rec["closed"]), set(rec["open"]), rec["expand"]
    sol = set()
    if solution:
        sol = {frozenset(p) for p in zip(solution, solution[1:])}
    tree = {frozenset((c, p)) for c, p in parent.items() if p}
    for (a, b), w in sorted(edges.items()):
        e = frozenset((a, b))
        st = "sol" if e in sol else ("tr" if e in tree else "ln")
        L.append(r"\draw[%s] (%.2f,%.2f) -- (%.2f,%.2f);"
                 % (st, pos[a][0], pos[a][1], pos[b][0], pos[b][1]))
        L.append(r"\node[wt] at (%.2f,%.2f) {%d};"
                 % ((pos[a][0] + pos[b][0]) / 2, (pos[a][1] + pos[b][1]) / 2, w))
    for n, (x, y) in sorted(pos.items()):
        if n == cur:
            st = "dn" if rec.get("goal") else "cu"
        elif n in openl:
            st = "op"
        elif n in closed:
            st = "cl"
        else:
            st = ""
        L.append(r"\node[%s%s] (%s) at (%.2f,%.2f) {%s};"
                 % (shape, (", " + st) if st else "", n, x, y, n))
        if n in g and (n in openl or n in closed):
            L.append(r"\node[tag, anchor=north] at (%.2f,%.2f) {%s};"
                     % (x, y - 0.32, r"$%d{\mid}%d$" % (g[n], g[n] + h[n])))
    return "\n".join(L) + "\n" + r"\end{tikzpicture}"


def bf_panel(title, pos, kids, h, rec, solution=None, bbox=None, scale=0.66):
    """One expansion of best first on the 2076 Bhadra tree."""
    L = head(bbox, scale, title)
    parent = rec["parent"]
    closed, openl, cur = set(rec["closed"]), set(rec["open"]), rec["expand"]
    sol = {frozenset(p) for p in zip(solution, solution[1:])} if solution else set()
    seen = closed | openl
    for p, cs in sorted(kids.items()):
        for c in cs:
            e = frozenset((p, c))
            st = "sol" if e in sol else ("tr" if c in seen else "ln")
            L.append(r"\draw[%s] (%.2f,%.2f) -- (%.2f,%.2f);"
                     % (st, pos[p][0], pos[p][1], pos[c][0], pos[c][1]))
            L.append(r"\node[wt] at (%.2f,%.2f) {%d};"
                     % (0.45 * pos[p][0] + 0.55 * pos[c][0],
                        0.45 * pos[p][1] + 0.55 * pos[c][1], h[c]))
    for n, (x, y) in sorted(pos.items()):
        if n == cur:
            st = "dn" if rec.get("goal") else "cu"
        elif n in openl:
            st = "op"
        elif n in closed:
            st = "cl"
        else:
            st = ""
        shape = "sq" if n == "I" else "nd"
        L.append(r"\node[%s%s] at (%.2f,%.2f) {%s};"
                 % (shape, (", " + st) if st else "", x, y, n))
    return "\n".join(L) + "\n" + r"\end{tikzpicture}"


def game_panel(title, nodes, pos, val, win=None, cut=None, cur=None,
               bbox=None, scale=0.74):
    """One snapshot of a game tree: squares MAX, circles MIN, values inside."""
    L = head(bbox, scale, title)
    win, cut = win or {}, cut or set()
    for nid, (kids, _, _) in sorted(nodes.items()):
        for c in kids:
            st = "cx" if c in cut else ("tr" if c in val else "ln")
            L.append(r"\draw[%s] (%.2f,%.2f) -- (%.2f,%.2f);"
                     % (st, pos[nid][0], pos[nid][1], pos[c][0], pos[c][1]))
            if c in cut:
                L.append(r"\node[font=\tiny, text=mkc, inner sep=0.4pt]"
                         r" at (%.2f,%.2f) {$\times$};"
                         % ((pos[nid][0] + pos[c][0]) / 2,
                            (pos[nid][1] + pos[c][1]) / 2))
    for nid, (kids, leaf, depth) in sorted(nodes.items()):
        x, y = pos[nid]
        shape = "sq" if (not kids or depth % 2 == 0) else "nd"
        dead = _under_cut(nid, cut)
        if dead:
            st = ""
        elif nid == cur:
            st = "cu"
        elif nid in val:
            st = "cl"
        elif nid in win:
            st = "op"
        else:
            st = ""
        # a pruned leaf still prints its number, greyed: the point of the
        # figure is to show WHAT the cut saved looking at
        if dead and not kids:
            body = "%d" % leaf
        else:
            body = "" if (dead or nid not in val) else "%d" % val[nid]
        L.append(r"\node[%s%s] at (%.2f,%.2f) {%s};"
                 % (shape, (", " + st) if st else "", x, y, body))
        if kids and nid in win and not dead:
            a, b = win[nid]
            L.append(r"\node[tag, anchor=south, fill=white, inner sep=0.8pt]"
                     r" at (%.2f,%.2f) {$%s,%s$};" % (x, y + 0.30, a, b))
    return "\n".join(L) + "\n" + r"\end{tikzpicture}"


def _under_cut(nid, cut):
    return any(len(c) <= len(nid) and nid[:len(c)] == c for c in cut)


LEGEND = [("cl", "closed"), ("op", "on OPEN"), ("cu", "expanding now"),
          ("dn", "goal")]
LEGEND_G = [("cl", "value backed up"), ("op", "entered, $\\alpha,\\beta$ set"),
            ("cu", "just finished"), ("", "pruned")]


def legend(items):
    """Chained left to right off each previous label, so the spacing is exact
    rather than a guess at the width of the text."""
    L = [r"\begin{tikzpicture}" + STYLE % (1.0, 1.0)]
    prev = None
    for i, (st, lab) in enumerate(items):
        where = "(0,0)" if prev is None else "([xshift=4.5mm]%s.east)" % prev
        L.append(r"\node[nd%s, minimum size=3.2mm, anchor=west] (s%d) at %s {};"
                 % ((", " + st) if st else "", i, where))
        L.append(r"\node[tag, anchor=west] (t%d) at ([xshift=1.2mm]s%d.east) {%s};"
                 % (i, i, lab))
        prev = "t%d" % i
    return "\n".join(L) + "\n" + r"\end{tikzpicture}"


def figure(panels, per_row, legend_items):
    """A grid of panels, last row centred, with a legend strip under it."""
    rows = [panels[i:i + per_row] for i in range(0, len(panels), per_row)]
    L = [r"\begin{panelbox}",
         r"\setlength{\tabcolsep}{1.6mm}\renewcommand{\arraystretch}{1.25}",
         r"\begin{tabular}{@{}" + "c" * per_row + r"@{}}"]
    for r in rows:
        cells = list(r) + [""] * (per_row - len(r))
        if len(r) < per_row:
            pad = (per_row - len(r))
            left = pad // 2
            cells = [""] * left + list(r) + [""] * (pad - left)
        L.append(" &\n".join(cells) + r" \\")
    L.append(r"\multicolumn{%d}{@{}c@{}}{%s} \\" % (per_row, legend(legend_items)))
    L.append(r"\end{tabular}")
    L.append(r"\end{panelbox}")
    return "\n".join(L)


# =====================================================================
#  The eight figures
# =====================================================================
def ab_title(k, nid, nodes, val, cut, names, rootexpr):
    """`3. c_2 = min(2) = 2   prune 7` -- the arithmetic, not just the name."""
    if nid == ():
        return (r"%d.\, root $= %s = \mathbf{%d}$" % (k, rootexpr, val[()]))
    kids = nodes[nid][0]
    seen = [nodes[c][1] for c in kids if c not in cut]
    gone = [nodes[c][1] for c in kids if c in cut]
    op = r"\max" if nodes[nid][2] % 2 == 0 else r"\min"
    lab = r"%d.\, $%s = %s(%s) = %d$" % (k, names[nid], op,
                                         ",".join(str(v) for v in seen), val[nid])
    if gone:
        lab += (r" \,{\color{mkc}prune %s}"
                % ", ".join(str(v) for v in gone))
    return lab


GBOX = (-0.55, -2.10, 6.70, 2.35)     # the S..G graph plus its tags
BBOX = (-0.45, -4.10, 6.35, 1.15)     # the 2076 Bhadra tree
BOX79 = (-0.75, -4.80, 11.75, 1.35)
BOX76 = (-0.75, -2.85, 8.75, 1.35)


def build():
    figs = []

    # --- 3.N.1  A* on the 2081 Chaitra graph -------------------------
    steps, path, cost = astar_trace(H81)
    order = [s["expand"] for s in steps]
    assert order == list("SCAEFBDEFG"), order
    assert (path, cost) == (list("SBEFG"), 18), (path, cost)
    panels = []
    for k, s in enumerate(steps, 1):
        tail = "goal off OPEN" if s["goal"] else "$f$ %d" % s["f"]
        extra = ""
        if s["repl"]:
            extra = r"\,{\color{mkc}replace %s}" % ",".join(s["repl"])
        panels.append(graph_panel("%d.\\, expand %s \\,(%s)%s"
                                  % (k, s["expand"], tail, extra),
                                  C3_POS, C3_EDGES, s, H81,
                                  path if s["goal"] else None, GBOX, 0.615))
    figs.append(("c3_step_81ch", figure(panels, 4, LEGEND)))

    # --- 3.N.2  greedy, then A*, on the 2080 Chaitra graph -----------
    gsteps, gpath, gcost = greedy_trace(H80)
    assert [s["expand"] for s in gsteps] == list("SCDFG")
    assert (gpath, gcost) == (list("SCDFG"), 25), (gpath, gcost)
    panels = []
    for k, s in enumerate(gsteps, 1):
        tail = "goal" if s["goal"] else "$h$ %d" % s["f"]
        panels.append(graph_panel("%d.\\, expand %s \\,(%s)" % (k, s["expand"], tail),
                                  C3_POS, C3_EDGES, s, H80,
                                  gpath if s["goal"] else None, GBOX, 0.80))
    figs.append(("c3_step_80ch_greedy", figure(panels, 3, LEGEND)))

    asteps, apath, acost = astar_trace(H80)
    assert [s["expand"] for s in asteps] == list("SCAEBEDFG")
    assert (apath, acost) == (list("SBEFG"), 18), (apath, acost)
    panels = []
    for k, s in enumerate(asteps, 1):
        tail = "goal off OPEN" if s["goal"] else "$f$ %d" % s["f"]
        extra = ""
        if s["repl"]:
            extra = r"\,{\color{mkc}replace %s}" % ",".join(s["repl"])
        panels.append(graph_panel("%d.\\, expand %s \\,(%s)%s"
                                  % (k, s["expand"], tail, extra),
                                  C3_POS, C3_EDGES, s, H80,
                                  apath if s["goal"] else None, GBOX, 0.80))
    figs.append(("c3_step_80ch_astar", figure(panels, 3, LEGEND)))

    # --- 3.N.3  best first on the 2076 Bhadra tree -------------------
    bsteps, bpath = bestfirst_trace(BH_KIDS, BH_H)
    assert [s["expand"] for s in bsteps] == list("ADBGI")
    assert bpath == list("ADGI"), bpath
    panels = []
    for k, s in enumerate(bsteps, 1):
        tail = "goal" if s["goal"] else ("root" if s["expand"] == "A" else "value %d" % BH_H[s["expand"]])
        panels.append(bf_panel("%d.\\, expand %s \\,(%s)" % (k, s["expand"], tail),
                               BH_POS, BH_KIDS, BH_H, s,
                               bpath if s["goal"] else None, BBOX, 0.82))
    figs.append(("c3_step_76bh", figure(panels, 3, LEGEND)))

    # --- 3.N.4  minimax, then alpha-beta, on the 2079 Chaitra tree ---
    n79 = tree_nodes(T79)
    p79 = tree_layout(n79)
    stages = minimax_stages(n79)
    names = {3: "MIN over the leaves", 2: "MAX row", 1: "MIN row, then the root"}
    panels = []
    for k, (d, val) in enumerate(stages, 1):
        if d == 0:
            continue
        lab = names.get(d, "level %d" % d)
        if d == 1:
            val = stages[-1][1]
        panels.append(game_panel("%d.\\, %s" % (k, lab), n79, p79, val,
                                 bbox=BOX79, scale=0.735))
    figs.append(("c3_step_79ch_minimax",
                 figure(panels, 2, LEGEND_G)))

    snaps, v79, pr79 = ab_trace(n79, 3)
    assert v79 == 3 and pr79 == [7, 5], (v79, pr79)
    cnames = {}
    for i, nid in enumerate([n for n in sorted(n79) if n79[n][2] == 3], 1):
        cnames[nid] = "c_%d" % i
    ab = [game_panel(ab_title(k, nid, n79, val, cut, cnames, "\\max(2,3)"),
                     n79, p79, val, win, cut, nid, BOX79, 0.735)
          for k, (nid, val, win, cut, note) in enumerate(snaps, 1)]
    figs.append(("c3_step_79ch_ab1", figure(ab[:4], 2, LEGEND_G)))
    figs.append(("c3_step_79ch_ab2", figure(ab[4:], 2, LEGEND_G)))

    # --- 3.N.5  minimax, then alpha-beta, on the 2076 Baishakh tree --
    n76 = tree_nodes(T76)
    p76 = tree_layout(n76)
    stages = minimax_stages(n76)
    panels = []
    labs = {1: "MIN over each group of three leaves", 0: "MAX at the root"}
    for k, (d, val) in enumerate(stages, 1):
        panels.append(game_panel("%d.\\, %s" % (k, labs[d]), n76, p76, val,
                                 bbox=BOX76, scale=0.93))
    figs.append(("c3_step_76ba_minimax", figure(panels, 2, LEGEND_G)))

    snaps, v76, pr76 = ab_trace(n76, 1)
    assert v76 == 3 and pr76 == [8, 19, 7, 3], (v76, pr76)
    mnames = {(0,): "m_1", (1,): "m_2", (2,): "m_3"}
    ab = [game_panel(ab_title(k, nid, n76, val, cut, mnames, "\\max(3,2,2)"),
                     n76, p76, val, win, cut, nid, BOX76, 0.93)
          for k, (nid, val, win, cut, note) in enumerate(snaps, 1)]
    figs.append(("c3_step_76ba_ab", figure(ab, 2, LEGEND_G)))
    return figs


PRE = r"""\documentclass[border=4pt, multi=panelbox]{standalone}
\usepackage[default]{lato}
\usepackage{amsmath, amssymb, xcolor, tikz}
\usetikzlibrary{arrows.meta}
\definecolor{ink}{HTML}{16202A}\definecolor{sub}{HTML}{6B7785}
\definecolor{acc}{HTML}{2563A8}\definecolor{accL}{HTML}{D6E4F5}
\definecolor{mkc}{HTML}{C2410C}\definecolor{mkL}{HTML}{FDEBD9}
\definecolor{gd}{HTML}{15803D}\definecolor{gdL}{HTML}{DCFCE7}
\definecolor{ruleL}{HTML}{DEE3E8}
\newenvironment{panelbox}{}{}
\begin{document}
"""

CAPTION = {
    "c3_step_81ch": "Step by step: the graph after each expansion",
    "c3_step_80ch_greedy": "Step by step: greedy best first",
    "c3_step_80ch_astar": "Step by step: A* on the same graph",
    "c3_step_76bh": "Step by step: the tree after each expansion",
    "c3_step_79ch_minimax": "Step by step: minimax backing the values up",
    "c3_step_79ch_ab1": "Step by step: alpha-beta, left half",
    "c3_step_79ch_ab2": "Step by step: alpha-beta, right half and the root",
    "c3_step_76ba_minimax": "Step by step: minimax backing the values up",
    "c3_step_76ba_ab": "Step by step: alpha-beta, one MIN node at a time",
}


def strip_blocks(src):
    """Remove the generated blocks and nothing else. The pattern anchors on
    line starts rather than on a leading newline: matching the newline would
    eat the one that terminates the slot line above, gluing the next run's
    marker onto real source. That is what mangled the file once already."""
    return re.sub(r"(?m)^" + re.escape(MARK) + r"c3_step_\w+.*?^"
                  + re.escape(MARK) + r"end\n", "", src, flags=re.S)


def report():
    for name, _ in build():
        print("ok  %s" % name)
    steps, path, cost = astar_trace(H81)
    for k, s in enumerate(steps, 1):
        print("81Ch %2d expand %s f=%-2d OPEN %s%s%s"
              % (k, s["expand"], s["f"],
                 " ".join("%s/%d" % (n, s["g"][n] + H81[n]) for n in s["open"]),
                 "  repl=" + ",".join(s["repl"]) if s["repl"] else "",
                 "  drop=" + ",".join(s["drop"]) if s["drop"] else ""))
    print("81Ch path %s cost %d" % ("-".join(path), cost))
    for tag, h in (("80Ch greedy", H80),):
        st, p, c = greedy_trace(h)
        for k, s in enumerate(st, 1):
            print("%s %2d expand %s h=%-2d OPEN %s" % (tag, k, s["expand"], s["f"],
                  " ".join("%s/%d" % (n, h[n]) for n in s["open"])))
        print("%s path %s cost %d" % (tag, "-".join(p), c))
    st, p, c = astar_trace(H80)
    for k, s in enumerate(st, 1):
        print("80Ch A* %2d expand %s f=%-2d OPEN %s%s"
              % (k, s["expand"], s["f"],
                 " ".join("%s/%d" % (n, s["g"][n] + H80[n]) for n in s["open"]),
                 "  repl=" + ",".join(s["repl"]) if s["repl"] else ""))
    print("80Ch A* path %s cost %d" % ("-".join(p), c))
    st, p = bestfirst_trace(BH_KIDS, BH_H)
    for k, s in enumerate(st, 1):
        print("76Bh %2d expand %s OPEN %s" % (k, s["expand"],
              " ".join("%s/%d" % (n, BH_H[n]) for n in s["open"])))
    print("76Bh path %s" % "-".join(p))


def main():
    if "--report" in sys.argv:
        report()
        return
    figs = build()
    work = os.path.join(FIGS, "_searchfig")
    os.makedirs(work, exist_ok=True)
    doc = PRE + "\n\n".join(b for _, b in figs) + "\n" + BS + "end{document}\n"
    tex = os.path.join(work, "searchfig.tex")
    open(tex, "w", encoding="utf-8").write(doc)
    r = subprocess.run([TECTONIC, "-X", "compile", "searchfig.tex"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-4000:] + r.stderr[-4000:])
    pdf = fitz.open(os.path.join(work, "searchfig.pdf"))
    if len(pdf) != len(figs):
        sys.exit("expected %d pages, got %d" % (len(figs), len(pdf)))
    widths = {}
    for (name, _), page in zip(figs, pdf):
        page.get_pixmap(dpi=DPI).save(os.path.join(FIGS, name + ".png"))
        widths[name] = min(page.rect.width, MAXPT)

    src = strip_blocks(open(TEX, encoding="utf-8").read()).rstrip("\n") + "\n"
    for name, _ in figs:
        anchor = SLOT + name
        i = src.find(anchor)
        if i < 0:
            sys.exit("no slot for %s in ch3-num.tex" % name)
        if src[i - 1:i] != "\n" or not src[i + len(anchor):].startswith("\n"):
            sys.exit("slot for %s is not alone on its line" % name)
        j = src.find("\n", i) + 1
        block = ("\n" + MARK + name + " (generated by searchfig.py; do not edit)\n"
                 + BS + "penalty0" + BS + "vspace{3pt}\n"
                 + BS + "lead{" + CAPTION[name] + "}\n"
                 + BS + "begin{center}" + BS
                 + "includegraphics[width=%.1fpt]{figs/%s.png}" % (widths[name], name)
                 + BS + "end{center}\n" + MARK + "end\n")
        src = src[:j] + block.lstrip("\n") + src[j:]
    open(TEX, "w", encoding="utf-8").write(src)
    print("%d step figures written" % len(figs))


if __name__ == "__main__":
    main()
