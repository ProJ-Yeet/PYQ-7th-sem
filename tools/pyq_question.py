# -*- coding: utf-8 -*-
r"""Pull a paper's question VERBATIM out of an OCR archive, by year code.

    python tools/pyq_question.py DSAP "74 Ash"              # whole paper
    python tools/pyq_question.py DSAP "74 Ash" --find kaiser
    python tools/pyq_question.py DSAP --find "circular convolution"
    python tools/pyq_question.py DSAP --find DFT --tex      # LaTeX-escaped

Why a script and not a model reading the archive: the -num chapters have to
print every paper's question exactly as the paper prints it, typos included
(the house rule at the top of ch5-num.tex). That is transcription, it is
checkable, and a model retyping 40 questions will silently normalise a
"Gibb's" or drop a "[2+6]". This reads the archive once and prints the
bytes. See tools/route.py for the lane rule.

The year code is this repo's own: two-digit year plus the month
abbreviation from CLAUDE.md's Conventions block (Ba, Jth, Asa, Shr, Bh,
Ash, Ka, Mng, Po, Ma, Ch). Ash and Asa are different months.

ONE CODE CAN NAME TWO PAPERS. DSAP's "69 Bh" is both a CT 704 paper and an
EX 753 one, so a lookup on it returns both, each tagged with its own
section heading. Never assume a code is unique; tools/dsap_qcount.py keys
on (course, year, month) for the same reason.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONTHS = {"Baishakh": "Ba", "Jestha": "Jth", "Ashad": "Asa", "Shrawan": "Shr",
          "Bhadra": "Bh", "Ashwin": "Ash", "Kartik": "Ka", "Mangsir": "Mng",
          "Poush": "Po", "Magh": "Ma", "Chaitra": "Ch"}


def archives(subject):
    d = os.path.join(REPO, subject, "ocr")
    if not os.path.isdir(d):
        sys.exit("no ocr/ under %s" % subject)
    return [os.path.join(d, f) for f in sorted(os.listdir(d))
            if f.lower().endswith(".md")]


def load(subject):
    """-> [(code, heading, [question, ...]), ...], archive order preserved."""
    out = []
    for path in archives(subject):
        s = io.open(path, encoding="utf-8").read()
        for part in re.split(r"(?m)^## ", s)[1:]:
            head = part.split("\n", 1)[0].strip()
            m = re.search(r"(\d{4})\s+([A-Z][a-z]+)", head)
            if not m:
                continue
            code = "%s %s" % (m.group(1)[2:],
                              MONTHS.get(m.group(2), m.group(2)))
            blocks, cur = [], []
            for line in part.split("\n"):
                if re.match(r"^\s*\d+\.\s", line):
                    if cur:
                        blocks.append(cur)
                    cur = [line]
                elif cur:
                    cur.append(line)
            if cur:
                blocks.append(cur)
            qs = []
            for b in blocks:
                q = re.sub(r"\s+", " ", " ".join(x.strip() for x in b)).strip()
                # a "> NOTE:" belongs to the archive, not to the paper
                q = re.split(r">\s*NOTE", q)[0].strip()
                if q:
                    qs.append(q)
            out.append((code, head, qs))
    return out


def texify(q):
    r"""Escape what LaTeX would choke on. Math is left to the caller: the
    archive writes plain text, and only a human knows which run of it is a
    formula."""
    for a, b in (("\\", "\\textbackslash "), ("&", "\\&"), ("%", "\\%"),
                 ("$", "\\$"), ("#", "\\#"), ("_", "\\_"), ("{", "\\{"),
                 ("}", "\\}"), ("~", "\\textasciitilde "),
                 ("^", "\\textasciicircum ")):
        q = q.replace(a, b)
    return q


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        sys.exit(__doc__)
    subject = args.pop(0)
    find, code, tex = None, None, False
    while args:
        a = args.pop(0)
        if a == "--find":
            find = args.pop(0).lower()
        elif a == "--tex":
            tex = True
        else:
            code = a
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    papers = load(subject)
    if code:
        papers = [p for p in papers if p[0] == code]
        if not papers:
            sys.exit("no paper with code %r in %s" % (code, subject))
        if len(papers) > 1:
            print("NOTE: %r names %d papers; both follow.\n"
                  % (code, len(papers)))
    hits = 0
    for c, head, qs in papers:
        sel = [q for q in qs if find in q.lower()] if find else qs
        if not sel:
            continue
        hits += 1
        print("=== %s  |  %s" % (c, head))
        for q in sel:
            print("    " + (texify(q) if tex else q))
        print("")
    if not hits:
        sys.exit("nothing matched")


if __name__ == "__main__":
    main()
