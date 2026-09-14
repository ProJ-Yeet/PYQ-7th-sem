# -*- coding: utf-8 -*-
"""Dump the machine text layer of every notes PDF that has one.

    python tools/notes_text_dump.py <Subject>

Writes one .txt per source PDF into <Subject>/ocr/notes_text/, mirroring the
folder names with " -- " separators, with a "=== p<N> ===" marker per page.
Files whose text layer is missing or useless are skipped and listed instead --
those are the ones that need tools/ocr_page.py, or eyes, and the point of this
tool is to shrink that list to the pages that really need it.

Free compared with OCR or rendering: PyMuPDF get_text only reads what the PDF
already carries. See golden rule 2 in CLAUDE.md.
"""
import io
import os
import re
import sys

import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def useful(doc):
    """Fraction of sampled pages carrying real text."""
    n = len(doc)
    idx = sorted(set(int(i * (n - 1) / 11) for i in range(12))) if n > 1 else [0]
    hit = sum(1 for i in idx if len(doc[i].get_text().strip()) > 40)
    return hit / float(len(idx))


def main():
    subject = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    src = os.path.join(ROOT, subject, "Notes")
    dst = os.path.join(ROOT, subject, "ocr", "notes_text")
    if not os.path.isdir(src):
        sys.exit("no such folder: " + src)
    os.makedirs(dst, exist_ok=True)

    wrote, skipped = [], []
    for dp, dn, fn in os.walk(src):
        for f in sorted(fn):
            if not f.lower().endswith(".pdf"):
                continue
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, src)
            doc = fitz.open(path)
            if useful(doc) < 0.5:
                skipped.append((rel, len(doc)))
                doc.close()
                continue
            name = rel.replace(os.sep, " -- ")[:-4] + ".txt"
            out = [rel, "%d pages" % len(doc), ""]
            for i, page in enumerate(doc):
                t = page.get_text("text", sort=True)
                t = re.sub(r"[ \t]+\n", "\n", t)
                t = re.sub(r"\n{3,}", "\n\n", t).strip()
                out.append("=== p%d ===" % (i + 1))
                out.append(t)
            io.open(os.path.join(dst, name), "w", encoding="utf-8",
                    newline="\n").write("\n".join(out) + "\n")
            wrote.append((name, len(doc)))
            doc.close()

    print("wrote %d files (%d pages) to %s" %
          (len(wrote), sum(n for _, n in wrote), os.path.relpath(dst, ROOT)))
    for n, p in wrote:
        print("   %4dpp  %s" % (p, n))
    print("\nNO USABLE TEXT LAYER -- %d files, %d pages, need OCR or eyes:" %
          (len(skipped), sum(n for _, n in skipped)))
    for n, p in skipped:
        print("   %4dpp  %s" % (p, n))


if __name__ == "__main__":
    main()
