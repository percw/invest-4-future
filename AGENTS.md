# AGENTS.md — operating manual for any LLM agent working in this repo

## Boot sequence

When you start a session in this repo, read these in order:

1. `brain/identity.md` — who the user is, mandate, edge
2. `brain/mandate.md` — hard rules (ASK, sizing, asymmetry)
3. `brain/playbook.md` — the 5-step framework
4. `brain/world-model.md` — current macro/sector view
5. `brain/scorecard.md` — calibration track record: what the process gets right/wrong
6. `hypotheses/_index.md` — what's live
7. `portfolio/journal.md` — recent messages from the user (newest last)

Only load the slice you need. Don't dump the whole repo into context.
For a one-shot snapshot before loading individual files, run
`python3 tools/i4f.py status` (add `--json` for machine-readable output).

## File ownership

| Path | Who writes |
|---|---|
| `brain/identity.md`, `mandate.md`, `playbook.md` | User only. Agents read. |
| `brain/world-model.md`, `lessons.md` | Agent proposes via PR-style diff; user merges. |
| `brain/scorecard.md` | Agent rebuilds via `i4f scorecard`. Don't hand-edit. |
| `episodes/MS-*.md` | User pastes raw input; agent reads. |
| `hypotheses/*.md` | Agent creates. User edits verdict/conviction freely. |
| `recommendations/*.md` | Agent creates. Status field user-controlled. |
| `portfolio/positions.md`, `transactions.md` | User-controlled. Agent reads, may suggest. **Git-ignored — local/private.** |
| `portfolio/watchlist.md` | Agent appends. User prunes. |
| `portfolio/prices.md` | Agent or user refreshes — a price snapshot, overwritten freely. **Git-ignored — local/private.** |
| `portfolio/journal.md` | User appends via `i4f journal`. Agent reads, never edits. **Git-ignored — local/private.** |
| `portfolio/action-board.md` | Agent rebuilds via `i4f board`. Don't hand-edit. **Git-ignored — local/private.** |
| `prompts/*.md` | User curates. |

Files marked **local/private** are git-ignored: they hold real holdings,
trade prices, and P&L, and never leave your machine. The CLI tolerates
their absence — in a fresh clone the board is simply empty until they are
populated locally.

## Conventions

- **Front-matter**: every artifact starts with YAML. See templates.
- **IDs**: `MS-YYYY-MM-DD` (episode), `MS-YYYY-MM-DD-H{n}` (hypothesis).
- **Tickers**: uppercase, paired with exchange code (NASDAQ, NYSE, OSL, AMS, STO, LON, EPA, FRA).
- **Currency**: numbers in local currency unless field is suffixed `_NOK`.
- **Status enums**: defined in each template. Don't invent new values.
- **Update log**: append-only. Don't rewrite history; add a dated line.

## Cognitive cores (which model for which step)

| Step | Prompt file | Suggested model | Why |
|---|---|---|---|
| Extract hypotheses | `prompts/01-extract.md` | Sonnet 4.6 | High recall over long transcripts |
| Variant perception | `prompts/02-variant.md` | Opus 4.7 + WebSearch | Contrarian reasoning, fresh data |
| Investability screen | `prompts/03-investability.md` | Sonnet 4.6 | Precise rule application |
| Asymmetry math | `prompts/04-asymmetry.md` | Opus 4.7 | Conservative numerical reasoning |
| Synthesize | `prompts/05-synthesize.md` | Sonnet 4.6 | Structured emit |
| Review & self-critique | `prompts/06-review.md` | Opus 4.7 + WebSearch | Honest outcome assessment, fresh catalyst data |

These are defaults. Override per task. Steps 01-05 run weekly; step 06 runs
on the review cadence (see below).

## Tooling — `tools/i4f.py`

A dependency-free CLI (Python 3.8+, stdlib only). Prefer it over hand-editing
indices or guessing IDs — its output is deterministic.

