"""Generate the ID3 working in ch3-num.tex, AI-notes style, from each problem's own table.

Fills every  % id3tab:<slot> ... % id3tab:end  block in ch3-num.tex. The data is read from the
problem's printed (asked) table, never typed here. Arithmetic is carried at 4 dp the way a
student does it by hand: each weighted term is n/N times the PRINTED entropy, the residual is
the sum of the printed terms, the gain is printed Info minus printed residual, so every line of
the page adds up exactly. The script asserts that this hand arithmetic picks the same winner as
exact arithmetic at every node, and that every printed number is within 5e-4 of the exact one.

    python id3tab.py            # rewrite the slots
    python id3tab.py --check    # exit 1 if the .tex is not what the script would write
"""
import math
import re
import sys
from collections import Counter

TEX = "ch3-num.tex"


def H(counts):
    n = sum(counts)
    return -sum(c / n * math.log2(c / n) for c in counts if c) if n else 0.0


def r4(x):
    return round(x + 0.0, 4)


def f4(x):
    s = "%.4f" % x
    return "0.0000" if s == "-0.0000" else s


# ---------------------------------------------------------------------------
#  Problem data, read from the asked tables
# ---------------------------------------------------------------------------
def section(tex, a, b):
    i = tex.index(a)
    j = tex.index(b, i + 1)
    return tex[i:j]


def cells(line):
    return [x.strip() for x in line.split("&")]


def load(tex):
    P = {}
    s = section(tex, r"\creamq{Problem 1.1}", r"\creamq{Problem 1.2}")
    rows = [tuple(cells(l)) for l in
            re.findall(r"(?m)^((?:Youth|Middle\\_Aged|Senior)\s*&[^\n]*?)\\\\", s)]
    P["11"] = dict(rows=rows, names=["Age", "Income", "Student", r"Credit\_Rating"],
                   classes=["Yes", "No"], cls=["Yes", "No"], recurse=True, n=14)
    s = section(tex, r"\creamq{Problem 1.2}", r"\creamq{Problem 1.3}")
    rows = [tuple(cells(l)) for l in re.findall(r"(?m)^((?:Male|Female)\s*&[^\n]*?)\\\\", s)]
    P["12"] = dict(rows=rows, names=["Gender", "Car ownership", "Travel cost", "Income level"],
                   classes=["Bus", "Car", "Train"], cls=["Bus", "Car", "Train"], recurse=True, n=10)
    s = section(tex, r"\creamq{Problem 1.3}", r"\creamq{Problem 1.4")
    inc = {r"\$0 to \$15K": r"\$0--15K", r"\$15 to \$35K": r"\$15--35K",
           r"over \$35K": r"over \$35K"}
    rows = []
    for l in re.findall(r"(?m)^(\d+\s*&[^\n]*?)\\\\", s):
        c = cells(l)
        rows.append((c[1], c[2], c[3], inc[c[4]], c[5]))
    P["13"] = dict(rows=rows, names=["Credit history", "Debt", "Collateral", "Income"],
                   classes=["high", "moderate", "low"], cls=["high", "mod", "low"],
                   recurse=True, n=14)
    s = section(tex, r"\creamq{Problem 1.4", r"\T{M2.")
    rows = [tuple(cells(l)) for l in re.findall(r"(?m)^((?:Male|Female)\s*&[^\n]*?)\\\\", s)]
    P["14"] = dict(rows=rows, names=["Gender", "Car ownership", "Travel cost", "Income level"],
                   classes=["Bus", "Train", "Car"], cls=["Bus", "Train", "Car"], recurse=False,
                   n=10)
    for k, p in P.items():
        if len(p["rows"]) != p["n"]:
            sys.exit("%s: expected %d rows, read %d" % (k, p["n"], len(p["rows"])))
    return P


# ---------------------------------------------------------------------------
#  ID3 with hand arithmetic
# ---------------------------------------------------------------------------
def counts(rows, classes):
    c = Counter(r[-1] for r in rows)
    return [c[k] for k in classes]


def split(rows, a, ids, classes, info_p):
    """Hand-arithmetic split of rows on attribute a."""
    N = len(rows)
    parts = []
    for v in dict.fromkeys(r[a] for r in rows):
        sel = [i for i, r in enumerate(rows) if r[a] == v]
        sub = [rows[i] for i in sel]
        cc = counts(sub, classes)
        h = r4(H(cc))
        w = r4(len(sub) / N * h)
        parts.append(dict(v=v, ids=[ids[i] for i in sel], rows=sub, c=cc, n=len(sub), h=h, w=w))
    res = r4(sum(p["w"] for p in parts))
    g = r4(info_p - res)
    exact = H(counts(rows, classes)) - sum(
        p["n"] / N * H(p["c"]) for p in parts)
    assert abs(g - exact) < 5e-4, (a, g, exact)
    return dict(a=a, parts=parts, res=res, g=g, exact=exact)


