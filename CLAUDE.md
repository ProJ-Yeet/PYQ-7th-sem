# PYQ Sorted Chapterwise — project instructions

Chapter-sorted past-exam-question compilations for IOE (Tribhuvan University) 7th semester,
plus two sets of full exam notes. LaTeX sources built with Tectonic; inputs are scanned
question papers with no text layer.

**The full method lives in `HANDOFF-pyq-and-notes-method.md`.** Read it before writing
anything. `handoff-current.txt` holds the running status board and session log.

## Golden rules

These are the measured cost drivers in this repo (223 MB tracked: 165 MB of PDFs,
57 MB of PNGs, and only 1.2 MB of `.tex`). Breaking one of them is what makes a session
expensive.

1. **Never read a source scan as a page image when `<Subject>/ocr/*_OCR.md` already covers
   it.** The archives are complete and verbatim for O&M (29 papers), RF-Microwave (24),
   DSAP (44), Wireless (22), AI (17, CT653/CT710 only) and Data Mining (17). Re-render a
   page only to crop a figure, or when the archive itself flags a line as uncertain.

2. **To transcribe a page that is not yet in an archive, run the OCR tool first — do not
   look at the page image.**

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

3. **Write the OCR archive incrementally, one paper at a time, as you read.** Never hold a
   batch of transcriptions in context "to write at the end". A context compaction or a
   cleared scratchpad destroys unwritten work and forces a full re-read — this has already
   cost one session. The archive file is the deliverable, not a by-product.

4. **Never read a whole source PDF, and never read `BEI IV-I(1).pdf`** (96 pp, no text
   layer, multi-subject bundle, not used by any document). To identify papers cheaply,
   build a header contact sheet — the top ~20 % of six pages stacked into one PNG — rather
   than opening six full pages.

5. **The page index lies.** Confirm every paper from its own printed header, never from its
   position in the file. Real cases in this repo: a page where the 2073 Bhadra Wireless
   paper belonged was a DSP paper; one paper prints `BEI` on what is the BEX sheet;
   O&M tagged 2070 **Ashad** as `70 Ash` (Ashwin) for two years. When a subject has two
   scans, diff them page by page — each usually holds a paper the other lacks.

6. **No truncation in a Detailed document.** `grep` for `\dots`, `\ldots`, `\cdots` and a
   literal `...` before shipping; it must return nothing. Data tables get typeset as
   `tabular`/`bmatrix`, not cropped as images. Crop an image only for a true line drawing.

7. **Count questions per paper before calling a subject done.** `check.py` compares each
   paper's question count in the archive against how many times its year code appears in
   the `.tex`. This has caught real omissions three times: DSAP 2067 Mangsir Q8, twelve
   short O&M papers, and two whole RF papers (2072 Magh, 2074 Magh) that were in both scans
   but in neither document.

8. **Bash heredocs on Windows mangle backslashes.** Any file containing LaTeX or a regex
   must be written with the Write tool, never piped through a heredoc. This has silently
   no-op'd edits twice. In Python helpers, build backslashes from `chr(92)`.

9. **Rebuild, verify, then commit sources and PDFs together.** A `.tex` committed without
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
