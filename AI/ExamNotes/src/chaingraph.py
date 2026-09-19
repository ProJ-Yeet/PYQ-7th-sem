# -*- coding: utf-8 -*-
"""Forward- and backward-chaining figures for the two worked chaining examples.

  c4_chain_west_fwd.png   ch4-num P6 (81 Ash): Colonel West by forward chaining,
                          three rows (given facts, iteration 1, iteration 2)
  c4_chain_west_bwd.png   the same premises backward: goal at the top, each
                          sub-goal expanded until it meets a fact, the binding
                          under the node that produced it
  c4_chain_flu.png        ch4 4.6 rule-based reasoning: the fever/cough/flu
                          example both ways, side by side

The facts, rules and bindings below are the ones the worked text prints; if the
text changes, change them here and rerun. Figures go in through marked blocks,
exactly like resgraph.py: never edit the PNGs or the blocks by hand.

    python chaingraph.py
"""
import os, re, subprocess, sys

import fitz

import resgraph as R

HERE = R.HERE
BS = chr(92)
MARK = "% chaingraph:"

STYLE = (r"[font=\footnotesize, >=latex,"
         r" kb/.style={draw=acc, fill=accL, text=ink, rounded corners=2pt, inner sep=3pt},"
         r" res/.style={draw=mkc, fill=mkL, text=ink, rounded corners=2pt, inner sep=3pt},"
         r" goal/.style={res, very thick},"
         r" note/.style={text=sub, font=\scriptsize},"
         r" row/.style={text=sub, font=\scriptsize\bfseries, anchor=east},"
         r" arr/.style={->, draw=sub, thick}]")

# (name, style, x, y, text, note under it)
WEST_FWD = [
    ("mi", "kb", 0.8, 0.0, "Missile(M_1)", ""),
    ("ow", "kb", 4.6, 0.0, "Owns(Nono, M_1)", ""),
    ("am", "kb", 8.6, 0.0, "American(West)", ""),
    ("en", "kb", 12.6, 0.0, "Enemy(Nono, America)", ""),
    ("we", "res", 0.8, 1.8, "Weapon(M_1)", r"rule 4, $[M_1/x]$"),
    ("se", "res", 4.2, 1.8, "Sells(West, M_1, Nono)", r"rule 3, $[M_1/x]$"),
    ("ho", "res", 12.6, 1.8, "Hostile(Nono)", r"rule 5, $[Nono/x]$"),
    ("cr", "goal", 8.6, 3.7, "Criminal(West)", r"rule 1, $[West/p,\,M_1/q,\,Nono/r]$"),
]
WEST_FWD_EDGES = [("mi", "we"), ("mi", "se"), ("ow", "se"), ("en", "ho"),
                  ("am", "cr"), ("we", "cr"), ("se", "cr"), ("ho", "cr")]
WEST_FWD_ROWS = [(0.0, "given facts"), (1.8, "iteration 1"), (3.7, "iteration 2")]

WEST_BWD = [
    ("cr", "goal", 6.0, 0.0, "Criminal(West)", r"rule 1, $[West/p]$"),
    ("am", "kb", 0.4, -1.9, r"American(West)\;\checkmark", "fact"),
    ("we", "res", 3.6, -1.9, "Weapon(q)", "rule 4"),
    ("se", "res", 7.4, -1.9, "Sells(West, M_1, r)", "rule 3"),
    ("ho", "res", 12.4, -1.9, "Hostile(Nono)", r"rule 5, $[Nono/x]$"),
    ("m1", "kb", 3.6, -3.8, r"Missile(M_1)\;\checkmark", r"$[M_1/q]$"),
    ("m2", "kb", 5.9, -3.8, r"Missile(M_1)\;\checkmark", ""),
    ("o2", "kb", 8.9, -3.8, r"Owns(Nono, M_1)\;\checkmark", r"$[Nono/r]$"),
    ("en", "kb", 12.9, -3.8, r"Enemy(Nono, America)\;\checkmark", ""),
]
WEST_BWD_EDGES = [("cr", "am"), ("cr", "we"), ("cr", "se"), ("cr", "ho"),
                  ("we", "m1"), ("se", "m2"), ("se", "o2"), ("ho", "en")]

