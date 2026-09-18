# Digital Signal Analysis and Processing — Anki deck

`DSAP_ExamNotes.apkg` — **135 cards**, built straight from the LaTeX sources of
`DSAP/ExamNotes/`, so the deck says exactly what the notes say. Import it into
Anki (File → Import, or double-click). Re-importing a newer build **updates** the
existing cards instead of duplicating them, and your scheduling is kept.

## What a card is

One card per exam question. Front is the question as the notes head it, with its
marks chips; back is that question's answer, figures, tables and all.

| Source in `ExamNotes/src` | Cards |
|---|---|
| `\Q{...}` and `\qq{...}` in `ch<N>.tex` | the exam question as the notes head it — 55 |
| `\T{...}` / `\creamq{...}` in `ch<N>-num.tex` | one per numerical, fronted by the `asked` statement **verbatim as the paper prints it** — 66 |
| the material above the first topic band | one "how is this chapter examined" card per chapter — 14 |

**Question → Answer only.** The note type has a single card template, so Anki
never generates a reverse card.

## Coverage, and why the count is what it is

Seven chapters, **CT 704 only**. Chapter 8 of the PYQ documents is the `EX753`
(BEX) material that lies outside the CT 704 syllabus; there is no chapter 8 in
the notes and none in this deck.

The deck is smaller than Wireless's 177 for a real reason, not a gap: DSAP asks
the same six procedures 30 to 40 times each (DIT/DIF FFT in 43 questions, lattice
in 38, convolution in 34, inverse Z in 32, bilinear Butterworth in 32), and the
notes deliberately group those into **one worked solution plus a table of the
sibling papers' answers**. One card per method is the point. The tables ride
along on the back of that method's card, so every paper's numbers are still
there to check against.

## Decks and tags

Decks follow the syllabus, `DSAP::Ch 6 - IIR Filter Design` and so on, with
numericals in a `::Numericals` subdeck so they can be studied, or postponed, on
their own.

Tags: `ch1`…`ch7`, `theory` / `numerical` / `opener`, `tier::TOP` `tier::HOT`
`tier::PIN` (the frequency tier the notes assign, counted over all **45** papers),
and one `yr::81-Bh`-style tag per paper the question comes from. So
`tag:tier::TOP -tag:numerical` is the theory asked most often, and
`tag:yr::82-Bh` is last year's paper.

Note on the year tags: 45 papers carry only 44 distinct year codes, because
`69 Bh` names one CT 704 paper and one EX 753 paper. A `yr::69-Bh` search
therefore returns both.

## Rebuilding

```bash
python tools/anki_from_notes.py DSAP
```

Reads `ExamNotes/src/ch*.tex` directly — nothing is transcribed by hand, so the
deck cannot drift from the notes. It writes the `.apkg`, a `.tsv` fallback for a
manual import, and `_media/` (downscaled copies of the figures, git-ignored; they
are packed into the `.apkg`). `--report` parses and prints statistics without
writing anything, `--dump preview.html` writes a browser preview of every card.

**Read the `UNHANDLED MACROS` line if it appears.** It means a chapter used a
macro the converter does not know, and the content behind it would be dropped
silently otherwise. DSAP triggered exactly one: `\newline`, the in-table line
break, used 169 times because `\lb` expands to `\\` which inside a `tabular` ends
the row instead. The converter now maps it to `<br>`.

Math is MathJax, which Anki renders natively. Figures are the same ones the PDFs
use, never redrawn.
