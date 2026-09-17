# RF and Microwave Engineering — ExamNotes build progress

EX 716 (BEI, IV/I) / EX 752 (BEX, IV/II), 24 papers 2069–2082 BS.
Sources in `ExamNotes/src/`, PDFs deployed one level up in `ExamNotes/`.
Method: `../HANDOFF-pyq-and-notes-method.md` and the Phase 0–3 workflow.

## Build

```bash
cd RF-Microwave/ExamNotes/src && python build.py ch3 ch3-num
```

`build.py` **skips a missing target silently**, so a bare `python build.py`
looks green while building almost nothing. Always name the target.
Audit pagination with `PYTHONIOENCODING=utf-8 python audit.py`
(the bare form dies on a cp1252 `UnicodeEncodeError`).

## Chapter status

| Ch | Title | Theory | Numerical | Notes |
|----|-------|--------|-----------|-------|
| 1 | Introduction | ✅ 10 pp | — none (stated in §1.7) | audited and repaired 2026-09-10 |
| 2 | RF and M/W Transmission Lines | ✅ 12 pp | ✅ 42 pp, 24 problems | the Smith-chart chapter |
| 3 | Network Theory and Analysis | ✅ 13 pp | ✅ 18 pp, 12 problems | the magic-tee chapter |
| 4 | Components and Devices | ✅ 16 pp | ✅ 8 pp, 8 problems | the waveguide chapter; `wg.py` |
| 5 | Microwave Generators | ✅ 10 pp | — none (stated in §5.10) | tubes; `tubes.py` |
| 6 | RF Design Practices | ✅ 11 pp | ✅ 7 pp, 10 problems | heaviest; `amp.py`, `filt.py` |
| 7 | Antennas and Propagation | ✅ 11 pp | ✅ 5 pp, 2 problems | radiation hazards; `ant.py` |
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
| 7 | 20 | 138 → **162** | 6.8 | 8.4 % of 1920 (recounted 2026-09-17 after the PYQ fixes) |
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
- **`src/check.py`** — tier-chip auditor. Compares every `\tS` / `\tF` / `\tP{n}` chip
  to its own `\yr{}` list *and* to the Detailed PYQ, so a chapter cannot cite a
  paper that asks no question in it. Found 8 defects in ch1, 0 in ch2.
- **`src/verify.py`** — walks each published stub design forward through the line
  equations and asserts `y_in = 1+j0`, re-deriving every susceptance from the
  **published length** so a wrong length cannot hide behind a right `b`. 24/24 pass.
- **`src/sparam.py`** — Chapter-3 S-parameter solver. Re-derives the E-plane tee,
  H-plane tee, magic tee, circulator and directional coupler **from their stated
  properties** and then asserts reciprocity / unitary / matching on each; brute-forces
  the 3-port impossibility theorem over the whole reciprocal-matched family;
  reduces an n-port by terminating ports (`terminate()`, used for the shorted magic
  tee); and asserts every published number for 2079 Bhadra and 2082 Bhadra.
  `python sparam.py` runs the lot.
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

- **`src/ant.py`** — Chapter-7 exit test. Radiation-zone boundaries for every PYQ antenna
  and both deck examples, **with a validity check** (`D > λ`; small antennas use `λ/2π` and
  `2λ`), FCC OET-65 and ICNIRP-1998 limits as functions of f, compliance distance, SAR,
  photon energy, FSPL, radio horizon, Fresnel radius, dish gain. Two of my own hand-estimates
  (Fresnel radius, dish gain) were wrong and its asserts caught both.
- **`src/check.py` parser fix (2026-09-17)**: it read only the *last* `(years)` group on a
  Detailed line, so `[8] (69 Bh) [5] (70 Bh, 73 Ma)` hid 69 Bh. It now reads every group
  after `\hfill`. All seven chapters still clean.

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
- RF Pulchowk Ch3 deck p32 prints `Insertion loss (dB) = 10 log |a1|²/|b1|²`.
  `b1` is the wave coming **back out of port 1**, so that is the return loss.
  Insertion loss compares `|a1|²` with `|b2|²`, i.e. `20 log 1/|S21|`, which is what
  the deck's own next line prints. Corrected in §3.4, marked `[verified/added]`.

