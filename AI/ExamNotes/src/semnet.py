# -*- coding: utf-8 -*-
"""Draw the answer net under every semantic-net set in ch5-num.tex.

Each set already carries its answer as an arc table:

    Person & \\code{isa} & Mammal \\\\

This script reads those tables and draws them. The ARCS come from the table,
so a drawing cannot disagree with the text; only the node POSITIONS are kept
here, one layout per table, in the order the tables appear. A node in the
table with no position, or a position with no node, stops the run: edit the
table and the layout together.

Published figures (lecture decks, the textbook) stay where they are: this adds
the drawing of the paper's own sentences beside them, never a redraw of theirs.

Layout convention, from the recipe at the top of the file: most general class
at the top, isa / instance pointing up, individuals low, values sideways.

    python semnet.py
"""
import os, re, subprocess, sys

import fitz

import resgraph as R

HERE = R.HERE
TEX = os.path.join(HERE, "ch5-num.tex")
BS = chr(92)
MARK = "% semnet:"

# one dict per arc table, in file order: node text -> (x, y) in cm
LAYOUTS = [
    # 5.N.1 Sakti Gauchan
    {"Mammal": (0, 3.2), "Person": (0, 1.6), "Nose": (4, 1.6),
     "Sakti Gauchan": (0, 0), "Nepalese team": (-4.2, 0), "Red/Blue": (4, 0)},
    # 5.N.2 Pee-wee-Reese
    {"Person": (0, 5.2), "Adult Male": (0, 3.9), "Baseball Player": (0, 2.6),
     "Fielder": (0, 1.3), "Pee-wee-Reese": (0, 0), "5.10": (4.2, 3.9),
     "0.252": (4.2, 2.6), "Brooklyn Dodger": (4.2, 0)},
    # 5.N.3 Tom, 82 Bh / 81 Ch
    {"Animal": (0, 4.5), "Mammal": (-2, 3.1), "Bird": (3, 1.6), "Cat": (-2, 1.6),
     "Tom": (-2, 0), "Fur": (-5.8, 3.3), "Cream": (-5.8, 2.1), "Mat": (-5.8, 1.0),
     "Ginger": (-5.8, -0.2), "Sudeep": (1.6, 0), "20": (4.4, 0)},
    # 5.N.3 Tom, 79 Bh variant
    {"Animal": (0, 4.5), "Mammal": (-2, 3.1), "Rat": (3, 3.1), "Cat": (-2, 1.6),
     "Tom": (-2, 0), "Cheese": (6, 3.1), "Baby": (-5.8, 3.3), "Milk": (-5.8, 2.1),
     "Bed": (-5.8, 1.0), "Black": (-5.8, -0.2), "Ram": (1.6, 0)},
    # 5.N.4 mammals, fur and water
    {"Animal": (0, 3.0), "Mammal": (-2, 1.5), "Fish": (3, 1.5), "Cat": (-4.5, 0),
     "Bear": (-2, 0), "Whale": (0.5, 0), "Fur": (-3.25, -1.6), "Water": (2.2, -1.6),
     "Vertebra": (-5.8, 1.5)},
    # 5.N.5 Fido
    {"Animal": (0, 4.2), "Mammal": (0, 2.8), "Dog": (0, 1.4), "Fido": (0, 0),
     "Fur": (3.6, 2.8), "Rohit": (-3.6, 0), "Ginger": (3.6, 0)},
    # 5.N.6 employees and supervisors
    {"Human": (0, 3.0), "Employee": (-3, 1.5), "Supervisor": (0, 1.5),
     "Hari": (-3, 0), "Ram": (0, 0), "Sita": (3, 0)},
    # 5.N.7 Ram and Jhilke
    {"Animal": (0, 3.0), "Person": (-3, 1.5), "Cat": (0.5, 1.5), "Fish": (3.6, 1.5),
     "Ram": (-3, 0), "Jhilke": (0.5, 0)},
    # 5.N.8 Tweety and Sweety
    {"Bird": (0, 2.8), "Fly": (3.8, 2.8), "Crow": (1.8, 1.2), "Sparrow": (4.4, 1.2),
     "Wing": (4.4, -0.4), "Tweety": (-3.2, 1.2), "Sweety": (0.3, -0.6),
     "Beak": (-6.2, 1.2), "Red": (-6.2, -0.6)},
    # 5.N.9 the AI course
    {"Person": (-4, 5.0), "Student": (-5.6, 3.4), "Teacher": (-2.4, 3.4),
     "Ram": (-5.6, 1.6), "Course": (1.5, 3.4), "Elective": (4.9, 3.4),
     "Chapter": (4.9, 5.0), "AI (CT 710)": (1.5, 1.6), "Search": (1.5, 0),
     "A*": (-1.8, 0), "3": (5.2, 2.1), "IV/I": (5.2, 1.2), "BEI": (5.2, 0.3)},
]

# relations that hold both ways get a double-headed arrow
SYMMETRIC = {"married-to"}


def tables(src):
    """[(end_offset, [(from, link, to)])] for every From/Link/To table."""
    out = []
    head = BS + "thead{From} & " + BS + "thead{Link}"
    for m in re.finditer(re.escape(BS) + r"begin\{tabularx\}", src):
        end = src.index(BS + "end{tabularx}", m.end())
        body = src[m.end():end]
        if head not in body:
            continue
        rows = body.split(BS + "midrule", 1)[1].split(BS + "bottomrule")[0]
        arcs = []
        for row in rows.split(BS + BS):
            cells = [c.strip() for c in row.split("&")]
            if len(cells) < 3:
                continue
            link = re.search(re.escape(BS) + r"code\{([^}]*)\}", cells[1])
            to = re.split(re.escape(BS) + r"quad", cells[2])[0].strip()
            arcs.append((cells[0], link.group(1) if link else cells[1], to))
        out.append((m.start(), arcs))
    return out