FLU = [
    ("fe", "kb", 0.0, 0.0, r"\text{fever}", ""),
    ("co", "kb", 2.4, 0.0, r"\text{cough}", ""),
    ("fl", "res", 1.2, 1.5, r"\text{flu}", "R1 fires"),
    ("pr", "goal", 1.2, 3.0, r"\text{prescribe rest}", "R2 fires"),
    ("bp", "goal", 8.2, 3.0, r"\text{prescribe rest}", "goal"),
    ("bf", "res", 8.2, 1.5, r"\text{flu}\;?", "sub-goal, by R2"),
    ("bfe", "kb", 7.0, 0.0, r"\text{fever}\;\checkmark", "fact"),
    ("bco", "kb", 9.4, 0.0, r"\text{cough}\;\checkmark", "fact"),
]
FLU_EDGES = [("fe", "fl"), ("co", "fl"), ("fl", "pr")]
FLU_BWD_EDGES = [("bp", "bf"), ("bf", "bfe"), ("bf", "bco")]


def nodes(spec):
    out = []
    for name, st, x, y, text, note in spec:
        lab = r"$%s$" % text
        if note:
            lab += r"\\{\color{sub}\scriptsize %s}" % note
        out.append(r"\node[%s, align=center] (%s) at (%.2f,%.2f) {%s};" % (st, name, x, y, lab))
    return out


def pic(spec, edges, rows=(), down=False, extra=()):
    L = [r"\begin{tikzpicture}" + STYLE] + nodes(spec)
    for a, b in edges:
        # forward: premise up into the fact it derived; backward: goal down
        # into the sub-goal it needs
        L.append(r"\draw[arr] (%s.%s) -- (%s.%s);"
                 % (a, "south" if down else "north", b, "north" if down else "south"))
    xmin = min(s[2] for s in spec) - 1.6
    for y, t in rows:
        L.append(r"\node[row] at (%.2f,%.2f) {%s};" % (xmin, y, t))
    L += list(extra)
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def figures():
    flu_extra = [r"\draw[arr] (%s.south) -- (%s.north);" % e for e in FLU_BWD_EDGES]
    flu_extra += [r"\node[row, anchor=south] at (1.2,3.9) {FORWARD: from the facts up};",
                  r"\node[row, anchor=south] at (8.2,3.9) {BACKWARD: from the goal down};"]
    return [
        ("c4_chain_west_fwd", pic(WEST_FWD, WEST_FWD_EDGES, WEST_FWD_ROWS)),
        ("c4_chain_west_bwd", pic(WEST_BWD, WEST_BWD_EDGES, down=True)),
        ("c4_chain_flu", pic(FLU, FLU_EDGES, extra=flu_extra)),
    ]


# where each figure goes: after the \sbs block that holds this text
PLACES = [
    ("ch4-num.tex", "Forward chaining, iteration by iteration",
     ["c4_chain_west_fwd", "c4_chain_west_bwd"]),
    ("ch4.tex", "Two directions, one rule base", ["c4_chain_flu"]),
]


def strip_blocks(src):
    return re.sub(r"\n" + re.escape(MARK) + r"c4_chain.*?\n" + re.escape(MARK) + r"end\n",
                  "\n", src, flags=re.S)


def main():
    figs = figures()
    work = os.path.join(HERE, "figs", "_resgraph")
    os.makedirs(work, exist_ok=True)
    # amssymb's \checkmark: it works in math mode, pifont's \ding does not
    doc = R.PRE +"\n\n".join(p for _, p in figs) + "\n\\end{document}\n"
    open(os.path.join(work, "chaingraph.tex"), "w", encoding="utf-8").write(doc)
    r = subprocess.run([R.TECTONIC, "-X", "compile", "chaingraph.tex"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-3000:] + r.stderr[-3000:])
    pdf = fitz.open(os.path.join(work, "chaingraph.pdf"))
    width = {}
    for (name, _), page in zip(figs, pdf):
        page.get_pixmap(dpi=R.DPI).save(os.path.join(HERE, "figs", name + ".png"))
        width[name] = min(page.rect.width, 480.0)
    for fname, anchor, names in PLACES:
        path = os.path.join(HERE, fname)
        src = strip_blocks(open(path, encoding="utf-8").read())
        at = R.enclosing_sbs_end(src, src.index(anchor))
        block = "\n" + MARK + names[0] + " (generated by chaingraph.py; do not edit)\n"
        for n in names:
            block += (BS + "penalty0" + BS + "vspace{2pt}\n" + BS + "begin{center}"
                      + BS + "includegraphics[width=%.1fpt]{figs/%s.png}" % (width[n], n)
                      + BS + "end{center}\n")
        block += MARK + "end\n"
        open(path, "w", encoding="utf-8").write(src[:at] + block + src[at:])
    print("%d chaining figures written" % len(figs))


if __name__ == "__main__":
    main()
