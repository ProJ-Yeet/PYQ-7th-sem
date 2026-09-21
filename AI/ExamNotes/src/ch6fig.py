# -*- coding: utf-8 -*-
"""Draw the finished ID3 decision tree under every decision-tree problem in ch6-num.tex.

The notes compute each split as a gain table. This script runs ID3 on the
same data table and draws the tree it produces. Every internal node shows
the rows that reach it, its class counts, its entropy, the gain of the
attribute that won and the gain of the runner-up. Every leaf shows its rows
and its class. For the mushroom island, U, V and W are dropped through the
tree and drawn under the leaf they land in.

The data tables are imported from verify.py, so there is one transcription.
The exit test is replay. Every node's winning gain and runner-up gain,
formatted to four places, must be printed in ch6-num.tex. Every leaf's path
must be printed there as a \\code{A = v, B = w -> class} rule. The winner at
every node must be unique, so the tree does not depend on tie-breaking.

    python ch6fig.py            regenerate every figure and its \\includegraphics block
    python ch6fig.py --report   run the checks only

Figures are PNGs so tools/anki_from_notes.py carries them onto the cards.
"""
import math
import os
import re
import subprocess
import sys
from collections import Counter

import fitz

import verify

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch6-num.tex")
FIGS = os.path.join(HERE, "figs")
TECTONIC = os.path.join(HERE, "..", "..", "..", "Data Mining", "ExamNotes", "src",
                        "tectonic.exe")
BS = chr(92)
MARK = "% ch6fig:"
SLOT = "% ch6fig:slot "
DPI = 300
MAXPT = 515.0
SCALE = 1.4       # the trees are drawn in tiny type; print them larger

# display names: verify.py abbreviates two attributes
SHOW = {"Temp": "Temperature"}


def H(labels):
    n = len(labels)
    return -sum(v / n * math.log2(v / n) for v in Counter(labels).values() if v)


def id3(rows, attrs, tgt, pos, path=()):
    """Return the tree as nested dicts, one per node, with the evidence kept."""
    labels = [r[tgt] for r in rows]
    node = {"ids": [r["_id"] for r in rows], "p": labels.count(pos),
            "n": len(labels) - labels.count(pos), "h": H(labels), "path": path}
    if node["h"] < 1e-12 or not attrs:
        node["leaf"] = Counter(labels).most_common(1)[0][0]
        return node
    gains = {}
    for a in attrs:
        res = 0.0
        for v in {r[a] for r in rows}:
            sub = [r[tgt] for r in rows if r[a] == v]
            res += len(sub) / len(rows) * H(sub)
        gains[a] = node["h"] - res
    ranked = sorted(gains, key=lambda a: -gains[a])
    best, second = ranked[0], ranked[1]
    if abs(gains[best] - gains[second]) < 1e-9:
        sys.exit("tie for the split at %s: %s / %s" % (path, best, second))
    node.update(attr=best, gain=gains[best], second=second, sgain=gains[second])
    vals = []
    for r in rows:                       # value order = first appearance in the table
        if r[best] not in vals:
            vals.append(r[best])
    node["kids"] = [(v, id3([r for r in rows if r[best] == v],
                            [a for a in attrs if a != best], tgt, pos,
                            path + ((best, v),)))
                    for v in vals]
    return node


def classify(node, row):
    while "leaf" not in node:
        node = dict(node["kids"])[row[node["attr"]]]
    return node


def leaves(node):
    if "leaf" in node:
        return [node]
    return [l for _, k in node["kids"] for l in leaves(k)]


def internals(node):
    if "leaf" in node:
        return []
    return [node] + [i for _, k in node["kids"] for i in internals(k)]


def check(name, tree, cls, tex):
    flat = re.sub(r"\s+", " ", tex)
    for nd in internals(tree):
        for g in (nd["gain"], nd["sgain"]):
            s = "%.4f" % g
            if s not in flat:
                sys.exit("%s: gain %s at %s is not printed in ch6-num.tex"
                         % (name, s, nd["path"] or "root"))
    for lf in leaves(tree):
        rule = ", ".join("%s = %s" % (SHOW.get(a, a), v) for a, v in lf["path"])
        rule += " -> " + cls[lf["leaf"]]
        if (BS + "code{" + rule + "}") not in flat:
            sys.exit("%s: leaf rule not printed: %s" % (name, rule))


