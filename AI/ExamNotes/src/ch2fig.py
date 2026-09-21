# -*- coding: utf-8 -*-
"""Draw the step-by-step solution under every chapter-2 numerical in ch2-num.tex.

Chapter 2's problems are crypt-arithmetic puzzles, water jugs, the river
crossing and tic-tac-toe. The notes argue each one in bullets; this script
draws the SAME chain, one panel per deduction, so the reader sees which
column each step reads and which letters it fixes.

Every crypt-arithmetic panel carries a coloured TECHNIQUE chip naming the
move the step makes (leading carry, max-sum bound, a carry of 2, adding two
column equations, substitution, cancellation, parity, case split, AllDiff),
and each puzzle's decisive step is framed as the KEY STEP. The chips are
the point: the same dozen moves solve every puzzle in 41 papers, and the
generated technique index at the top of the chapter says where each is used.

Like searchfig.py this draws the SOLUTION, never a source figure, and the
exit test is replay: every letter a panel fixes is checked against the final
assignment, every carry against the carries that assignment produces, every
final sum against the sum the .tex prints, every jug and river state against
a simulation of the rules and a BFS for the shortest path, and the
tic-tac-toe counts the notes quote (5,478 states; 3 and 12 distinct openings
up to symmetry) are recomputed.

    python ch2fig.py            regenerate every figure and its \\includegraphics block
    python ch2fig.py --report   run the checks only

Figures are PNGs so tools/anki_from_notes.py carries them onto the cards.
"""
import os
import re
import subprocess
import sys
from collections import deque

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "ch2-num.tex")
FIGS = os.path.join(HERE, "figs")
TECTONIC = os.path.join(HERE, "..", "..", "..", "Data Mining", "ExamNotes", "src",
                        "tectonic.exe")
BS = chr(92)
MARK = "% ch2fig:"
SLOT = "% ch2fig:slot "
DPI = 300
MAXPT = 515.0


# =====================================================================
#  Techniques: the moves every crypt-arithmetic chain is made of
# =====================================================================
TECH = {
    # key: (chip label, colour, what it means)
    "LEAD": ("leading carry", "tLEAD",
             "The answer is one digit longer than the addends, so its first digit "
             "is only a carry: it is 1."),
    "BOUND": ("sum bound", "tBOUND",
              "The largest a column or a whole sum can reach caps a letter "
              "(9+9+1 = 19; 999+999 = 1998)."),
    "CARRY2": ("carry = 2", "tCARRY2",
               "Three addends: a column can reach 9+9+9+1 = 28, so a carry may be 2."),
    "ADD": ("add columns", "tADD",
            "Add two column equations so the letters cancel and one unknown is left."),
    "SUBST": ("substitute", "tSUBST",
              "Put a relation found in one column into another column's equation."),
    "CANCEL": ("cancel", "tCANCEL",
               "The same letter on both sides of one column cancels (X+X = ..X)."),
    "PARITY": ("parity", "tPARITY",
               "2X is even: a digit that is the last digit of 2X is even, "
               "and an equation needing an odd 2X is impossible."),
    "CASES": ("case split", "tCASES",
              "Try each value a carry or letter can take and kill the ones that clash."),
    "ALLDIFF": ("AllDiff", "tALLDIFF",
                "A value already taken by another letter is ruled out."),
    "DOMAIN": ("narrow domain", "tDOMAIN",
               "Intersect the few digits still unused with what the column allows."),
    "LINK": ("link letters", "tLINK",
             "One column ties two letters together (X = M+1, R = 2W+c)."),
    "ARITH": ("arithmetic", "tARITH",
              "Everything else in the column is known: just add."),
    "CHOOSE": ("free choice", "tCHOOSE",
               "The constraints do not fix this letter: say so, then pick a value."),
    "CHECK": ("carry check", "tCHECK",
              "Confirm the carry an earlier column assumed is the one produced."),
}
TECH_ORDER = ["LEAD", "BOUND", "CARRY2", "ADD", "SUBST", "CANCEL", "PARITY",
              "CASES", "ALLDIFF", "DOMAIN", "LINK", "ARITH", "CHOOSE", "CHECK"]


# =====================================================================
#  The crypt-arithmetic chains, step for step as ch2-num.tex prints them
# =====================================================================
# A step: (title, techniques, columns read, letters fixed, carries fixed,
#          the one-line argument, key step?)
# Column k is counted from the units end; carry c_k is the carry OUT of k.
def S(title, tech, cols, fix=None, car=None, eq="", key=False):
    return dict(title=title, tech=tech, cols=cols, fix=fix or {}, car=car or {},
                eq=eq, key=key)


