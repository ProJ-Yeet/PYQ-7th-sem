# Wireless Communication — Anki deck

`Wireless_ExamNotes.apkg` — **177 cards**, built straight from the LaTeX sources of
`Wireless/ExamNotes/`, so the deck says exactly what the notes say. Import it into
Anki (File → Import, or double-click). Re-importing a newer build **updates** the
existing cards instead of duplicating them, and your scheduling is kept.

## What a card is

One card per exam question. Front is the question as the notes head it, with its
marks chips; back is that question's answer, figures, tables and all.

| Source in `ExamNotes/src` | Cards |
|---|---|
| `\Q{...}` in `ch<N>.tex` | the main exam question — 83 |
| `\qq{...}` in `ch<N>.tex` | a sub-question inside one — 20 |
| `\T{Problem ...}` / `\lead{n.m ...}` in `ch<N>-num.tex` | one per numerical, fronted by the `asked` statement **verbatim as the paper prints it** — 61 |
| the material above the first topic band | one "how is this chapter examined" card per chapter — 13 |

A `\Q` that has `\qq` children keeps their content in its own answer, because that
is what the full-mark answer has to say; the children also stand as their own
cards, so those topics come up twice at different grain. Suspend the `qq` ones if
you would rather not see them.

**Question → Answer only.** The note type has a single card template, so Anki
never generates a reverse card.

## Decks and tags

Decks follow the syllabus: `Wireless::03 Radio Wave Propagation…`, with numericals
in a `::Numericals` subdeck so they can be studied (or postponed) on their own.

Tags: `ch1`…`ch8`, `theory` / `numerical` / `opener`, `tier::TOP` `tier::HOT`
`tier::PIN` (the frequency tier the notes assign, counted over all 23 papers), and
one `yr::81-Bh`-style tag per paper the question comes from. So
`tag:tier::TOP -tag:numerical` is the theory that is asked most often, and
`tag:yr::82-Ba` is last year's paper.

## Rebuilding

```bash
python tools/anki_from_notes.py Wireless
```

Reads `ExamNotes/src/ch*.tex` directly — nothing is transcribed by hand, so the deck
cannot drift from the notes. It writes the `.apkg`, a `.tsv` fallback for a manual
import, and `_media/` (downscaled copies of the figures, git-ignored; they are packed
into the `.apkg`). `--report` parses and prints statistics without writing anything,
`--dump preview.html` writes a browser preview of every card, and `--maxwidth`
controls the figure size (default 900 px, which is most of the 15 MB).

Math is MathJax, which Anki renders natively. Figures are the same ones the PDFs use,
never redrawn.
