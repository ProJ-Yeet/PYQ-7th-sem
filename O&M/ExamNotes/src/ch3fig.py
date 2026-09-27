# -*- coding: utf-8 -*-
"""Chapter 3 (Motivation, Leadership, Entrepreneurship) generated figures: the lists
and processes the notes print, where Adhikari's slides have text only. Source
figures (Maslow, Vroom, grid, styles, ERG table, Herzberg pair...) are cropped by
figs.py; the ERG progression/regression diagram is a Commons file (w_erg.png).

    python ch3fig.py
"""
import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

import diagkit as K

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------ 3.1
K.cycle("c3_need_cycle.png", ["Unsatisfied need", "Tension", "Drive (motive)",
                              "Goal-directed behaviour", "Need satisfied", "New need"],
        width=3.0, center="Need-drive-goal", R=1.0, box=(0.72, 0.27), tone=0)

K.columns("c3_needs_class.png", [
    ("Primary needs", ["Physiological: food, water, air, sleep",
                       "Safety: from harm, threat, danger"], 0),
    ("Secondary needs", ["Social: accepted, liked, loved", "Esteem: recognition, status",
                         "Self-realization: own capability"], 1),
], width=3.3, wrap=30)

K.hub("c3_types.png", "Types of motivation",
      ["Incentive (carrot)", "Fear (stick)", "Achievement", "Growth", "Power", "Social"],
      width=3.0, ring=0.95, box=(0.72, 0.27), tone=1)

K.columns("c3_techniques.png", [
    ("Financial", ["Money: wages, bonus", "incentives, profit share", "ESOP"], 2),
    ("Non-financial", ["appraisal, praise, recognition", "status and pride", "competition",
                       "delegation of authority", "participation", "job security",
                       "job enlargement", "quality of work life"], 1),
], width=3.3, wrap=24, item_h=0.17)

K.columns("c3_self_motivation.png", [
    ("Causes of decline", ["monotonous work", "driven by boss", "bad physical condition",
                           "poor relations", "money problems"], 2),
    ("Effects", ["unwilling to work", "seeks sympathy", "inferiority complex"], 3),
    ("Solutions", ["make the job interesting", "think constructively", "use strong points",
                   "adapt to the situation", "sound principles of life"], 1),
], width=6.9, wrap=22)

# ------------------------------------------------------------ 3.2
K.columns("c3_maslow_erg.png", [
    ("Maslow (5)", ["Self-actualization", "Esteem", "Social", "Safety", "Physiological"], 0),
    ("Alderfer ERG (3)", ["Growth", "Growth / Relatedness", "Relatedness",
                          "Existence", "Existence"], 1),
    ("Herzberg (2)", ["Motivators", "Motivators", "Hygiene", "Hygiene", "Hygiene"], 2),
], width=3.3, wrap=18)

K.columns("c3_xy.png", [
    ("Theory X workers", ["don't like working", "do as little as possible", "resist change",
                          "need to be told", "can't be trusted to decide",
                          "only interested in money", "must be closely watched"], 2),
    ("Theory Y workers", ["enjoy their work", "work hard for rewards", "want new things",
                          "work independently", "trusted to make decisions",
                          "motivated beyond money", "work unsupervised"], 1),
], width=3.3, wrap=26, item_h=0.17)

# Herzberg: two separate continua
fig, ax = plt.subplots(figsize=(3.3, 1.55))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.2)
ax.axis("off")
for y, left, right, col, lab in ((3.0, "Dissatisfaction", "No dissatisfaction", K.MKC,
                                  "Hygiene factors: pay, security, policy, supervision, conditions"),
                                 (0.9, "No satisfaction", "Satisfaction", K.GD,
                                  "Motivators: achievement, recognition, work itself, growth")):
    ax.add_patch(FancyArrowPatch((1.8, y), (8.2, y), arrowstyle="<|-|>", mutation_scale=10,
                                 lw=1.6, color=col))
    ax.text(1.7, y, left, ha="right", va="center", fontsize=6.8, color=K.INK)
    ax.text(8.3, y, right, ha="left", va="center", fontsize=6.8, color=K.INK)
    ax.text(5, y + 0.45, lab, ha="center", va="center", fontsize=6.5, color=col, fontweight="bold")
K._save(fig, "c3_herzberg_scales.png")

K.hub("c3_mcclelland.png", "Learned needs",
      ["Achievement: excel", "Power: influence others", "Affiliation: be liked"],
      width=2.6, ring=0.85, box=(0.78, 0.3), tone=3)

