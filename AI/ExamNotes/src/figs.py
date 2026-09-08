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

from PIL import Image, ImageDraw

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


def add(name, pdf, page, box=None, pick=0, dpi=300, pad=0.004, flat=False,
        mask=None):
    """`mask` paints rectangles of the finished crop white.

    For stray text baked INTO a pasted raster, which no box can remove: a
    slide author screenshots a figure together with the line above it, so the
    text sits in a corner the figure itself does not use. Rectangles are
    fractions of the cropped image, (x0, y0, x1, y1). Only ever use it on
    empty corners -- it is the "trim the watermark strip" rule, not a licence
    to edit a figure.
    """
    JOBS.append(dict(name=name, pdf=pdf, page=page, box=box, pick=pick,
                     dpi=dpi, pad=pad, flat=flat, mask=mask))


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


# ------------------------------------------------------------------ chapter 4
# BA Sir's CH-04 deck is 4 slides to a page, so every box here is a manual
# clip inside one quadrant. The deck pastes each figure as its own raster but
# several quadrants carry two, so the largest-raster default picks the wrong
# one -- boxes it is.
# The resolution refutation cascade for the Colonel West premises: the exact
# shape the answer to 33 of the 41 papers has to take.
add("c4_res_graph.png", BA4, 9, box=(0.085, 0.628, 0.462, 0.900))
# Backward chaining as a proof tree (Russell & Norvig fig 9.7), with the KB
# clauses and the goal beside it.
add("c4_bwd_chain.png", BA4, 11, box=(0.196, 0.210, 0.452, 0.455))
# Bayes' theorem with every term named: likelihood, prior, posterior,
# marginalisation. Five papers ask the theorem itself before the numerical.
add("c4_bayes_anatomy.png", BA4, 11, box=(0.532, 0.213, 0.918, 0.438))
# The alarm network, the standard belief-network example. The whole slide, not just
# the graph: the CPT boxes sit ON the graph and the joint-probability worked example
# beside it is the calculation the caption quotes. Cropping tighter cuts a line of it.
add("c4_bbn_alarm.png", BA4, 12, box=(0.528, 0.268, 0.918, 0.472))
# A causal network proper: Cloudy -> Sprinkler / Rain -> WetGrass. Same shape
# as the network 78 Ba prints, so it reads as a rehearsal for that question.
add("c4_causal_net.png", BA4, 12, box=(0.138, 0.694, 0.283, 0.845))
# Forward chaining drawn the way Insights draws it: facts on the bottom row,
# each iteration adding a row above until the goal appears.
ins("c4_fwd_chain.png", 119, (0.00, 0.313, 1.00, 0.566))
# The Bayesian network 78 Ba prints with its question, reused from the crop
# already made for the Sorted PYQ document.
JOBS.append(dict(name="c4_78ba_bbn.png", pdf=None, page=None, box=None,
                 pick=0, dpi=0, pad=0, flat=False,
                 copy=os.path.join(HERE, "..", "..", "images", "ai_78ba_bbn.png")))


# ------------------------------------------------------------------ chapter 5
# BA Sir's CH-05 is ONE slide per page (unlike CH-04, which is four to a page),
# and every figure on it is pasted as a single embedded raster, so the
# largest-raster default is exact here and no boxes are needed.
PS5 = os.path.join(PS, "5.Structured Knowledge Representation_old_syllabus.pdf")
BJ5 = os.path.join(BJ, "AI_Chapter5_new.pdf")

# The semantic net for the Tom-the-cat sentence set. This one figure IS the
# published answer to three papers (79 Bh, 82 Bh, 81 Ch) and to Insights
# Example 5.2, and BA Sir's is the cleanest drawing of it anywhere in Notes\.
# The pasted raster includes the slide line above it ("...represent the
# data:"), which sits in an empty top-left corner of the figure. Masked.
add("c5_semnet_tom.png", BA5, 11, mask=[(0.0, 0.0, 0.47, 0.055)])
# isa Vs instance-of on one small net (bird / robin / Clyde / nest-1). The
# distinction is what the papers mean by "the two commonly used links".
add("c5_isa_instance.png", BA5, 10)
# A frame description of a hotel room: four frames, each with slots, linked by
# their own slot values. The only figure in Notes\ that shows frames POINTING
# AT each other, which is the whole difference from a slot table.
add("c5_frame_hotel.png", BA5, 13, box=(0.497, 0.196, 0.985, 0.874))
# Conceptual dependency worked on seven sentences in the arrow notation. The
# notation cannot be typeset, so it has to be the picture.
add("c5_cd_examples.png", BA5, 18)
# The restaurant script in CD form, scenes 2 then 3-4.
add("c5_script_rest1.png", BA5, 23)
add("c5_script_rest2.png", BA5, 24)