# =====================================================================
#  Drawing
# =====================================================================
PRE = r"""\documentclass[border=4pt, tikz]{standalone}
\usepackage[default]{lato}
\usepackage{amsmath, amssymb, xcolor, tikz}
\usetikzlibrary{arrows.meta}
\definecolor{ink}{HTML}{16202A}\definecolor{sub}{HTML}{6B7785}
\definecolor{acc}{HTML}{2563A8}\definecolor{accL}{HTML}{D6E4F5}
\definecolor{mkc}{HTML}{C2410C}\definecolor{mkL}{HTML}{FDEBD9}
\definecolor{gd}{HTML}{15803D}\definecolor{gdL}{HTML}{DCFCE7}
\definecolor{ruleL}{HTML}{DEE3E8}
\tikzset{
  inode/.style={draw=acc, fill=accL, rounded corners=2pt, line width=0.7pt,
                align=center, inner sep=2.5pt, text width=3.5cm, font=\tiny},
  pleaf/.style={draw=gd, fill=gdL, rounded corners=6pt, line width=0.7pt,
                align=center, inner sep=2.5pt, text width=2.25cm, font=\tiny},
  nleaf/.style={draw=mkc, fill=mkL, rounded corners=6pt, line width=0.7pt,
                align=center, inner sep=2.5pt, text width=2.25cm, font=\tiny},
  edge/.style={draw=sub, line width=0.6pt, -{Stealth[length=2.2mm]}},
  elab/.style={fill=white, inner sep=1.2pt, font=\scriptsize\bfseries, text=ink},
  probe/.style={font=\tiny\bfseries, text=ink, fill=white, draw=ink,
                rounded corners=1pt, inner sep=1.5pt},
}
\begin{document}
"""

SLOTW = 2.55      # cm per leaf
LEVELH = 2.05     # cm per level


def hnum(h):
    return "0" if h < 5e-5 else "%.4f" % h


def ids(lst):
    return ", ".join(str(i) for i in lst)


def layout(node, depth, cursor):
    node["y"] = -depth * LEVELH
    if "leaf" in node:
        node["x"] = cursor[0] * SLOTW
        cursor[0] += 1
        return
    for _, k in node["kids"]:
        layout(k, depth + 1, cursor)
    xs = [k["x"] for _, k in node["kids"]]
    node["x"] = (min(xs) + max(xs)) / 2


def draw(tree, cls, pos):
    layout(tree, 0, [0])
    L = [BS + "begin{tikzpicture}"]
    count = [0]

    def emit(nd):
        count[0] += 1
        nd["tag"] = "n%d" % count[0]
        who = ("all %d rows" % len(nd["ids"]) if nd is tree
               else "rows " + ids(nd["ids"]))
        stats = r"%s\\%d\,+ \;\;%d\,$-$ \quad \textit{H} = %s" % (
            who, nd["p"], nd["n"], hnum(nd["h"]))
        if "leaf" in nd:
            style = "pleaf" if nd["leaf"] == pos else "nleaf"
            txt = r"{\scriptsize\bfseries %s}\\%s" % (cls[nd["leaf"]], stats)
        else:
            style = "inode"
            txt = (r"{\scriptsize\bfseries\color{acc} split on %s}\\%s\\"
                   r"\textbf{Gain %.4f}\; {\color{sub}(next: %s %.4f)}"
                   % (SHOW.get(nd["attr"], nd["attr"]), stats, nd["gain"],
                      SHOW.get(nd["second"], nd["second"]), nd["sgain"]))
        L.append(r"\node[%s] (%s) at (%.3f,%.3f) {%s};"
                 % (style, nd["tag"], nd["x"], nd["y"], txt))
        for v, k in nd.get("kids", []):
            emit(k)
            L.append(r"\draw[edge] (%s.south) -- node[elab] {%s} (%s.north);"
                     % (nd["tag"], v, k["tag"]))

    emit(tree)
    L.append(BS + "end{tikzpicture}")
    return "\n".join(L)


# =====================================================================
#  The four problems
# =====================================================================
def numbered(rows, key=None):
    out = []
    for i, r in enumerate(rows, 1):
        r = dict(r)
        r["_id"] = r[key] if key else i
        out.append(r)
    return out


