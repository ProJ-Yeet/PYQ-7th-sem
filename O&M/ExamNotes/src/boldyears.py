# -*- coding: utf-8 -*-
"""Bold every Regular-exam paper inside \yr{...} in the named chapter files.

    python boldyears.py ch2 [ch3 ...]

The Regular set is read from the Detailed PYQ's \bo{...} tags, so it can
never drift from the archive. Idempotent: a \yr body already holding a
\textbf is left alone.
"""
import re
import sys

B = chr(92)
YR = re.compile(r"(\d{2}) (Ba|Bh|Ash|Asa|Ma|Ch|Jth|Shr|Ka|Mng|Po)\b")


def regulars():
    d = open("../../OM_Sorted_PYQ_Detailed_65-82.tex", encoding="utf-8").read()
    reg = set()
    for m in re.finditer(re.escape(B) + r"bo\{([^}]*)\}", d):
        reg |= {a + " " + b for a, b in YR.findall(m.group(1))}
    return reg


def fix(s, reg):
    out, i, key = [], 0, B + "yr{"
    while True:
        j = s.find(key, i)
        if j < 0:
            out.append(s[i:])
            return "".join(out)
        out.append(s[i:j + len(key)])
        k, depth = j + len(key), 1
        st = k
        while depth:
            depth += (s[k] == "{") - (s[k] == "}")
            k += 1
        body = s[st:k - 1]
        if B + "textbf{" not in body:
            body = YR.sub(lambda m: B + "textbf{" + m.group(0) + "}"
                          if m.group(0) in reg else m.group(0), body)
        out.append(body + "}")
        i = k


if __name__ == "__main__":
    reg = regulars()
    for stem in sys.argv[1:]:
        p = stem + ".tex"
        s = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(fix(s, reg))
        print(p, "done")