PUZZLES = [
    dict(name="c2_step_send", add=["SEND", "MORE"], res="MONEY", c="C",
         sol=dict(S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2),
         sum="9567 + 1085 = 10652", per=4,
         steps=[
             S("$M = 1$", ["LEAD"], [5], dict(M=1), {4: 1},
               r"$C_4 = M$, a carry is at most 1, and $M \neq 0$ leads MONEY."),
             S("$O = 0$", ["BOUND", "ALLDIFF"], [4], dict(O=0), {},
               r"$S + 1 + C_3 \leq 9+1+1 = 11$, so $O \in \{0,1\}$; 1 is $M$'s."),
             S("$S = 9$, $C_3 = 0$", ["CASES", "ALLDIFF"], [4, 3], dict(S=9), {3: 0},
               r"$C_3 = 1$ needs $E + C_2 = 10$, so $N = 0 = O$. Hence $C_3 = 0$, $S + 1 = 10$."),
             S("$N = E + 1$, $C_2 = 1$", ["LINK", "ALLDIFF"], [3], {}, {2: 1},
               r"Column 3: $E + C_2 = N$. $C_2 = 0$ would give $E = N$."),
             S("$R = 8$, $C_1 = 1$", ["SUBST", "ALLDIFF"], [2], dict(R=8), {1: 1},
               r"$N + R + C_1 = 10 + E$; put $N = E+1$: $R + C_1 = 9$. $R = 9$ is $S$'s.",
               key=True),
             S("$D = 7$", ["BOUND", "CASES"], [1], dict(D=7), {},
               r"$D + E = 10 + Y \geq 12$ from $\{2..7\}$: $5{+}7$ or $6{+}7$. $E = 7$ gives $N = 8 = R$."),
             S("$E = 5$, $N = 6$, $Y = 2$", ["ALLDIFF", "ARITH"], [1, 3],
               dict(E=5, N=6, Y=2), {},
               r"$E = 6$ gives $N = 7 = D$. So $E = 5$, $N = 6$, $Y = 12 - 10 = 2$."),
         ]),
    dict(name="c2_step_base", add=["BASE", "BALL"], res="GAMES", c="C",
         sol=dict(B=7, A=4, S=8, E=3, L=5, G=1, M=9),
         sum="7483 + 7455 = 14938", per=3,
         steps=[
             S("$G = 1$", ["LEAD"], [5], dict(G=1), {4: 1},
               r"Two 4-digit numbers stay under 20000, so $C_4 = G = 1$."),
             S("$L = 5$, $C_1 = 0$, $C_2 = 1$", ["ADD", "PARITY"], [1, 2], dict(L=5),
               {1: 0, 2: 1},
               r"Add columns 1 and 2: $E, S$ cancel, $2L = 9C_1 + 10C_2$. Even, so $C_1 = 0$; $L = 0$ makes $E = S$.",
               key=True),
             S("$S = E + 5$", ["LINK", "DOMAIN"], [1], {}, {},
               r"Column 1: $E + 5 = S$, so $E \in \{2,3,4\}$ ($E = 0$ gives $S = 5 = L$)."),
             S("$E = 3$, $S = 8$", ["CASES"], [3, 4], dict(E=3, S=8), {},
               r"$E = 2$: forces $B = 7 = S$. $E = 4$: every branch needs $2B$ odd."),
             S("$M = 9$, $A = 4$", ["PARITY", "ALLDIFF"], [3], dict(M=9, A=4), {3: 0},
               r"$2A + 1 = 10C_3 + M$: $M$ is odd and unused, so $M = 9$, $A = 4$, $C_3 = 0$."),
             S("$B = 7$", ["ARITH"], [4], dict(B=7), {},
               r"$2B + C_3 = 10 + A = 14$, so $B = 7$."),
         ]),
    dict(name="c2_step_ten", add=["TEN", "TEN", "FORTY"], res="SIXTY", c="C",
         sol=dict(T=8, E=5, N=0, F=2, O=9, R=7, Y=6, S=3, I=1, X=4),
         sum="850 + 850 + 29786 = 31486", per=3,
         steps=[
             S("$N \\in \\{0, 5\\}$", ["CANCEL"], [1], {}, {},
               r"$2N + Y = 10C_1 + Y$: $Y$ cancels, $2N = 10C_1$."),
             S("$N = 0$, $E = 5$, $C_2 = 1$", ["CANCEL", "PARITY"], [2], dict(N=0, E=5),
               {1: 0, 2: 1},
               r"$T$ cancels: $2E + C_1 = 10C_2$. $N = 5$ makes $C_1 = 1$ and $2E$ odd."),
             S("$C_4 = 1$, $S = F + 1$", ["ALLDIFF", "LINK"], [5], {}, {4: 1},
               r"$F + C_4 = S$ and $F \neq S$, so $C_4 = 1$."),
             S("$O = 9$, $C_3 = 2$, $I = 1$", ["CARRY2", "CASES"], [4, 3], dict(O=9, I=1),
               {3: 2},
               r"Column 3 reaches $9{+}9{+}9{+}1 = 28$: $C_3$ may be \textbf{2}. $O + C_3 = 10 + I$; $(8,2)$ and $(9,1)$ give $I = 0 = N$.",
               key=True),
             S("$T = 8$, $R = 7$, $X = 4$", ["DOMAIN"], [3], dict(T=8, R=7, X=4), {},
               r"$2T + R = 19 + X$ with $\{2,3,4,6,7,8\}$ left: $T = 8$, $R = X + 3 = 7$."),
             S("$F = 2$, $S = 3$, $Y = 6$", ["ALLDIFF", "LINK"], [5, 1],
               dict(F=2, S=3, Y=6), {},
               r"$\{2,3,6\}$ remain and $S = F + 1$."),
         ]),
    dict(name="c2_step_logic", add=["LOGIC", "LOGIC"], res="PROLOG", c="a",
         sol=dict(L=9, O=0, G=4, I=5, C=2, P=1, R=8),
         sum="90452 + 90452 = 180904", per=3,
         steps=[
             S("$P = 1$", ["LEAD"], [6], dict(P=1), {5: 1},
               r"$2 \times$ LOGIC $< 200000$, so $a_5 = P = 1$."),
             S("$O = 0$, $a_3 = a_4 = 0$", ["CANCEL", "CASES"], [4], dict(O=0),
               {3: 0, 4: 0},
               r"$2O + a_3 = 10a_4 + O$: $O + a_3 = 10a_4$. The branch $O = 9$ dies at the end."),
             S("$I = 5$, $a_2 = 1$", ["ALLDIFF", "PARITY"], [2], dict(I=5), {1: 0, 2: 1},
               r"$2I + a_1 = 10a_2$; $a_2 = 0$ gives $I = 0 = O$; $a_1$ even, so 0."),
             S("$G = 2C$, $L = 4C + 1$", ["SUBST"], [1, 3], {}, {},
               r"Col 1: $G = 2C$. Col 3: $L = 2G + 1$; substitute: $L = 4C + 1$.",
               key=True),
             S("$R = 8C - 8$", ["SUBST"], [5], {}, {},
               r"Col 5: $2L + 0 = 10 + R$, and $L = 4C+1$ gives $R = 8C - 8$."),
             S("$C = 2$: $G = 4$, $L = 9$, $R = 8$", ["BOUND", "ALLDIFF"], [1, 3, 5],
               dict(C=2, G=4, L=9, R=8), {},
               r"$4C + 1 \leq 9$ so $C \leq 2$; $C = 0$ is $O$'s, $C = 1$ gives $L = 5 = I$."),
         ]),
    dict(name="c2_step_eat", add=["EAT", "THAT"], res="APPLE", c="C",
         sol=dict(E=8, A=1, T=9, H=2, P=0, L=3),
         sum="819 + 9219 = 10038", per=3,
         steps=[
             S("$A = 1$", ["LEAD", "BOUND"], [5], dict(A=1), {4: 1},
               r"$999 + 9999 = 10998$, so the 5-digit answer begins with 1."),
             S("$T = 9$", ["BOUND"], [4], dict(T=9), {},
               r"Sum $\geq 10000$, so THAT $\geq 10000 - 999 = 9001$.", key=True),
             S("$E = 8$, $C_1 = 1$", ["ARITH"], [1], dict(E=8), {1: 1},
               r"$9 + 9 = 18$."),
             S("$L = 3$, $C_2 = 0$", ["ARITH"], [2], dict(L=3), {2: 0},
               r"$1 + 1 + 1 = 3$."),
             S("$P = 0$, $C_3 = 1$", ["BOUND"], [4], dict(P=0), {3: 1},
               r"$9 + C_3 = 10 + P$, and a carry is at most 1."),
             S("$H = 2$", ["ARITH"], [3], dict(H=2), {},
               r"$8 + H + 0 = 10 + 0$."),
         ]),
    dict(name="c2_step_cross", add=["CROSS", "ROADS"], res="DANGER", c="a",
         sol=dict(C=9, R=6, O=2, S=3, A=5, D=1, N=8, G=7, E=4),
         sum="96233 + 62513 = 158746", per=4,
         steps=[
             S("$D = 1$", ["LEAD"], [6], dict(D=1), {5: 1},
               r"Two 5-digit numbers stay under 200000, so $a_5 = D = 1$."),
             S("$R$ is even", ["PARITY"], [1], {}, {},
               r"$R$ is the last digit of $2S$."),
             S("$C, R$ both large", ["BOUND"], [5], {}, {},
               r"$C + R + a_4 = A + 10$ with $C, R \leq 9$."),
             S("the one assignment", ["CASES", "CHECK"], [1, 2, 3, 4, 5],
               dict(C=9, R=6, O=2, S=3, A=5, D=1, N=8, G=7, E=4),
               {1: 0, 2: 0, 3: 0, 4: 0},
               r"Propagating column by column leaves one assignment; every column checks, $a_1..a_4 = 0$.",
               key=True),
         ]),
    dict(name="c2_step_love", add=["LOVE", "LOVE"], res="HATE", c="C",
         sol=dict(L=3, O=5, V=6, E=0, H=7, A=1, T=2),
         sum="3560+3560=7120", per=4, multi=True,
         steps=[
             S("$E = 0$", ["CANCEL"], [1], dict(E=0), {1: 0},
               r"$E + E = 10C_1 + E$: $E = 10C_1$, a digit, so 0.", key=True),
             S("$T$ even", ["PARITY"], [2], {}, {},
               r"$2V + 0 = 10C_2 + T$."),
             S("$L \\leq 4$", ["BOUND"], [4], {}, {},
               r"$2L + C_3 = H \leq 9$. Nothing else is forced."),
             S("choose $L, O, V = 3, 5, 6$", ["CHOOSE", "CHECK"], [2, 3, 4],
               dict(L=3, O=5, V=6, T=2, A=1, H=7), {2: 1, 3: 1},
               r"$T = 2$, $A = 11 - 10 = 1$, $H = 6 + 1 = 7$."),
         ]),
    dict(name="c2_step_one", add=["ONE", "ONE", "TWO"], res="FOUR", c="c",
         sol=dict(O=6, N=4, E=2, T=3, W=8, F=1, U=7, R=0),
         sum="642 + 642 + 386 = 1670", per=3, multi=True,
         steps=[
             S("$F$ is a carry", ["LEAD"], [4], {}, {},
               r"3-digit addends, 4-digit FOUR: $F = c_3 \geq 1$."),
             S("$O + T + c_2 = 10F$", ["CANCEL"], [3], {}, {},
               r"Column 3: $2O + T + c_2 = 10F + O$; one $O$ cancels."),
             S("$F = 1$, not 2", ["BOUND", "CARRY2"], [3], dict(F=1), {3: 1},
               r"Three addends, so $c_2 \leq 2$; still $O + T + c_2 \leq 9{+}8{+}2 = 19 < 20$.",
               key=True),
             S("choose $E = 2$, $O = 6$", ["CHOOSE"], [1], dict(E=2, O=6, R=0), {1: 1},
               r"$4 + 6 = 10$: $R = 0$, $c_1 = 1$."),
             S("$T = 3$", ["CHOOSE", "LINK"], [3], dict(T=3), {2: 1},
               r"$6 + T + c_2 = 10$: take $c_2 = 1$, $T = 3$."),
             S("$N = 4$, $W = 8$: $U = 7$", ["CHOOSE", "CHECK"], [2],
               dict(N=4, W=8, U=7), {},
               r"$8 + 8 + 1 = 17$: $U = 7$ and $c_2 = 1$ as assumed."),
         ]),
    dict(name="c2_step_wrong", add=["WRONG", "WRONG"], res="RIGHT", c="c",
         sol=dict(W=3, R=7, O=0, N=8, G=1, I=4, H=6, T=2),
         sum="37081 + 37081 = 74162", per=4, multi=True,
         steps=[
             S("$W \\leq 4$", ["BOUND"], [5], {}, {},
               r"No sixth digit: $2 \times$ WRONG $< 100000$. The only bound.", key=True),
             S("$R = 2W + c_4$", ["LINK"], [5], {}, {},
               r"Column 5 pins $R$ once $W$ and $c_4$ are chosen."),
             S("$T$ even", ["PARITY"], [1], {}, {},
               r"$2G = 10c_1 + T$."),
             S("choose $W = 3$, $c_4 = 1$", ["CHOOSE"], [5], dict(W=3, R=7), {4: 1},
               r"$R = 6 + 1 = 7$."),
             S("$G = 1$: $T = 2$", ["CHOOSE"], [1], dict(G=1, T=2), {1: 0},
               r"$2 \cdot 1 = 2$, no carry."),
             S("$N = 8$: $H = 6$", ["CHOOSE"], [2], dict(N=8, H=6), {2: 1},
               r"$16$: $H = 6$, $c_2 = 1$."),
             S("$O = 0$ gives $G = 1$", ["CHECK"], [3], dict(O=0), {3: 0},
               r"$0 + 1 = 1 = G$, the value column 1 chose."),
             S("$I = 4$, $c_4 = 1$", ["CHECK"], [4], dict(I=4), {},
               r"$2(7) + 0 = 14$: carry 1, what column 5 assumed."),
         ]),
    dict(name="c2_step_swim", add=["SWIM", "WEAR"], res="RELAX", c="c",
         sol=dict(S=9, W=4, I=0, M=5, E=3, A=2, R=1, L=7, X=6),
         sum="9405 + 4321 = 13726", per=4, multi=True,
         steps=[
             S("$R = 1$", ["LEAD"], [5], dict(R=1), {4: 1},
               r"Two 4-digit numbers, a 5-digit answer."),
             S("$I + c_1 = 10c_2$", ["CANCEL"], [2], {}, {},
               r"Column 2: $I + A + c_1 = 10c_2 + A$; $A$ cancels."),
             S("$I = 0$", ["CASES", "ALLDIFF"], [2, 1], dict(I=0), {1: 0, 2: 0},
               r"$c_2 = 1$: $I = 9$, $c_1 = 1$, then $M = 9 + X$ needs $M = 9 = I$.",
               key=True),
             S("$X = M + 1$", ["LINK"], [1], {}, {},
               r"Column 1 with $c_1 = 0$: $M + 1 = X$."),
             S("choose $W = 4$, $E = 3$: $S = 9$", ["CHOOSE"], [4], dict(W=4, E=3, S=9),
               {3: 0},
               r"Column 4: $S + W + c_3 = 10 + E$, with $c_3 = 0$."),
             S("$L = 7$", ["CHECK"], [3], dict(L=7), {},
               r"$4 + 3 + 0 = 7$, $c_3 = 0$ as assumed."),
             S("$A = 2$, $M = 5$, $X = 6$", ["CHOOSE", "LINK"], [1, 2],
               dict(A=2, M=5, X=6), {},
               r"$A$ meets only AllDiff. $X = M + 1$."),
         ]),
    dict(name="c2_step_right", add=["RIGHT", "RIGHT"], res="WRONG", c="c",
         sol=dict(R=4, I=2, G=0, H=6, T=5, W=8, O=1, N=3),
         sum="42065 + 42065 = 84130", per=4, multi=True,
         steps=[
             S("$R \\leq 4$", ["BOUND"], [5], {}, {},
               r"Five digits both sides: $2 \times$ RIGHT $< 100000$."),
             S("$W = 2R + c_4$", ["LINK"], [5], {}, {}, r"Column 5."),
             S("$G$ even", ["PARITY"], [1], {}, {},
               r"$2T = 10c_1 + G$. Column 3 feeds on this $G$.", key=True),
             S("choose $R = 4$, $c_4 = 0$", ["CHOOSE"], [5], dict(R=4, W=8), {4: 0},
               r"$W = 8$."),
             S("$T = 5$: $G = 0$", ["CHOOSE"], [1], dict(T=5, G=0), {1: 1},
               r"$10$: $G = 0$, $c_1 = 1$."),
             S("$H = 6$: $N = 3$", ["CHOOSE"], [2], dict(H=6, N=3), {2: 1},
               r"$12 + 1 = 13$."),
             S("$O = 1$", ["ARITH"], [3], dict(O=1), {3: 0},
               r"$2(0) + 1 = 1$."),
             S("$I = 2$, $c_4 = 0$", ["CHECK"], [4], dict(I=2), {},
               r"$2I + 0 = 4 = R$: carry 0, as column 5 assumed."),
         ]),
    dict(name="c2_step_two", add=["TWO", "TWO"], res="FOUR", c="c",
         sol=dict(T=7, W=3, O=4, F=1, U=6, R=8),
         sum="734 + 734 = 1468", per=3, multi=True,
         steps=[
             S("$F = 1$", ["LEAD", "BOUND"], [4], dict(F=1), {3: 1},
               r"$999 + 999 = 1998$."),
             S("$T \\geq 5$", ["BOUND"], [3], {}, {},
               r"$2T + c_2 = 10 + O$ with $c_2 \leq 1$.", key=True),
             S("$R$ even", ["PARITY"], [1], {}, {}, r"$2O = 10c_1 + R$."),
             S("choose $T = 7$, $c_2 = 0$", ["CHOOSE"], [3], dict(T=7, O=4), {2: 0},
               r"$14 = 10 + O$: $O = 4$."),
             S("$R = 8$", ["ARITH"], [1], dict(R=8), {1: 0}, r"$2(4) = 8$."),
             S("$W = 3$: $U = 6$", ["CHOOSE", "CHECK"], [2], dict(W=3, U=6), {},
               r"$U = 2W$; $c_2 = 0$ as assumed."),
         ]),
]


