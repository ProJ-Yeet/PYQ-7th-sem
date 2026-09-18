# -*- coding: utf-8 -*-
"""Unfold a side-by-side pair of PYQ topics into two full-width \\creamq blocks.

    python unpair.py ch2 "Outsourcing"

A \\sbs pair whose two columns each open with \\lead{Title \\m{..}} and a
tier meta line is two exam questions. tools/anki_from_notes.py only makes a
card at a line-start \\Q or \\creamq, so a question headed inside a minipage
never gets its own card. This rewrites

    \\sbs{%\\n\\lead{A \\m{x}}\\n{meta A}\\n<body A>}{%\\n\\lead{B \\m{y}}\\n{meta B}\\n<body B>}

as

    \\creamq{A}{\\m{x}}\\n{meta A}\\n<body A>\\n\\n\\creamq{B}{\\m{y}}\\n{meta B}\\n<body B>

The pair is found by the start of its first \\lead title.
"""
import sys

B = chr(92)


def split_title(lead):
    """'Title \\m{4}\\m{5}' -> ('Title', '\\m{4}\\m{5}')."""
    k = lead.find(B + "m{")
    if k < 0:
        return lead.strip(), ""
    return lead[:k].strip(), lead[k:].strip()


def lead_at(s, i):
    """Parse \\lead{...} starting at i; return (inner, index after '}')."""
    assert s.startswith(B + "lead{", i), s[i:i + 40]
    j = i + len(B + "lead{")
    depth, k = 1, j
    while depth:
        depth += (s[k] == "{") - (s[k] == "}")
        k += 1
    return s[j:k - 1], k


def unpair(s, title):
    start = s.index(B + "sbs{%\n" + B + "lead{" + title)
    i = start + len(B + "sbs{%\n")
    a_lead, i = lead_at(s, i)
    sep = s.index("}{%\n" + B + "lead{", i)
    body_a = s[i:sep]
    j = sep + len("}{%\n")
    b_lead, j = lead_at(s, j)
    # end of the \sbs: the matching close of its second argument
    depth, k = 1, j
    while depth:
        depth += (s[k] == "{") - (s[k] == "}")
        k += 1
    body_b = s[j:k - 1]
    ta, ma = split_title(a_lead)
    tb, mb = split_title(b_lead)
    new = (B + "creamq{" + ta + "}{" + ma + "}" + body_a.rstrip() + "\n\n"
           + B + "creamq{" + tb + "}{" + mb + "}" + body_b.rstrip())
    return s[:start] + new + s[k:]


if __name__ == "__main__":
    stem, title = sys.argv[1], sys.argv[2]
    p = stem + ".tex"
    s = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(unpair(s, title))
    print(p, "unpaired:", title)
