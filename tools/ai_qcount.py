# -*- coding: utf-8 -*-
"""Per-paper question counter for the AI documents, aware of the THREE course codes.

The plain checker in tools/check.py counts a year code as a string, which is wrong
for AI: "77 Ch" names a CT653 paper and "\textit{77 Ch}" a different CT78506 one.
This script keys every count on (code, year, month).

  python tools/ai_qcount.py AI/AI_Sorted_PYQ_Detailed_69-82.tex

Expected counts are read from the two OCR archives; the .tex side counts how many
times each paper's year code appears with the right font wrapper.
"""
import collections
import io
import re
import sys

B = chr(92)

MONTH = {
    "Baishakh": "Ba", "Baisakh": "Ba", "Jestha": "Jth", "Ashar": "Asa",
    "Ashad": "Asa", "Shrawan": "Shr", "Bhadra": "Bh", "Ashwin": "Ash",
    "Kartik": "Ka", "Mangsir": "Mng", "Poush": "Po", "Magh": "Ma",
    "Chaitra": "Ch",
}

ARCHIVES = [
    "AI/ocr/CT-653_CT-710_OCR.md",
    "AI/ocr/CT-653_CT-710_CT-78506_NewScan_OCR.md",
]


def code_of(heading):
    if "78506" in heading:
        return "CT78506"
    if "710" in heading:
        return "CT710"
    return "CT653"


def expected():
    """paper -> number of top-level numbered questions, taken from the archives."""
    out = {}
    for path in ARCHIVES:
        try:
            text = io.open(path, encoding="utf-8").read()
        except IOError:
            continue
        blocks = re.split(r"^## ", text, flags=re.M)[1:]
        for blk in blocks:
            head, _, body = blk.partition("\n")
            m = re.search(r"(20\d\d)\s+([A-Za-z]+)", head)
            if not m or m.group(2) not in MONTH:
                continue
            year = m.group(1)[2:]
            key = (code_of(head), "%s %s" % (year, MONTH[m.group(2)]))
            n = len(re.findall(r"^\s{0,3}(\d{1,2})\.\s", body, flags=re.M))
            if n == 0:
                continue                      # cross-reference block, no question list
            out[key] = max(out.get(key, 0), n)
    return out


def in_tex(path):
    s = io.open(path, encoding="utf-8").read()
    s = s[s.find("tableofcontents"):]
    pat = re.compile(
        r"(?:(" + re.escape(B) + r"text(?:tt|it))\{)?"
        r"\b(6\d|7\d|8\d)\s+(Ba|Jth|Asa|Shr|Bh|Ash|Ka|Mng|Po|Ma|Ch)\b")
    c = collections.Counter()
    for m in pat.finditer(s):
        wrapper = m.group(1)
        code = {B + "texttt": "CT710", B + "textit": "CT78506"}.get(wrapper, "CT653")
        c[(code, "%s %s" % (m.group(2), m.group(3)))] += 1
    return c


def main():
    exp = expected()
    got = in_tex(sys.argv[1])
    short = []
    for key in sorted(exp, key=lambda k: (k[0], k[1].split()[0], k[1].split()[1])):
        n, e = got.get(key, 0), exp[key]
        flag = "  <-- SHORT" if n < e else ""
        print("%-8s %-7s tex=%3d paper=%3d%s" % (key[0], key[1], n, e, flag))
        if n < e:
            short.append(key)
    stray = {k: v for k, v in got.items() if k not in exp}
    if stray:
        print("CODES IN TEX WITH NO PAPER:", stray)
    print("papers:", len(exp), " SHORT:", short if short else "none")


if __name__ == "__main__":
    main()