def carries(add, res, sol):
    """{k: carry out of column k}, asserting every column adds up."""
    n = len(res)
    out, c = {}, 0
    for k in range(1, n + 1):
        s = c + sum(sol[w[-k]] for w in add if len(w) >= k)
        assert s % 10 == sol[res[-k]], (res, k, s)
        c = s // 10
        if k < n:
            out[k] = c
    assert c == 0, (res, "overflow")
    return out


def check_puzzle(p, tex):
    add, res, sol = p["add"], p["res"], p["sol"]
    letters = set("".join(add) + res)
    assert set(sol) == letters, (p["name"], letters ^ set(sol))
    assert len(set(sol.values())) == len(sol), (p["name"], "not all different")
    for w in add + [res]:
        assert sol[w[0]] != 0, (p["name"], w)
    car = carries(add, res, sol)
    nums = [int("".join(str(sol[ch]) for ch in w)) for w in add + [res]]
    assert sum(nums[:-1]) == nums[-1]
    printed = " + ".join(str(x) for x in nums[:-1]) + " = " + str(nums[-1])
    flat = re.sub(r"\s", "", tex)
    assert re.sub(r"\s", "", printed) in flat, (p["name"], printed)
    assert re.sub(r"\s", "", p["sum"]) == re.sub(r"\s", "", printed)
    for st in p["steps"]:
        for ch, v in st["fix"].items():
            assert sol[ch] == v, (p["name"], st["title"], ch)
        for k, v in st["car"].items():
            assert car[k] == v, (p["name"], st["title"], k, car[k])
        for t in st["tech"]:
            assert t in TECH, t
    known = set()
    for st in p["steps"]:
        known |= set(st["fix"])
    assert known == letters, (p["name"], "never fixed", letters - known)
    assert sum(st["key"] for st in p["steps"]) == 1, p["name"]
    return car


