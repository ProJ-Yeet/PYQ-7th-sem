#!/usr/bin/env python3
r"""Build an Anki deck from a subject's ExamNotes LaTeX sources.

One card per exam question. Front = the question exactly as the notes head
it, with its marks chips; back = the answer body from the notes, converted
to HTML (lists, tables, side-by-side pairs, figures, MathJax).

  theory chapter   ch<N>.tex       one card per \Q and per \qq heading
  numericals       ch<N>-num.tex   one card per \T{Problem ...} band, or per
                                   numbered \lead{n.m ...} sub-problem, fronted
                                   by the \begin{asked} statement(s) verbatim
  chapter opener   the material before the first \T           one card

Question -> Answer only: the note type has a single card template, so no
reverse cards are ever generated.

    python tools/anki_from_notes.py Wireless
    python tools/anki_from_notes.py Wireless --report      # no .apkg, stats only

Writes <Subject>/Anki/<Subject>_ExamNotes.apkg and a sibling .tsv fallback.
Figures are downscaled into the package; the sources are untouched.
"""

import argparse
import collections
import html as htmlmod
import io
import os
import re
import shutil
import sys
import zlib

BS = chr(92)

# ---------------------------------------------------------------- utilities


def strip_comments(s):
    """Drop TeX comments. A % eats the rest of the line and the line break."""
    out = []
    for line in s.split("\n"):
        if re.match(r"^[ \t]*%", line):
            continue  # whole-line comment: the line disappears entirely
        cut = None
        j = 0
        while j < len(line):
            if line[j] == "%" and (j == 0 or line[j - 1] != BS):
                cut = j
                break
            j += 1
        if cut is None:
            out.append(line)
        else:
            out.append(line[:cut] + "\x01")  # \x01 = join with the next line
    s = "\n".join(out)
    return re.sub(r"\x01\n[ \t]*", "", s)


def grab_group(s, i):
    """s[i] == '{'. Return (contents, index just past the closing brace)."""
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == BS:
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced brace at %d: %r" % (i, s[i:i + 60]))


def grab_opt(s, i):
    """Optional [..] argument at s[i] if present."""
    k = i
    while k < len(s) and s[k] in " \t\n":
        k += 1
    if k < len(s) and s[k] == "[":
        depth = 0
        j = k
        while j < len(s):
            if s[j] == "[":
                depth += 1
            elif s[j] == "]":
                depth -= 1
                if depth == 0:
                    return s[k + 1:j], j + 1
            j += 1
    return None, i


def grab_args(s, i, n):
    """n mandatory brace groups starting at/after i."""
    args = []
    for _ in range(n):
        while i < len(s) and s[i] in " \t\n":
            i += 1
        if i >= len(s) or s[i] != "{":
            args.append("")
            continue
        a, i = grab_group(s, i)
        args.append(a)
    return args, i


