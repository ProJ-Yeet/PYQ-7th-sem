# -*- coding: utf-8 -*-
"""Draw a resolution graph under every resolution-refutation proof in ch4-num.tex.

The proofs are already written out as numbered step lists:

    \\item[9.] $\\neg eats(y, Peanuts) \\vee killed(y)$ \\hfill \\yr{(8,\\,4) $[Peanuts/x]$}

and each step names its two parent clauses. This script reads those lists,
looks every parent label up in the same problem's CNF / negated-goal lists,
and draws the textbook's shape (the Colonel West figure, c4_res_graph.png):
the clause each step spends on the left, the running resolvent down the
right, the empty clause at the foot. A proof that joins two chains (Marcus,
Curiosity) draws the second chain in its own column to the left.

It is generated, never hand-drawn, so it cannot disagree with the proof it
sits under. Edit the step list and rerun; never edit a c4_resg_*.png or the
marked block in ch4-num.tex by hand.

    python resgraph.py            regenerate every graph and the \\includegraphics blocks
    python resgraph.py --report   parse only: print each proof's steps

The figures are PNGs (not PDFs) so tools/anki_from_notes.py can carry them onto
the Anki cards like every other figure.
"""
import os, re, subprocess, sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch4-num.tex")
TECTONIC = os.path.join(HERE, "..", "..", "..", "Data Mining", "ExamNotes", "src",
                        "tectonic.exe")
BS = chr(92)
MARK = "% resgraph:"
DPI = 300
WIDTH_CM = 17.0      # the text block is 18.1 cm; leave a margin

STEP = re.compile(re.escape(BS) + r"yr\{\((\w+),\s*(?:" + re.escape(BS)
                  + r",)?\s*(\w+)\)\s*(?:\$(\[[^$]*\])\$)?")
DEF = re.compile(r"(?:" + re.escape(BS) + r"item\[(\w+)\.\]|" + re.escape(BS)
                 + r"textbf\{(\w+)\.\})\s*\$([^$]+)\$")


def strip_blocks(src):
    """Remove every block this script inserted before."""
    return re.sub(r"\n" + re.escape(MARK) + r"c4_resg_\d+.*?\n"
                  + re.escape(MARK) + r"end\n", "", src, flags=re.S)


def group_end(src, i):
    """Index just past the brace group opening at src[i] == '{'."""
    d = 0
    while i < len(src):
        c = src[i]
        if c == BS:
            i += 2
            continue
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced")


def enclosing_sbs_end(src, pos):
    """End of the top-level \\sbs / \\sbsr block that holds pos."""
    for m in reversed(list(re.finditer(r"(?m)^" + re.escape(BS) + r"sbsr?\{", src[:pos]))):
        i = m.end() - 1
        nargs = 3 if src[m.start():m.end()].startswith(BS + "sbsr") else 2
        for _ in range(nargs):
            while src[i] in " \t\n%":
                i += 1
            i = group_end(src, i)
        if i > pos:
            return i
    raise ValueError("proof at %d is not inside an \\sbs" % pos)


def goal_labels(src, lo, hi):
    """{label: clause} for the negated goal."""
    out = {}
    for m in re.finditer(re.escape(BS) + r"lead\{[^\n]*Negate", src[lo:hi]):
        a = lo + m.end()
        b = src.find(BS + "lead{", a)
        for d in DEF.finditer(src[a:b]):
            out[d.group(1) or d.group(2)] = d.group(3).strip()
    # the one-off sets name it in the proof heading instead:
    # \lead{Proof \; \yr{negated goal 8. $child(Scrooge)$}}
    for m in re.finditer(r"negated goal (\w+)\.\s*\$([^$]+)\$", src[lo:hi]):
        out[m.group(1)] = m.group(2).strip()
    # or tag the clause itself: \item[5.] $...$ \hfill \yr{negated goal}
    for m in re.finditer(re.escape(BS) + r"item\[(\w+)\.\]\s*\$([^$]+)\$[^\n]*"
                         + re.escape(BS) + r"yr\{negated goal\}", src[lo:hi]):
        out[m.group(1)] = m.group(2).strip()
    return out


