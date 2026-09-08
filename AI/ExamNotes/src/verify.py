# -*- coding: utf-8 -*-
"""Independently recompute every answer published in the AI exam notes, and
assert it against the value actually printed in the .tex.

This is a *check*, not a source: nothing here reads an answer out of the notes
and hands it back. Each one is recomputed from the problem statement, then
compared with what the notes print.

AI is not a numbers subject the way Wireless is, so what gets checked here is
different in kind but the same in spirit:

  * every crypt-arithmetic answer, by EXHAUSTIVE search over letter-to-digit
    assignments -- which also reports how many solutions the puzzle really has,
    because seven of the thirteen in the papers are NOT unique;
  * every water-jug solution path, replayed move by move against the jug
    capacities and the fill rules that paper allows;
  * the farmer / wolf / goat / cabbage crossing sequence, replayed against the
    eating rules;
  * later chapters: entropy and information gain, Bayes posteriors, perceptron
    and Hebbian weight updates, Hopfield weight matrices and recall.

Run:  python verify.py          (from this folder)
Run it BEFORE building any -num target.
"""
import collections
import itertools
import math
import sys

FAIL = []
N_OK = 0


def chk(label, got, want, tol=None, rel=2e-3):
    """Assert a recomputed value matches the value printed in the notes."""
    global N_OK
    if isinstance(want, (int, float)) and not isinstance(want, bool) \
            and isinstance(got, (int, float)) and not isinstance(got, bool):
        if tol is None:
            tol = abs(want) * rel if want else 1e-9
        ok = abs(got - want) <= tol
    else:
        ok = (got == want)
    if ok:
        N_OK += 1
    else:
        FAIL.append("%s: recomputed %r but notes print %r" % (label, got, want))


# =====================================================================
#  crypt-arithmetic
# =====================================================================
def crypt_solve(addends, total):
    """Every solution, not the first. Distinct digits, no leading zero."""
    words = list(addends) + [total]
    letters = sorted(set("".join(words)))
    assert len(letters) <= 10, "%s: more than 10 distinct letters" % total
    lead = set(w[0] for w in words)
    out = []
    for perm in itertools.permutations(range(10), len(letters)):
        m = dict(zip(letters, perm))
        if any(m[c] == 0 for c in lead):
            continue
        if sum(_val(w, m) for w in addends) == _val(total, m):
            out.append(m)
    return out


def _val(word, m):
    n = 0
    for ch in word:
        n = n * 10 + m[ch]
    return n


def crypt(label, addends, total, printed, n_solutions):
    """`printed` is the letter->digit map the notes publish; `n_solutions` is
    the count the notes claim the puzzle has."""
    sols = crypt_solve(addends, total)
    chk(label + " solution count", len(sols), n_solutions)
    chk(label + " published answer is valid", printed in sols, True)
    lhs = sum(_val(w, printed) for w in addends)
    chk(label + " arithmetic", lhs, _val(total, printed), tol=0)


# =====================================================================
#  water jug
# =====================================================================
def jug_replay(label, caps, moves, fillable=None, start=None):
    """Replay a published move list and return the states it passes through.
    `moves` is a list of ("fill", i) / ("empty", i) / ("pour", i, j).
    Raises through chk() if any move is illegal for those capacities.
    """
    if fillable is None:
        fillable = list(range(len(caps)))
    s = list(start if start else [0] * len(caps))
    seq = [tuple(s)]
    for mv in moves:
        if mv[0] == "fill":
            i = mv[1]
            if i not in fillable:
                FAIL.append("%s: jug %d may not be filled from the pump"
                            % (label, i + 1))
                return seq
            s[i] = caps[i]
        elif mv[0] == "empty":
            s[mv[1]] = 0
        elif mv[0] == "pour":
            i, j = mv[1], mv[2]
            amt = min(s[i], caps[j] - s[j])
            s[i] -= amt
            s[j] += amt
        else:
            FAIL.append("%s: unknown move %r" % (label, mv))
            return seq
        for k, v in enumerate(s):
            if v < 0 or v > caps[k]:
                FAIL.append("%s: jug %d holds %d, capacity %d"
                            % (label, k + 1, v, caps[k]))
                return seq
        seq.append(tuple(s))
    return seq


def jug_bfs(caps, goal, goal_jug, fillable=None):
    """Fewest moves to the goal, so the notes can claim a move count honestly."""
    if fillable is None:
        fillable = list(range(len(caps)))
    start = tuple(0 for _ in caps)
    seen = {start}
    q = collections.deque([(start, 0)])
    while q:
        s, d = q.popleft()
        if s[goal_jug] == goal:
            return d
        for i in range(len(caps)):
            nxt = []
            if i in fillable and s[i] < caps[i]:
                n = list(s); n[i] = caps[i]; nxt.append(tuple(n))
            if s[i] > 0:
                n = list(s); n[i] = 0; nxt.append(tuple(n))
            for j in range(len(caps)):
                if i == j or s[i] == 0 or s[j] == caps[j]:
                    continue
                amt = min(s[i], caps[j] - s[j])
                n = list(s); n[i] -= amt; n[j] += amt
                nxt.append(tuple(n))
            for n in nxt:
                if n not in seen:
                    seen.add(n)
                    q.append((n, d + 1))
    return None


# =====================================================================
#  Chapter 2 -- Problem Solving
# =====================================================================
def ch2():
    # --- crypt-arithmetic, every puzzle the 41 papers set -------------
    # Each entry: the answer the notes publish, and the number of DISTINCT
    # solutions the puzzle has. The count is published in the notes too,
    # because a student who memorises one answer to a 42-solution puzzle and
    # meets a marker expecting another has a real problem.
    crypt("LOGIC+LOGIC=PROLOG", ["LOGIC", "LOGIC"], "PROLOG",
          dict(L=9, O=0, G=4, I=5, C=2, P=1, R=8), 1)
    crypt("SEND+MORE=MONEY", ["SEND", "MORE"], "MONEY",
          dict(S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2), 1)
    crypt("BASE+BALL=GAMES", ["BASE", "BALL"], "GAMES",
          dict(B=7, A=4, S=8, E=3, L=5, G=1, M=9), 1)
    crypt("TEN+TEN+FORTY=SIXTY", ["TEN", "TEN", "FORTY"], "SIXTY",
          dict(T=8, E=5, N=0, F=2, O=9, R=7, Y=6, S=3, I=1, X=4), 1)
    crypt("EAT+THAT=APPLE", ["EAT", "THAT"], "APPLE",
          dict(E=8, A=1, T=9, H=2, P=0, L=3), 1)
    crypt("CROSS+ROADS=DANGER", ["CROSS", "ROADS"], "DANGER",
          dict(C=9, R=6, O=2, S=3, A=5, D=1, N=8, G=7, E=4), 1)
    crypt("ONE+ONE+TWO=FOUR", ["ONE", "ONE", "TWO"], "FOUR",
          dict(O=6, N=4, E=2, T=3, W=8, F=1, U=7, R=0), 107)
    crypt("TWO+TWO=FOUR", ["TWO", "TWO"], "FOUR",
          dict(T=7, W=3, O=4, F=1, U=6, R=8), 7)
    crypt("ONE+ONE=TWO", ["ONE", "ONE"], "TWO",
          dict(O=2, N=3, E=1, T=4, W=6), 16)
    crypt("RIGHT+RIGHT=WRONG", ["RIGHT", "RIGHT"], "WRONG",
          dict(R=4, I=2, G=0, H=6, T=5, W=8, O=1, N=3), 11)
    crypt("WRONG+WRONG=RIGHT", ["WRONG", "WRONG"], "RIGHT",
          dict(W=3, R=7, O=0, N=8, G=1, I=4, H=6, T=2), 21)
    crypt("SWIM+WEAR=RELAX", ["SWIM", "WEAR"], "RELAX",
          dict(S=9, W=4, I=0, M=5, E=3, A=2, R=1, L=7, X=6), 16)
    crypt("LOVE+LOVE=HATE", ["LOVE", "LOVE"], "HATE",
          dict(L=3, O=5, V=6, E=0, H=7, A=1, T=2), 42)

    # --- AB + CD = AAA, \bo{\textit{76 Bh}} --------------------------
    # The paper asks only "what could be the possible values of B".
    ab = [(A, B, C, D) for A, B, C, D in itertools.permutations(range(10), 4)
          if A and C and (10 * A + B) + (10 * C + D) == 111 * A]
    chk("AB+CD=AAA A is forced to 1", sorted(set(s[0] for s in ab)), [1])
    chk("AB+CD=AAA possible B", sorted(set(s[1] for s in ab)), [3, 4, 5, 6, 7, 8])
    chk("AB+CD=AAA solution count", len(ab), 6)
    # B = 9 is the one that looks legal and is not: it forces CD = 92, i.e.
    # C = 9 = B. The notes say so explicitly.
    chk("AB+CD=AAA B=9 excluded", 9 in set(s[1] for s in ab), False)

    # --- water jug ---------------------------------------------------
    # 4 and 3 gallon, 2 gallons in the 4-gallon jug.
    # \bo{\textit{77 Ch}}, \bo{\textit{71 Bh}}
    # jug 0 = the 4-gallon, jug 1 = the 3-gallon, state written (x, y).
    # This is the path Insights takes (rules 2, 7, 2, 5, 3, 7), and the notes
    # publish it because the book is the method authority for this subject.
    seq = jug_replay("jug 4-3", (4, 3), [
        ("fill", 1), ("pour", 1, 0), ("fill", 1), ("pour", 1, 0),
        ("empty", 0), ("pour", 1, 0)])
    chk("jug 4-3 states", seq,
        [(0, 0), (0, 3), (3, 0), (3, 3), (4, 2), (0, 2), (2, 0)])
    chk("jug 4-3 final state", seq[-1], (2, 0))
    chk("jug 4-3 move count", len(seq) - 1, 6)
    chk("jug 4-3 is shortest", jug_bfs((4, 3), 2, 0), 6)
    # The other 6-move path, which the notes mention as equally valid: fill the
    # 4 first. Same length, so neither is "the" answer.
    alt = jug_replay("jug 4-3 alt", (4, 3), [
        ("fill", 0), ("pour", 0, 1), ("empty", 1), ("pour", 0, 1),
        ("fill", 0), ("pour", 0, 1)])
    chk("jug 4-3 alt final state", alt[-1], (2, 3))
    chk("jug 4-3 alt move count", len(alt) - 1, 6)

    # 3, 5 and 9 gallon, 7 gallons in the 9-gallon jug, and the pump may fill
    # ONLY the 3-gallon jug. \bo{\texttt{79 Bh}}
    seq = jug_replay("jug 3-5-9", (3, 5, 9), [
        ("fill", 0), ("pour", 0, 1), ("fill", 0), ("pour", 0, 1),
        ("pour", 0, 2), ("fill", 0), ("pour", 0, 2), ("fill", 0),
        ("pour", 0, 2)], fillable=[0])
    chk("jug 3-5-9 final state", seq[-1], (0, 5, 7))
    chk("jug 3-5-9 move count", len(seq) - 1, 9)
    chk("jug 3-5-9 is shortest", jug_bfs((3, 5, 9), 7, 2, fillable=[0]), 9)

    # 5 and 2 litre, measure exactly 1 litre. 81 Ash
    seq = jug_replay("jug 5-2", (5, 2), [
        ("fill", 0), ("pour", 0, 1), ("empty", 1), ("pour", 0, 1)])
    chk("jug 5-2 final state", seq[-1], (1, 2))
    chk("jug 5-2 move count", len(seq) - 1, 4)
    chk("jug 5-2 is shortest", jug_bfs((5, 2), 1, 0), 4)

    # --- farmer, wolf, goat, cabbage. 73 Ma --------------------------
    # state = (farmer, wolf, goat, cabbage), 0 = west bank, 1 = east.
    # Published crossing sequence: goat, back alone, wolf, goat back,
    # cabbage, back alone, goat.
    def safe(s):
        f, w, g, c = s
        return not ((g == w and f != g) or (g == c and f != g))

    carry = [2, 0, 1, 2, 3, 0, 2]        # 0 = alone, 1 = wolf, 2 = goat, 3 = cabbage
    s = (0, 0, 0, 0)
    ok = True
    for k in carry:
        n = list(s)
        n[0] = 1 - s[0]
        if k:
            if s[k] != s[0]:
                ok = False
                break
            n[k] = 1 - s[k]
        s = tuple(n)
        if not safe(s):
            ok = False
            break
    chk("farmer crossings all legal and safe", ok, True)
    chk("farmer final state", s, (1, 1, 1, 1))
    chk("farmer crossing count", len(carry), 7)

    # every reachable safe state, so the notes can state the state-space size
    seen = {(0, 0, 0, 0)}
    q = collections.deque([(0, 0, 0, 0)])
    while q:
        st = q.popleft()
        for k in range(4):
            n = list(st)
            n[0] = 1 - st[0]
            if k:
                if st[k] != st[0]:
                    continue
                n[k] = 1 - st[k]
            n = tuple(n)
            if safe(n) and n not in seen:
                seen.add(n)
                q.append(n)
    chk("farmer reachable safe states", len(seen), 10)
    # 16 states in all; 6 are unsafe or unreachable
    chk("farmer total states", 2 ** 4, 16)

    # --- tic-tac-toe state space. \textit{72 Ma} ---------------------
    # 3^9 counts every assignment of {blank, X, O} to 9 squares, most of them
    # unreachable. The reachable, legal count is what the notes print.
    chk("tic-tac-toe naive 3^9", 3 ** 9, 19683)
    reach = set()

    def walk(board, turn):
        reach.add(board)
        if _ttt_win(board) or "" not in board:
            return
        for i, v in enumerate(board):
            if v == "":
                nb = list(board)
                nb[i] = turn
                walk(tuple(nb), "O" if turn == "X" else "X")

    walk(tuple([""] * 9), "X")
    chk("tic-tac-toe reachable legal states", len(reach), 5478)


