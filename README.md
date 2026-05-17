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
portfolio/        canonical state — positions, transactions, watchlist
prompts/          cognitive cores, one file per agent role
tools/            deterministic CLI — validate, index, status, scaffold
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
```

## Weekly flow

1. Drop transcript / summary into `episodes/MS-YYYY-MM-DD.md`.
2. Run the agent chain (prompts/01 → 05).
3. Review diffs: `git diff hypotheses/ recommendations/`.
4. Hand-edit verdicts, conviction, status as needed.
5. Commit. Roll forward.

## Why markdown, not Sheets

Sheets is a great dashboard but a poor database for reasoning artifacts.
A hypothesis is not a row — it has a claim, a mechanism, falsification
triggers, and an update log. That belongs in a file. A view layer can
render `portfolio/positions.md` into Sheets when you want GOOGLEFINANCE.