# PS Sir's deck is 720x540 with the figures placed as rasters over a blue
# footer wave, so these are boxes taken from the rasters' own page rectangles.
# The canonical semantic net (Rich & Knight fig 9.1): Pee-Wee-Reese, with the
# four FOPL predicates printed under it. Every "convert these sentences into a
# semantic network" question in the papers is a redressing of this figure.
add("c5_semnet_peewee.png", PS5, 27, box=(0.016, 0.185, 0.990, 0.835))
# The same net redressed for Sakti Gauchan, which is what 72 Ma and 78 Po ask
# for almost word for word.
add("c5_semnet_sakti.png", PS5, 34, box=(0.130, 0.530, 0.898, 0.905))
# An EVENT node: "John gave the book to Mary" cannot be drawn with binary
# links, so the give-event becomes a node (EV7) with agent / object /
# beneficiary arcs. This is the answer to "how do you represent a three-place
# predicate in a net".
add("c5_semnet_event.png", PS5, 29, box=(0.212, 0.172, 0.885, 0.782))
# The bird / robin / wing hierarchy, the shape 77 Ch's Tweety-Sweety set takes.
add("c5_semnet_bird.png", PS5, 32, box=(0.532, 0.213, 0.878, 0.782))
# A frame system and its first-order-logic translation, side by side in one
# figure: the answer to 75 Ba ("provide examples of both with FOPL statements")
# and half the answer to 81 Ba (net -> frame).
add("c5_frame_fopl.png", PS5, 45, box=(0.128, 0.105, 0.924, 0.891))
# Every facet a slot can carry -- value, default, cardinality, type, attached
# procedure, salience, constraint -- on one worked STUDENT frame.
add("c5_frame_facets.png", PS5, 44, box=(0.000, 0.140, 1.000, 1.000))
# Fig 9.5, the simplified frame system for Pee-Wee-Reese: the FRAME form of
# c5_semnet_peewee.png, so the two print together as the net->frame conversion.
add("c5_frame_system.png", PS5, 41, box=(0.055, 0.000, 0.960, 0.998))
# A generic Car frame with if-added / if-needed demons attached to its slots.
add("c5_frame_demons.png", PS5, 46, box=(0.378, 0.138, 0.974, 0.591))

# Link types with their set-theoretic semantics (subset, member, R): the one
# table that says what a semantic-net arc actually MEANS.
add("c5_semnet_links.png", BJ5, 43)

# Insights book p136: class / subclass / instance frames. (Its book p135
# net-to-frame figure is NOT used: it prints "like John" and "type Ginger"
# where the net says owned-by and colour, and gives John an Age/Color pair
# carried over from the car example. The notes use the Rich & Knight pair
# c5_semnet_peewee + c5_frame_system for that conversion instead, and record
# the book error in the text.)
# dpi is deliberately low: this is a photographed book page, so the paper
# grain quantises badly and at 210 dpi the single figure was 948 kB, three
# times the next largest in the chapter. It prints in a half-width column,
# where 950 px is still about 280 dpi on the page.
ins("c5_frame_classes.png", 136, (0.06, 0.090, 0.99, 0.525), dpi=52)


# ------------------------------------------------------------------ chapter 6
# BA Sir's CH-06 is one slide per page. Most figures on it are pasted rasters,
# but the three that matter most (the analogy pair, the GA cycle, the GA
# flowchart) are drawn as native vector shapes, so those are manual boxes.
PS6 = os.path.join(PS, "6.Machine Learning_old_syllabus.pdf")
SG6 = os.path.join(SG, "AIChapter_6.pdf")

# The four components of a learning system -- environment, learning element,
# knowledge base, performance element -- with the arrows between them. This IS
# the answer to "explain the learning framework with a suitable block diagram"
# (78 Ba, 69 Bh, 78 Po). SG Sir's is the only one anywhere in Notes\ that draws
# all four boxes AND the loop back from the performance element.
add("c6_framework.png", SG6, 15)
# Deductive and inductive reasoning as two ladders read in opposite directions
# (theory -> hypothesis -> observation -> confirmation, against
# observation -> pattern -> hypothesis -> theory). One picture answers
# "induction versus deduction" (73 Bh short note) outright.
add("c6_ind_ded.png", SG6, 9)
# The reinforcement-learning loop: agent, environment, state, action, reward.
# 78 Po asks all three feedback types with examples and this is the only one
# of the three that needs a drawing.
add("c6_rl_loop.png", PS6, 25, box=(0.073, 0.236, 0.903, 0.855))

