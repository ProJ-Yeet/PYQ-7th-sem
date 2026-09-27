# -*- coding: utf-8 -*-
"""Chapter 1 generated figures: lists and processes the notes print, drawn where
no local source (Adhikari, AJ Sir, ioenotes) has a picture of them. Source
figures are cropped by figs.py instead; web photos live in figs/web/.

Every number drawn is asserted to be printed in ch1.tex.

    python ch1fig.py
"""
import io
import os

import diagkit as K

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = io.open(os.path.join(HERE, "ch1.tex"), encoding="utf-8").read()


def printed(*vals):
    if os.environ.get("NOCHECK"):   # drafting figures before the text exists
        return
    for v in vals:
        if str(v) not in TEX:
            raise SystemExit("drawn value %r is not printed in ch1.tex" % (v,))


# ------------------------------------------------------------ 1.1 Organization
K.hub("c1_principles.png", "Principles of organization",
      ["Unity of objectives", "Specialization", "Scalar chain", "Unity of command",
       "Authority = responsibility", "Span of control", "Delegation", "Coordination",
       "Flexibility", "Continuity"], width=3.3, ring=1.1, box=(0.66, 0.26), fs=6.6)

K.flow("c1_history.png", [
    ("Self-sufficiency", "village economy"),
    ("Barter, then money", "marketable surplus"),
    ("Transport, trade", "ships, railways"),
    ("Industrial revolution", "steam engine, factories"),
    ("Joint stock company", "limited liability"),
    ("Scientific management", "Taylor, Fayol"),
    ("Automation", "liberalization"),
    ("Globalization", "MNCs, WTO 1995"),
], width=3.3, box_h=0.12, title="Historical development of organization", wrap=60)

K.hub("c1_ob.png", "Organizational behaviour",
      ["Psychology", "Sociology", "Social psychology", "Anthropology", "Political science"],
      width=3.0, ring=0.95, box=(0.7, 0.26), tone=3)

# ------------------------------------------------------------ 1.2 Management
K.hub("c1_functions.png", "Management",
      ["Planning", "Organizing", "Staffing", "Directing", "Motivating", "Controlling",
       "Co-ordinating", "Communicating"], width=3.3, ring=1.0, box=(0.66, 0.26))

K.flow("c1_planning_steps.png", [
    ("Determine objectives", ""), ("Set premises and constraints", ""),
    ("Decide the planning period", ""), ("Collect and process information", ""),
    ("Develop alternative courses", ""), ("Evaluate alternatives", ""),
    ("Select the best plan", ""), ("Frame subsidiary plans", ""), ("Control the plans", ""),
], width=3.0, box_h=0.085, title="Steps in planning (Adhikari)", tone=0)

K.pyramid("c1_plan_hierarchy.png",
          ["Goals", "Objectives", "Policies", "Rules, procedures", "Programs, schedules",
           "Budgets"],
          notes=["long-run targets", "ends activities aim at", "framework for executive action",
                 "fixed choices; how to carry out a policy", "step-by-step action; when each happens",
                 "expected costs and revenues in numbers"], width=3.3)

K.flow("c1_organizing_steps.png", [
    ("Determine activities", ""), ("Divide + group them", ""), ("Fit people into jobs", ""),
    ("Assign authority", ""),
], width=3.3, horizontal=True, box_h=0.6, title="Steps in organizing", tone=1, wrap=14)

K.flow("c1_staffing_steps.png", [
    ("Recruitment", ""), ("Selection", ""), ("Placement", ""), ("Training", ""),
    ("Development", ""), ("Pay + appraisal", ""),
], width=2.2, box_h=0.1, title="Steps in staffing", tone=2)

K.cycle("c1_control_cycle.png", ["Set standards", "Measure performance", "Compare with standard",
                                 "Take corrective action"],
        width=2.8, center="Control", R=0.9, box=(0.72, 0.28), tone=2)

K.grid("c1_coord_types.png", ["Where", "Direction"], ["", ""],
       [[("Internal", "among departments, levels and people inside the firm"),
         ("External", "with customers, suppliers, government, public")],
        [("Vertical", "between levels: top, middle, lower"),
         ("Horizontal", "same level: production, sales, finance")]],
       width=3.3, tones=[[0, 1], [2, 3]], cell_h=0.55)

