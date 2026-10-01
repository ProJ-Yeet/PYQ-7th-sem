# -*- coding: utf-8 -*-
r"""Split each chapter's PYQ marks into numerical and theory.

    python tools/num_split.py DSAP            # per-chapter table
    python tools/num_split.py DSAP --review   # also list the calls a human should check
    python tools/num_split.py DSAP --rows 3   # every question of chapter 3 with its call

The Detailed PYQ documents carry no numerical flag, so the call is made from
the numerical companions, which are the repo's own record of which questions
are calculations: every worked problem opens with its paper code and, in most
subjects, its marks (\m{2+6} or [2+6]).

A Detailed question (chapter c, paper p, marks m) is NUMERICAL when
  1. the chapter-c companion cites paper p with marks m, or
  2. the companion cites paper p with no marks next to it and the question
     carries math, numbers or a data table (see mathy).
Everything else is THEORY. A question the keyword test calls numerical but
the companion never cites is listed under --review: either the companion
skipped it or the keyword test is wrong, and only reading settles which.

Marks and share come from tools/ch_tally.py, so the totals here always agree
with the chapter headers.
"""
import io, os, re, sys, glob, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import ch_tally as T

BS = chr(92)
CODE = re.compile(r"(\d\d)\s+(Ba|Jth|Asa|Shr|Bh|Ash|Ka|Mng|Po|Ma|Ch)\b")
# marks written after a code: \m{2+6}  or  [2+6]  (within a short window)
MK_AFTER = re.compile(re.escape(BS) + r"m\{([0-9+/ ]+)\}|\[([0-9+/ ]+)\]")

VERBS = re.compile(
    r"\b(find|calculate|compute|determine|evaluate|obtain|design (?:a|an|the)|solve|use|perform|"
    r"identify (?:the )?(?:candidate|frequent|large)|derive association|"
    r"realize|realise|draw the (?:direct|cascade|parallel|lattice|ladder|signal)|"
    r"construct|convert|prove that|show that|using (?:the )?(?:smith chart|apriori|"
    r"fp-growth|k-means|id3|naive|bayes|resolution|a\*|minimax|alpha)|"
    r"apply|trace|generate|cluster|classify|express .* in|"
    r"how many|what is the (?:value|probability|gain|output|number))\b", re.I)


# a statement that opens like a theory question
THEORY = re.compile(r"^\s*(?:" + re.escape(BS) + r"(?:item|lb)\s*)?(?:\([a-z]\)\s*)?"
                    r"(?:explain|describe|define|discuss|why|what|when|how|list|write|"
                    r"short note|compare|differentiate|distinguish|state|mention|"
                    r"illustrate|elaborate|give)\b", re.I)


def norm(raw):
    return "+".join(x.strip() for x in raw.replace(" ", "").split("+")) if raw else None


def mathy(text):
    dollars = text.count("$")
    digits = len(re.findall(r"\d", CODE.sub("", re.sub(r"\[[0-9+/ ]+\]", "", text))))
    tab = ("tabular" in text) or ("bmatrix" in text) or ("includegraphics" in text)
    return dollars >= 2 or digits >= 4 or tab


def looks_numerical(text):
    dollars = text.count("$")
    digits = len(re.findall(r"\d", CODE.sub("", re.sub(r"\[[0-9+/ ]+\]", "", text))))
    tab = ("tabular" in text) or ("bmatrix" in text) or ("includegraphics" in text)
    return bool(VERBS.search(text)) and (dollars >= 2 or digits >= 4 or tab)


def companion(subject, i):
    src = os.path.join(REPO, subject, "ExamNotes", "src")
    for pat in ("ch%d-num-body.tex", "ch%d-num.tex"):
        p = os.path.join(src, pat % i)
        if os.path.exists(p):
            return io.open(p, encoding="utf-8").read()
    return None


FULL = re.compile(r"20(\d\d)\s+(Baisakh|Baishakh|Jestha|Jeth|Jyestha|Ashadh|Ashad|Asar|"
                  r"Shrawan|Bhadra|Ashwin|Asoj|Kartik|Mangsir|Poush|Push|Magh|Chaitra)\b")
MONTH = {"Baisakh": "Ba", "Baishakh": "Ba", "Jestha": "Jth", "Jeth": "Jth", "Jyestha": "Jth",
         "Ashadh": "Asa", "Ashad": "Asa", "Asar": "Asa", "Shrawan": "Shr", "Bhadra": "Bh",
         "Ashwin": "Ash", "Asoj": "Ash", "Kartik": "Ka", "Mangsir": "Mng", "Poush": "Po",
         "Push": "Po", "Magh": "Ma", "Chaitra": "Ch"}


