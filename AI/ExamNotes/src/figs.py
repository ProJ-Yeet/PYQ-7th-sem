# -*- coding: utf-8 -*-
"""Crop figures out of the source lecture PDFs and the textbook into figs/.

House rule: never redraw a figure. Clip it from the source page and trim the
watermark / footer strip.

Two ways to say where the figure is:

  add(name, pdf, page)                 -> largest EMBEDDED RASTER on that page.
                                          Most slide decks paste figures as
                                          images, so this is exact and is the
                                          default. `pick=n` takes the n-th
                                          largest instead.
  add(name, pdf, page, box=(a,b,c,d))  -> manual clip, page-size fractions.
                                          Needed for vector drawings and for
                                          scanned pages (whole page is one
                                          image).

  add(name, pdf, page, flat=True, ...) -> rebuild the page from its embedded
                                          images instead of letting PyMuPDF
                                          render it. Needed where a deck's
                                          figures are 8-bit /Indexed images
                                          over an ICCBased base: PyMuPDF drops
                                          the palette and a normal render gives
                                          a SOLID BLACK BOX. Decoding the index
                                          stream through the lookup table by
                                          hand recovers them exactly.

INSIGHTS IS A TWO-PAGE SPREAD PER PDF PAGE. A box on it must stay inside one
half: x < 0.5 is the LEFT (even) book page, x > 0.5 the RIGHT (odd) one. Use
ins() and give it the PRINTED book page; it works the PDF page out, including
the one spread the scan skips (book pp.96-97 are not in the file).

Run from this folder:  python figs.py [name ...]
"""
import fitz, io, os, re, sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "Notes"))
FIGS = os.path.join(HERE, "figs")

BA = os.path.join(SRC, "Notes by BA Sir")
BJ = os.path.join(SRC, "Notes by BJ Sir")
PS = os.path.join(SRC, "Notes by PS Sir")
SG = os.path.join(SRC, "Notes by SG sir")
IOE = os.path.join(SRC, "Notes by ioe_notes")
IIT = os.path.join(SRC, "Notes by IIT Kharagpur")
MISC = os.path.join(SRC, "Misc")

# "Insights on Artificial Intelligence" -- Shrestha, Giri, Joshi, Dahal.
# The student's chosen method authority for worked problems. Two-page spread.
INS = os.path.join(SRC, "Insights ArtificialIntelligence.pdf")

BA1 = os.path.join(BA, "CH-01 AI.pdf")
BA2 = os.path.join(BA, "CH-02 AI.pdf")
BA3 = os.path.join(BA, "CH-03 AI.pdf")
BA4 = os.path.join(BA, "CH-04 AI.pdf")
BA5 = os.path.join(BA, "CH-05 Structured Knowledge Representation.pdf")
BA6 = os.path.join(BA, "CH-06 Machine Learning.pdf")
BA7 = os.path.join(BA, "CH-07 Applications of AI.pdf")

PS1 = os.path.join(PS, "1. Introduction_old_syllabus.pdf")
PS2 = os.path.join(PS, "2.Problem Solving_old_syllabus.pdf")

CSIT = os.path.join(MISC, "AI (Detailed) for CSIT.pdf")

JOBS = []


def add(name, pdf, page, box=None, pick=0, dpi=300, pad=0.004, flat=False):
    JOBS.append(dict(name=name, pdf=pdf, page=page, box=box, pick=pick,
                     dpi=dpi, pad=pad, flat=flat))


def ins_pdf_page(book):
    """PDF page holding a given Insights book page.

    Two book pages per PDF page, left half even and right half odd. But the
    scan SKIPS ONE SPREAD: pdf p50 holds book pp.94-95 and pdf p51 holds book
    pp.98-99, so book pages 96 and 97 do not exist in this file at all. The
    offset therefore drops by one PDF page from book 98 on. Verified against
    the printed folios, which is also how AI/ocr/notes_text/insights/ is
    numbered.
    """
    if book in (96, 97):
        raise SystemExit("Insights book pp.96-97 are missing from the scan")
    off = 6 if book < 96 else 4
    return (book + off) // 2 if book % 2 == 0 else (book + off - 1) // 2


