# RF and Microwave Engineering — ExamNotes build progress

EX 716 (BEI, IV/I) / EX 752 (BEX, IV/II), 24 papers 2069–2082 BS.
Sources in `ExamNotes/src/`, PDFs deployed one level up in `ExamNotes/`.
Method: `../HANDOFF-pyq-and-notes-method.md` and the Phase 0–3 workflow.

## Build

```bash
cd RF-Microwave/ExamNotes/src && python build.py ch2 ch2-num
```

`build.py` **skips a missing target silently**, so a bare `python build.py`
looks green while building almost nothing. Always name the target.
Audit pagination with `PYTHONIOENCODING=utf-8 python audit.py`
(the bare form dies on a cp1252 `UnicodeEncodeError`).

## Chapter status

| Ch | Title | Theory | Numerical | Notes |
|----|-------|--------|-----------|-------|
| 1 | Introduction | ✅ 10 pp | — (no numerical content) | built by a lower model; **audit pending** |
| 2 | RF and M/W Transmission Lines | 🔨 in progress | 🔨 24 problems | the Smith-chart chapter |
| 3 | Network Theory and Analysis | ⬜ | ⬜ | S-parameters |
| 4 | Components and Devices | ⬜ | ⬜ | biggest question count (52) |
| 5 | Microwave Generators | ⬜ | — | |
| 6 | RF Design Practices | ⬜ | ⬜ | **heaviest chapter, 22.4 % of marks** |
| 7 | Antennas and Propagation | ⬜ | — | |
| 8 | RF/Microwave Measurements | ⬜ | — | |
| — | Combined masters | ⬜ | ⬜ | `master`, `master-num` |

## Weight of each chapter (measured from the Detailed PYQ, 24 papers)

| Ch | Q | Marks | Avg/paper | Share |
|----|---|-------|-----------|-------|
| 1 | 25 | 184 | 7.7 | 9.7 % |
| 2 | 32 | 297 | 12.4 | 15.6 % |
| 3 | 27 | 193 | 8.0 | 10.1 % |
| 4 | 52 | 317 | 13.2 | 16.7 % |
| 5 | 22 | 166 | 6.9 | 8.7 % |
| 6 | 46 | 426 | 17.8 | 22.4 % |
| 7 | 20 | 138 | 5.8 | 7.3 % |
| 8 | 25 | 181 | 7.5 | 9.5 % |

Total 1902 marks against a theoretical 24 × 80 = 1920, i.e. the PYQ archive
is 99.1 % complete — the tier counts derived from it can be trusted.
Regenerate with `tools/`-style scripts; the counter used lives in the
session scratchpad, keyed on `\section` blocks of the Detailed `.tex`.

## Tools built for this subject

- **`src/rf.py`** — exact transmission-line and stub solver. No chart reading,
  no formula quoted from memory: single stub (shunt and series), double stub,
  microstrip synthesis, WTG readings. `python rf.py` self-tests against the
  four worked problems printed in Er. Gangaju's Chapter-2 deck.
- **`src/smith.py`** — Smith chart renderer that draws the **construction**,
  not just the answer: SWR circle, g = 1 circle, spacing circle, the walk
  toward the generator, the constant-g arc a shunt stub moves along, and the
  stub length stepped off round the rim. `python smith.py` asserts its own
  geometry before rendering.

### Two conventions that were got wrong first time — both now asserted in code

1. **The WTG scale reads 0.000 at `p = -1`, increasing clockwise.** Verified
   against the deck: `z_L = 0.3 + j0.2` reads 0.034λ and `y_L`, half a turn
   away, reads 0.284λ — which is the number the deck prints.
2. **On an admittance chart the terminations swap ends**: `y = 0` (open) sits
   at `p = -1` and `y = ∞` (short) at `p = +1`, the mirror of the impedance
   chart. Getting this backwards silently corrupts every stub length.

The double-stub susceptance is `B = (1 ± √(g(1+t²) − g²t²)) / t` with
`t = tan βd` — note the leading **1**, not `g`. Forbidden region is
`g > 1/sin²(βd)`.

## Source material

Third-party and gitignored — build input only, never publish.

- `Notes/RF Pulchowk/Chapter N/` — **clean text layer, cheap to extract.**
  Gangaju's `Chapter_2 _RF.pdf` (82 pp) is the primary Ch2 theory source and
  carries the exact local method, step numbering and two fully worked
  double-stub problems with published chart readings.
- `Notes/Lectures by KK Sir/` — handwritten scans with garbage machine OCR
  (`"Dou b le St-,.J b Makh i n9"`). **Do not read these as page images**;
  `rf.py` + `smith.py` reproduce the same worked examples exactly.
- `Books/` — Pozar 4e, Liao, Annapurna Das. 144 MB.
- `Notes/SmithChart.pdf` — blank vector chart, 1 p.

## Errors found in the source notes (corrected in ours, marked `[verified/added]`)

- Gangaju deck, Double-Stub Problem 1: prints `l2 = 0.232λ` for `b2 = 3.3`.
  An open stub with `b = 3.3` is `atan(3.3)/2π = 0.203λ`. Digit transposition
  in the source; the deck's own `b2` is right. **We carry 0.204λ.**
- Same deck, Double-Stub Problem 2 step 5 prints `y1=0.55-j-0.11`; the double
  sign is a typo for `0.55 - j0.11`, confirmed by its own step 6 arithmetic.

## Standing traps (see also ../CLAUDE.md)

- `\bo{}` **does not exist in ExamNotes** — it is defined only in the two PYQ
  documents. Use `\textbf{}`. This already broke one ch1 build.
- A bare `°` in math mode is silently dropped from the PDF. Use `^\circ`.
  RF-Microwave was wrong this way for its whole history.
- `\lb` must never follow a blank line, and never directly follow
  `\end{center}`.
- Never write LaTeX or regexes through a bash heredoc on Windows — backslashes
  get mangled. Use the Write tool; in Python build backslashes from `chr(92)`.
- Rebuild, verify, then commit sources **and** PDFs together, one commit per
  chapter as soon as it builds.

## Session log

- **2026-09-09** — Ch1 (Introduction, 10 pp) built and committed.
- **2026-09-10** — Phase-0 re-scope for the remaining 7 chapters. Built and
  verified `rf.py` and `smith.py`. Started Ch2.
  User asked that the numericals show **every Smith-chart construction step**,
  not just the output, and that Ch1 be audited against the workflow spec at
  the end of the session.
