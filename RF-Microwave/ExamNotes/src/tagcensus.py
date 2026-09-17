# -*- coding: utf-8 -*-
"""Year-tag bolding census: ExamNotes sources vs the Detailed PYQ.

The Detailed PYQ is the source of truth: every paper code there is uniformly
bold (Regular) or plain (Back). This reports, for every year code in every
ExamNotes chapter file, whether it sits inside \\textbf{...} and whether that
agrees with the Detailed PYQ.

Context matters, so each hit is classified:
  yr     inside a \\yr{...} tag list          -> must match
  asked  inside an \\begin{asked}{...} header -> must match
  other  anywhere else (prose, headings, \\mk) -> reported, not counted

Run from src\\:   python tagcensus.py [file.tex ...]   (exit 1 on a yr/asked mismatch)
Regexes are built from chr(92); no escape ever sees a bare backslash-letter.
"""
import os
import re
import sys

B = chr(92)
HERE = os.path.dirname(os.path.abspath(__file__))
PYQ = os.path.normpath(os.path.join(HERE, "..", "..", "RF-Microwave_Sorted_PYQ_Detailed_69-82.tex"))
FILES = ["ch1.tex", "ch2.tex", "ch2-num-body.tex", "ch3.tex", "ch3-num-body.tex",
         "ch4.tex", "ch4-num-body.tex", "ch5.tex", "ch6.tex", "ch6-num-body.tex",
         "ch7.tex", "ch7-num-body.tex"]
YR = re.compile(r"(?<!\d)(\d{2}) (Ba|Bh|Ash|Ma|Ch)\b")


def group_end(s, i):
    """Index just past the {...} group whose opening brace is at s[i-1]."""
    d = 1
    while d and i < len(s):
        if s[i] == B:
            i += 2
            continue
        d += (s[i] == "{") - (s[i] == "}")
        i += 1
    return i


def spans(s, macros):
    out = []
    for m in re.finditer(re.escape(B) + "(?:" + "|".join(macros) + r")\{", s):
        out.append((m.end(), group_end(s, m.end())))
    return out


def inside(pos, sp):
    return any(a <= pos < b for a, b in sp)


def truth():
    s = open(PYQ, encoding="utf-8").read()
    s = s[s.find("tableofcontents"):]
    bold = spans(s, ["bo", "textbf"])
    state = {}
    for m in YR.finditer(s):
        k = m.group(0)
        state.setdefault(k, set()).add(inside(m.start(), bold))
    mixed = {k for k, v in state.items() if len(v) > 1}
    if mixed:
        sys.exit("Detailed PYQ itself is mixed for: " + ", ".join(sorted(mixed)))
    return {k: v.pop() for k, v in state.items()}


def census(path, want):
    s = open(path, encoding="utf-8").read()
    bold = spans(s, ["textbf"])
    yr = spans(s, ["yr"])
    asked = []
    for m in re.finditer(re.escape(B) + r"begin\{asked\}(?:\[[^]]*\])?\{", s):
        asked.append((m.end(), group_end(s, m.end())))
    bad, other = [], []
    for m in YR.finditer(s):
        k = m.group(0)
        if k not in want:
            bad.append((m.start(), k, "UNKNOWN CODE", ""))
            continue
        ctx = "yr" if inside(m.start(), yr) else "asked" if inside(m.start(), asked) else "other"
        isb = inside(m.start(), bold)
        if isb != want[k]:
            line = s.count("\n", 0, m.start()) + 1
            rec = (line, k, ctx, "bold" if isb else "plain")
            (bad if ctx != "other" else other).append(rec)
    return bad, other


def main():
    want = truth()
    files = sys.argv[1:] or FILES
    nbad = 0
    for f in files:
        bad, other = census(os.path.join(HERE, f), want)
        nbad += len(bad)
        print("=== %s: %d tag mismatch(es), %d other" % (f, len(bad), len(other)))
        for line, k, ctx, got in bad:
            print("  ! %s:%s  %-6s %-5s is %s, PYQ says %s"
                  % (f, line, k, ctx, got, "bold" if want.get(k) else "plain"))
        for line, k, ctx, got in other:
            print("    %s:%s  %-6s %-5s is %s (prose, not counted)" % (f, line, k, ctx, got))
    print("\n%d tag mismatch(es)" % nbad)
    sys.exit(1 if nbad else 0)


if __name__ == "__main__":
    main()