def proofs(src):
    """[(insert_at, steps, clause_text, goal_set)] for every complete proof."""
    items = list(re.finditer(r"(?m)^\s*" + re.escape(BS) + r"item\[(\w+)\.\]", src))
    runs, cur = [], []
    for it in items:
        # an item runs to the next \item or \end{itemize}; a long step wraps,
        # so its \yr{(a,b)} can sit on the continuation line
        ends = [e for e in (src.find(BS + "item", it.end()),
                            src.find(BS + "end{itemize}", it.end())) if e >= 0]
        whole = src[it.end():min(ends)]
        yr = STEP.search(whole)
        if not yr:
            cur = []
            continue
        mm = re.match(r"\s*\$(.+?)\$\s*" + re.escape(BS) + "hfill", whole, re.S)
        text = re.sub(r"\s+", " ", mm.group(1)).strip() if mm else ""
        cur.append((it.group(1), text, yr.group(1), yr.group(2), yr.group(3) or "",
                    it.start()))
        if BS + "square" in text:
            runs.append(cur)
            cur = []
    out = []
    prev_end = 0
    for run in runs:
        start = run[0][5]
        # the problem's clause lists: back to the previous proof, or the \T above
        lo = max(prev_end, src.rfind(BS + "T{", 0, start))
        defs = {}
        for d in DEF.finditer(src, lo, run[-1][5] + 1):
            defs[d.group(1) or d.group(2)] = d.group(3).strip()
        goals = goal_labels(src, lo, start)
        defs.update(goals)
        for lab, text, a, b, th, _ in run:
            defs[lab] = text
        steps = [(lab, a, b, th) for lab, _, a, b, th, _ in run]
        out.append((enclosing_sbs_end(src, start), steps, defs, set(goals)))
        # past the previous proof's last step, so its "8. \square" is not
        # read as this problem's clause 8
        prev_end = src.find("\n", run[-1][5]) + 1
    return out


def layout(steps, goals):
    """Grid cells for the derivation tree.

    Rows follow the order the proof was written in: step k's resolvent sits in
    row k, the clauses it consumed in row k-1. Each chain gets two columns, its
    side clauses on the left and its running resolvent on the right. At a
    step whose parents are BOTH resolvents, the parent that descends from the
    negated goal carries on the chain and the other becomes a chain of its
    own, further left.

    Returns ({label: (row, col)}, ncols, edges[(parent, child, 'main'|'side')],
    anchors{col: 'east'|'west'}).
    """
    parents = {lab: (a, b) for lab, a, b, _ in steps}
    idx = {lab: k for k, (lab, _, _, _) in enumerate(steps, 1)}

    def has_goal(lab):
        if lab in goals:
            return True
        return lab in parents and any(has_goal(p) for p in parents[lab])

    def split(lab):
        """(main parent, side parent) of a resolvent."""
        a, b = parents[lab]
        ra, rb = a in parents, b in parents
        if ra and rb:
            if has_goal(a) != has_goal(b):
                return (a, b) if has_goal(a) else (b, a)
            return (a, b) if idx[a] > idx[b] else (b, a)
        if ra or rb:
            return (a, b) if ra else (b, a)
        if b in goals and a not in goals:
            return b, a
        return a, b

    def chain(lab):
        """The resolvents on lab's chain, bottom first, and the top leaf."""
        out = []
        while lab in parents:
            out.append(lab)
            lab = split(lab)[0]
        return out, lab

    def width(lab):
        c, _ = chain(lab)
        return 2 + sum(width(split(r)[1]) for r in c if split(r)[1] in parents)

    # A KB clause used twice is drawn twice, once beside each step that
    # spends it, as the textbook does: node ids are "label#step" for leaves.
    pos, edges, anchors = {}, [], {}

    def place(lab, left):
        c, top = chain(lab)
        subs = [r for r in reversed(c) if split(r)[1] in parents]
        x = left
        for r in subs:
            place(split(r)[1], x)
            x += width(split(r)[1])
        side, spine = x, x + 1
        anchors[side], anchors[spine] = "east", "west"
        pos["%s#%s" % (top, c[-1])] = (idx[c[-1]] - 1, spine)
        for r in c:
            m, s = split(r)
            pos[r] = (idx[r], spine)
            edges.append((m if m in parents else "%s#%s" % (m, r), r, "main"))
            if s in parents:
                edges.append((s, r, "branch"))
            else:
                pos["%s#%s" % (s, r)] = (idx[r] - 1, side)
                edges.append(("%s#%s" % (s, r), r, "side"))

    final = steps[-1][0]
    place(final, 0)
    return pos, width(final), edges, anchors


