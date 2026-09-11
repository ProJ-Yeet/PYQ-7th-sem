# -*- coding: utf-8 -*-
"""Two-way marks reconciliation between a Sorted PYQ Concise and its Detailed source.

A Concise document promises "marks in (); unique values only", so every distinct
marks split printed in the Detailed must appear somewhere in the matching Concise
chapter, and nothing else may. This walks both documents chapter by chapter
(\\section in the Detailed, \\section* in the Concise, matched by position) and
prints what each side has that the other lacks.

  missing  = in the Detailed, absent from the Concise -> a question lost in the squeeze
  spurious = in the Concise, absent from the Detailed -> a marks value invented,
             mis-copied, or filed under the wrong chapter

A clean run is "missing: -  spurious: -" on every chapter. Chapter counts must
match too; if they do not, the positional pairing is meaningless and the run
says so rather than printing nonsense.

Usage:  python tools/concise_cov.py <Concise.tex> <Detailed.tex>
        python tools/concise_cov.py --all          (every subject in the repo)

Regexes are built from chr(92) so no Python escape ever sees a bare
backslash-letter (CLAUDE.md golden rule 9).
"""
import io, os, re, sys

B = chr(92)

SUBJECTS = [
    ("AI", "AI/AI_Sorted_PYQ_Concise_69-82.tex",
           "AI/AI_Sorted_PYQ_Detailed_69-82.tex"),
    ("DSAP", "DSAP/DSAP_Sorted_PYQ_Concise_66-82.tex",
             "DSAP/DSAP_Sorted_PYQ_Detailed_66-82.tex"),
    ("Data Mining", "Data Mining/Data-Mining_Sorted_PYQ_Concise_69-82.tex",
                    "Data Mining/Data-Mining_Sorted_PYQ_Detailed_69-82.tex"),
    ("O&M", "O&M/OM_Sorted_PYQ_Concise_65-82.tex",
            "O&M/OM_Sorted_PYQ_Detailed_65-82.tex"),
    ("RF-Microwave", "RF-Microwave/RF-Microwave_Sorted_PYQ_Concise_69-82.tex",
                     "RF-Microwave/RF-Microwave_Sorted_PYQ_Detailed_69-82.tex"),
    ("Wireless", "Wireless/Wireless_Sorted_PYQ_Concise_70-82.tex",
                 "Wireless/Wireless_Sorted_PYQ_Detailed_70-82.tex"),
]

SEC_D = re.compile(re.escape(B) + r"section\{([^}]*)\}")
SEC_C = re.compile(re.escape(B) + r"section\*\{([^}]*)\}")
# Detailed marks are bracketed, e.g. [4] [2+6] [2.5+2.5]; a line may carry
# several, one per paper that asked it with a different split.
MK_D = re.compile(r"\[([0-9][0-9.+ ]*)\]")
# Concise marks are parenthesised and run together, e.g. (4)(2+6).
MK_C = re.compile(r"\(([0-9][0-9.+]*)\)")


def real_mark(tok):
    """Reject data that merely looks like a marks split.

    Bracketed binary strings and matrix rows in the Data Mining questions
    ([001101], [40201]) match the marks pattern. No part of an 80-mark paper
    is worth three digits, and no mark starts with a zero.
    """
    for part in tok.split("+"):
        if not part or part[0] == "0" and part != "0":
            return False
        if part.isdigit() and len(part) > 2:
            return False
    return True


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def chapters(text, rx):
    """Split on section headings, returning [(title, body), ...]."""
    out, pos, name = [], None, None
    for m in rx.finditer(text):
        if name is not None:
            out.append((name, text[pos:m.start()]))
        name, pos = m.group(1), m.end()
    if name is not None:
        out.append((name, text[pos:]))
    return out


def reconcile(concise_path, detailed_path, label=None):
    c = load(concise_path)
    d = load(detailed_path)
    d = d[d.find("tableofcontents"):]          # skip the Notes block
    ds, cs = chapters(d, SEC_D), chapters(c, SEC_C)
    print("==== %s" % (label or os.path.basename(concise_path)))
    if len(ds) != len(cs):
        print("  CHAPTER COUNT MISMATCH: detailed %d, concise %d "
              "- pair them by hand before trusting anything below"
              % (len(ds), len(cs)))
    bad = 0
    for i, (dn, db) in enumerate(ds):
        cn, cb = cs[i] if i < len(cs) else ("<NO CONCISE CHAPTER>", "")
        dm = set(x.replace(" ", "") for x in MK_D.findall(db))
        cm = set(MK_C.findall(cb))
        dm = set(x for x in dm if real_mark(x))
        cm = set(x for x in cm if real_mark(x))
        missing, spurious = sorted(dm - cm), sorted(cm - dm)
        bad += len(missing) + len(spurious)
        print("  %-38s | missing: %-34s spurious: %s"
              % (cn[:38], ", ".join(missing) or "-", ", ".join(spurious) or "-"))
    print("  TOTAL discrepancies: %d" % bad)
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--all"]:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        total = 0
        for label, cp, dp in SUBJECTS:
            total += reconcile(os.path.join(root, cp),
                               os.path.join(root, dp), label)
        print("\nGRAND TOTAL: %d" % total)
    elif len(args) == 2:
        reconcile(args[0], args[1])
    else:
        print(__doc__)
        sys.exit(2)
