# -*- coding: utf-8 -*-
"""Chapter 5 (MIS) generated figures, for the lists and processes the notes print
where no source picture exists. Source figures (Adhikari's TPS/MIS/DSS/ESS diagrams,
S.K. Joshi's scanned figures) are cropped by figs.py; DIKW, IBM 704 and data-centre
images are Wikimedia Commons files (w_*.png / w_*.jpg).

    python ch5fig.py
"""
import diagkit as K

# ------------------------------------------------------------ 5.1
K.hub("c5_functions.png", "MIS functions",
      ["Data capture", "Processing", "Storage + retrieval", "Determine needs",
       "Evaluation", "Abstraction", "Dissemination"],
      width=3.1, ring=1.0, box=(0.72, 0.27), tone=0)

K.columns("c5_needs.png", [
    ("Production manager", ["production costs", "labour costs", "machine costs",
                            "overhead costs", "capacity"], 0),
    ("Marketing manager", ["new product development", "sales trends", "selling costs",
                           "market research"], 1),
    ("Personnel manager", ["turnover", "absenteeism", "skill levels", "labour market",
                           "wage levels"], 2),
], width=3.3, wrap=14, item_h=0.26)

K.hub("c5_qualities.png", "Good information",
      ["Accurate", "Timely", "Complete", "Concise", "Relevant", "Right frequency",
       "Understandable", "Worth its cost"],
      width=3.0, ring=1.0, box=(0.7, 0.27), tone=1)

# ------------------------------------------------------------ 5.2
K.flow("c5_planning_qs.png", [
    ("Where are we?", "past performance"), ("Where do we want to go?", "forecasts"),
    ("How do we get there?", "resources, methods"), ("When? Who?", "schedules, people"),
    ("How much will it cost?", "budgets"),
], width=6.9, horizontal=True, title="Questions a plan answers, each fed by MIS", tone=0)

K.flow("c5_decision_steps.png", [
    ("Identify the problem", "exception reports"), ("Generate alternatives", "data, models"),
    ("Evaluate", "what-if, DSS"), ("Choose", ""), ("Monitor", "feedback"),
], width=6.9, horizontal=True, title="Decision making supported by information", tone=1)

K.pyramid("c5_levels4.png", ["Strategic", "Tactical control", "Operational control",
                             "Transaction processing"],
          notes=["policy; aggregate, external, yearly", "management control; summaries, monthly",
                 "day-to-day; detailed, daily", "every business event recorded"], width=3.3)

# ------------------------------------------------------------ 5.3
K.columns("c5_reports.png", [
    ("Detailed", ["confirms each transaction", "Eg detailed order report"], 0),
    ("Summary", ["totals, tables, graphs", "Eg inventory summary"], 1),
    ("Exception", ["only what is out of range", "Eg items below reorder level"], 2),
], width=3.3, wrap=12, item_h=0.3)

K.columns("c5_tps_modes.png", [
    ("Online processing", ["each transaction at once", "deposits, reservations", "most TPS today"], 0),
    ("Batch processing", ["grouped, run later", "paychecks, invoices", "efficient for bulk"], 2),
], width=3.3, wrap=22)

K.columns("c5_dss_sources.png", [
    ("Internal data", ["sales", "manufacturing", "inventory", "finance"], 1),
    ("External data", ["interest rates", "population trends", "construction costs",
                       "raw material prices"], 3),
], width=3.3, wrap=20)

K.flow("c5_expert.png", [
    ("User describes a situation", ""), ("Inference rules", "logical judgements"),
    ("Knowledge base", "experts' knowledge + experience"), ("Advice / decision", ""),
], width=6.9, horizontal=True, title="How an expert system reasons", tone=3)

# ------------------------------------------------------------ 5.4
K.columns("c5_computer_uses.png", [
    ("Data (transaction) processing", ["routine daily transactions", "predetermined reports",
                                       "less flexible: design needs carefully"], 0),
    ("End-user computing", ["managers, accountants, sales staff", "spreadsheets, queries",
                            "flexible, interactive"], 1),
], width=3.3, wrap=24)

K.columns("c5_quick_response.png", [
    ("Online", ["manager works directly", "with the computer"], 0),
    ("Real-time", ["runs with the activity", "Eg ATM, airline booking"], 1),
    ("Time sharing", ["many users share", "one computer"], 2),
], width=3.3, wrap=16)

K.hub("c5_database.png", "Customer database",
      ["Accounts", "Loans", "ATM", "Mobile banking", "Branch tellers", "Reports (MIS)"],
      width=2.9, ring=0.95, box=(0.7, 0.27), tone=2)

K.tree("c5_networks.png",
       ("Networks", [("By area", [("LAN", []), ("MAN", []), ("WAN", [])], 1),
                     ("By users", [("Internet", []), ("Intranet", []), ("Extranet", [])], 2)], 0),
       width=3.3, box_h=0.32, level_gap=0.2, wrap=10, fs=6.8)

K.columns("c5_organize.png", [
    ("Centralized", ["one IS department", "+ control, standards", "- slow, distant"], 0),
    ("Decentralized", ["IS in each department", "+ responsive", "- duplication, cost"], 2),
    ("Hybrid (distributed)", ["central data + standards", "local processing", "most common"], 1),
], width=6.9, wrap=22)

K.flow("c5_evolution.png", [
    ("Manual ledgers, punch cards", ""), ("EDP, 1959 on", "record keeping"),
    ("MIS reports", "1960s-70s"), ("DSS", "1970s, OR models"), ("EIS / ESS", "1980s"),
    ("PCs, end users", "GUI, direct use"), ("Networks, ERP", "integrated systems"),
    ("Internet, cloud, BI", ""),
], width=6.9, horizontal=True, title="Evolution of MIS", tone=0)
