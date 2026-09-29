# -*- coding: utf-8 -*-
"""Chapter 4 (Case Studies) figures. No local source has a case-study diagram
(Adhikari pp259-272 and AJ Sir's deck are text only), so these are generated
from the lists the notes print, in the notes' palette.

The NEA data series are the published NEA figures cited in ch4.tex; the college
case uses illustrative survey numbers that ch4.tex labels as illustrative.
The assertions below make sure every drawn number is also printed in ch4.tex.

    python ch4fig.py
"""
import io
import os
import re

import diagkit as K

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = io.open(os.path.join(HERE, "ch4.tex"), encoding="utf-8").read()


def printed(*vals):
    for v in vals:
        if str(v) not in TEX:
            raise SystemExit("drawn value %r is not printed in ch4.tex" % (v,))


# ------------------------------------------------------------ 4.1
K.hub("c4_objectives.png", "Case study method",
      ["Impart knowledge & facts", "Problem analysis", "Decision making",
       "Communication", "Attitude formation", "Theory to practice", "Teamwork & judgement"],
      width=3.3, ring=1.05, box=(0.7, 0.3))

K.grid("c4_types.png", ["Describe / prepare", "Explain / test"],
       ["One or few instances", "Many sites or a larger study"],
       [[("Illustrative", "one or two instances show what a situation is like"),
         ("Exploratory (pilot)", "short study before a large one: find questions, measures")],
        [("Critical instance", "unique site; tests cause-effect or a universal claim"),
         ("Cumulative", "pools past studies from many sites and times")]],
       width=3.3, tones=[[0, 1], [2, 3]], cell_h=0.62, col_title="Scope",
       row_title="Aim")

# ------------------------------------------------------------ 4.2
K.flow("c4_phases.png", [
    ("Study the details", "What is happening? What more data is needed?"),
    ("Collect additional facts", "ask the discussion leader; sort facts by use in the decision"),
    ("Define the problem", "group agrees on the real problem; phrases the critical questions"),
    ("Individual decisions", "How would I handle it? How would I support it? Same-view sub-groups argue"),
    ("Learn from the whole case", "How could more have been achieved?"),
], width=3.3, box_h=0.15, title="Five phases (group discussion)", wrap=48)

K.flow("c4_steps.png", [
    ("State the problem", "what must be done or answered"),
    ("Collect & analyse data", "arrange facts; separate facts from opinions"),
    ("Tentative solutions", "list every alternative"),
    ("Recommended solution", "best answer on the given data"),
    ("Written report", "present the result"),
    ("Checklist", "achieved? difficulties? limits? best option?"),
], width=3.3, box_h=0.13, title="Six steps (individual analysis)", wrap=58,
    loop_back=(5, 2, "fails the check"))

K.flow("c4_analysis.png", [
    ("Title of the case", ""),
    ("Company + case problems", ""),
    ("Careful, detailed reading", ""),
    ("Meet the central characters", ""),
    ("Define problems, develop solution", ""),
], width=6.9, horizontal=True, box_h=0.62, title="Analysing a case problem (AJ Sir)", wrap=19)

# ------------------------------------------------------------ 4.3
K.columns("c4_report.png", [
    ("1. Organizational background", ["Goals and objectives", "Formation", "Structure",
                                      "Social needs and value", "Historical relation",
                                      "Financial position"], 0),
    ("2. Case study report", ["Identify the problem", "Develop the hypothesis",
                              "Case research design", "Collect + analyse data",
                              "Generalize + interpret", "Conclusions + recommendations"], 1),
], width=3.3, wrap=26, item_h=0.19)

# ------------------------------------------------------------ 4.4 NEA mock case
K.tree("c4_nea_org.png",
       ("Board of Directors", [
           ("Managing Director", [
               ("Generation", []), ("Transmission", []),
               ("Distribution & Consumer Services", []), ("Planning, Monitoring & IT", []),
               ("Engineering Services", []), ("Project Management", []),
               ("Administration", []), ("Finance", []),
           ], 1)], 0),
       width=6.9, wrap=14, box_h=0.42, level_gap=0.22, fs=6.8)

years = ["72/73", "73/74", "74/75", "75/76", "76/77", "77/78", "78/79", "79/80", "80/81"]
loss = [25.78, 22.90, 20.45, 15.32, 15.27, 17.18, 15.38, 13.46, 12.73]
printed(*["%.2f" % v for v in loss])
K.chart("c4_nea_loss.png", years, loss, kind="line", ylabel="system loss, %",
        highlight=(0, 8), fmt="%.2f", ylim=(0, 30), width=3.3, height=1.95,
        marks={0.6: "new MD, 2073 Bh"},
        note="FY (BS). Source: NEA figures reported in Kathmandu Post 2017 and Khabarhub 2024.")

K.fishbone("c4_nea_fishbone.png", "Poor NEA performance (2072/73)", [
    ("Planning", ["short horizon", "no load forecast", "projects late"]),
    ("Leadership", ["frequent MD change", "political pressure", "weak accountability"]),
    ("Supply", ["winter dry season", "few storage plants", "import limits"]),
    ("Motivation", ["no performance targets", "seniority pay", "low morale"]),
    ("HRD", ["little training", "no succession plan", "skill gaps"]),
    ("Distribution", ["25.78% loss", "theft, hooking", "dedicated-feeder bias"]),
], width=6.9)

