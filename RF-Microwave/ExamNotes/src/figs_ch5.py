# -*- coding: utf-8 -*-
"""Chapter 5 figures, lifted from the sources and never redrawn.

Original embedded image blobs, pulled from Er. Kobid Karkee's Chapter_5 deck
(pptx and its PDF export) and from two 2078 student presentations. A job names
the source, the slide (pptx) or page (pdf, 1-based), and which picture on it.

Run from src\\:   python figs_ch5.py
"""
import io
import os

import fitz
from PIL import Image
from pptx import Presentation

HERE = os.path.dirname(os.path.abspath(__file__))
RP = os.path.normpath(os.path.join(HERE, "..", "..", "Notes", "RF Pulchowk"))
STU = os.path.join(RP, "New_Chapter_5", "students presentation_2078")
SRC = {
    "deck": os.path.join(RP, "all", "Chapter_5.pptx"),
    "pdf": os.path.join(RP, "Chapter 5", "Chapter_5.pdf"),
    "bwo_cfa": os.path.join(STU, "RF and Microwave.pptx"),
    "twt_mag": next(os.path.join(STU, f) for f in sorted(os.listdir(STU)) if "Travelling" in f),
}
OUT = os.path.join(HERE, "figs")

# name: (source, slide or page, picture index among pictures >= the size floor)
JOBS = {
    "c5_interelectrode": ("deck", 4, 0),
    "c5_twocavity":      ("deck", 14, 0),
    "c5_twocav_osc":     ("deck", 18, 0),
    "c5_threecavity":    ("deck", 19, 0),
    "c5_bwo_helix":      ("deck", 40, 0),
    "c5_mag_paths":      ("deck", 48, 0),
    "c5_mag_spokes":     ("deck", 50, 0),
    "c5_applegate":      ("pdf", 22, 6),
    "c5_reflex":         ("pdf", 29, 6),
    "c5_reflex_apple":   ("pdf", 30, 6),
    "c5_mag_build":      ("pdf", 55, 6),
    "c5_mag_cutoff":     ("pdf", 61, 6),
    "c5_bwo_mtype":      ("bwo_cfa", 6, 0),
    "c5_cfa":            ("bwo_cfa", 13, 0),
    "c5_twt":            ("twt_mag", 4, 0),
}


def flatten(im):
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def pptx_pic(path, slide, idx):
    prs = Presentation(path)
    pics = []
    for sh in prs.slides[slide - 1].shapes:
        if sh.shape_type == 13:
            im = Image.open(io.BytesIO(sh.image.blob))
            if im.size[0] >= 150 and im.size[1] >= 100:
                pics.append(im)
    return flatten(pics[idx])


def pdf_pic(path, page, idx):
    doc = fitz.open(path)
    # raw image index: every page of this export carries a full-page slide
    # background first, so the figure sits further down the list
    info = doc[page - 1].get_images(full=True)[idx]
    pm = fitz.Pixmap(doc, info[0])
    if pm.n - pm.alpha > 3:
        pm = fitz.Pixmap(fitz.csRGB, pm)
    return flatten(Image.open(io.BytesIO(pm.tobytes("png"))))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (src, n, idx) in JOBS.items():
        path = SRC[src]
        im = pdf_pic(path, n, idx) if src == "pdf" else pptx_pic(path, n, idx)
        g = im.convert("L")
        dark = sum(1 for v in g.get_flattened_data() if v < 200) / float(g.size[0] * g.size[1])
        if dark < 0.005:
            raise AssertionError("%s looks blank" % name)
        im.save(os.path.join(OUT, name + ".png"))
        print("%-18s %-8s %2d  %4dx%-4d ink %.3f" % (name, src, n, im.size[0], im.size[1], dark))


if __name__ == "__main__":
    main()
