# Handoff: how we build sorted PYQ documents and exam notes

**Read this whole file before writing anything.** It is the complete method behind a
working set of documents for IOE (Tribhuvan University) 7th-semester subjects: six
subjects of chapter-sorted past questions, and two subjects of full exam notes
(13 PDFs / 202 pages for one of them). Everything here has been through real build
cycles; the gotchas sections exist because each one cost a wasted rebuild.

This file is written **for the AI**, not for the student. If you are the AI: treat it as
the project spec. The conventions are not suggestions, they are what the output has to
look like. Where a rule looks arbitrary, it is usually there because the obvious
alternative was tried and rejected — those cases are called out so you do not re-litigate
them.

---

## 0. What gets produced

Two independent deliverables. Do not mix them up.

| # | Deliverable | Files per subject | Purpose |
|---|---|---|---|
| **A** | **Sorted PYQ** | `<Subject>_Sorted_PYQ_Detailed.tex/.pdf` + `<Subject>_Sorted_PYQ_Concise.tex/.pdf` | Every past question re-ordered by syllabus topic instead of by year. Detailed = full text of every question. Concise = the same thing crushed to keywords, one page. |
| **B** | **Exam Notes** | `Ch<N> - <Name>.pdf` per chapter, plus `Ch<N> - <Name> - Numerical Problems & Solutions.pdf` where the chapter has numericals | A syllabus-order textbook written to be answered from directly: every topic tagged with the years it was asked and how often, every numerical reproduced verbatim then solved in full. |

**A comes first.** B depends on A: the notes' topic ordering and tier badges are counted
off the question set that A organises.

---

## 1. Environment

What the setup looked like here. Yours may differ; what matters is that the equivalents exist.

