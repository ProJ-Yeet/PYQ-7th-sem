# -*- coding: utf-8 -*-
"""Build the Artificial Intelligence exam-notes PDFs.

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

KR = "Knowledge Representation, Inference and Reasoning"

TARGETS = {
    "master":  ("master", "Artificial Intelligence - Complete Exam Notes.pdf"),
    "master-num": ("master-num",
                   "Artificial Intelligence - Complete Solved Problems.pdf"),
    "ch1":     ("ch1-standalone", "Ch1 - Introduction.pdf"),
    "ch2":     ("ch2-standalone", "Ch2 - Problem Solving.pdf"),
    "ch2-num": ("ch2-num-standalone",
                "Ch2 - Problem Solving - Solved Problems.pdf"),
    "ch3":     ("ch3-standalone", "Ch3 - Search Techniques.pdf"),
    "ch3-num": ("ch3-num-standalone",
                "Ch3 - Search Techniques - Solved Problems.pdf"),
    "ch4":     ("ch4-standalone", "Ch4 - " + KR + ".pdf"),
    "ch4-num": ("ch4-num-standalone", "Ch4 - " + KR + " - Solved Problems.pdf"),
    "ch5":     ("ch5-standalone", "Ch5 - Structured Knowledge Representation.pdf"),
    "ch5-num": ("ch5-num-standalone",
                "Ch5 - Structured Knowledge Representation - Solved Problems.pdf"),
    "ch6":     ("ch6-standalone", "Ch6 - Machine Learning.pdf"),
    "ch6-num": ("ch6-num-standalone",
                "Ch6 - Machine Learning - Solved Problems.pdf"),
    "ch7":     ("ch7-standalone", "Ch7 - Applications of AI.pdf"),
    "ch7-num": ("ch7-num-standalone",
                "Ch7 - Applications of AI - Solved Problems.pdf"),
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
        # errors="replace" on purpose: tectonic emits bytes the Windows ANSI
        # codepage cannot decode, and without this the reader thread dies with
        # a UnicodeDecodeError. The build still produced a PDF, but the error
        # and @SBS-TOO-TALL scans below then ran on truncated output and passed
        # silently -- a failing build that reports success.
        r = subprocess.run([tex, "--print", stem + ".tex"], cwd=HERE,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
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
