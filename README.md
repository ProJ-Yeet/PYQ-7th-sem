# PYQ Sorted Chapterwise
### For 7th Semester (IOE)

This is a collection of **Past Year Questions (PYQ)** of the Institute of Engineering (IOE), Tribhuvan University, sorted chapter-wise by syllabus topic.

The subjects covered are from the Electronics/Computer 7th semester:

1. Artificial Intelligence [CT653 / CT710]
2. Digital Signal Analysis and Processing [CT704] + Digital Signal Processing [EX753]
3. Organization and Management [ME708]
4. RF and Microwave Engineering [EX752 / EX716]
5. Wireless Communication [EX751 / EX715]
6. Data Mining, Elective I [CT72502 / CT725]

## Structure

Each subject folder contains:
- `*_Sorted_PYQ_Detailed.tex` / `.pdf` — every past question, chapter-wise, in full (nothing abbreviated)
- `*_Sorted_PYQ_Concise.tex` / `.pdf` — the same content compressed to keyword form, for quick revision
- the raw scanned question papers the compilations were built from
- `images/` — figures cropped out of scanned papers and referenced by the `.tex` files
- `ocr/` — a verbatim transcription of every scanned paper, so the scans never have to be re-read

Once a subject has been extended with newer papers, its filenames carry the year span they cover, e.g. `DSAP_Sorted_PYQ_Detailed_66-82.pdf`, `Wireless_Sorted_PYQ_Detailed_70-82.pdf`.

Two subjects additionally carry a full set of syllabus-order exam notes, with LaTeX sources under `src/`:

- `Data Mining/ExamNotes/` — 7 chapters + numerical-problem companions
- `Wireless/ExamNotes/` — 8 chapters + 5 numerical-problem companions, 13 PDFs in all

The notes are written to be answered from directly: every topic carries the years it was asked and a tier badge counted over that subject's whole paper set, every numerical reproduces the exam question verbatim before working it, and figures are copied from the lecture sources rather than redrawn. In `src/`, `build.py` compiles and deploys, `verify.py` recomputes every published numerical answer independently and asserts it against the printed value, `audit.py` checks that no topic heading is left stranded at the foot of a page, and `figs.py` re-crops the figures from their sources.

## Notes

- Questions are grouped by syllabus subsection, not by year.
- **Bold** = Regular exam, plain = Back exam. `monospace` marks the second programme where a subject has two.
- Programme and exam type are independent axes, so all four combinations occur: **`80 Bh`** is a Regular paper of the monospace programme, `81 Ba` a Back paper of it.
- Which programme gets the monospace differs by subject, so read each document's own Notes block. AI, RF-Microwave and Wireless mark the *newer* code that way (CT710 vs CT653). DSAP is the exception: there the current paper (CT704, BEI/BCT) is plain and the older BEX paper (EX753) is monospace.
- Month abbreviations: Ba = Baishakh, Jth = Jestha, Asa = Ashad, Shr = Shrawan, Bh = Bhadra, Ash = Ashwin, Ka = Kartik, Mng = Mangsir, Po = Poush, Ma = Magh, Ch = Chaitra.
- Where a source paper is itself defective — a missing data table, a reversed inequality, seven entries listed for an eight-point DFT — the document records it as printed and says so, rather than silently correcting it.
- Built with [Tectonic](https://tectonic-typesetting.github.io/).

## Coverage

| Subject | Papers | Span |
|---|---|---|
| Artificial Intelligence | 17 | 2069–2081 |
| DSAP (CT704) | 27 | 2066–2082 |
| DSAP (EX753) | 17 | 2069–2081 |
| Organization and Management | 29 | 2065–2082 |
| RF and Microwave | 14 | 2069–2081 |
| Wireless Communication (EX751) | 16 | 2070–2080 |
| Wireless Communication (EX715) | 6 | 2079–2082 |
| Data Mining | 17 | 2070–2081 |