# =====================================================================
#  Drawing: shared
# =====================================================================
PRE = r"""\documentclass[border=4pt, multi=panelbox]{standalone}
\usepackage[default]{lato}
\usepackage{amsmath, amssymb, xcolor, tikz, array}
\usetikzlibrary{arrows.meta, positioning}
\definecolor{ink}{HTML}{16202A}\definecolor{sub}{HTML}{6B7785}
\definecolor{acc}{HTML}{2563A8}\definecolor{accL}{HTML}{D6E4F5}
\definecolor{mkc}{HTML}{C2410C}\definecolor{mkL}{HTML}{FDEBD9}
\definecolor{gd}{HTML}{15803D}\definecolor{gdL}{HTML}{DCFCE7}
\definecolor{ruleL}{HTML}{DEE3E8}\definecolor{rowL}{HTML}{F4F7FA}
\definecolor{water}{HTML}{93C5FD}\definecolor{waterD}{HTML}{3B82F6}
\definecolor{bank}{HTML}{E7EFE3}
\definecolor{tLEAD}{HTML}{2563A8}\definecolor{tBOUND}{HTML}{6D28D9}
\definecolor{tCARRY2}{HTML}{DC2626}\definecolor{tADD}{HTML}{B45309}
\definecolor{tSUBST}{HTML}{BE185D}\definecolor{tCANCEL}{HTML}{0F766E}
\definecolor{tPARITY}{HTML}{0369A1}\definecolor{tCASES}{HTML}{4D7C0F}
\definecolor{tALLDIFF}{HTML}{7C2D12}\definecolor{tDOMAIN}{HTML}{475569}
\definecolor{tLINK}{HTML}{0E7490}\definecolor{tARITH}{HTML}{334155}
\definecolor{tCHOOSE}{HTML}{8A94A0}\definecolor{tCHECK}{HTML}{15803D}
\newenvironment{panelbox}{}{}
\tikzset{
  chip/.style={rounded corners=1.5pt, text=white, font=\tiny\bfseries,
               inner xsep=2pt, inner ysep=1.2pt, anchor=north west},
  cell/.style={minimum width=4.6mm, minimum height=4.6mm, inner sep=0pt,
               rounded corners=1pt},
  lt/.style={cell, draw=ruleL, text=sub, font=\scriptsize},
  dg/.style={cell, draw=ruleL, fill=white, text=ink, font=\scriptsize\bfseries},
  nw/.style={cell, draw=mkc, fill=mkL, text=ink, font=\scriptsize\bfseries,
             line width=0.7pt},
  cy/.style={font=\tiny, text=sub, inner sep=0.5pt},
  cyn/.style={font=\tiny\bfseries, text=mkc, inner sep=0.5pt},
  cy2/.style={font=\tiny\bfseries, text=white, fill=tCARRY2, rounded corners=1pt,
              inner sep=1pt},
  frame/.style={draw=ruleL, rounded corners=2pt, line width=0.4pt},
  keyf/.style={draw=mkc, rounded corners=2pt, line width=1.1pt},
  keytag/.style={font=\tiny\bfseries, text=white, fill=mkc, rounded corners=1pt,
                 inner sep=1.2pt, anchor=south east},
  eqn/.style={font=\tiny, text=ink, align=flush left, anchor=north west, inner sep=0pt},
  ttl/.style={font=\scriptsize\bfseries, text=acc, anchor=north west, inner sep=0pt},
}
\begin{document}
"""


def chips(techs, x, y):
    """Chips chained left to right from (x, y)."""
    L, prev = [], None
    for i, t in enumerate(techs):
        lab, col, _ = TECH[t]
        where = "(%.2f,%.2f)" % (x, y) if prev is None else "([xshift=1pt]%s.north east)" % prev
        L.append(r"\node[chip, fill=%s] (k%d) at %s {%s};" % (col, i, where, lab))
        prev = "k%d" % i
    return L


def frame(L, x0, y0, x1, y1, key):
    L.insert(1, r"\path[use as bounding box] (%.2f,%.2f) rectangle (%.2f,%.2f);"
             % (x0 - 0.12, y0 - 0.08, x1 + 0.12, y1 + 0.12))
    L.append(r"\draw[%s] (%.2f,%.2f) rectangle (%.2f,%.2f);"
             % ("keyf" if key else "frame", x0 - 0.08, y0 - 0.04, x1 + 0.08, y1 + 0.08))
    if key:
        L.append(r"\node[keytag] at (%.2f,%.2f) {KEY STEP};" % (x1 + 0.08, y0 - 0.04))


