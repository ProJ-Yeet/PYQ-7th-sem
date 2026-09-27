# -*- coding: utf-8 -*-
"""Chapter 2 (Personnel Management) generated figures. Adhikari's Ch.2 slides have no
diagrams (pp150-191 are text and two wage tables), so every process and list the
notes print is drawn here. The incentive-plan charts are computed from the plans'
own formulas and every plotted value is asserted to be printed in ch2.tex.

    python ch2fig.py
"""
import io
import os

import matplotlib.pyplot as plt

import diagkit as K

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = io.open(os.path.join(HERE, "ch2.tex"), encoding="utf-8").read()


def printed(*vals):
    if os.environ.get("NOCHECK"):
        return
    for v in vals:
        if str(v) not in TEX:
            raise SystemExit("drawn value %r is not printed in ch2.tex" % (v,))


# ------------------------------------------------------------ overview
K.flow("c2_employee_line.png", [
    ("Plan", "how many, what kind"), ("Analyse the job", "description + specification"),
    ("Recruit + select", "pool, then choose"), ("Train", "skills for the job"),
    ("Appraise", "merit rating"), ("Pay", "wages + incentives"),
], width=6.9, horizontal=True, title="The chapter follows one employee", tone=0)

# ------------------------------------------------------------ 2.1
K.hub("c2_operative.png", "Operative functions",
      ["Procurement", "Development", "Compensation", "Integration", "Maintenance",
       "Motivation", "Records + separation"], width=3.2, ring=1.0, box=(0.7, 0.27), tone=1)

K.columns("c2_aspects.png", [
    ("Welfare", ["working conditions", "canteen, housing", "health, safety"], 1),
    ("Labour / personnel", ["recruitment", "pay, promotion", "training"], 0),
    ("Industrial relations", ["unions", "disputes", "collective bargaining"], 2),
], width=3.3, wrap=16)

K.hub("c2_principles.png", "Principles",
      ["Maximum individual development", "Scientific selection", "High morale",
       "Dignity of labour", "Team spirit", "Effective communication", "Joint management",
       "Fair reward", "Effective utilization", "National prosperity"],
      width=3.3, ring=1.1, box=(0.7, 0.27), fs=6.4, tone=3)

# ------------------------------------------------------------ 2.2
K.columns("c2_handbook.png", [
    ("About the firm", ["welcome, history", "values, structure"], 0),
    ("Joining + working", ["recruitment, probation", "hours, leave", "code of conduct",
                           "health and safety"], 1),
    ("Pay + growth", ["salary, allowances", "benefits, PF, gratuity", "training, promotion"], 2),
    ("Problems + exit", ["grievance procedure", "union, bargaining", "resignation, retirement"], 3),
], width=6.9, wrap=20)

# ------------------------------------------------------------ 2.3
K.flow("c2_mpp.png", [
    ("Study objectives and plans", ""), ("Inventory present manpower", ""),
    ("Forecast demand", ""), ("Forecast supply", "internal + external"),
    ("Net requirement", "demand minus supply"), ("Action plans", "recruit, train, redeploy, downsize"),
    ("Monitor and review", ""),
], width=3.2, box_h=0.1, title="Manpower planning process", tone=0, wrap=60)

# ------------------------------------------------------------ 2.4
K.columns("c2_sources.png", [
    ("Internal", ["promotion", "transfer", "internal posting", "former employees",
                  "employee referral"], 1),
    ("External", ["advertisement, job sites", "campus recruitment", "employment exchange",
                  "applications at the gate", "labour unions, agencies"], 2),
], width=3.3, wrap=24)

K.flow("c2_selection.png", [
    ("Receive applications", ""), ("Screen, shortlist", ""), ("Preliminary interview", ""),
    ("Application blank", ""), ("Employment tests", ""), ("Employment interview", ""),
    ("Reference check", ""), ("Medical examination", ""), ("Final selection, offer", ""),
    ("Placement + induction", ""),
], width=2.6, box_h=0.085, title="Selection procedure", tone=2)