## Standing traps (see also ../CLAUDE.md)

- `\bo{}` **does not exist in ExamNotes** — it is defined only in the two PYQ
  documents. Use `\textbf{}`. This already broke one ch1 build.
- A bare `°` in math mode is silently dropped from the PDF. Use `^\circ`.
  RF-Microwave was wrong this way for its whole history.
- `\lb` must never follow a blank line, and never directly follow
  `\end{center}`.
- Never write LaTeX or regexes through a bash heredoc on Windows — backslashes
  get mangled. Use the Write tool; in Python build backslashes from `chr(92)`.
  **This bit three times in the 2026-09-10 session alone.** The specific failure
  is silent: a Python string `"\textbf"` is a literal TAB plus `extbf`, and
  `"\t"`, `"\b"`, `"\f"`, `"\v"`, `"\a"`, `"\n"`, `"\r"` all do this. Unknown
  escapes like `"\O"` survive but only warn. Guard with
  `python -W error::SyntaxWarning -c "import <mod>"`, and grep the generated
  output for raw control characters before building.
- A companion trap: a blanket "fix escaping" regex must **skip raw strings**.
  Doubling the backslash inside `r"\textbf{79 Ch}"` turns it into `\\textbf`,
  which LaTeX renders as a line break followed by the literal word `textbf`.
- Rebuild, verify, then commit sources **and** PDFs together, one commit per
  chapter as soon as it builds.
- **Em dashes are banned by the house style** and Ch3 is written without them.
  Ch1, Ch2 and Ch2-num still carry about 350 of them, mostly as `Problem N ---`
  and `Step N ---` separators; a sweep to `:` is pending the user's call.

## Session log

- **2026-09-09** — Ch1 (Introduction, 10 pp) built and committed.
- **2026-09-10** — Phase-0 re-scope for the remaining 7 chapters. Built and
  verified `rf.py`, `smith.py`, `verify.py`, `check.py`. **Ch2 shipped**: theory
  12 pp + numerical companion 42 pp with all 24 PYQ constructions worked step by
  step (the user asked for every chart step, not just the output). **Ch1 audited
  and repaired**: 3 ghost paper citations removed, 4 tier counts resynced, one
  tier reclassified, §1.7 PYQ-mapping band added, 3 content errors corrected.
- **2026-09-11** — **Ch3 shipped**: theory 13 pp (nine bands) + numerical companion
  18 pp (12 problems, ~100 marks). `sparam.py` added. `check.py` clean, `audit.py`
  0 stranded, mean fill 80 % / 87 %. Findings worth carrying forward:
  - **Every one of the five "identify the passive device from this S-matrix"
    questions is a magic tee** (78 Ch, 81 Bh, 74 Bh, 75 Bh; 82 Bh prints amplifier
    sets instead). The papers permute which port number is the E-arm, so the
    identification rule is **read the sign pattern down the column, not the port
    number**.
  - The Detailed PYQ compresses 82 Bh Q3 to "three-port network model". The paper
    actually asks for the **S-matrix of a magic tee with both E- and H-arms
    shorted**. No source note carries it; derived here and asserted:
    `[S] = [[-1,0],[0,-1]]`, total reflection with a 180° flip and the collinear
    isolation intact.
  - `Notes/RF Pulchowk/Chapter 4/S-parameters.pdf` (8 pp, handwritten OneNote ink,
    no text layer) holds the **local** E-plane, H-plane and magic-tee derivations
    step by step. It is the authoritative source for Ch3 §3.5-3.6 and worth the
    8 page renders; the Ch3 deck itself has its equations as images.
  - **`\lead{}` has no orphan protection** — unlike `\T` / `\Q` / `\creamq` it
    carries no `\Needspace` and no `\qhold`, so a bold step heading can strand at
    the foot of a page. `audit.py` does not catch it (it only tests `\T` bands).
    Ch3 needed 8 local `\par\penalty0\Needspace{N\baselineskip}` guards, re-run to
    convergence. **Ch1 p7 and Ch2-num pp. 5, 8, 38 still carry the same defect.**
  Next: Ch4 (Components and Devices, 317 marks, 52 questions, the biggest question
  count) — note Ch3 §3.6 already catalogues the tee / coupler / circulator
  S-matrices, so Ch4 should cover the physical construction and cross-reference.
