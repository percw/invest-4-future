# AGENTS.md — operating manual for any LLM agent working in this repo

## Boot sequence

When you start a session in this repo, read these in order:

1. `brain/identity.md` — who the user is, mandate, edge
2. `brain/mandate.md` — hard rules (ASK, sizing, asymmetry)
3. `brain/playbook.md` — the 5-step framework
4. `brain/world-model.md` — current macro/sector view
5. `hypotheses/_index.md` — what's live

Only load the slice you need. Don't dump the whole repo into context.
For a one-shot snapshot before loading individual files, run
`python3 tools/i4f.py status` (add `--json` for machine-readable output).

## File ownership

| Path | Who writes |
|---|---|
| `brain/identity.md`, `mandate.md`, `playbook.md` | User only. Agents read. |
| `brain/world-model.md`, `lessons.md` | Agent proposes via PR-style diff; user merges. |
| `episodes/MS-*.md` | User pastes raw input; agent reads. |
| `hypotheses/*.md` | Agent creates. User edits verdict/conviction freely. |
| `recommendations/*.md` | Agent creates. Status field user-controlled. |
| `portfolio/positions.md`, `transactions.md` | User-controlled. Agent reads, may suggest. |
| `portfolio/watchlist.md` | Agent appends. User prunes. |
| `prompts/*.md` | User curates. |

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

These are defaults. Override per task.

## Tooling — `tools/i4f.py`

A dependency-free CLI (Python 3.8+, stdlib only). Prefer it over hand-editing
indices or guessing IDs — its output is deterministic.

| Command | Use it for |
|---|---|
| `i4f validate` | Check every artifact's front-matter: required fields, enum values, ID format, broken cross-references, stale indices. Run before every commit. |
| `i4f index` | Rebuild `hypotheses/_index.md` and `recommendations/_index.md` from the artifact files. Never hand-edit an `_index.md`. |
| `i4f status` | Snapshot of live state (counts, active hypotheses, watchlist). `--json` for programmatic use. |
| `i4f new episode\|hypothesis\|recommendation` | Scaffold a new artifact from its template with IDs and dates filled in. Hypothesis numbers (`-H{n}`) auto-increment. |

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
