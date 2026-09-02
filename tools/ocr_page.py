# -*- coding: utf-8 -*-
"""Local OCR for the scanned question papers — no vision tokens.

Renders a page of a source PDF and runs RapidOCR (ONNX, CPU, no system binary)
over it, emitting plain text in reading order. Reading that text costs ordinary
text tokens instead of the ~1.5-3k image tokens a rendered page costs.

    python tools/ocr_page.py "New PYQ/RF.pdf" 9
    python tools/ocr_page.py "New PYQ/AI.pdf" 19 --zoom 3.0
    python tools/ocr_page.py "New PYQ/AI.pdf" 19-26 --out ocr_raw/ai

Notes
-----
* Accuracy is good on clean body text and poor on the marks column, on
  S-parameter subscripts and on faint scans. Treat the output as a DRAFT:
  transcribe from it, then image-verify only the bands it got wrong
  (`--crop y0 y1` renders just that band for a vision read).
* `--layout` keeps the raw boxes so a right-hand marks column can be
  separated from the body text by x-coordinate.
"""
import argparse
import io
import os
import re
import sys

import fitz

_ENGINE = None


def engine():
    global _ENGINE
    if _ENGINE is None:
        from rapidocr_onnxruntime import RapidOCR
        _ENGINE = RapidOCR()
    return _ENGINE


def render(src, page_no, zoom, y0=0.0, y1=1.0):
    doc = fitz.open(src)
    page = doc[page_no - 1]
    rect = page.rect
    clip = fitz.Rect(0, rect.height * y0, rect.width, rect.height * y1)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
    return pix.tobytes("png")


def ocr(png_bytes, layout=False):
    import numpy as np
    from PIL import Image
    img = np.array(Image.open(io.BytesIO(png_bytes)).convert("RGB"))
    result, _ = engine()(img)
    if not result:
        return "" if not layout else []
    boxes = []
    for box, text, score in result:
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        boxes.append({
            "x0": min(xs), "x1": max(xs),
            "y0": min(ys), "y1": max(ys),
            "cy": sum(ys) / len(ys),
            "text": text, "score": score,
        })
    boxes.sort(key=lambda b: (b["cy"], b["x0"]))
    if layout:
        return boxes
    return reflow(boxes)


def reflow(boxes, line_tol=12):
    """Group boxes into visual lines, then join each line left-to-right."""
    lines, cur, cur_y = [], [], None
    for b in boxes:
        if cur_y is None or abs(b["cy"] - cur_y) <= line_tol:
            cur.append(b)
            cur_y = b["cy"] if cur_y is None else (cur_y + b["cy"]) / 2
        else:
            lines.append(cur)
            cur, cur_y = [b], b["cy"]
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:
        ln.sort(key=lambda b: b["x0"])
        out.append(" ".join(b["text"] for b in ln))
    return "\n".join(out)


def parse_pages(spec):
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a), int(b) + 1))
        else:
            pages.append(int(part))
    return pages


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("pages", help='e.g. "9", "9,11", "19-26"')
    ap.add_argument("--zoom", type=float, default=2.6)
    ap.add_argument("--crop", nargs=2, type=float, metavar=("Y0", "Y1"),
                    default=[0.0, 1.0], help="vertical slice as page fractions")
    ap.add_argument("--layout", action="store_true",
                    help="print x/y boxes instead of reflowed text")
    ap.add_argument("--out", help="write <out>/p<N>.txt per page instead of stdout")
    args = ap.parse_args()

    if args.out:
        os.makedirs(args.out, exist_ok=True)

    for n in parse_pages(args.pages):
        png = render(args.src, n, args.zoom, args.crop[0], args.crop[1])
        if args.layout:
            body = "\n".join(
                "x=%6.0f-%6.0f y=%6.0f  %s" % (b["x0"], b["x1"], b["cy"], b["text"])
                for b in ocr(png, layout=True))
        else:
            body = ocr(png)
        header = "===== %s p%d =====" % (os.path.basename(args.src), n)
        if args.out:
            path = os.path.join(args.out, "p%d.txt" % n)
            with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(header + "\n" + body + "\n")
            print("wrote", path, "(%d chars)" % len(body))
        else:
            print(header)
            print(body)


if __name__ == "__main__":
    main()