K.columns("c3_deterrence.png", [
    ("General deterrence", ["punishment is public", "aims at everyone else",
                            "deter future deviance"], 2),
    ("Specific deterrence", ["aims at the offender", "correct the behaviour",
                             "stop repeat offences"], 0),
], width=3.3, wrap=22)

# ------------------------------------------------------------ 3.3
K.hub("c3_leader_types.png", "Types of leaders",
      ["By position", "By personality, charisma", "By moral example", "By power held",
       "Intellectual", "By ability to get things done"],
      width=3.0, ring=0.98, box=(0.76, 0.28), tone=0)

K.hub("c3_qualities.png", "Good leader",
      ["Guiding vision", "Passion", "Integrity", "Honesty", "Trust", "Curiosity",
       "Calculated risk", "Dedication", "Charisma", "Listening"],
      width=3.3, ring=1.1, box=(0.66, 0.26), fs=6.6, tone=1)

K.grid("c3_mgr_vs_leader.png", ["Planning", "Organizing", "Directing", "Controlling"],
       ["Manager", "Leader"],
       [[("budgets, targets, detailed steps, allocates", ""), ("strategy, direction, vision", "")],
        [("structure, job descriptions, staffing, delegates", ""),
         ("gets people on board; communicates, networks", "")],
        [("solves problems, negotiates, builds consensus", ""), ("empowers people; cheerleader", "")],
        [("control systems, measures, fixes variances", ""),
         ("motivates, inspires, sense of accomplishment", "")]],
       width=3.3, tones=[[0, 1]] * 4, cell_h=0.4, wrap=26, fs=6.5)

K.hub("c3_style_factors.png", "Choice of style",
      ["The task", "Tradition of the firm", "Type of labour force", "Leader's personality",
       "Time available", "Followers' maturity"],
      width=3.0, ring=0.98, box=(0.74, 0.28), tone=2)

K.columns("c3_theories.png", [
    ("Born", ["Great Man", "Trait"], 0),
    ("Situation decides", ["Contingency", "Situational"], 1),
    ("Learned behaviour", ["Behavioural", "Participative"], 2),
    ("Exchange / inspiration", ["Management (transactional)", "Relationship (transformational)"], 3),
], width=6.9, wrap=22)

K.hub("c3_power.png", "Sources of power",
      ["Legitimate (position)", "Reward", "Coercive", "Expert", "Referent (charisma)"],
      width=2.8, ring=0.9, box=(0.76, 0.28), tone=3)

# ------------------------------------------------------------ 3.4
K.flow("c3_entre_functions.png", [
    ("See an opportunity", ""), ("Organize the enterprise", ""), ("Raise capital", ""),
    ("Hire labour", ""), ("Arrange materials", ""), ("Select managers", ""),
], width=6.9, horizontal=True, title="Functions of an entrepreneur (Adhikari)", tone=2)

K.flow("c3_edp.png", [
    ("Identify and select", "people who can be developed"),
    ("Develop capability", "motivation, training"),
    ("Choose a viable project", ""),
    ("Equip them", "administration, finance, management"),
    ("Link to support", "finance, infrastructure"),
], width=3.2, box_h=0.12, title="Entrepreneurship development programme", tone=1, wrap=60)

K.hub("c3_entre_chars.png", "Entrepreneur",
      ["Administrative capability", "Creativity", "Self-confidence", "Human relations",
       "Foresight", "Clear objectives", "Communication", "Technical knowledge", "Secrecy",
       "Optimism", "Decision making", "Risk taking"],
      width=3.3, ring=1.35, box=(0.64, 0.24), fs=6.2, tone=2)

K.flow("c3_small_scale.png", [
    ("Self-assessment", ""), ("Product / service + market research", ""),
    ("Feasibility, project report", ""), ("Form of ownership", ""), ("Location", ""),
    ("Registration, approvals", ""), ("Finance", ""), ("Land, building, machinery", ""),
    ("Recruit + train", ""), ("Materials, production, QC", ""), ("Marketing", ""),
    ("Monitor + improve", ""),
], width=2.8, box_h=0.08, title="Setting up a small scale unit", tone=0)

K.hub("c3_entre_role.png", "Small scale industry",
      ["Employment", "Meets rising demand", "Fair income distribution",
       "Balanced development", "Decentralization", "Better use of resources",
       "Self-employment"], width=3.2, ring=1.02, box=(0.74, 0.27), tone=1)

K.hub("c3_environment.png", "Conducive environment",
      ["Political stability", "Access to finance", "Infrastructure", "Easy registration",
       "Market access", "Skilled labour", "Culture that accepts failure", "Law enforcement"],
      width=3.2, ring=1.05, box=(0.72, 0.27), fs=6.6, tone=3)
