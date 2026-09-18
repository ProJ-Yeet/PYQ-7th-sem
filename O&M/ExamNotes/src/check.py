# -*- coding: utf-8 -*-
"""Check every tier chip against its own year list, and against the archive.

Golden rule 8: count questions per paper before calling a chapter done. Here
the unit is the topic band -- a \\tS{n} / \\tF{n} / \\tP{n} chip claims the
topic was asked in n papers, and the \\yr{...} beside it lists them. Those two
numbers must agree, and every paper listed must actually ask a question in
THIS chapter according to the Detailed PYQ.

Run from src\\:   python check.py [ch1] [ch2] ...
"""
import os
import re
import sys

B = chr(92)
HERE = os.path.dirname(os.path.abspath(__file__))
PYQ = os.path.normpath(os.path.join(
    HERE, "..", "..", "OM_Sorted_PYQ_Detailed_65-82.tex"))

YR = re.compile(r"(\d{2})\s+(Ba|Bh|Ash|Asa|Ma|Ch|Jth|Shr|Ka|Mng|Po)")
CHIP = re.compile(re.escape(B) + r"t([SFPL])\{(\d+)\}")

# ExamNotes chapter -> \section title in the Detailed PYQ
SECTION = {
    "ch1": "Introduction",
    "ch2": "Personnel Management",
    "ch3": "Motivation, Leadership and Entrepreneurship",
    "ch4": "Case Studies",
    "ch5": "Management Information System (MIS)",
}
# The Detailed PYQ keeps 25 old short-note prompts in a separate "Extra"
# section. The notes fold each one into the chapter it belongs to, so a chip
# may cite an Extra paper without that being a ghost.
EXTRA = "Extra"


def balanced(src, start):
    """Contents of the {...} group beginning at `start` (the brace index)."""
    i, depth = start + 1, 1
    while i < len(src) and depth:
        depth += (src[i] == "{") - (src[i] == "}")
        i += 1
    return src[start + 1:i - 1], i


def archive_papers():
    t = open(PYQ, encoding="utf-8").read()
    parts = re.split(re.escape(B) + r"section\{(.+?)\}", t)[1:]
    out = {}
    for i in range(0, len(parts), 2):
        name, body = parts[i], parts[i + 1]
        papers = set()
        for line in body.splitlines():
            if (B + "item" in line or B + "lb" in line) and B + "hfill" in line:
                # every "[marks] (years)" group after \hfill, not only the last:
                # "[8] (69 Bh) [5] (70 Bh, 73 Ma)" names three papers
                tail = line.split(B + "hfill", 1)[1]
                for y in YR.finditer(tail):
                    papers.add(y.group(1) + " " + y.group(2))
        out[name] = papers
    return out


def check(stem, arch):
    path = os.path.join(HERE, stem + ".tex")
    if not os.path.exists(path):
        return 0
    src = open(path, encoding="utf-8").read()
    want = arch.get(SECTION[stem], set())
    bad = 0
    cited = set()

    for m in CHIP.finditer(src):
        # the \yr{...} that follows this chip on the same meta line
        j = src.find(B + "yr{", m.end())
        if j < 0 or j - m.end() > 400:
            print("  ! chip %s with no \\yr list nearby" % m.group(0))
            bad += 1
            continue
        body, _ = balanced(src, j + len(B + "yr{") - 1)
        years = [y.group(1) + " " + y.group(2) for y in YR.finditer(body)]
        cited.update(years)
        claimed = int(m.group(2))
        line = src.count("\n", 0, m.start()) + 1
        if claimed != len(years):
            print("  ! %s:%d  chip claims %d papers, list has %d"
                  % (stem + ".tex", line, claimed, len(years)))
            bad += 1
        ghosts = [y for y in years if y not in want | arch.get(EXTRA, set())]
        if ghosts:
            print("  ! %s:%d  cites %s -- no %s question in the archive"
                  % (stem + ".tex", line, ", ".join(sorted(set(ghosts))),
                     SECTION[stem]))
            bad += 1
        dupes = {y for y in years if years.count(y) > 1}
        if dupes:
            print("  ! %s:%d  duplicate year tags: %s"
                  % (stem + ".tex", line, ", ".join(sorted(dupes))))
            bad += 1

    uncited = sorted(want - cited)
    if uncited:
        print("  ! %s never cites %d paper(s) that ask a %s question: %s"
              % (stem + ".tex", len(uncited), SECTION[stem], ", ".join(uncited)))
        bad += 1
    return bad


def main():
    arch = archive_papers()
    stems = sys.argv[1:] or sorted(SECTION)
    total = 0
    for s in stems:
        path = os.path.join(HERE, s + ".tex")
        if not os.path.exists(path):
            continue
        if s not in SECTION:
            # numerical companions carry their tier chips in the theory file
            print("=== %s ===\n  not a chapter file, skipped" % s)
            continue
        print("=== %s ===" % s)
        n = check(s, arch)
        total += n
        if not n:
            print("  clean")
    print("\n%d problem(s)" % total)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
