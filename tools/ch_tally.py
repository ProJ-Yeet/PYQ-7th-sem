# -*- coding: utf-8 -*-
r"""Count what a chapter of a Sorted PYQ document actually asks.

    python tools/ch_tally.py DSAP 4
    python tools/ch_tally.py DSAP            # every chapter, one summary line each
    python tools/ch_tally.py DSAP 4 --rows   # one line per question

Reads the Detailed document, finds the named \section, and walks each marks
bracket to the year codes that follow it. Prints question counts, total marks,
distinct papers, and the per-subsection split, which is what the tier chips and
the chapter header need.

Why a script and not a model: this is arithmetic over a known markup, the
answer is checkable, and a wrong tier chip is a defect that reading cannot
catch. The rule this repo runs on is in tools/route.py.

The counting rule, which is the only subtle part. A single source line can
carry several questions:

    \lb $y[n]...$ \hfill [2+4] (\bo{78 Bh}); \hfill [3+7] (\bo{81 Bh})

so at every marks bracket we take the text up to the NEXT marks bracket and
read the year codes out of that window. A window naming two papers is two
questions sharing one statement. Marks of the form 8/7 mean the same question
was worth different marks in the two papers it cites, in order.
"""
import io, os, re, sys, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A marks bracket is never glued to an identifier. That is what separates
# "\hfill [2+4]" and "; [8]" from a sequence index like x[0]=1 or h[2].
MARK = re.compile(r"(?<![A-Za-z0-9}\]])\[([0-9]+(?:\s*[+/]\s*[0-9]+)*)\]")
CODE = re.compile(r"(\d\d)\s+(Ba|Jth|Asa|Shr|Bh|Ash|Ka|Mng|Po|Ma|Ch)\b")
SEC = re.compile(r"^\\section\{(.+)\}\s*$")
SUB = re.compile(r"^\s*\\subsection\{(.+)\}\s*$")


def detailed(subject):
    import glob
    pat = os.path.join(REPO, subject, "*_Sorted_PYQ_Detailed_*.tex")
    hit = glob.glob(pat)
    if not hit:
        raise SystemExit("no Detailed document under " + os.path.join(REPO, subject))
    return hit[0]


def value(m):
    """'3+7' -> [10].  '8/7' -> [8, 7], one per paper cited, in order."""
    m = m.replace(" ", "")
    # '/' separates the alternatives, one per paper cited; each alternative may
    # itself be a sum, as in [3+4/2+4].
    return [sum(int(x) for x in part.split("+")) for part in m.split("/")]


def chapters(path):
    """-> list of (title, [lines]), in document order."""
    lines = io.open(path, encoding="utf-8").read().split("\n")
    out, cur, title = [], None, None
    for l in lines:
        m = SEC.match(l)
        if m:
            if cur is not None:
                out.append((title, cur))
            title, cur = m.group(1), []
            continue
        if cur is not None:
            cur.append(l)
    if cur is not None:
        out.append((title, cur))
    return out


def tally(body):
    rows = []
    noted = []
    sub = None
    for l in body:
        m = SUB.match(l)
        if m:
            sub = m.group(1)
            continue
        marks = list(MARK.finditer(l))
        if not marks:
            if CODE.search(l):
                noted.append(("no marks bracket", l.strip()[:96]))
            continue
        for i, mm in enumerate(marks):
            lo = mm.end()
            hi = marks[i + 1].start() if i + 1 < len(marks) else len(l)
            window = l[lo:hi]
            codes = CODE.findall(window)
            if not codes:
                noted.append(("marks [%s] with no year code" % mm.group(1),
                              window.strip()[:80]))
                continue
            vals = value(mm.group(1))
            bold = r"\bo{" in window
            for j, (yr, mo) in enumerate(codes):
                tag = yr + " " + mo
                tt = (r"\texttt{" + yr) in window
                rows.append({
                    "sub": sub, "paper": tag,
                    "marks": vals[j] if j < len(vals) else vals[-1],
                    "raw": mm.group(1),
                    "flag": ("R" if bold else "B") + ("+tt" if tt else ""),
                    "text": l.strip(),
                })
    return rows, noted


def report(title, rows, noted, show_rows=False):
    per = collections.Counter()
    marks = collections.Counter()
    papers = collections.Counter()
    for r in rows:
        per[r["sub"]] += 1
        marks[r["sub"]] += r["marks"]
        papers[r["paper"]] += 1
    print("")
    print("=" * 78)
    print(title)
    print("=" * 78)
    print("questions %d   marks %d   distinct papers %d"
          % (len(rows), sum(r["marks"] for r in rows), len(papers)))
    for s in per:
        print("   %-58s %3d q  %4d mk" % ((s or "(no subsection)")[:58],
                                          per[s], marks[s]))
    top = [(n, p) for p, n in papers.items() if n >= 3]
    if top:
        print("   papers cited 3+ times: "
              + ", ".join("%s x%d" % (p, n) for n, p in sorted(top, reverse=True)))
    if noted:
        print("   lines needing a human eye:")
        for why, txt in noted:
            print("      %-28s %s" % (why, txt))
    if show_rows:
        print("")
        print("   %-9s %-4s %-7s %s" % ("paper", "mk", "flag", "statement"))
        for r in rows:
            print("   %-9s %-4d %-7s %s" % (r["paper"], r["marks"], r["flag"],
                                            r["text"][:78]))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show = "--rows" in sys.argv
    if not args:
        raise SystemExit(__doc__.strip().split("\n\n")[1])
    subject = args[0]
    path = detailed(subject)
    chs = chapters(path)
    want = int(args[1]) if len(args) > 1 else None
    print("source: " + os.path.relpath(path, REPO))

    # Always tally every chapter, even when only one is being printed: a chapter
    # header claims a RANK ("second heaviest"), and a rank cannot be known from
    # one chapter's numbers. Getting that wrong twice is what put this here.
    allrows = [(i, title, tally(body)[0], tally(body)[1])
               for i, (title, body) in enumerate(chs, 1)]
    weights = sorted(((sum(r["marks"] for r in rows), i)
                      for i, _, rows, _ in allrows), reverse=True)
    rank = {i: n for n, (_, i) in enumerate(weights, 1)}
    npapers = 45

    for i, title, rows, noted in allrows:
        if want and i != want:
            continue
        mk = sum(r["marks"] for r in rows)
        report("Chapter %d: %s" % (i, title), rows, noted, show_rows=show)
        print("   about %.1f marks in an 80 mark paper   RANK %d of %d by weight"
              % (mk / float(npapers), rank[i], len(allrows)))

    if want is None:
        print("")
        print("%-4s %-46s %6s %6s %5s" % ("rank", "chapter", "marks", "/80", "q"))
        for n, (mk, i) in enumerate(weights, 1):
            title = allrows[i - 1][1]
            q = len(allrows[i - 1][2])
            print("%-4d %-46s %6d %6.1f %5d"
                  % (n, title[:46], mk, mk / float(npapers), q))
        print("")
        print("all chapters, total marks: %d  (%.1f per paper against a printed 80)"
              % (sum(w for w, _ in weights),
                 sum(w for w, _ in weights) / float(npapers)))


if __name__ == "__main__":
    main()
