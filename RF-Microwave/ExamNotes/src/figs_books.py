# -*- coding: utf-8 -*-
"""Topic figures clipped out of the vector textbooks. Never redrawn.

Pozar 4e and Das & Das carry their figures as vector drawings with a text
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

SRC = {
    "pozar": os.path.join(BOOKS, "Microwave_Engineering_David_M_Pozar_4ed_Wiley_2012.pdf"),
    "das": os.path.join(BOOKS, "Microwave Engineering (Annapurna Das, Sisir K Das) (z-lib.org).pdf"),
}

# name: (book, page, caption prefix, sub=(x0frac, x1frac) or None)
JOBS = {
    "c1_em_spectrum.png":    ("pozar", 22,  "FIGURE 1.1 ", None),
    "c1_stripline.png":      ("pozar", 161, "FIGURE 3.22", None),
    "c1_microstrip.png":     ("pozar", 167, "FIGURE 3.25", None),
    "c2_planar_lines.png":   ("das",   115, "Fig. 3.27",   None),
    "c2_lumped_model.png":   ("pozar", 69,  "FIGURE 2.1 ", None),
    "c2_lossless_match.png": ("pozar", 249, "FIGURE 5.1 ", None),
    "c2_single_stub_a.png":  ("pozar", 255, "FIGURE 5.4",  None),
    "c2_single_stub_b.png":  ("pozar", 255, "FIGURE 5.4",  None),
    "c2_double_stub.png":    ("pozar", 262, "FIGURE 5.7",  None),
    "c3_nport.png":          ("pozar", 194, "FIGURE 4.5",  None),
    "c3_circulators.png":    ("pozar", 339, "FIGURE 7.2",  None),
    "c3_magictee_a.png":     ("pozar", 391, "FIGURE 7.50", None),
    "c3_magictee_b.png":     ("pozar", 391, "FIGURE 7.50", None),
    "c3_hybrid180.png":      ("pozar", 382, "FIGURE 7.41", None),
    "c5_lna_general.png":    ("pozar", 582, "FIGURE 12.2", None),
    "c6_mixer_conv.png":     ("pozar", 657, "FIGURE 13.24", None),
    "c6_mixer_diode.png":    ("pozar", 662, "FIGURE 13.25", None),
    "c7_refraction.png":     ("pozar", 722, "FIGURE 14.28", None),
    "c7_atm_atten.png":      ("pozar", 723, "FIGURE 14.29", None),
}

# Where the text above a figure is an unnumbered display (a matrix), the
# prose test cannot see it; give the figure's top edge by hand, in pt.
TOP = {
    "c3_nport.png": 455,
}

# Two stacked panels set side by side instead halve the height a figure costs.
# name: (keep "above" or "below", y in pt just under the (a) panel label)
SPLIT = {
    "c2_single_stub_a.png": ("above", 198),
    "c2_single_stub_b.png": ("below", 198),
    "c3_magictee_a.png":    ("above", 518),
    "c3_magictee_b.png":    ("below", 518),
}

# Cut a figure short, in pt: keep only the part above this line.
BOTTOM = {
    # the spectrum bar only; the band table under it uses older letter-band
    # edges (K 18-26 GHz) that contradict the IEEE table the notes print
    "c1_em_spectrum.png": 195,
}


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


if __name__ == "__main__":
    main()