def grid(panels, per_row, legend_tikz):
    rows = [panels[i:i + per_row] for i in range(0, len(panels), per_row)]
    L = [r"\begin{panelbox}",
         r"\setlength{\tabcolsep}{1.2mm}\renewcommand{\arraystretch}{1.3}",
         r"\begin{tabular}{@{}" + "c" * per_row + r"@{}}"]
    for r in rows:
        pad = per_row - len(r)
        cells = [""] * (pad // 2) + list(r) + [""] * (pad - pad // 2)
        L.append(" &\n".join(cells) + r" \\")
    L.append(r"\end{tabular}")
    if legend_tikz:
        # outside the panel tabular: a wide legend in a multicolumn would
        # widen the last column and open a gap before the last panel
        L.insert(1, r"\begin{tabular}{@{}c@{}}")
        L.append(r"\\[1pt]" + legend_tikz)
        L.append(r"\end{tabular}")
    L.append(r"\end{panelbox}")
    return "\n".join(L)


# =====================================================================
#  Crypt-arithmetic panels
# =====================================================================
CW = 0.56          # column pitch, cm


def crypt_panel(p, k, st, known, kcar):
    add, res = p["add"], p["res"]
    n = len(res)
    W = (n + 1) * CW
    x0, x1 = -CW, n * CW
    colx = {c: (n - c) * CW + CW / 2 for c in range(1, n + 1)}
    y_car = -0.98
    y_add = [-1.42 - i * 0.50 for i in range(len(add))]
    y_line = y_add[-1] - 0.28
    y_res = y_line - 0.30
    y_eq = y_res - 0.38
    y0 = y_eq - p.get("eqh", 0.95)
    L = [r"\begin{tikzpicture}"]
    L.append(r"\node[ttl, text width=%.2fcm] at (%.2f,0) {%d.\, %s};"
             % (W - 0.1, x0, k, st["title"]))
    L += chips(st["tech"], x0, -0.42)
    # the columns this step reads
    for c in st["cols"]:
        L.append(r"\fill[accL, rounded corners=1.5pt] (%.2f,%.2f) rectangle (%.2f,%.2f);"
                 % (colx[c] - CW / 2 + 0.02, y_res - 0.30, colx[c] + CW / 2 - 0.02,
                    y_car + 0.20))
    # carry row: c_k sits over column k+1
    for c in range(1, n):
        x = colx[c + 1]
        if c in kcar:
            v = kcar[c]
            sty = "cy2" if v == 2 else ("cyn" if c in st["car"] else "cy")
            L.append(r"\node[%s] at (%.2f,%.2f) {%d};" % (sty, x, y_car, v))
        else:
            L.append(r"\node[cy] at (%.2f,%.2f) {$%s_{%d}$};" % (x, y_car, p["c"], c))

    def put(word, y):
        for i, ch in enumerate(reversed(word), 1):
            x = colx[i]
            if ch in known:
                sty = "nw" if ch in st["fix"] else "dg"
                L.append(r"\node[%s] at (%.2f,%.2f) {%d};" % (sty, x, y, known[ch]))
                L.append(r"\node[font=\fontsize{3.6}{4}\selectfont, text=sub,"
                         r" inner sep=0pt, anchor=north west] at (%.2f,%.2f) {%s};"
                         % (x - 0.225, y + 0.225, ch))
            else:
                L.append(r"\node[lt] at (%.2f,%.2f) {%s};" % (x, y, ch))

    for i, (w, y) in enumerate(zip(add, y_add)):
        put(w, y)
        if i:
            L.append(r"\node[font=\scriptsize, text=sub] at (%.2f,%.2f) {$+$};"
                     % (x0 + CW / 2, y))
    L.append(r"\draw[ink, line width=0.5pt] (%.2f,%.2f) -- (%.2f,%.2f);"
             % (colx[n] - CW / 2, y_line, x1, y_line))
    put(res, y_res)
    L.append(r"\node[eqn, text width=%.2fcm] at (%.2f,%.2f) {%s};"
             % (W, x0, y_eq, st["eq"]))
    frame(L, x0, y0, x1, 0.0, st["key"])
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def crypt_legend(techs):
    L = [r"\begin{tikzpicture}"]
    L.append(r"\node[dg, minimum size=3.4mm] (a) at (0,0) {5};")
    L.append(r"\node[cy, anchor=west] (at) at ([xshift=1mm]a.east) {fixed};")
    L.append(r"\node[nw, minimum size=3.4mm, anchor=west] (b) at ([xshift=3mm]at.east) {5};")
    L.append(r"\node[cy, anchor=west] (bt) at ([xshift=1mm]b.east) {fixed this step};")
    L.append(r"\node[fill=accL, minimum width=3.4mm, minimum height=3.4mm, inner sep=0pt,"
             r" anchor=west] (c) at ([xshift=3mm]bt.east) {};")
    L.append(r"\node[cy, anchor=west] (ct) at ([xshift=1mm]c.east) {column read};")
    L.append(r"\node[keytag, anchor=west] (d) at ([xshift=3mm]ct.east) {KEY STEP};")
    L.append(r"\node[cy, anchor=west] (dt) at ([xshift=1mm]d.east) {the decisive move};")
    prev = "dt"
    for i, t in enumerate(techs):
        lab, col, _ = TECH[t]
        L.append(r"\node[chip, fill=%s, anchor=west] (t%d) at ([xshift=%s]%s.east) {%s};"
                 % (col, i, "3mm" if i == 0 else "1pt", prev, lab))
        prev = "t%d" % i
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def crypt_figure(p):
    known, kcar, panels = {}, {}, []
    for k, st in enumerate(p["steps"], 1):
        known.update(st["fix"])
        kcar.update(st["car"])
        panels.append(crypt_panel(p, k, st, dict(known), dict(kcar)))
    techs = [t for t in TECH_ORDER if any(t in st["tech"] for st in p["steps"])]
    return grid(panels, p["per"], crypt_legend(techs))


# ---------------------------------------------------------------------
#  AB + CD = AAA
# ---------------------------------------------------------------------
def ab_values():
    """Every (A,B,C,D), all different, with AB + CD = AAA and A, C != 0."""
    out = {}
    for a in range(1, 10):
        for b in range(10):
            for c in range(1, 10):
                for d in range(10):
                    if len({a, b, c, d}) == 4 and 10 * a + b + 10 * c + d == 111 * a:
                        out.setdefault(b, []).append((a, c, d))
    return out


def ab_figure():
    vals = ab_values()
    assert sorted(vals) == [3, 4, 5, 6, 7, 8], sorted(vals)
    assert all(v == [(1, 9, 11 - b)] for b, v in vals.items()), vals
    p = dict(add=["AB", "CD"], res="AAA", c="c", eqh=0.75)
    s1 = S("$A = 1$", ["BOUND"], [3], dict(A=1), {2: 1},
           r"$99 + 99 = 198$, and the only repdigit in range is 111.")
    s2 = S("CD $= 101 - B$", ["SUBST"], [1, 2], dict(C=9), {},
           r"AB $= 10 + B$, so CD $= 111 - (10 + B)$. For $B \geq 2$ CD is in the 90s: $C = 9$.")
    pan = [crypt_panel(p, 1, s1, dict(A=1), {2: 1}),
           crypt_panel(p, 2, s2, dict(A=1, C=9), {2: 1})]
    # the strip of every B
    L = [r"\begin{tikzpicture}"]
    L.append(r"\node[ttl] at (-0.3,0) {3.\, test every $B$};")
    L += chips(["ALLDIFF", "BOUND"], -0.3, -0.42)
    why = {0: "CD\\,=\\,101", 1: "B\\,=\\,A", 2: "C\\,=\\,D\\,=\\,9", 9: "B\\,=\\,C\\,=\\,9"}
    for b in range(10):
        x = b * 0.78
        ok = b in vals
        L.append(r"\node[cell, minimum size=5.4mm, draw=%s, fill=%s, text=ink,"
                 r" font=\scriptsize\bfseries] at (%.2f,-1.25) {%d};"
                 % ("gd" if ok else "mkc", "gdL" if ok else "mkL", x, b))
        if ok:
            L.append(r"\node[cy, align=center] at (%.2f,-1.95) {%d\\$+$%d};"
                     % (x, 10 + b, 101 - b))
        else:
            L.append(r"\node[font=\tiny, text=mkc, align=center, text width=0.75cm]"
                     r" at (%.2f,-1.95) {%s};" % (x, why[b]))
    L.append(r"\node[eqn, text width=7.5cm] at (-0.3,-2.45) {Survivors: "
             r"$B \in \{3,4,5,6,7,8\}$. $B = 9$ is the case that is easy to miss.};")
    frame(L, -0.45, -2.85, 7.5, 0.0, True)
    L.append(r"\end{tikzpicture}")
    pan.append("\n".join(L))
    extra = (r"\multicolumn{2}{@{}c@{}}{" + pan[2] + r"} \\" + "\n"
             + r"\multicolumn{2}{@{}c@{}}{" + crypt_legend(["BOUND", "SUBST", "ALLDIFF"])
             + r"} \\" + "\n")
    return grid(pan[:2], 2, "").replace(r"\end{tabular}", extra + r"\end{tabular}")


# =====================================================================
#  Water jugs
# =====================================================================
def jug_rules(x, y, X, Y):
    """The eight production rules of the notes, for capacities X > Y."""
    out = []
    if x < X: out.append((1, (X, y)))
    if y < Y: out.append((2, (x, Y)))
    if x > 0: out.append((3, (0, y)))
    if y > 0: out.append((4, (x, 0)))
    if x + y >= X and y > 0: out.append((5, (X, y - (X - x))))
    if x + y >= Y and x > 0: out.append((6, (x - (Y - y), Y)))
    if x + y <= X and y > 0: out.append((7, (x + y, 0)))
    if x + y <= Y and x > 0: out.append((8, (0, x + y)))
    return out


def bfs_len(start, succ, goal):
    seen, q = {start: 0}, deque([start])
    while q:
        s = q.popleft()
        if goal(s):
            return seen[s]
        for _, t in succ(s):
            if t not in seen:
                seen[t] = seen[s] + 1
                q.append(t)
    return None


def replay_jug(rules, X, Y):
    s, out = (0, 0), [(0, 0)]
    for r in rules:
        nxt = dict(jug_rules(*s, X, Y))
        assert r in nxt, (s, r)
        s = nxt[r]
        out.append(s)
    return out


def three_succ(s, caps=(3, 5, 9)):
    out = []
    if s[0] < caps[0]:
        out.append(("fill A", (caps[0], s[1], s[2])))
    for i in range(3):
        if s[i]:
            t = list(s); t[i] = 0
            out.append(("empty " + "ABC"[i], tuple(t)))
        for j in range(3):
            if i != j and s[i] and s[j] < caps[j]:
                m = min(s[i], caps[j] - s[j])
                t = list(s); t[i] -= m; t[j] += m
                out.append(("pour %s into %s" % ("ABC"[i], "ABC"[j]), tuple(t)))
    return out


def jug_panel(k, title, state, caps, prev, act, key, unit):
    names = [("%d" % c) for c in caps]
    wj, gap = 0.62, 0.34
    H = max(caps) * unit
    L = [r"\begin{tikzpicture}"]
    x0 = 0.0
    x1 = len(caps) * wj + (len(caps) - 1) * gap
    x1 = max(x1, 2.35)
    L.append(r"\node[ttl, text width=%.2fcm] at (0,0) {%s};" % (x1, title))
    base = -0.55 - H
    for i, (c, v) in enumerate(zip(caps, state)):
        x = i * (wj + gap)
        changed = prev is not None and prev[i] != v
        if v:
            L.append(r"\fill[water] (%.2f,%.2f) rectangle (%.2f,%.2f);"
                     % (x, base, x + wj, base + v * unit))
        L.append(r"\draw[%s] (%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f);"
                 % ("mkc, line width=1pt" if changed else "sub, line width=0.6pt",
                    x, base + c * unit, x, base, x + wj, base, x + wj, base + c * unit))
        L.append(r"\node[font=\scriptsize\bfseries, text=%s] at (%.2f,%.2f) {%d};"
                 % ("mkc" if changed else "ink", x + wj / 2, base + c * unit + 0.17, v))
        L.append(r"\node[cy] at (%.2f,%.2f) {cap %s};" % (x + wj / 2, base - 0.14, names[i]))
    y_eq = base - 0.32
    L.append(r"\node[eqn, text width=%.2fcm] at (0,%.2f) {%s};" % (x1, y_eq, act))
    frame(L, 0.0, y_eq - 0.52, x1, 0.0, key)
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


JUG_ACT = {1: "fill the big jug", 2: "fill the small jug", 3: "empty the big jug",
           4: "empty the small jug", 5: "pour small into big until full",
           6: "pour big into small until full", 7: "pour all of small into big",
           8: "pour all of big into small"}


def jug_legend(extra=""):
    return (r"\begin{tikzpicture}\fill[water] (0,0) rectangle (0.3,0.2);"
            r"\node[cy, anchor=west] at (0.35,0.1) {water};"
            r"\draw[mkc, line width=1pt] (1.4,0.2) -- (1.4,0) -- (1.7,0) -- (1.7,0.2);"
            r"\node[cy, anchor=west] at (1.75,0.1) {jug changed by this move};"
            r"\node[keytag, anchor=west] at (4.6,0.1) {KEY STEP};"
            r"\node[cy, anchor=west] at (5.55,0.1) {the move the puzzle turns on%s};"
            r"\end{tikzpicture}" % extra)


def jug43_figures(tex):
    left = replay_jug([2, 7, 2, 5, 3, 7], 4, 3)
    right = replay_jug([1, 6, 4, 8, 1, 6], 4, 3)
    assert left == [(0, 0), (0, 3), (3, 0), (3, 3), (4, 2), (0, 2), (2, 0)], left
    assert right == [(0, 0), (4, 0), (1, 3), (1, 0), (0, 1), (4, 1), (2, 3)], right
    succ = lambda s: jug_rules(*s, 4, 3)
    assert bfs_len((0, 0), succ, lambda s: s[0] == 2) == 6
    flat = re.sub(r"\s", "", tex)
    for s in left[1:] + right[1:]:
        assert "(%d,%d)" % s in flat, s
    rules = [2, 7, 2, 5, 3, 7]
    pan = [jug_panel(0, "start", left[0], (4, 3), None, "both jugs empty", False, 0.34)]
    for k, (r, s) in enumerate(zip(rules, left[1:]), 1):
        act = "rule %d: %s" % (r, JUG_ACT[r])
        if k == 4:
            act += r"; the 4 takes only 1, \textbf{2 stay} in the 3"
        if k == 6:
            act += r" \,{\color{gd}\textbf{goal} $(2, 0)$}"
        pan.append(jug_panel(k, "%d.\\, $(%d, %d)$" % (k, s[0], s[1]), s, (4, 3),
                             left[k - 1], act, k == 4, 0.34))
    steps = grid(pan, 4, jug_legend())
    # the two-branch search tree
    L = [r"\begin{tikzpicture}[st/.style={draw=acc, fill=white, rounded corners=1.5pt,"
         r" font=\scriptsize, inner sep=1.6pt, minimum width=8.5mm},"
         r" gl/.style={st, draw=gd, fill=gdL, line width=0.8pt, font=\scriptsize\bfseries}]"]
    L.append(r"\node[st] (r) at (0,0) {$(0,0)$};")
    for name, path, rs, y in (("a", right, [1, 6, 4, 8, 1, 6], 0.55),
                              ("b", left, rules, -0.55)):
        prev = "r"
        for i, (s, r) in enumerate(zip(path[1:], rs), 1):
            sty = "gl" if i == len(rs) else "st"
            L.append(r"\node[%s] (%s%d) at (%.2f,%.2f) {$(%d,%d)$};"
                     % (sty, name, i, 1.55 * i + 0.3, y, s[0], s[1]))
            L.append(r"\draw[-{Stealth[length=1.6mm]}, acc] (%s) -- node[cy, fill=white,"
                     r" %s] {r%d} (%s%d);" % (prev, "above" if y > 0 else "below", r, name, i))
            prev = "%s%d" % (name, i)
    L.append(r"\node[cy, anchor=west] at (0.1,1.25) {Only rules 1 and 2 apply at the root: "
             r"two branches, and each reaches a goal in 6 moves (BFS finds nothing shorter).};")
    L.append(r"\end{tikzpicture}")
    tree = r"\begin{panelbox}" + "\n".join(L) + r"\end{panelbox}"
    return steps, tree


def jug3_figure(tex):
    moves = ["fill A", "pour A into B", "fill A", "pour A into B", "pour A into C",
             "fill A", "pour A into C", "fill A", "pour A into C"]
    s, path = (0, 0, 0), [(0, 0, 0)]
    for m in moves:
        s = [t for a, t in three_succ(s) if a == m][0]
        path.append(s)
    want = [(0, 0, 0), (3, 0, 0), (0, 3, 0), (3, 3, 0), (1, 5, 0), (0, 5, 1), (3, 5, 1),
            (0, 5, 4), (3, 5, 4), (0, 5, 7)]
    assert path == want, path
    assert bfs_len((0, 0, 0), three_succ, lambda s: s[2] == 7) == 9
    flat = re.sub(r"\s", "", tex)
    for st in path[1:-1]:
        assert "(%d,%d,%d)" % st in flat, st
    pan = [jug_panel(0, "start", path[0], (3, 5, 9), None, "only A can be filled", False,
                     0.20)]
    for k, (m, st) in enumerate(zip(moves, path[1:]), 1):
        act = m
        if k == 4:
            act += r": B takes 2, \textbf{1 stranded in A}"
        if k == 9:
            act += r" \,{\color{gd}\textbf{goal}: $1{+}3{+}3 = 7$}"
        pan.append(jug_panel(k, "%d.\\, $(%d,%d,%d)$" % ((k,) + st), st, (3, 5, 9),
                             path[k - 1], act, k == 4, 0.20))
    return grid(pan, 5, jug_legend())


def jug52_figure(tex):
    rules = [1, 6, 4, 6]
    path = replay_jug(rules, 5, 2)
    assert path == [(0, 0), (5, 0), (3, 2), (3, 0), (1, 2)], path
    assert bfs_len((0, 0), lambda s: jug_rules(*s, 5, 2), lambda s: 1 in s) == 4
    pan = [jug_panel(0, "start", path[0], (5, 2), None, "both empty", False, 0.30)]
    for k, (r, s) in enumerate(zip(rules, path[1:]), 1):
        act = "rule %d: %s" % (r, JUG_ACT[r])
        if k == 4:
            act += r"; \textbf{1 left} in the 5 {\color{gd}\textbf{goal}}"
        pan.append(jug_panel(k, "%d.\\, $(%d, %d)$" % (k, s[0], s[1]), s, (5, 2),
                             path[k - 1], act, k == 4, 0.30))
    return grid(pan, 5, jug_legend())


# =====================================================================
#  Farmer, wolf, goat, cabbage
# =====================================================================
ITEMS = "FWGC"


def safe(s):
    f, w, g, c = s
    return not ((w == g != f) or (g == c != f))


def river_succ(s):
    out = []
    for i in (None, 1, 2, 3):
        if i is not None and s[i] != s[0]:
            continue
        t = list(s)
        t[0] ^= 1
        if i is not None:
            t[i] ^= 1
        t = tuple(t)
        if safe(t):
            out.append(("alone" if i is None else ITEMS[i], t))
    return out


def river_figures(tex):
    cargo = ["G", "alone", "W", "G", "C", "alone", "G"]
    s, path = (0, 0, 0, 0), [(0, 0, 0, 0)]
    for c in cargo:
        s = [t for a, t in river_succ(s) if a == c][0]
        path.append(s)
    assert path[-1] == (1, 1, 1, 1)
    assert bfs_len((0, 0, 0, 0), river_succ, lambda s: s == (1, 1, 1, 1)) == 7
    for st in path[1:]:
        assert " ".join("WE"[b] for b in st) in tex, st
    # every reachable safe state
    seen, q = {(0, 0, 0, 0)}, deque([(0, 0, 0, 0)])
    while q:
        u = q.popleft()
        for _, v in river_succ(u):
            if v not in seen:
                seen.add(v); q.append(v)
    assert len(seen) == 10, len(seen)
    assert sum(safe(t) for t in __import__("itertools").product((0, 1), repeat=4)) == 10

    name = {"F": "Farmer", "W": "Wolf", "G": "Goat", "C": "Cabbage"}
    col = {"F": "acc", "W": "sub", "G": "mkc", "C": "gd"}

    def panel(k, st, prev, what, key):
        L = [r"\begin{tikzpicture}"]
        title = "start" if k == 0 else "%d.\\, %s" % (k, what)
        L.append(r"\node[ttl, text width=3.0cm] at (0,0) {%s};" % title)
        L.append(r"\fill[bank] (0,-0.45) rectangle (0.95,-2.05);")
        L.append(r"\fill[water!45] (0.95,-0.45) rectangle (2.05,-2.05);")
        L.append(r"\fill[bank] (2.05,-0.45) rectangle (3.0,-2.05);")
        L.append(r"\node[cy] at (0.475,-2.2) {west}; \node[cy] at (2.525,-2.2) {east};")
        for i, it in enumerate(ITEMS):
            x = 0.475 if st[i] == 0 else 2.525
            y = -0.72 - i * 0.37
            moved = prev is not None and prev[i] != st[i]
            L.append(r"\node[circle, draw=%s, fill=%s, text=%s, inner sep=0pt,"
                     r" minimum size=3.4mm, font=\tiny\bfseries%s] at (%.2f,%.2f) {%s};"
                     % (col[it], "mkL" if moved else "white", col[it],
                        ", line width=0.9pt" if moved else "", x, y, it))
        if prev is not None:
            east = st[0] == 1
            a, b = (1.05, 1.95) if east else (1.95, 1.05)
            L.append(r"\draw[-{Stealth[length=1.6mm]}, mkc, line width=0.8pt]"
                     r" (%.2f,-1.25) -- (%.2f,-1.25);" % (a, b))
            moved = [it for i, it in enumerate(ITEMS) if i and prev[i] != st[i]]
            L.append(r"\node[font=\tiny\bfseries, text=mkc] at (1.5,-1.02) {%s};"
                     % "+".join(["F"] + moved))
        frame(L, 0.0, -2.35, 3.0, 0.0, key)
        L.append(r"\end{tikzpicture}")
        return "\n".join(L)

    words = {"G": "take the goat over", "W": "take the wolf over",
             "C": "take the cabbage over", "alone": "return alone"}
    pan = [panel(0, path[0], None, "", False)]
    for k, (c, st) in enumerate(zip(cargo, path[1:]), 1):
        w = words[c]
        if k == 4:
            w = "bring the goat back"
        if k == 7:
            w += r" {\color{gd}goal}"
        pan.append(panel(k, st, path[k - 1], w, k == 4))
    leg = (r"\begin{tikzpicture}\node[circle, draw=mkc, fill=mkL, inner sep=0pt,"
           r" minimum size=3mm, line width=0.9pt] at (0,0) {};"
           r"\node[cy, anchor=west] at (0.2,0) {moved this crossing};"
           r"\node[keytag, anchor=west] at (2.6,0) {KEY STEP};"
           r"\node[cy, anchor=west, align=left] at (3.55,0) {the backward move: the goat is"
           r" the only item unsafe with both others, so it goes first and comes back};"
           r"\end{tikzpicture}")
    steps = grid(pan, 4, leg)

    # the state-space graph of the 10 safe states
    pos = {(0, 0, 0, 0): (0, 0), (1, 0, 1, 0): (1.75, 0), (0, 0, 1, 0): (3.5, 0),
           (1, 1, 1, 0): (5.25, 0.75), (1, 0, 1, 1): (5.25, -0.75),
           (0, 1, 0, 0): (7.0, 0.75), (0, 0, 0, 1): (7.0, -0.75),
           (1, 1, 0, 1): (8.75, 0), (0, 1, 0, 1): (10.5, 0), (1, 1, 1, 1): (12.25, 0)}
    assert set(pos) == seen
    sol = {frozenset(e) for e in zip(path, path[1:])}

    def lab(s):
        w = "".join(it for i, it in enumerate(ITEMS) if s[i] == 0) or "--"
        e = "".join(it for i, it in enumerate(ITEMS) if s[i] == 1) or "--"
        return r"%s\,\textbar\,%s" % (w, e)

    L = [r"\begin{tikzpicture}[st/.style={draw=acc, fill=white, rounded corners=1.5pt,"
         r" font=\tiny\bfseries, inner sep=1.8pt, minimum width=11mm},"
         r" sl/.style={st, draw=gd, fill=gdL, line width=0.8pt}]"]
    ids = {}
    for i, (s, (x, y)) in enumerate(sorted(pos.items(), key=lambda kv: kv[1])):
        ids[s] = "n%d" % i
        on = any(s in e for e in sol)
        L.append(r"\node[%s] (n%d) at (%.2f,%.2f) {%s};" % ("sl" if on else "st", i, x, y,
                                                           lab(s)))
    done = set()
    for s in pos:
        for a, t in river_succ(s):
            e = frozenset((s, t))
            if e in done:
                continue
            done.add(e)
            carry = a if a != "alone" else ""
            L.append(r"\draw[%s] (%s) -- node[cy, fill=white] {%s} (%s);"
                     % ("gd, line width=1.1pt" if e in sol else "acc, line width=0.5pt",
                        ids[s], "F" + ("+" + carry if carry else ""), ids[t]))
    L.append(r"\node[cy, anchor=north west, align=flush left, text width=13.0cm]"
             r" at (-0.6,-1.25) {Each node is"
             r" \emph{west}\,\textbar\,\emph{east}. All 10 safe reachable states are drawn;"
             r" the other 6 of the $2^4 = 16$ leave goat with wolf or cabbage unattended."
             r" Green: the solution above. The lower branch is the mirror solution"
             r" (cabbage third, then wolf).};")
    L.append(r"\end{tikzpicture}")
    graph = r"\begin{panelbox}" + "\n".join(L) + r"\end{panelbox}"
    return steps, graph


# =====================================================================
#  Tic-tac-toe
# =====================================================================
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8),
         (0, 4, 8), (2, 4, 6)]