K.flow("c2_interview.png", [
    ("Preparation", "study JD + application"), ("Reception", "put candidate at ease"),
    ("Information exchange", "knowledge, attitude"), ("Close", "candidate's questions"),
    ("Evaluation", "standard rating form"),
], width=6.9, horizontal=True, title="Interviewing process", tone=1)

# ------------------------------------------------------------ 2.5
K.columns("c2_tna.png", [
    ("Organization analysis", ["goals", "low output", "high scrap", "accidents"], 0),
    ("Task analysis", ["job description", "vs skills needed"], 1),
    ("Person analysis", ["appraisal gaps", "supervisor reports", "self-assessment"], 2),
], width=3.3, wrap=14)

K.columns("c2_training_methods.png", [
    ("Workers", ["demonstration", "on-the-job", "vestibule school", "apprenticeship"], 0),
    ("Supervisors", ["induction", "lectures", "conferences", "written instruction",
                     "training within industry"], 1),
    ("Executives: on the job", ["understudy", "committee member", "job rotation",
                                "enlargement, enrichment", "MBO"], 2),
    ("Executives: off the job", ["lectures", "case study", "business games", "role playing"], 3),
], width=6.9, wrap=18)

K.hub("c2_training_benefits.png", "Benefits of training",
      ["Productivity", "Morale", "Fewer accidents", "Less spoilage", "Less supervision",
       "Stability, flexibility", "Versatility", "Less turnover", "Fewer breakdowns",
       "Higher earnings"], width=3.3, ring=1.1, box=(0.66, 0.26), fs=6.5, tone=1)

# ------------------------------------------------------------ 2.6
K.tree("c2_job_analysis.png",
       ("Job analysis", [
           ("Job description: the job", [("Recruit", []), ("Evaluate job", []),
                                         ("Train", [])], 1),
           ("Job specification: the person", [("Select", []), ("Appraise", []),
                                              ("Promote", [])], 2)], 0),
       width=4.4, box_h=0.4, level_gap=0.2, wrap=13, fs=6.6)

K.grid("c2_job_eval.png", ["Job vs job", "Job vs scale"],
       ["Whole job (non-quantitative)", "By factors (quantitative)"],
       [[("Ranking", "jobs ordered most to least important"),
         ("Factor comparison", "skill, mental, physical, responsibility, conditions")],
        [("Classification", "jobs slotted into grades"),
         ("Point rating", "points per factor, total sets the grade")]],
       width=3.3, tones=[[0, 1], [2, 3]], cell_h=0.6)

K.columns("c2_appraisal.png", [
    ("Traditional (traits)", ["ranking", "paired comparison", "man-to-man", "grading",
                              "graphic scale", "checklist", "essay", "critical incident"], 0),
    ("Modern (results)", ["MBO", "assessment centre", "360-degree", "BARS",
                          "HR accounting", "KPI scorecard"], 1),
], width=3.3, wrap=20, item_h=0.17)

K.hub("c2_360.png", "Employee", ["Superior", "Peers", "Subordinates", "Customers", "Self"],
      width=2.6, ring=0.85, box=(0.66, 0.27), tone=2)

# ------------------------------------------------------------ 2.7
K.pyramid("c2_wage_levels.png", ["Living wage", "Fair wage", "Minimum wage"],
          notes=["decent living standard of the locality", "equal pay for equal work",
                 "legal floor, lifts those below the poverty line"], width=3.3)

K.hub("c2_wage_factors.png", "Wage / salary structure",
      ["Ability to pay", "Demand + supply", "Market rate", "Cost of living", "Legal rules",
       "Job requirements", "Productivity", "Union power", "Qualification, experience",
       "Regularity, hours"], width=3.3, ring=1.1, box=(0.66, 0.26), fs=6.4, tone=2)

