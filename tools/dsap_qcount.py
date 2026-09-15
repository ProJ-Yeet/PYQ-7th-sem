# -*- coding: utf-8 -*-
"""Per-paper question counter for the DSAP documents, aware of the TWO course codes.

    python tools/dsap_qcount.py DSAP/DSAP_Sorted_PYQ_Detailed_66-82.tex

tools/check.py counts a year code as a plain string, which is wrong here: the
archive holds 45 papers but only 44 DISTINCT year codes, because "69 Bh" names
one CT 704 paper and one EX 753 paper. This keys every count on
(course, year, month), the same trap tools/ai_qcount.py was written for.

Typography, as the documents themselves declare it:
    CT 704 (BEI/BCT)  plain
    EX 753 (BEX)      \texttt{}
so "\texttt{69 Bh}" and "69 Bh" are different papers.

A paper counting 0 in the .tex was never audited in at all; one counting fewer
than the archive has lost questions in the sort. A count HIGHER than the
archive is normal and not flagged: one exam question often lands in two
chapters, and a \lb variant line can carry the same year code twice.

Regexes are built from chr(92) so no Python escape ever sees a bare
backslash-letter (CLAUDE.md golden rule 9).
"""
import collections
import io
import os
import re
import sys

B = chr(92)

MONTH = {
    "Baishakh": "Ba", "Baisakh": "Ba", "Jestha": "Jth", "Ashar": "Asa",
    "Ashad": "Asa", "Shrawan": "Shr", "Bhadra": "Bh", "Ashwin": "Ash",
    "Kartik": "Ka", "Mangsir": "Mng", "Poush": "Po", "Magh": "Ma",
    "Chaitra": "Ch",
}

ARCHIVE = "DSAP/ocr/CT-704_EX-753_OCR.md"


def expected(root):
    """(course, 'YY Mon') -> number of top-level numbered questions."""
    text = io.open(os.path.join(root, ARCHIVE), encoding="utf-8").read()
    # the archive is split into a CT704 half and an EX753 half by "# " banners
    course = "CT704"
    out = {}
    order = []
    for chunk in re.split(r"^(#{1,2}) ", text, flags=re.M)[1:]:
        pass
    # simpler: walk the lines, tracking the most recent banner
    cur = "CT704"
    blocks = []
    head = None
    buf = []
    for line in text.splitlines():
        if line.startswith("# "):
            if "EX753" in line or "EX 753" in line:
                cur = "EX753"
            elif "CT704" in line or "CT 704" in line:
                cur = "CT704"
            continue
        if line.startswith("## "):
            if head:
                blocks.append((head[0], head[1], buf))
            head, buf = (cur, line[3:]), []
            continue
        if head:
            buf.append(line)
    if head:
        blocks.append((head[0], head[1], buf))

    for cur, heading, body in blocks:
        m = re.search(r"(20\d\d)\s+([A-Za-z]+)", heading)
        if not m or m.group(2) not in MONTH:
            continue
        key = (cur, "%s %s" % (m.group(1)[2:], MONTH[m.group(2)]))
        n = len(re.findall(r"^\s{0,3}(\d{1,2})\.\s", "\n".join(body), flags=re.M))
        if n == 0:
            continue                       # a cross-check block, not a paper
        if key not in out:
            order.append(key)
        out[key] = max(out.get(key, 0), n)
    return out, order


def in_tex(path):
    s = io.open(path, encoding="utf-8").read()
    cut = s.find("tableofcontents")
    if cut > 0:
        s = s[cut:]
    pat = re.compile(
        r"(?:(" + re.escape(B) + r"texttt)\{)?"
        r"\b(6\d|7\d|8\d)\s+(Ba|Jth|Asa|Shr|Bh|Ash|Ka|Mng|Po|Ma|Ch)\b")
    c = collections.Counter()
    for m in pat.finditer(s):
        course = "EX753" if m.group(1) else "CT704"
        c[(course, "%s %s" % (m.group(2), m.group(3)))] += 1
    return c


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        root, "DSAP", "DSAP_Sorted_PYQ_Detailed_66-82.tex")
    exp, order = expected(root)
    got = in_tex(path)

    missing, short = [], []
    print("%-7s %-7s %5s %6s" % ("course", "paper", "tex", "paper"))
    for key in sorted(exp, key=lambda k: (k[0], -int(k[1].split()[0]), k[1])):
        n, e = got.get(key, 0), exp[key]
        flag = ""
        if n == 0:
            flag = "   <-- NEVER CITED"
            missing.append(key)
        elif n < e:
            flag = "   <-- SHORT by %d" % (e - n)
            short.append(key)
        print("%-7s %-7s %5d %6d%s" % (key[0], key[1], n, e, flag))

    stray = sorted(k for k in got if k not in exp)
    print()
    print("papers in archive: %d   (distinct year codes: %d)"
          % (len(exp), len({k[1] for k in exp})))
    print("never cited      : %s" % (missing if missing else "none"))
    print("short            : %s" % (short if short else "none"))
    print("codes in tex with no paper: %s" % (stray if stray else "none"))
    return 1 if (missing or stray) else 0


if __name__ == "__main__":
    sys.exit(main())