def ins(name, book, box, dpi=320):
    """A figure on one half of an Insights spread. `box` is in HALF-PAGE
    fractions (0-1 across that half), so a figure is placed the same way
    whether it sits on a left or a right book page."""
    pdf_page = ins_pdf_page(book)
    left = (book % 2 == 0)
    x0 = (box[0] * 0.5) if left else (0.5 + box[0] * 0.5)
    x1 = (box[2] * 0.5) if left else (0.5 + box[2] * 0.5)
    add(name, INS, pdf_page, box=(x0, box[1], x1, box[3]), dpi=dpi)


# ------------------------------------------------------------------ chapter 1
# The agent block diagrams, asked in 7 papers as "explain the types of
# intelligent agent". Insights has them too (Fig 1.2-1.7, book pp.22-27) but
# it is a photographed book page: curved, shadowed, and it omits the LEARNING
# agent, which \bo{75 Bh} asks for by name. BJ Sir's deck pastes each one as a
# single clean raster, one per slide, learning agent included -- so these come
# from there. Default mode (largest embedded raster) is exact here.
BJ1 = os.path.join(BJ, "Chapter1_Artificial_Intelligence.pdf")
add("c1_agent_table.png", BJ1, 63)
add("c1_agent_reflex.png", BJ1, 64)
add("c1_agent_model.png", BJ1, 65)
add("c1_agent_goal.png", BJ1, 66)
add("c1_agent_learning.png", BJ1, 67)
# the utility-based agent is the one type BJ Sir does not paste, so it comes
# from Insights instead.
add("c1_agent_env.png", BJ1, 54, pick=0)
add("c1_vacuum_world.png", BJ1, 55)
ins("c1_agent_utility.png", 27, (0.06, 0.04, 0.97, 0.36))


# ------------------------------------------------------------------ chapter 3
BA3 = os.path.join(BA, "CH-03 AI.pdf")
# The objective-function-vs-state-space landscape: global maximum, local
# maximum, shoulder, plateau, flat local maximum, ridge, all labelled on one
# curve. It is the answer to "problems associated with hill climbing" (6
# papers) in a single picture. BA Sir's deck is 4 slides to a page, so this is
# a manual box inside the top-left quadrant.
add("c3_hill_landscape.png", BA3, 10, box=(0.268, 0.329, 0.480, 0.459))
add("c3_hill_contour.png", BA3, 10, box=(0.325, 0.148, 0.425, 0.245))

# The five question figures the papers print. These were cropped out of the
# scanned papers for the Sorted PYQ document and are reused here so each
# `asked` block shows the graph or tree the student is actually given.
for _n in ("ai_81ch_astar", "ai_80ch_astar", "ai_76bh_bfs",
           "ai_79ch_minmax", "ai_76ba_minmax"):
    JOBS.append(dict(name="c3_" + _n[3:] + ".png", pdf=None, page=None,
                     box=None, pick=0, dpi=0, pad=0, flat=False,
                     copy=os.path.join(HERE, "..", "..", "images", _n + ".png")))


def rect_for(pg, job):
    r = pg.rect
    if job["box"]:
        b = job["box"]
        return fitz.Rect(r.x0 + b[0] * r.width, r.y0 + b[1] * r.height,
                         r.x0 + b[2] * r.width, r.y0 + b[3] * r.height)
    rects = []
    for im in pg.get_images(full=True):
        for rr in pg.get_image_rects(im[0]):
            rects.append(rr)
    if not rects:
        raise SystemExit(f"{job['name']}: no embedded image on page {job['page']}")
    rects.sort(key=lambda x: -(x.width * x.height))
    rr = rects[job["pick"]]
    p = job["pad"]
    return fitz.Rect(max(r.x0, rr.x0 - p * r.width), max(r.y0, rr.y0 - p * r.height),
                     min(r.x1, rr.x1 + p * r.width), min(r.y1, rr.y1 + p * r.height))


_IDX = re.compile(r"/ColorSpace\[/Indexed \d+ 0 R (\d+) (\d+) 0 R\]")


