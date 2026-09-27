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
ADD3 = os.path.join(HERE, "..", "..", "Notes", "Additional",
                    "Chapter 3. motivation-leadership-entrepreneurship.pdf")
# S.K. Joshi's book is phone photos of an open book (yellow cast, no text layer):
# its crops are rendered in grayscale with auto-contrast (ENHANCE below).
JOSHI = os.path.join(HERE, "..", "..", "Books", "OnM_SKJ.pdf")
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
    # ---- ch3 expansion (2026-09-27)
    "c3_erg_table.png": (OM, 215, None),                      # ERG levels with descriptions and examples
    "c3_herzberg_pair.png": (OM, 217, (10, 195, 705, 520)),   # animal avoiding pain vs human growing
    "c3_vroom_high.png": (OM, 221, (60, 235, 672, 498)),      # high E, I, V -> high motivation
    "c3_leadership_what.png": (OM, 224, (10, 90, 690, 495)),  # leading, influencing, commanding, guiding
    "c3_mgr_leader_plan.png": (OM, 228, (0, 84, 700, 490)),   # manager vs leader in planning
    "c3_boss_leader.png": (OM, 247, None),                    # a boss says "Go!", a leader "Let's go!"
    "c3_approaches_ioe.png": (ADD3, 13, None),                # trait, behavioural, contingency, integrated
    # ---- ch5 expansion (2026-09-27)
    "c5_joshi_info_needs.png": (JOSHI, 56, (95, 60, 372, 280)),     # Fig 3.3 information content by level
    "c5_joshi_anthony.png": (JOSHI, 60, (455, 75, 735, 175)),       # Fig 3.5 Anthony's triangle
    "c5_joshi_anthony2.png": (JOSHI, 60, (445, 418, 745, 560)),     # Fig 3.6 integrated triangle, data sides
    "c5_joshi_is_model.png": (JOSHI, 62, (55, 40, 400, 222)),       # Fig 3.7 IS model
    "c5_joshi_paradigm.png": (JOSHI, 62, (405, 165, 760, 330)),     # Fig 3.8 problem-solving paradigm
    "c5_joshi_decision_levels.png": (JOSHI, 67, (120, 200, 395, 338)),  # Fig 3.12 levels and information
    "c5_joshi_system_view.png": (JOSHI, 70, (160, 175, 395, 335)),  # Fig 3.13 computer as a system
    "c5_data_info.png": (OM, 277, (60, 140, 690, 440)),             # data -> processing -> information, feedback
    "c5_mis_roles.png": (OM, 286, None),                            # MIS roles in the organization
    "c5_payroll_tps.png": (OM, 291, None),                          # symbolic payroll TPS
    "c5_tps_mis.png": (OM, 293, None),                              # TPS files feeding MIS reports
    "c5_dss_voyage.png": (OM, 295, None),                           # voyage-estimating DSS
    "c5_ess_model.png": (OM, 297, None),                            # typical executive support system
    "c5_mis_parts.png": (OM, 303, None),                            # management + information + systems
}
ENHANCE = {JOSHI}


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
        pm = page.get_pixmap(dpi=DPI, clip=rect & page.rect)
        if src in ENHANCE:
            from PIL import Image, ImageOps
            im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples).convert("L")
            ImageOps.autocontrast(im, cutoff=2).save(os.path.join(FIGS, name))
        else:
            pm.save(os.path.join(FIGS, name))
        print("ok %-24s p%d %s" % (name, pno, tuple(round(v) for v in rect)))


if __name__ == "__main__":
    main()
