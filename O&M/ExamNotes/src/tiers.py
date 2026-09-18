# -*- coding: utf-8 -*-
"""List every tiered question heading in the chapter files, most-asked first.

    python tiers.py            # TOP and HOT only
    python tiers.py --all      # every tier

Feeds the Last-Minute Revision tables in revision.tex, so those counts are
read from the chapters (which check.py has already verified) rather than
retyped by hand.
"""
import re
import sys

B = chr(92)
PAT = re.compile(
    re.escape(B) + r"(Q|creamq)\{(.+?)\}\{[^\n]*\n\{" + re.escape(B)
    + r"color\{sub\}" + re.escape(B) + r"footnotesize " + re.escape(B)
    + r"t([SFPLN])(?:\{(\d+)\})?")

rows = []
for ch in range(1, 6):
    s = open("ch%d.tex" % ch, encoding="utf-8").read()
    for m in PAT.finditer(s):
        tier, n = m.group(3), int(m.group(4) or 0)
        if "--all" in sys.argv or tier in "SF":
            rows.append((n, ch, tier, m.group(2)))
for n, ch, tier, title in sorted(rows, key=lambda r: (-r[0], r[1])):
    print("%2d  ch%d  %s  %s" % (n, ch, tier, title[:100]))
