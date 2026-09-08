# -*- coding: utf-8 -*-
"""Build the Data Mining exam-notes PDFs.

Run from inside this src\ folder:   python build.py [ch1] [ch2] ...
With no args it builds everything. Finished PDFs land one level up, in
ExamNotes\, under their display names; everything else stays in here.

Needs tectonic.exe on PATH or in this folder. See the "PYQ LaTeX project
layout" memory for where to find a copy.
"""
import os, shutil, subprocess, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

TARGETS = {
    "master":  ("master", "Data Mining - Complete Exam Notes.pdf"),
    "master-num": ("master-num",
                "Data Mining - Complete Numerical Problems & Solutions.pdf"),
    "ch1":     ("ch1-standalone",     "Ch1 - Introduction.pdf"),
    "ch2":     ("ch2-standalone",     "Ch2 - Data Preprocessing.pdf"),
    "ch2-num": ("ch2-num-standalone",
                "Ch2 - Data Preprocessing - Numerical Problems & Solutions.pdf"),
    "ch3":     ("ch3-standalone",     "Ch3 - Classification.pdf"),
    "ch3-num": ("ch3-num-standalone",
                "Ch3 - Classification - Numerical Problems & Solutions.pdf"),
    "ch6":     ("ch6-standalone",     "Ch6 - Anomaly and Fraud Detection.pdf"),
    "ch6-num": ("ch6-num-standalone",
                "Ch6 - Anomaly and Fraud Detection - Numerical Problems & Solutions.pdf"),
    "ch4":     ("ch4-standalone",     "Ch4 - Association Analysis.pdf"),
    "ch4-num": ("ch4-num-standalone",
                "Ch4 - Association Analysis - Numerical Problems & Solutions.pdf"),
    "ch5":     ("ch5-standalone",     "Ch5 - Cluster Analysis.pdf"),
    "ch5-num": ("ch5-num-standalone",
                "Ch5 - Cluster Analysis - Numerical Problems & Solutions.pdf"),
    "ch7":     ("ch7-standalone",     "Ch7 - Advanced Applications.pdf"),
    "ch7-num": ("ch7-num-standalone",
                "Ch7 - Advanced Applications - Numerical Problems & Solutions.pdf"),
}

def tectonic():
    if shutil.which("tectonic"):
        return "tectonic"
    local = os.path.join(HERE, "tectonic.exe")
    if os.path.exists(local):
        return local
    # fall back to any copy left in a previous session scratchpad
    pat = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude",
                       "D--College-PYQ", "*", "scratchpad", "tectonic.exe")
    hits = glob.glob(pat)
    if hits:
        return hits[0]
    sys.exit("tectonic.exe not found. See the PYQ LaTeX project layout memory.")

def main():
    tex = tectonic()
    names = sys.argv[1:] or list(TARGETS)
    for n in names:
        if n not in TARGETS:
            print("unknown target:", n); continue
        stem, pretty = TARGETS[n]
        print(f"--- building {n}")
        r = subprocess.run([tex, stem + ".tex"], cwd=HERE,
                           capture_output=True, text=True)
        err = [l for l in (r.stderr or "").splitlines() if l.lower().startswith("error")]
        if err:
            print("\n".join(err)); sys.exit(f"{n} FAILED")
        shutil.move(os.path.join(HERE, stem + ".pdf"), os.path.join(OUT, pretty))
        print("   ->", pretty)
    print("done")

if __name__ == "__main__":
    main()