K.gantt("c4_nea_plan.png", [
    ("End dedicated-feeder bias; fair rota", 0, 1, 2),
    ("Leakage drive: meters, raids, feeder audits", 0, 3, 2),
    ("Peak-hour import from India", 0, 2, 0),
    ("Targets + ranking per distribution centre", 1, 4, 1),
    ("Training academy; merit promotion", 1, 6, 3),
    ("Transmission lines, substations", 2, 6, 0),
    ("Storage + peaking plants; export", 3, 6, 0),
], ["Yr 1 H1", "Yr 1 H2", "Yr 2", "Yr 3", "Yr 4", "Yr 5"], width=6.9, label_w=2.6)

# ------------------------------------------------------------ 4.4 college mock case
areas = ["Teaching", "Labs", "Library", "Internet", "Career cell", "Hostel"]
score = [3.4, 2.3, 2.9, 2.1, 1.8, 2.6]
printed(*["%.1f" % v for v in score])
K.chart("c4_college_survey.png", areas, score, kind="bar", ylabel="mean score (1 to 5)",
        highlight=(1, 3, 4), fmt="%.1f", ylim=(0, 5), width=3.3, height=1.9,
        note="Illustrative survey of 240 students; orange = below 2.5, act first.")

K.fishbone("c4_college_fishbone.png", "Low pass rate and weak image", [
    ("Faculty", ["part-time heavy", "no training", "high turnover"]),
    ("Facilities", ["old lab kits", "slow internet", "few e-books"]),
    ("Students", ["irregular attendance", "no mentoring", "weak feedback"]),
    ("Management", ["no MIS", "late results", "no QAA plan"]),
], width=6.9)

# ------------------------------------------------------------ 4.6 sample report (cement plant)
K.flow("c4_cem_process.png", [
    ("Quarry", "limestone: drill, blast, haul 12 km"),
    ("Crusher", "crush, stockpile, pre-blend"),
    ("Raw mill", "limestone + clay + iron ore ground to raw meal"),
    ("Preheater + kiln", "raw meal burnt at 1,450 °C → clinker"),
    ("Cooler + silo", "clinker air-cooled, stored"),
    ("Cement mill", "clinker + gypsum (OPC) or + fly ash (PPC)"),
    ("Packing + dispatch", "50 kg bags; trucks to depots, dealers"),
], width=6.9, horizontal=True, title="Production process, ABC Cement Industries Ltd.", wrap=14)

K.tree("c4_cem_org.png",
       ("Board of Directors", [
           ("Managing Director", [
               ("Plant Manager (Works)", [
                   ("Production", []), ("Mechanical", []),
                   ("Electrical & Instrumentation", []), ("Quality Control", []),
                   ("Mines", []),
               ]),
               ("Marketing & Sales", []), ("Finance & Accounts", []),
               ("Stores & Purchase", []), ("HR & Admin", []), ("IT / MIS", []),
               ("Safety & Environment", []),
           ])]),
       width=6.9, wrap=12, box_h=0.46, level_gap=0.22, fs=6.4,
       dashed=("Safety & Environment",))

causes = ["Power\ntrips", "Break-\ndowns", "Planned\nshutdown", "Clinker\nyard full",
          "Coal,\nmaterial", "Others"]
hours = [610, 420, 360, 240, 150, 70]
printed(*hours)
printed("1,850", "1,490")
assert sum(hours) == 1850 and sum(hours) - 360 == 1490
K.chart("c4_cem_stops.png", causes, hours, kind="bar", ylabel="kiln stop hours",
        highlight=(0, 1), fmt="%d", ylim=(0, 700), width=3.3, height=1.95,
        note="FY 2082/83, 1,850 h in all. Illustrative plant log; orange = 69% of unplanned stops.")

K.fishbone("c4_cem_fishbone.png", "Plant runs at 69% of capacity", [
    ("Power", ["trips, voltage dips", "no standby for kiln drives", "shared 33 kV line"]),
    ("Machines", ["refractory failures", "bearing wear", "old raw mill"]),
    ("Materials", ["coal import delays", "3-4 month spares lead time", "no min stock"]),
    ("People", ["contract turnover 28%", "safety-only training", "seniority promotion"]),
    ("Methods", ["breakdown maintenance", "stores and maintenance unlinked", "no daily KPI"]),
    ("Market", ["oversupply, price war", "monsoon slump", "clinker yard full"]),
], width=6.9)

K.gantt("c4_cem_plan.png", [
    ("Dedicated line + standby DG set for kiln drives", 0, 3, 0),
    ("Preventive + condition-based maintenance", 0, 4, 1),
    ("Min-max stock of critical spares; rate contracts", 0, 2, 1),
    ("ERP: stores, maintenance, production, sales", 1, 5, 3),
    ("Skill matrix, training; regularize contract operators", 1, 6, 2),
    ("Shift incentive on kiln run hours", 1, 2, 2),
    ("New districts, project sales, mason meets", 2, 6, 4),
], ["Q1", "Q2", "Q3", "Q4", "Yr 2 H1", "Yr 2 H2"], width=6.9, label_w=3.0)