def find_env_end(s, i, env):
    r"""Index of the matching \end{env} start, from i (just past \begin{env})."""
    pat = re.compile(re.escape(BS + "begin{" + env + "}") + "|" +
                     re.escape(BS + "end{" + env + "}"))
    depth = 1
    pos = i
    while True:
        m = pat.search(s, pos)
        if not m:
            raise ValueError("unclosed environment %s" % env)
        if m.group(0).startswith(BS + "begin"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return m.start(), m.end()
        pos = m.end()


# ---------------------------------------------------------------- math

MATH = []


def _stash(tex):
    MATH.append(tex)
    return "\x02%d\x02" % (len(MATH) - 1)


def protect_math(s):
    """Replace every math island with a placeholder, MathJax-ready."""
    def disp(m):
        return _stash(BS + "[" + m.group(1) + BS + "]")

    def aligned(m):
        return _stash(BS + "[" + BS + "begin{aligned}" + m.group(1) +
                      BS + "end{aligned}" + BS + "]")

    s = re.sub(re.escape(BS + "begin{align") + r"\*?\}(.*?)" +
               re.escape(BS + "end{align") + r"\*?\}",
               aligned, s, flags=re.S)
    # The lookbehind is not decoration. \\[2pt] is a LINE BREAK carrying an
    # extra-space option, and its second backslash plus the bracket look
    # exactly like the \[ that opens display math. Without the guard the
    # lazy scan runs to the next \] anywhere in the file and swallows
    # everything between as one math island -- which is what put a page of
    # raw TeX on the front of every chapter's opener card.
    s = re.sub(r"(?<!" + re.escape(BS) + r")" + re.escape(BS + "[") +
               r"(.*?)" + re.escape(BS + "]"),
               disp, s, flags=re.S)
    # $...$  (no $$ in these sources)
    s = re.sub(r"(?<!" + re.escape(BS) + r")\$(.+?)(?<!" + re.escape(BS) + r")\$",
               lambda m: _stash(BS + "(" + m.group(1) + BS + ")"), s, flags=re.S)
    return s


def restore_math(s):
    def back(m):
        tex = MATH[int(m.group(1))]
        # MathJax reads the raw TeX; only the HTML-hostile characters move
        tex = tex.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return tex
    return re.sub("\x02(\\d+)\x02", back, s)


# ---------------------------------------------------------------- text pieces

SYMBOLS = {
    "gap": "&nbsp;", "quad": "&emsp;", "qquad": "&emsp;&emsp;",
    "checkmark": "&#10003;", "xmark": "&times;", "textperiodcentered": "&middot;",
    "textendash": "&ndash;", "textemdash": "&mdash;", "dots": "&hellip;",
    "ldots": "&hellip;", "S": "&sect;", "textbackslash": BS,
    "hfill": " ", "enter": "<br>", "lb": "<br>&rarr; ",
    # \newline is the in-table line break. \lb expands to \\, which inside a
    # tabular ends the ROW instead, so every multi-line table cell in DSAP
    # ch3, ch6 and ch7 uses \newline. 169 of them were being dropped.
    "newline": "<br>",
    "rightarrow": " &rarr; ", "Rightarrow": " &rArr; ", "leftarrow": " &larr; ",
    "times": " &times; ", "cdot": " &middot; ", "approx": " &asymp; ",
    "le": " &le; ", "ge": " &ge; ", "ne": " &ne; ", "pm": " &plusmn; ",
    "alpha": "&alpha;", "beta": "&beta;", "gamma": "&gamma;", "delta": "&delta;",
    "lambda": "&lambda;", "mu": "&mu;", "pi": "&pi;", "sigma": "&sigma;",
    "tau": "&tau;", "phi": "&phi;", "theta": "&theta;", "omega": "&omega;",
    "eta": "&eta;", "xi": "&xi;", "Delta": "&Delta;", "Omega": "&Omega;",
    "Gamma": "&Gamma;", "infty": "&infin;", "circ": "&deg;",
}

# commands that take one argument and wrap it
WRAP1 = {
    "textbf": ("<b>", "</b>"), "emph": ("<i>", "</i>"), "textit": ("<i>", "</i>"),
    "texttt": ('<span class="tt">', "</span>"), "underline": ("<u>", "</u>"),
    "mk": ('<span class="mk">', "</span>"), "thead": ('<b class="th">', "</b>"),
    "code": ("<code>", "</code>"), "yr": ('<span class="yr">', "</span>"),
    "mbox": ("", ""), "text": ("", ""), "textsf": ("", ""),
    "normalfont": ("", ""), "phantomsection": ("", ""),
}

# commands whose arguments are dropped whole
DROP_ARGS = {
    "vspace": 1, "hspace": 1, "vspace*": 1, "hspace*": 1, "needspace": 1,
    "Needspace": 1, "setcounter": 2, "rule": 2, "label": 1, "index": 1,
    "addcontentsline": 3, "typeout": 1, "phantom": 1, "input": 1,
    "renewcommand": 2, "newcommand": 2, "hphantom": 1, "raisebox": 1,
}

# declarations that colour or size the rest of their group
DECL = {
    "footnotesize": ('<span class="sm">', "</span>"),
    "scriptsize": ('<span class="sm">', "</span>"),
    "small": ('<span class="sm">', "</span>"),
    "large": ("", ""), "Large": ("", ""), "LARGE": ("", ""), "Huge": ("", ""),
    "normalsize": ("", ""), "bfseries": ("<b>", "</b>"),
    "itshape": ("<i>", "</i>"), "ttfamily": ('<span class="tt">', "</span>"),
    "raggedright": ("", ""), "centering": ('<div class="ctr">', "</div>"),
    "displaystyle": ("", ""),
}

NOARG_DROP = {
    "par", "noindent", "nobreak", "hr0", "toprule", "midrule", "bottomrule",
    "hline", "hrow", "cleardoublepage", "clearpage", "newpage", "pagebreak",
    "arraybackslash", "relax", "protect", "leavevmode", "penalty",
    "interlinepenalty", "linewidth", "textwidth", "textheight", "baselineskip",
    "tabcolsep", "fboxsep", "smallskip", "medskip", "bigskip", "strut",
}

TIER = {"tS": "TOP", "tF": "HOT", "tP": "PIN"}


class Conv(object):
    """LaTeX -> HTML for the ExamNotes macro set."""

    def __init__(self, figprefix="", media=None, unknown=None):
        self.figprefix = figprefix
        self.media = media if media is not None else set()
        self.unknown = unknown if unknown is not None else collections.Counter()

    # -- entry point ------------------------------------------------------
    def html(self, tex):
        out = self.conv(tex)
        out = re.sub(r"\x06", "<br>", out)  # row breaks outside any table
        out = re.sub(r"(\s*<br>\s*){3,}", "<br><br>", out)
        out = re.sub(r"\x03", "<br>", out)  # paragraph breaks left over
        for tag in ("ul", "ol", "table", "div", "hr", "p"):
            out = re.sub(r"<br>\s*(<" + tag + r")", r"\1", out)
            out = re.sub(r"(</" + tag + r">)\s*<br>", r"\1", out)
        out = re.sub(r"^(\s*<br>)+", "", out)
        out = re.sub(r"(<br>\s*)+$", "", out)
        return restore_math(out).strip()

    # -- scanner ----------------------------------------------------------
    def conv(self, s):
        out = []
        closers = []  # declarations opened in this group
        i, n = 0, len(s)
        while i < n:
            c = s[i]
            if c == BS:
                m = re.match(r"[a-zA-Z]+\*?", s[i + 1:])
                if m:
                    name = m.group(0)
                    i += 1 + m.end()
                    # TeX eats spaces after a control word
                    k = i
                    while k < n and s[k] in " \t":
                        k += 1
                    if k > i and not (k < n and s[k] == "\n"):
                        i = k
                    frag, i, opened = self.command(name, s, i)
                    out.append(frag)
                    if opened:
                        closers.append(opened)
                else:
                    sym = s[i + 1] if i + 1 < n else ""
                    i += 2
                    if sym == BS:
                        _, i = grab_opt(s, i)
                        # \x06, not <br>. Inside a tabular \\ ends the ROW,
                        # while \newline breaks a LINE within one cell, and
                        # both used to arrive here as <br> -- so table() split
                        # a row at every in-cell break and shunted the rest of
                        # that row's cells left into a new one. Keeping them
                        # distinct is the whole fix; html() turns any \x06
                        # that never reached a table into a <br>.
                        out.append("\x06")
                    elif sym in "%&_$#{}":
                        out.append(htmlmod.escape(sym))
                    elif sym in " ,;:":
                        out.append(" ")
                    elif sym == "!":
                        pass
                    else:
                        out.append(htmlmod.escape(sym))
            elif c == "{":
                g, i = grab_group(s, i)
                out.append(self.conv(g))
            elif c == "}":
                i += 1
            elif c == "~":
                out.append("&nbsp;")
                i += 1
            elif c == "&":
                out.append("\x04")  # table cell separator, escaped elsewhere
                i += 1
            elif c == "\n":
                m = re.match(r"\n[ \t]*\n\s*", s[i:])
                if m:
                    out.append("\x03")
                    i += m.end()
                else:
                    out.append(" ")
                    i += 1
            else:
                m = re.match(r"[^" + re.escape(BS) + r"{}~&\n]+", s[i:])
                txt = m.group(0)
                i += m.end()
                out.append(self.text(txt))
        for op in reversed(closers):
            out.append(op)
        return "".join(out)

    def text(self, t):
        t = htmlmod.escape(t)
        t = t.replace("---", "&mdash;").replace("--", "&ndash;")
        t = t.replace("``", "&ldquo;").replace("''", "&rdquo;")
        return t

    # -- command dispatch -------------------------------------------------
    def command(self, name, s, i):
        """Return (html, new index, closing tag to defer or None)."""
        if name == "begin":
            (env,), i = grab_args(s, i, 1)
            return self.environment(env, s, i)
        if name == "end":
            _, i = grab_args(s, i, 1)
            return "", i, None

        if name in ("T",):
            (a,), i = grab_args(s, i, 1)
            return '<div class="band">%s</div>' % self.conv(a), i, None
        if name in ("Q", "creamq", "qq"):
            (a, b), i = grab_args(s, i, 2)
            return ('<div class="qh">%s %s</div>' %
                    (self.conv(a), self.conv(b)), i, None)
        if name == "lead":
            (a,), i = grab_args(s, i, 1)
            return '<div class="lead">%s</div>' % self.conv(a), i, None
        if name == "m":
            (a,), i = grab_args(s, i, 1)
            return '<span class="m">%s</span>' % self.conv(a), i, None
        if name in TIER:
            (a,), i = grab_args(s, i, 1)
            return ('<span class="tier t%s">%s&nbsp;%s</span>' %
                    (TIER[name], TIER[name], self.conv(a)), i, None)
        if name == "added":
            return '<span class="chip gd">verified/added</span>', i, None
        if name == "pill":
            (_, _, c), i = grab_args(s, i, 3)
            return '<span class="chip">%s</span>' % self.conv(c), i, None
        if name == "pillo":
            (_, c), i = grab_args(s, i, 2)
            return '<span class="chip">%s</span>' % self.conv(c), i, None
        if name == "hr":
            return "<hr>", i, None
        if name in ("sbs", "sbsr"):
            nargs = 2 if name == "sbs" else 3
            args, i = grab_args(s, i, nargs)
            left, right = args[-2], args[-1]
            return ('<div class="cols"><div class="col">%s</div>'
                    '<div class="col">%s</div></div>'
                    % (self.conv(left), self.conv(right)), i, None)
        if name == "figT":
            (f,), i = grab_args(s, i, 1)
            return self.figure(f), i, None
        if name == "figC":
            (f, _), i = grab_args(s, i, 2)
            return self.figure(f), i, None
        if name == "includegraphics":
            _, i = grab_opt(s, i)
            (f,), i = grab_args(s, i, 1)
            return self.figure(f.split("/")[-1]), i, None
        if name == "color":
            (c,), i = grab_args(s, i, 1)
            cls = "sub" if c == "sub" else ("mk" if c in ("mkc", "acc") else "")
            if cls:
                return '<span class="%s">' % cls, i, "</span>"
            return "", i, None
        if name == "textcolor":
            (c, t), i = grab_args(s, i, 2)
            cls = "sub" if c == "sub" else ("mk" if c in ("mkc", "acc") else "")
            body = self.conv(t)
            return ('<span class="%s">%s</span>' % (cls, body) if cls else body,
                    i, None)
        if name == "colorbox":
            (_, t), i = grab_args(s, i, 2)
            return self.conv(t), i, None
        if name == "multicolumn":
            (_, _, t), i = grab_args(s, i, 3)
            return self.conv(t), i, None
        if name == "rowcolor":
            _, i = grab_opt(s, i)
            _, i = grab_args(s, i, 1)
            return "", i, None
        if name == "item":
            opt, i = grab_opt(s, i)
            return "\x05" + (opt or ""), i, None  # handled by the list builder
        if name == "section" or name == "section*":
            (a,), i = grab_args(s, i, 1)
            return "", i, None
        if name in WRAP1:
            (a,), i = grab_args(s, i, 1)
            o, c = WRAP1[name]
            return o + self.conv(a) + c, i, None
        if name in DROP_ARGS:
            _, i = grab_opt(s, i)
            _, i = grab_args(s, i, DROP_ARGS[name])
            return "", i, None
        if name in DECL:
            o, c = DECL[name]
            return (o, i, c) if o else ("", i, None)
        if name in SYMBOLS:
            if i < len(s) and s[i:i + 2] == "{}":
                i += 2
            return SYMBOLS[name], i, None
        if name in NOARG_DROP:
            m = re.match(r"\s*-?\d+", s[i:])  # \penalty0, \interlinepenalty10000
            if name.endswith("penalty") and m:
                i += m.end()
            return "", i, None

        self.unknown[name] += 1
        return "", i, None

    # -- environments -----------------------------------------------------
    def environment(self, env, s, i):
        base = env.rstrip("*")
        if base in ("itemize", "enumerate"):
            _, i = grab_opt(s, i)
            end, after = find_env_end(s, i, env)
            return self.list_env(base, s[i:end], s, after)
        if base in ("center", "flushleft"):
            end, after = find_env_end(s, i, env)
            return ('<div class="ctr">%s</div>' % self.conv(s[i:end]),
                    after, None)
        if base == "asked":
            opt, i = grab_opt(s, i)
            (tags,), i = grab_args(s, i, 1)
            end, after = find_env_end(s, i, env)
            hdr = opt or "QUESTION AS PRINTED"
            return ('<div class="asked"><div class="askedhdr">'
                    '<span class="ah">%s</span> <span class="yr">%s</span></div>'
                    '%s</div>' % (self.conv(hdr), self.conv(tags),
                                  self.conv(s[i:end])), after, None)
        if base in ("tabularx", "tabular", "tabular*"):
            if base == "tabularx":
                _, i = grab_args(s, i, 1)
            else:
                _, i = grab_opt(s, i)
            _, i = grab_args(s, i, 1)  # column spec
            end, after = find_env_end(s, i, env)
            return self.table(s[i:end]), after, None
        if base in ("bmatrix", "pmatrix", "cases", "gathered", "aligned",
                    "array", "matrix", "vmatrix"):
            end, after = find_env_end(s, i, env)
            tex = (BS + "[" + BS + "begin{" + env + "}" + s[i:end] +
                   BS + "end{" + env + "}" + BS + "]")
            return _stash(tex), after, None
        if base in ("minipage",):
            _, i = grab_opt(s, i)
            _, i = grab_args(s, i, 1)
            end, after = find_env_end(s, i, env)
            return self.conv(s[i:end]), after, None
        if base in ("list",):
            _, i = grab_args(s, i, 2)
            end, after = find_env_end(s, i, env)
            return self.conv(s[i:end]), after, None
        # unknown environment: keep the contents
        self.unknown["env:" + env] += 1
        end, after = find_env_end(s, i, env)
        return self.conv(s[i:end]), after, None

    def list_env(self, kind, body, s, after):
        conv = self.conv(body)
        parts = conv.split("\x05")
        if not parts:
            return "", after, None
        items = []
        for p in parts[1:]:
            p = p.strip()
            p = re.sub(r"^(\x03|\x06|<br>)+", "", p)
            p = re.sub(r"(\x03|\x06|<br>)+$", "", p)
            items.append(p)
        tag = "ul" if kind == "itemize" else "ol"
        inner = "".join("<li>%s</li>" % it for it in items if it)
        return "<%s>%s</%s>" % (tag, inner, tag), after, None

    def table(self, body):
        conv = self.conv(body)
        rows = []
        # rows break on \x06 (the tabular's own \\) ONLY. A <br> here came
        # from \newline and belongs inside the cell it is sitting in.
        for raw in re.split(r"\x06", conv):
            cells = raw.split("\x04")
            cells = [c.strip() for c in cells]
            if not any(c and c not in ("\x03",) for c in cells):
                continue
            cells = [re.sub(r"\x03", " ", c) for c in cells]
            rows.append(cells)
        if not rows:
            return ""
        out = ['<table class="nt">']
        head_done = False
        for r in rows:
            is_head = (not head_done and
                       all(('class="th"' in c or not c) for c in r) and
                       any('class="th"' in c for c in r))
            tag = "th" if is_head else "td"
            if is_head:
                head_done = True
            out.append("<tr>" + "".join("<%s>%s</%s>" % (tag, c, tag)
                                        for c in r) + "</tr>")
        out.append("</table>")
        return "".join(out)

    def figure(self, fname):
        self.media.add(fname)
        return '<div class="fig"><img src="%s%s"></div>' % (self.figprefix, fname)


# ---------------------------------------------------------------- parsing

MONTHS = "Ba|Jth|Asa|Shr|Bh|Ash|Ka|Mng|Po|Ma|Ch"
YEAR_RE = re.compile(r"\b(\d{2})\s+(%s)\b" % MONTHS)
HEAD_RE = re.compile(r"(?m)^[ \t]*" + re.escape(BS) + r"(T|Q|creamq|qq)\{")
NUMSEG_RE = re.compile(r"(?m)^[ \t]*" + re.escape(BS) +
                       r"(T)\{|^[ \t]*" + re.escape(BS) + r"(lead)\{\d+\.\d+")


def meta_split(body):
    """Pull the '{\\color{sub}\\footnotesize ...}' tag line off the front."""
    m = re.match(r"\s*\{\s*" + re.escape(BS) + r"color\{sub\}", body)
    if not m:
        return "", body
    start = body.index("{")
    tag, end = grab_group(body, start)
    return tag, body[end:]


def years_of(tex):
    return ["%s-%s" % (y, mo) for y, mo in YEAR_RE.findall(tex)]


def marks_of(tex):
    return re.findall(re.escape(BS) + r"m\{([^}]*)\}", tex)


def tier_of(tex):
    m = re.search(re.escape(BS) + r"t([SFP])\{(\d+)\}", tex)
    if not m:
        return None, None
    return TIER["t" + m.group(1)], int(m.group(2))


class Card(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


def parse_theory(path, chno, chtitle, conv):
    src = strip_comments(open(path, encoding="utf-8").read())
    src = protect_math(src)
    heads = list(HEAD_RE.finditer(src))
    cards = []

    # chapter opener: everything before the first band or question
    first = heads[0].start() if heads else len(src)
    opener = src[:first]
    opener = re.sub(re.escape(BS) + r"section\*?\{[^}]*\}", "", opener, count=1)
    opener_html = conv.html(opener)
    if len(re.sub("<[^>]+>", "", opener_html).strip()) > 120:
        cards.append(Card(
            kind="opener", chno=chno, chtitle=chtitle, band="",
            question="Chapter %d &mdash; %s: how is it examined?" % (chno, chtitle),
            marks="", meta="", answer=opener_html, years=[], tier=None,
            key="ch%d-opener" % chno))

    def block(idx):
        """(question, marks, meta, body) for the heading at heads[idx].

        A \\Q owns everything up to the next \\Q or topic band, its \\qq
        sub-questions included: the sub-questions are what a 6-mark answer to
        the parent has to say, and they also stand as cards of their own. A
        \\qq owns only up to the next heading of any kind.
        """
        h = heads[idx]
        start = h.end() - 1  # at the '{'
        stops = ("Q", "T") if h.group(1) == "Q" else ("Q", "T", "creamq", "qq")
        stop = len(src)
        for j in range(idx + 1, len(heads)):
            if heads[j].group(1) in stops:
                stop = heads[j].start()
                break
        args, after = grab_args(src, start, 2)
        meta, body = meta_split(src[after:stop])
        body = re.sub(r"\s*" + re.escape(BS) + r"hr\s*$", "", body)
        return args[0], args[1], meta, body

    band = ""
    for idx, h in enumerate(heads):
        kind = h.group(1)
        if kind == "T":
            arg, _ = grab_group(src, h.end() - 1)
            band = conv.html(arg)
            band = re.sub("<[^>]+>", "", band).strip()
            continue
        qtex, mtex, meta, body = block(idx)
        # two question headings stacked on one shared answer: the first has no
        # body of its own and is answered by the block under the second
        if not re.sub(r"\\[a-zA-Z]+|\s+", " ", body).strip() and idx + 1 < len(heads):
            if heads[idx + 1].group(1) in ("Q", "creamq", "qq"):
                body = block(idx + 1)[3]
        tier, tiern = tier_of(meta)
        cards.append(Card(
            kind="theory", chno=chno, chtitle=chtitle, band=band,
            question=conv.html(qtex),
            marks=conv.html(mtex),
            meta=conv.html(meta),
            answer=conv.html(body),
            years=years_of(meta),
            tier=tier,
            key="ch%d-q%d" % (chno, idx)))
    return cards


def parse_num(path, chno, chtitle, conv):
    src = strip_comments(open(path, encoding="utf-8").read())
    src = protect_math(src)
    segs = list(NUMSEG_RE.finditer(src))
    cards = []

    first = segs[0].start() if segs else len(src)
    intro = src[:first]
    # Brace-match the \section*{...}; a lazy \{.*?\} stops at the first
    # closing brace, which here is the one ending {\color{acc}, and leaves
    # the whole title -- rule, tint macros and all -- on the opener card.
    m = re.search(re.escape(BS) + r"section\*?\{", intro)
    if m:
        _, after = grab_group(intro, m.end() - 1)
        intro = intro[:m.start()] + intro[after:].lstrip()
    intro = re.sub(re.escape(BS) + r"vspace\{[^}]*\}\{" + re.escape(BS) +
                   r"color\{acc\}" + re.escape(BS) + r"rule[^\n]*", "", intro)
    intro_html = conv.html(intro)
    if len(re.sub("<[^>]+>", "", intro_html).strip()) > 120:
        cards.append(Card(
            kind="opener", chno=chno, chtitle=chtitle, band="",
            question="Chapter %d numericals &mdash; which formulas does everything "
                     "come from?" % chno,
            marks="", meta="", answer=intro_html, years=[], tier=None,
            key="ch%d-num-opener" % chno))

    band = ""
    bandmeta = ""
    bandasked = ""   # a statement printed under the band, shared by its parts
    bandtex = ""
    for idx, seg in enumerate(segs):
        stop = segs[idx + 1].start() if idx + 1 < len(segs) else len(src)
        start = src.index("{", seg.start())
        arg, after = grab_group(src, start)
        title = re.sub("<[^>]+>", "", conv.html(arg)).strip()
        body = src[after:stop]
        meta, body = meta_split(body)
        if seg.group(1) == "T":
            band = title
            bandmeta = meta
            bandasked = ""
            bandtex = ""
            heading = title
        else:
            heading = "%s &mdash; %s" % (band, title) if band else title
            meta = meta or ""
        allmeta = (bandmeta + " " + meta) if seg.group(1) != "T" else meta

        # the statement(s) as printed go on the front, the rest is the answer
        asked = []
        rest = []
        pos = 0
        pat = re.escape(BS) + r"begin\{asked\}"
        while True:
            m = re.search(pat, body[pos:])
            if not m:
                rest.append(body[pos:])
                break
            rest.append(body[pos:pos + m.start()])
            s0 = pos + m.end()
            end, aft = find_env_end(body, s0, "asked")
            asked.append(body[pos + m.start():aft])
            pos = aft
        answer = conv.html("".join(rest))
        if not re.sub("<[^>]+>", "", answer).strip():
            # a band that only introduces its numbered sub-problems. Any
            # statement printed under it belongs to every one of them.
            if seg.group(1) == "T":
                bandasked = conv.html("".join(asked))
                bandtex = "".join(asked)
            continue
        front_extra = bandasked + conv.html("".join(asked))
        asked_tex = bandtex + "".join(asked)
        tier, _ = tier_of(allmeta)
        cards.append(Card(
            kind="numerical", chno=chno, chtitle=chtitle, band=band,
            question=heading,
            marks="",
            meta=conv.html(allmeta),
            statement=front_extra,
            answer=answer,
            years=years_of(allmeta + " " + asked_tex),
            tier=tier,
            key="ch%d-num%d" % (chno, idx)))
    return cards


# ---------------------------------------------------------------- media


def pack_media(names, figdir, outdir, prefix, maxwidth, log):
    """Downscale the referenced figures into outdir. Returns [paths]."""
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    paths = []
    total = 0
    for n in sorted(names):
        src = os.path.join(figdir, n)
        if not os.path.exists(src):
            log.append("MISSING FIGURE: %s" % n)
            continue
        dst = os.path.join(outdir, prefix + n)
        im = Image.open(src)
        if im.mode in ("P", "LA"):
            im = im.convert("RGBA")
        if im.width > maxwidth:
            h = int(im.height * maxwidth / im.width)
            im = im.resize((maxwidth, h), Image.LANCZOS)
        buf = io.BytesIO()
        flat = im.convert("RGB") if im.mode == "RGBA" else im
        flat.save(buf, "PNG", optimize=True)
        if buf.tell() > 200 * 1024:
            buf = io.BytesIO()
            flat.convert("RGB").save(buf, "JPEG", quality=85, optimize=True)
            dst = os.path.splitext(dst)[0] + ".jpg"
        with open(dst, "wb") as fh:
            fh.write(buf.getvalue())
        total += buf.tell()
        paths.append(dst)
    log.append("media: %d files, %.1f MB after downscale" % (len(paths), total / 1e6))
    return paths


def remap_media(cards, paths, prefix):
    """PNG that became JPEG needs the src rewritten."""
    renamed = {}
    for p in paths:
        base = os.path.basename(p)
        if base.endswith(".jpg"):
            renamed[prefix + os.path.splitext(base[len(prefix):])[0] + ".png"] = base
    if not renamed:
        return
    for c in cards:
        for fld in ("answer", "statement"):
            v = getattr(c, fld, None)
            if not v:
                continue
            for old, new in renamed.items():
                v = v.replace('src="%s"' % old, 'src="%s"' % new)
            setattr(c, fld, v)


# ---------------------------------------------------------------- deck

CSS = """
.card { font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
        font-size: 16px; text-align: left; color: #16202A; background: #fff;
        line-height: 1.45; }
.nightMode .card, .night_mode .card { color: #E6EAEE; background: #1B1F24; }
.crumb { font-size: 12px; color: #6B7785; letter-spacing: .04em;
         text-transform: uppercase; margin-bottom: 6px; }
.qtext { font-size: 20px; font-weight: 700; line-height: 1.3; }
.meta { font-size: 12.5px; color: #6B7785; margin-top: 6px; }
.sub, .yr, .sm { color: #6B7785; font-size: 0.92em; }
.mk { color: #C2410C; font-weight: 700; }
.nightMode .mk { color: #F79B6B; }
.tt { font-family: ui-monospace, Consolas, monospace; font-size: .94em; }
code { font-family: ui-monospace, Consolas, monospace; font-size: .94em;
       background: #F4F7FA; padding: 0 3px; border-radius: 3px; }
.nightMode code { background: #2A3038; }
.m { display: inline-block; background: #FDEBD9; color: #C2410C;
     font-weight: 700; font-size: 12px; border-radius: 4px;
     padding: 1px 5px; margin: 0 2px; }
.tier { display: inline-block; color: #fff; font-weight: 700; font-size: 11px;
        border-radius: 4px; padding: 1px 6px; margin-right: 4px; }
.tTOP { background: #C2410C; } .tHOT { background: #2563A8; }
.tPIN { background: #6D28D9; }
.chip { display: inline-block; border: 1px solid #6B7785; color: #6B7785;
        font-size: 11px; border-radius: 4px; padding: 0 5px; }
.gd { border-color: #15803D; color: #15803D; }
.band { background: #D6E4F5; color: #2563A8; font-weight: 700;
        padding: 3px 7px; border-radius: 4px; margin: 10px 0 6px; }
.nightMode .band { background: #24384F; color: #9EC5F0; }
.qh { font-weight: 700; font-size: 1.05em; margin: 10px 0 4px; }
.lead { font-weight: 700; margin: 9px 0 2px; }
hr { border: none; border-top: 1px solid #DEE3E8; margin: 10px 0; }
.nightMode hr { border-top-color: #39414A; }
ul, ol { margin: 3px 0 3px 0; padding-left: 20px; }
li { margin: 1.5px 0; }
ul { list-style-type: none; }
ul > li::before { content: "\\2013"; color: #2563A8; font-weight: 700;
                  display: inline-block; width: 12px; margin-left: -12px; }
ul ul > li::before { color: #6B7785; }
.cols { display: flex; gap: 18px; flex-wrap: wrap; align-items: flex-start; }
.col { flex: 1 1 300px; min-width: 260px; }
.nt { border-collapse: collapse; margin: 6px 0; font-size: .93em;
      width: 100%; }
.nt td, .nt th { border: 1px solid #DEE3E8; padding: 3px 6px;
                 vertical-align: top; text-align: left; }
.nightMode .nt td, .nightMode .nt th { border-color: #39414A; }
.nt th, .th { color: #2563A8; font-weight: 700; }
.fig { text-align: center; margin: 7px 0; }
.fig img { max-width: 100%; border-radius: 3px; background: #fff; }
.asked { border-left: 3px solid #2563A8; background: #F4F7FA;
         padding: 6px 10px; margin: 8px 0; border-radius: 0 4px 4px 0; }
.nightMode .asked { background: #232A32; }
.askedhdr { font-size: 11px; color: #2563A8; font-weight: 700;
            letter-spacing: .04em; margin-bottom: 3px; }
.ah { text-transform: uppercase; }
.ctr { text-align: center; }
.ans { margin-top: 4px; }
"""

FRONT = """<div class="crumb">{{Chapter}}{{#Band}} &middot; {{Band}}{{/Band}}</div>
<div class="qtext">{{Question}}</div>
{{#Marks}}<div class="meta">{{Marks}}</div>{{/Marks}}
{{#Statement}}<div class="ans">{{Statement}}</div>{{/Statement}}
"""

BACK = """{{FrontSide}}
<hr id=answer>
{{#Meta}}<div class="meta">{{Meta}}</div>{{/Meta}}
<div class="ans">{{Answer}}</div>
"""


def stable_id(text):
    return 1 << 30 | (zlib.crc32(text.encode("utf-8")) & 0x3FFFFFFF)


def build(subject, cards, media_paths, outdir, deckname, log):
    import genanki
    model = genanki.Model(
        stable_id("model:" + subject),
        "IOE Exam Notes (Q -> A)",
        fields=[{"name": "Question"}, {"name": "Marks"}, {"name": "Statement"},
                {"name": "Answer"}, {"name": "Meta"}, {"name": "Chapter"},
                {"name": "Band"}],
        templates=[{"name": "Question -> Answer", "qfmt": FRONT, "afmt": BACK}],
        css=CSS,
    )
    decks = {}
    for c in cards:
        sub = "%s::%02d %s" % (deckname, c.chno, c.chtitle)
        if c.kind == "numerical":
            sub += "::Numericals"
        if sub not in decks:
            decks[sub] = genanki.Deck(stable_id("deck:" + subject + sub), sub)
        tags = ["ch%d" % c.chno, c.kind]
        if c.tier:
            tags.append("tier::" + c.tier)
        for y in sorted(set(c.years)):
            tags.append("yr::" + y)
        note = genanki.Note(
            model=model,
            fields=[c.question, c.marks, getattr(c, "statement", ""),
                    c.answer, c.meta, "Ch %d &middot; %s" % (c.chno, c.chtitle),
                    c.band],
            tags=tags,
            guid=genanki.guid_for(subject, c.key),
        )
        decks[sub].add_note(note)
    pkg = genanki.Package(list(decks.values()))
    pkg.media_files = media_paths
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "%s_ExamNotes.apkg" % subject.replace(" ", "_"))
    pkg.write_to_file(out)
    log.append("decks: %d" % len(decks))
    return out


def write_tsv(cards, outdir, subject):
    out = os.path.join(outdir, "%s_ExamNotes.tsv" % subject.replace(" ", "_"))
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write("#separator:tab\n#html:true\n#notetype column:0\n#tags column:8\n")
        for c in cards:
            row = [c.question, c.marks, getattr(c, "statement", ""), c.answer,
                   c.meta, "Ch %d - %s" % (c.chno, c.chtitle), c.band,
                   c.kind,
                   " ".join(["ch%d" % c.chno, c.kind] +
                            (["tier::" + c.tier] if c.tier else []) +
                            ["yr::" + y for y in sorted(set(c.years))])]
            fh.write("\t".join(x.replace("\t", " ").replace("\n", " ")
                               for x in row) + "\n")
    return out


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--deck", default=None)
    ap.add_argument("--maxwidth", type=int, default=900)
    ap.add_argument("--report", action="store_true",
                    help="parse and print statistics, write nothing")
    ap.add_argument("--dump", default=None, help="write an HTML preview here")
    args = ap.parse_args()

    src = os.path.join(args.root, args.subject, "ExamNotes", "src")
    if not os.path.isdir(src):
        sys.exit("no such notes source: %s" % src)
    figdir = os.path.join(src, "figs")
    prefix = "".join(w[0] for w in re.split(r"[\s_-]+", args.subject)).lower() + "_"

    log = []
    media = set()
    unknown = collections.Counter()
    conv = Conv(figprefix=prefix, media=media, unknown=unknown)

    titles = {}
    for f in sorted(os.listdir(src)):
        m = re.match(r"ch(\d+)\.tex$", f)
        if not m:
            continue
        head = open(os.path.join(src, f), encoding="utf-8").read()
        t = re.search(re.escape(BS) + r"section\{(.+?)\}", head)
        title = t.group(1) if t else "Chapter " + m.group(1)
        title = htmlmod.unescape(re.sub("<[^>]+>", "", conv.html(title)))
        titles[int(m.group(1))] = title.replace("::", "-").strip()

    cards = []
    for ch in sorted(titles):
        cards += parse_theory(os.path.join(src, "ch%d.tex" % ch), ch,
                              titles[ch], conv)
        numf = os.path.join(src, "ch%d-num.tex" % ch)
        if os.path.exists(numf):
            cards += parse_num(numf, ch, titles[ch], conv)

    by_kind = collections.Counter(c.kind for c in cards)
    log.append("cards: %d  (%s)" % (len(cards), ", ".join(
        "%s %d" % (k, v) for k, v in sorted(by_kind.items()))))
    for ch in sorted(titles):
        n = sum(1 for c in cards if c.chno == ch)
        log.append("  ch%d %-46s %3d cards" % (ch, titles[ch], n))
    if unknown:
        log.append("UNHANDLED MACROS: " + ", ".join(
            "%s(%d)" % (k, v) for k, v in unknown.most_common()))

    outdir = os.path.join(args.root, args.subject, "Anki")
    mediadir = os.path.join(outdir, "_media")
    if not args.report:
        if os.path.isdir(mediadir):
            shutil.rmtree(mediadir)
        paths = pack_media(media, figdir, mediadir, prefix, args.maxwidth, log)
        # after this the .png that had to become .jpg are renamed in the cards,
        # so the preview must be written from here on, not before
        remap_media(cards, paths, prefix)
        deck = args.deck or args.subject
        out = build(args.subject, cards, paths, outdir, deck, log)
        tsv = write_tsv(cards, outdir, args.subject)
        log.append("wrote %s (%.1f MB)" % (out, os.path.getsize(out) / 1e6))
        log.append("wrote %s" % tsv)

    if args.dump:
        rel = os.path.relpath(mediadir, os.path.dirname(os.path.abspath(args.dump)))
        rel = rel.replace(os.sep, "/") + "/"
        with open(args.dump, "w", encoding="utf-8") as fh:
            fh.write("<meta charset=utf-8><style>%s"
                     "body{max-width:820px;margin:20px auto;padding:0 16px}"
                     ".cardbox{border:1px solid #DEE3E8;border-radius:6px;"
                     "padding:12px 14px;margin:16px 0}</style>" % CSS)
            fh.write('<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],'
                     'displayMath:[["\\\\[","\\\\]"]]}};</script>'
                     '<script src="https://cdnjs.cloudflare.com/ajax/libs/'
                     'mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>')
            for c in cards:
                fh.write(('<div class="cardbox card"><div class="crumb">Ch %d &middot; '
                          '%s</div><div class="qtext">%s</div><div class="meta">%s %s'
                          '</div>%s<hr>%s</div>\n'
                          % (c.chno, c.chtitle, c.question, c.marks, c.meta,
                             getattr(c, "statement", ""), c.answer)
                          ).replace('src="' + prefix, 'src="' + rel + prefix))
        log.append("preview: %s" % args.dump)

    print("\n".join(log))


if __name__ == "__main__":
    main()
