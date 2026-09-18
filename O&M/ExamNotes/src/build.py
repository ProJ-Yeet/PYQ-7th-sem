# -*- coding: utf-8 -*-
"""Build the Organization and Management exam-notes PDFs.

Run from inside this src\\ folder:   python build.py [ch1] [ch2-num] ...
With no args it builds everything. Finished PDFs land one level up, in
ExamNotes\\, under their display names; everything else stays in here.

Needs tectonic.exe on PATH or in this folder.
"""
import os
import shutil
import subprocess
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

TARGETS = {
    "master":     ("master", "Organization and Management - Complete Exam Notes.pdf"),
    "ch1":        ("ch1-standalone", "Ch1 - Introduction.pdf"),
    "ch2":        ("ch2-standalone", "Ch2 - Personnel Management.pdf"),
    "ch3":        ("ch3-standalone", "Ch3 - Motivation, Leadership and Entrepreneurship.pdf"),
    "ch4":        ("ch4-standalone", "Ch4 - Case Studies.pdf"),
    "ch5":        ("ch5-standalone", "Ch5 - Management Information System.pdf"),
}


def tectonic():
    local = os.path.join(HERE, "tectonic.exe")
    if os.path.exists(local):
        return local
    if shutil.which("tectonic"):
        return "tectonic"
    sibling = os.path.normpath(os.path.join(
        HERE, "..", "..", "..", "Data Mining", "ExamNotes", "src", "tectonic.exe"))
    if os.path.exists(sibling):
        return sibling
    sys.exit("tectonic.exe not found.")


def main():
    tex = tectonic()
    names = sys.argv[1:] or list(TARGETS)
    stale = []
    for n in names:
        if n not in TARGETS:
            print("unknown target:", n)
            continue
        stem, pretty = TARGETS[n]
        tex_file = os.path.join(HERE, stem + ".tex")
        if not os.path.exists(tex_file):
            print(f"--- skipping {n} ({stem}.tex does not exist yet)")
            continue
        print(f"--- building {n}")
        r = subprocess.run([tex, "--print", stem + ".tex"], cwd=HERE,
                           capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        err = [l for l in out.splitlines() if l.lower().startswith("error")]
        if err:
            print("\n".join(err))
            sys.exit(f"{n} FAILED")
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
