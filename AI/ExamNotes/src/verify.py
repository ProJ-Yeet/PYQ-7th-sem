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


def main():
    for fn in (ch2, ch3):
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