def cites(text):
    """-> (set of (paper, marks)), set of papers"""
    text = FULL.sub(lambda m: m.group(1) + " " + MONTH[m.group(2)], text)
    withmk, papers = set(), set()
    for m in CODE.finditer(text):
        tag = m.group(1) + " " + m.group(2)
        papers.add(tag)
        # the marks written after this code, before the next code: covers
        # "72 Ash \m{2+6}" and "2074 Ashwin . Q5 . [8]"
        nxt = CODE.search(text, m.end())
        seg = text[m.end():min(m.end() + 70, nxt.start() if nxt else len(text))]
        mm = MK_AFTER.search(seg)
        if mm:
            withmk.add((tag, norm(mm.group(1) or mm.group(2))))
    return withmk, papers


def split(subject):
    chs = T.chapters(T.detailed(subject))
    out = []
    for i, (title, body) in enumerate(chs, 1):
        rows, _ = T.tally(body)
        comp = companion(subject, i)
        withmk, papers = cites(comp) if comp else (set(), set())
        # A question's data table usually sits on the lines ABOVE its marks
        # line, so judge each question on everything since the previous one.
        blocks, buf = [], []
        for l in body:
            if T.SUB.match(l):
                buf = []
                continue
            buf.append(l)
            if T.MARK.search(l):
                blocks.append((l.strip(), "\n".join(buf)))
                buf = []
        k = 0
        for r in rows:
            while k < len(blocks) and blocks[k][0] != r["text"]:
                k += 1
            r["block"] = blocks[k][1] if k < len(blocks) else r["text"]
        for r in rows:
            raw = r["raw"].split("/")
            kw = looks_numerical(r["block"])
            hit = (r["paper"], norm(r["raw"])) in withmk or \
                  any((r["paper"], norm(x)) in withmk for x in raw)
            if hit:
                call, why = "N", "companion+marks"
            elif r["paper"] in papers and (kw or mathy(r["block"])):
                call, why = "N", "companion+math"
            elif kw and comp is not None:
                call, why = "T", "REVIEW keyword-only"
            elif r["paper"] in papers and comp is not None:
                call, why = "T", "CHECK cited-paper-no-math"
            else:
                call, why = "T", ""
            # A companion match is only sure when the statement itself shows a
            # calculation: a shared paper and marks value can be coincidence
            # ("Why is spectral transformation required? [2]" beside a [2] design).
            shows = mathy(r["text"]) or bool(VERBS.search(r["text"]))
            if call == "N":
                sure = why == "companion+marks" and (shows or not THEORY.search(r["text"]))
            else:
                sure = not mathy(r["block"]) and not VERBS.search(r["text"])
            key = (subject, str(i), r["paper"], r["raw"], keyof(r["text"]))
            if key in CALLS:
                call, why = CALLS[key], "read"
            elif not sure:
                why = "UNREAD " + why
            r.update(call=call, why=why, key=key)
        out.append((i, title, rows, comp is not None))
    return out


# Calls made by reading, for every question the rules above are not sure of.
# One row per question: subject, chapter, paper, marks, statement key, N|T.
CALLS_TSV = os.path.join(REPO, "tools", "num_split_calls.tsv")


def keyof(text):
    return re.sub(r"\s+", " ", text)[:60]


def load_calls():
    calls = {}
    if os.path.exists(CALLS_TSV):
        for l in io.open(CALLS_TSV, encoding="utf-8"):
            p = l.rstrip("\n").split("\t")
            if len(p) == 6 and not l.startswith("#"):
                calls[tuple(p[:5])] = p[5]
    return calls


CALLS = load_calls()


def summary(subject):
    """-> total, [(i, title, marks, num, share%, num% of chapter)]"""
    res = split(subject)
    total = sum(r["marks"] for _, _, rows, _ in res for r in rows)
    out = []
    for i, title, rows, has in res:
        mk = sum(r["marks"] for r in rows)
        n = sum(r["marks"] for r in rows if r["call"] == "N")
        out.append((i, title, mk, n, 100.0 * mk / total, 100.0 * n / mk if mk else 0.0))
    return total, out


