# -*- coding: utf-8 -*-
"""Crop the O&M topic figures out of their source decks. Never redraws.

Adhikari's deck ("Notes/O _ M.pdf") stamps an "IOE Syllabus" watermark image at
bbox (225,135,495,405) on every page. Deleting that image before rendering gives a
clean crop; nothing else on the page is touched.

    python figs.py          render every spec below into figs/
"""
import os
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
OM = os.path.join(HERE, "..", "..", "Notes", "O _ M.pdf")
ADD1 = os.path.join(HERE, "..", "..", "Notes", "Additional",
                    "Chapter 1. Organization-and-management-introduction.pdf")
DPI = 220
WATERMARK = (225, 135)

# name: (source, 1-based page, clip rect in pt or None for the page's largest picture)
SPECS = {
    "c3_motivation_eq.png": (OM, 201, None),   # Motivation equation: inputs -> performance -> outcomes
    "c5_is_environment.png": (OM, 281, None),  # IS inside the organisation inside its environment
    "c5_is_pyramid.png": (OM, 300, None),      # IS types by management level x functional area
    # ---- ch1 expansion (2026-09-27)
    "c1_process_cycle.png": (OM, 36, (348, 112, 705, 470)),   # management process: plan..evaluate, revise
    "c1_eff_matrix.png": (OM, 37, None),                      # efficiency x effectiveness 2x2
    "c1_comm_process.png": (OM, 53, (95, 222, 620, 428)),     # idea -> encode -> transmit -> ... -> feedback
    "c1_skills_mix.png": (OM, 58, None),                      # conceptual / human / technical by level
    "c1_admin_mgmt.png": (OM, 59, None),                      # administration vs management share by level
    "c1_model_hier.png": (OM, 65, None),                      # hierarchical model: president -> VPs -> units
    "c1_model_task.png": (OM, 66, (346, 95, 718, 395)),       # task-oriented model: five tasks in a cycle
    "c1_model_team.png": (OM, 69, None),                      # team effort model (photo)
    "c1_system_plan.png": (OM, 88, (28, 248, 712, 492)),      # system approach: plan, inputs, process, output
    "c1_partner_conflict.png": (OM, 104, (420, 105, 715, 440)),  # partnership disadvantages (clip art)
    "c1_open_system.png": (ADD1, 1, None),                    # open system with sub-systems and feedback
    "c1_levels_pyramid.png": (ADD1, 4, None),                 # levels pyramid with functions per level
    "c1_importance_cycle.png": (ADD1, 5, (72, 82, 583, 196)), # low/high productivity cycles
    "c1_models_ioe.png": (ADD1, 5, (72, 337, 599, 577)),      # hierarchical, task, allocation sketches
    "c1_models_ioe2.png": (ADD1, 7, None),                    # knowledge-oriented and goal-concentrated
    "c1_line_staff_adv.png": (ADD1, 16, (92, 62, 542, 351)),                # line and staff with advisory staff
    "c1_org_chart.png": (ADD1, 20, (72, 492, 534, 697)),      # organization chart with advisory committee
}


def drop_watermark(page):
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if (round(r.x0), round(r.y0)) == WATERMARK:
                page.delete_image(img[0])
                break


def largest_picture(page):
    best = None
    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"])
        if best is None or r.get_area() > best.get_area():
            best = r
    return best


def main():
    docs = {}
    for name, (src, pno, clip) in SPECS.items():
        doc = docs.setdefault(src, fitz.open(src))
        page = doc[pno - 1]
        drop_watermark(page)
        rect = fitz.Rect(clip) if clip else largest_picture(page)
        if rect is None:
            raise SystemExit("no picture on p%d for %s" % (pno, name))
        page.get_pixmap(dpi=DPI, clip=rect & page.rect).save(os.path.join(FIGS, name))
        print("ok %-24s p%d %s" % (name, pno, tuple(round(v) for v in rect)))


if __name__ == "__main__":
    main()