K.columns("c1_motivation_class.png", [
    ("Internal (intrinsic)", ["Interests", "Emotional attachment", "Burning desire",
                              "Fighting spirit for a noble cause"], 1),
    ("External (extrinsic)", ["Attractive salary, bonus", "Praise, incentive",
                              "Punishment", "Fear of losing the job"], 2),
], width=3.3, wrap=24)

K.columns("c1_mintzberg.png", [
    ("Interpersonal", ["Figurehead", "Leader", "Liaison"], 0),
    ("Informational", ["Monitor", "Disseminator", "Spokesperson"], 1),
    ("Decisional", ["Entrepreneur", "Disturbance handler", "Resource allocator", "Negotiator"], 2),
], width=3.3, wrap=14)

K.hub("c1_models.png", "Models of management",
      ["Hierarchical", "Task-oriented", "Allocational", "Transactional", "Team effort",
       "Knowledge-oriented", "Goal-concentrated"], width=3.3, ring=1.0, box=(0.7, 0.26), tone=3)

# ------------------------------------------------------------ 1.3 Theories
printed("12.5", "47.5", "1.15", "1.85")
K.chart("c1_pigiron_output.png", ["before", "after"], [12.5, 47.5], ylabel="tons / day / man",
        highlight=(1,), fmt="%.1f", width=1.6, height=1.5)
K.chart("c1_pigiron_wage.png", ["before", "after"], [1.15, 1.85], ylabel="wage, \\$ / day",
        highlight=(1,), fmt="%.2f", width=1.6, height=1.5, ylim=(0, 2.2))

K.flow("c1_hawthorne.png", [
    ("Illumination", "1924-27: output rose with light up or down"),
    ("Relay assembly room", "6 women: output rose with attention"),
    ("Interviewing", "21,000 workers: feelings matter"),
    ("Bank wiring room", "14 men: group sets its own norm"),
], width=6.9, horizontal=True, box_h=0.62, title="Hawthorne experiments, Western Electric, 1924-32",
    tone=1, wrap=18)

K.hub("c1_fayol_activities.png", "Industrial undertaking",
      ["Technical", "Commercial", "Financial", "Security", "Accounting",
       "Managerial (POCCC)"], width=3.0, ring=0.95, box=(0.72, 0.28), tone=0)

K.columns("c1_modern_streams.png", [
    ("Quantitative", ["models, OR", "simulation", "linear programming"], 0),
    ("System", ["open system", "sub-systems", "Boulding, Churchman"], 1),
    ("Contingency", ["it depends", "if-then", "Woodward, Fiedler"], 2),
    ("Operational", ["universal body", "of knowledge", "Koontz, O'Donnell"], 3),
], width=6.9, wrap=18)

K.flow("c1_contingency.png", [
    ("Environment", "size, technology, market, people (IF)"),
    ("Contingent relationship", "match the tool to the situation"),
    ("Management concepts", "process, behavioural, quantitative, system tools (THEN)"),
], width=3.3, horizontal=True, box_h=0.78, tone=2, wrap=13)

K.cycle("c1_mbo.png", ["Set org goals", "Agree individual objectives", "Action plans",
                       "Periodic review", "Appraise + reward"],
        width=2.8, center="MBO", R=0.95, box=(0.7, 0.28), tone=1)

# ------------------------------------------------------------ 1.4 Ownership
K.columns("c1_forms.png", [
    ("Single ownership", ["one owner", "unlimited liability", "no separate entity",
                          "ends with owner"], 0),
    ("Partnership", ["2+ partners, deed", "unlimited liability", "no separate entity",
                     "ends with a partner"], 1),
    ("Joint stock co.", ["shareholders", "limited liability", "separate entity",
                         "perpetual"], 2),
    ("Co-operative", ["members, 1 vote each", "limited liability", "separate entity",
                      "service motive"], 3),
    ("Public corp.", ["government", "special act", "separate entity", "public service"], 4),
], width=6.9, wrap=17)

K.flow("c1_jsc_formation.png", [
    ("Promotion", "idea, feasibility, promoters"),
    ("Name approval", "Office of the Company Registrar"),
    ("File documents", "MoA, AoA, IDs, consents, fee"),
    ("Certificate of incorporation", "company now exists in law"),
    ("PAN / VAT, ward", "tax and local registration"),
    ("Public company only", "SEBON prospectus, IPO, commencement, NEPSE"),
], width=3.3, box_h=0.14, title="Forming a company in Nepal", tone=2, wrap=60)

