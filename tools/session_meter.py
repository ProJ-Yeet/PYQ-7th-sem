# -*- coding: utf-8 -*-
r"""Measure, after every session, whether delegating to a cheaper model paid off.

    python tools/session_meter.py                 # the session that just ended
    python tools/session_meter.py --all           # every transcript, the baseline
    python tools/session_meter.py --session 2998  # an id prefix
    python tools/session_meter.py --ledger        # also append to the ledger
    python tools/session_meter.py --report        # the cross-session verdict

What it reads: the Claude Code transcripts under
%USERPROFILE%\.claude\projects\D--College-PYQ\*.jsonl. Every assistant turn
carries its model name and its usage block, and a subagent's turns carry
isSidechain, so a session's spend splits by model without any bookkeeping of
our own.

Three numbers per delegation, because they answer different questions:

  priced      cost in Opus-token-equivalents. Answers "was it cheaper?"
  displaced   tool-result volume the subagent absorbed that never entered the
              main window. Answers "did it keep the main thread small?" In this
              repo that is the number that matters: cache reads are ~95 % of all
              raw input tokens, so a token kept out of the window is paid once,
              while a token let in is re-read on every later turn.
  repairs     main-thread Edit/Write calls, after the subagent returned, to
              files the subagent had written. Answers "was the quality
              acceptable?" A delegation that needs the main model to rewrite its
              output did not save anything.

The priced comparison rests on one assumption, stated so it can be argued with:
that Opus doing the same task would have consumed a comparable number of tokens.
For the mechanical lanes in route.py that is close to true. For authoring it is
not, which is why authoring is not delegated.
"""
import io, json, os, re, sys, glob, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PROJ = os.path.join(os.path.expanduser("~"), ".claude", "projects", "D--College-PYQ")
LEDGER_TSV = os.path.join(HERE, "agent-ledger.tsv")
LEDGER_MD = os.path.join(REPO, "AGENTS-LEDGER.md")

sys.path.insert(0, HERE)
try:
    from route import RATE
except Exception:
    RATE = {"opus": 1.00, "sonnet": 0.20, "haiku": 0.04, "script": 0.0}

# price multipliers relative to an input token
W_IN, W_CC, W_CR, W_OUT = 1.0, 1.25, 0.10, 5.0


def units(u):
    return (u.get("input_tokens", 0) * W_IN
            + u.get("cache_creation_input_tokens", 0) * W_CC
            + u.get("cache_read_input_tokens", 0) * W_CR
            + u.get("output_tokens", 0) * W_OUT)


def short(m):
    if not m:
        return "unknown"
    m = m.lower()
    for k in ("opus", "sonnet", "haiku", "fable"):
        if k in m:
            return k
    return m


def blocks(msg):
    c = msg.get("content") if isinstance(msg, dict) else None
    return c if isinstance(c, list) else []


def result_chars(blk):
    c = blk.get("content")
    n = imgs = 0
    if isinstance(c, str):
        n = len(c)
    elif isinstance(c, list):
        for x in c:
            if isinstance(x, dict):
                if x.get("type") == "text":
                    n += len(x.get("text") or "")
                elif x.get("type") == "image":
                    imgs += 1
    return n, imgs


def link_key(d):
    """A sidechain entry's pointer back to the Task call that spawned it. The
    field name has moved between Claude Code versions, so try all of them."""
    for k in ("parentToolUseID", "parentToolUseId", "toolUseID", "toolUseId",
              "agentId", "parent_tool_use_id"):
        v = d.get(k)
        if v:
            return v
    return None


AGENT_RE = re.compile(r"[.]claude[/\\]agents[/\\]([A-Za-z0-9_-]+)[.]md")


def agent_label(inp):
    """What lane did this delegation claim?

    Normally the subagent_type names it. But a named agent in .claude/agents/ only
    registers at session start, so a session that just created one has to spawn a
    generic agent and point it at the brief instead. When the prompt names a brief,
    that brief is the lane -- otherwise the ledger would file real pyq-extract runs
    under "claude" and the per-lane verdict would never accumulate."""
    st = inp.get("subagent_type")
    m = AGENT_RE.search(inp.get("prompt") or "")
    if m and (not st or st in ("claude", "general-purpose", None)):
        return m.group(1)
    return st or "claude"


