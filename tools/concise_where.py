# -*- coding: utf-8 -*-
"""For every discrepancy concise_cov.py reports, show WHERE it comes from.

    python tools/concise_where.py <Concise.tex> <Detailed.tex>

concise_cov.py says a marks value is missing or spurious; it cannot say which
question carries it, and that is the part a human has to see before editing.
This prints, per chapter:

  MISSING  <marks>   the Detailed line that carries it, trimmed
  SPURIOUS <marks>   the Concise bullet that carries it, trimmed

so each fix is a lookup rather than a search. It reuses concise_cov's own
splitting so the two tools can never disagree about chapter boundaries.

Regexes are built from chr(92) so no Python escape ever sees a bare
backslash-letter (CLAUDE.md golden rule 9).
"""
import io
import re
import sys

B = chr(92)

# EXACTLY concise_cov.py's own regexes. An earlier version of this file
# used looser ones and over-reported by six: it counted the document's
# documented key "(+)" (Advantage) as a marks value, and it counted an
# en-dash RANGE such as [1--5] as a single value. Neither is a marks
# split, and concise_cov deliberately ignores both.
MARKS = re.compile(r"(?<![A-Za-z])\[([0-9][0-9.+ ]*(?:/[0-9][0-9.+ ]*)*)\]")
CMARKS = re.compile(r"\(([0-9][0-9.+]*)\)")


def load(p):
    return io.open(p, encoding="utf-8").read()


def chapters(text, star):
    pat = re.escape(B) + "section" + (re.escape("*") if star else "") + r"\{"
    idx = [m.start() for m in re.finditer(pat, text)]
    out = []
    for i, a in enumerate(idx):
        b = idx[i + 1] if i + 1 < len(idx) else len(text)
        blk = text[a:b]
        name = re.search(r"\{(.+?)\}", blk).group(1)
        out.append((name, blk))
    return out


def detail_marks(blk):
    """marks value -> list of trimmed source lines carrying it."""
    out = {}
    for line in blk.splitlines():
        for m in MARKS.finditer(line):
            for v in m.group(1).replace(" ", "").split("/"):
                out.setdefault(v, []).append(_trim(line))
            continue
            body = line.strip()
            body = re.sub(re.escape(B) + r"(item|lb)\b", "", body).strip()
            body = re.sub(r"\s+", " ", body)
            out.setdefault(v, []).append(body[:150])
    return out


def concise_marks(blk):
    out = {}
    for line in blk.splitlines():
        for m in CMARKS.finditer(line):
            body = re.sub(r"\s+", " ", line.strip())
            out.setdefault(m.group(1), []).append(body[:150])
    return out


def main():
    cz, dz = load(sys.argv[1]), load(sys.argv[2])
    cch, dch = chapters(cz, True), chapters(dz, False)
    if len(cch) != len(dch):
        print("chapter counts differ: %d vs %d" % (len(cch), len(dch)))
        return 2
    total = 0
    for (cn, cb), (dn, db) in zip(cch, dch):
        dm, cm = detail_marks(db), concise_marks(cb)
        missing = [v for v in dm if v not in cm]
        spurious = [v for v in cm if v not in dm]
        if not missing and not spurious:
            continue
        print("=" * 78)
        print(cn)
        for v in sorted(missing):
            print("  MISSING  (%s)" % v)
            for src in dm[v][:3]:
                print("      D: %s" % src)
        for v in sorted(spurious):
            print("  SPURIOUS (%s)" % v)
            for src in cm[v][:2]:
                print("      C: %s" % src)
        total += len(missing) + len(spurious)
    print("=" * 78)
    print("TOTAL: %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