K.hub("c1_partners.png", "Types of partners",
      ["General / active", "Limited", "Sleeping", "Nominal", "Minor", "By estoppel"],
      width=3.0, ring=0.95, box=(0.7, 0.27), tone=1)

K.hub("c1_coop_types.png", "Co-operatives",
      ["Producers'", "Consumers'", "Marketing", "Housing", "Savings + credit", "Multipurpose",
       "Farming"], width=3.0, ring=0.95, box=(0.66, 0.27), tone=3)

# ------------------------------------------------------------ 1.5 Structure
K.flow("c1_structure_design.png", [
    ("Set objectives", ""), ("List activities", ""), ("Group into departments", ""),
    ("Decide levels + span", ""), ("Assign authority", ""), ("Link coordination", ""),
    ("Draw chart, review", ""),
], width=6.9, horizontal=True, box_h=0.46, title="Designing an organization structure",
    tone=0, wrap=12)

K.tree("c1_span_narrow.png",
       ("Manager", [("Supervisor", [("W", []), ("W", [])]), ("Supervisor", [("W", []), ("W", [])]),
                    ("Supervisor", [("W", []), ("W", [])])], 0),
       width=3.2, box_h=0.3, level_gap=0.22, wrap=10, fs=6.8)
K.tree("c1_span_wide.png",
       ("Manager", [("W", []) for _ in range(8)], 0),
       width=3.2, box_h=0.3, level_gap=0.22, wrap=10, fs=6.8)

rel = [n * (2 ** (n - 1) + n - 1) for n in range(1, 9)]
printed(*rel)
K.chart("c1_graicunas.png", [str(n) for n in range(1, 9)], rel, kind="line",
        ylabel="relationships", highlight=(5,), fmt="%d", width=3.3, height=1.7,
        ylim=(0, 1250), note="n subordinates: relationships = n(2^(n-1) + n - 1)")

K.columns("c1_committees.png", [
    ("By life", ["Ad hoc: one task", "Standing: permanent"], 0),
    ("By power", ["Advisory: recommends", "Executive: decides"], 1),
    ("By origin", ["Formal: by charter", "Informal: by need"], 2),
], width=3.3, wrap=14)

# ------------------------------------------------------------ 1.6 Purchasing and marketing
K.hub("c1_5r.png", "Purchasing",
      ["Right quality", "Right quantity", "Right price", "Right time", "Right source",
       "Right place"], width=3.0, ring=0.95, box=(0.7, 0.27), tone=2)

K.flow("c1_purchase_proc.png", [
    ("Purchase requisition", ""), ("Specify need", ""), ("Enquiry to suppliers", ""),
    ("Quotations / tenders", ""), ("Comparative statement", ""), ("Select + negotiate", ""),
    ("Purchase order", ""), ("Follow up", ""), ("Receive + inspect", ""),
    ("Check invoice, pay", ""), ("Issue + record", ""),
], width=2.6, box_h=0.085, title="Purchasing procedure", tone=2)

K.columns("c1_purchase_methods.png", [
    ("By timing", ["By requirement", "For a period", "Market purchasing", "Speculative"], 0),
    ("By arrangement", ["Rate contract", "Group purchasing", "Government agency"], 1),
    ("By procedure", ["Direct", "Quotation (3+)", "Tender"], 2),
], width=3.3, wrap=16)

K.flow("c1_marketing_evolution.png", [
    ("Production", "make it cheap"), ("Product", "make it better"), ("Selling", "push what we make"),
    ("Marketing", "make what customers want"), ("Societal", "and keep society well"),
], width=6.9, horizontal=True, box_h=0.55, title="Evolution of the marketing concept", tone=3, wrap=14)

K.hub("c1_4p.png", "Marketing mix", ["Product", "Price", "Place", "Promotion"],
      width=2.4, ring=0.8, box=(0.66, 0.28), tone=0)

K.columns("c1_marketing_functions.png", [
    ("Exchange", ["Buying", "Selling"], 0),
    ("Physical distribution", ["Transport", "Storage"], 1),
    ("Facilitating", ["Standardization, grading", "Financing", "Risk bearing",
                      "Market information"], 2),
], width=3.3, wrap=16)