- **2026-09-17** — Ch4 started. **`src/wg.py` added** (runs in ~7 s): rectangular TE/TM
  components checked symbolically against both curl equations and all four walls;
  circular TE/TM checked numerically in cylindrical coordinates plus `E_phi(a)=0`;
  mode-existence proofs enumerated; every waveguide numerical; rectangular cavity mode
  order; two magic tees joined E-to-E (77 Ch) and H-to-H (78 Ch) by real port
  connection; hybrid tee with matched terminations (82 Ba). **Mutation-tested**: a
  flipped sign in any field component fails the curl check on its own.
  Sources for Ch4: `Notes/RF Pulchowk/all/Chapter_4.pptx` (Gangaju, 99 slides, the
  spine; slides exported to PNG with PowerPoint COM, waveguide equations are images),
  `Chapter 4/Waveguide.pdf` (13 pp OneNote ink, the only circular-guide derivation),
  `Chapter 4/Chapter_4_Part_B.pdf` (44 pp, clean text: microwave transistor, varactor,
  Schottky, Gunn, IMPATT/TRAPATT/BARITT, MMIC).
  Errors found in the sources:
  - Deck slide 18, TE boundary condition (iv) prints `k_y = nπ/a`; it is `nπ/b`.
  - Waveguide.pdf p11, TM circular: prints `E_phi = +jβn/(k_c²ρ)(A cos nφ − B sin nφ)J_n`.
    The sign is **minus**; `wg.py` fails the curl equation with the plus sign.
  - Deck slide 25 prints TE10 of WR430 as 1.372 GHz; exact with c = 3e8 is 1.373.
  Paper defect: **81 Bh Q3a asks to show TE10 is dominant "when b > a"**. With b > a the
  dominant mode is TE01 (cut-off c/2b < c/2a). TE10 is dominant when a > b. Answer the
  intended physics and say so.
  **Ch4 shipped** 2026-09-17: theory 16 pp (4.1-4.11) + companion 8 pp (8 problems,
  46 marks). check.py clean, audit.py 0 stranded, no overfull or too-tall boxes.
  `figs_ch4.py` extracts the deck's original image blobs with python-pptx; a `MASKS`
  table whites out stray slide text left inside a crop box.
  Next: Ch5 (Microwave Generators, 22 questions, 166 marks), no numerical companion.
- **2026-09-17** — **Ch5 shipped**: theory 10 pp (5.1-5.10), no numerical PYQ in 24 papers.
  `src/tubes.py` checks the chapter's quantitative claims by simulating electrons:
  ballistic bunching gives 2 J1(X) peaking at X = 1.841 (58 % efficiency); reflex return
  power peaks at 1.750 cycles; trajectory bisection reproduces the Hull cut-off exactly;
  helix slowing factor and synchronous beam voltage; Friis. `figs_ch5.py` extracts 15
  figures (Karkee deck + PDF export, whose pages carry a full-page background image first,
  so PDF figure indices are raw image indices; plus two 2078 student decks).
  Found and fixed in the PYQ documents first (commit a007df2): 71 Bh BWO short note
  missing; 73 Ma / 73 Bh riders swapped; 70 Ma wrongly under bunching.
  Source errors: PDF p23 "all kinetic energy converted"; PDF p38 TWT beam "at the velocity
  of light"; reflex 22.78 % is X' rounded (exact first zero of J0 gives 22.7 %); student
  BWO slides describe klystron cavities. LNA (73 Bh) has no source note: written
  [verified/added].
  Next: Ch6 (RF Design Practices, 46 questions, 426 marks, heaviest; has a numerical companion).