- **No LaTeX distribution installed.** PDFs are built with **[Tectonic](https://tectonic-typesetting.github.io/)**,
  a single-binary engine (~20 MB, no admin rights, downloads packages on first use). It runs
  multiple passes internally, so **one run resolves the table of contents** — the old
  "run pdflatex twice" rule does not apply. Compile from the folder that owns `images/`
  so relative paths resolve.
- **No tesseract, no OCR binary.** The source question papers are pure image scans
  (`page.get_text()` returns empty on every page). Transcription is done by rendering pages
  with **PyMuPDF** (`fitz`) and reading the images directly. See §3.
- **PyMuPDF, Pillow, python-pptx** available. `pywin32` + Microsoft Office let you read legacy
  `.ppt` / `.doc` lecture material through COM automation (`win32com.client`,
  `PowerPoint.Application`, `Slide.Export`).
- **Bash heredocs on Windows mangle backslashes** (`\\` collapses to `\`). Any Python helper
  script that contains LaTeX must be written with a file-write tool, never piped through a
  heredoc. Always read the file back and confirm the edit landed.
- Folder names with spaces (`Data Mining`) must be quoted in every shell command.

Directory layout, per subject:

```
<Subject>/
  <source-scans>.pdf                    <- INPUT: scanned question papers
  <Subject>_Sorted_PYQ_Detailed.tex/.pdf
  <Subject>_Sorted_PYQ_Concise.tex/.pdf
  images/                               <- figures cropped out of the scans
  ocr/<source-basename>_OCR.md          <- verbatim transcription of every paper
  Notes/                                <- INPUT for deliverable B: lecture slides, books
  ExamNotes/                            <- OUTPUT B: the chapter PDFs
    src/                                <- .tex sources, preamble, build/verify/audit scripts
      figs/                             <- figures cropped out of the lecture sources
Syllabus/<subject>.tex                  <- INPUT: the printed syllabus, typed up. Do not edit.
```

Once a subject is extended with newer papers, **append the year span to the filename**:
`Wireless_Sorted_PYQ_Detailed_70-82.pdf`. It makes it obvious at a glance which compilation
is current.

---

# PART A — Sorted PYQ documents

## 2. The one rule that decides everything

**Sort by syllabus order, never by year.** The syllabus `.tex` is the skeleton; every question
is filed under the syllabus subsection it belongs to. A subsection with no questions keeps its
heading and stays empty — that empty heading is information (nobody has been examined on it yet).

Grouping rules:

1. Identical or near-identical questions collapse into **one parent item**; variant phrasings
   hang under it as sub-variants.
2. Numerical problems: one parent item, and each distinct parameter set becomes a sub-variant.
3. "Write short notes on X" topics get filed under the syllabus subsection for X, not in a
   short-notes bin at the end.
4. Both programmes/course codes go in **one** document, distinguished typographically (§4).
5. Material examined under one code but genuinely outside the other's syllabus goes in a
   trailing chapter called "Extra".

## 3. OCR archives — build one, then never re-read the scans

The scans have no text layer, so reading a page means rendering it to PNG and reading the image.
That is expensive, so it is done **once** and the transcription is saved.

**Method:** render at `fitz.Matrix(2.4, 2.4)` grayscale (~1430x2020 px per page), read the images,
write the `.md`. For a faint or heavily-inked band, re-crop just that band at `Matrix(5.0, 5.0)`
to confirm wording. That rescue crop was needed roughly once per 20 pages.

**Format:** `<Subject>/ocr/<source-pdf-basename>_OCR.md`, one section per paper:

```
## p14 — 2080 Bhadra, Regular, BEI, CT710
```

followed by every question verbatim with `[marks]` exactly as printed. Include a page-order
table at the top, a figure index, and per-paper defect notes.

**Rules:**

1. Before rendering any page of a source PDF, check `ocr/` first.
2. Re-render only for a **figure crop** (the archive describes figures, it cannot contain them)
   or when the archive itself flags a line as uncertain.
3. If you OCR a subject with no archive yet, **write the archive out** before moving on.
4. **Transcribe verbatim, typos included** (`Caesor`, `bakpropagation`, `900 MHza`, `EIRP oh 1 kW`).
   Do not silently correct them — the `.tex` quotes these statements, and later the exam notes
   quote them again. Where the paper itself is defective (a missing data table, a reversed
   inequality, seven entries listed for an eight-point DFT), record it as printed and say so.

**The page index lies.** Confirm every paper's identity by reading its own header. Real examples
from this project, all of which the page order alone would have got wrong:

- A page sitting exactly where the 2073 Bhadra Wireless paper belonged was actually a Digital
  Signal Processing paper.
- One paper printed `Programme: BEI` on what was unambiguously the BEX paper.
- Two pages were duplicate scans of the same paper; two others were blank.
- A newer scan was clipped at the foot, and only the older scan had the full question.

When a subject has two scans, **diff them page by page** — each usually holds a paper the other
is missing, so neither can be deleted. Compare rendered-page md5s to detect a scan that is
byte-identical to a subset of another.

## 4. Typographic conventions (the key rules)

Two **independent** axes, so all four combinations occur.

**Axis 1 — exam type**, read straight off the header ("Regular" vs "Back" / "New Back (2066 & Later Batch)"):

- Regular exam -> **bold**
- Back exam -> plain

**Axis 2 — programme / course code**, shown with `\texttt{}`:

- one programme is plain, the other is monospace
- which one gets the monospace is a per-subject decision. Normally the newer code is monospace.
  In one subject it was deliberately inverted so that every year code already in the document
  stayed valid — that is legitimate, but **each document must state its own choice in its Notes block.**
- a subject with a single common paper for all programmes uses **no** monospace axis at all.

```
\bo{72 Ash}            old programme, Regular
73 Ma                  old programme, Back
\bo{\texttt{79 Bh}}    new programme, Regular
\texttt{81 Ba}         new programme, Back
```

A header cell printing "Regular / Back" in one box counts as **Regular** (bold). Set that
precedent once and apply it everywhere.

**Month abbreviations** (Bikram Sambat):

```
Ba  = Baishakh   Jth = Jestha    Asa = Ashar
Shr = Shrawan    Bh  = Bhadra    Ash = Ashwin
Ka  = Kartik     Mng = Mangsir   Po  = Poush
Ma  = Magh       Ch  = Chaitra
```

**Keyword replacements** (mandatory, both documents):

```
(I)   -> Importance / Need / Significance
(+)   -> Advantage
(-)   -> Disadvantage
+Fig  -> Figure / Diagram
+Eg   -> Example / Numerical example
Vs    -> Compare / Differentiate / Contrast
```

Never use "define" as a keyword — just put the marks next to the topic.

**Marks:**

- Detailed: square brackets, original split preserved — `\hfill [4+4] (\bo{72 Ash}, 70 Ma)`
- Concise: round brackets, **unique values only** — `\hfill (4)(8)`, never `(4)(4)(4)`

## 5. The no-truncation rule (Detailed documents) — IMPORTANT

In the Detailed document a question statement is reproduced **in full**. Never abbreviate a
numerical or word problem with `$\dots$`, never summarise it as "(cigar-smoking survey)".
Every percentage, prior, name and axiom must be present, because the student has to be able to
solve the question straight from the document.

Data tables get **typeset in LaTeX** (`tabular`, `bmatrix`) rather than cropped as images —
transaction tables, confusion matrices, covariance matrices, power-delay profiles, Erlang tables.
Crop an image only for a true line drawing.

Only the **Concise** document may compress to keywords, and there `\dots` is allowed as a
deliberate shorthand pointer (`T100-T500, {M,O,N,K,E,Y}...`).

The check before shipping: grep the Detailed `.tex` for `$\dots$`. It must return nothing.

## 6. Detailed document — preamble and structure

```latex
\documentclass[12pt]{article}
\usepackage{hyperref}
\usepackage{amsmath, amssymb, amsfonts}
\usepackage[margin=1.2cm]{geometry}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{enumitem}
\parindent 0pt
\newcommand{\lb}{\\$\left|\rightarrow\right.$}
\newcommand{\enter}{\\\textcolor{white}{1}}
```

Do **not** add `\usepackage{inconsolata}` — it is not in the Tectonic bundle and is a fatal error.

The `\bo{}` macro bolds a comma-separated list of year codes in one call
(`\bo{72 Ash, 74 Bh}` -> both bold). It needs the full expl3 form; do not "simplify" it:

```latex
\ExplSyntaxOn
\NewDocumentCommand{\bo}{m}
 {
   \bold_commas:n { #1 }
 }
\cs_new:Npn \bold_commas:n #1
 {
   \seq_set_split:Nnn \l_tmpa_seq { , } { #1 }
   \seq_map_indexed_function:NN \l_tmpa_seq \__bold_commas_aux:nn
 }
\cs_new:Npn \__bold_commas_aux:nn #1 #2
 {
   \textbf{#2}
   \int_compare:nNnTF { #1 } < { \seq_count:N \l_tmpa_seq }
     { , }
     { }
 }
\ExplSyntaxOff
```

Body:

```latex
\begin{document}
\maketitle
\vspace{6cm}          % tune per subject so the Notes block sits low on the title page
[Notes block: sources + year range, bold/plain rule, programme rule, months, keywords]
\pagebreak
\tableofcontents
\pagebreak

\pagebreak
%=======================================================================
\section{Chapter Name}
\begin{center}(X Hours)\end{center}
  \subsection{Syllabus subsection}
    \begin{enumerate}[topsep=0pt, noitemsep]
      \item Question text \hfill [marks] (year codes)
        \lb variant phrasing \hfill [marks] (year codes)
    \end{enumerate}
\end{document}
```

`\lb` is the indented arrow marking a sub-variant of the same question; `\enter` gives a very
long question a blank line before its `\hfill`. Each chapter starts on a new page.

## 7. Concise document — preamble and structure

```latex
\documentclass[10pt]{article}
\usepackage{hyperref}
\usepackage{amsmath, amssymb, amsfonts}
\usepackage[margin=1cm]{geometry}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{multicol}
\usepackage{titlesec}
\parindent 0pt
\setlength{\columnsep}{18pt}
\setlist{noitemsep, topsep=1pt, leftmargin=1.4em}
\titlespacing*{\section}{0pt}{4pt}{2pt}
\titleformat{\section}{\normalfont\large\bfseries}{\thesection.}{0.5em}{}
```

Body wrapped in `\begin{multicols}{2}` at `\footnotesize`, sections as `\section*{N. Name}`.

```latex
\section*{N. Chapter Name}
\begin{itemize}
  \item Topic keywords \hfill (4)(8)
    \begin{itemize}
      \item Sub-topic \hfill (6)
    \end{itemize}
\end{itemize}
```

Rules: two-column newspaper layout, very tight. **No** page breaks between chapters, **no**
table of contents, three nesting levels maximum, no `\subsection` (bold sub-heads are just
`\textbf{...}` on their own line). Keywords only, no sentences.

**Target: one page.** If it runs over, the trick that works is replacing `\maketitle` with a
compact `\begin{center}` title block — that alone recovers about 5 cm of full-width space — and
tightening `\titlespacing` to `{3pt}{1pt}`. Do **not** shrink the body font to `\scriptsize`
to force it; a two-page readable sheet beats a one-page unreadable one.

## 8. Figures in the PYQ documents

The scans are one full-page image per page, so figures are cropped **by rectangle**, not
extracted as objects:

```python
import fitz
d = fitz.open('SOURCE.pdf')
pg = d[PAGE_INDEX]; r = pg.rect
clip = fitz.Rect(r.width*x0, r.height*y0, r.width*x1, r.height*y1)
pg.get_pixmap(matrix=fitz.Matrix(3.2, 3.2), clip=clip).save('images/name.png')
```

Then `\includegraphics[width=5in]{images/name.png}`.

Crop, then **read the PNG back** and re-crop with adjusted fractions if neighbouring text bled in.
Expect two passes on a tight figure. Name crops `<subj>_<year><month>_<what>.png`.

## 9. Definition of done, Part A

- [ ] Every paper in the source scans is transcribed in `ocr/` and accounted for in the document.
- [ ] Question count per paper is sane (no paper contributing suspiciously few questions).
- [ ] `grep '\$\\dots\$'` on the Detailed `.tex` returns nothing.
- [ ] Every year code carries the right bold/plain and mono/plain treatment.
- [ ] The Notes block states this document's own programme convention.
- [ ] Concise fits its page target.
- [ ] Both PDFs rebuilt and committed **together with** their `.tex` sources.

`Overfull \hbox` warnings on a few long question lines are cosmetic; ignore them.

---
# PART B — Exam Notes

## 10. What "make notes of <subject>" means

You are an **editor and subject-matter expert building one cohesive exam-targeted textbook**.
You are **not** a note-merger and not a summariser. If three lecturers' slides say the same thing
three ways, the notes say it once, correctly. If all three are wrong, the notes are right and say so.

**Inputs:** `<Subject>/Notes/` (lecture slides in mixed formats, plus the standard textbook),
`Syllabus/<subject>.tex`, and the already-built `<Subject>_Sorted_PYQ_Detailed.tex` plus its
`ocr/` archive.

**The OCR archive, not the PYQ document, is the authority for tier counts.** The sorted PYQ
document is a derived artefact and can carry errors (in this project it mis-tagged three years
and had dropped one paper entirely). Count frequencies off the archive; if that disagrees with
the PYQ document, fix the PYQ document.

This is a multi-session job. It compounds errors if the map is wrong, so the checkpoints below
are deliberate and non-negotiable.

## 11. Phase 0 — scope report, then STOP

Produce a report and **wait for the student to confirm** before writing any content:

1. Syllabus structure with topic counts.
2. Notes inventory: how many files, what formats, which need OCR or COM extraction.
3. PYQ inventory: papers, years, questions per chapter.
4. **Frequency table per chapter**, with the tier thresholds written as concrete counts.
5. Contradictions and outdated content already spotted between sources.
6. Proposed chapter list, so filenames are fixed up front and never churn.

**Tier definitions** (denominator = total papers in the set; here 22):

| Tier | Rule | Chip |
|---|---|---|
| TOP | asked in **6+** papers | `\tS{n}` orange fill |
| HOT | asked in **3–5** papers | `\tF{n}` blue fill |
| PIN | **1–2** papers but **>=6 marks** | `\tP{n}` purple fill |
| `syllabus, no PYQ yet` | never examined; written anyway | plain grey text |

Scale the thresholds to the paper count and **state them in the notes themselves**. Hard-code
the denominator into the chip macros (`TOP n/22`) so a reader knows what the count is out of.

## 12. Phase 1 — one chapter at a time, checkpoint after each

### A. Content

Per topic, use only the sub-sections that actually apply:

```
Definition -> Key idea -> Steps/Algorithm -> Formula -> Example
           -> Advantages/Disadvantages -> PYQ relevance
```

Order **within** a chapter:

1. frequently repeated PYQ material
2. high-mark / core concepts
3. prerequisites
4. formulas and procedures
5. worked examples
6. supplementary (keep minimal)

Include where relevant: small worked examples; diagrams (see §16 — copied, never redrawn);
comparison tables **only** for pairs actually confused in the papers; and ready-to-write
5-mark / 8-mark answer skeletons as bullets, not essays.

Open every chapter with a **"Read this first"** block: which two or three questions carry the
chapter, the one trade-off or idea everything hangs off, and which pairs the examiner reliably
asks together. This is the highest-value paragraph in the file — it is what a student reads the
night before.

### B. PYQ mapping

- Tag **every** question with its tier and its year codes.
- Group same-question-different-wording under one entry, noting the variant phrasings.
- A question in the papers that the lecture notes do not cover: research it, write it, mark it
  **`[verified/added]`**.
- A syllabus topic with zero notes coverage: same treatment, same badge.
- A syllabus topic never examined: still write it, labelled `syllabus, no PYQ yet`.

### C. Numerical companion

A **separate file per chapter** that has numerical content. Say so explicitly when a chapter
has none.

- One explanation per distinct **method**, then each PYQ instance as a solved problem.
- Open the file with "the N formulas everything here is built on".
- Every numerical opens with the **question as printed** (§13), then:

```
Problem -> Given -> Formula/Method -> Step-by-step -> Final Answer
```

- 1–2 extra practice problems only where a pattern is not covered by any PYQ. Label those
  `PROBLEM`, not `QUESTION AS PRINTED`.

## 13. The `asked` block — verbatim question, always

Every numerical opens with the exam question **exactly as the paper prints it**, data table and
all, so the problem can be attempted from the PDF alone. Source it from the OCR archive.

```latex
\begin{asked}{2071 Bhadra \textperiodcentered{} Q2 \textperiodcentered{} [4+4]}
Prove that for a hexagonal geometry the co-channel reuse ratio is given by
$Q = \sqrt{3N}$; Where $N = i^2 + j^2 + ij$. A cellular service provider decides to use a
digital TDMA scheme which can tolerate a Signal-to-Interference Ratio of 15 dB in the worst
case. Find the optimal value of $N$ for
\begin{enumerate}[label=\alph*), leftmargin=1.6em]
  \item Omni directional antennas
  \item $120^\circ$ Sectoring
  \item $60^\circ$ Sectoring
\end{enumerate}
[Use path loss exponent of 4 and consider trunking efficiency]
\end{asked}
```

- The paper's own typos are reproduced, with a small grey note pointing them out.
- Optional first argument relabels the band: `\begin{asked}[PROBLEM]{not a PYQ ...}`.
- Where the papers only ask the theory but a numerical is worth working anyway, **both** bands
  appear: `QUESTION AS PRINTED` then `PROBLEM`.
- The environment is a `list`, not a `minipage`, **on purpose** — it must be breakable, because
  a statement carrying a full data table will not fit in the space left on a page.

## 14. Phase 2 — cross-check

Verify every formula, algorithm step, definition and numerical answer against the syllabus, the
notes and reliable external sources. **Never preserve an error just because several source notes
repeat it.** Resolve contradictions; note the non-obvious corrections. De-duplicate across
chapters: keep content where it is most central, cross-reference from elsewhere.

Numerical answers get a machine check, not an eyeball — see §18.

## 15. Phase 3 — deliverables

- One PDF per chapter, in syllabus order.
- One numerical companion PDF per chapter that has numericals.
- A closing **Last-Minute Revision** section: Must Know / Must Memorize / Must Practice /
  Most Repeated PYQs / One-Day Revision checklist.
- An **abbreviation chart** at the end of every standalone document (`abbrev.tex`, `\input` at
  the end of each), listing every short form used, the exam-paper month codes, and what the tier
  and mark chips mean.
- Optionally a Formula Sheet / Algorithms / PYQ Classification PDF — **only if genuinely
  non-duplicative.** In practice these were skipped.

- **Two combined masters, built last, once the chapter content is frozen:**
  `master.tex` → `<Subject> - Complete Exam Notes.pdf` (all theory chapters, then Last-Minute
  Revision and the abbreviation chart) and `master-num.tex` →
  `<Subject> - Complete Numerical Problems & Solutions.pdf` (every numerical companion in
  syllabus order, then the chart). Both are thin wrappers: they `\input` the same `chN.tex` /
  `chN-num.tex` the standalones use, so a master is never a second copy of the text. The
  companions head themselves with `\section*`, which produces no TOC entry — the master adds
  `\phantomsection\addcontentsline{toc}{section}{...}` before each `\input` rather than editing
  the chapter files. Title page carries a per-chapter count table; drop the chapters that set
  no numericals and say in the blurb that no paper asks for one.

Order of work is standalone chapters first, masters at the end — a master built early has to be
rebuilt after every chapter edit.

## 16. House style — how the writing has to read

The reference is the student's own preferred note sets — terse, scannable, exam-oriented.

**Prose is banned. Everything becomes points.** Never write an explanatory paragraph where a
bullet stack will do. This sentence:

> *"Loose coupling: the mining system fetches data from a repo managed by the DB/DW and stores
> results back into a file, using the DBMS for storage and retrieval only, so it cannot exploit
> indexing and does not scale"*

becomes one bullet per clause, each starting from its subject, with `->` carrying the consequence.

**Never chain clauses with a semicolon or a comma-list inside one bullet.** Indent them into
sub-bullets. `ROLAP: extended relational DBMS; maps multidim ops -> relational ops. Scales large.`
becomes `ROLAP:` plus three sub-bullets.

**Cut words hard, but only abbreviate what is instantly recognisable.**

- Drop articles (a, an, the) wherever the line still reads.
- Safe: DB, DW, DBMS, OLAP, OLTP, ETL, BI, ER, PCA, KNN, ANN, attr(s), dim(s), multidim, txn,
  info, ops, repo, freq, config, no., w/, w/o, rm, vs, Eg, +Fig — plus whatever is standard in
  your own subject.
- **Do not invent cryptic ones.** `char.`, `betw`, `defn`, `mem`, `sim`, `dept`, `prob` were all
  rejected. Write those out.
- Use `->` for "leads to / therefore", `+` for "and", `=` for "is".

**Never use em dashes.** Use `:` , `->` , `,` or brackets. This is absolute.

**Never type a literal check or cross character.** The Lato font has no glyph for U+2713/U+2717
and Tectonic does not fall back silently — they render as empty tofu boxes (about 70 of them in
one file before this was caught). Use the `\checkmark` / `\xmark` macros in the preamble.

**Mark up questions the way the student does.** Question heading = bold, with the marks it has
carried in brackets after it (`[3] [4] [5]` when the same question recurred at different marks).
The tier badge and year codes go on a small muted line underneath.

**Use the horizontal space.** Two-column side-by-side blocks for paired content, image-right /
text-left for anything with a figure. Never let a figure sit alone on a full-width line if text
can sit beside it.

**Numerical solutions get more room than theory bullets — do not compress them to match the terse
house style.** Every step must show the calculation performed, why it was done, and which formula
was used. This is the `Step-by-step` field taken literally. Still visually tidy — aligned tables,
boxed final answers, `\lead{}` step headers — just not word-count-minimised.

> The real failure mode found in a sweep of an earlier subject was **not** general terseness. It
> was **"the table given nowhere"**: a problem built `L1`–`L3` from a 9-transaction table that
> was never printed, so the reader could not check a single count. If you audit numerical files,
> check for that first. Print the data, then show the lookups the counts came from
> (`AC: T1, T3 -> 2` style).

**Figures: never redraw.** See §17.

## 17. Figures — copy them, never redraw

Screenshot the figure out of the source PDF, or export the slide from the source `.ppt`
(PowerPoint COM `Slide.Export`, or a PyMuPDF clip-crop for PDFs), then trim the watermark strip.
Build something by hand only when it is genuinely trivial — i.e. a table.
**Redrawing diagrams in TikZ is the wrong output for this project.**

A `figs.py` in `src/` owns every crop, so figures are reproducible rather than hand-made
one-offs. Three ways to locate a figure:

```python
add(name, pdf, page)                  # largest EMBEDDED RASTER on that page. Most slide decks
                                      # paste figures as images, so this is exact -> the default.
                                      # pick=n takes the n-th largest instead.
add(name, pdf, page, box=(a,b,c,d))   # manual clip in page-size fractions. Needed for vector
                                      # drawings and for scanned pages (whole page is one image).
add(name, pdf, page, flat=True, ...)  # rebuild the page from its embedded images instead of
                                      # letting PyMuPDF render it.
```

That third mode exists because of a real trap: **one lecturer's deck rendered every figure as a
solid black box.** Its images are 8-bit `/Indexed` over an `ICCBased` base, and PyMuPDF drops the
palette on render. Decoding the index stream through the lookup table by hand recovers them
exactly. If a crop comes out black, this is why — the figure is not lost.

Also: **decks mix page sizes**, so a box fraction tuned on one file will be wrong on another from
the same course. Always read the crop back before shipping it.

### 17a. Figure coverage: every figure-less topic, every graph-shaped numerical

Standing rule since 2026-09-20 (AI), applied to O&M, RF and Data Mining on 2026-09-21:

1. **Census first.** Split each `ch*.tex` on line-start `\T{` and list the bands with no
   `\figT` / `\figC` / `\includegraphics` / tikzpicture. Every band whose answer is visual
   (architecture, block diagram, flow, cross-section, curve, anything asked "with a neat
   diagram") gets a sourced crop. Leave a band bare only when the figure would be a redraw of a
   list, or no local source draws it, and say which in the commit.
2. **Vector textbooks are the best source.** `figs_books.py` (RF, DM) finds the box from the text
   layer alone: caption below, last full-width prose block or numbered equation above, running
   head skipped, union of drawings between. Stacked (a)/(b) panels can be split and set side
   by side to halve the height.
3. **Numericals that ask for a graph get a generated one** (dendrogram, decision tree, FP-tree
   evolution, stability circles, Smith-chart matching, zone strips, boxplot). The script recomputes
   from the problem data and **asserts every drawn value is printed in the .tex** before drawing:
   `ampfig.py`, `zonefig.py` (RF), `dendfig.py`, `dtfig.py`, `fpfig.py`, `boxfig.py` (DM),
   `searchfig.py`, `semnet.py`, `resgraph.py` (AI).
4. **A figure inside an `\sbs` column makes the unbreakable pair taller and it jumps a page.**
   Log each column's height first (a temporary `\renewcommand{\sbsr}` that `\typeout`s both
   minipage heights), put figures only where a column has slack, else make a small pair of their
   own. Compare `audit.py` short pages against a HEAD build of the same chapters before committing.

### 17b. Step figures: the solution drawn, one panel per step

Standing rule since 2026-09-21 (AI ch2-num, ch6-num), applied to all six Data Mining
numerical companions on 2026-09-22. **Every numerical ends with its solution drawn**, not only
the ones whose answer is a graph (17a.3).

1. **One panel per step of the worked solution**, in the order the notes argue it. A panel shows
   the state *after* its step: the tree so far, the matrix after the merge, the centroids after the
   move, the cells the metric reads.
2. **A coloured TECHNIQUE chip on every panel** names the move it makes (prune, join, read the axes,
   Laplace, share prefix, smallest entry, move to mean...). The chips are the point: a dozen moves
   solve every problem in the archive, and naming them is what turns a worked answer into a method.
3. **The decisive panel is framed KEY STEP**, and a **generated index** at the top of the chapter
   lists every move, what it says, and where it is used (problem and step; the key step in orange).
4. **The exit test is replay.** The script recomputes the whole solution from the problem data and
   asserts every value it draws is printed in that problem's text. Never read a number out of the
   notes and draw it back: that proves nothing. This is what caught DM ch2's `0.6300`
   (10/15.8745 = 0.6299), ch3's 1.446 entropy typo and ch4's doubled brand dimension.
5. **Match the notes' own arithmetic, not exact arithmetic.** H&K truncates 0.2467 to 0.246, and
   PageRank tables carry each row rounded to 4 places (in float that lands at 0.44834999... and
   rounds the wrong way, so compute those in `Decimal`). Accept a printed value within a small
   tolerance and *display the printed one*, so page and figure never disagree.

`<Subject>/ExamNotes/src/stepkit.py` is the shared machinery: the panel/chip/KEY STEP drawing, the
technique index (two columns past 20 moves), `need()` for the replay assertions, and `render()`,
which compiles every figure in one tectonic run, writes the PNGs and inserts each block at a
`% ch<N>fig:slot <name>` line in the `.tex` (re-running replaces the block, never stacks a second).
Per-chapter scripts are `ch<N>fig.py`. Figures are PNGs so `anki_from_notes.py` carries them onto
the cards — **inline `tikzpicture` is dropped by the converter**, so a drawing that matters must be
generated, not written inline (DM ch4 lost five FP-tree and subgraph drawings to this for months).

## 18. The three-script harness

Every subject's `src/` carries these. They are the reason the output is trustworthy.

| Script | Job | Pass condition |
|---|---|---|
| `build.py` | compile each standalone `.tex`, deploy the PDF one level up under its display name | no LaTeX errors, no over-tall pair |
| `verify.py` | **independently recompute every published numerical answer** and assert it against the printed value | 557/557 here; must be all-pass before a build |
| `audit.py` | read the built PDFs back and report topics torn across a page boundary | **0 stranded headings** |

`verify.py` is the important idea and the one most likely to be skipped. It is a **check, not a
source**: nothing in it reads a number out of the notes and hands it back. Each answer is
recomputed from the problem statement in plain Python, then compared:

```python
def chk(label, got, want, tol=None, rel=2e-3):
    """Assert a recomputed value matches the value printed in the notes."""
    global N_OK
    if tol is None:
        tol = abs(want) * rel if want else 1e-9
    if abs(got - want) <= tol:
        N_OK += 1
    else:
        FAIL.append(f"{label}: recomputed {got!r} but notes print {want!r} (tol {tol:.3g})")
```

Then one `chk(...)` per published answer, with the domain helpers (`fspl`, `erlang_b`,
`hata_urban`, ...) written once at the top. Run it **before** building a numerical target.

Two more checks worth keeping:

- **Content-integrity diff after any layout pass:** extract the text of the old and new PDFs and
  compare as **word multisets**. It is the only check that catches a brace closed in the wrong
  place. Legitimate differences are captions you edited on purpose and hyphenation shifts from a
  changed column width.
- **A PDF open in the student's viewer locks the file on Windows.** The copy fails with "Device
  or resource busy" and the deliverable silently stays stale. `build.py` catches the `OSError`,
  names the files to close, and exits non-zero. Check page counts after deploying.

---

## 19. Layout and visual design

The look is deliberately **not** default LaTeX: a real sans face (Lato), rounded colour chips for
marks and tiers, tinted band sub-headings, tinted table header rows, thin light rules.

Each chapter is a `\input`-ed body plus a tiny standalone wrapper:

```latex
\documentclass[10pt]{article}
\input{preamble}

\begin{document}
{\LARGE\bfseries Wireless Communication \gap\textcolor{sub}{Exam Notes}}\par
{\footnotesize\color{sub} EX 715 (BEI) / EX 751 (BEX) $\cdot$ IV-I $\cdot$ TU, IOE
$\cdot$ tiers over 22 papers, 2070--2082 BS}
\vspace{3pt}\hrule\vspace{4pt}

\setcounter{section}{1}     % so Ch2's \section prints as "2."
\input{ch2}

\input{abbrev}
\end{document}
```

And this is what a topic looks like in a chapter source — band, question heading with mark chips,
muted tag line, then a side-by-side pair:

```latex
\T{2.1 The cellular concept}

\Q{What is the cellular concept? What is a cell footprint? Explain interference tier}{\m{1+4}\m{5}}
{\color{sub}\footnotesize \yr{80 Ch} \gap$\cdot$\gap background for every other question here}

\sbs{%
\lead{The problem it solved}
\begin{itemize}
  \item Early mobile radio $=$ \textbf{one high-power transmitter} on a tall tower.
  \begin{itemize}
    \item Large coverage, but the same frequencies could \textbf{never} be reused inside it.
  \end{itemize}
  \item Spectrum is fixed by the regulator $\rightarrow$ capacity could not grow.
\end{itemize}}{%
\lead{The cellular idea}
\begin{itemize}
  \item Replace one high-power transmitter with \textbf{many low-power transmitters}.
  \item \textbf{Reuse the same channel set} at cells far enough apart.
\end{itemize}}

\penalty0\vspace{2pt}
```

Note the `\penalty0` in front of the standalone `\vspace`. That is not decoration — see §21.

The full shared preamble follows. **Copy it verbatim.** Only three things are subject-specific:
the tier-chip denominators (`/22`), the running header text, and the palette if you want a
different accent colour.

```latex
% =====================================================================
%  Wireless Communication — Exam Notes : shared preamble
%  Lifted verbatim from Data Mining\ExamNotes\src\preamble.tex; only the
%  tier-chip denominators and the running header differ.
%  Style: bare-bones bullets, modern sans, marks as chips,
%         figures copied from source PDFs/slides (never redrawn).
% =====================================================================
\usepackage[margin=1.45cm, top=1.35cm, bottom=1.35cm]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{array}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{colortbl}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage{needspace}
\usepackage[T1]{fontenc}
\usepackage[default]{lato}
% beramono silently fails to load under tectonic (no mono font ends up
% embedded and \texttt falls back to CM Roman). lmtt does load.
\renewcommand{\ttdefault}{lmtt}
\usepackage{microtype}

\parindent 0pt
\setlength{\parskip}{2pt}
\linespread{1.05}
% no orphans and no widows anywhere: a heading's year-tag line and the
% opening lines of an answer must not be cut off from each other
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\brokenpenalty=10000

% ---------------------------------------------------------------- palette
\definecolor{ink}{HTML}{16202A}   % body text
\definecolor{sub}{HTML}{6B7785}   % muted meta text
\definecolor{acc}{HTML}{2563A8}   % primary accent (section, headings)
\definecolor{accL}{HTML}{D6E4F5}  % accent tint
\definecolor{mkc}{HTML}{C2410C}   % marks / warnings
\definecolor{mkL}{HTML}{FDEBD9}
\definecolor{gd}{HTML}{15803D}    % verified/added
\definecolor{gdL}{HTML}{DCFCE7}
\definecolor{pin}{HTML}{6D28D9}   % pin tier
\definecolor{ruleL}{HTML}{DEE3E8}
\definecolor{rowL}{HTML}{F4F7FA}
\color{ink}

% tight lists: this is the whole look
\setlist{topsep=1pt, itemsep=0.6pt, parsep=0pt, partopsep=0pt}
\setlist[itemize,1]{leftmargin=1.15em, label=\textcolor{acc}{\textbf{\textendash}}}
\setlist[itemize,2]{leftmargin=1.05em, label=\textcolor{sub}{\textendash}}
\setlist[itemize,3]{leftmargin=1.05em, label=\textcolor{sub}{$\circ$}}
\setlist[enumerate,1]{leftmargin=1.5em, label=\textcolor{acc}{\bfseries\arabic*.}}

% ---------------------------------------------------------------- chips
% rounded pill used for marks and tier badges
\newcommand{\pill}[3]{%
  \tikz[baseline=(p.base)]{\node[rounded corners=2.2pt, inner xsep=3.4pt,
        inner ysep=1.5pt, fill=#1, text=#2, font=\bfseries\scriptsize] (p) {#3};}}
\newcommand{\pillo}[2]{%
  \tikz[baseline=(p.base)]{\node[rounded corners=2.2pt, inner xsep=3.2pt,
        inner ysep=1.3pt, draw=#1, line width=0.4pt, text=#1,
        font=\bfseries\scriptsize] (p) {#2};}}

\newcommand{\m}[1]{\pill{mkL}{mkc}{#1}\hspace{0.5pt}}          % marks chip
\newcommand{\tS}[1]{\pill{mkc}{white}{TOP\, #1/22}}            % 6+ papers
\newcommand{\tF}[1]{\pill{acc}{white}{HOT\, #1/22}}            % 3-5 papers
\newcommand{\tP}[1]{\pill{pin}{white}{PIN\, #1/22}}            % 1-2, >=6 marks
\newcommand{\added}{\pill{gdL}{gd}{verified/added}}
\newcommand{\yr}[1]{\textcolor{sub}{\footnotesize #1}}
\newcommand{\mk}[1]{\textcolor{mkc}{\bfseries#1}}
\newcommand{\gap}{\hspace{0.55em}}
% pass/fail marks for tables and inline checks: Lato has no glyph for the
% Unicode check/cross characters (renders as a tofu box), so route through
% \checkmark (amssymb, already has a Lato-independent math glyph) and this.
% Both are control words, so TeX silently eats the space after them when
% they're followed by more prose ("\checkmark all" -> "\checkmarkall") --
% \xspace fixes that without adding a space before closing punctuation.
\usepackage{xspace}
\newcommand{\xmark}{\ensuremath{\times}\xspace}
\let\origcheckmark\checkmark
\renewcommand{\checkmark}{\origcheckmark\xspace}
% inline code / file name with a soft tint
\newcommand{\code}[1]{{\setlength{\fboxsep}{1.2pt}\colorbox{rowL}{\texttt{\small #1}}}}

% ---------------------------------------------------------------- headings
\titleformat{\section}
  {\normalfont\LARGE\bfseries\color{acc}}{\thesection.}{0.35em}{}
  [\vspace{-7pt}{\color{acc}\rule{\textwidth}{1.1pt}}]
\titlespacing*{\section}{0pt}{6pt}{7pt}

% ------------------------------------------------------- keeping a topic whole
% Lower-case \needspace reserves space by injecting stretchable glue in FRONT
% of a -100 penalty, so the reserve doubles as the width of a window in which
% TeX finds that penalty cheap: it breaks there whenever the free space is
% under roughly 4.6x the reserve, which is where the half-empty pages came
% from (at 11\baselineskip the window ran to ~640pt). Capital \Needspace, from
% the same package, instead compares \pagegoal-\pagetotal against the reserve
% and breaks only when the page really is that short. No window, so the
% reserve can be honest. Every heading below uses it.
%
% Second half of the same problem: a topic band was being stranded at the foot
% of a page with its question on the next one, and the culprit was the
% FOLLOWING heading's own reserve, which put a breakpoint between the two. \T
% raises \ifbandopen and \Q / \creamq answer it with \nobreak instead of a
% reserve of their own, so band, heading and the opening lines of the answer
% can only travel together.
% The flag has to be global (a band is often followed by a tag line wrapped in
% a group) and it has to expire on its own, or a band followed by prose rather
% than a heading would rob the NEXT question of its reserve. So the first
% paragraph started after a band clears it through \everypar and puts \everypar
% back the way it found it.
\newif\ifbandopen
\newcommand{\bandon}{\global\let\ifbandopen\iftrue
  \global\everypar{\bandoff\global\everypar{}}}
\newcommand{\bandoff}{\global\let\ifbandopen\iffalse}
\bandoff
\newcommand{\holdspace}[1]{%
  \ifbandopen \nobreak \bandoff \else \Needspace{#1\baselineskip}\fi}

% Third instalment of the same problem, 2026-08-30: the reserve is a
% guess (9 or 12 lines) and the answer under the heading is usually a \sbs
% pair three or four times that tall, so the reserve was satisfied, the
% band + heading + year-tag line were set, and then the unbreakable pair
% would not fit and went overleaf -- heading at the foot of one page, its
% whole answer on the next.
%
% Guessing a bigger reserve only trades the split for wasted paper. What
% actually fixes it is removing every legal breakpoint between the band and
% the first block of the answer, so the page builder has to fall back to the
% breakpoint BEFORE the band and move the topic whole. \nobreak (penalty
% 10000) is the only value that works: an underfull page costs 100000
% whatever penalty sits there, so 9999 would still be taken, and ties go to
% the later breakpoint.
%
% The junctions are: band|heading (already \nobreak), heading|rule,
% rule|tag, inside the tag paragraph, and tag|answer. The tag line is plain
% source text rather than a macro, so the last three are closed by \qhold
% below, which is where all the awkwardness lives.
%
% There is no escape hatch, because TeX will not give one: \unpenalty is
% illegal on the main vertical list, so the glue cannot be taken back once
% laid down, and any finite penalty loses to a later breakpoint (an underfull
% page costs 100000 whatever the penalty, and ties go to the later one). A
% pair too tall to fit under its own heading on a fresh page therefore has
% nowhere to break and would print past the bottom margin. \sbsr measures
% itself and shouts @SBS-TOO-TALL at build time instead; build.py fails on
% it. The fix for one is always the same and always in the content: split it
% into two pairs at a \lead boundary.
\makeatletter
\newcommand{\qhold}{%
  \nobreak
  % the tag line must not break in the middle either, and \clubpenalty
  % alone cannot say that for a three-line one
  \global\interlinepenalty10000
  % ... and it must not come away from the answer under it. There is no
  % LaTeX hook for "after the next paragraph": para/after would do it, but
  % switching the paragraph hooks on inserts its own node ahead of \parskip
  % and hands the page builder back the very breakpoint being closed. So
  % \par is borrowed for exactly one paragraph and put back on first use.
  \global\let\qhsavedpar\par
  \gdef\par{\qhsavedpar\global\let\par\qhsavedpar
            \global\interlinepenalty0 \nobreak}%
  % Last junction, and the one that cost the most to find: a tag line is
  % written {\color{sub}\footnotesize ...}, and \color in vertical mode puts
  % a whatsit on the list. A whatsit is not discardable, so the \parskip glue
  % that follows it becomes a legal breakpoint again and the \nobreak above
  % is wasted -- the heading would keep its rule and lose its tag. Starting
  % the paragraph here instead means \color runs in horizontal mode and
  % \parskip lands directly behind the \nobreak. Only do it when a group
  % really does come next, or a following \sbsr or list would be handed an
  % empty paragraph and an extra baseline of white.
  \qh@peek}
% The lookahead has to step over a blank line first: \T is normally followed
% by one, and that \par would otherwise both fail the group test and burn the
% one-shot hook above. Swallowing it is safe because a band always ends in
% vertical mode, so the \par would have been a no-op anyway.
\newcommand{\qh@peek}{%
  \@ifnextchar\par{\qh@eatpar}{\@ifnextchar\bgroup{\leavevmode}{}}}
\long\def\qh@eatpar#1{\qh@peek}
\makeatother

% Q = exam question heading. #1 text, #2 mark chips
\newcommand{\Q}[2]{%
  \par\vspace{7pt}\holdspace{9}%
  \begingroup\interlinepenalty10000 \noindent
  {\large\bfseries\color{ink}#1}\hspace{0.45em}#2\par\endgroup
  \nobreak\vspace{1pt}%
  \nobreak\noindent{\color{ruleL}\rule{\textwidth}{0.7pt}}\par
  \nobreak\vspace{1.5pt}\qhold}

% T = topic band (tinted full-width bar). The reserve has to cover the band,
% the question heading under it, the year-tag line and a few lines of answer.
% \qhold at the end covers the case where the band is followed by prose
% rather than by a \Q: without it the band strands at the foot of the page
% with its intro line, or with nothing at all. When a \Q does follow,
% \qhold's lookahead sees a control sequence rather than a group, so it
% leaves the paragraph unstarted and \ifbandopen survives for \Q to answer.
\newcommand{\T}[1]{%
  \par\vspace{7pt}\Needspace{12\baselineskip}\noindent
  \colorbox{accL}{\makebox[\dimexpr\textwidth-2\fboxsep][l]{%
    \textcolor{acc}{\bfseries #1}}}\par\nobreak\vspace{3pt}\bandon\qhold}

% small question sub-heading inside PYQ lists
\newcommand{\creamq}[2]{%
  \par\vspace{4pt}\holdspace{6}%
  \begingroup\interlinepenalty10000
  {\bfseries\color{acc}#1}\hspace{0.4em}#2\par\endgroup
  \nobreak\vspace{1pt}\qhold}
\let\qq\creamq

% ---------------------------------------------------------------- question box
% \begin{asked}{<year / marks tags>} ... \end{asked}
%   The exam question reproduced as the paper prints it, data table and all,
%   so a problem can be attempted from this document alone. Optional first
%   argument relabels the band for problems that are not PYQs.
%   Breakable across pages on purpose (a list, not a minipage): several
%   statements carry a full data table and will not fit in the space left.
\newenvironment{asked}[2][QUESTION AS PRINTED]%
  {\par\vspace{4pt}\Needspace{4\baselineskip}\noindent
   \colorbox{rowL}{\makebox[\dimexpr\textwidth-2\fboxsep][l]{%
     \textcolor{acc}{\bfseries\scriptsize #1}\hspace{0.7em}%
     \textcolor{sub}{\footnotesize #2}}}\par\nobreak\vspace{2pt}%
   \begin{list}{}{\leftmargin=9pt \rightmargin=0pt \topsep=0pt
                  \partopsep=0pt \parsep=1.5pt \itemsep=0pt}\item[]\small}
  {\end{list}\vspace{1pt}}

% ---------------------------------------------------------------- abbreviations
% \abbr{SHORT}{long}  — one row of the closing abbreviation chart
\newenvironment{abbrtable}
  {\par\vspace{2pt}\begin{tabularx}{\textwidth}{@{}L{1.9cm}X@{}L{1.9cm}X@{}}}
  {\end{tabularx}\par}
\newcommand{\abbr}[1]{\textbf{#1}}

% bold lead-in line
\newcommand{\lead}[1]{\vspace{2.5pt}\par\textbf{#1}\par\vspace{0.5pt}}

% ---------------------------------------------------------------- figures
\newcommand{\figC}[2]{\begin{center}\includegraphics[width=#2]{figs/#1}\end{center}}
% figure INSIDE a side-by-side column: \vspace{0pt} pins the minipage
% reference point to the TOP, else the image baseline shoves text down.
\newcommand{\figT}[1]{\vspace{0pt}\includegraphics[width=\linewidth]{figs/#1}}

% side-by-side columns
%   \sbsr{left width fraction}{left}{right}
%   \sbs{left}{right}  -> even split
% minipage on purpose: an unbreakable box, so a topic and its contents are
% never torn across a page. Costs some blank space at the foot of a page
% when a pair does not fit; that trade was made deliberately -- keeping a
% topic whole beats filling the page. Do NOT "fix" this with paracol or
% multicol: both split the pair and were reverted for exactly that reason.
% The pair is built into a box first so it can be measured. A pair taller
% than \sbsmax cannot fit under its own heading on any page, so the \nobreak
% that \qhold laid down between the tag line and this pair is taken back off
% the vertical list -- otherwise the topic would have no legal breakpoint at
% all and would print past the bottom margin. Anything over \sbsmax is a
% content bug: split it into two pairs at a \lead boundary.
\newlength{\sbsmax}\setlength{\sbsmax}{0.78\textheight}
\newsavebox{\sbsbox}
\newcommand{\sbsr}[3]{%
  \par
  \setbox\sbsbox=\hbox to\textwidth{%
  \begin{minipage}[t]{#1\textwidth}\vspace{0pt}\raggedright #2\end{minipage}%
  \hfill
  \begin{minipage}[t]{\dimexpr 0.97\textwidth - #1\textwidth\relax}%
    \vspace{0pt}\raggedright #3\end{minipage}}%
  \typeout{@SBS \the\dimexpr\ht\sbsbox+\dp\sbsbox\relax\space of \the\textheight}%
  \ifdim\dimexpr\ht\sbsbox+\dp\sbsbox\relax>\sbsmax
    \typeout{@SBS-TOO-TALL \the\dimexpr\ht\sbsbox+\dp\sbsbox\relax}%
  \fi
  \noindent\usebox{\sbsbox}\par}
\newcommand{\sbs}[2]{\sbsr{0.485}{#1}{#2}}

% ---------------------------------------------------------------- tables
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\arrayrulecolor{ruleL}
\newcommand{\thead}[1]{\textcolor{acc}{\bfseries#1}}
\newcommand{\hr}{\vspace{3pt}{\color{ruleL}\rule{\textwidth}{0.7pt}}\vspace{2pt}\par}
% tinted header row for tabularx
\newcommand{\hrow}{\rowcolor{rowL}}

% ---------------------------------------------------------------- header
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\footnotesize\color{sub} Wireless Communication \textperiodcentered{} EX 715 / EX 751}
\fancyhead[R]{\footnotesize\color{sub}\thepage}
\renewcommand{\headrulewidth}{0pt}
\fancyheadoffset{0pt}

```
---

## 20. The column model is settled — do not "optimise" it

`\sbs` / `\sbsr` are **minipage-based**. Three generations were built and both alternatives were
rejected by the student:

| Approach | Behaviour | Verdict |
|---|---|---|
| **minipage** (current) | unbreakable box; a topic and its contents are never torn across a page. Costs blank space at the foot of a page when a pair does not fit. | **kept** |
| paracol | breakable, but the two sides are synced streams: when they need different amounts of room both break at the same point, leaving a short side mostly blank under its own heading. | rejected |
| multicol | true flowing newspaper columns; fixed paracol's blank slabs and read correctly, but **split topics across the column gutter**. | rejected |

The verdict on both alternatives was *"this just ended up making it confusing"*. The student wants
**all topics more or less trying to remain on the same page**, and accepts the blank space that costs.

**Therefore: blank space at the foot of a page is NOT a bug here.** If a page looks empty, fix it
by adjusting **content** — widen the text column, shrink the figure column, split a tall table —
never by changing the box model. Getting this wrong cost a full rebuild cycle.

## 21. Keeping a topic whole — the pagination law and its four TeX traps

This is the part that took three passes to get right, and every trap below looks exactly like
"the macro simply did not work".

**Measure two defects separately, because they need different fixes.**

- **STRANDED** — the last ink on a page is a topic band, a question heading, or a year-tag line,
  so the answer it introduces sits overleaf. **This is a bug. It must be 0.**
- **GAP** — the ink stops well above the bottom margin. **This is not a bug**; it is the
  sanctioned price of moving a topic whole. A big one is still worth a look: split that topic's
  pair at a `\lead` boundary so half stays and half flows over.

Classify by **how a line is set**, not by what it says. A grey `\footnotesize` line on its own is
a figure **caption**; it only counts as a year-tag when a heading or band sits directly above it.
Without that rule the audit is ~80% false positives.

### Trap 1 — lower-case `\needspace` creates the very breakpoint it is supposed to prevent

`\needspace{N}` reserves space by emitting `\vskip 0 plus N` **in front of** a `\penalty-100`.
So the reserve doubles as the width of a window in which that penalty is cheap: TeX takes it
whenever the free space is under roughly **4.6x the reserve**. At `11\baselineskip` that window
ran to ~640pt, i.e. half-empty pages everywhere.

Worse, the culprit for stranded headings was **not the band's own reserve** but the **following**
heading's — every `\Q` opened a bargain breakpoint sitting exactly between the band and its content.

Capital **`\Needspace{N}`** (same package) instead compares `\pagegoal-\pagetotal` against the
reserve and calls `\break` only when the page really is that short. No glue, no window, so the
reserve can be honest. Switching every heading to it fixed the orphans **and** cut foot-of-page
whitespace by 22% and the page count 201 -> 195 across 13 PDFs.

### Trap 2 — a reserve is a guess, and the answer is bigger than any guess

Even with `\Needspace`, topics still split: the reserve is 9 or 12 lines while the `\sbs` pair
under the heading is three or four times that tall. The reserve passed, band + heading + tag were
placed, and then the unbreakable pair went overleaf anyway.

**A bigger reserve only trades the split for wasted paper.** The fix is to **remove every legal
breakpoint between the band and the first block of the answer** (`\qhold`), so the page builder
must fall back to the breakpoint *before* the band and carry the whole topic over.
Stranded headings 31 -> 0.

### Trap 3 — `\color` in vertical mode re-opens the breakpoint you just closed

`\color` appends a **whatsit**, and a whatsit is **not discardable**, so the `\parskip` glue behind
it becomes a legal breakpoint again and the `\nobreak` in front of it is wasted. Every tag line is
written `{\color{sub}\footnotesize ...}` — which is precisely why the heading kept losing its tag
no matter how many `\nobreak`s were added.

Cure: start the paragraph yourself (`\leavevmode`) so `\color` runs in horizontal mode. Guard it
with `\@ifnextchar\bgroup`, or a following `\sbsr`/list gets an empty paragraph and a spare
baseline of white. And step over the blank line first, or the `\par` burns the one-shot hook.

### Trap 4 — `para/after` makes it worse, only `\penalty10000` works, and there is no undo

- **LaTeX's `para/after` hook cannot close that junction.** Switching the paragraph hooks on
  inserts its own node ahead of `\parskip` and hands back the very breakpoint you are closing.
  The symptom is that adding the hook makes the split *worse*. Borrow `\par` for exactly one
  paragraph instead and restore it on first use.
- **Only `\penalty10000` works.** An underfull page costs 100000 *whatever* penalty sits there
  (TeX's `c = deplorable` when `b = 10000`), and ties go to the **later** breakpoint — so a
  "strongly discouraged" 9999 is still taken. Never reach for a finite penalty.
- **There is no escape hatch.** `\unpenalty` is illegal on the main vertical list
  ("You can't use `\unpenalty' in vertical mode"), so glue once laid down cannot be taken back.
  A pair taller than the page therefore has **nowhere** to break and prints past the bottom
  margin. `\sbsr` measures itself against `\sbsmax` (0.78 `\textheight`) and emits
  `@SBS-TOO-TALL`; **`build.py` fails the build on it.**

### Trap 5 (separate, larger, and invisible) — `\vspace` between two blocks glues them together

`\@vspace` emits `\hrule height0pt \nobreak` **before** its own glue. So a bare
`\par\vspace{2pt}` between two `\sbs` pairs leaves **no legal breakpoint** and both travel as one
lump. This is a large, invisible source of half-empty pages and it predates the orphan work
entirely. **Every standalone `\vspace` in the chapter sources carries `\penalty0` in front of it**
(294 sites in one subject).

The same trap applies between consecutive `tabularx` blocks. `abbrev.tex` needed both shorter
tables **and** `\par\penalty0` between them: `tabularx` cannot break across a page, so a 43-row
block moved whole. Now at most **16 rows per block** — 12-row chunks were tried and cost an extra
page in repeated headers, 16 is the sweet spot.

### Splitting a tall pair is content work, not a script

Cut at a `\lead` boundary. Move the figure up so it travels with the half it illustrates, and give
the second half a **real** right-hand column (the other half of a comparison, a second figure)
rather than an empty one. Aim for **under ~45% of `\textheight`** per pair.
About 30 pairs were split this way. **Not every split helps** — one added a page and had to be
reverted — so rebuild and re-measure after each one.

Target fill: **65–73% mean** per page is the band that reads well.

---

## 22. `build.py`

Compiles each standalone target, fails loudly on errors and on over-tall pairs, and deploys the
finished PDF one level up under its display name. Adapt `TARGETS` and the tectonic lookup.

```python
# -*- coding: utf-8 -*-
"""Build the Wireless Communication exam-notes PDFs.

Run from inside this src\\ folder:   python build.py [ch2] [ch3-num] ...
With no args it builds everything. Finished PDFs land one level up, in
ExamNotes\\, under their display names; everything else stays in here.

Needs tectonic.exe on PATH or in this folder. See the "PYQ LaTeX project
layout" memory for where to find a copy.

Before building a numerical target, run verify.py: it recomputes every
published answer independently and asserts it against the printed value.
"""
import os
import shutil
import subprocess
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

TARGETS = {
    "ch1":     ("ch1-standalone", "Ch1 - Introduction.pdf"),
    "ch2":     ("ch2-standalone", "Ch2 - Cellular Mobile Communication Concepts.pdf"),
    "ch2-num": ("ch2-num-standalone",
                "Ch2 - Cellular Mobile Communication Concepts - Numerical Problems & Solutions.pdf"),
    "ch3":     ("ch3-standalone", "Ch3 - Radio Wave Propagation.pdf"),
    "ch3-num": ("ch3-num-standalone",
                "Ch3 - Radio Wave Propagation - Numerical Problems & Solutions.pdf"),
    "ch4":     ("ch4-standalone",
                "Ch4 - Modulation and Demodulation Methods.pdf"),
    "ch5":     ("ch5-standalone", "Ch5 - Equalization and Diversity Techniques.pdf"),
    "ch5-num": ("ch5-num-standalone",
                "Ch5 - Equalization and Diversity Techniques - Numerical Problems & Solutions.pdf"),
    "ch6":     ("ch6-standalone", "Ch6 - Speech and Channel Coding Fundamentals.pdf"),
    "ch6-num": ("ch6-num-standalone",
                "Ch6 - Speech and Channel Coding Fundamentals - Numerical Problems & Solutions.pdf"),
    "ch7":     ("ch7-standalone", "Ch7 - Multiple Access in Wireless Communications.pdf"),
    "ch7-num": ("ch7-num-standalone",
                "Ch7 - Multiple Access in Wireless Communications - Numerical Problems & Solutions.pdf"),
    "ch8":     ("ch8-standalone", "Ch8 - Wireless Systems and Standards.pdf"),
}


def tectonic():
    if shutil.which("tectonic"):
        return "tectonic"
    local = os.path.join(HERE, "tectonic.exe")
    if os.path.exists(local):
        return local
    # fall back to the Data Mining copy, or any left in a session scratchpad
    sibling = os.path.normpath(os.path.join(
        HERE, "..", "..", "..", "Data Mining", "ExamNotes", "src", "tectonic.exe"))
    if os.path.exists(sibling):
        return sibling
    pat = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude",
                       "D--College-PYQ", "*", "scratchpad", "tectonic.exe")
    hits = glob.glob(pat)
    if hits:
        return hits[0]
    sys.exit("tectonic.exe not found. See the PYQ LaTeX project layout memory.")


def main():
    tex = tectonic()
    names = sys.argv[1:] or list(TARGETS)
    stale = []
    for n in names:
        if n not in TARGETS:
            print("unknown target:", n)
            continue
        stem, pretty = TARGETS[n]
        print(f"--- building {n}")
        r = subprocess.run([tex, "--print", stem + ".tex"], cwd=HERE,
                           capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        err = [l for l in out.splitlines() if l.lower().startswith("error")]
        if err:
            print("\n".join(err))
            sys.exit(f"{n} FAILED")
        # a \sbs pair taller than \sbsmax cannot fit under its own heading on
        # any page. \Q glues the two together, so such a pair has nowhere to
        # break and prints past the bottom margin. Split it into two pairs at
        # a \lead boundary. See the keeping-a-topic-whole note in preamble.tex.
        tall = sorted(set(l for l in out.splitlines()
                          if l.startswith("@SBS-TOO-TALL")))
        if tall:
            print("\n".join("   " + t for t in tall))
            sys.exit(f"{n}: over-tall \\sbs pair, split it at a \\lead boundary")
        src = os.path.join(HERE, stem + ".pdf")
        dst = os.path.join(OUT, pretty)
        try:
            shutil.move(src, dst)
            print("   ->", pretty)
        except OSError as e:
            # a PDF open in a viewer locks the file on Windows
            stale.append((pretty, stem, e))
            print(f"   !! could not replace {pretty}: {e}")
            print(f"      the fresh build is left as src\\{stem}.pdf")
    if stale:
        print("\nClose these in your PDF viewer and rerun the target:")
        for pretty, stem, _ in stale:
            print(f"  {pretty}")
        sys.exit(1)
    print("done")


if __name__ == "__main__":
    main()

```

## 23. `audit.py`

Reads the **built PDFs** back with PyMuPDF and reports stranded headings (bugs) separately from
foot-of-page gaps (the accepted price). The classifier is the part worth copying: it judges a
line by font size, colour and weight, not by its text.

```python
# -*- coding: utf-8 -*-
"""Audit the built PDFs for topics torn across a page boundary.

Run from inside this src\\ folder:   python audit.py [gap-threshold]
Reads the deployed PDFs one level up, in ExamNotes\\.

Two separate defects, and they need different fixes:

  STRANDED  the last thing on a page is a topic band, a question heading or
            a year-tag line, so the answer it introduces sits overleaf.
            This is a BUG. It means a breakpoint is open somewhere between
            the band and the first block of the answer -- see the
            keeping-a-topic-whole note in preamble.tex.

  GAP       the ink stops well above the bottom margin. This is NOT a bug
            on its own: a \\sbs pair is an unbreakable box, so a topic that
            does not fit is moved whole rather than being torn, and the
            blank space is the price. A big one is still worth a look --
            the fix is to split that topic's pair at a \\lead boundary so
            half stays on the page and half flows over.

Classify by how a line is set, not by what it says: a gray footnotesize line
on its own is a figure CAPTION, and only counts as a year-tag when a heading
or a band sits directly above it. Without that rule the report is mostly
false positives.
"""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

MARG = 1.35 * 28.3465          # top and bottom margin, pt (see geometry)
SUB = 0x6B7785                 # muted meta text
ACC = 0x2563A8                 # accent: bands and sub-headings


def classify(spans):
    """What kind of line is this, judged by how it is set."""
    if not spans:
        return ""
    size = max(s["size"] for s in spans)
    colours = {s["color"] for s in spans}
    bold = any("Bold" in s["font"] or "Black" in s["font"] for s in spans)
    if colours <= {SUB} and size < 9:
        return "TAG"
    if bold and size > 10.5:
        return "HEADING"
    if bold and colours <= {ACC}:
        return "BAND"
    return ""


def audit(path, cut):
    doc = fitz.open(path)
    rows = []
    tops = {}
    for i, page in enumerate(doc):
        floor = MARG + 6                       # below the running header
        bottom = 0.0
        lines = []
        for blk in page.get_text("dict")["blocks"]:
            if blk["type"] != 0:               # an image block
                bottom = max(bottom, blk["bbox"][3])
                continue
            for ln in blk["lines"]:
                if ln["bbox"][3] < floor:
                    continue
                if not "".join(s["text"] for s in ln["spans"]).strip():
                    continue
                lines.append((ln["bbox"][3], ln["spans"]))
                bottom = max(bottom, ln["bbox"][3])
        for drawing in page.get_drawings():
            r = drawing["rect"]
            if r.y1 < floor or r.height > page.rect.height * 0.9:
                continue
            bottom = max(bottom, r.y1)
        for img in page.get_images():
            for r in page.get_image_rects(img[0]):
                bottom = max(bottom, r.y1)

        lines.sort(key=lambda t: t[0])
        tops[i] = [" ".join(s["text"] for s in sp)
                   for _, sp in sorted(lines, key=lambda t: t[0])[:2]]
        kinds = [classify(sp) for _, sp in lines[-4:]]
        kind = ""
        if kinds:
            if kinds[-1] in ("HEADING", "BAND"):
                kind = "STRANDED:" + kinds[-1]
            elif kinds[-1] == "TAG" and any(
                    k in ("HEADING", "BAND") for k in kinds[:-1]):
                kind = "STRANDED:TAG"
        gap = ((page.rect.height - MARG) - bottom) / (page.rect.height - 2 * MARG)
        # the last page of a document is meant to end early
        if kind or (gap > cut and i < doc.page_count - 1):
            rows.append((kind, gap, i + 1, doc.page_count))
    out = [(k, g, p, n, tops.get(p, [])) for k, g, p, n in rows]
    doc.close()
    return out


def main():
    cut = float(sys.argv[1]) if len(sys.argv) > 1 else 0.33
    stranded, gaps = [], []
    for fn in sorted(os.listdir(OUT)):
        if not fn.lower().endswith(".pdf"):
            continue
        for kind, gap, pg, n, top in audit(os.path.join(OUT, fn), cut):
            name = fn.split(" - ")[0]
            (stranded if kind else gaps).append((gap, name, pg, n, kind, top))

    if stranded:
        print("STRANDED HEADINGS -- these are bugs:")
        for gap, name, pg, n, kind, top in sorted(stranded, reverse=True):
            print(f"  {gap*100:5.1f}%  {name:<8} p{pg}/{n}  {kind}")
    else:
        print("no stranded headings")

    print(f"\npages ending more than {cut*100:.0f}% short "
          f"(the topic named is the one that would not fit):")
    for gap, name, pg, n, _, top in sorted(gaps, reverse=True):
        print(f"  {gap*100:5.1f}%  {name:<8} p{pg}/{n}  -> "
              + " / ".join(t[:44] for t in top))
    print(f"\n{len(stranded)} stranded, {len(gaps)} short pages")
    return 1 if stranded else 0


if __name__ == "__main__":
    sys.exit(main())

```

---

## 24. Working discipline

**Keep a progress file.** `<Subject>/NOTES-BUILD-PROGRESS.md`, updated at every checkpoint, so a
session that runs out of context can resume exactly where it stopped. Record per chapter: what is
written, the tier table counted from the OCR archive, which topics were written from outside the
lecture notes and carry `[verified/added]`, source defects found, and the current page counts.

**Commit after every PDF build.** Sources and rebuilt PDFs go in the **same commit**. Do not stop
at "not committed, that's your call" — the PDFs are tracked build artefacts, so a
rebuilt-but-uncommitted tree leaves the repo's PDFs out of sync with its `.tex`. Sequence:
`verify.py` -> `build.py` -> `audit.py` -> `git status --short` (watch for untracked `??` entries
in a new folder) -> `git add` the changed sources **and** PDFs -> commit naming the subject and
what changed. Never `--no-verify`.

**Never `git add -A` a tree like this.** Read `git status --short` first. In this project an
indiscriminate `add -A` swept in a 51 MB vendored `tectonic.exe` and the extracted full text of a
commercial textbook, and the history had to be rewritten with `git filter-branch` to strip them.

**Do not commit:** extracted textbook/lecture text (copyright — it is a build input only),
vendored binaries, and internal working notes if the student wants them unpublished. Gitignore
them explicitly.

**Author is the student, not the AI.** Match the surrounding history for trailers —
`git log -5 --format=%b` before writing a message.

## 25. Digest: the things that will bite you

Ordered by how much time each one cost.

1. **The page index of a scan lies.** Confirm every paper from its own header. Expect duplicates,
   blanks, a paper from an entirely different subject, and a header printing the wrong programme.
2. **A reserve cannot stop a heading orphan** — closing the breakpoints can. `\Needspace` not
   `\needspace`; `\qhold` between band and answer; `\penalty0` in front of every standalone
   `\vspace`.
3. **A figure that renders as a solid black box is not lost** — it is a palette-indexed image and
   PyMuPDF dropped the lookup table. Rebuild the page from its embedded images.
4. **A PDF open in the viewer locks the file on Windows.** The copy fails and the deliverable
   silently stays stale. Check the copy landed and check page counts.
5. **Bash heredocs mangle backslashes.** Write any script containing LaTeX with a file-write tool,
   then read it back.
6. **`tabularx` and `minipage` cannot break across a page.** A tall one dumps a big gap at the
   foot of the previous page. Fix it in the content, not the box model.
7. **A `tabularx` opened while a paragraph is still running** is set as an hbox on the current line
   and runs off the right margin. Always `\par` before a table that follows prose.
8. **`beramono` silently fails under Tectonic** — no mono font is embedded and `\texttt` falls back
   to CM Roman. `lmtt` loads.
9. **Literal check/cross characters render as tofu.** `\checkmark` / `\xmark` only.
10. **Regex escapes in Python patch scripts:** a doubled backslash is needed where you would expect
    one, or Python raises "bad escape".

## 26. Definition of done, Part B

- [ ] Phase 0 report delivered and **confirmed** before any content was written.
- [ ] Every chapter checkpointed with the student before moving to the next.
- [ ] Every topic carries a tier badge counted from the **OCR archive** and its year codes.
- [ ] Every numerical opens with the verbatim `asked` block and shows every step.
- [ ] Everything researched or added by you is marked `[verified/added]`.
- [ ] Zero-PYQ syllabus topics written and labelled.
- [ ] `verify.py` all-pass.
- [ ] `audit.py` reports **0 stranded headings**; gaps reviewed and the worst ones split.
- [ ] `build.py` clean — no `@SBS-TOO-TALL`.
- [ ] Abbreviation chart and Last-Minute Revision section present.
- [ ] Word-multiset diff against the previous PDFs shows only intended changes.
- [ ] Sources + PDFs committed together, progress file updated.

## 27. Suggested order of work for a new subject

1. Type the printed syllabus into `Syllabus/<subject>.tex`. This is the spine of everything.
2. Inventory the scans; render and read every page; write `ocr/<name>_OCR.md`. **Do this once, properly.**
3. Build the Detailed PYQ document, syllabus order, no truncation.
4. Build the Concise sheet from it. Target one page.
5. Compile, run the checks in §9, commit.
6. Phase 0 scope report for the notes. **Stop and wait.**
7. Chapter by chapter: content, PYQ mapping, numerical companion. Checkpoint after each.
8. Cross-check pass; `verify.py` grows with every numerical you publish.
9. Layout pass: `audit.py`, split the tall pairs, re-measure.
10. Abbreviations, revision section, final build, commit.

Expect the notes to be the larger job by a wide margin. For reference: one subject came out at
**13 PDFs, 202 pages, 557 verified numerical answers, 0 stranded headings**, across roughly a
dozen working sessions.

---

*End of handoff.*
