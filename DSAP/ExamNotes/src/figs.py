# -*- coding: utf-8 -*-
"""Crop figures for the DSAP exam notes out of the source decks and scans.

    python figs.py            # cut every figure in SPECS
    python figs.py ch1        # only the ones whose name starts ch1
    python figs.py --sheet    # also build a contact sheet of the results

House style: figures are never redrawn, only cropped from the source that
already has them (see the exam-notes-style memory). Picking a crop box by eye
costs a page render per figure, so each spec instead names the page and lets
the tool find the ink: the union of the page's vector drawings and raster
images, minus any band the spec asks to drop (a slide title, a footer). Verify
the results from the contact sheet, which is one image for the whole batch.

A spec is (out-name, source pdf relative to Notes\\, 1-based page, options):
  drop_top    fraction of the page height to ignore at the top (slide titles)
  drop_bot    same at the bottom (page numbers, footers)
  box         explicit (x0, y0, x1, y1) in page fractions, skipping detection
  pad         extra margin in points, default 6
  zoom        render scale, default 3.0
"""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
NOTES = os.path.normpath(os.path.join(HERE, "..", "..", "Notes"))

BB = "Notes by BB Sir"
CW = "Chapterwise"

SPECS = [
    # ---- chapter 1
    ("c1_elementary.png", BB + r"\Chapter 1.7 (Next).pdf", 2, {}),
    # no transformation-of-variable figure exists: BB 1.1 p18-19 are empty
    # slides (background rect only, no drawing, no image). Done as bullets.
    ("c1_freq_periodic.png", BB + r"\Chapter 1.1.pdf", 12, {"drop_top": 0.12}),
    ("c1_conv_shift.png", BB + r"\Chapter 3.pdf", 5, {"drop_top": 0.12}),
    ("c1_conv_graph.png", BB + r"\Chapter 3.pdf", 14, {"drop_top": 0.06}),
    ("c1_sampling_spectra.png", CW + r"\Chapter 2. Discrete Time Signals and Systems.pdf",
     43, {"drop_top": 0.05, "drop_bot": 0.08}),
    ("c1_sampling_rates.png", CW + r"\Chapter 2. Discrete Time Signals and Systems.pdf",
     45, {"drop_top": 0.05, "drop_bot": 0.10}),
]


def ink_box(page, drop_top=0.0, drop_bot=0.0):
    """Union of every drawing and image bbox on the page, minus the dropped bands."""
    r = page.rect
    lo = r.y0 + drop_top * r.height
    hi = r.y1 - drop_bot * r.height
    boxes = []
    for d in page.get_drawings():
        boxes.append(fitz.Rect(d["rect"]))
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") == 1:                   # image block
            boxes.append(fitz.Rect(blk["bbox"]))
    keep = [b for b in boxes
            if b.y1 > lo and b.y0 < hi and b.width > 2 and b.height > 2]
    if not keep:
        return None
    out = keep[0]
    for b in keep[1:]:
        out |= b
    out.y0 = max(out.y0, lo)
    out.y1 = min(out.y1, hi)
    return out


def cut(name, rel, pageno, opt):
    path = os.path.join(NOTES, rel)
    doc = fitz.open(path)
    page = doc[pageno - 1]
    r = page.rect
    if "box" in opt:
        x0, y0, x1, y1 = opt["box"]
        clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height,
                         r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    else:
        clip = ink_box(page, opt.get("drop_top", 0.0), opt.get("drop_bot", 0.0))
        if clip is None:
            print("   !! no ink found on %s p%d" % (rel, pageno))
            doc.close()
            return None
        pad = opt.get("pad", 6)
        clip = fitz.Rect(clip.x0 - pad, clip.y0 - pad, clip.x1 + pad, clip.y1 + pad)
        clip &= r
    pm = page.get_pixmap(clip=clip, dpi=int(72 * opt.get("zoom", 3.0)))
    os.makedirs(FIGS, exist_ok=True)
    out = os.path.join(FIGS, name)
    pm.save(out)
    print("   %-26s %4dx%-4d  %s p%d" % (name, pm.width, pm.height, rel, pageno))
    doc.close()
    return out


def sheet(paths, out):
    """Stack the crops into one PNG, scaled to a common width, for one-shot review."""
    pics = [fitz.Pixmap(p) for p in paths if p and os.path.exists(p)]
    if not pics:
        return
    W = 900
    scaled = []
    for p in pics:
        f = W / float(p.width)
        d = fitz.Document()
        pg = d.new_page(width=W, height=p.height * f)
        pg.insert_image(pg.rect, pixmap=p)
        scaled.append(d)
    H = int(sum(d[0].rect.height for d in scaled)) + 12 * len(scaled)
    doc = fitz.open()
    page = doc.new_page(width=W, height=H)
    y = 0.0
    for d, p in zip(scaled, paths):
        h = d[0].rect.height
        page.show_pdf_page(fitz.Rect(0, y, W, y + h), d, 0)
        page.insert_text((4, y + 10), os.path.basename(p), fontsize=9, color=(1, 0, 0))
        y += h + 12
    page.get_pixmap(dpi=96).save(out)
    print("contact sheet ->", out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want = args[0] if args else ""
    made = []
    for name, rel, pageno, opt in SPECS:
        if want and not name.startswith(want):
            continue
        made.append(cut(name, rel, pageno, opt))
    if "--sheet" in sys.argv:
        sheet(made, os.path.join(FIGS, "_sheet.png"))


if __name__ == "__main__":
    main()
