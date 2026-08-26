# -*- coding: utf-8 -*-
"""Crop figures out of the source lecture PDFs into figs/.

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

Run from this folder:  python figs.py [name ...]
"""
import fitz, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "Notes"))
FIGS = os.path.join(HERE, "figs")

AS = os.path.join(SRC, "Notes", "Notes by AS Sir")
SSD = os.path.join(SRC, "Notes", "Notes by SSD Sir")
SST = os.path.join(SRC, "Notes", "Notes by SST Sir")
BOOK = os.path.join(SRC, "Books", [f for f in os.listdir(os.path.join(SRC, "Books"))
                                   if f.endswith(".pdf")][0])

C2_SST = os.path.join(SST, "Chapter 2 Cellular Systems--Cellular Concepts.pdf")
C2_SSD = os.path.join(SSD, "Chapter 2 Cellular Systems--Cellular Concepts.pdf")
C3_SST = os.path.join(SST, "Chapter 3 Radio Propagation.pdf")
C3_SSD = os.path.join(SSD, "Chapter 3 Radio Propagation.pdf")
C3A1 = os.path.join(AS, "Chapter 3 Radio wave propagation Lecture 1.pdf")
C3A2 = os.path.join(AS, "Chapter 3 Radio wave propagation Lecture 2.pdf")
C3A3 = os.path.join(AS, "Chapter 3 Radio wave propagation Lecture 3.pdf")
C5_SST = os.path.join(SST, "Chapter 5 Equalization and Diversity Techiques.pdf")
C5_SSD = os.path.join(SSD, "Chapter 5 Equalization and Diversity Techiques.pdf")
C5_AS = os.path.join(AS, "Chapter 5 Equalization and Diversity techniques.pdf")
C6_SST = os.path.join(SST, "Chapter 6 Speech and channel coding fundamental.pdf")
C6_SST1 = os.path.join(SST, "Chapter 6_1 Channel Coding Introduction.pdf")
C6_SST2 = os.path.join(SST, "Chapter 6_2 Speech and Channel Coding Fundamental.pdf")
C6_SSD = os.path.join(SSD, "Chapter 6 Speech and channel coding fundamental.pdf")
C6_AS = os.path.join(AS, "Chapter 6 Channel and Source Coding technique.pdf")

JOBS = []


def add(name, pdf, page, box=None, pick=0, dpi=300, pad=0.004):
    JOBS.append(dict(name=name, pdf=pdf, page=page, box=box, pick=pick,
                     dpi=dpi, pad=pad))


# ------------------------------------------------------------------ chapter 2
add("c2_reuse_layout.png", C2_SST, 8)
add("c2_interf_tier.png", C2_SST, 11)
add("c2_ij_locate.png", C2_SST, 12, box=(0.465, 0.155, 0.978, 0.765))
add("c2_handoff_proper.png", C2_SST, 17)
add("c2_umbrella.png", C2_SST, 21)
add("c2_nearfar.png", C2_SST, 37, box=(0.067, 0.143, 0.894, 0.647))
add("c2_cell_splitting.png", C2_SST, 47, box=(0.400, 0.270, 0.990, 0.900))
add("c2_sectoring.png", C2_SST, 51, pick=1)
add("c2_sector_shapes.png", C2_SST, 51, pick=0)
add("c2_microcell_zone.png", C2_SST, 52)
add("c2_erlangb_table.png", C2_SST, 42, box=(0.02, 0.015, 0.985, 0.955))
# Rappaport 2e vector figures (pp. 24-71 of the scan carry a real text layer)
add("c2_cochannel_geom.png", BOOK, 39, box=(0.135, 0.125, 0.885, 0.565))
add("c2_sector_interf.png", BOOK, 59, box=(0.40, 0.45, 0.80, 0.815))

# ------------------------------------------------------------------ chapter 3
add("c3_tworay_geom.png", C3_SST, 15, box=(0.030, 0.335, 0.655, 0.815))
add("c3_tworay_images.png", C3_SSD, 19, box=(0.070, 0.368, 0.440, 0.739))
add("c3_knife_edge.png", C3_SST, 26)
add("c3_fresnel.png", C3_SST, 27, box=(0.047, 0.563, 0.639, 0.908))
add("c3_doppler.png", C3_SST, 40)
add("c3_pdp.png", C3_SSD, 64)
add("c3_rayleigh_pdf.png", C3_SST, 65, box=(0.06, 0.145, 0.95, 0.875))
add("c3_ricean_pdf.png", C3_SST, 69)
add("c3_pathloss_exp.png", C3_SST, 75)
add("c3_okumura_amu.png", C3_SST, 83, box=(0.075, 0.143, 0.487, 0.892))
add("c3_okumura_garea.png", C3_SST, 83, pick=1, pad=0.0)
add("c3_partition.png", C3_SST, 94, box=(0.055, 0.135, 0.985, 0.795))

