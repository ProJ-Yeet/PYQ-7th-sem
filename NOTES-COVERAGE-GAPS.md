# Exam-notes coverage audit — flagged gaps

Audited 2026-09-08. Scope: every question in the OCR archives for the three subjects that
have exam notes (Data Mining, Wireless, AI), checked against what the notes actually answer.

## Status — Data Mining CLOSED 2026-09-08

Everything below under sections A and B has been written, built and verified.

- **A1** 100 % / 99 % confidence — answered in `ch4.tex` §4.1 as its own `\creamq` block;
  the false "All Ch 4 PYQs covered" claim is gone.
- **A2** rules at any confidence threshold — the general principle is in §4.2 rule
  generation, the table-specific answer is Problem 1.10 of the Ch 4 companion.
- **B1 / B2** all five missing or thin theory topics written: the likelihood (mixture-model)
  approach to anomaly detection, decision tree vs rule-based classifier, the
  holdout / random-subsampling / k-fold / bootstrap merits-and-demerits table, the
  distance-metric-in-an-instance-based-classifier bridge, and the
  "data mining turns data into knowledge" justification.
- **B3** all 14 new numericals solved, including the three firsts: a real DBSCAN PYQ, a
  Manhattan K-means, and an SSE computation. The stale "No PYQ sets a DBSCAN numerical"
  claim in `ch5-num.tex` is corrected.
- **Six-paper merge** finished: `\yr` citations, tier chips recounted out of 23 (was 17),
  chapter intro counts, and a "Papers added by the 2026-09 merge" block in every chapter's
  PYQ Mapping index.
- **Also fixed while in there**: 2076 Ch Q8(b), the edge-growing candidate-subgraph question,
  which the Ch 4 mapping claimed was in the companion but which was never written;
  Problem 1.1 never computed the confidence half; Problem 3.1's FP-Growth conditional pattern
  base for Y truncated two prefix paths; Problem 1.2's Income-level information gain was
  printed as 0.971 and is 0.695.
- `verify.py` now runs **242 checks, 0 failures** (was 189).

**AI CLOSED 2026-09-17.** The checklist has now been run over ch6, ch7 and both combined
masters, and AI is clean. Four passes, not three — the per-chapter and per-(paper, marks)
reconciliations below were added because the citation-density ratio alone cannot see a
single dropped question inside an otherwise well-cited paper.

- **Pass 2, citation density.** All 41 papers cited, lowest ratio 1.70 (2069 Poush). The
  three papers flagged as thin in section D — 2071 Magh, 2069 Poush, 2074 Magh — were thin
  only because ch6 and ch7 did not exist yet. They now sit at 2.70, 1.70 and 2.10.
- **Per-chapter.** Every paper the Detailed document files under chapter N is cited by
  `ch<N>.tex` or `ch<N>-num.tex`. **0 gaps in all seven chapters.**
- **Per-(paper, marks).** 23 pairs the Detailed has and the notes' `\yr` bands do not.
  All 23 triaged by hand to false positives of the matcher: those papers are cited in a
  plain `{\color{sub}\footnotesize ...}` footnote rather than in a `\yr{}`+`\m{}` band, so
  the marks value cannot be paired mechanically. Ch2's nine are the whole multi-answer
  crypt-arithmetic table in `ch2-num.tex`; Ch3's seven are theory asks answered in
  `ch3.tex` (§3.1 evaluation criteria, §3.5 hill climbing, blind-search comparison).
- **Pass 3, theory riders on numericals.** Nothing unanswered. The rider that looked most
  exposed, 2075 Bhadra's *"What do you understand by swarm intelligence?"* [2], is
  researched and written in `ch6.tex` §6.9 with a note that no lecture deck in the subject
  contains the word. Boltzmann, Sugeno, ANN non-linearity, "differs from classical binary
  logic" and the perceptron/NLP definitional riders all land in their chapters too.

AI layout is 0 stranded, 75 short pages. Wireless needs nothing.

## Method (reproducible)

Three independent passes, scripts in the session scratchpad:

1. **Indexed-but-unanswered.** Each Data Mining chapter carries a `\T{x.y PYQ Mapping}`
   index. Split the `.tex` at that band, then check every mapping `\item` against the body
   above it. A question listed in the index with no matching body section is a gap.
2. **Citation density.** For every paper in the archive, count its questions, then count how
   many times the notes cite that paper's year-tag. Ratio near zero = paper never audited in.
3. **Theory riders on numericals.** Extract every `\begin{asked}{...}` block from the
   numerical companions, split the statement into sentences, keep the sentences that ask for
   theory rather than computation, and check whether an answer or a chapter cross-reference
   follows.

Wireless and AI chapters have **no PYQ-mapping index**, so pass 1 does not apply to them;
passes 2 and 3 do.

Two more reconciliations were added 2026-09-17, because a density ratio above 1.0 proves
only that a paper was read, not that each of its questions was answered:

4. **Per-chapter.** Split the Detailed document at `\section`, collect the year tags in
   each chapter, and check that `ch<N>.tex` or `ch<N>-num.tex` cites every one of them. A
   (chapter, paper) pair the Detailed has and the notes do not is a question the notes may
   never answer. Key on (course code, year, month) wherever a subject has more than two
   course codes — for AI, plain = CT653, `\texttt` = CT710, `\textit` = CT78506.
5. **Per-(paper, marks).** The same, one level finer: pair each year tag with the marks
   value next to it, using `ch_tally.py`'s windowing rule (at every marks bracket, read the
   year codes up to the next bracket) on the Detailed side, and the `\m{}` inside each
   `\yr{}` band on the notes side. **Expect false positives and triage them by hand** — a
   paper cited in a plain footnote rather than a `\yr{}`+`\m{}` band cannot be paired
   mechanically, and on AI every one of the 23 hits was of that kind.

---

## Headline

| Subject | Papers in archive | Papers cited in notes | Verdict |
|---|---|---|---|
| Wireless | 22 | 22 (min ratio 0.94) | clean |
| AI | 41 | 41 (min ratio 1.70) | clean, all 7 chapters |
| **Data Mining** | **23** | **17** | **six papers never audited in** |

The reported miss is real, and it is not isolated. Data Mining is the weak set for two
separate reasons.

---

## A. Data Mining — indexed but never answered

**A1. The reported question.** `Data Mining/ExamNotes/src/ch4.tex:331`

> \item \tP{1} Why 100\% confidence is uninteresting but 99\% is. \hfill \m{4} \yr{80 Ba}

2080 Baishakh Q5 [4+5]. The 5-mark Apriori half is solved in the Ch 4 companion
(`ch4-num.tex`, "Candidate + large itemsets, min support 2"). The **4-mark theory half is
answered nowhere.** The only mention of it in the whole notes set is that one index line.
Section 4.1's "Pattern evaluation: why support–confidence is not enough" covers the
lift / null-invariant material but never touches the 100 % vs 99 % argument.

The answer wants: a 100 %-confidence rule is a functional dependency / tautology already
implied by the data definition, so it carries no new information and is often trivially
redundant (X → X, or an attribute implying its own superset); 99 % is interesting precisely
because the 1 % of exceptions is where the anomaly, the fraud case or the data-entry error
lives.

`ch4.tex` also asserts "All Ch 4 PYQs covered" in its Coverage-check block. That line is
false and needs correcting with the fix.

**A2. Same class, different paper — also missing.** 2079 Baishakh Q5 (b) [3]

> Is it possible to generate any rules out of the frequent items, considering any value of
> confidence threshold?

Exactly the same kind of exception-case rider, attached to an Apriori numerical. Not in the
notes at all — this paper is in group B below. The answer turns on the frequent itemsets
that particular table produces: if no frequent itemset of size ≥ 2 survives min_sup, then no
rule exists at *any* confidence threshold, because rules need a 2-itemset to split.

---

## B. Data Mining — six papers never merged into the notes

The notes were built 2026-08-26. `New PYQ/DM4.1BCT.pdf` was merged on 2026-09-03 and added
six papers. **The notes were never re-audited afterwards.** Zero citations to any of them in
any `.tex`:

| Paper | Questions / sub-parts | Citations in notes |
|---|---|---|
| 2082 Bhadra | 11 | 0 |
| 2081 Bhadra | 13 | 0 |
| 2079 Baishakh | 19 | 0 |
| 2073 Chaitra | 12 | 0 |
| 2070 Ashad | 11 | 0 |
| 2069 Chaitra | 9 | 0 |
| **total** | **75** | **0** |

Most of the 75 are standard asks the body already answers and need only a `\yr` citation and
a PYQ-mapping line. The ones below need actual new content.

### B1. Theory topics with no coverage at all

| Paper | Q | Marks | Ask | State |
|---|---|---|---|---|
| 2070 Ashad | 8 | 8 | "Explain **likelihood approach** for anomaly detection" | zero hits for "likelihood" in `ch6.tex` and `ch6-num.tex`. Ch 6 covers statistical (parametric, Grubbs, non-parametric, convex hull), distance, density (LOF), clustering — but not the likelihood / Arning formulation |
| 2079 Baishakh | 5b | 3 | rules at any confidence threshold (see A2) | absent |
| 2069 Chaitra | 2 | 8 | "How is decision tree classifier **different than** rule based classifier?" | §3.2 and §3.3 each stand alone; §3.3 has "rule extraction from a decision tree" but no side-by-side comparison |

### B2. Theory topics present but too thin for the marks

| Paper | Q | Marks | Ask | State |
|---|---|---|---|---|
| 2079 Baishakh | 4 | 8 | holdout, random sampling, k-fold, bootstrap — "working mechanism **as well as merits and demerits**" | `ch3.tex:576-591` gives each mechanism in one line; merits are partial, demerits mostly absent. 8 marks needs a proper table |
| 2070 Ashad | 3 | 10 | properties of a distance metric **+ how the metric is used in an instance-based classifier** | properties are in §2.4, KNN in §3.4; the bridge between them is never stated |
| 2081 Bhadra | 1 | 6 | "Data mining turns a large collection of data into knowledge." Justify | Ch 1 answers the neighbouring "data rich but information poor" quote; this prompt needs its own framing |

