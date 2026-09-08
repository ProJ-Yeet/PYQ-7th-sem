# -*- coding: utf-8 -*-
"""Per-page ink coverage of the built PDFs.

audit.py answers "is a heading stranded" (a bug) and "which pages end short"
(not a bug). This answers the other question: is the document as a whole set
too loose or too tight? The band that reads well is a mean of about 65-73 %,
measured across every page but the last, which is meant to end early.

Run from inside this src\\ folder:   python fill.py [Ch2] [Ch3] ...
With no args it measures every PDF one level up, in ExamNotes\\.
"""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

MARG = 1.35 * 28.3465          # top and bottom margin, pt (see geometry)


def page_fill(page):
    floor = MARG + 6                       # below the running header
    bottom = 0.0
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"] != 0:               # an image block
            bottom = max(bottom, blk["bbox"][3])
            continue
        for ln in blk["lines"]:
            if ln["bbox"][3] < floor:
                continue
            if not "".join(s["text"] for s in ln["spans"]).strip():
                continue
            bottom = max(bottom, ln["bbox"][3])
    for drawing in page.get_drawings():
        r = drawing["rect"]
        if r.y1 < floor or r.height > page.rect.height * 0.9:
            continue
        bottom = max(bottom, r.y1)
    for img in page.get_images():
        for r in page.get_image_rects(img[0]):
            bottom = max(bottom, r.y1)
    return (bottom - MARG) / (page.rect.height - 2 * MARG)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    want = [a.lower() for a in sys.argv[1:]]
    names = sorted(f for f in os.listdir(OUT) if f.lower().endswith(".pdf"))
    if want:
        names = [f for f in names if any(w in f.lower() for w in want)]
    grand = []
    for fn in names:
        doc = fitz.open(os.path.join(OUT, fn))
        fills = [page_fill(p) for p in doc]
        body = fills[:-1] or fills          # the last page is meant to end early
        mean = sum(body) / len(body)
        grand.extend(body)
        worst = sorted(range(len(body)), key=lambda i: body[i])[:3]
        print("%-58s %2d pp  mean %5.1f%%  thinnest: %s"
              % (fn[:58], doc.page_count, mean * 100,
                 ", ".join("p%d %.0f%%" % (i + 1, body[i] * 100) for i in worst)))
        doc.close()
    if len(names) > 1 and grand:
        print("\nacross %d documents, %d body pages: mean %.1f%%  (target 65-73)"
              % (len(names), len(grand), 100 * sum(grand) / len(grand)))


if __name__ == "__main__":
    main()
