# -*- coding: utf-8 -*-
"""Chapter 4 figures, lifted from the sources and never redrawn.

Most come straight out of Er. Gangaju's Chapter_4.pptx as the ORIGINAL embedded
image blobs (python-pptx), so there is no re-rendering loss and the job is
reproducible from the deck alone. A crop box, where given, is fractional
(left, top, right, bottom) of that blob. The circular-guide sketch is the one
drawing that exists only in the handwritten Waveguide.pdf.

Run from src\\:   python figs_ch4.py
"""
import io
import os

import fitz
from PIL import Image
from pptx import Presentation

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.normpath(os.path.join(HERE, "..", "..", "Notes", "RF Pulchowk"))
DECK = os.path.join(NOTES, "all", "Chapter_4.pptx")
WGPDF = os.path.join(NOTES, "Chapter 4", "Waveguide.pdf")
OUT = os.path.join(HERE, "figs")

# name: (slide number, picture index on that slide, crop box or None)
DECK_JOBS = {
    "c4_probe":        (3, 0, None),
    "c4_loop":         (6, 0, None),
    "c4_rect_geom":    (12, 0, (0.615, 0.03, 1.00, 0.50)),
    "c4_te_patterns":  (20, 0, None),
    "c4_cutoff_line":  (22, 0, (0.40, 0.278, 1.00, 0.805)),
    "c4_attenuator":   (39, 1, None),
    "c4_ratrace":      (51, 0, None),
    "c4_coupler":      (54, 0, None),
    "c4_twohole":      (57, 0, None),
    "c4_circulator":   (62, 0, None),
    "c4_isolator":     (66, 1, None),
    "c4_gunn_build":   (69, 0, None),
    "c4_gunn_iv":      (73, 0, None),
    "c4_maser":        (78, 0, None),
    "c4_mesfet":       (85, 0, (0.00, 0.05, 0.42, 1.00)),
    "c4_hemt":         (86, 0, (0.50, 0.00, 1.00, 1.00)),
    "c4_rect_cavity":  (90, 0, None),
    "c4_circ_cavity":  (93, 0, (0.18, 0.40, 0.82, 1.00)),
}

# stray text left inside a crop box: name -> [(l, t, r, b) fraction of the CROP]
MASKS = {
    "c4_rect_geom": [(0.0, 0.0, 0.20, 0.30)],   # tail of the Helmholtz line
}

# name: (0-based page, crop box as fraction of the page)
PDF_JOBS = {
}


def crop(im, box):
    if box is None:
        return im
    w, h = im.size
    l, t, r, b = box
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def flatten(im):
    """Transparent PNGs from the deck render black in some PDF viewers."""
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def not_blank(im, name):
    g = im.convert("L")
    dark = sum(1 for v in g.get_flattened_data() if v < 200) / float(g.size[0] * g.size[1])
    if dark < 0.005:
        raise AssertionError("%s looks blank (%.4f dark)" % (name, dark))
    return dark


def main():
    os.makedirs(OUT, exist_ok=True)
    prs = Presentation(DECK)
    for name, (sl, idx, box) in DECK_JOBS.items():
        pics = [s for s in prs.slides[sl - 1].shapes if s.shape_type == 13]
        im = flatten(Image.open(io.BytesIO(pics[idx].image.blob)))
        im = crop(im, box)
        for mb in MASKS.get(name, []):
            w, h = im.size
            im.paste("white", (int(mb[0] * w), int(mb[1] * h), int(mb[2] * w), int(mb[3] * h)))
        d = not_blank(im, name)
        im.save(os.path.join(OUT, name + ".png"))
        print("%-16s slide %2d  %4dx%-4d  ink %.3f" % (name, sl, im.size[0], im.size[1], d))
    doc = fitz.open(WGPDF)
    for name, (pg, box) in PDF_JOBS.items():
        page = doc[pg]
        r = page.rect
        clip = fitz.Rect(r.x0 + box[0] * r.width, r.y0 + box[1] * r.height,
                         r.x0 + box[2] * r.width, r.y0 + box[3] * r.height)
        pm = page.get_pixmap(dpi=300, clip=clip)
        im = Image.open(io.BytesIO(pm.tobytes("png"))).convert("RGB")
        d = not_blank(im, name)
        im.save(os.path.join(OUT, name + ".png"))
        print("%-16s pdf p%-2d   %4dx%-4d  ink %.3f" % (name, pg + 1, im.size[0], im.size[1], d))


if __name__ == "__main__":
    main()