def winner(b):
    for a, c, d in LINES:
        if b[a] and b[a] == b[c] == b[d]:
            return b[a]
    return 0


def ttt_reachable():
    start = (0,) * 9
    seen, q = {start}, deque([start])
    while q:
        b = q.popleft()
        if winner(b) or all(b):
            continue
        turn = 1 if b.count(1) == b.count(2) else 2
        for i in range(9):
            if not b[i]:
                t = b[:i] + (turn,) + b[i + 1:]
                if t not in seen:
                    seen.add(t); q.append(t)
    return len(seen)


SYM = []
for rot in range(4):
    for flip in (False, True):
        m = list(range(9))
        for _ in range(rot):
            m = [m[6], m[3], m[0], m[7], m[4], m[1], m[8], m[5], m[2]]
        if flip:
            m = [m[2], m[1], m[0], m[5], m[4], m[3], m[8], m[7], m[6]]
        SYM.append(m)


def canon(b):
    return min(tuple(b[m[i]] for i in range(9)) for m in SYM)


def children(b, turn):
    out, seen = [], set()
    for i in range(9):
        if not b[i]:
            t = b[:i] + (turn,) + b[i + 1:]
            c = canon(t)
            if c not in seen:
                seen.add(c); out.append(t)
    return out


def board(b, x, y, s=0.19, hi=None):
    L = []
    for i in range(9):
        r, c = divmod(i, 3)
        cx, cy = x + (c - 1) * s, y - (r - 1) * s
        fill = "mkL" if hi is not None and i == hi else "white"
        L.append(r"\node[draw=ruleL, fill=%s, minimum size=%.2fcm, inner sep=0pt,"
                 r" font=\fontsize{4.5}{5}\selectfont\bfseries, text=%s] at (%.3f,%.3f) {%s};"
                 % (fill, s, "acc" if b[i] == 1 else "mkc", cx, cy,
                    {0: "", 1: "X", 2: "O"}[b[i]]))
    return L