### B3. New numerical instances absent from the companion (14)

| Paper | Q | Method | Note |
|---|---|---|---|
| 2082 Bhadra | 3 | ID3 decision tree | new dataset |
| 2082 Bhadra | 4 | Apriori, min sup 60 %, conf 80 % | new table |
| 2082 Bhadra | 5 | **DBSCAN**, ε = 2, MinPts = 2, 8 points | see below |
| 2082 Bhadra | 6 | K-means, 2 clusters | new dataset |
| 2081 Bhadra | 5 | ID3 root node only | new dataset |
| 2081 Bhadra | 7 | Apriori, conf 65 %, min sup 50 % | new table |
| 2081 Bhadra | 8 | K-means, given initial centroid, k = 2 | + "problems and ways to solve" rider |
| 2079 Baishakh | 2 | binning (depth 3) + min-max + z-score + decimal scaling | companion has binning at depth 4 and the normalisations separately; this is one combined 4-part question |
| 2079 Baishakh | 5a | Apriori, min_sup 20 % | the 7-row A1–A9 table |
| 2079 Baishakh | 6 | confusion matrix, 6 metrics | new matrix |
| 2079 Baishakh | 8 | K-means with **Manhattan** distance, 3 centres, 3 iterations | zero hits for "manhattan" in `ch5-num.tex` — every worked K-means is Euclidean |
| 2073 Chaitra | 4 | TPR, FPR, accuracy from confusion matrix | new matrix (both axes mislabelled "Predicted" on the paper) |
| 2073 Chaitra | 5 | Apriori, 50 % / 50 % | new table |
| 2073 Chaitra | 7 | K-means on 1-D points + **calculate SSE** | zero hits for "SSE" in `ch5-num.tex`; §5.5 gives the formula but it is never computed |

**Stale claim to fix.** `ch5-num.tex:450` reads:

> No PYQ sets a DBSCAN numerical, but the algorithm is asked in 8 papers and a worked
> classification makes the definitions concrete.

That was true of the 17 old papers. 2082 Bhadra Q5 now sets one, with real coordinates. The
invented practice problem should be replaced by (or demoted beneath) the real PYQ.

---

## C. Wireless — clean

22 of 22 papers cited, lowest density ratio 0.94 (2071 Bhadra). Both exception-case questions
in the archive are handled:

- 2074 Magh Q8 [6+2] "Show that TDMA frame efficiency **cannot reach 100 %** in GSM" —
  answered as its own worked item, `ch7-num.tex:252`.
- 2081 Bhadra "Being a cellular planning engineer, which option do you think is best and
  why?" — answered, with an explicit note that the prose half is what turns it into a
  full-mark answer.

Theory riders on numericals are either answered in the chapter or carry a cross-reference
("The first two parts are theory, answered in chapter §7.1 and §7.6").

## D. AI — clean (all seven chapters, re-audited 2026-09-17)

> The section below was written 2026-09-08, when only chapters 1–5 existed. Its verdict
> still holds and now covers ch6 and ch7 as well; see the **AI CLOSED** block at the top
> for the four passes and their numbers. The instruction that used to close this section,
> *"Re-audit AI chapters 6 and 7 against this same checklist once they are written"*, is
> discharged.


Chapters 1–5 of 7 are written; Ch 6 (Machine Learning) and Ch 7 (NLP / expert systems) are
not. Every low-density paper is explained by those two unwritten chapters, not by an
omission — 2071 Magh, 2069 Poush and 2074 Magh are thin only in their GA / NN / NLP /
expert-system / machine-vision questions.

The exception-case riders inside written chapters are handled well, including two that are
close cousins of the Data Mining miss:

- 2076 Bhadra "AB + CD = AAA, what could be the possible values of B? Justify" — answered as
  a set with the B = 9 case called out as "the case that is easy to miss".
- 2072 Ashwin "Why is it good news that the disease is rare?" — answered under its own
  heading, ending "A 99 % test is not a 99 % answer".

**Re-audited 2026-09-17; see the AI CLOSED block at the top. Nothing outstanding.**

---

## Suggested order for the fix session

1. `ch4.tex` — write the 100 % / 99 % answer into §4.1, correct the Coverage-check claim.
2. `ch4-num.tex` — add the 2079 Ba Q5 (a)+(b) pair, since (b) is the same class of question.
3. Merge the six papers: `\yr` citations and PYQ-mapping lines first (cheap, mechanical),
   then B1 and B2 content, then the 14 numericals in B3.
4. `ch5-num.tex` — the real DBSCAN PYQ, the Manhattan K-means, the SSE computation.
5. Rebuild, verify, commit sources and PDFs together.