# ------------------------------------------------------------------ chapter 5
add("c5_eq_block.png", C5_SST, 21)
add("c5_adaptive_eq.png", C5_SST, 24)
add("c5_eq_class.png", C5_AS, 15, box=(0.270, 0.090, 0.730, 0.880))
add("c5_lte.png", C5_SST, 31)
add("c5_ff_fb_taps.png", C5_SST, 32)
add("c5_lattice.png", C5_SST, 33)
add("c5_dfe.png", C5_SST, 35)
add("c5_mlse.png", C5_SSD, 43, box=(0.097, 0.167, 0.812, 0.612))
add("c5_space_div.png", C5_SST, 7)
add("c5_selection.png", C5_SSD, 9, box=(0.055, 0.167, 0.929, 0.876))
add("c5_scanning.png", C5_SST, 11, box=(0.264, 0.576, 0.760, 0.896))
add("c5_mrc.png", C5_SST, 12)
add("c5_egc.png", C5_SST, 13)
add("c5_polarization.png", C5_AS, 41, box=(0.285, 0.125, 0.735, 0.800))
add("c5_snr_div.png", C5_AS, 31, box=(0.185, 0.085, 0.620, 0.845))
add("c5_rake.png", C5_AS, 43, box=(0.300, 0.395, 1.000, 0.885))
add("c5_interleaver.png", C5_AS, 45, box=(0.050, 0.100, 0.680, 0.880))

# ------------------------------------------------------------------ chapter 6
add("c6_hierarchy.png", C6_AS, 3, box=(0.125, 0.100, 0.560, 0.875))
add("c6_speech_wave.png", C6_SST, 30, box=(0.100, 0.133, 0.852, 0.885))
add("c6_speech_gen.png", C6_SST, 29, box=(0.418, 0.260, 0.904, 0.871))
add("c6_subband.png", C6_AS, 12, box=(0.180, 0.095, 0.905, 0.905))
add("c6_chvoc_ana.png", C6_SST, 33, box=(0.075, 0.070, 0.985, 0.900))
add("c6_chvoc_syn.png", C6_SST, 35, box=(0.075, 0.070, 0.995, 0.900))
add("c6_formants.png", C6_SST, 37, box=(0.289, 0.427, 0.661, 0.735))
add("c6_formant_ana.png", C6_SST, 40, box=(0.065, 0.095, 0.985, 0.900))
add("c6_formant_syn.png", C6_SST, 41, box=(0.095, 0.095, 0.985, 0.880))
add("c6_lpc.png", C6_AS, 24, box=(0.235, 0.095, 0.845, 0.855))
add("c6_relp.png", C6_AS, 28, box=(0.065, 0.085, 0.855, 0.885))
add("c6_gsm_codec.png", C6_AS, 34, box=(0.085, 0.085, 0.925, 0.900))
add("c6_hamming_struct.png", C6_SST1, 11, box=(0.058, 0.411, 0.625, 0.745))
add("c6_conv_enc.png", C6_SST1, 21, box=(0.067, 0.354, 0.476, 0.889))
add("c6_code_tree.png", C6_SST1, 22, box=(0.130, 0.489, 0.699, 0.860))
add("c6_trellis.png", C6_SST1, 23, box=(0.058, 0.585, 0.890, 0.989))
add("c6_viterbi.png", C6_SST1, 25, box=(0.050, 0.078, 1.000, 0.905))
add("c6_turbo.png", C6_SST, 17, box=(0.051, 0.290, 0.496, 0.762))


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


def main():
    os.makedirs(FIGS, exist_ok=True)
    want = set(a.replace(".png", "") for a in sys.argv[1:])
    for job in JOBS:
        if want and job["name"].replace(".png", "") not in want:
            continue
        d = fitz.open(job["pdf"])
        pg = d[job["page"] - 1]
        clip = rect_for(pg, job)
        pm = pg.get_pixmap(dpi=job["dpi"], clip=clip)
        pm.save(os.path.join(FIGS, job["name"]))
        print(f"{job['name']:30s} {pm.width:5d}x{pm.height:<5d} "
              f"<- {os.path.basename(job['pdf'])[:38]} p{job['page']}")
        d.close()


if __name__ == "__main__":
    main()
