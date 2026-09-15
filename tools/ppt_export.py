# -*- coding: utf-8 -*-
"""Export a legacy .ppt deck to PDF with PowerPoint COM, then dump its text.

    python tools/ppt_export.py "DSAP/Notes/SPP Sir Slides/DSAP_Sanjeeb_7(DFT).ppt"
    python tools/ppt_export.py "DSAP/Notes/SPP Sir Slides"        # every .ppt

The SPP Sir decks are the only source in DSAP that maps 1:1 onto the CT 704
chapters, and they are .ppt, which nothing in this repo can read directly.
PowerPoint COM opens them and saves a PDF next to the original; from there
notes_text_dump.py (or a one-line fitz call) gets the text layer for free.

This had been done by hand three times, for decks 4, 6 and then 7 and 8.
Writing it down so the fourth time costs nothing.

Skips a deck whose .pdf already exists and is newer than the .ppt.
Needs PowerPoint installed; it is a no-op on any other machine.
"""
import os
import sys

FMT_PDF = 32                     # ppSaveAsPDF


def export(path, force=False):
    """Save <deck>.ppt as <deck>.pdf. Returns the pdf path, or None."""
    path = os.path.abspath(path)
    pdf = os.path.splitext(path)[0] + ".pdf"
    if not force and os.path.exists(pdf) and \
            os.path.getmtime(pdf) >= os.path.getmtime(path):
        print("   up to date   %s" % os.path.basename(pdf))
        return pdf

    import win32com.client                      # pywin32
    app = win32com.client.Dispatch("PowerPoint.Application")
    deck = None
    try:
        # WithWindow=False fails on some builds; open visible and close fast
        deck = app.Presentations.Open(path, WithWindow=False)
        deck.SaveAs(pdf, FMT_PDF)
        print("   exported     %s  (%d slides)" %
              (os.path.basename(pdf), deck.Slides.Count))
    finally:
        if deck is not None:
            deck.Close()
        app.Quit()
    return pdf


def dump_text(pdf, out_dir):
    """Write the PDF's text layer to <out_dir>/<name>.txt, page-marked the
    way notes_text_dump.py does, so both sets read alike."""
    import fitz
    doc = fitz.open(pdf)
    name = os.path.splitext(os.path.basename(pdf))[0]
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "SPP Sir Slides -- %s.txt" % name)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("SPP Sir Slides\\%s.pdf\n%d pages\n\n" % (name, doc.page_count))
        for i, page in enumerate(doc, 1):
            fh.write("=== p%d ===\n" % i)
            fh.write(page.get_text("text", sort=True))
            fh.write("\n")
    doc.close()
    print("   text         %s" % os.path.basename(out))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    force = "--force" in sys.argv
    target = args[0]
    decks = []
    if os.path.isdir(target):
        for fn in sorted(os.listdir(target)):
            if fn.lower().endswith(".ppt"):
                decks.append(os.path.join(target, fn))
    else:
        decks.append(target)

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(here, "DSAP", "ocr", "notes_text")
    for d in decks:
        print(os.path.basename(d))
        pdf = export(d, force)
        if pdf:
            dump_text(pdf, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