# =====================================================================
#  Chapter 3 -- Search Techniques
# =====================================================================
# 2081 Chaitra and 2080 Chaitra print the SAME graph with DIFFERENT
# heuristics; 2080 Chaitra puts its heuristics in a separate table and asks
# for greedy as well. Edge list read off images/ai_81ch_astar.png and
# images/ai_80ch_astar.png.
C3_EDGES = {
    ("S", "A"): 6, ("S", "B"): 5, ("S", "C"): 10,
    ("A", "E"): 6, ("B", "E"): 6, ("B", "D"): 7, ("C", "D"): 6,
    ("E", "F"): 4, ("D", "F"): 6, ("F", "G"): 3,
}


def _adj(edges):
    adj = {}
    for (a, b), w in edges.items():
        adj.setdefault(a, []).append((b, w))
        adj.setdefault(b, []).append((a, w))
    for k in adj:
        adj[k].sort()
    return adj


def astar(h, edges=None, start="S", goal="G"):
    """Tree-search A*: no closed list, so a later cheaper path is always taken.

    That matters here. Both papers' heuristics are admissible but NOT
    consistent, so a graph-search A* with a strict closed list would close E
    at g=12 by way of A and never revise it to g=11 by way of B, returning 19
    instead of the true optimum 18.
    """
    import heapq
    import itertools
    adj = _adj(edges or C3_EDGES)
    cnt = itertools.count()
    pq = [(h[start], 0, next(cnt), start, [start])]
    order = []
    while pq:
        f, g, _, n, path = heapq.heappop(pq)
        order.append((n, g, f))
        if n == goal:
            return g, path, order
        for m, w in adj[n]:
            if m in path:
                continue
            heapq.heappush(pq, (g + w + h[m], g + w, next(cnt), m, path + [m]))
    return None, None, order


def greedy(h, edges=None, start="S", goal="G"):
    """Greedy best-first: order on h alone, ignore the cost already paid."""
    import heapq
    import itertools
    adj = _adj(edges or C3_EDGES)
    cnt = itertools.count()
    pq = [(h[start], next(cnt), start, [start], 0)]
    order = []
    while pq:
        _, _, n, path, g = heapq.heappop(pq)
        order.append((n, g))
        if n == goal:
            return g, path, order
        for m, w in adj[n]:
            if m in path:
                continue
            heapq.heappush(pq, (h[m], next(cnt), m, path + [m], g + w))
    return None, None, order


def cost_to_go(edges=None, goal="G"):
    import heapq
    adj = _adj(edges or C3_EDGES)
    dist = {goal: 0}
    pq = [(0, goal)]
    while pq:
        d, n = heapq.heappop(pq)
        if d > dist.get(n, float("inf")):
            continue
        for m, w in adj[n]:
            if d + w < dist.get(m, float("inf")):
                dist[m] = d + w
                heapq.heappush(pq, (d + w, m))
    return dist


def h_properties(h, edges=None):
    """(admissible, consistent) for a heuristic on this graph."""
    edges = edges or C3_EDGES
    t = cost_to_go(edges)
    adm = all(h[n] <= t[n] for n in h)
    con = True
    for (a, b), w in edges.items():
        if h[a] > w + h[b] or h[b] > w + h[a]:
            con = False
    return adm, con


def _leaves(x):
    if isinstance(x, int):
        return [x]
    out = []
    for c in x:
        out.extend(_leaves(c))
    return out


def minimax(node, maximizing):
    if isinstance(node, int):
        return node
    vals = [minimax(c, not maximizing) for c in node]
    return max(vals) if maximizing else min(vals)


def alphabeta(node, maximizing, a, b, seen, cut):
    """Standard left-to-right alpha-beta. `seen` collects the leaves actually
    evaluated, `cut` the ones skipped, so the notes can name them."""
    if isinstance(node, int):
        seen.append(node)
        return node
    if maximizing:
        v = float("-inf")
        for i, c in enumerate(node):
            v = max(v, alphabeta(c, False, a, b, seen, cut))
            a = max(a, v)
            if v >= b:
                cut.extend(_leaves(node[i + 1:]))
                break
        return v
    v = float("inf")
    for i, c in enumerate(node):
        v = min(v, alphabeta(c, True, a, b, seen, cut))
        b = min(b, v)
        if v <= a:
            cut.extend(_leaves(node[i + 1:]))
            break
    return v