AGENTID_RE = re.compile(r"agentId:{0,1}[ ]+([0-9a-zA-Z]{6,})")
NOTIF_RE = re.compile(r"<task-id>([^<]+)</task-id>.*?<status>([^<]+)</status>",
                      re.S)
NOTIF_BLOCK_RE = re.compile(r"<task-notification>(.*?)</task-notification>", re.S)
TOK_RE = re.compile(r"<subagent_tokens>\s*(\d+)\s*</subagent_tokens>")
USES_RE = re.compile(r"<tool_uses>\s*(\d+)\s*</tool_uses>")
DUR_RE = re.compile(r"<duration_ms>\s*(\d+)\s*</duration_ms>")
RESULT_RE = re.compile(r"<result>(.*?)</result>", re.S)
TID_RE = re.compile(r"<task-id>([^<]+)</task-id>")
STATUS_RE = re.compile(r"<status>([^<]+)</status>")

FAIL_MARKS = (
    "agent type", "not found", "terminated early", "rate_limit",
    "You've hit your", "hit your session limit", "InputValidationError",
)


def result_text(blk):
    """Flatten a tool_result's text so it can be pattern-matched."""
    c = blk.get("content")
    if isinstance(c, str):
        return c
    out = []
    if isinstance(c, list):
        for x in c:
            if isinstance(x, dict) and x.get("type") == "text":
                out.append(x.get("text") or "")
    return "NEWLINE".join(out).replace("NEWLINE", chr(10))


def fail_reason(txt, blk):
    """Did this delegation never actually run? A spawn that was refused or killed
    must not be scored: its prompt cost is real but it did no work, and calling that
    a saving of minus-N units would libel the lane."""
    if blk.get("is_error"):
        return "tool error"
    low = txt.lower()
    for mark in FAIL_MARKS:
        if mark.lower() in low:
            return mark
    return None


def task_dirs(session_id):
    """Where a backgrounded agent's own transcript lands."""
    base = os.path.join(os.environ.get("TEMP") or os.environ.get("TMP") or "",
                        "claude", "D--College-PYQ", session_id, "tasks")
    alt = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp",
                       "claude", "D--College-PYQ", session_id, "tasks")
    return [d for d in (base, alt) if d and os.path.isdir(d)]


def tally_task_file(path):
    """Usage and absorbed tool output from one background-agent transcript. Read by
    a script, never into a model's context: that is the whole point of the lane."""
    got = {"units": 0.0, "out": 0, "turns": 0, "absorbed": 0, "absorbed_imgs": 0,
           "model": None}
    try:
        fh = io.open(path, encoding="utf-8", errors="replace")
    except Exception:
        return got
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get("message")
            if not isinstance(msg, dict):
                continue
            if d.get("type") == "assistant":
                u = msg.get("usage") or {}
                got["units"] += units(u)
                got["out"] += u.get("output_tokens", 0) or 0
                got["turns"] += 1
                got["model"] = got["model"] or short(msg.get("model"))
            elif d.get("type") == "user":
                for b in blocks(msg):
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        n, im = result_chars(b)
                        got["absorbed"] += n
                        got["absorbed_imgs"] += im
    return got