# Learning by analogy, drawn as the pair the question always uses: a hydraulics
# junction beside Kirchhoff's current law. Vector art on the slide, so a box.
add("c6_analogy.png", BA6, 8, box=(0.22, 0.31, 0.78, 0.61))

# Russell & Norvig fig 19.4: the SAME examples split on Type and on Patrons,
# side by side, positives in light boxes and negatives in dark. It shows in one
# glance WHY one attribute beats another, which is the whole of "how is the
# best attribute selected in a decision tree".
add("c6_id3_split.png", BA6, 13)

# The GA flowchart -- START, generate random population, evaluate fitness, is
# the answer good enough, mate, check for mutation, mutate, END. Asked by name
# in 81 Ba ("with a flowchart") and as "block diagram" in six more. Two stacked
# rasters plus vector arrows, so one box over the pair.
add("c6_ga_flowchart.png", BA6, 21, box=(0.00, 0.17, 0.49, 0.95))
# The same algorithm as a cycle: Population -> Selection -> Parents ->
# Crossover -> Mutation -> Offspring -> Replacement -> Population. Vector.
add("c6_ga_cycle.png", BA6, 18, box=(0.43, 0.505, 0.955, 0.95))
# Single-point crossover shown twice over: as coloured parent/child bars AND as
# a table of the four bit strings with the cut marked. PS Sir's is used rather
# than BA Sir's because the table lets a reader check the swap gene by gene.
add("c6_ga_crossover.png", PS6, 102, box=(0.030, 0.443, 0.975, 0.883),
    mask=[(0.0, 0.76, 0.44, 1.0)])
# Mutation: one gene flipped, before and after.
add("c6_ga_mutation.png", BA6, 21, box=(0.60, 0.62, 0.93, 0.92))
# f against x with one global and four local optima. This is the answer to
# "when shall we use a genetic algorithm" (81 Ash, 80 Ch) as a picture: a
# hill-climber stops on whichever bump it started under.
add("c6_ga_optima.png", PS6, 92, pad=0)

# The fuzzy inference system: crisp input -> fuzzifier -> inference engine
# (with the rule base above it) -> defuzzifier -> crisp output, with the fuzzy
# input and output sets labelled on the internal arrows. Asked as "the
# architecture and working mechanism of a fuzzy inference system" (82 Ba) and
# as "the block diagram" in five more papers.
add("c6_fuzzy_arch.png", PS6, 143)
# The same block diagram drawn WITH the membership curves on it, so the reader
# sees what "fuzzy input" actually is. BA Sir's, and it carries the rule base
# as an IF..THEN box.
add("c6_fuzzy_infer.png", BA6, 25, pick=0, mask=[(0.90, 0.0, 1.0, 0.14)])
# Crisp against fuzzy on one worked table: eleven people's heights, membership
# of "tall" as a 0/1 step and as a graded value, with both curves plotted.
# The cleanest possible answer to "how does fuzzy logic differ from classical
# binary logic" (82 Bh).
add("c6_crisp_fuzzy_tbl.png", BA6, 25, pick=1)
# The set-theoretic version of the same point: a crisp set boundary against a
# fuzzy one, showing that b is simply outside A on the left but partially
# inside it on the right.
add("c6_crisp_fuzzy_set.png", PS6, 123, pad=0)
# Triangular membership functions for three linguistic variables at once
# (humidity, temperature, moisture), which is what "construct membership
# functions for them" produces in the fuzzy-learning steps.
add("c6_memb_fns.png", BA6, 26, pick=0)

# A Boltzmann machine as an undirected graph: visible nodes, hidden nodes,
# every pair symmetrically connected, no self loops. The one figure that makes
# "there is no output layer" obvious.
add("c6_boltzmann.png", PS6, 154, box=(0.100, 0.325, 0.905, 0.990), pad=0)
# A restricted Boltzmann machine in its two phases, learning and generating,
# with the digit vectors it reconstructs underneath.
add("c6_rbm.png", BA6, 28, pick=0)


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
        for m in (job.get("mask") or ()):
            ImageDraw.Draw(img).rectangle(
                (round(m[0] * img.width), round(m[1] * img.height),
                 round(m[2] * img.width), round(m[3] * img.height)),
                fill=(255, 255, 255))
        img = shrink(img)
        img.save(out, optimize=True)
        w, h = img.size
        kb = os.path.getsize(out) / 1024.0
        print(f"{job['name']:30s} {w:5d}x{h:<5d} {kb:7.0f} kB "
              f"<- {os.path.basename(job['pdf'])[:34]} p{job['page']}")
        d.close()


if __name__ == "__main__":
    main()
