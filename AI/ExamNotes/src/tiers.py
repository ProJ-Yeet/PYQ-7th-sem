# -*- coding: utf-8 -*-
"""Check every tier chip in the chapter sources against its own year tags.

A chip such as \\tS{8} claims "asked in 8 of the 41 papers". The year-tag line
directly under it lists which papers those are. Those two must agree, and the
TIER must match the count under the thresholds this subject uses. Counting by
eye got three chips wrong in Chapter 2 alone, so it is done here instead.

Thresholds (stated in abbrev.tex and in NOTES-BUILD-PROGRESS.md):

    TOP  \\tS{n}   n >= 8
    HOT  \\tF{n}   4 <= n <= 7
    PIN  \\tP{n}   1 <= n <= 3   and the topic is worth >= 6 marks

A paper is keyed on (course code, year, month), because the same year code
names different papers under different codes: plain = CT653, \\texttt = CT710,
\\textit = CT78506. \\textbf is the regular/back axis and is ignored here.

Run from inside this src\\ folder:   python tiers.py [ch2] [ch3-num] ...
With no args it checks every ch*.tex.
"""
import glob
import io
import os
import re
import sys

B = chr(92)

HERE = os.path.dirname(os.path.abspath(__file__))

CHIP = re.compile(re.escape(B) + r"t([SFP])\{(\d*)\}")
PAPER = re.compile(
    r"(?:(" + re.escape(B) + r"text(?:tt|it))\{)?"
    r"\b(6\d|7\d|8\d)\s+(Ba|Jth|Asa|Shr|Bh|Ash|Ka|Mng|Po|Ma|Ch)\b")
MARKS = re.compile(re.escape(B) + r"m\{([\d+]+)\}")
CODE = {B + "texttt": "710", B + "textit": "785"}

TIER = {"S": "TOP", "F": "HOT", "P": "PIN"}


def papers(text):
    out = set()
    for m in PAPER.finditer(text):
        out.add("%s/%s %s" % (CODE.get(m.group(1), "653"), m.group(2), m.group(3)))
    return out


def first_yr(tail):
    """The contents of the first \\yr{...} group in `tail`, brace-balanced.

    Brace counting rather than a regex: a year tag routinely contains nested
    groups (\\textbf{\\texttt{82 Bh}} \\m{2+6}), so a non-greedy match stops in
    the wrong place and a greedy one runs into the next paragraph.
    """
    i = tail.find(B + "yr{")
    if i < 0:
        return ""
    j = i + len(B) + 3
    depth = 1
    while j < len(tail) and depth:
        if tail[j] == "{":
            depth += 1
        elif tail[j] == "}":
            depth -= 1
        j += 1
    return tail[i + len(B) + 3:j - 1]


def tier_for(n):
    if n >= 8:
        return "S"
    if n >= 4:
        return "F"
    return "P"


def check(path):
    src = io.open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    bad = []
    for m in CHIP.finditer(src):
        kind, claimed = m.group(1), m.group(2)
        line_no = src.count("\n", 0, m.start()) + 1
        if not claimed:
            continue                      # \tS{} in abbrev.tex is a legend, not a claim
        claimed = int(claimed)
        # A chip counts exactly the papers in the FIRST \yr{...} group after it,
        # and only when that group is in the same paragraph and before the next
        # chip. Two reasons for the bound: anything past the following
        # \gap$\cdot$\gap is commentary that often names OTHER papers ("growth
        # areas asked at ...", "also inside the Turing question at ..."), and a
        # chip cited inside a Read-this-first list has no year tags of its own,
        # so an unbounded search would charge it with the next topic's.
        nxt = CHIP.search(src, m.end())
        stops = [len(src)]
        if nxt:
            stops.append(nxt.start())
        para = src.find("\n\n", m.end())
        if para > 0:
            stops.append(para)
        # ... and at the next list item. A Read-this-first bullet cites a chip
        # with no year tags of its own, and without this bound the search runs
        # into a LATER bullet's \yr{} and charges this chip with those papers.
        item = src.find(B + "item", m.end())
        if item > 0:
            stops.append(item)
        window = src[m.end():min(stops)]
        found = papers(first_yr(window)) if (B + "yr{") in window else None
        # the heading above the chip may carry mark chips; the tier rule needs them
        head = src[max(0, m.start() - 400):m.start()]
        marks = [sum(int(x) for x in v.split("+")) for v in MARKS.findall(head)]
        top_mark = max(marks) if marks else 0

        if found and len(found) != claimed:
            bad.append("%s:%d  chip %s{%d} but its year tags list %d papers: %s"
                       % (name, line_no, TIER[kind], claimed, len(found),
                          " ".join(sorted(found))))
        want = tier_for(claimed)
        if want != kind:
            bad.append("%s:%d  %d papers should be tier %s, chip says %s"
                       % (name, line_no, claimed, TIER[want], TIER[kind]))
        if kind == "P" and top_mark and top_mark < 6:
            bad.append("%s:%d  PIN needs >=6 marks, heading's largest chip is %d"
                       % (name, line_no, top_mark))
    return bad


def main():
    want = sys.argv[1:]
    files = ([os.path.join(HERE, w if w.endswith(".tex") else w + ".tex")
              for w in want]
             if want else
             sorted(f for f in glob.glob(os.path.join(HERE, "ch*.tex"))
                    if "standalone" not in f))
    bad = []
    n = 0
    for f in files:
        if not os.path.exists(f):
            print("no such file:", f)
            continue
        n += len(CHIP.findall(io.open(f, encoding="utf-8").read()))
        bad.extend(check(f))
    if bad:
        print("%d problem(s) across %d chips:\n" % (len(bad), n))
        for b in bad:
            print("  -", b)
        return 1
    print("all %d tier chips agree with their year tags" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