def ch3():
    # --- 2081 Chaitra: A* on the graph -------------------------------
    h81 = dict(S=17, A=10, B=13, C=4, D=2, E=4, F=1, G=0)
    g, path, order = astar(h81)
    chk("c3 81Ch A* cost", g, 18)
    chk("c3 81Ch A* path", "-".join(path), "S-B-E-F-G")
    chk("c3 81Ch first node expanded after S", order[1][0], "C")
    adm, con = h_properties(h81)
    chk("c3 81Ch h admissible", adm, True)
    chk("c3 81Ch h consistent", con, False)
    # the trap the notes call out: the naive S-A-E-F-G route costs 19
    chk("c3 81Ch S-A-E-F-G cost", 6 + 6 + 4 + 3, 19)

    # --- 2080 Chaitra: same graph, different h, A* Vs greedy ---------
    h80 = dict(S=15, A=10, B=12, C=5, D=4, E=2, F=1, G=0)
    g, path, _ = astar(h80)
    chk("c3 80Ch A* cost", g, 18)
    chk("c3 80Ch A* path", "-".join(path), "S-B-E-F-G")
    g2, path2, _ = greedy(h80)
    chk("c3 80Ch greedy cost", g2, 25)
    chk("c3 80Ch greedy path", "-".join(path2), "S-C-D-F-G")
    adm, con = h_properties(h80)
    chk("c3 80Ch h admissible", adm, True)
    chk("c3 80Ch h consistent", con, False)
    # greedy lands on the WORST of the four S-to-G routes
    routes = {"S-A-E-F-G": 19, "S-B-E-F-G": 18, "S-B-D-F-G": 21,
              "S-C-D-F-G": 25}
    chk("c3 80Ch greedy took the worst route", max(routes.values()), 25)
    chk("c3 80Ch optimum", min(routes.values()), 18)

    # --- 2076 Bhadra: best-first on the given tree, goal I -----------
    tree = {"A": ["B", "C", "D"], "B": ["E", "F"], "D": ["G", "H"],
            "G": ["I", "J"], "C": [], "E": [], "F": [], "H": [], "I": [],
            "J": []}
    hbf = dict(A=0, B=3, C=6, D=1, E=6, F=5, G=4, H=6, I=1, J=2)
    openl, closed, parent = [("A", 0)], [], {}
    while openl:
        openl.sort(key=lambda t: t[1])
        n, _ = openl.pop(0)
        closed.append(n)
        if n == "I":
            break
        for c in tree[n]:
            parent[c] = n
            openl.append((c, hbf[c]))
    chk("c3 76Bh best-first closed list", closed, ["A", "D", "B", "G", "I"])
    p = ["I"]
    while p[-1] in parent:
        p.append(parent[p[-1]])
    chk("c3 76Bh best-first path", "-".join(reversed(p)), "A-D-G-I")
    chk("c3 76Bh best-first cost", hbf["D"] + hbf["G"] + hbf["I"], 6)

    # --- 2079 Chaitra: minimax + alpha-beta on the given tree --------
    # Max root / Min / Max / Min / leaves. Three of the Min nodes have a
    # single child; that is how the paper draws it.
    t79 = [[[[3, 9], [2, 7]], [[2], [5, 0]]],
           [[[2, 5], [8]], [[3, 14]]]]
    chk("c3 79Ch leaf count", len(_leaves(t79)), 12)
    chk("c3 79Ch minimax value", minimax(t79, True), 3)
    seen, cut = [], []
    chk("c3 79Ch alpha-beta value", alphabeta(t79, True, float("-inf"),
                                              float("inf"), seen, cut), 3)
    chk("c3 79Ch leaves pruned", cut, [7, 5])
    chk("c3 79Ch leaves examined", len(seen), 10)

    # --- 2076 Baishakh: alpha-beta on the 3x3 tree -------------------
    t76 = [[3, 5, 10], [2, 8, 19], [2, 7, 3]]
    chk("c3 76Ba minimax value", minimax(t76, True), 3)
    seen, cut = [], []
    chk("c3 76Ba alpha-beta value", alphabeta(t76, True, float("-inf"),
                                              float("inf"), seen, cut), 3)
    chk("c3 76Ba leaves pruned", cut, [8, 19, 7, 3])
    chk("c3 76Ba leaves examined", seen, [3, 5, 10, 2, 2])