def ttt_figure(tex):
    n = ttt_reachable()
    assert n == 5478, n
    assert "5{,}478" in tex and "19{,}683" in tex and "362{,}880" in tex
    assert 3 ** 9 == 19683 and len(LINES) == 8
    root = (0,) * 9
    ply1 = children(root, 1)
    assert len(ply1) == 3
    ply2 = [children(b, 2) for b in ply1]
    assert [len(c) for c in ply2] == [5, 5, 2] or sorted(len(c) for c in ply2) == [2, 5, 5]
    assert sum(len(c) for c in ply2) == 12

    # (a) the data structure
    L = [r"\begin{tikzpicture}"]
    L.append(r"\node[ttl] at (0,0) {1.\, the board as two 9-bit masks};")
    L += chips(["DOMAIN"], 0, -0.42)[:0]
    ex = (1, 0, 2, 0, 1, 0, 0, 0, 0)
    for i in range(9):
        r, c = divmod(i, 3)
        x, y = 0.45 + c * 0.55, -0.85 - r * 0.55
        L.append(r"\node[draw=ruleL, minimum size=0.55cm, inner sep=0pt,"
                 r" font=\scriptsize\bfseries, text=%s] at (%.2f,%.2f) {%s};"
                 % ("acc" if ex[i] == 1 else "mkc", x, y, {0: "", 1: "X", 2: "O"}[ex[i]]))
        L.append(r"\node[font=\fontsize{4}{4}\selectfont, text=sub, anchor=north west,"
                 r" inner sep=0.6pt] at (%.2f,%.2f) {%d};" % (x - 0.27, y + 0.27, i + 1))
    xm = sum(1 << i for i in range(9) if ex[i] == 1)
    om = sum(1 << i for i in range(9) if ex[i] == 2)
    bits = lambda m: "".join("1" if m >> i & 1 else "0" for i in range(8, -1, -1))
    L.append(r"\node[eqn, text width=3.6cm] at (1.85,-0.55) {"
             r"square $i$ is bit $i$\\[2pt]"
             r"\textbf{X} $= %s_2 = %d$\\ \textbf{O} $= %s_2 = %d$\\[2pt]"
             r"legal move $i$: bit $i$ of X$|$O is 0\\"
             r"win: \texttt{X \& line == line}\\ for the 8 lines, e.g.\ diagonal"
             r" $1,5,9 = %d$: X needs square 9}; "
             % (bits(xm), xm, bits(om), om, (1 << 0) | (1 << 4) | (1 << 8)))
    frame(L, 0.0, -2.55, 5.5, 0.0, False)
    L.append(r"\end{tikzpicture}")
    a = "\n".join(L)

    # (b) the 8 goal lines
    L = [r"\begin{tikzpicture}"]
    L.append(r"\node[ttl] at (0,0) {2.\, goal test: the 8 lines};")
    for k, ln in enumerate(LINES):
        b = tuple(1 if i in ln else 0 for i in range(9))
        L += board(b, 0.35 + (k % 4) * 0.78, -0.75 - (k // 4) * 0.78, 0.2)
    L.append(r"\node[eqn, text width=3.1cm] at (0,-2.05) {3 rows, 3 columns, 2 diagonals."
             r" Draw: all 9 filled, no line.};")
    frame(L, 0.0, -2.55, 3.05, 0.0, False)
    L.append(r"\end{tikzpicture}")
    b_ = "\n".join(L)

    # (c) the first two plies up to symmetry
    L = [r"\begin{tikzpicture}"]
    L.append(r"\node[ttl] at (-0.2,0) {3.\, state space, first two plies up to symmetry};")
    xs, leaf = [], 0
    pos1 = []
    for kids in ply2:
        start = leaf
        leaf += len(kids)
        pos1.append((start + leaf - 1) / 2.0)
    pitch = 0.98
    pos1 = [x + 0.4 / pitch for x in pos1]    # clear of the left frame
    rootx = (pos1[0] + pos1[-1]) / 2 * pitch
    L += board(root, rootx, -0.65)
    leaf = 0.4 / pitch
    for b1, x1i, kids in zip(ply1, pos1, ply2):
        hx = [i for i in range(9) if b1[i]][0]
        L.append(r"\draw[acc] (%.2f,-0.95) -- (%.2f,-1.35);" % (rootx, x1i * pitch))
        L += board(b1, x1i * pitch, -1.65, hi=hx)
        for b2 in kids:
            ho = [i for i in range(9) if b2[i] == 2][0]
            L.append(r"\draw[ruleL] (%.2f,-1.95) -- (%.2f,-2.35);" % (x1i * pitch, leaf * pitch))
            L += board(b2, leaf * pitch, -2.65, hi=ho)
            leaf += 1
    right = (leaf - 1) * pitch + 0.35
    L.append(r"\node[cy, anchor=west] at (%.2f,-0.65) {ply 0: the empty board};"
             % (rootx + 0.4))
    L.append(r"\node[cy, anchor=east, align=flush right] at (%.2f,-1.65) {ply 1: 9 moves,"
             r"\\only 3 distinct:\\corner, edge, centre};" % (pos1[0] * pitch - 0.4))
    L.append(r"\node[cy, anchor=north west, align=flush left, text width=%.2fcm] at"
             r" (-0.2,-3.05) {ply 2: 72 boards, 12 distinct up to rotation and reflection."
             r" The branching factor falls 9, 8, 7 and so on, and the whole tree has at most"
             r" $9! = 362{,}880$ games, so minimax can search it to the end.};"
             % (right + 0.2))
    frame(L, -0.2, -3.55, right, 0.0, False)
    L.append(r"\end{tikzpicture}")
    c = "\n".join(L)
    return grid([a, b_], 2, "") .replace(r"\end{tabular}",
                                          r"\multicolumn{2}{@{}c@{}}{" + c + r"} \\"
                                          + "\n" + r"\end{tabular}")


# =====================================================================
#  The technique index
# =====================================================================
SHORT = {"c2_step_send": "SEND", "c2_step_base": "BASE", "c2_step_ten": "TEN",
         "c2_step_logic": "LOGIC", "c2_step_eat": "EAT", "c2_step_cross": "CROSS",
         "c2_step_love": "LOVE", "c2_step_one": "ONE", "c2_step_wrong": "WRONG",
         "c2_step_swim": "SWIM", "c2_step_right": "RIGHT", "c2_step_two": "TWO"}


def tech_index():
    rows = []
    for t in TECH_ORDER:
        where = []
        for p in PUZZLES:
            ks = [(r"\textbf{\color{mkc}%d}" % k) if st["key"] else str(k)
                  for k, st in enumerate(p["steps"], 1) if t in st["tech"]]
            if ks:
                where.append("%s %s" % (SHORT[p["name"]], ",".join(ks)))
        lab, col, what = TECH[t]
        rows.append(r"\tikz[baseline=(c.base)]\node[chip, fill=%s] (c) {%s}; & %s &"
                    r" \leavevmode{\color{sub}%s} \\"
                    % (col, lab, what, "; ".join(where) or "--"))
    return (r"\begin{panelbox}\footnotesize\renewcommand{\arraystretch}{1.35}"
            r"\begin{tabular}{@{}l>{\raggedright\arraybackslash}p{7.6cm}"
            r">{\raggedright\arraybackslash}p{6.4cm}@{}}"
            r"\textbf{Move} & \textbf{What it says} & \textbf{Where it is used (puzzle, step;"
            r" {\color{mkc}orange} = the puzzle's key step)} \\ \hline" + "\n"
            + "\n".join(rows) + r"\end{tabular}\end{panelbox}")


# =====================================================================
#  Build
# =====================================================================
CAPTION = {
    "c2_tech_index": "The fourteen moves every crypt-arithmetic chain below is built from",
    "c2_step_send": "Step by step: SEND $+$ MORE $=$ MONEY",
    "c2_step_base": "Step by step: BASE $+$ BALL $=$ GAMES",
    "c2_step_ten": "Step by step: TEN $+$ TEN $+$ FORTY $=$ SIXTY (the carry of 2)",
    "c2_step_logic": "Step by step: LOGIC $+$ LOGIC $=$ PROLOG",
    "c2_step_eat": "Step by step: EAT $+$ THAT $=$ APPLE",
    "c2_step_cross": "Step by step: CROSS $+$ ROADS $=$ DANGER",
    "c2_step_love": "Step by step: LOVE $+$ LOVE $=$ HATE",
    "c2_step_one": "Step by step: ONE $+$ ONE $+$ TWO $=$ FOUR",
    "c2_step_wrong": "Step by step: WRONG $+$ WRONG $=$ RIGHT",
    "c2_step_swim": "Step by step: SWIM $+$ WEAR $=$ RELAX",
    "c2_step_right": "Step by step: RIGHT $+$ RIGHT $=$ WRONG",
    "c2_step_two": "Step by step: TWO $+$ TWO $=$ FOUR",
    "c2_step_ab": "Step by step: AB $+$ CD $=$ AAA",
    "c2_step_jug43": "Step by step: the jugs after each rule",
    "c2_tree_jug43": "Search tree: both branches from $(0,0)$",
    "c2_step_jug359": "Step by step: the three jugs after each move",
    "c2_step_jug52": "Step by step: the jugs after each rule",
    "c2_step_river": "Step by step: the banks after each crossing",
    "c2_graph_river": "Search space: every safe state and the two 7-crossing solutions",
    "c2_step_ttt": "The state space, the data structure and the goal, drawn",
}


def build():
    tex = open(TEX, encoding="utf-8").read()
    figs = [("c2_tech_index", tech_index())]
    for p in PUZZLES:
        check_puzzle(p, tex)
        figs.append((p["name"], crypt_figure(p)))
    figs.append(("c2_step_ab", ab_figure()))
    s, t = jug43_figures(tex)
    figs += [("c2_step_jug43", s), ("c2_tree_jug43", t)]
    figs.append(("c2_step_jug359", jug3_figure(tex)))
    figs.append(("c2_step_jug52", jug52_figure(tex)))
    s, g = river_figures(tex)
    figs += [("c2_step_river", s), ("c2_graph_river", g)]
    figs.append(("c2_step_ttt", ttt_figure(tex)))
    return figs


def strip_blocks(src):
    return re.sub(r"(?m)^" + re.escape(MARK) + r"c2_\w+ \(generated.*?^"
                  + re.escape(MARK) + r"end\n", "", src, flags=re.S)


def main():
    figs = build()
    if "--report" in sys.argv:
        for name, _ in figs:
            print("ok  %s" % name)
        return
    work = os.path.join(FIGS, "_ch2fig")
    os.makedirs(work, exist_ok=True)
    doc = PRE + "\n\n".join(b for _, b in figs) + "\n" + BS + "end{document}\n"
    open(os.path.join(work, "ch2fig.tex"), "w", encoding="utf-8").write(doc)
    r = subprocess.run([TECTONIC, "-X", "compile", "ch2fig.tex"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-4000:] + r.stderr[-4000:])
    pdf = fitz.open(os.path.join(work, "ch2fig.pdf"))
    if len(pdf) != len(figs):
        sys.exit("expected %d pages, got %d" % (len(figs), len(pdf)))
    widths, heights = {}, {}
    for (name, _), page in zip(figs, pdf):
        page.get_pixmap(dpi=DPI).save(os.path.join(FIGS, name + ".png"))
        widths[name] = min(page.rect.width, MAXPT)
        heights[name] = page.rect.height * widths[name] / page.rect.width
    if "--figs-only" in sys.argv:
        print("%d figures rendered, .tex untouched" % len(figs))
        return
    src = strip_blocks(open(TEX, encoding="utf-8").read()).rstrip("\n") + "\n"
    for name, _ in figs:
        anchor = SLOT + name
        i = src.find(anchor)
        if i < 0:
            sys.exit("no slot for %s in ch2-num.tex" % name)
        if src[i - 1:i] != "\n" or not src[i + len(anchor):].startswith("\n"):
            sys.exit("slot for %s is not alone on its line" % name)
        j = src.find("\n", i) + 1
        block = (MARK + name + " (generated by ch2fig.py; do not edit)\n"
                 + BS + "penalty0" + BS + "vspace{3pt}\n"
                 # caption and figure travel together: reserve the figure's
                 # own height plus the caption line
                 + BS + "Needspace{%.0fpt}\n" % (heights[name] + 24)
                 + BS + "lead{" + CAPTION[name] + "}\n"
                 + BS + "begin{center}" + BS
                 + "includegraphics[width=%.1fpt]{figs/%s.png}" % (widths[name], name)
                 + BS + "end{center}\n"
                 # the next \creamq reserves 6 lines, but its asked box is taller:
                 # after a tall figure that strands the heading at the page foot
                 + BS + "par" + BS + "Needspace{16" + BS + "baselineskip}\n"
                 + MARK + "end\n")
        src = src[:j] + block + src[j:]
    open(TEX, "w", encoding="utf-8").write(src)
    print("%d figures written" % len(figs))


if __name__ == "__main__":
    main()