def tikz(steps, defs, goals):
    pos, ncols, edges, anchors = layout(steps, goals)
    labs = set(s[0] for s in steps)
    note = {lab: "(%s,\\,%s)%s" % (a, b, (r"\;$%s$" % th) if th else "")
            for lab, a, b, th in steps}
    # below ~5 cm an atom like tryAssassinate(Marcus, Caesar), which has no
    # point to break at, spills out of its box; a wide tree is scaled down to
    # the text block by \includegraphics instead
    box_cm = max(5.0, min(6.1, WIDTH_CM / ncols - 1.0))

    def kind(node):
        lab = node.split("#")[0]
        if lab in goals:
            return "goal"
        return "res" if lab in labs else "kb"

    def box(node):
        lab = node.split("#")[0]
        t = defs.get(lab)
        if t is None:
            raise KeyError("clause %s is never defined" % lab)
        if BS + "square" in t:
            body = r"$\square$"
        else:
            body = r"\lb{%s}$%s$" % (lab, t)
        if lab in note:
            body += r"\par{\color{sub}\scriptsize %s}" % note[lab]
        return r"\begin{varwidth}{%.2fcm}\raggedright %s\end{varwidth}" % (box_cm, body)

    names = {lab: "n%d" % k for k, lab in enumerate(sorted(pos))}
    nrows = max(r for r, _ in pos.values()) + 1
    grid = [[""] * ncols for _ in range(nrows)]
    for lab, (r, c) in pos.items():
        grid[r][c] = r"\node[%s] (%s) {%s};" % (kind(lab), names[lab], box(lab))

    L = [r"\begin{tikzpicture}[font=\footnotesize,"
         r" kb/.style={draw=acc, fill=accL, text=ink, rounded corners=2pt, inner sep=3pt},"
         r" res/.style={draw=mkc, fill=mkL, text=ink, rounded corners=2pt, inner sep=3pt},"
         r" goal/.style={res, very thick}]"]
    cols = ", ".join("column %d/.style={anchor=%s}" % (c + 1, a)
                     for c, a in sorted(anchors.items()))
    L.append(r"\matrix[row sep=2.8mm, column sep=8mm, %s] {" % cols)
    for row in grid:
        L.append(" & ".join(row) + r" \\")
    L.append("};")
    for p, ch, how in edges:
        a, b = names[p], names[ch]
        if how == "main":
            L.append(r"\draw[sub, thick] ([xshift=5mm]%s.south west) -- ([xshift=5mm]%s.north west);"
                     % (a, b))
        elif how == "side":
            L.append(r"\draw[sub, thick] (%s.east) -- ([xshift=5mm]%s.north west);" % (a, b))
        else:
            # run the join through the gap above the child's row: a straight
            # line at the child's own height crosses every box in between
            L.append(r"\draw[sub, thick] ([xshift=5mm]%s.south west) |- "
                     r"([xshift=5mm, yshift=1.4mm]%s.north west) -- ([xshift=5mm]%s.north west);"
                     % (a, b, b))
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


PRE = r"""\documentclass[border=3pt, multi=tikzpicture]{standalone}
\usepackage[default]{lato}
\usepackage{amsmath, amssymb, xcolor, tikz, varwidth}
\definecolor{ink}{HTML}{16202A}\definecolor{sub}{HTML}{6B7785}
\definecolor{acc}{HTML}{2563A8}\definecolor{accL}{HTML}{D6E4F5}
\definecolor{mkc}{HTML}{C2410C}\definecolor{mkL}{HTML}{FDEBD9}
\newcommand{\lb}[1]{{\color{sub}\scriptsize\bfseries #1\;}}
\begin{document}
"""


def main():
    report = "--report" in sys.argv
    src = strip_blocks(open(TEX, encoding="utf-8").read())
    ps = proofs(src)
    if report:
        for k, (at, steps, defs, goals) in enumerate(ps, 1):
            print("c4_resg_%02d  goal=%s  %s" % (k, sorted(goals),
                  " ".join("%s=(%s,%s)" % (l, a, b) for l, a, b, _ in steps)))
        return
    work = os.path.join(HERE, "figs", "_resgraph")
    os.makedirs(work, exist_ok=True)
    body = [tikz(steps, defs, goals) for _, steps, defs, goals in ps]
    doc = PRE + "\n\n".join(body) + "\n\\end{document}\n"
    tex = os.path.join(work, "resgraph.tex")
    open(tex, "w", encoding="utf-8").write(doc)
    r = subprocess.run([TECTONIC, "-X", "compile", "resgraph.tex"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-3000:] + r.stderr[-3000:])
    pdf = fitz.open(os.path.join(work, "resgraph.pdf"))
    if len(pdf) != len(ps):
        sys.exit("expected %d pages, got %d" % (len(ps), len(pdf)))
    widths = []
    for k, page in enumerate(pdf, 1):
        name = "c4_resg_%02d.png" % k
        page.get_pixmap(dpi=DPI).save(os.path.join(HERE, "figs", name))
        widths.append(page.rect.width)
    # insert from the bottom up so earlier offsets stay valid
    for k in range(len(ps), 0, -1):
        at = ps[k - 1][0]
        w = min(widths[k - 1], 515.0)
        name = "c4_resg_%02d" % k
        block = ("\n" + MARK + name + " (generated by resgraph.py; do not edit)\n"
                 + BS + "penalty0" + BS + "vspace{2pt}\n"
                 + BS + "begin{center}" + BS + "includegraphics[width=%.1fpt]{figs/%s.png}"
                 % (w, name) + BS + "end{center}\n" + MARK + "end\n")
        src = src[:at] + block + src[at:]
    open(TEX, "w", encoding="utf-8").write(src)
    print("%d resolution graphs written" % len(ps))


if __name__ == "__main__":
    main()
