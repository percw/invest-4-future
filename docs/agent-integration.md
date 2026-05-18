# Agent integration guide

How to connect a local AI agent to this repo so it can run the weekly
pipeline end-to-end.

## What "connecting" means

The repo is the agent's working memory on disk. The agent reads files,
runs `tools/i4f.py` commands, writes artifact files, and commits.
There is no server, no API, no database. The only interface is the
filesystem and a shell.

---

## Prerequisites

1. Clone the repo to a local path the agent can read and write.

   ```sh
   git clone <repo-url> ~/invest-4-future
   ```

2. Python 3.8+ must be available as `python3`. No pip install — the CLI
   is stdlib only.

3. The agent needs permission to run `python3` and `git` in the repo
   directory.

---

## The agent contract

**Read `AGENTS.md` before doing anything else.** It is the operating
manual: boot sequence, file ownership table, conventions, definition of
done. This guide does not duplicate it.

Key rules:

- Follow the boot sequence in `AGENTS.md` — load `brain/` files in order,
  then `hypotheses/_index.md`. Use `status` first for a cheap snapshot.
- Respect the file-ownership table. `brain/identity.md` and
  `brain/mandate.md` are user-owned. Agents read them; they never write
  them unless the user explicitly instructs.
- Use status enums as defined in the templates. Do not invent new values.
- Update logs are append-only. Add a dated line; never rewrite history.

---

## Deterministic tools — `tools/i4f.py`

Prefer the CLI over hand-editing index files or constructing IDs manually.
IDs and indices are a pure function of the artifact files; the CLI computes
them deterministically.

Invoke from anywhere in the repo:

```sh
python3 tools/i4f.py <command>
```

### Commands

**`status`** — load a snapshot of live state before touching individual
files. Use `--json` for programmatic parsing.

```sh
python3 tools/i4f.py status
python3 tools/i4f.py status --json
```

**`new`** — scaffold a new artifact from its template. IDs and dates are
filled in; hypothesis numbers auto-increment.

```sh
python3 tools/i4f.py new episode       --date 2025-06-02 --title "Episode title"
python3 tools/i4f.py new hypothesis    --episode MS-2025-06-02 --theme "Theme text"
python3 tools/i4f.py new recommendation \
    --ticker ACME --exchange NASDAQ --company "Acme Corp" \
    --hypothesis MS-2025-06-02-H1
```

**`index`** — rebuild `hypotheses/_index.md` and
`recommendations/_index.md` from the artifact files. Run after writing
any hypothesis or recommendation. Never hand-edit the `_index.md` files.

```sh
python3 tools/i4f.py index
```

**`validate`** — check every artifact's front-matter: required fields,
enum values, ID format, cross-references, index staleness. Exits non-zero
on errors.

```sh
python3 tools/i4f.py validate
```

Wire `validate` into the agent's pre-commit step. If it fails, fix the
errors before committing.

---

## The weekly loop

Full detail is in `AGENTS.md` (definition of done). The short version:

1. Drop the episode transcript or summary into `episodes/`. Use `new
   episode` to scaffold the file.
2. Run the prompt chain in order: `prompts/01-extract.md` through
   `prompts/05-synthesize.md`. Each prompt file specifies its role.
3. For each hypothesis and recommendation the agent emits, use `new
   hypothesis` / `new recommendation` to create the files.
4. Run `python3 tools/i4f.py index` to rebuild the indices.
5. Run `python3 tools/i4f.py validate`. Fix any errors.
6. Read `portfolio/journal.md` — recent entries carry fills, decisions,
   and out-of-band context from the user. Factor them in before committing.
7. Review `git diff hypotheses/ recommendations/` before committing.
8. Commit with a conventional message:
   `weekly: MS-YYYY-MM-DD — {short title}`

---

## Decision loop

The weekly run produces recommendations. The decision loop turns them into
actionable signals and carries the user's feedback back. Run it whenever a
read on what to do is wanted — independent of the weekly cadence.

Full detail is in the "Decision loop" section of `AGENTS.md`. The short
version:

1. **Refresh `portfolio/prices.md`.** Hermes fetches current quotes for
   every held and watched ticker by whatever quote source it has, then
   rewrites the price table. The CLI does not fetch prices itself — that
   is Hermes's job. Leave `—` for any ticker it cannot quote; the board
   will flag it as `NO PRICE`.

2. **Run `board` to rebuild the action board.**

   ```sh
   python3 tools/i4f.py board
   ```

   This reads `portfolio/prices.md`, all recommendations, and
   `portfolio/positions.md`, then writes `portfolio/action-board.md` with
   three sections:
   - **Buy signals** — each NEW/WATCHING recommendation: price placed
     against its entry zone (in zone / below / above / wait).
   - **Sell / review signals** — held positions whose linked hypothesis
     was falsified, expired, or rejected.
   - **Portfolio performance** — per-position value and P/L %.

   The board is a decision surface, not a trade order. The human decides.

3. **Surface the board to the user.** Present `portfolio/action-board.md`
   and wait for a response.

4. **Log fills and observations with `journal`.**

   ```sh
   python3 tools/i4f.py journal "bought TSM 8 @ 272"
   ```

   This appends a dated line to `portfolio/journal.md`. The weekly run
   and the review cycle both read recent journal entries — it is how fills,
   doubts, and market events reach the process. Append-only; never rewrite
   past entries.

`portfolio/positions.md`, `prices.md`, `journal.md`, and `action-board.md`
are git-ignored — they hold real holdings and performance, so they stay on
the machine where the agent runs and never reach the shared repo.

---

## Hermes quickstart

Hermes is a local Python-based AI agent running on Mac. The same steps
apply to Open Interpreter, Goose, Claude Code, or any agent that can
read/write files and run shell commands.

1. **Point Hermes at the cloned repo directory.** Set its working
   directory (or equivalent config) to the repo root.

2. **Allow it to run `python3` and `git`.** Confirm those commands are
   permitted in its tool / shell policy.

3. **Have it read `AGENTS.md` first** on every session boot, before
   reading anything else. This is the operating manual.

4. **Use `status --json` as the boot shortcut** to load a machine-readable
   snapshot cheaply, then load only the individual files the task requires.

5. **Wire `validate` before every commit.** The agent should refuse to
   commit if `validate` exits non-zero.

6. **For decision-loop runs:** fetch prices into `portfolio/prices.md`,
   run `board`, present `portfolio/action-board.md` to the user, then
   record any reply with `journal`.

There is no Hermes-specific config format or API to set up. The repo
interface is files and shell commands; any agent that can exercise those
two primitives works.

---

## Safety

- The repo interface is files and git only — no external accounts, no
  write APIs. (A prompt step may use the agent's own web search for
  research; that is separate from how it touches the repo.)
- The human reviews `git diff` and decides what to merge. The agent
  proposes; the human merges.
- Always run `python3 tools/i4f.py validate` before every commit. It
  catches broken IDs, missing fields, bad enum values, and stale indices.
- For changes to `brain/world-model.md` or `brain/lessons.md`, the agent
  should produce a diff for human review rather than committing directly.
  See the file-ownership table in `AGENTS.md`.