def kinds(arcs):
    indiv = {a for a, l, b in arcs if l == "instance"}
    classes = ({b for a, l, b in arcs if l in ("isa", "instance")}
               | {a for a, l, b in arcs if l == "isa"})
    return lambda n: "ind" if n in indiv else ("cls" if n in classes else "val")


def tikz(arcs, pos):
    nodes = {a for a, _, _ in arcs} | {b for _, _, b in arcs}
    if nodes != set(pos):
        raise ValueError("table and layout disagree: only in table %s, only in layout %s"
                         % (sorted(nodes - set(pos)), sorted(set(pos) - nodes)))
    kind = kinds(arcs)
    ids = {n: "v%d" % i for i, n in enumerate(sorted(nodes))}
    L = [r"\begin{tikzpicture}[font=\footnotesize, >=latex,"
         r" cls/.style={draw=acc, fill=accL, text=ink, rounded corners=2pt, inner sep=3pt},"
         r" ind/.style={draw=mkc, fill=mkL, text=ink, rounded corners=2pt, inner sep=3pt},"
         r" val/.style={draw=sub, fill=white, text=ink, rounded corners=6pt, inner sep=3pt},"
         r" lnk/.style={font=\scriptsize\ttfamily, text=sub, fill=white, inner sep=1pt}]"]
    for n in sorted(nodes):
        x, y = pos[n]
        L.append(r"\node[%s] (%s) at (%.2f,%.2f) {%s};" % (kind(n), ids[n], x, y, n))
    pairs = {}
    for a, l, b in arcs:
        pairs.setdefault(frozenset((a, b)), []).append((a, l, b))
    for a, l, b in arcs:
        arrow = "<->" if l in SYMMETRIC else "->"
        if len(pairs[frozenset((a, b))]) > 1:
            # two arcs between one pair (child-of / parent-of) bow apart, each
            # label on the outside of its own bow
            how, lab = "bend left=35", "lnk, auto, fill=none, pos=0.3"
        elif abs(pos[a][0] - pos[b][0]) < 0.3:
            # a sloped label on a short vertical link is longer than the gap
            # and runs into both boxes; stand it beside the link instead
            how, lab = "", "lnk, right, fill=none"
        else:
            how, lab = "", "lnk, sloped"
        L.append(r"\draw[%s, draw=sub, thick] (%s) to[%s] node[%s] {%s} (%s);"
                 % (arrow, ids[a], how, lab, l, ids[b]))
    # legend
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    lx, ly = min(xs) - 0.6, min(ys) - 1.2
    L.append(r"\node[cls, anchor=west, font=\scriptsize] (k1) at (%.2f,%.2f) {class};" % (lx, ly))
    L.append(r"\node[ind, anchor=west, font=\scriptsize, right=2mm of k1] (k2) {individual};")
    L.append(r"\node[val, anchor=west, font=\scriptsize, right=2mm of k2] {value};")
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def strip_blocks(src):
    return re.sub(r"\n" + re.escape(MARK) + r"c5_net_\d+.*?\n" + re.escape(MARK) + r"end\n",
                  "", src, flags=re.S)


def main():
    src = strip_blocks(open(TEX, encoding="utf-8").read())
    ts = tables(src)
    if len(ts) != len(LAYOUTS):
        sys.exit("%d arc tables but %d layouts" % (len(ts), len(LAYOUTS)))
    pics = [tikz(arcs, pos) for (_, arcs), pos in zip(ts, LAYOUTS)]
    work = os.path.join(HERE, "figs", "_resgraph")
    os.makedirs(work, exist_ok=True)
    doc = R.PRE.replace(r"\begin{document}",
                        BS + "usetikzlibrary{positioning}\n" + BS + "begin{document}")
    doc += "\n\n".join(pics) + "\n\\end{document}\n"
    open(os.path.join(work, "semnet.tex"), "w", encoding="utf-8").write(doc)
    r = subprocess.run([R.TECTONIC, "-X", "compile", "semnet.tex"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-3000:] + r.stderr[-3000:])
    pdf = fitz.open(os.path.join(work, "semnet.pdf"))
    width = []
    for k, page in enumerate(pdf, 1):
        page.get_pixmap(dpi=R.DPI).save(os.path.join(HERE, "figs", "c5_net_%02d.png" % k))
        width.append(min(page.rect.width, 430.0))
    for k in range(len(ts), 0, -1):
        at = R.enclosing_sbs_end(src, ts[k - 1][0])
        name = "c5_net_%02d" % k
        block = ("\n" + MARK + name + " (generated by semnet.py; do not edit)\n"
                 + BS + "penalty0" + BS + "vspace{2pt}\n"
                 + BS + "begin{center}" + BS + "includegraphics[width=%.1fpt]{figs/%s.png}"
                 % (width[k - 1], name) + BS + "end{center}\n" + MARK + "end\n")
        src = src[:at] + block + src[at:]
    open(TEX, "w", encoding="utf-8").write(src)
    print("%d semantic nets written" % len(ts))


if __name__ == "__main__":
    main()
