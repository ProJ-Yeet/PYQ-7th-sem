# -*- coding: utf-8 -*-
"""Audit the built PDFs for topics torn across a page boundary.

Run from inside this src\\ folder:   python audit.py [gap-threshold]
Reads the deployed PDFs one level up, in ExamNotes\\.

Two separate defects, and they need different fixes:

  STRANDED  the last thing on a page is a topic band, a question heading or
            a year-tag line, so the answer it introduces sits overleaf.
            This is a BUG. It means a breakpoint is open somewhere between
            the band and the first block of the answer -- see the
            keeping-a-topic-whole note in preamble.tex.

  GAP       the ink stops well above the bottom margin. This is NOT a bug
            on its own: a \\sbs pair is an unbreakable box, so a topic that
            does not fit is moved whole rather than being torn, and the
            blank space is the price. A big one is still worth a look --
            the fix is to split that topic's pair at a \\lead boundary so
            half stays on the page and half flows over.

Classify by how a line is set, not by what it says: a gray footnotesize line
on its own is a figure CAPTION, and only counts as a year-tag when a heading
or a band sits directly above it. Without that rule the report is mostly
false positives.
"""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

MARG = 1.35 * 28.3465          # top and bottom margin, pt (see geometry)
SUB = 0x6B7785                 # muted meta text
ACC = 0x2563A8                 # accent: bands and sub-headings


def classify(spans):
    """What kind of line is this, judged by how it is set."""
    if not spans:
        return ""
    size = max(s["size"] for s in spans)
    colours = {s["color"] for s in spans}
    bold = any("Bold" in s["font"] or "Black" in s["font"] for s in spans)
    if colours <= {SUB} and size < 9:
        return "TAG"
    if bold and size > 10.5:
        return "HEADING"
    if bold and colours <= {ACC}:
        return "BAND"
    return ""


def audit(path, cut):
    doc = fitz.open(path)
    rows = []
    tops = {}
    for i, page in enumerate(doc):
        floor = MARG + 6                       # below the running header
        bottom = 0.0
        lines = []
        for blk in page.get_text("dict")["blocks"]:
            if blk["type"] != 0:               # an image block
                bottom = max(bottom, blk["bbox"][3])
                continue
            for ln in blk["lines"]:
                if ln["bbox"][3] < floor:
                    continue
                if not "".join(s["text"] for s in ln["spans"]).strip():
                    continue
                lines.append((ln["bbox"][3], ln["spans"]))
                bottom = max(bottom, ln["bbox"][3])
        for drawing in page.get_drawings():
            r = drawing["rect"]
            if r.y1 < floor or r.height > page.rect.height * 0.9:
                continue
            bottom = max(bottom, r.y1)
        for img in page.get_images():
            for r in page.get_image_rects(img[0]):
                bottom = max(bottom, r.y1)

        lines.sort(key=lambda t: t[0])
        tops[i] = [" ".join(s["text"] for s in sp)
                   for _, sp in sorted(lines, key=lambda t: t[0])[:2]]
        kinds = [classify(sp) for _, sp in lines[-4:]]
        kind = ""
        if kinds:
            if kinds[-1] in ("HEADING", "BAND"):
                kind = "STRANDED:" + kinds[-1]
            elif kinds[-1] == "TAG" and any(
                    k in ("HEADING", "BAND") for k in kinds[:-1]):
                kind = "STRANDED:TAG"
        gap = ((page.rect.height - MARG) - bottom) / (page.rect.height - 2 * MARG)
        # the last page of a document is meant to end early
        if kind or (gap > cut and i < doc.page_count - 1):
            rows.append((kind, gap, i + 1, doc.page_count))
    out = [(k, g, p, n, tops.get(p, [])) for k, g, p, n in rows]
    doc.close()
    return out


def main():
    # the console here is cp1252; a topic line carrying a math glyph such as
    # <= used to crash the report after printing most of it
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    cut = float(sys.argv[1]) if len(sys.argv) > 1 else 0.33
    stranded, gaps = [], []
    for fn in sorted(os.listdir(OUT)):
        if not fn.lower().endswith(".pdf"):
            continue
        for kind, gap, pg, n, top in audit(os.path.join(OUT, fn), cut):
            name = fn.split(" - ")[0]
            (stranded if kind else gaps).append((gap, name, pg, n, kind, top))

    if stranded:
        print("STRANDED HEADINGS -- these are bugs:")
        for gap, name, pg, n, kind, top in sorted(stranded, reverse=True):
            print(f"  {gap*100:5.1f}%  {name:<8} p{pg}/{n}  {kind}")
    else:
        print("no stranded headings")

    print(f"\npages ending more than {cut*100:.0f}% short "
          f"(the topic named is the one that would not fit):")
    for gap, name, pg, n, _, top in sorted(gaps, reverse=True):
        print(f"  {gap*100:5.1f}%  {name:<8} p{pg}/{n}  -> "
              + " / ".join(t[:44] for t in top))
    print(f"\n{len(stranded)} stranded, {len(gaps)} short pages")
    return 1 if stranded else 0


if __name__ == "__main__":
    sys.exit(main())