def write_tex(subject):
    """Write <Subject>/ExamNotes/src/weightage.tex: the chapter table both
    masters \\input on their title page. Marks and the split come from the PYQ;
    topic, hours and papers are hand facts kept in src/chapters.tsv.
    Generated, never hand-edited."""
    total, rows = summary(subject)
    tn = sum(r[3] for r in rows)
    b = BS
    facts = {}
    tsv = os.path.join(REPO, subject, "ExamNotes", "src", "chapters.tsv")
    for l in io.open(tsv, encoding="utf-8"):
        if l.startswith("#") or not l.strip():
            continue
        ch, topic, hours, papers = (l.rstrip("\n").split("\t") + ["", "", ""])[:4]
        facts[int(ch)] = (topic, hours, papers)
    hrs = [int(f[1]) for f in facts.values() if f[1].isdigit()]
    bf = lambda s: b + "textbf{" + s + "}"

    def full(p):   # "41/41" -> asked in every paper
        x = p.split("/")
        return len(x) == 2 and x[0] == x[1]

    L = ["% GENERATED by tools/num_split.py --tex from src/chapters.tsv and the Detailed PYQ.",
         "% Do not edit; rerun the tool.",
         b + "begin{center}",
         b + "begin{tabularx}{" + b + "textwidth}{@{}L{0.5cm}XL{0.9cm}L{1.1cm}L{1.0cm}L{1.0cm}"
         "L{1.6cm}L{1.0cm}L{1.0cm}@{}}",
         b + "toprule",
         b + "hrow " + b + "thead{Ch} & " + b + "thead{Topic} & " + b + "thead{Hours} & "
         + b + "thead{Papers} & " + b + "thead{Marks} & " + b + "thead{Share} & "
         + b + "thead{Numerical} & " + b + "thead{Theory} & " + b + "thead{Num.\\,\\%} " + b + b]
    for i, title, mk, n, sh, pc in rows:
        topic, hours, papers = facts.get(i, (title, "", ""))
        half = (lambda s: bf(s)) if pc >= 50 else (lambda s: s)
        L.append("%d & %s & %s & %s & %d & %.1f\\%% & %s & %d & %s %s%s" % (
            i, topic, bf(hours) if hrs and hours == str(max(hrs)) else hours,
            bf(papers) if full(papers) else papers, mk, sh,
            half(str(n)), mk - n, half("%.0f\\%%" % pc), b, b))
    L += [b + "midrule",
          "& " + bf("Total") + " & " + bf(str(sum(hrs))) + " & & " + bf(str(total))
          + " & 100\\% & " + bf(str(tn)) + " & " + bf(str(total - tn)) + " & "
          + bf("%.0f\\%%" % (100.0 * tn / total)) + " " + b + b,
          b + "bottomrule",
          b + "end{tabularx}",
          b + "end{center}",
          b + "vspace{-6pt}",
          b + "begin{center}" + b + "begin{minipage}{" + b + "textwidth}" + b + "footnotesize"
          + b + "color{sub}",
          "Share is of every mark the Detailed PYQ records. \\emph{Numerical} = a calculation,"
          " construction or trace of the kind the numerical companion solves; a question's"
          " whole marks go to one side. Bold numerical: at least half the chapter.",
          b + "end{minipage}" + b + "end{center}",
          ""]
    p = os.path.join(REPO, subject, "ExamNotes", "src", "weightage.tex")
    io.open(p, "w", encoding="utf-8", newline="").write("\n".join(L))
    print("wrote " + os.path.relpath(p, REPO))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    subject = args[0]
    if "--tex" in sys.argv:
        write_tex(subject)
        return
    res = split(subject)
    total = sum(r["marks"] for _, _, rows, _ in res for r in rows)
    print("%-3s %-44s %6s %6s %6s %6s %6s" % ("ch", "chapter", "marks", "num", "theory", "num%", "share"))
    tn = 0
    for i, title, rows, has in res:
        mk = sum(r["marks"] for r in rows)
        n = sum(r["marks"] for r in rows if r["call"] == "N")
        tn += n
        print("%-3d %-44s %6d %6d %6d %5.0f%% %5.1f%%%s" % (
            i, title[:44], mk, n, mk - n, 100.0 * n / mk if mk else 0,
            100.0 * mk / total, "" if has else "   (no companion)"))
    print("all %-44s %6d %6d %6d %5.0f%%" % ("", total, tn, total - tn, 100.0 * tn / total))
    unread = [r for _, _, rows, _ in res for r in rows if r["why"].startswith("UNREAD")]
    if unread:
        print("UNREAD: %d questions still on an automatic call; --dump lists them" % len(unread))
    if "--dump" in sys.argv:
        # one line per unread question, ready to be judged and appended to CALLS_TSV
        for r in unread:
            print("\t".join(r["key"]) + "\t" + r["call"] + "\t" + r["text"][:170] + "\t|| "
                  + re.sub(r"\s+", " ", r["block"])[-260:])
    if "--review" in sys.argv:
        print("\nREVIEW: reads like a calculation, companion does not cite it")
        for i, title, rows, has in res:
            for r in rows:
                if r["why"].startswith(("REVIEW", "CHECK")):
                    print("  ch%d %-7s [%s] %s" % (i, r["paper"], r["raw"], r["text"][:110]))
    if "--rows" in sys.argv:
        want = int(args[1])
        for i, title, rows, has in res:
            if i == want:
                for r in rows:
                    print("  %s %-7s [%-5s] %-20s %s" % (r["call"], r["paper"], r["raw"], r["why"], r["text"][:90]))


if __name__ == "__main__":
    main()