def build(tex):
    figs = []
    wcols = ["Outlook", "Temp", "Humidity", "Windy"]
    yn = {"Yes": "Yes", "No": "No"}
    for name, rows in (("c6_tree_golf", verify.GOLF), ("c6_tree_cricket", verify.CRICKET)):
        t = id3(numbered(rows), wcols, "Play", "Yes")
        check(name, t, yn, tex)
        figs.append((name, draw(t, yn, "Yes")))

    letters = "ABCDEFGH"
    mush = [dict(r, Ex=letters[i]) for i, r in enumerate(verify.MUSH)]
    ed = {"1": "Edible", "0": "Poisonous"}
    t = id3(numbered(mush, "Ex"), ["NotHeavy", "Smelly", "Spotted", "Smooth"],
            "Edible", "1")
    check("c6_tree_mush", t, ed, tex)
    unknown = {"U": dict(NotHeavy="0", Smelly="1", Spotted="1", Smooth="1"),
               "V": dict(NotHeavy="1", Smelly="1", Spotted="0", Smooth="1"),
               "W": dict(NotHeavy="1", Smelly="1", Spotted="0", Smooth="0")}
    # the verdicts the notes print for U, V, W must be the tree's
    for ex, row in unknown.items():
        want = ed[classify(t, row)["leaf"]]
        pat = BS + "code{" + ex + ":"
        i = tex.find(pat)
        if i < 0 or (BS + "textbf{" + want + "}") not in tex[i:tex.find("\n", i)]:
            sys.exit("c6_tree_mush: %s should read %s in ch6-num.tex" % (ex, want))
    fig = draw(t, ed, "1")
    # probes are placed after drawing, once each leaf has its tag
    land = {}
    for ex, row in unknown.items():
        land.setdefault(classify(t, row)["tag"], []).append(ex)
    extra = []
    for tag, exs in land.items():
        extra.append(r"\node[probe, anchor=north] at ([yshift=-3pt]%s.south) {%s %s here};"
                     % (tag, " and ".join(exs), "land" if len(exs) > 1 else "lands"))
    fig = fig.replace(BS + "end{tikzpicture}", "\n".join(extra) + "\n" + BS + "end{tikzpicture}")
    figs.append(("c6_tree_mush", fig))

    ud = {"Up": "Up", "Down": "Down"}
    t = id3(numbered(verify.PROFIT), ["Age", "Competition", "Type"], "Profit", "Up")
    check("c6_tree_profit", t, ud, tex)
    figs.append(("c6_tree_profit", draw(t, ud, "Up")))
    return figs


CAPTION = {
    "c6_tree_golf": "The finished tree: play golf (rows numbered 1 to 14 top to bottom)",
    "c6_tree_cricket": "The finished tree: play cricket, two tests instead of three",
    "c6_tree_mush": "The finished tree: the mushroom island, with U, V and W dropped through it",
    "c6_tree_profit": "The finished tree: profit (rows numbered 1 to 10 top to bottom)",
}


def strip_blocks(src):
    return re.sub(r"(?m)^" + re.escape(MARK) + r"c6_\w+ \(generated.*?^"
                  + re.escape(MARK) + r"end\n", "", src, flags=re.S)


def main():
    tex = strip_blocks(open(TEX, encoding="utf-8").read())
    figs = build(tex)
    if "--report" in sys.argv:
        for name, _ in figs:
            print("ok  %s" % name)
        return
    work = os.path.join(FIGS, "_ch6fig")
    os.makedirs(work, exist_ok=True)
    doc = PRE + "\n\n".join(b for _, b in figs) + "\n" + BS + "end{document}\n"
    open(os.path.join(work, "ch6fig.tex"), "w", encoding="utf-8").write(doc)
    r = subprocess.run([TECTONIC, "-X", "compile", "ch6fig.tex"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-4000:] + r.stderr[-4000:])
    pdf = fitz.open(os.path.join(work, "ch6fig.pdf"))
    if len(pdf) != len(figs):
        sys.exit("expected %d pages, got %d" % (len(figs), len(pdf)))
    widths, heights = {}, {}
    for (name, _), page in zip(figs, pdf):
        page.get_pixmap(dpi=DPI).save(os.path.join(FIGS, name + ".png"))
        widths[name] = min(page.rect.width * SCALE, MAXPT)
        heights[name] = page.rect.height * widths[name] / page.rect.width
    if "--figs-only" in sys.argv:
        print("%d figures rendered, .tex untouched" % len(figs))
        return
    src = tex.rstrip("\n") + "\n"
    for name, _ in figs:
        anchor = SLOT + name
        i = src.find(anchor)
        if i < 0:
            sys.exit("no slot for %s in ch6-num.tex" % name)
        if src[i - 1:i] != "\n" or not src[i + len(anchor):].startswith("\n"):
            sys.exit("slot for %s is not alone on its line" % name)
        j = src.find("\n", i) + 1
        block = (MARK + name + " (generated by ch6fig.py; do not edit)\n"
                 + BS + "penalty0" + BS + "vspace{3pt}\n"
                 + BS + "Needspace{%.0fpt}\n" % (heights[name] + 24)
                 + BS + "lead{" + CAPTION[name] + "}\n"
                 + BS + "begin{center}" + BS
                 + "includegraphics[width=%.1fpt]{figs/%s.png}" % (widths[name], name)
                 + BS + "end{center}\n"
                 + BS + "par" + BS + "Needspace{16" + BS + "baselineskip}\n"
                 + MARK + "end\n")
        src = src[:j] + block + src[j:]
    open(TEX, "w", encoding="utf-8").write(src)
    print("%d figures written" % len(figs))


if __name__ == "__main__":
    main()
