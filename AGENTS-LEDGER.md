# Agent ledger

Written by `tools/session_meter.py --ledger` after each session. One row
per delegation, in `tools/agent-ledger.tsv`. Never edit by hand except the
`note` column.

**Totals:** 10 delegations, 337992 units saved, 438441 tokens kept out of the main window.

| agent | model | runs | net saved | displaced | repairs | outcome |
|---|---|---|---|---|---|---|
| pyq-extract | sonnet | 5 | 181245 | 245084 | 0 | accepted 3, failed 2 |
| pyq-scout | haiku | 3 | 65802 | 70693 | 0 | accepted 1, failed 2 |
| pyq-latex | sonnet | 2 | 90945 | 122664 | 0 | accepted 2 |

Columns: **net saved** is Opus-token-equivalents, delegate spend and the
main thread's prompt-plus-report overhead already subtracted. **displaced**
is tool output the subagent absorbed that never entered the main window --
the number that matters most here, since cache reads are about 95 % of raw
input. **repairs** counts main-thread rewrites of files the subagent wrote,
and is the quality signal: a delegation whose output gets rewritten saved
nothing.

Lanes live in `tools/route.py`. Updated 2026-09-14.