def _pil(doc, xref):
    """One embedded image as RGB, applying an /Indexed palette by hand."""
    obj = doc.xref_object(xref, compressed=True)
    m = _IDX.search(obj)
    if m:
        w = int(re.search(r"/Width (\d+)", obj).group(1))
        h = int(re.search(r"/Height (\d+)", obj).group(1))
        idx = doc.xref_stream(xref)[:w * h].ljust(w * h, b"\x00")
        im = Image.frombytes("P", (w, h), idx)
        im.putpalette(doc.xref_stream(int(m.group(2))))
        return im.convert("RGB")
    return Image.open(io.BytesIO(doc.extract_image(xref)["image"])).convert("RGB")


def flat_page(doc, pg, dpi):
    """Rebuild a page from its embedded images, at their own page rects.
    Only the images are drawn -- any vector overlay or text on the slide is
    lost. That is fine for the decks this is needed for, where the figure IS
    a single pasted bitmap.
    """
    r = pg.rect
    s = dpi / 72.0
    canvas = Image.new("RGB", (round(r.width * s), round(r.height * s)), "white")
    for im in pg.get_images(full=True):
        xref = im[0]
        try:
            src = _pil(doc, xref)
        except Exception:
            continue
        for rr in pg.get_image_rects(xref):
            w, h = round(rr.width * s), round(rr.height * s)
            if w < 2 or h < 2:
                continue
            canvas.paste(src.resize((w, h), Image.LANCZOS),
                         (round((rr.x0 - r.x0) * s), round((rr.y0 - r.y0) * s)))
    return canvas


# A figure is placed at most \textwidth wide, about 6.6 in. At 300 dpi that is
# 2000 px, and anything past that is weight in the repo for no visible gain --
# these crops came out at 3800-5000 px and 1.5 MB each. Cap the long edge, then
# palette-quantise: line diagrams and scanned book pages carry few real colours,
# and 8-bit indexed PNG is 5-10x smaller than RGB with no visible loss.
MAXEDGE = 1800
QCOLORS = 128


def shrink(img):
    if max(img.size) > MAXEDGE:
        s = MAXEDGE / float(max(img.size))
        img = img.resize((max(1, round(img.width * s)),
                          max(1, round(img.height * s))), Image.LANCZOS)
    q = img.convert("RGB").quantize(colors=QCOLORS, method=Image.MEDIANCUT,
                                    dither=Image.Dither.NONE)
    return q


def main():
    os.makedirs(FIGS, exist_ok=True)
    want = set(a.replace(".png", "") for a in sys.argv[1:])
    for job in JOBS:
        if want and job["name"].replace(".png", "") not in want:
            continue
        # a figure already cropped for the Sorted PYQ document: take it as is,
        # through the same size cap so the whole folder obeys one policy
        if job.get("copy"):
            out = os.path.join(FIGS, job["name"])
            img = shrink(Image.open(job["copy"]).convert("RGB"))
            img.save(out, optimize=True)
            print("%-30s %5dx%-5d %7.0f kB <- images/%s"
                  % (job["name"], img.size[0], img.size[1],
                     os.path.getsize(out) / 1024.0,
                     os.path.basename(job["copy"])))
            continue
        d = fitz.open(job["pdf"])
        pg = d[job["page"] - 1]
        clip = rect_for(pg, job)
        out = os.path.join(FIGS, job["name"])
        if job["flat"]:
            s = job["dpi"] / 72.0
            r = pg.rect
            img = flat_page(d, pg, job["dpi"]).crop(
                (round((clip.x0 - r.x0) * s), round((clip.y0 - r.y0) * s),
                 round((clip.x1 - r.x0) * s), round((clip.y1 - r.y0) * s)))
        else:
            pm = pg.get_pixmap(dpi=job["dpi"], clip=clip)
            img = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
        img = shrink(img)
        img.save(out, optimize=True)
        w, h = img.size
        kb = os.path.getsize(out) / 1024.0
        print(f"{job['name']:30s} {w:5d}x{h:<5d} {kb:7.0f} kB "
              f"<- {os.path.basename(job['pdf'])[:34]} p{job['page']}")
        d.close()


if __name__ == "__main__":
    main()
