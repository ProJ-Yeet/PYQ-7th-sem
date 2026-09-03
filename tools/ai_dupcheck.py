# -*- coding: utf-8 -*-
"""Cross-check a new-scan page against the paper already in the old OCR archive.

For each (old-archive heading, new-scan page) pair, take the old archive's
question stems, reduce them to a bag of lower-case alphanumeric words, and
report what fraction of those words appear in the new page's raw OCR text.

A score near 1.0 means the same paper. A low score means the page index lied
and the two are different papers.

    python tools/ai_dupcheck.py
"""
import io
import os
import re

ARCHIVE = "AI/ocr/CT-653_CT-710_OCR.md"
RAW = "ocr_raw/ai"

# old-archive page  ->  new-scan page
PAIRS = [
    ("p1", 48), ("p2", 47), ("p3", 46), ("p4", 45), ("p5", 44), ("p6", 43),
    ("p7", 42), ("p8", 41), ("p9", 40), ("p10", 39), ("p11", 38), ("p12", 37),
    ("p13", 26), ("p14", 16), ("p15", 15), ("p16", 17), ("p17", 18),
]


def archive_sections():
    text = io.open(ARCHIVE, encoding="utf-8").read()
    out = {}
    parts = re.split(r"^## (p\d+)[^\n]*$", text, flags=re.M)
    for i in range(1, len(parts), 2):
        out[parts[i]] = parts[i + 1]
    return out


def words(s):
    return set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3)


def main():
    secs = archive_sections()
    for old, new in PAIRS:
        body = secs.get(old, "")
        path = os.path.join(RAW, "p%d.txt" % new)
        if not body or not os.path.exists(path):
            print("%-4s -> p%-3d  MISSING" % (old, new))
            continue
        raw = io.open(path, encoding="utf-8").read()
        a, b = words(body), words(raw)
        if not a:
            continue
        score = len(a & b) / float(len(a))
        flag = "" if score >= 0.60 else "   <-- CHECK"
        missing = sorted(a - b)[:8]
        print("%-4s -> p%-3d  %.2f%s  %s" % (old, new, score, flag, " ".join(missing)))


if __name__ == "__main__":
    main()
