# -*- coding: utf-8 -*-
"""Topic figures clipped out of the sources. Never redrawn.

Adapted from RF-Microwave/ExamNotes/src/figs_books.py. Han & Kamber 3rd ed carries their figures as vector drawings with a text
layer, so a clip renders crisp at any dpi. Each job names the book, the
1-based page and the caption's opening words. The box is found, not typed:
it runs from the bottom of the last body-text block above the caption to the
top of the caption, and is then shrunk to the union of the drawings and
label text inside that band, so the caption itself and the running text
never land in the crop. `sub` optionally keeps only a horizontal fraction of
that box, for one panel of a multi-panel figure.

    python figs_books.py            render every job
    python figs_books.py --boxes    print the boxes only
"""
import os
import re
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.normpath(os.path.join(HERE, "..", "..", "Books"))
OUT = os.path.join(HERE, "figs")
DPI = 300
PAD = 3.0

HK = os.path.join(BOOKS, "The-Morgan-Kaufmann-Series-in-Data-Management-Systems-Jiawei-Han-"
                  "Micheline-Kamber-Jian-Pei-Data-Mining.-Concepts-and-Techniques-3rd-Edition-"
                  "Morgan-Kaufmann-2011.pdf")
MISHRA = os.path.normpath(os.path.join(HERE, "..", "..", "Notes", "data mining_"))
SRC = {
    "hk": HK,
    "m3": os.path.join(MISHRA, "Chapter 3 - Classification.pdf"),
    "m4": os.path.join(MISHRA, "Chapter-4 Association Analysis.pdf"),
    "m67": os.path.join(MISHRA, "Chapter  6 _ 7.pdf"),
}

# Han & Kamber 3rd ed: vector figures, found by caption.
# name: (book, page, caption prefix, sub=(x0frac, x1frac) or None)
JOBS = {
    "c2_preproc_forms.png":  ("hk", 124, "Figure 3.1 ",  None),
    "c2_boxplot_hk.png":     ("hk", 87,  "Figure 2.3 ",  None),
    "c3_class_learn.png":    ("hk", 366, "Figure 8.1 ",  None),
    "c3_class_use.png":      ("hk", 366, "Figure 8.1 ",  None),
    "c3_rules_vs_tree.png":  ("hk", 55,  "Figure 1.9 ",  None),
    "c4_apriori_example.png": ("hk", 288, "Figure 6.2 ", None),
    "c4_fptree_hk.png":      ("hk", 295, "Figure 6.7 ",  None),
    "c5_kmeans_iter.png":    ("hk", 490, "Figure 10.3 ", None),
    "c5_agglo_divisive.png": ("hk", 497, "Figure 10.6 ", None),
    "c5_dendrogram_hk.png":  ("hk", 497, "Figure 10.7 ", None),
    "c5_dbscan_reach.png":   ("hk", 510, "Figure 10.14 ", None),
    "c6_outlier_region.png": ("hk", 581, "Figure 12.1 ", None),
    "c6_collective.png":     ("hk", 584, "Figure 12.2 ", None),
    "c6_global_local.png":   ("hk", 601, "Figure 12.8 ", None),
    "c7_timeseries.png":     ("hk", 625, "Figure 13.2 ", None),
}

# Mishra's chapter notes paste their figures as pictures: take the largest one.
# name: (book, page)
PICS = {
    "c3_knn_k.png":          ("m3", 13),
    "c4_subgraph_types.png": ("m4", 9),
    "c7_web_taxonomy.png":   ("m67", 6),
}

TOP = {}
# Two stacked panels set side by side halve the height a figure costs.
# name: (keep "above" or "below", y in pt just under the (a) panel label)
SPLIT = {
    "c3_class_learn.png": ("above", 285),
    "c3_class_use.png":   ("below", 285),
}
BOTTOM = {}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def find_box(page, prefix, floor=None):
    blocks = [b for b in page.get_text("blocks") if b[6] == 0]
    cap = [b for b in blocks if norm(b[4]).startswith(prefix)]
    if len(cap) != 1:
        raise SystemExit("caption %r found %d times on p%d" % (prefix, len(cap), page.number + 1))
    cap = fitz.Rect(cap[0][:4])
    # body text above: a block of running prose (long) ending above the caption.
    # Other captions count too, so a second figure higher up the page is excluded.
    top = page.rect.y0 + 40          # below the running head
    # H&K's running head ("50 Chapter 2 ...") sits lower than Pozar's: start below it
    for b in blocks:
        if b[1] < 50 and b[3] < cap.y0:
            top = max(top, b[3])
    for b in blocks:
        r = fitz.Rect(b[:4])
        t = norm(b[4])
        # prose = a long block spanning most of the text column; label blocks
        # inside a figure can be long (a frequency table) but are narrow
        # A numbered display equation, eg "(3.193)", is running text too.
        prose = ((len(t) > 90 and r.width > 0.6 * page.rect.width)
                 or re.match(r"(FIGURE|Fig\.)\s*\d", t)
                 or re.search(r"\(\d+\.\d+[a-z]?\)\s*,?$", t))
        if prose and r.y1 <= cap.y0 - 2 and r.y1 > top:
            top = r.y1
    if floor is not None:
        top = max(top, floor)
    band = fitz.Rect(page.rect.x0, top, page.rect.x1, cap.y0 - 1)
    box = fitz.Rect()
    for d in page.get_drawings():
        r = d["rect"]
        if band.contains(r) and r.width < page.rect.width * 0.98:
            box |= r
    for b in blocks:
        r = fitz.Rect(b[:4])
        if band.contains(r):
            box |= r
    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"])
        if band.intersects(r):
            box |= r & band
    if box.is_empty:
        raise SystemExit("nothing drawn above %r on p%d" % (prefix, page.number + 1))
    return box + (-PAD, -PAD, PAD, PAD)


def main():
    only_boxes = "--boxes" in sys.argv
    docs = {}
    for name, (book, pno, prefix, sub) in JOBS.items():
        doc = docs.setdefault(book, fitz.open(SRC[book]))
        page = doc[pno - 1]
        box = find_box(page, prefix, TOP.get(name))
        if name in SPLIT:
            side, y = SPLIT[name]
            if side == "above":
                box.y1 = y
            else:
                box.y0 = y
        if name in BOTTOM:
            box.y1 = BOTTOM[name]
        if sub:
            w = box.width
            box = fitz.Rect(box.x0 + sub[0] * w, box.y0, box.x0 + sub[1] * w, box.y1)
        print("%-24s %s p%d %s" % (name, book, pno, tuple(round(v) for v in box)))
        if not only_boxes:
            page.get_pixmap(dpi=DPI, clip=box).save(os.path.join(OUT, name))
    for name, (book, pno) in PICS.items():
        doc = docs.setdefault(book, fitz.open(SRC[book]))
        page = doc[pno - 1]
        best = max((fitz.Rect(i["bbox"]) for i in page.get_image_info()),
                   key=lambda r: r.get_area())
        print("%-24s %s p%d %s" % (name, book, pno, tuple(round(v) for v in best)))
        if not only_boxes:
            page.get_pixmap(dpi=DPI, clip=best).save(os.path.join(OUT, name))


if __name__ == "__main__":
    main()