def node(rows, attrs, ids, classes, path=()):
    cc = counts(rows, classes)
    info = r4(H(cc))
    nd = dict(rows=rows, ids=ids, c=cc, info=info, path=path)
    if sum(1 for x in cc if x) == 1:
        nd["leaf"] = rows[0][-1]
        return nd
    sp = [split(rows, a, ids, classes, info) for a in attrs]
    order = sorted(sp, key=lambda s: (-s["g"], attrs.index(s["a"])))
    exact = sorted(sp, key=lambda s: (-round(s["exact"], 9), attrs.index(s["a"])))
    assert order[0]["a"] == exact[0]["a"], ("hand arithmetic picks a different winner", path)
    best = order[0]
    nd.update(sp=sp, order=order, best=best["a"],
              tie=[s["a"] for s in order[1:] if abs(s["exact"] - best["exact"]) < 1e-9])
    nd["kids"] = [(p["v"], node(p["rows"], [a for a in attrs if a != best["a"]], p["ids"],
                                classes, path + ((best["a"], p["v"]),)))
                  for p in best["parts"]]
    return nd


# ---------------------------------------------------------------------------
#  LaTeX
# ---------------------------------------------------------------------------
def frac(a, b):
    return r"\tfrac{%d}{%d}" % (a, b)


def hcell(h):
    return r"\mk{0}" if h == 0 else f4(h)


def info_line(p, nd):
    N = len(nd["rows"])
    terms, vals = [], []
    for k, c in zip(p["classes"], nd["c"]):
        if c:
            terms.append(r"- %s\log_2%s" % (frac(c, N), frac(c, N)))
            vals.append(f4(r4(-c / N * math.log2(c / N))))
    who = r",\ ".join(r"\textbf{%d %s}" % (c, k) for k, c in zip(p["classes"], nd["c"]))
    return "\n".join([
        r"{\color{sub}\footnotesize %d rows: %s.}" % (N, who.replace(r",\ ", ", ")),
        r"\[ Info(D) = %s" % " ".join(terms),
        r"        = %s = \mathbf{%s} \]" % (" + ".join(vals), f4(nd["info"])),
    ])


def root_table(p, nd):
    N = len(nd["rows"])
    k = len(p["classes"])
    spec = r"@{}L{2.4cm}L{2.0cm}" + "c" * (k + 2) + "X@{}"
    head = (r"\hrow \thead{Attribute} & \thead{Value} & "
            + " & ".join(r"\thead{%s}" % c for c in p["cls"])
            + r" & \thead{$|D_j|$} & \thead{$Info(D_j)$} & \thead{$\frac{|D_j|}{%d}Info(D_j)$} \\" % N)
    L = [r"\begin{tabularx}{\textwidth}{%s}" % spec, head]
    for s in nd["sp"]:
        name = p["names"][s["a"]]
        win = s["a"] == nd["best"]
        for i, q in enumerate(s["parts"]):
            lab = (r"\textbf{%s}" % name if win else name) if i == 0 else ""
            w = "0" if q["h"] == 0 else r"$%s(%s)=%s$" % (frac(q["n"], N), f4(q["h"]), f4(q["w"]))
            L.append(r"%s & %s & %s & %d & %s & %s \\"
                     % (lab, q["v"], " & ".join(map(str, q["c"])), q["n"], hcell(q["h"]), w))
        g = r"Gain $=%s-%s=%s$" % (f4(nd["info"]), f4(s["res"]), f4(s["g"]))
        L.append(r"\hrow \multicolumn{%d}{@{}l}{$Info_{\text{%s}}(D)=%s$} & %s \\"
                 % (k + 4, name, f4(s["res"]), r"\mk{%s}" % g if win else g))
    L.append(r"\end{tabularx}")
    return "\n".join(L)