| Command | Use it for |
|---|---|
| `i4f validate` | Check every artifact's front-matter: required fields, enum values, ID format, broken cross-references, stale indices. Run before every commit. |
| `i4f index` | Rebuild `hypotheses/_index.md` and `recommendations/_index.md` from the artifact files. Never hand-edit an `_index.md`. |
| `i4f status` | Snapshot of live state (counts, active hypotheses, watchlist). `--json` for programmatic use. |
| `i4f new episode\|hypothesis\|recommendation` | Scaffold a new artifact from its template with IDs and dates filled in. Hypothesis numbers (`-H{n}`) auto-increment. |
| `i4f review` | List hypotheses and positions due for review — horizon elapsed, not reviewed in 90 days, or a rejected hypothesis past its horizon awaiting a reject-audit. The entry point of the review cycle. |
| `i4f scorecard` | Rebuild `brain/scorecard.md` — the calibration track record (verdict accuracy, rejected-pile audit, conviction calibration, estimated-vs-realized). |
| `i4f board` | Rebuild `portfolio/action-board.md` — buy signals (price vs entry zone), sell/review signals (falsified theses), per-position P/L. Refresh `portfolio/prices.md` first. |
| `i4f journal "..."` | Append a dated message to `portfolio/journal.md` — the user's feedback channel. |

Invoke as `python3 tools/i4f.py <command>` from anywhere in the repo.
`validate` exits non-zero on errors; wire it into your pre-commit step.

## Anti-patterns

- Don't write a 5000-token prompt. Use the brain/ files as durable spec; keep prompts terse.
- Don't dump tool output verbatim into hypothesis files. Distill.
- Don't fill the recommendation quota. If <3 ideas survive screening, output fewer.
- Don't use authority ("Diamandis said") as a reason. Mechanism + variant + investability or reject.
- Don't edit `brain/identity.md` or `mandate.md` without explicit user instruction.

## Definition of done for a weekly run

- [ ] One new file in `episodes/`
- [ ] N new files in `hypotheses/` (rejected ones written too, with `verdict: hype` or `priced-in`)
- [ ] M new files in `recommendations/` where M ≤ N
- [ ] `portfolio/watchlist.md` appended (NEW recs)
- [ ] `python3 tools/i4f.py index` run (rebuilds both `_index.md` files)
- [ ] `python3 tools/i4f.py validate` passes with no errors
- [ ] One commit. Conventional message: `weekly: MS-YYYY-MM-DD — {short title}`

## Decision loop — buy, sell, and feedback

The pipeline produces recommendations; the decision loop turns them into
actions and carries the user's feedback back. Run it whenever a read on
what to do is wanted:

1. Refresh `portfolio/prices.md` — the local agent fetches current quotes
   for every held and watched ticker, or the user edits the table by hand.
2. `python3 tools/i4f.py board` rebuilds `portfolio/action-board.md`:
   - **Buy signals** — each NEW/WATCHING recommendation, its price placed
     against its entry zone (in zone / below / above / wait).
   - **Sell / review signals** — held positions whose linked hypothesis
     was falsified, expired, or rejected.
   - **Portfolio performance** — per-position value and P/L.
   The board is a decision surface, not an order. The user decides.
3. Log every fill, decision, or observation with
   `python3 tools/i4f.py journal "bought TSM 8 @ 272"`.

`portfolio/journal.md` is the user's channel to the model. The weekly run
and the review cycle both read recent journal entries before acting — it
is how out-of-band context (a fill, a doubt, a market event) reaches the
process. Append-only; never rewrite past entries.

## Review cycle — the self-improvement loop

The weekly run is open-loop: it generates hypotheses but never learns
whether they were right. The review cycle closes that loop. Run it on a
periodic cadence (monthly, or whenever `i4f review` surfaces items):

1. `python3 tools/i4f.py review` — list hypotheses and positions due
   (horizon elapsed, or not reviewed in 90 days).
2. For each, assess the outcome — use WebSearch for catalysts and
   falsification triggers. Set `status` to CONFIRMED / FALSIFIED /
   EXPIRED, fill the `## Review` section, set `reviewed:` to today.
   For rejected hypotheses past their horizon, audit whether the claim
   came true anyway and set `reject_outcome` to `vindicated` or `missed`
   — half the alpha is in what you didn't buy.
3. `python3 tools/i4f.py scorecard` — rebuild `brain/scorecard.md`
   (verdict accuracy, conviction calibration, estimated-vs-realized).
4. Append notable hits and misses to `brain/lessons.md`.
5. Where the scorecard shows a recurring error, propose a diff to
   `playbook.md` or `world-model.md`. Propose — never apply, and never
   touch `mandate.md` or `identity.md`. The user merges.

`prompts/06-review.md` is the cognitive core for this cycle. A falsified
hypothesis is a feature: the scorecard only improves if outcomes are
scored honestly.
