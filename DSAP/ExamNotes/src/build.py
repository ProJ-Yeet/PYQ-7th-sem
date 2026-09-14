# -*- coding: utf-8 -*-
"""Build the DSAP / DSP exam-notes PDFs.

Run from inside this src\\ folder:   python build.py [ch2] [ch3-num] ...
With no args it builds everything. Finished PDFs land one level up, in
ExamNotes\\, under their display names; everything else stays in here.

Needs tectonic.exe on PATH or in this folder. See the "PYQ LaTeX project
layout" memory for where to find a copy.

Before building a numerical target, run verify.py: it recomputes every
published answer independently and asserts it against the printed value.

Copied from Wireless\\ExamNotes\\src\\build.py; only TARGETS differs.
"""
import os
import shutil
import subprocess
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

NUM = " - Numerical Problems & Solutions.pdf"
CH = {
    "ch1": "Ch1 - Discrete-Time Signals and Systems",
    "ch2": "Ch2 - Z-Transform",
    "ch3": "Ch3 - Analysis of LTI Systems in the Frequency Domain",
    "ch4": "Ch4 - Discrete Filter Structures",
    "ch5": "Ch5 - FIR Filter Design",
    "ch6": "Ch6 - IIR Filter Design",
    "ch7": "Ch7 - Discrete Fourier Transform and FFT",
    "ch8": "Ch8 - DSP Fundamentals and Implementation",
}

TARGETS = {
    "master": ("master", "DSAP - Complete Exam Notes.pdf"),
    "master-num": ("master-num", "DSAP - Complete Numerical Problems & Solutions.pdf"),
}
for k, name in CH.items():
    TARGETS[k] = (k + "-standalone", name + ".pdf")
    if k != "ch8":                      # ch8 is theory; its one small numerical is inline
        TARGETS[k + "-num"] = (k + "-num-standalone", name + NUM)


def tectonic():
    if shutil.which("tectonic"):
        return "tectonic"
    local = os.path.join(HERE, "tectonic.exe")
    if os.path.exists(local):
        return local
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
        if not os.path.exists(os.path.join(HERE, stem + ".tex")):
            print(f"--- skipping {n}: {stem}.tex not written yet")
            continue
        print(f"--- building {n}")
        r = subprocess.run([tex, "--print", stem + ".tex"], cwd=HERE,
                           capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        err = [l for l in out.splitlines() if l.lower().startswith("error")]
        if err:
            print("\n".join(err))
            sys.exit(f"{n} FAILED")
        # a \sbs pair taller than \sbsmax cannot fit under its own heading on
        # any page; split it into two pairs at a \lead boundary.
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
