# invest-4-future

A markdown-native investment brain. Inspired by Karpathy's "LLM OS" framing:
the LLM is the CPU, this repo is the disk, the agent boots into it each run.

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
```

Read `AGENTS.md` for the operating manual. Read `brain/playbook.md` for
the Diamandis × Steinhardt 5-step framework.

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