# Taylor differential piece rate: standard 80/day, Rs 12/h, 8 h -> Rs 1.20 per piece
printed("0.96", "1.44", "72", "122.40")
units = list(range(60, 101))
earn = [u * (0.96 if u < 80 else 1.44) for u in units]
fig, ax = plt.subplots(figsize=(3.2, 1.9))
ax.plot([u for u in units if u < 80], [e for u, e in zip(units, earn) if u < 80], color=K.ACC, lw=1.6)
ax.plot([u for u in units if u >= 80], [e for u, e in zip(units, earn) if u >= 80], color=K.MKC, lw=1.6)
ax.axvline(80, color=K.SUB, lw=0.8, ls="--")
for u, e, lab, off in ((75, 72.0, "A: 75 pcs, Rs 72", (-62, 10)),
                       (85, 122.40, "B: 85 pcs, Rs 122.40", (6, -12))):
    ax.plot([u], [e], "o", color=K.INK, ms=3.5)
    ax.annotate(lab, (u, e), xytext=off, textcoords="offset points", fontsize=6.3,
                color=K.INK)
ax.text(80.5, 58, "standard 80", fontsize=6.2, color=K.SUB)
ax.set_xlabel("pieces per day", fontsize=7, color=K.SUB)
ax.set_ylabel("earnings, Rs", fontsize=7, color=K.SUB)
ax.tick_params(labelsize=6.4, colors=K.SUB)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(color=K.RULE, lw=0.5)
K._save(fig, "c2_taylor_rate.png")

# Halsey vs Rowan bonus, Ts = 8 h, R = Rs 10
Ta = [7, 6, 5, 4, 3, 2, 1]
halsey = [0.5 * 10 * (8 - t) for t in Ta]
rowan = [(8 - t) / 8 * t * 10 for t in Ta]
printed(*["%.2f" % b for b in rowan])
printed(*["%.2f" % b for b in halsey])
fig, ax = plt.subplots(figsize=(3.2, 1.9))
ax.plot(Ta, halsey, "o-", color=K.ACC, lw=1.5, ms=3, label="Halsey (50%)")
ax.plot(Ta, rowan, "o-", color=K.MKC, lw=1.5, ms=3, label="Rowan")
ax.annotate("Rowan peaks at Ta = Ts/2", (4, 20), xytext=(6.9, 30), fontsize=6.2, color=K.MKC,
            arrowprops=dict(arrowstyle="-", color=K.MKC, lw=0.6))
ax.invert_xaxis()
ax.set_xlabel("actual time Ta, h (Ts = 8, R = Rs 10)", fontsize=7, color=K.SUB)
ax.set_ylabel("bonus, Rs", fontsize=7, color=K.SUB)
ax.tick_params(labelsize=6.4, colors=K.SUB)
ax.legend(fontsize=6.4, frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(color=K.RULE, lw=0.5)
K._save(fig, "c2_halsey_rowan.png")

# Emerson: bonus % against efficiency, using the points the plan fixes
eff = [60, 66.67, 90, 100, 110, 120]
bon = [0, 0, 10, 20, 30, 40]
printed("66.67", "10\\%", "20\\%")
fig, ax = plt.subplots(figsize=(3.2, 1.8))
ax.plot(eff, bon, "o-", color=K.GD, lw=1.5, ms=3)
for e, b, lab, off in ((60, 0, "X 60%: no bonus", (3, 5)), (100, 20, "Y 100%: 20%", (-58, 3)),
                       (120, 40, "Z 120%: 40%", (-58, -3))):
    ax.annotate(lab, (e, b), xytext=off, textcoords="offset points", fontsize=6.2,
                color=K.INK)
ax.set_xlabel("efficiency, % of standard", fontsize=7, color=K.SUB)
ax.set_ylabel("bonus, % of time wage", fontsize=7, color=K.SUB)
ax.tick_params(labelsize=6.4, colors=K.SUB)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(color=K.RULE, lw=0.5)
K._save(fig, "c2_emerson.png")

# ------------------------------------------------------------ 2.8
K.hub("c2_ir_actors.png", "Industrial relations", ["Management", "Workers + unions",
                                                   "Government"],
      width=2.4, ring=0.8, box=(0.72, 0.28), tone=0)

K.flow("c2_bargaining.png", [
    ("Preparation", "charter of demands; data"), ("Negotiation", "proposals, give and take"),
    ("Agreement", "written, signed, registered"), ("Implementation", ""),
    ("Administration + review", "grievances; renegotiate"),
], width=3.2, box_h=0.12, title="Collective bargaining process", tone=2, wrap=60)
