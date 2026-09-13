# PYQ Sorted Chapterwise — project instructions

Chapter-sorted past-exam-question compilations for IOE (Tribhuvan University) 7th semester,
plus two sets of full exam notes. LaTeX sources built with Tectonic; inputs are scanned
question papers, almost all of them with no text layer (see golden rule 2 for the one
exception).

**The full method lives in `HANDOFF-pyq-and-notes-method.md`.** Read it before writing
anything. `handoff-current.txt` holds the running status board and session log.

## Golden rules

These are the measured cost drivers in this repo (223 MB tracked: 165 MB of PDFs,
57 MB of PNGs, and only 1.2 MB of `.tex`). Breaking one of them is what makes a session
expensive.

1. **Never read a source scan as a page image when `<Subject>/ocr/*_OCR.md` already covers
   it.** The archives are complete and verbatim for O&M (29 papers), RF-Microwave (24),
   DSAP (44), Wireless (22), AI (41, all three of CT653/CT710/CT78506 — two files, the
   older one holding the 17 papers the newer one cross-references) and Data Mining (23 —
   also two files, one per scan, and here *neither* scan is a superset of the other).
   Re-render a page only to crop a figure, or when the archive itself flags a line as
   uncertain.

2. **Check for a text layer before doing anything else.** One line settles it:

   ```bash
   python -c "import fitz; print(repr(fitz.open('New PYQ/X.pdf')[0].get_text()[:80]))"
   ```

   **Every `New PYQ/*.pdf` scan carries a substantial machine text layer**, not just
   Data Mining. Measured 2026-09-13: WC 22/23 pages, DM4.1BCT 26/28, DSAP 42/47,
   OM 23/27, RF 23/25, 4.1bei_dsap 25/30, rf4.1bei 10/11, wc4.1bei 6/7, AI 17/48.
   Only the two **older** scans have none at all: `Wireless/EX-715_81-70.pdf` (0/15)
   and `DSAP/CT-704_69-81.pdf` (0/22). An earlier version of this rule claimed Data
   Mining was the only one; that was wrong and it cost two whole papers (see below).

   It is sloppy machine OCR (`TRIBHUV.AN LNIVERSITY`, `t6l` for `[6]`, `12+6)` for
   `[2+6]`), but `page.get_text('text', sort=True)` is cheaper than the OCR tool and far
   cheaper than rendering. Its weakest spot is the marks column, so **reconcile every
   paper's marks against the printed Full Marks of 80** — that arithmetic is what makes
   them trustworthy. It recovered all six new Data Mining papers' marks exactly, and it
   is what confirmed both 2082 Baishakh papers.

   **Never infer "blank page" from an empty text layer.** A page returning zero
   characters inside a scan that otherwise has one is usually a *dark* page the
   embedded OCR gave up on, not a blank sheet. `WC.pdf` p2 and `DSAP.pdf` p2 were both
   archived as blank for months; each is a whole **2082 Baishakh** paper, recovered
   2026-09-13. Ink coverage separates the two cases in one line — a real question page
   runs about 1.4 % dark pixels, those two ran 4.8–5.0 %, a truly blank sheet is near 0:

   ```bash
   python -c "import fitz; pm=fitz.open('New PYQ/X.pdf')[1].get_pixmap(dpi=36,colorspace=fitz.csGRAY); print(sum(1 for b in pm.samples if b<128)/len(pm.samples))"
   ```

3. **To transcribe a page that has no text layer and is not yet in an archive, run the OCR
   tool first — do not look at the page image.**

   ```bash
   python tools/ocr_page.py "New PYQ/AI.pdf" 19-26 --out ocr_raw/ai
   ```

   RapidOCR (ONNX, CPU, no system binary) emits reading-order text. One page costs roughly
   700 text tokens instead of ~2,500 image tokens, and it is *more* reliable on the marks
   column than a hurried visual read. Treat the output as a draft, then image-verify only
   the bands it got wrong:

   ```bash
   python tools/ocr_page.py "New PYQ/AI.pdf" 19 --crop 0.30 0.42 --zoom 4.0
   ```

   It is weak on faint scans, on S-parameter subscripts, and on stacked fractions. Those,
   and figures, still need eyes.

4. **Write the OCR archive incrementally, one paper at a time, as you read.** Never hold a
   batch of transcriptions in context "to write at the end". A context compaction or a
   cleared scratchpad destroys unwritten work and forces a full re-read — this has already
   cost one session. The archive file is the deliverable, not a by-product.

5. **Never read a whole source PDF, and never read `BEI IV-I(1).pdf`** (96 pp, no text
   layer, multi-subject bundle, not used by any document). To identify papers cheaply,
   build a header contact sheet — the top ~20 % of six pages stacked into one PNG — rather
   than opening six full pages.