class Session(object):
    def __init__(self, path):
        self.path = path
        self.sid = os.path.basename(path)[:-6]
        self.start = self.end = None
        self.spend = collections.defaultdict(lambda: collections.Counter())
        self.spawns = []
        self.by_id = {}
        self.main_file_writes = []      # (ts, path)
        self.notif = {}                 # task-id -> what it reported
        self.parse()

    def parse(self):
        pending = {}                    # tool_use_id -> (name, sidechain, spawn)
        cur_spawn = [None]
        with io.open(self.path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if "task-notification" in line:
                    self.scan_text(line)
                ts = d.get("timestamp")
                if ts:
                    if self.start is None or ts < self.start:
                        self.start = ts
                    if self.end is None or ts > self.end:
                        self.end = ts
                side = bool(d.get("isSidechain"))
                msg = d.get("message")
                if not isinstance(msg, dict):
                    continue
                if d.get("type") == "user":
                    self.scan_notifications(msg)

                spawn = None
                if side:
                    k = link_key(d)
                    spawn = self.by_id.get(k) or cur_spawn[0]

                if d.get("type") == "assistant":
                    mdl = short(msg.get("model"))
                    key = (mdl, side)
                    u = msg.get("usage") or {}
                    c = self.spend[key]
                    for f in ("input_tokens", "cache_creation_input_tokens",
                              "cache_read_input_tokens", "output_tokens"):
                        c[f] += u.get(f, 0) or 0
                    c["units"] += units(u)
                    c["turns"] += 1
                    if side and spawn is not None:
                        spawn["units"] += units(u)
                        spawn["out"] += u.get("output_tokens", 0) or 0
                        spawn["turns"] += 1
                        spawn["model"] = spawn["model"] or mdl
                        spawn["seen_model"] = mdl

                    for b in blocks(msg):
                        if not isinstance(b, dict) or b.get("type") != "tool_use":
                            continue
                        nm = b.get("name") or "?"
                        inp = b.get("input") or {}
                        pending[b.get("id")] = (nm, side, spawn)
                        if nm in ("Task", "Agent") and not side:
                            sp = {
                                "id": b.get("id"), "ts": ts,
                                "agent": agent_label(inp),
                                "model": short(inp.get("model")) if inp.get("model") else None,
                                "seen_model": None,
                                "desc": inp.get("description") or "",
                                "prompt_chars": len(inp.get("prompt") or ""),
                                "units": 0.0, "out": 0, "turns": 0,
                                "absorbed": 0, "absorbed_imgs": 0,
                                "report_chars": 0, "files": set(), "repairs": 0,
                                "repair_files": [], "agent_id": None,
                                "failed": None,
                            }
                            self.spawns.append(sp)
                            self.by_id[b.get("id")] = sp
                            cur_spawn[0] = sp
                        if not side and nm in ("Edit", "Write", "NotebookEdit"):
                            self.main_file_writes.append(
                                (ts, (inp.get("file_path") or "").replace("\\", "/")))
                        if side and spawn is not None and nm in ("Edit", "Write", "NotebookEdit"):
                            spawn["files"].add((inp.get("file_path") or "").replace("\\", "/"))

                elif d.get("type") == "user":
                    for b in blocks(msg):
                        if not isinstance(b, dict) or b.get("type") != "tool_result":
                            continue
                        nm, was_side, sp = pending.get(b.get("tool_use_id"),
                                                       ("?", False, None))
                        n, im = result_chars(b)
                        if nm in ("Task", "Agent"):
                            tgt = self.by_id.get(b.get("tool_use_id"))
                            if tgt is not None:
                                tgt["report_chars"] = n
                                tgt["done_ts"] = ts
                                txt = result_text(b)
                                m = AGENTID_RE.search(txt)
                                if m:
                                    tgt["agent_id"] = m.group(1)
                                tgt["failed"] = fail_reason(txt, b)
                                cur_spawn[0] = None
                        elif was_side and sp is not None:
                            sp["absorbed"] += n
                            sp["absorbed_imgs"] += im

        # a backgrounded agent's turns are in its own file, not this transcript
        dirs = task_dirs(self.sid)
        for sp in self.spawns:
            if sp["turns"] or not sp.get("agent_id"):
                continue
            for d in dirs:
                f = os.path.join(d, sp["agent_id"] + ".output")
                if not os.path.exists(f):
                    continue
                got = tally_task_file(f)
                sp["units"] += got["units"]
                sp["out"] += got["out"]
                sp["turns"] += got["turns"]
                sp["absorbed"] += got["absorbed"]
                sp["absorbed_imgs"] += got["absorbed_imgs"]
                sp["seen_model"] = sp["seen_model"] or got["model"]
                sp["async"] = True
                break

        # fold in what each background agent reported about itself
        for sp in self.spawns:
            rec = self.notif.get(sp.get("agent_id") or "")
            if not rec:
                continue
            if rec.get("reason") and not sp["turns"]:
                sp["failed"] = sp["failed"] or rec["reason"]
            if rec.get("tokens"):
                # one total, no in/out/cache split: priced as input-equivalent, which
                # understates the delegate's cost and so understates the saving
                sp["units"] = max(sp["units"], float(rec["tokens"]))
                sp["notified"] = True
            if rec.get("tool_uses"):
                sp["turns"] = max(sp["turns"], rec["tool_uses"])
            if rec.get("result_chars"):
                sp["report_chars"] = rec["result_chars"]
            sp["duration_ms"] = rec.get("duration_ms")

        # quality proxy: main-thread rewrites of subagent files, after it returned
        for sp in self.spawns:
            done = sp.get("done_ts") or sp["ts"]
            for ts, path in self.main_file_writes:
                if ts and ts > done and path in sp["files"]:
                    sp["repairs"] += 1
                    sp["repair_files"].append(os.path.basename(path))

    def scan_notifications(self, msg):
        """A background agent reports itself through a task-notification, and that is
        the only place its token total appears. Later notifications for the same
        task-id win, so a resumed agent is scored on its final state."""
        c = msg.get("content")
        chunks = []
        if isinstance(c, str):
            chunks = [c]
        elif isinstance(c, list):
            for b in c:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text":
                    chunks.append(b.get("text") or "")
                elif b.get("type") == "tool_result":
                    # a notification that fired while the main thread was mid-call is
                    # appended to that call's result, not sent as its own message
                    chunks.append(result_text(b))
        for t in chunks:
            self.scan_text(t)

    def scan_text(self, t):
        if "task-notification" not in t:
            return
        for block in self.notif_blocks(t):
            self.scan_block(block)

    def notif_blocks(self, t):
        """One notification per block where the closing tag survives; otherwise treat
        each <task-id> as starting a block, so a truncated tail still scores."""
        found = NOTIF_BLOCK_RE.findall(t)
        if found:
            return found
        parts = t.split("<task-id>")
        return ["<task-id>" + x for x in parts[1:]] or [t]

    def scan_block(self, block):
        if True:
                mt = TID_RE.search(block)
                if not mt:
                    return
                tid = mt.group(1).strip()
                ms = STATUS_RE.search(block)
                status = (ms.group(1).strip().lower() if ms else "?")
                rec = self.notif.setdefault(tid, {})
                rec["status"] = status
                mk = TOK_RE.search(block)
                if mk:
                    rec["tokens"] = int(mk.group(1))
                mu = USES_RE.search(block)
                if mu:
                    rec["tool_uses"] = int(mu.group(1))
                md = DUR_RE.search(block)
                if md:
                    rec["duration_ms"] = int(md.group(1))
                mr = RESULT_RE.search(block)
                if mr:
                    rec["result_chars"] = len(mr.group(1))
                if status != "completed":
                    low = block.lower()
                    rec["reason"] = ("rate limit"
                                     if "rate_limit" in low or "usage limit" in low
                                     else status)

    # ---- derived numbers

    def main_units(self):
        return sum(c["units"] for (m, s), c in self.spend.items() if not s)

    def side_units(self):
        return sum(c["units"] for (m, s), c in self.spend.items() if s)

    def main_turns_after(self, ts):
        return 0  # filled by report(); kept for clarity of intent

    def score(self, sp):
        """priced saving, and context displaced, for one delegation."""
        mdl = sp["seen_model"] or sp["model"] or "sonnet"
        rate = RATE.get(mdl, 0.2)
        spent = sp["units"] * rate
        counterfactual = sp["units"] * RATE["opus"]
        # Opus overhead: the prompt it wrote, and the report it read back
        overhead = (sp["prompt_chars"] / 3.7) * W_OUT + (sp["report_chars"] / 3.7) * W_IN
        net = counterfactual - spent - overhead
        if sp.get("notified"):
            # everything the subagent consumed would otherwise have flowed through the
            # main window: its prompt, its tool results, its own reasoning. What did
            # enter the main window is the report.
            displaced = max(sp["units"] - sp["report_chars"] / 3.7, 0)
        else:
            displaced = max(sp["absorbed"] - sp["report_chars"], 0) / 3.7
            displaced += sp["absorbed_imgs"] * 2500
        return spent, counterfactual, overhead, net, displaced

    def verdict(self, sp):
        if sp.get("failed") and not sp["turns"]:
            return "FAILED"
        if not sp["turns"]:
            return "UNMEASURED"
        spent, cf, oh, net, disp = self.score(sp)
        if sp["repairs"] >= 3:
            return "REJECT"
        if sp["repairs"] > 0:
            return "REPAIRED"
        if net <= 0:
            return "NO-SAVING"
        return "ACCEPTED"

    def report(self, verbose=True):
        print("")
        print("=" * 78)
        print("SESSION " + self.sid[:8] + "   " + str(self.start)[:16]
              + " -> " + str(self.end)[:16])
        print("=" * 78)
        print("%-9s %-10s %6s %10s %12s %12s"
              % ("model", "thread", "turns", "out", "raw in", "units"))
        for (mdl, side), c in sorted(self.spend.items(), key=lambda kv: -kv[1]["units"]):
            raw = (c["input_tokens"] + c["cache_creation_input_tokens"]
                   + c["cache_read_input_tokens"])
            print("%-9s %-10s %6d %10d %12d %12d"
                  % (mdl, "sidechain" if side else "main", c["turns"],
                     c["output_tokens"], raw, c["units"]))
        mu, su = self.main_units(), self.side_units()
        print("-" * 78)
        print("main %d units, sidechain %d units" % (mu, su))

        if not self.spawns:
            print("")
            print("NO DELEGATIONS. Everything ran on the main model.")
            print("Check `python tools/route.py` for the lanes that were available.")
            return

        print("")
        print("DELEGATIONS (%d)" % len(self.spawns))
        for sp in self.spawns:
            spent, cf, oh, net, disp = self.score(sp)
            print("")
            print("  %-14s %-7s %s" % (sp["agent"], sp["seen_model"] or sp["model"] or "?",
                                       sp["desc"][:52]))
            if sp.get("notified"):
                print("     tool uses=%d  tokens=%d (self-reported)  report=%d chars%s"
                      % (sp["turns"], int(sp["units"]), sp["report_chars"],
                         ("  %.0fs" % (sp["duration_ms"] / 1000.0))
                         if sp.get("duration_ms") else ""))
            else:
                print("     turns=%d  absorbed=%dk chars +%d images  report=%d chars"
                      % (sp["turns"], sp["absorbed"] // 1000, sp["absorbed_imgs"],
                         sp["report_chars"]))
            print("     priced: spent %d, Opus would be %d, overhead %d  ->  net %+d units"
                  % (spent, cf, oh, net))
            print("     context displaced from the main window: %d tokens" % disp)
            if sp["files"]:
                print("     wrote: " + ", ".join(sorted(
                    os.path.basename(f) for f in sp["files"])[:6]))
            print("     repairs after it returned: %d %s"
                  % (sp["repairs"], sp["repair_files"][:4] or ""))
            print("     VERDICT " + self.verdict(sp)
                  + ((" -- " + sp["failed"]) if sp.get("failed") else ""))

    def ledger_rows(self):
        for sp in self.spawns:
            spent, cf, oh, net, disp = self.score(sp)
            v = self.verdict(sp)
            if v in ("FAILED", "UNMEASURED"):
                spent = cf = net = disp = 0
            yield [
                str(sp["ts"] or self.start)[:19], self.sid[:8], sp["agent"],
                sp["seen_model"] or sp["model"] or "?",
                sp["desc"][:60].replace("\t", " "),
                sp["turns"], int(sp["units"]), int(spent), int(cf), int(oh),
                int(net), int(disp), sp["repairs"], v,
                sp.get("failed") or "",
            ]


HEAD = ["when", "session", "agent", "model", "task", "turns", "units",
        "priced", "opus_equiv", "overhead", "net_saved", "displaced",
        "repairs", "verdict", "note"]


PROVISIONAL = ("UNMEASURED", "FAILED", "")


def append_ledger(sessions):
    """Add new delegations, and upgrade rows that were logged too early.

    The meter can run while an agent is still working: the row lands as
    UNMEASURED, the agent finishes, and a plain dedup would then discard the
    corrected row and leave the lane unmeasured for ever. So a row whose stored
    verdict is provisional is REPLACED when a real one turns up, keeping any
    note written by hand."""
    new = []
    for s in sessions:
        new.extend(s.ledger_rows())
    if not new:
        print("nothing to log: no delegations in this session")
        return

    rows, order = {}, []
    if os.path.exists(LEDGER_TSV):
        with io.open(LEDGER_TSV, encoding="utf-8") as fh:
            lines = [l.rstrip("\n").split("\t") for l in fh if l.strip()]
        for r in lines[1:]:
            while len(r) < len(HEAD):
                r.append("")
            k = (r[0], r[1], r[4])
            if k not in rows:
                order.append(k)
            rows[k] = r

    added = upgraded = 0
    iv, inote = HEAD.index("verdict"), HEAD.index("note")
    for r in new:
        r = [str(x) for x in r]
        k = (r[0], r[1], r[4])
        if k not in rows:
            rows[k] = r
            order.append(k)
            added += 1
            continue
        old_row = rows[k]
        if old_row[iv] in PROVISIONAL and r[iv] not in PROVISIONAL:
            r[inote] = old_row[inote] or r[inote]   # never lose a hand note
            rows[k] = r
            upgraded += 1

    with io.open(LEDGER_TSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(HEAD) + "\n")
        for k in order:
            fh.write("\t".join(rows[k]) + "\n")
    if not added and not upgraded:
        print("ledger already current")
        return
    print("ledger: +%d row(s), %d upgraded -> %s"
          % (added, upgraded, LEDGER_TSV))
    write_md()


def read_ledger():
    if not os.path.exists(LEDGER_TSV):
        return []
    out = []
    with io.open(LEDGER_TSV, encoding="utf-8") as fh:
        lines = [l.rstrip("\n").split("\t") for l in fh if l.strip()]
    if not lines:
        return []
    head = lines[0]
    for p in lines[1:]:
        out.append(dict(zip(head, p)))
    return out


def verdict_table():
    rows = read_ledger()
    per = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        k = (r.get("agent"), r.get("model"))
        c = per[k]
        c["n"] += 1
        for f in ("net_saved", "displaced", "repairs"):
            try:
                c[f] += int(r.get(f) or 0)
            except ValueError:
                pass
        c[r.get("verdict", "?")] += 1
    return per


def report_across():
    per = verdict_table()
    if not per:
        print("ledger is empty. Run a delegation, then --ledger.")
        return
    print("%-14s %-7s %4s %12s %12s %8s  %s"
          % ("agent", "model", "runs", "net saved", "displaced", "repairs", "calls"))
    print("-" * 86)
    for (agent, mdl), c in sorted(per.items(), key=lambda kv: -kv[1]["n"]):
        calls = " ".join("%s=%d" % (v, c[v]) for v in
                         ("ACCEPTED", "REPAIRED", "NO-SAVING", "REJECT",
                          "FAILED", "UNMEASURED") if c[v])
        print("%-14s %-7s %4d %12d %12d %8d  %s"
              % (agent, mdl, c["n"], c["net_saved"], c["displaced"], c["repairs"], calls))
    print("")
    print("RECOMMENDATION")
    for (agent, mdl), c in sorted(per.items()):
        n = c["n"] - c["FAILED"] - c["UNMEASURED"]
        bad = c["REJECT"] + c["REPAIRED"]
        if n <= 0:
            print("  %-14s %-7s no run completed yet (%d failed, %d unmeasured)"
                  % (agent, mdl, c["FAILED"], c["UNMEASURED"]))
            continue
        if n < 3:
            verdict = "keep sampling, %d run(s) is not evidence" % n
        elif c["REJECT"] or bad * 2 > n:
            verdict = "STOP routing here; repair rate %d/%d" % (bad, n)
        elif c["net_saved"] <= 0:
            verdict = "quality fine but no saving; fold back into the main thread"
        else:
            verdict = "keep, and widen the lane"
        print("  %-14s %-7s %s" % (agent, mdl, verdict))


def write_md():
    rows = read_ledger()
    per = verdict_table()
    tot_net = sum(int(r.get("net_saved") or 0) for r in rows)
    tot_disp = sum(int(r.get("displaced") or 0) for r in rows)
    L = []
    L.append("# Agent ledger")
    L.append("")
    L.append("Written by `tools/session_meter.py --ledger` after each session. One row")
    L.append("per delegation, in `tools/agent-ledger.tsv`. Never edit by hand except the")
    L.append("`note` column.")
    L.append("")
    L.append("**Totals:** %d delegations, %d units saved, %d tokens kept out of the "
             "main window." % (len(rows), tot_net, tot_disp))
    L.append("")
    L.append("| agent | model | runs | net saved | displaced | repairs | outcome |")
    L.append("|---|---|---|---|---|---|---|")
    for (agent, mdl), c in sorted(per.items(), key=lambda kv: -kv[1]["n"]):
        calls = ", ".join("%s %d" % (v.lower(), c[v]) for v in
                         ("ACCEPTED", "REPAIRED", "NO-SAVING", "REJECT",
                          "FAILED", "UNMEASURED") if c[v])
        L.append("| %s | %s | %d | %d | %d | %d | %s |"
                 % (agent, mdl, c["n"], c["net_saved"], c["displaced"],
                    c["repairs"], calls))
    L.append("")
    L.append("Columns: **net saved** is Opus-token-equivalents, delegate spend and the")
    L.append("main thread's prompt-plus-report overhead already subtracted. **displaced**")
    L.append("is tool output the subagent absorbed that never entered the main window --")
    L.append("the number that matters most here, since cache reads are about 95 % of raw")
    L.append("input. **repairs** counts main-thread rewrites of files the subagent wrote,")
    L.append("and is the quality signal: a delegation whose output gets rewritten saved")
    L.append("nothing.")
    L.append("")
    L.append("Lanes live in `tools/route.py`. Updated " +
             datetime.datetime.now().strftime("%Y-%m-%d") + ".")
    io.open(LEDGER_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote " + LEDGER_MD)


def pick(args):
    paths = sorted(glob.glob(os.path.join(PROJ, "*.jsonl")))
    if "--all" in args:
        return paths
    for i, a in enumerate(args):
        if a == "--session" and i + 1 < len(args):
            pre = args[i + 1]
            hit = [p for p in paths if os.path.basename(p).startswith(pre)]
            if hit:
                return hit
            print("no transcript starts with " + pre)
            return []
    if not paths:
        return []
    return [max(paths, key=os.path.getmtime)]


def main():
    args = sys.argv[1:]
    if "--report" in args:
        report_across()
        return
    paths = pick(args)
    if not paths:
        print("no transcripts under " + PROJ)
        return
    sessions = [Session(p) for p in paths]
    if "--all" in args:
        g = collections.defaultdict(lambda: collections.Counter())
        nspawn = 0
        for s in sessions:
            nspawn += len(s.spawns)
            for k, c in s.spend.items():
                for f in c:
                    g[k][f] += c[f]
        print("BASELINE over %d transcripts" % len(sessions))
        tot = sum(c["units"] for c in g.values())
        for (mdl, side), c in sorted(g.items(), key=lambda kv: -kv[1]["units"]):
            print("  %-9s %-10s turns=%-6d out=%-9d units=%-12d %5.1f%%"
                  % (mdl, "sidechain" if side else "main", c["turns"],
                     c["output_tokens"], c["units"], 100.0 * c["units"] / max(tot, 1)))
        print("  delegations across all history: %d" % nspawn)
    else:
        for s in sessions:
            s.report()
    if "--ledger" in args:
        append_ledger(sessions)


if __name__ == "__main__":
    main()
