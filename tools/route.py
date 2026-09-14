# -*- coding: utf-8 -*-
"""Model routing table for this repo.

Single source of truth for which lane a piece of work belongs in. Imported by
session_meter.py so a measured delegation can be scored against the lane it
claimed. Run it bare to print the table, or with a task description to get a
suggestion:

    python tools/route.py
    python tools/route.py "find which notes PDFs cover DSAP chapter 3"

Lanes, cheapest first:

  script   no model at all. A tool already does it deterministically.
  haiku    retrieval and tallying. No judgement, output is a table.
  sonnet   bounded mechanical work behind a machine-checkable exit test.
  opus     authoring, answers, tiering, diagnosis, anything the reader sees.

The rule behind the split: **delegate the work whose correctness a script can
prove, keep the work whose correctness only a reader can judge.** Every sonnet
lane below names its own exit test; if a task has no exit test it is not a
sonnet task.
"""
import sys

# Relative price per token, Opus = 1.0. List-price ratios are roughly 5:1
# Opus:Sonnet and 5:1 Sonnet:Haiku. Edit here only.
RATE = {"opus": 1.00, "sonnet": 0.20, "haiku": 0.04, "script": 0.0}

# lane, agent, task class, exit test, why
TABLE = [
    ("script", None, "build a chapter PDF",
     "tectonic exit 0", "build.py already does it; a model adds nothing"),
    ("script", None, "verify published numerical answers",
     "verify.py all-pass", "verify.py recomputes independently; never re-derive by hand"),
    ("script", None, "audit layout (stranded headings, short pages)",
     "audit.py 0 findings", "audit.py measures the PDF"),
    ("script", None, "reconcile question counts against the archive",
     "check.py 0 mismatches", "check.py compares archive to .tex"),
    ("script", None, "rebuild the Anki deck",
     "0 unhandled macros", "anki_from_notes.py parses the chapters directly"),
    ("script", None, "census a PDF's text layer",
     "page counts printed", "one fitz line, golden rule 2"),

    ("haiku", "pyq-scout", "sweep a notes tree and report which files cover a topic",
     "every claim carries file:page", "grep and page counts, no interpretation"),
    ("haiku", "pyq-scout", "tally year codes / marks / chip counts from a .tex",
     "arithmetic reconciles to 80 per paper", "counting, and the total proves it"),
    ("haiku", "pyq-scout", "git hygiene check before a commit",
     "git status clean of strays", "mechanical inspection"),
    ("haiku", "pyq-scout", "grep the OCR archives for a question by keyword",
     "verbatim quote with its year code", "retrieval, quoted not paraphrased"),

    ("sonnet", "pyq-extract", "transcribe scanned pages into an OCR archive",
     "marks reconcile to the printed Full Marks of 80",
     "golden rules 2-4; the marks arithmetic is the exit test"),
    ("sonnet", "pyq-extract", "dump and triage a deck for chapter source material",
     "page list, each confirmed by its own text",
     "bulk reading; the tokens never need to reach the main thread"),
    ("sonnet", "pyq-latex", "chase a LaTeX build error to a clean build",
     "tectonic exit 0 and page count unchanged",
     "the compiler is the oracle; iteration is cheap and checkable"),
    ("sonnet", "pyq-latex", "repair layout findings to convergence",
     "audit.py 0 stranded, 0 short",
     "each fix repaginates, so it needs a loop, not judgement"),
    ("sonnet", "pyq-figure", "crop figures and review the contact sheet",
     "every spec yields non-blank ink inside the named box",
     "figs.py plus eyes on one sheet; a bad crop is self-evident"),
    ("sonnet", "pyq-crosscheck", "locate a question check.py says is missing",
     "quote found in the archive, or absence proven",
     "bounded search with a definite answer"),

    ("opus", None, "write chapter theory or a numerical solution",
     "a reader's judgement only",
     "RF Ch1 was drafted by a weaker model: 3 phantom citations, 4 tier chips "
     "disagreeing with their own year lists, no PYQ band, a physics "
     "misconception. Repair cost more than the draft saved."),
    ("opus", None, "assign frequency tiers and PYQ mapping",
     "check.py agrees, but only after the judgement is made",
     "the same defect class as above"),
    ("opus", None, "diagnose a defective exam paper",
     "none", "needs the maths to decide a misprint from a hard question"),
    ("opus", None, "group numericals into one worked example",
     "none", "deciding that two problems share a procedure IS the content"),
    ("opus", None, "decide house style, or anything the user reads",
     "none", "voice and the checkpoint report"),
]


def suggest(text):
    t = text.lower()
    hits = []
    for lane, agent, task, exit_test, why in TABLE:
        score = sum(1 for w in task.lower().split() if len(w) > 3 and w in t)
        if score:
            hits.append((score, lane, agent, task, exit_test))
    hits.sort(reverse=True)
    if not hits:
        print("no match. Default to opus, and if it turns out mechanical with an")
        print("exit test, add a row to TABLE so the next one routes itself.")
        return
    for score, lane, agent, task, exit_test in hits[:3]:
        print("%-7s %-14s %s" % (lane, agent or "-", task))
        print("        exit test: " + exit_test)


def main():
    if len(sys.argv) > 1:
        suggest(" ".join(sys.argv[1:]))
        return
    cur = None
    for lane, agent, task, exit_test, why in TABLE:
        if lane != cur:
            cur = lane
            print("")
            print("== " + lane.upper() + "   (relative cost per token: %.2f)" % RATE[lane])
        print("  %-14s %s" % (agent or "-", task))
        print("  %-14s exit: %s" % ("", exit_test))
    print("")
    print("Cost ratios: " + ", ".join("%s=%.2f" % (k, v) for k, v in RATE.items()))


if __name__ == "__main__":
    main()