- **2026-09-17** — **Ch6 shipped**: theory 11 pp (6.1-6.7) + companion 7 pp (10 problems:
  all 13 amplifier S-parameter sets in 22 papers, and the 82 Bh fifth-order ladder).
  `src/amp.py`: Delta, K, mu, stability circles (sampled: |Gamma_in| = 1 on them),
  simultaneous conjugate match (checked = MAG, Gamma_S = Gamma_in*), unilateral gain,
  M bounds, gain circles, stub+line matching networks walked forward; reproduces the deck's
  800 MHz and 8 GHz examples. `src/filt.py`: Butterworth/Chebyshev g-values (= Pozar
  tables), order selection, scaling + LP->HP/BP transforms checked at -3 dB by ABCD,
  stepped-impedance table (= deck example 8.6), and to-scale microstrip layout drawings
  (pi, double-pi, double-pad T, shunt-arm stubs, HPF gaps + shorted stubs, gap-coupled BPF).
  Only three sets are not unconditionally stable: 0.894/-60.6 (72 Ash, 70 Ma, 80 Ba, 79 Bh),
  76 Bh, 73 Ma; bilateral max gain does not exist there (MSG quoted).
  PYQ documents fixed first (commit 4ec0754): 71 Ma set/marks, 70 Ma and 80 Ba asks,
  75 Bh Smith-chart stability and 72 Ma mixer note were missing.
  Deck errors: slide 51 |Delta| 0.168 / K 3.53 (exact 0.173 / 3.445); slide 52 M = 0.04
  (exact 0.034); slide 66 Gunn R_L = 60 ohm breaks its own |R_out| >= 1.2 R_L rule;
  example 8.6 N = 6 where N = 5 already meets 20 dB. Mixer has no deck source: added.
  Next: Ch7 (Antennas and Propagation) and Ch8 (Measurements), then the masters.
- **2026-09-17** — **Ch7 shipped**: theory 11 pp (7.1-7.8) + companion 5 pp (2 problems).
  23 of 24 papers ask it (only 72 Ash does not); nearly all marks are radiation hazards,
  zones, SAR, standards and practices; antenna types and propagation are unexamined and
  written as syllabus-only bands. `src/ant.py`, `src/figs_ch7.py` (10 figures; the PDF's zone
  diagram is inverted from white-on-black).
  PYQ documents fixed first (commits 118e902, 2137554): the hazard short notes were tagged
  71 Ma and 72 Ash, which ask none; they are 70 Bh, 71 Bh and 73 Ma (73 Ma missing); 70 Ma's
  note is [5] (printed [2+8] is a 2x5 misprint, 80-mark total confirms). Bolding made
  consistent: 73 Bh plain in 4 places, `\bo{70 Bh, 70 Ma}` bolded a Back paper, 69 Bh and 71 Bh
  plain despite "Regular / Back" headers. **Ch1-Ch6 ExamNotes still tag 69 Bh / 71 Bh plain.**
  Source errors: SAR density printed kg/m² (kg/m³); PDF p17 "IRPA" table is the 50 Hz
  power-line limit; deck's 150 MHz zone example has D < λ so its boundaries are invalid (same
  trap as 82 Ba's quarter-wave antennas); student decks: cancer "known" (IARC 2B), non-thermal
  "several times more harmful", "threshold SAR 0.4" (limit 0.4, threshold 4), microstrip "used
  at low frequency", Yagi pictured as MIMO. Girish Kumar "minutes per day" slides left out.
  Next: Ch8 (Measurements), then the masters.