def compare(p, nd):
    name = p["names"]
    L = [r"\begin{tabularx}{\linewidth}{@{}L{3.0cm}X@{}}",
         r"\hrow \thead{Attribute} & \thead{Gain} \\"]
    top = nd["order"][0]
    for s in nd["order"]:
        mates = [t for t in nd["order"] if t is not s and abs(t["exact"] - s["exact"]) < 1e-9]
        tie = r" {\color{sub}\footnotesize tie with %s}" % name[mates[0]["a"]] if mates else ""
        if s is top:
            L.append(r"\mk{%s} & \mk{%s}%s \\" % (name[s["a"]], f4(s["g"]), tie))
        else:
            L.append(r"%s & %s%s \\" % (name[s["a"]], f4(s["g"]), tie))
    L += [r"\end{tabularx}",
          r"\par\penalty0\vspace{3pt}",
          r"\noindent\colorbox{gdL}{\parbox{\dimexpr\linewidth-2\fboxsep}{\textbf{Answer.} The root",
          r"attribute is \textbf{%s}, with the highest information gain, \textbf{%s}.}}"
          % (name[top["a"]], f4(top["g"]))]
    return "\n".join(L)


def where(p, nd):
    return ", ".join(r"%s $=$ %s" % (p["names"][a], v) for a, v in nd["path"])


def branch_block(p, nd):
    """One impure branch: heading, table, residual line."""
    present = [i for i, c in enumerate(nd["c"]) if c]
    who = ", ".join("%d %s" % (nd["c"][i], p["classes"][i]) for i in present)
    L = [r"\textbf{%s} {\color{sub}\footnotesize rows %s \gap %s \gap $Info=%s$}"
         % (where(p, nd), ", ".join(map(str, nd["ids"])), who, f4(nd["info"])),
         r"\par\vspace{2pt}",
         r"{\small\setlength{\tabcolsep}{3pt}%",
         r"\begin{tabularx}{\linewidth}{@{}l@{\hspace{4pt}}X%sr@{}}" % ("c" * (len(present) + 1)),
         r"\hrow \thead{Attribute} & \thead{Value (rows)} & %s & \thead{$Info$} & \thead{Gain} \\"
         % " & ".join(r"\thead{%s}" % p["cls"][i] for i in present)]
    notes = []
    for j, s in enumerate(nd["order"]):
        name = p["names"][s["a"]]
        win = s["a"] == nd["best"]
        for i, q in enumerate(s["parts"]):
            lab = (r"\textbf{%s}" % name if win else name) if i == 0 else ""
            last = i == len(s["parts"]) - 1
            gcell = (r"\mk{%s}" % f4(s["g"]) if win else f4(s["g"])) if last else ""
            L.append(r"%s%s & %s (%s) & %s & %s & %s \\"
                     % (r"\hrow " if (i == 0 and j > 0) else "", lab, q["v"],
                        ",".join(map(str, q["ids"])),
                        " & ".join(str(q["c"][x]) for x in present), hcell(q["h"]), gcell))
        terms = [r"%s(%s)" % (frac(q["n"], len(nd["rows"])), f4(q["h"]))
                 for q in s["parts"] if q["h"] != 0]
        res = "0" if not terms else ("%s=%s" % ("+".join(terms), f4(s["res"]))
                                     if len(terms) > 1 or s["parts"][0]["n"] != len(nd["rows"])
                                     else f4(s["res"]))
        notes.append(r"%s: residual $%s$, gain $%s-%s=%s$."
                     % (name, res, f4(nd["info"]), f4(s["res"]), f4(s["g"])))
    L.append(r"\end{tabularx}}")
    L.append(r"\par\vspace{2pt}")
    tail = r"\mk{Split on %s.}" % p["names"][nd["best"]]
    if nd["tie"]:
        tail = (r"\mk{A tie at %s}: %s and %s split it equally well. Say so and pick one; "
                r"the tree takes \textbf{%s}, the first in column order."
                % (f4(nd["order"][0]["g"]), p["names"][nd["best"]],
                   " and ".join(p["names"][a] for a in nd["tie"]), p["names"][nd["best"]]))
    L.append(r"{\footnotesize %s %s}" % (" ".join(notes), tail))
    return "\n".join(L)


def internals(nd):
    for _, k in nd.get("kids", []):
        if "leaf" not in k:
            yield k
            yield from internals(k)


