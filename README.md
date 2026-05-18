# invest-4-future

A markdown-native investment brain. The model is the CPU, this repo is the
disk: a local AI agent boots into it each run, reads only the files it needs,
and writes back artifacts. No DB, no server — just files and git.

## What this is

A weekly Moonshots-podcast → testable hypotheses → portfolio pipeline,
implemented as plain markdown files. Hand-editable. Git-versioned. No DB.

## Layout

```
brain/            durable identity, mandate, framework — rarely changes
episodes/         raw input layer, one file per podcast episode
hypotheses/       living documents, status mutates over time
recommendations/  one file per ticker, P/L tracked
portfolio/        watchlist (shared); holdings, trades, prices, board (git-ignored)
prompts/          cognitive cores, one file per agent role
tools/            deterministic CLI — validate, index, board, review, scorecard
```

Read `AGENTS.md` for the operating manual. Read `brain/playbook.md` for
the Diamandis × Steinhardt 5-step framework. Read
`docs/agent-integration.md` to point a local agent at this repo.

## Tooling

`tools/i4f.py` is a dependency-free CLI (Python 3.8+, stdlib only) that
makes indices and IDs a pure function of the artifact files — so an agent
never invents an index row or a duplicate ID:

```
python3 tools/i4f.py validate    # check every artifact's front-matter
python3 tools/i4f.py index       # rebuild the _index.md files
python3 tools/i4f.py status      # snapshot of live state (--json for agents)
python3 tools/i4f.py new ...     # scaffold an episode/hypothesis/recommendation
python3 tools/i4f.py review      # list hypotheses/positions due for review
python3 tools/i4f.py scorecard   # rebuild the calibration track record
python3 tools/i4f.py board       # rebuild the buy/sell/performance board
python3 tools/i4f.py journal "." # append a message to the portfolio journal
```

## Weekly flow

1. Drop transcript / summary into `episodes/MS-YYYY-MM-DD.md`.
2. Run the agent chain (prompts/01 → 05).
3. Review diffs: `git diff hypotheses/ recommendations/`.
4. Hand-edit verdicts, conviction, status as needed.
5. Commit. Roll forward.

## Self-improvement loop

The weekly run generates ideas; the review cycle scores them. When a
hypothesis's horizon elapses, `i4f review` surfaces it,
`prompts/06-review.md` assesses the real-world outcome and closes the file,
and `i4f scorecard` rebuilds `brain/scorecard.md` — a running calibration
record: verdict accuracy, the rejected-pile audit (claims you passed on
that came true anyway), conviction calibration, estimated-vs-realized
asymmetry. Recurring errors there feed proposed edits to the playbook. The
process corrects itself on evidence, not memory. See `AGENTS.md` →
"Review cycle".

## Decision loop

Recommendations only matter if they turn into action. Refresh
`portfolio/prices.md`, then `i4f board` rebuilds `portfolio/action-board.md`
— buy signals (each watched ticker's price against its entry zone), sell
signals (positions whose thesis was falsified), and per-position P/L. It is
a decision surface, not an order. Log every fill and observation with
`i4f journal "..."` — `portfolio/journal.md` is the channel back to the
model, and the weekly run and review cycle both read it. See `AGENTS.md` →
"Decision loop".

## Why markdown, not Sheets

Sheets is a great dashboard but a poor database for reasoning artifacts.
A hypothesis is not a row — it has a claim, a mechanism, falsification
triggers, and an update log. That belongs in a file. A view layer can
render `portfolio/positions.md` into Sheets when you want GOOGLEFINANCE.
