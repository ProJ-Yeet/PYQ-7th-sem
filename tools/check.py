# -*- coding: utf-8 -*-
"""Structural + truncation checker for a Sorted PYQ .tex, plus per-paper question counts.

Usage: python check.py <tex> ["<year code>:<count>" ...]
Regexes are built from chr(92) so no Python escape ever sees a bare backslash-letter.
"""
import io, re, sys, collections

B = chr(92)


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def structure(s):
    problems = []
    nb, ne = s.count(B + "begin{"), s.count(B + "end{")
    if nb != ne:
        problems.append("begin/end mismatch: %d vs %d" % (nb, ne))
    if s.count("{") != s.count("}"):
        problems.append("brace delta: %d" % (s.count("{") - s.count("}")))
    if s.count("$") % 2:
        problems.append("odd number of $")
    ell = re.findall(re.escape(B) + r"(?:dots|ldots|cdots)|[.]{3}", s)
    if ell:
        problems.append("TRUNCATION: %d ellipsis marks" % len(ell))
    for m in re.finditer(re.escape(B) + r"includegraphics(?:\[[^]]*\])?\{([^}]*)\}", s):
        problems.append("figure ref: " + m.group(1))
    return problems


def counts(s, expected):
    body = s[s.find("tableofcontents"):]
    codes = re.findall(r"\b(6\d|7\d|8\d)\s+(Ba|Jth|Asa|Shr|Bh|Ash|Ka|Mng|Po|Ma|Ch)\b", body)
    c = collections.Counter("%s %s" % (a, b) for a, b in codes)
    short = []
    for k in sorted(expected, key=lambda x: (x.split()[0], x.split()[1])):
        got, exp = c.get(k, 0), expected[k]
        flag = "  <-- SHORT" if got < exp else ""
        print("%-8s tex=%3d paper>=%3d%s" % (k, got, exp, flag))
        if got < exp:
            short.append(k)
    unexpected = {k: v for k, v in c.items() if k not in expected}
    if unexpected:
        print("UNEXPECTED CODES:", unexpected)
    return short


if __name__ == "__main__":
    path = sys.argv[1]
    exp = {}
    for a in sys.argv[2:]:
        y, n = a.rsplit(":", 1)
        exp[y] = int(n)
    s = load(path)
    print("=== structure ===")
    p = structure(s)
    print("\n".join(p) if p else "all pass")
    if exp:
        print("=== per-paper counts ===")
        short = counts(s, exp)
        print("SHORT papers:", short if short else "none")