def recursion(p, nd):
    groups = []
    for _, k in nd["kids"]:
        if "leaf" not in k:
            groups.append([k] + list(internals(k)))
    if len(groups) == 1:
        g = groups[0]
        groups = [g[:(len(g) + 1) // 2], g[(len(g) + 1) // 2:]]
    assert len(groups) == 2, "recursion layout expects two columns"
    col = [("\n" + r"\par\vspace{6pt}" + "\n").join(branch_block(p, n) for n in g) for g in groups]
    return "\\sbs{%%\n%s}{%%\n%s}" % (col[0], col[1])


def leaves(nd):
    if "leaf" in nd:
        yield nd
    for _, k in nd.get("kids", []):
        yield from leaves(k)


def plain(s):
    return s.replace(r"\_", "_").replace(r"\$", "$").replace("--", "-")


def rules(p, nd):
    rs = []
    for lf in leaves(nd):
        cond = ", ".join("%s = %s" % (plain(p["names"][a]), plain(v)) for a, v in lf["path"])
        rs.append(r"\texttt{%s $\rightarrow$ %s}" % (cond.replace("$", r"\$").replace("_", r"\_"),
                                        plain(lf["leaf"]).replace("_", r"\_")))
    unused = [p["names"][a] for a in range(len(p["names"]))
              if all(a not in [x for x, _ in lf["path"]] for lf in leaves(nd))]
    depth = max(len(lf["path"]) for lf in leaves(nd))
    s = (r"\noindent\textbf{The tree}, %d levels of tests and %d leaves, one rule per leaf: "
         % (depth, len(rs)) + "; ".join(rs) + ".")
    if unused:
        s += (r" %s never appears: \mk{ID3 has decided it is irrelevant}, which is the "
              r"feature-selection side of the algorithm." % " and ".join(unused))
    return s


def blocks(P):
    out = {}
    for k, p in P.items():
        nd = node(p["rows"], list(range(len(p["names"]))), list(range(1, len(p["rows"]) + 1)),
                 p["classes"])
        out["p%s_info" % k] = info_line(p, nd)
        out["p%s_root" % k] = root_table(p, nd)
        out["p%s_cmp" % k] = compare(p, nd)
        if p["recurse"]:
            out["p%s_rec" % k] = recursion(p, nd)
            out["p%s_rules" % k] = rules(p, nd)
    return out


def logtable(P):
    """Every entropy the four problems need, as (counts, H)."""
    seen = {}

    def key(cc):
        c = [x for x in cc if x]
        g = 0
        for x in c:
            g = math.gcd(g, x)
        return tuple(sorted((x // g for x in c), reverse=True))
    for k, p in P.items():
        nd = node(p["rows"], list(range(len(p["names"]))), list(range(1, len(p["rows"]) + 1)),
                  p["classes"])
        stack = [nd]
        while stack:
            n = stack.pop()
            for s in n.get("sp", []):
                for q in s["parts"]:
                    c = key(q["c"])
                    if len(c) > 1:
                        seen[c] = q["h"]
            c = key(n["c"])
            if len(c) > 1:
                seen[c] = n["info"]
            stack += [kid for _, kid in n.get("kids", [])]
    return sorted(seen.items(), key=lambda t: (len(t[0]), sum(t[0]), t[0]))


def log_block(P):
    lt = logtable(P)
    two = [(c, h) for c, h in lt if len(c) == 2]
    three = [(c, h) for c, h in lt if len(c) == 3]
    def row(items):
        return ("\\begin{tabularx}{\\textwidth}{@{}l%s@{}}\n" % ("X" * len(items))
                + r"\hrow \thead{Split} & " + " & ".join(r"\thead{%s}" % ":".join(map(str, c))
                                                         for c, _ in items) + r" \\" + "\n"
                + r"$Info$ & " + " & ".join(f4(h) for _, h in items) + r" \\" + "\n"
                + r"\end{tabularx}")
    parts = [row(two), row(three)]
    return ("\n" + r"\par\vspace{2pt}" + "\n").join(parts)


def main():
    tex = open(TEX, encoding="utf-8").read()
    P = load(tex)
    B = blocks(P)
    B["logs"] = log_block(P)
    pat = re.compile(r"(% id3tab:(\w+)\n)(.*?)(% id3tab:end)", re.S)
    found = set()

    def sub(m):
        name = m.group(2)
        if name not in B:
            sys.exit("unknown slot %s" % name)
        found.add(name)
        return m.group(1) + B[name] + "\n" + m.group(4)
    new = pat.sub(sub, tex)
    missing = set(B) - found
    if missing:
        print("slots not in the .tex (skipped):", ", ".join(sorted(missing)))
    if "--check" in sys.argv:
        sys.exit(0 if new == tex else "ch3-num.tex is stale: run id3tab.py")
    if new != tex:
        open(TEX, "w", encoding="utf-8", newline="\n").write(new)
    print("id3tab: %d slots filled" % len(found))


if __name__ == "__main__":
    main()