6. **The page index lies.** Confirm every paper from its own printed header, never from its
   position in the file. Real cases in this repo: a page where the 2073 Bhadra Wireless
   paper belonged was a DSP paper; one paper prints `BEI` on what is the BEX sheet;
   O&M tagged 2070 **Ashad** as `70 Ash` (Ashwin) for two years; AI's 2072 Magh names two
   different papers, both printing programme BCT, separated only by course code; Data
   Mining's 2079 Baishakh paper is captured as a phone screenshot whose **PDF-viewer title
   bar reads "2079 Chaitra"** — app chrome is not a header. A page an archive calls
   *blank* is a claim to confirm too, not inherit: `WC.pdf` p2 and `DSAP.pdf` p2 each
   held a whole 2082 Baishakh paper (golden rule 2). When a subject has two scans,
   diff them page by page — each usually holds a paper the other lacks, though AI's new
   scan turned out to be a strict superset. Data Mining is the opposite case: neither of
   its two scans contains the other, so both must stay on disk.

7. **No truncation in a Detailed document.** `grep` for `\dots`, `\ldots`, `\cdots` and a
   literal `...` before shipping; it must return nothing. Data tables get typeset as
   `tabular`/`bmatrix`, not cropped as images. Crop an image only for a true line drawing.

8. **Count questions per paper before calling a subject done.** `check.py` compares each
   paper's question count in the archive against how many times its year code appears in
   the `.tex`. This has caught real omissions four times: DSAP 2067 Mangsir Q8, twelve
   short O&M papers, two whole RF papers (2072 Magh, 2074 Magh) that were in both scans but
   in neither document, and two AI questions (2072 Ashwin Q10, 2071 Magh Q10) that the old
   document had dropped along with two mis-tagged 2070 Magh questions.
   A year code alone is not a key when a subject has more than two course codes: AI needed
   `tools/ai_qcount.py`, which keys on (code, year, month) because `77 Ch` and
   `\textit{77 Ch}` are different papers.

   A Concise document is checked differently, against the Detailed rather than the archive.
   It promises "marks in (); unique values only", so `tools/concise_cov.py` reconciles the
   two both ways per chapter: every `[n]` in a Detailed chapter must appear as `(n)` in the
   matching Concise chapter, and nothing else may. The Concise documents had all drifted;
   Wireless was rebuilt to zero on 2026-09-11, the other five are queued in
   `handoff-current.txt`. The tool cannot see a marks value attached to the wrong bullet
   inside the right chapter, nor a topic dropped while a common marks value survives on a
   neighbouring bullet — both were real in Wireless — so still read bullet against
   subsection by hand.

9. **Bash heredocs on Windows mangle backslashes.** Any file containing LaTeX or a regex
   must be written with the Write tool, never piped through a heredoc. This has silently
   no-op'd edits twice. In Python helpers, build backslashes from `chr(92)`.

10. **Rebuild, verify, then commit sources and PDFs together.** A `.tex` committed without
   its rebuilt `.pdf` leaves the published document stale.

## Build

```bash
cd <Subject> && "../Data Mining/ExamNotes/src/tectonic.exe" -X compile <file>.tex
```

Tectonic resolves the table of contents in one run. Compile from the folder that owns
`images/` so relative paths resolve. `Overfull \hbox` on a few long question lines is
cosmetic; ignore it.

## LaTeX traps that have each cost a build cycle

- `\lb` expands to `\\`, and LaTeX rejects `\\` immediately after `\end{center}`
  ("There's no line here to end"). Centre a figure or formula with
  `\\ \mbox{}\hfill<content>\hfill\mbox{}` instead.
- The same error fires when a `\lb` follows a **blank line**, because the blank line starts
  a fresh paragraph and `\\` then has no line to end. When appending a `\lb` variant to an
  existing question, put it on the line immediately after the previous one — never with a
  blank line between. Worth a scripted check before every build:
  `grep -B1 '\lb' <file>.tex` should never show an empty preceding line.
- A bare `°` in math mode falls back to `cmr12`, which has no such glyph, so **degree signs
  are silently dropped from the PDF**. Use `^\circ`. RF-Microwave was wrong this way for its
  whole history; the other subjects have not been checked.
- `\usepackage{inconsolata}` is not in the Tectonic bundle and is a fatal error.
- The `\bo{}` macro needs its full expl3 form. Do not "simplify" it.

## Conventions

Regular exam = **bold**, Back exam = plain, and a header printing "Regular / Back" in one
box counts as Regular. A second course code is marked `\texttt{}`; **which** code gets the
monospace differs by subject, so each document states its own choice in its Notes block.
Months: Ba, Jth, Asa (Ashad), Shr, Bh, Ash (Ashwin), Ka, Mng, Po, Ma, Ch — **Ash and Asa are
different months.**