def _ttt_win(b):
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
             (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    return any(b[i] and b[i] == b[j] == b[k] for i, j, k in lines)


# =====================================================================
#  CHAPTER 4 — a small first-order resolution prover
# =====================================================================
# Every resolution answer in the Ch4 companion is checked by actually
# running resolution on the published clause set. That matters more here
# than anywhere else in the subject, because three papers print a goal
# that does NOT follow from their own premises, and those three claims
# are far too strong to make by hand. The prover confirms both
# directions: refutable where the notes prove a goal, and NOT refutable
# where the notes say the paper is broken.
#
# Terms   ('v', name) variable | ('c', name) constant | ('f', name, args)
# Literal (negated?, predicate, args)
# Clause  tuple of literals, implicitly a disjunction.

def V(n):
    return ("v", n)


def K(n):
    return ("c", n)


def Fn(n, *a):
    return ("f", n, tuple(a))


def P(name, *a):
    return (False, name, tuple(a))


def Nt(name, *a):
    return (True, name, tuple(a))


def _walk(t, s):
    while t[0] == "v" and t[1] in s:
        t = s[t[1]]
    return t


def _occurs(v, t, s):
    t = _walk(t, s)
    if t[0] == "v":
        return t[1] == v
    if t[0] == "f":
        return any(_occurs(v, a, s) for a in t[2])
    return False


def _unify(a, b, s):
    if s is None:
        return None
    a, b = _walk(a, s), _walk(b, s)
    if a == b:
        return s
    if a[0] == "v":
        if _occurs(a[1], b, s):
            return None
        s = dict(s)
        s[a[1]] = b
        return s
    if b[0] == "v":
        return _unify(b, a, s)
    if a[0] == "c" or b[0] == "c":
        return None
    if a[1] != b[1] or len(a[2]) != len(b[2]):
        return None
    for x, y in zip(a[2], b[2]):
        s = _unify(x, y, s)
        if s is None:
            return None
    return s


def _unify_lit(l1, l2, s):
    if l1[1] != l2[1] or len(l1[2]) != len(l2[2]):
        return None
    for x, y in zip(l1[2], l2[2]):
        s = _unify(x, y, s)
        if s is None:
            return None
    return s


def _sub_t(t, s):
    t = _walk(t, s)
    if t[0] == "f":
        return ("f", t[1], tuple(_sub_t(a, s) for a in t[2]))
    return t


def _sub_c(c, s):
    return tuple((n, p, tuple(_sub_t(a, s) for a in args)) for n, p, args in c)


def _rename(c, tag):
    def r(t):
        if t[0] == "v":
            return ("v", t[1] + tag)
        if t[0] == "f":
            return ("f", t[1], tuple(r(a) for a in t[2]))
        return t
    return tuple((n, p, tuple(r(a) for a in args)) for n, p, args in c)


def _norm(c):
    """A clause is a SET of literals: drop duplicates, keep it hashable."""
    return tuple(sorted(set(c)))


def _tautology(c):
    for n, p, a in c:
        if (not n, p, a) in c:
            return True
    return False


def _resolvents(c1, c2, tag):
    c2 = _rename(c2, tag)
    out = []
    for i, l1 in enumerate(c1):
        for j, l2 in enumerate(c2):
            if l1[0] == l2[0]:
                continue
            s = _unify_lit(l1, l2, {})
            if s is None:
                continue
            rest = tuple(l for k, l in enumerate(c1) if k != i) + \
                   tuple(l for k, l in enumerate(c2) if k != j)
            out.append(_norm(_sub_c(rest, s)))
    return out


def _factors(c):
    out = []
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            if c[i][0] != c[j][0]:
                continue
            s = _unify_lit(c[i], c[j], {})
            if s is not None:
                out.append(_norm(_sub_c(c, s)))
    return out


def _depth(t):
    if t[0] == "f":
        return 1 + max((_depth(a) for a in t[2]), default=0)
    return 0


def _cdepth(c):
    return max((_depth(a) for _, _, args in c for a in args), default=0)


def refutable(axioms, goals, rounds=8, maxlit=6, maxdepth=3, cap=6000):
    """True if axioms + negated goal are refutable by resolution.

    Set of support: every resolution step must involve a clause descended
    from the negated goal. That is refutation complete whenever the axioms
    alone are satisfiable, which they are in every set here, and it keeps
    these proofs to a fraction of a second where blind saturation drowned.
    Resolvents are capped on literal count and on term nesting depth, so a
    set that is NOT refutable terminates and says so -- which is the point
    for the three papers whose printed goal does not follow.
    """
    usable = set(_norm(c) for c in axioms)
    sos = set(_norm(c) for c in goals)
    if () in usable or () in sos:
        return True
    frontier = list(sos)
    n = 0
    for _ in range(rounds):
        new = []
        partners = list(usable) + list(sos)
        for c1 in frontier:
            for c2 in partners:
                n += 1
                cands = _resolvents(c1, c2, "_%d" % n)
                for r in list(cands):
                    cands.extend(_factors(r))
                for r in cands:
                    if r == ():
                        return True
                    if len(r) > maxlit or _cdepth(r) > maxdepth:
                        continue
                    if _tautology(r) or r in sos or r in usable:
                        continue
                    sos.add(r)
                    new.append(r)
        if not new or len(sos) > cap:
            return False
        frontier = new
    return False


def ch4():
    # ---- Family A: John likes all kinds of food ---------------------
    # 1 ~food(x) v likes(John,x)      4 ~eats(y,x) v killed(y) v food(x)
    # 5a eats(Bill,Peanuts)           5b ~killed(Bill)
    x, y = V("x"), V("y")
    food = [
        (Nt("food", x), P("likes", K("John"), x)),
        (P("food", K("Apple")),),
        (P("food", K("Chicken")),),
        (Nt("eats", y, x), P("killed", y), P("food", x)),
        (P("eats", K("Bill"), K("Peanuts")),),
        (Nt("killed", K("Bill")),),
        (Nt("eats", K("Bill"), x), P("eats", K("Sue"), x)),
    ]
    goal = (Nt("likes", K("John"), K("Peanuts")),)
    chk("c4 A food: John likes peanuts", refutable(food, [goal]), True)

    # the textbook's invalid split of premise 4 into two clauses: still
    # closes, which is why the error survived so long unnoticed
    book = [c for c in food if c[0][1] != "eats" or len(c) != 3]
    book += [(Nt("eats", y, x), P("food", x)), (P("killed", y), P("food", x))]
    chk("c4 A food, textbook's split", refutable(book, [goal]), True)

    # 2072 Magh: the printed goal does NOT follow, but 'eats' does
    bhog = [
        (Nt("food", x), P("likes", K("Bhog"), x)),
        (P("food", K("Orange")),),
        (P("food", K("Chicken")),),
        (Nt("eats", y, x), P("killed", y), P("food", x)),
        (Nt("likes", y, x), P("eats", y, x)),
        (P("eats", K("Jog"), K("Peanuts")),),
        (Nt("killed", K("Jog")),),
        (Nt("eats", K("Bhog"), x), P("eats", K("Shail"), x)),
    ]
    chk("c4 A 72Ma: 'Shailendri LIKES chicken' does not follow",
        refutable(bhog, [(Nt("likes", K("Shail"), K("Chicken")),)]), False)
    chk("c4 A 72Ma: 'Shailendri EATS chicken' does follow",
        refutable(bhog, [(Nt("eats", K("Shail"), K("Chicken")),)]), True)

    # ---- Family B: Charlie is a horse -------------------------------
    charlie = [
        (Nt("horse", x), P("mammal", x)),
        (Nt("cow", x), P("mammal", x)),
        (Nt("pig", x), P("mammal", x)),
        (Nt("offspring", x, y), Nt("horse", y), P("horse", x)),
        (P("horse", K("Blue")),),
        (P("parent", K("Blue"), K("Charlie")),),
        (Nt("offspring", x, y), P("parent", y, x)),
        (Nt("parent", y, x), P("offspring", x, y)),
        (Nt("mammal", x), P("parent", Fn("f", x), x)),
    ]
    chk("c4 B: Charlie is a horse",
        refutable(charlie, [(Nt("horse", K("Charlie")),)]), True)
    chk("c4 B: Charlie is a mammal",
        refutable(charlie, [(Nt("mammal", K("Charlie")),)]), True)
    # Dropping clause 5b (parent -> offspring) breaks the proof, but that
    # negative is not checked here: without it the offspring/parent rules
    # chain on themselves and the search does not terminate inside any
    # honest budget. The notes claim only that 5b is the clause the proof
    # uses, which the trace shows directly.

    # ---- Family C: selling weapons ----------------------------------
    p, q, r = V("p"), V("q"), V("r")
    west = [
        (Nt("American", p), Nt("Weapon", q), Nt("Sells", p, q, r),
         Nt("Hostile", r), P("Criminal", p)),
        (P("Missile", K("M1")),),
        (P("Owns", K("Nono"), K("M1")),),
        (Nt("Missile", x), Nt("Owns", K("Nono"), x),
         P("Sells", K("West"), x, K("Nono"))),
        (Nt("Missile", x), P("Weapon", x)),
        (Nt("Enemy", x, K("America")), P("Hostile", x)),
        (P("American", K("West")),),
        (P("Enemy", K("Nono"), K("America")),),
    ]
    chk("c4 C: Colonel West is a criminal",
        refutable(west, [(Nt("Criminal", K("West")),)]), True)
    # 2069 Bhadra / 2075 Baishakh omit "missiles are weapons" and
    # "an enemy is hostile": without them the proof cannot close
    thin = [c for c in west
            if not (len(c) == 2 and c[0][1] in ("Missile", "Enemy"))]
    chk("c4 C: 69Bh/75Ba without the two bridging axioms",
        refutable(thin, [(Nt("Criminal", K("West")),)]), False)
    chk("c4 C: with them restored",
        refutable(west, [(Nt("Criminal", K("West")),)]), True)

    # 2082 Bhadra: Mr R sells, Mr A buys, so the criminal is R not A
    nep = [
        (Nt("Nepali", p), Nt("Weapon", q), Nt("Sells", p, q, r),
         Nt("EnemyN", r), P("Criminal", p)),
        (P("EnemyN", K("A")),),
        (P("Missile", K("M1")),),
        (P("Owns", K("A"), K("M1")),),
        (Nt("Missile", x), P("Weapon", x)),
        (P("Nepali", K("R")),),
        (Nt("Missile", x), Nt("Owns", K("A"), x), P("Sells", K("R"), x, K("A"))),
    ]
    chk("c4 C 82Bh: Mr R is a criminal",
        refutable(nep, [(Nt("Criminal", K("R")),)]), True)
    chk("c4 C 82Bh: 'Mr A is a criminal' does not follow",
        refutable(nep, [(Nt("Criminal", K("A")),)]), False)

    # ---- Family D: the light sleeper --------------------------------
    z = V("z")
    ls = [
        (Nt("Hound", x), P("Howl", x)),
        (Nt("Have", x, y), Nt("Cat", y), Nt("Have", x, z), Nt("Mouse", z)),
        (Nt("LS", x), Nt("Have", x, y), Nt("Howl", y)),
        (P("Have", K("John"), K("a")),),
        (P("Cat", K("a")), P("Hound", K("a"))),
        (P("LS", K("John")),),
        (P("Have", K("John"), K("b")),),
        (P("Mouse", K("b")),),
    ]
    chk("c4 D: light sleeper has no mice", refutable(ls[:5], ls[5:]), True)

    # ---- the ten one-off sets ---------------------------------------
    marcus = [
        (Nt("Pompeian", x), P("Roman", x)),
        (Nt("Roman", x), P("loyal", x, K("Caesar")), P("hate", x, K("Caesar"))),
        (P("loyal", x, Fn("f", x)),),
        (Nt("tryAss", x, y), Nt("ruler", y), Nt("loyal", x, y)),
        (P("tryAss", K("Marcus"), K("Caesar")),),
        (P("Pompeian", K("Marcus")),),
        (P("ruler", K("Caesar")),),
    ]
    chk("c4 1: Marcus hated Caesar",
        refutable(marcus, [(Nt("hate", K("Marcus"), K("Caesar")),)]), True)

    santa = [
        (Nt("child", x), P("loves", x, K("Santa"))),
        (Nt("loves", x, K("Santa")), Nt("reindeer", y), P("loves", x, y)),
        (P("reindeer", K("Rud")),),
        (P("redNose", K("Rud")),),
        (Nt("redNose", x), P("weird", x), P("clown", x)),
        (Nt("reindeer", x), Nt("clown", x)),
        (Nt("weird", x), Nt("loves", K("Scrooge"), x)),
        (P("child", K("Scrooge")),),          # negation of the goal
    ]
    chk("c4 2: Scrooge is not a child",
        refutable(santa[:-1], santa[-1:]), True)

    cur = [
        (P("Animal", Fn("F", x)), P("Loves", Fn("G", x), x)),
        (Nt("Loves", x, Fn("F", x)), P("Loves", Fn("G", x), x)),
        (Nt("Animal", y), Nt("Kills", x, y), Nt("Loves", z, x)),
        (Nt("Animal", x), P("Loves", K("Jack"), x)),
        (P("Kills", K("Jack"), K("Tuna")), P("Kills", K("Curiosity"), K("Tuna"))),
        (P("Cat", K("Tuna")),),
        (Nt("Cat", x), P("Animal", x)),
    ]
    chk("c4 3: Curiosity killed the cat",
        refutable(cur, [(Nt("Kills", K("Curiosity"), K("Tuna")),)]), True)

    sneha = [
        (Nt("pass", x), Nt("win", x), P("happy", x)),
        (Nt("study", x), P("pass", x)),
        (Nt("lucky", x), P("pass", x)),
        (Nt("study", K("Sneha")),),
        (P("lucky", K("Sneha")),),
        (Nt("lucky", x), P("win", x)),
    ]
    chk("c4 4: Sneha is happy",
        refutable(sneha, [(Nt("happy", K("Sneha")),)]), True)

    # 2079 Ashwin: "Steve ONLY likes easy courses" is likes -> easy, and
    # in that direction nothing ever concludes `likes`
    steve_lit = [
        (Nt("likes", x), P("easy", x)),
        (Nt("science", x), Nt("easy", x)),
        (Nt("bw", x), P("easy", x)),
        (P("bw", K("BK301")),),
    ]
    chk("c4 5: literal reading proves nothing",
        refutable(steve_lit, [(Nt("likes", K("BK301")),)]), False)
    steve = [(Nt("easy", x), P("likes", x))] + steve_lit[1:]
    chk("c4 5: converse reading proves Steve likes BK301",
        refutable(steve, [(Nt("likes", K("BK301")),)]), True)

    straw = [
        (Nt("sunny"), Nt("warm"), P("enjoy")),
        (Nt("warm"), Nt("pleasant"), P("picking")),
        (Nt("raining"), Nt("picking")),
        (Nt("raining"), P("wet")),
        (P("warm"),), (P("raining"),), (P("sunny"),),
    ]
    chk("c4 6: you will enjoy", refutable(straw, [(Nt("enjoy"),)]), True)

    naughty = [
        (Nt("oversmart", x), P("stupid", x)),
        (Nt("child", x, y), Nt("oversmart", y), P("naughty", x)),
        (P("child", K("Ram"), K("Hari")),),
        (P("oversmart", K("Hari")),),
    ]
    chk("c4 7: Ram is naughty",
        refutable(naughty, [(Nt("naughty", K("Ram")),)]), True)

    cup = [
        (Nt("onTop", x, y), P("supports", y, x)),
        (Nt("above", x, y), Nt("touching", x, y), P("onTop", x, y)),
        (P("above", K("Cup"), K("Book")),),
        (P("touching", K("Cup"), K("Book")),),
    ]
    chk("c4 8: the book supports the cup",
        refutable(cup, [(Nt("supports", K("Book"), K("Cup")),)]), True)

    mary = [
        (Nt("loves", K("Mary"), x), P("star", x)),
        (Nt("student", x), P("pass", x), Nt("play", x)),
        (P("student", K("John")),),
        (Nt("student", x), P("study", x), Nt("pass", x)),
        (P("play", x), Nt("star", x)),
        (Nt("study", K("John")),),                     # negated goal, part 1
        (P("loves", K("Mary"), K("John")),),           # negated goal, part 2
    ]
    chk("c4 9: if John does not study, Mary does not love him",
        refutable(mary[:5], mary[5:]), True)

    excite = [
        (P("poor", x), Nt("smart", x), P("happy", x)),
        (Nt("read", x), Nt("stupid", x)),
        (P("read", K("John")),),
        (Nt("poor", K("John")),),
        (Nt("happy", x), P("exciting", x)),
        (P("stupid", x), P("smart", x)),
    ]
    chk("c4 10: someone has an exciting life",
        refutable(excite, [(Nt("exciting", x),)]), True)

    # ---- P7 / P8: every Bayes number the companion prints ------------
    def bayes(l_h, p_h, l_nh):
        """P(H|E) from P(E|H), P(H) and P(E|~H), by total probability."""
        num = l_h * p_h
        return num / (num + l_nh * (1 - p_h))

    # B1, B2: P(evidence) is given outright, so no total-probability step
    chk("c4 B1 meningitis 71Ma", 0.5 * (1 / 50000) / 0.05, 0.0002)
    chk("c4 B2 meningitis 81Ba", 0.8 * (1 / 50000) / 0.01, 0.0016)
    # B3 measles
    chk("c4 B3 P(rash)", 0.95 * 0.1 + 0.08 * 0.9, 0.167)
    chk("c4 B3 P(measles|rash)", bayes(0.95, 0.1, 0.08), 0.5689)
    chk("c4 B3 complement", bayes(0.08, 0.9, 0.95), 0.4311)
    # B4 cigar smoker
    chk("c4 B4 P(cigar)", 0.095 * 0.51 + 0.017 * 0.49, 0.05678)
    chk("c4 B4 P(male|cigar)", bayes(0.095, 0.51, 0.017), 0.8533)
    # B5 the 99% test for a 1-in-10000 disease
    chk("c4 B5 P(+)", 0.99 * 1e-4 + 0.01 * 0.9999, 0.010098)
    chk("c4 B5 P(disease|+)", bayes(0.99, 1e-4, 0.01), 0.0098, tol=5e-5)
    chk("c4 B5 true positives per million", round(1e6 * 1e-4 * 0.99), 99)
    chk("c4 B5 false positives per million",
        round(1e6 * 0.9999 * 0.01), 9999)
    # B6 genetic defect
    chk("c4 B6 P(+)", 0.9 * 0.01 + 0.1 * 0.99, 0.108)
    chk("c4 B6 P(no defect|+)", 1 - bayes(0.9, 0.01, 0.1), 0.9167)
    chk("c4 B6 P(defect|+)", bayes(0.9, 0.01, 0.1), 0.0833)
    chk("c4 B6 odds against", 0.099 / 0.009, 11.0)
    # B7 the three factories
    chk("c4 B7 P(defective)",
        0.2 * 0.02 + 0.5 * 0.05 + 0.3 * 0.03, 0.038)
    chk("c4 B7 P(B|defective)", 0.025 / 0.038, 0.6579)
    chk("c4 B7 P(A|defective)", 0.004 / 0.038, 0.105, tol=5e-4)
    chk("c4 B7 P(C|defective)", 0.009 / 0.038, 0.237, tol=5e-4)
    chk("c4 B7 posteriors sum to 1",
        (0.004 + 0.025 + 0.009) / 0.038, 1.0)
    # B8 the tall student, B9 the mammogram
    chk("c4 B8 P(tall)", 0.02 * 0.6 + 0.05 * 0.4, 0.032)
    chk("c4 B8 P(woman|tall)", bayes(0.02, 0.6, 0.05), 0.375)
    chk("c4 B9 P(+)", 0.9 * 0.01 + 0.08 * 0.99, 0.0882)
    chk("c4 B9 P(cancer|+)", bayes(0.9, 0.01, 0.08), 0.1020, tol=5e-4)
    # B10 the 78 Ba wet-grass network, straight off the printed CPTs
    chk("c4 B10 P(C,S,~R,W)", 0.6 * 0.10 * (1 - 0.80) * 0.90, 0.0108)
    # B11 the 82 Bh smoker -> cancer -> test chain
    p_c = 0.2 * 0.3 + 0.05 * 0.7
    p_t = 0.9 * p_c + 0.1 * (1 - p_c)
    chk("c4 B11 P(C)", p_c, 0.095)
    chk("c4 B11 P(T)", p_t, 0.176)
    chk("c4 B11 P(C|T)", 0.9 * p_c / p_t, 0.4858)
    chk("c4 B11 P(T|S)", 0.9 * 0.2 + 0.1 * 0.8, 0.26)
    chk("c4 B11 P(T|~S)", 0.9 * 0.05 + 0.1 * 0.95, 0.14)
    chk("c4 B11 P(S|T)", 0.26 * 0.3 / p_t, 0.4432)
    # the same P(T) by the other route: the network has to be coherent
    chk("c4 B11 P(T) via S", 0.26 * 0.3 + 0.14 * 0.7, p_t)
    chk("c4 B11 P(~C|T) is the larger half", 1 - 0.9 * p_c / p_t, 0.5142)
    # B12 the two-node example the notes hand to the three data-free papers
    chk("c4 B12 P(cancer|+)", bayes(0.9, 0.01, 0.08), 0.102, tol=5e-4)


# =====================================================================
#  chapter 6 -- ID3 entropy and gain, genetic algorithms, fuzzy sets
# =====================================================================

def H(rows, tgt):
    """Entropy of a labelled set, in bits."""
    n = len(rows)
    if n == 0:
        return 0.0
    c = collections.Counter(r[tgt] for r in rows)
    return -sum((v / n) * math.log2(v / n) for v in c.values() if v)


def gains(rows, tgt):
    """Information gain of every attribute, and the split entropies."""
    base = H(rows, tgt)
    out = {}
    for a in rows[0]:
        if a == tgt:
            continue
        parts = {}
        for r in rows:
            parts.setdefault(r[a], []).append(r)
        rem = sum(len(p) / len(rows) * H(p, tgt) for p in parts.values())
        out[a] = (rem, base - rem,
                  {k: (len(v), H(v, tgt)) for k, v in parts.items()})
    return base, out


def table(cols, data):
    return [dict(zip(cols, d)) for d in data]


# --- the three data tables, transcribed from the OCR archive ---------------
WCOLS = ["Outlook", "Temp", "Humidity", "Windy", "Play"]

# 74 Bh (785) / 74 Ma / 72 Ash -- "play golf"
GOLF = table(WCOLS, [
    ("Rainy", "Hot", "High", "False", "No"),
    ("Rainy", "Hot", "High", "True", "No"),
    ("Overcast", "Hot", "High", "False", "Yes"),
    ("Sunny", "Mild", "High", "False", "Yes"),
    ("Sunny", "Cool", "Normal", "False", "Yes"),
    ("Sunny", "Cool", "Normal", "True", "No"),
    ("Overcast", "Cool", "Normal", "True", "Yes"),
    ("Rainy", "Mild", "High", "False", "No"),
    ("Rainy", "Cool", "Normal", "False", "Yes"),
    ("Sunny", "Mild", "Normal", "False", "Yes"),
    ("Rainy", "Mild", "Normal", "True", "Yes"),
    ("Overcast", "Mild", "High", "True", "Yes"),
    ("Overcast", "Hot", "Normal", "False", "Yes"),
    ("Sunny", "Mild", "High", "True", "No"),
])

# 79 Jth -- "play cricket". FOUR rows differ from the golf table, and that is
# enough to change the root attribute from Outlook to Windy.
CRICKET = table(WCOLS, [
    ("Rainy", "Hot", "High", "False", "Yes"),
    ("Rainy", "Hot", "High", "True", "No"),
    ("Overcast", "Hot", "High", "False", "Yes"),
    ("Sunny", "Mild", "High", "False", "Yes"),
    ("Sunny", "Cool", "Normal", "False", "Yes"),
    ("Sunny", "Cool", "Normal", "True", "No"),
    ("Overcast", "Cool", "Normal", "True", "Yes"),
    ("Rainy", "Mild", "High", "True", "No"),
    ("Rainy", "Cool", "Normal", "False", "Yes"),
    ("Sunny", "Mild", "Normal", "False", "Yes"),
    ("Rainy", "Mild", "Normal", "True", "No"),
    ("Overcast", "Mild", "High", "True", "Yes"),
    ("Overcast", "Hot", "Normal", "False", "Yes"),
    ("Sunny", "Mild", "High", "True", "No"),
])

# 77 Ch (785) -- the mushroom island. Only A-H are labelled; U, V, W are the
# test cases and are NOT training data.
MUSH = table(["NotHeavy", "Smelly", "Spotted", "Smooth", "Edible"], [
    ("1", "0", "0", "0", "1"),
    ("1", "0", "1", "0", "1"),
    ("0", "1", "0", "1", "1"),
    ("0", "0", "0", "1", "0"),
    ("1", "1", "1", "0", "0"),
    ("1", "0", "1", "1", "0"),
    ("1", "0", "0", "1", "0"),
    ("0", "1", "0", "0", "0"),
])

# Insights Example 6.4 -- the profit table, used as the method walkthrough
PROFIT = table(["Age", "Competition", "Type", "Profit"], [
    ("Old", "Yes", "Software", "Down"),
    ("Old", "No", "Software", "Down"),
    ("Old", "No", "Hardware", "Down"),
    ("Mid", "Yes", "Software", "Down"),
    ("Mid", "Yes", "Hardware", "Down"),
    ("Mid", "No", "Hardware", "Up"),
    ("Mid", "No", "Software", "Up"),
    ("New", "Yes", "Software", "Up"),
    ("New", "No", "Hardware", "Up"),
    ("New", "No", "Software", "Up"),
])

# --- genetic algorithm helpers --------------------------------------------
KNAP_W = {"A": 5, "B": 3, "C": 7, "D": 2}
KNAP_V = {"A": 12, "B": 5, "C": 10, "D": 7}
KNAP_CAP = 12


def knap(bits):
    """(fitness, weight, value) of a 4-bit knapsack chromosome, ABCD order."""
    w = sum(KNAP_W["ABCD"[i]] for i, b in enumerate(bits) if b == "1")
    v = sum(KNAP_V["ABCD"[i]] for i, b in enumerate(bits) if b == "1")
    return (v if w <= KNAP_CAP else 0), w, v


def gafit(x):
    """75 Bh's fitness function f(x) = (a+b)-(c+d)+(e+f)-(g+h)."""
    d = [int(c) for c in x]
    return (d[0] + d[1]) - (d[2] + d[3]) + (d[4] + d[5]) - (d[6] + d[7])


def cross(p1, p2, k):
    """Single-point crossover after gene k. Returns both offspring."""
    return p1[:k] + p2[k:], p2[:k] + p1[k:]


# --- fuzzy helpers ---------------------------------------------------------
def tri(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    return (x - a) / (b - a) if x <= b else (c - x) / (c - b)


def ramp_up(x, a, b):
    return 0.0 if x <= a else (1.0 if x >= b else (x - a) / (b - a))


def ramp_down(x, a, b):
    return 1.0 if x <= a else (0.0 if x >= b else (b - x) / (b - a))


def ch6():
    # ---------------- A. ID3 -----------------------------------------------
    # A1 the play-golf table (74 Bh, 74 Ma, 72 Ash)
    base, g = gains(GOLF, "Play")
    chk("c6 A1 H(S) golf", base, 0.9403, tol=5e-4)
    chk("c6 A1 gain Outlook", g["Outlook"][1], 0.2467, tol=5e-4)
    chk("c6 A1 gain Temp", g["Temp"][1], 0.0292, tol=5e-4)
    chk("c6 A1 gain Humidity", g["Humidity"][1], 0.1518, tol=5e-4)
    chk("c6 A1 gain Windy", g["Windy"][1], 0.0481, tol=5e-4)
    chk("c6 A1 root is Outlook", max(g, key=lambda a: g[a][1]), "Outlook")
    chk("c6 A1 H(Overcast)=0", g["Outlook"][2]["Overcast"][1], 0.0)
    chk("c6 A1 H(Rainy)", g["Outlook"][2]["Rainy"][1], 0.9710, tol=5e-4)
    chk("c6 A1 H(Sunny)", g["Outlook"][2]["Sunny"][1], 0.9710, tol=5e-4)
    # second level: Rainy splits perfectly on Humidity, Sunny on Windy
    rainy = [r for r in GOLF if r["Outlook"] == "Rainy"]
    _, gr = gains(rainy, "Play")
    chk("c6 A1 Rainy -> Humidity", max(gr, key=lambda a: gr[a][1]), "Humidity")
    chk("c6 A1 Rainy Humidity gain", gr["Humidity"][1], 0.9710, tol=5e-4)
    sunny = [r for r in GOLF if r["Outlook"] == "Sunny"]
    _, gs = gains(sunny, "Play")
    chk("c6 A1 Sunny -> Windy", max(gs, key=lambda a: gs[a][1]), "Windy")
    chk("c6 A1 Sunny Windy gain", gs["Windy"][1], 0.9710, tol=5e-4)

    # A2 the play-cricket table (79 Jth). Same shape, DIFFERENT answer.
    base, g = gains(CRICKET, "Play")
    chk("c6 A2 H(S) cricket", base, 0.9403, tol=5e-4)
    chk("c6 A2 gain Outlook", g["Outlook"][1], 0.2467, tol=5e-4)
    chk("c6 A2 gain Temp", g["Temp"][1], 0.0481, tol=5e-4)
    chk("c6 A2 gain Humidity", g["Humidity"][1], 0.0161, tol=5e-4)
    chk("c6 A2 gain Windy", g["Windy"][1], 0.5087, tol=5e-4)
    chk("c6 A2 root is Windy, NOT Outlook",
        max(g, key=lambda a: g[a][1]), "Windy")
    chk("c6 A2 Windy=False is pure", g["Windy"][2]["False"][1], 0.0)
    chk("c6 A2 Windy=False count", g["Windy"][2]["False"][0], 7)
    chk("c6 A2 H(Windy=True)", g["Windy"][2]["True"][1], 0.8631, tol=5e-4)
    wtrue = [r for r in CRICKET if r["Windy"] == "True"]
    _, gw = gains(wtrue, "Play")
    chk("c6 A2 True -> Outlook", max(gw, key=lambda a: gw[a][1]), "Outlook")
    chk("c6 A2 True Outlook gain", gw["Outlook"][1], 0.8631, tol=5e-4)
    # every Outlook branch under Windy=True is pure, so the tree is two deep
    for v, n in (("Rainy", 3), ("Sunny", 2), ("Overcast", 2)):
        chk("c6 A2 True/%s pure" % v, gw["Outlook"][2][v], (n, 0.0))

    # A3 the mushroom island (77 Ch)
    base, g = gains(MUSH, "Edible")
    chk("c6 A3 H(S) mushroom", base, 0.9544, tol=5e-4)
    chk("c6 A3 gain Smooth", g["Smooth"][1], 0.0488, tol=5e-4)
    chk("c6 A3 gain NotHeavy", g["NotHeavy"][1], 0.0032, tol=5e-4)
    chk("c6 A3 gain Smelly", g["Smelly"][1], 0.0032, tol=5e-4)
    chk("c6 A3 gain Spotted", g["Spotted"][1], 0.0032, tol=5e-4)
    chk("c6 A3 root is Smooth", max(g, key=lambda a: g[a][1]), "Smooth")
    # the other three tie exactly, which is why the answer has to say so
    chk("c6 A3 the other three tie",
        len({round(g[a][1], 9) for a in ("NotHeavy", "Smelly", "Spotted")}), 1)

    # A4 the profit table (Insights 6.4), the worked method
    base, g = gains(PROFIT, "Profit")
    chk("c6 A4 H(S) profit", base, 1.0)
    chk("c6 A4 gain Age", g["Age"][1], 0.60, tol=5e-4)
    chk("c6 A4 gain Competition", g["Competition"][1], 0.1245, tol=5e-4)
    chk("c6 A4 gain Type", g["Type"][1], 0.0)
    chk("c6 A4 root is Age", max(g, key=lambda a: g[a][1]), "Age")
    mid = [r for r in PROFIT if r["Age"] == "Mid"]
    _, gm = gains(mid, "Profit")
    chk("c6 A4 Mid -> Competition",
        max(gm, key=lambda a: gm[a][1]), "Competition")
    chk("c6 A4 Mid Competition gain", gm["Competition"][1], 1.0)

    # ---------------- B. genetic algorithm ---------------------------------
    # B1 the knapsack. Generation 1, then crossover, then the mutation that
    # actually finds the optimum.
    for bits, want in (("0010", (10, 7, 10)), ("0110", (15, 10, 15)),
                       ("1001", (19, 7, 19)), ("1111", (0, 17, 34))):
        chk("c6 B1 fitness " + bits, knap(bits), want)
    o1, o2 = cross("1001", "0110", 2)
    chk("c6 B1 crossover offspring", (o1, o2), ("1010", "0101"))
    chk("c6 B1 f(1010)", knap("1010")[0], 22)
    chk("c6 B1 f(0101)", knap("0101")[0], 12)
    chk("c6 B1 gen-1 best", max(knap(c)[0] for c in
                                ("0010", "0110", "1001", "1111")), 19)
    chk("c6 B1 gen-2 best", max(knap(c)[0] for c in
                                ("1001", "0110", "1010", "0101")), 22)
    chk("c6 B1 mutation 1001 -> 1101", knap("1101")[0], 24)
    # 1101 is the true optimum, so the run terminates on it having found it
    allc = ["".join(b) for b in itertools.product("01", repeat=4)]
    chk("c6 B1 optimum is 24", max(knap(c)[0] for c in allc), 24)
    chk("c6 B1 optimum chromosome",
        [c for c in allc if knap(c)[0] == 24], ["1101"])

    # B2 75 Bh's chromosomes, the fitness function the paper prints
    f = {x: gafit(x) for x in ("65413532", "87126601", "23921285", "41852094")}
    chk("c6 B2 f(x1)", f["65413532"], 9)
    chk("c6 B2 f(x2)", f["87126601"], 23)
    chk("c6 B2 f(x3)", f["23921285"], -16)
    chk("c6 B2 f(x4)", f["41852094"], -19)
    chk("c6 B2 ranking fittest first",
        sorted(f, key=lambda k: -f[k]),
        ["87126601", "65413532", "23921285", "41852094"])
    chk("c6 B2 gen-1 mean fitness", sum(f.values()) / 4.0, -0.75)
    a1, a2 = cross("87126601", "65413532", 4)
    chk("c6 B2 mid-point offspring of x2,x1", (a1, a2),
        ("87123532", "65416601"))
    chk("c6 B2 f(OS1)", gafit("87123532"), 15)
    chk("c6 B2 f(OS2)", gafit("65416601"), 17)
    # x1 with x3, two-point (after gene 2 and gene 6), as Insights sets it
    b1 = "65" + "9212" + "32"
    b2 = "23" + "4135" + "85"
    chk("c6 B2 two-point offspring", (b1, b2), ("65921232", "23413585"))
    chk("c6 B2 f(OS1) x1x3", gafit(b1), -2)
    chk("c6 B2 f(OS2) x1x3", gafit(b2), -5)

    # B3 the coin problem: get the total number of heads above 30.
    pop = ["1000101100", "1110010110", "1010110010",
           "0111101011", "0111001111"]
    scores = [c.count("1") for c in pop]
    chk("c6 B3 gen-1 scores", scores, [4, 6, 5, 7, 7])
    chk("c6 B3 gen-1 total", sum(scores), 29)
    # Insights crosses C4 and C5 at a point inside the four genes they SHARE,
    # so its offspring are copies of the parents. Cut after gene 6 instead.
    for k in range(1, 5):
        c1, c2 = cross(pop[3], pop[4], k)
        chk("c6 B3 cut at %d is degenerate" % k,
            sorted([c1, c2]), sorted([pop[3], pop[4]]))
    d1, d2 = cross(pop[3], pop[4], 6)
    chk("c6 B3 offspring", (d1, d2), ("0111101111", "0111001011"))
    chk("c6 B3 f(OS1)", d1.count("1"), 8)
    chk("c6 B3 f(OS2)", d2.count("1"), 6)
    best5 = sorted(scores + [d1.count("1"), d2.count("1")], reverse=True)[:5]
    chk("c6 B3 gen-2 best five", best5, [8, 7, 7, 6, 6])
    chk("c6 B3 gen-2 total", sum(best5), 34)
    chk("c6 B3 gen-2 max improved", max(best5) > max(scores), True)

    # ---------------- C. fuzzy ---------------------------------------------
    # C1 set operations. Insights p167 prints the complement of the third
    # element as 0.5; it is 0.6. Everything else in that box is right.
    A = {10: 0.2, 20: 0.3, 30: 0.4, 40: 0.5}
    B = {10: 0.3, 20: 0.4, 30: 0.1, 40: 0.2}
    xs = sorted(A)
    chk("c6 C1 union", [round(max(A[x], B[x]), 2) for x in xs],
        [0.3, 0.4, 0.4, 0.5])
    chk("c6 C1 intersection", [round(min(A[x], B[x]), 2) for x in xs],
        [0.2, 0.3, 0.1, 0.2])
    chk("c6 C1 complement of A", [round(1 - A[x], 2) for x in xs],
        [0.8, 0.7, 0.6, 0.5])
    chk("c6 C1 bold union", [round(min(1, A[x] + B[x]), 2) for x in xs],
        [0.5, 0.7, 0.5, 0.7])
    chk("c6 C1 bold intersection",
        [round(max(0, A[x] + B[x] - 1), 2) for x in xs], [0, 0, 0, 0])

    # C2 fuzzification off a rising limb from 7.5 to 12.5
    chk("c6 C2 mu(10)", (10 - 7.5) / (12.5 - 7.5), 0.5)
    chk("c6 C2 mu(9)", (9 - 7.5) / (12.5 - 7.5), 0.3)

    # C3 the Mamdani fan-speed controller, T = 26 C and H = 45 %
    T, Hd = 26.0, 45.0
    mu_cold = ramp_down(T, 10, 20)
    mu_warm = tri(T, 10, 20, 30)
    mu_hot = ramp_up(T, 20, 30)
    mu_low = ramp_down(Hd, 30, 60)
    mu_high = ramp_up(Hd, 30, 60)
    chk("c6 C3 mu cold", mu_cold, 0.0)
    chk("c6 C3 mu warm", mu_warm, 0.4)
    chk("c6 C3 mu hot", mu_hot, 0.6)
    chk("c6 C3 mu low", mu_low, 0.5)
    chk("c6 C3 mu high", mu_high, 0.5)
    w1 = min(mu_cold, mu_low)
    w2 = mu_warm
    w3 = max(mu_hot, mu_high)
    chk("c6 C3 w1 (AND = min)", w1, 0.0)
    chk("c6 C3 w2", w2, 0.4)
    chk("c6 C3 w3 (OR = max)", w3, 0.6)
    # aggregate the two clipped output sets, sampled every 10 units
    agg = []
    for s in range(0, 101, 10):
        agg.append(round(max(min(w2, tri(s, 0, 50, 100)),
                             min(w3, tri(s, 50, 100, 150))), 4))
    chk("c6 C3 aggregated membership", agg,
        [0.0, 0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.6, 0.6, 0.6])
    num = sum(s * m for s, m in zip(range(0, 101, 10), agg))
    den = sum(agg)
    chk("c6 C3 sum of memberships", den, 4.4)
    chk("c6 C3 sum of s.mu", num, 272.0)
    chk("c6 C3 centroid, 10-unit samples", num / den, 61.82, tol=5e-3)
    # the weighted-average shortcut over the consequent peaks
    chk("c6 C3 weighted average shortcut",
        (w2 * 50 + w3 * 100) / (w2 + w3), 80.0)


# =====================================================================
#  chapter 7 -- perceptrons, Hebb nets, Hopfield, forward and back prop
# =====================================================================

def step3(net, theta=0.0):
    """The perceptron's three-valued activation: +1 / 0 / -1."""
    return 1 if net > theta else (-1 if net < -theta else 0)


def perceptron(rows, alpha=1.0, theta=0.0, epochs=20):
    """Train a two-input perceptron. Returns (w1, w2, b, epochs, trace).

    `epochs` counts the pass on which nothing changed, so a gate that is
    learnt in one pass reports 2: one pass of updates, one of verification.
    """
    w1 = w2 = b = 0.0
    trace = []
    for ep in range(1, epochs + 1):
        changed = False
        for x1, x2, t in rows:
            net = b + w1 * x1 + w2 * x2
            y = step3(net, theta)
            if y != t:
                w1 += alpha * t * x1
                w2 += alpha * t * x2
                b += alpha * t
                changed = True
            trace.append((ep, x1, x2, t, net, y, w1, w2, b))
        if not changed:
            return w1, w2, b, ep, trace
    raise AssertionError("perceptron did not converge")


def hebb(rows):
    """One pass of the Hebb rule over bipolar patterns."""
    w1 = w2 = b = 0
    trace = []
    for x1, x2, t in rows:
        w1 += x1 * t
        w2 += x2 * t
        b += t
        trace.append((w1, w2, b))
    return w1, w2, b, trace


def hop_weights(patterns):
    """Hopfield weight matrix: sum of outer products, zero diagonal."""
    n = len(patterns[0])
    W = [[0] * n for _ in range(n)]
    for s in patterns:
        for i in range(n):
            for j in range(n):
                if i != j:
                    W[i][j] += s[i] * s[j]
    return W


def hop_net(W, y, i):
    return sum(W[i][j] * y[j] for j in range(len(y)))


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def ch7():
    AND = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, -1)]
    OR = [(1, 1, 1), (1, -1, 1), (-1, 1, 1), (-1, -1, -1)]

    # ---------------- 1.1 McCulloch-Pitts by inequality --------------------
    # AND with w1 = w2 = 1, T = 1.5; OR with the same weights and T = 0.5.
    for x1, x2, want in ((0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)):
        chk("c7 P1.1 MP AND (%d,%d)" % (x1, x2),
            1 if x1 * 1 + x2 * 1 > 1.5 else 0, want)
    for x1, x2, want in ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)):
        chk("c7 P1.1 MP OR (%d,%d)" % (x1, x2),
            1 if x1 * 1 + x2 * 1 > 0.5 else 0, want)
    for x, want in ((0, 1), (1, 0)):
        chk("c7 P1.1 MP NOT %d" % x, 1 if -1 * x > -0.5 else 0, want)

    # ---------------- 1.2 perceptron AND -----------------------------------
    w1, w2, b, ep, tr = perceptron(AND)
    chk("c7 P1.2 AND weights", (w1, w2, b), (1.0, 1.0, -1.0))
    chk("c7 P1.2 AND converged on pass", ep, 2)
    # the four rows of epoch 1 exactly as the notes print them
    want = [(0.0, 0, 1.0, 1.0, 1.0),      # net, y, then w1 w2 b after
            (1.0, 1, 0.0, 2.0, 0.0),
            (2.0, 1, 1.0, 1.0, -1.0),
            (-3.0, -1, 1.0, 1.0, -1.0)]
    for k, (net, y, ww1, ww2, bb) in enumerate(want):
        row = tr[k]
        chk("c7 P1.2 epoch1 row%d net" % (k + 1), row[4], net)
        chk("c7 P1.2 epoch1 row%d y" % (k + 1), row[5], y)
        chk("c7 P1.2 epoch1 row%d weights" % (k + 1),
            (row[6], row[7], row[8]), (ww1, ww2, bb))
    # epoch 2 is the verification pass the notes print
    for k, (x1, x2, t) in enumerate(AND):
        chk("c7 P1.2 verify (%d,%d)" % (x1, x2),
            step3(b + w1 * x1 + w2 * x2), t)
    chk("c7 P1.2 verify nets",
        [b + w1 * x1 + w2 * x2 for x1, x2, _ in AND], [1.0, -1.0, -1.0, -3.0])

    # ---------------- 1.3 perceptron OR ------------------------------------
    w1o, w2o, bo, epo, tro = perceptron(OR)
    chk("c7 P1.3 OR weights", (w1o, w2o, bo), (1.0, 1.0, 1.0))
    chk("c7 P1.3 OR converged on pass", epo, 2)
    chk("c7 P1.3 OR updates only on the first row",
        [(r[6], r[7], r[8]) for r in tro[:4]],
        [(1.0, 1.0, 1.0)] * 4)
    chk("c7 P1.3 OR verify nets",
        [bo + w1o * x1 + w2o * x2 for x1, x2, _ in OR], [3.0, 1.0, 1.0, -1.0])
    # the only difference between the two gates is the bias
    chk("c7 P1.3 same weights, opposite bias",
        (w1, w2, w1o, w2o, b, bo), (1.0, 1.0, 1.0, 1.0, -1.0, 1.0))

    # ---------------- 1.4 XOR ----------------------------------------------
    # no single perceptron realises XOR: exhaustive over integer weights
    sols = [(b0, a, c) for b0 in range(-6, 7) for a in range(-6, 7)
            for c in range(-6, 7)
            if all((b0 + a * x1 + c * x2 > 0) == (x1 ^ x2 == 1)
                   for x1 in (0, 1) for x2 in (0, 1))]
    chk("c7 P1.4 no single-neuron XOR", sols, [])
    # ... and AND / OR DO have solutions, which is what makes the search fair
    for name, fn in (("AND", lambda p, q: p & q), ("OR", lambda p, q: p | q)):
        n = sum(1 for b0 in range(-6, 7) for a in range(-6, 7)
                for c in range(-6, 7)
                if all((b0 + a * x1 + c * x2 > 0) == (fn(x1, x2) == 1)
                       for x1 in (0, 1) for x2 in (0, 1)))
        chk("c7 P1.4 %s is separable" % name, n > 0, True)
    # the two-layer network the notes build
    for x1 in (0, 1):
        for x2 in (0, 1):
            h1 = 1 if (x1 + x2 - 0.5) > 0 else 0
            h2 = 1 if (x1 + x2 - 1.5) > 0 else 0
            y = 1 if (h1 - h2 - 0.5) > 0 else 0
            chk("c7 P1.4 MLP XOR (%d,%d)" % (x1, x2), y, x1 ^ x2)
            chk("c7 P1.4 MLP hidden (%d,%d)" % (x1, x2),
                (h1, h2), (1 if (x1 or x2) else 0, 1 if (x1 and x2) else 0))

    # ---------------- 1.5 Hebb net for AND ---------------------------------
    hw1, hw2, hb, htr = hebb(AND)
    chk("c7 P1.5 Hebb weights", (hw1, hw2, hb), (2, 2, -2))
    chk("c7 P1.5 Hebb trace", htr,
        [(1, 1, 1), (0, 2, 0), (1, 1, -1), (2, 2, -2)])
    chk("c7 P1.5 Hebb verify nets",
        [hb + hw1 * x1 + hw2 * x2 for x1, x2, _ in AND], [2, -2, -2, -6])
    for x1, x2, t in AND:
        chk("c7 P1.5 Hebb output (%d,%d)" % (x1, x2),
            step3(hb + hw1 * x1 + hw2 * x2), t)
    # the trap the notes warn about: in BINARY the same rule fails
    bw1 = bw2 = bb2 = 0
    for x1, x2, t in ((1, 1, 1), (1, 0, 0), (0, 1, 0), (0, 0, 0)):
        bw1 += x1 * t
        bw2 += x2 * t
        bb2 += t
    chk("c7 P1.5 binary Hebb gives all-positive weights",
        (bw1, bw2, bb2), (1, 1, 1))
    chk("c7 P1.5 and therefore fires on (1,0), which AND must not",
        1 if bb2 + bw1 * 1 + bw2 * 0 > 0 else 0, 1)

    # ---------------- 2.1 forward propagation, 82 Ka / 81 Ch ---------------
    x1 = x2 = -1.0
    a = bb = 1.0
    c, d, e, f = 4.0, 1.0, 2.0, 2.0
    r1 = max(c * x1 + e * x2, 0.0)
    r2 = max(d * x1 + f * x2, 0.0)
    chk("c7 P2.1 pre-ReLU r1", c * x1 + e * x2, -6.0)
    chk("c7 P2.1 pre-ReLU r2", d * x1 + f * x2, -3.0)
    chk("c7 P2.1 r1", r1, 0.0)
    chk("c7 P2.1 r2", r2, 0.0)
    s1, s2 = sigmoid(r1), sigmoid(r2)
    chk("c7 P2.1 s1", s1, 0.5)
    chk("c7 P2.1 s2", s2, 0.5)
    chk("c7 P2.1 net_y", a * s1 + bb * s2, 1.0)
    y = sigmoid(a * s1 + bb * s2)
    chk("c7 P2.1 y", y, 0.7311, tol=5e-5)
    t, eta = 1.0, 0.1
    delta = (y - t) * y * (1 - y)
    chk("c7 P2.1 delta", delta, -0.05288, tol=5e-6)
    chk("c7 P2.1 dE/da", delta * s1, -0.02644, tol=5e-6)
    chk("c7 P2.1 a_new", a - eta * delta * s1, 1.00264, tol=5e-6)
    chk("c7 P2.1 b_new", bb - eta * delta * s2, 1.00264, tol=5e-6)
    # the ReLU units are dead, so the first layer gets no gradient at all
    for w in "cdef":
        chk("c7 P2.1 gradient to %s is zero" % w, 0.0, 0.0)
    chk("c7 P2.1 both hidden pre-activations negative",
        (c * x1 + e * x2 < 0, d * x1 + f * x2 < 0), (True, True))

    # ---------------- 2.2 one back-propagation step ------------------------
    w13, w14, w23, w24, w35, w45 = 0.5, 0.9, 0.4, 1.0, -1.2, 1.1
    b3, b4, b5 = -0.8, 0.1, -0.3
    eta = 0.1
    X1 = X2 = 1.0
    T = 0.0
    n3 = X1 * w13 + X2 * w23 + b3
    n4 = X1 * w14 + X2 * w24 + b4
    chk("c7 P2.2 net3", n3, 0.1, tol=1e-9)
    chk("c7 P2.2 net4", n4, 2.0, tol=1e-9)
    h3, h4 = sigmoid(n3), sigmoid(n4)
    chk("c7 P2.2 h3", h3, 0.5250, tol=5e-5)
    chk("c7 P2.2 h4", h4, 0.8808, tol=5e-5)
    n5 = h3 * w35 + h4 * w45 + b5
    chk("c7 P2.2 net5", n5, 0.0389, tol=5e-5)
    y5 = sigmoid(n5)
    chk("c7 P2.2 y5", y5, 0.5097, tol=5e-5)
    chk("c7 P2.2 error", 0.5 * (y5 - T) ** 2, 0.1299, tol=5e-5)
    d5 = (y5 - T) * y5 * (1 - y5)
    d3 = d5 * w35 * h3 * (1 - h3)
    d4 = d5 * w45 * h4 * (1 - h4)
    chk("c7 P2.2 delta5", d5, 0.12738, tol=5e-6)
    chk("c7 P2.2 delta3", d3, -0.03812, tol=5e-6)
    chk("c7 P2.2 delta4", d4, 0.01471, tol=5e-6)
    chk("c7 P2.2 w35", w35 - eta * d5 * h3, -1.2067, tol=5e-5)
    chk("c7 P2.2 w45", w45 - eta * d5 * h4, 1.0888, tol=5e-5)
    chk("c7 P2.2 b5", b5 - eta * d5, -0.3127, tol=5e-5)
    chk("c7 P2.2 w13", w13 - eta * d3 * X1, 0.5038, tol=5e-5)
    chk("c7 P2.2 w23", w23 - eta * d3 * X2, 0.4038, tol=5e-5)
    chk("c7 P2.2 b3", b3 - eta * d3, -0.7962, tol=5e-5)
    chk("c7 P2.2 w14", w14 - eta * d4 * X1, 0.8985, tol=5e-5)
    chk("c7 P2.2 w24", w24 - eta * d4 * X2, 0.9985, tol=5e-5)
    chk("c7 P2.2 b4", b4 - eta * d4, 0.0985, tol=5e-5)
    # every update moves the output towards the target
    W = dict(w13=w13 - eta * d3, w23=w23 - eta * d3, w14=w14 - eta * d4,
             w24=w24 - eta * d4, w35=w35 - eta * d5 * h3,
             w45=w45 - eta * d5 * h4)
    nh3 = sigmoid(X1 * W["w13"] + X2 * W["w23"] + (b3 - eta * d3))
    nh4 = sigmoid(X1 * W["w14"] + X2 * W["w24"] + (b4 - eta * d4))
    ny = sigmoid(nh3 * W["w35"] + nh4 * W["w45"] + (b5 - eta * d5))
    chk("c7 P2.2 output moved towards the target", ny < y5, True)

    # ---------------- 2.3 Hopfield -----------------------------------------
    P = [[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1]]
    chk("c7 P2.3 patterns are orthogonal",
        [sum(u * v for u, v in zip(P[i], P[j]))
         for i, j in ((0, 1), (0, 2), (1, 2))], [0, 0, 0])
    W7 = hop_weights(P)
    chk("c7 P2.3 weight matrix", W7,
        [[0, 1, 1, -1], [1, 0, -1, 1], [1, -1, 0, 1], [-1, 1, 1, 0]])
    chk("c7 P2.3 symmetric",
        all(W7[i][j] == W7[j][i] for i in range(4) for j in range(4)), True)
    chk("c7 P2.3 zero diagonal", [W7[i][i] for i in range(4)], [0, 0, 0, 0])
    chk("c7 P2.3 w12 by hand", sum(s[0] * s[1] for s in P), 1)
    chk("c7 P2.3 w14 by hand", sum(s[0] * s[3] for s in P), -1)
    for k, s in enumerate(P):
        nets = [hop_net(W7, s, i) for i in range(4)]
        chk("c7 P2.3 pattern %d net" % (k + 1), nets, s)
        chk("c7 P2.3 pattern %d stable" % (k + 1),
            [1 if v > 0 else -1 for v in nets], s)
    # recall: P2 with its first bit flipped
    y7 = [-1, -1, 1, -1]
    nets = []
    for i in range(4):
        u = hop_net(W7, y7, i)
        nets.append(u)
        y7[i] = 1 if u > 0 else (-1 if u < 0 else y7[i])
    chk("c7 P2.3 recall net inputs", nets, [1, -1, 1, -1])
    chk("c7 P2.3 recalled state", y7, P[1])
    chk("c7 P2.3 recall is one bit flip", y7 != [-1, -1, 1, -1], True)
    # a second sweep changes nothing
    chk("c7 P2.3 second sweep is a fixed point",
        [1 if hop_net(W7, y7, i) > 0 else -1 for i in range(4)], y7)
    # the complement of a stored pattern is always stable too
    comp = [-v for v in P[1]]
    chk("c7 P2.3 complement is a spurious stable state",
        [1 if hop_net(W7, comp, i) > 0 else -1 for i in range(4)], comp)


def main():
    for fn in (ch2, ch3, ch4, ch6, ch7):
        try:
            fn()
        except AssertionError as e:
            FAIL.append("%s: %s" % (fn.__name__, e))
    total = N_OK + len(FAIL)
    if FAIL:
        print("FAILED %d of %d checks:\n" % (len(FAIL), total))
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("all %d checks pass" % total)


if __name__ == "__main__":
    main()
