# -*- coding: utf-8 -*-
"""Crop the O&M topic figures out of their source decks. Never redraws.

Adhikari's deck ("Notes/O _ M.pdf") stamps an "IOE Syllabus" watermark image at
bbox (225,135,495,405) on every page. Deleting that image before rendering gives a
clean crop; nothing else on the page is touched.

    python figs.py          render every spec below into figs/
"""
import os
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
OM = os.path.join(HERE, "..", "..", "Notes", "O _ M.pdf")
DPI = 220
WATERMARK = (225, 135)

# name: (source, 1-based page, clip rect in pt or None for the page's largest picture)
SPECS = {
    "c3_motivation_eq.png": (OM, 201, None),   # Motivation equation: inputs -> performance -> outcomes
    "c5_is_environment.png": (OM, 281, None),  # IS inside the organisation inside its environment
    "c5_is_pyramid.png": (OM, 300, None),      # IS types by management level x functional area
}


def drop_watermark(page):
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if (round(r.x0), round(r.y0)) == WATERMARK:
                page.delete_image(img[0])
                break


def largest_picture(page):
    best = None
    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"])
        if best is None or r.get_area() > best.get_area():
            best = r
    return best


def main():
    docs = {}
    for name, (src, pno, clip) in SPECS.items():
        doc = docs.setdefault(src, fitz.open(src))
        page = doc[pno - 1]
        drop_watermark(page)
        rect = fitz.Rect(clip) if clip else largest_picture(page)
        if rect is None:
            raise SystemExit("no picture on p%d for %s" % (pno, name))
        page.get_pixmap(dpi=DPI, clip=rect & page.rect).save(os.path.join(FIGS, name))
        print("ok %-24s p%d %s" % (name, pno, tuple(round(v) for v in rect)))


if __name__ == "__main__":
    main()
