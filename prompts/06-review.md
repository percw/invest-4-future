# Prompt 06 — Review & self-critique

**Role**: review open hypotheses and positions, assess real-world outcomes,
close the ones that have resolved, audit the rejected pile, score the
process's calibration, and propose corrections to the playbook.

**Suggested model**: Opus 4.7 + WebSearch (honest outcome assessment requires
fresh catalyst data).

## Input

- Output of `python3 tools/i4f.py review`
- The hypothesis and recommendation files it flags
- `brain/world-model.md`
- `brain/scorecard.md`
- `brain/playbook.md`
- `brain/lessons.md`
- `portfolio/journal.md` (recent user messages — fills, doubts, events)
- WebSearch

## Output

1. Run `python3 tools/i4f.py review` to surface what is due.

   ```
   python3 tools/i4f.py review
   ```

2. For each due hypothesis: use WebSearch to check whether catalysts fired
   and whether any falsification triggers fired. Then either:
   - **Close it** — set `status` to `CONFIRMED`, `FALSIFIED`, or `EXPIRED`;
     fill the `## Review` section; set `reviewed:` to today; append a dated
     line to `## Update log`.
   - **Keep it ACTIVE** — if the thesis is intact and the horizon has not
     elapsed, bump `reviewed:` to today and append a dated update-log line
     noting the check.
   - **Audit a reject** — for a hypothesis flagged with status REJECTED,
     check whether the claim came true anyway. Set `reject_outcome:` to
     `vindicated` (the reject held — the claim fizzled or stayed priced
     in) or `missed` (the claim came true; alpha was left on the table).
     Fill the `## Review` section and set `reviewed:` to today. Half the
     alpha is in what you did not buy — a `missed` reject is a real error.

3. For each due BOUGHT or TRIMMED position: confirm the thesis is still
   intact. If the position has been exited, set `status: EXITED`, fill
   `realized_pct` and `exit_date`, and complete the `## Review` section.

4. Rebuild `brain/scorecard.md`.

   ```
   python3 tools/i4f.py scorecard
   ```

5. Append notable hits and misses to `brain/lessons.md`. Use the format
   already in that file: a dated `##` heading, a short narrative, and a
   `→` line stating what to encode.

6. Where the scorecard reveals a recurring error pattern, propose edits to
   `brain/playbook.md` or `brain/world-model.md` as a unified diff in the
   output. Do not apply the diff. The user merges manually.

## Rules

1. A falsified hypothesis is a feature, not a failure. Score honestly; do
   not stretch evidence to keep a thesis alive.
2. Use WebSearch to verify catalysts and triggers — never assess outcomes
   from memory alone.
3. Update logs are append-only. Add a dated line; never rewrite history.
4. Propose process edits; never apply them. Never edit `brain/mandate.md`
   or `brain/identity.md` — those are user-only files. Edits to
   `playbook.md` and `world-model.md` are stated as diffs the user merges.
5. A hypothesis that remains ACTIVE after review must have `reviewed:`
   bumped so it does not re-flag immediately on the next run.

## Output checklist

- [ ] Every due hypothesis has `reviewed:` updated
- [ ] Closed hypotheses have a filled `## Review` section and a
      `CONFIRMED` / `FALSIFIED` / `EXPIRED` status
- [ ] Every rejected hypothesis past its horizon has `reject_outcome` set
      and a filled `## Review` section
- [ ] Closed positions have `status: EXITED`, `realized_pct`, and
      `exit_date` set, with a completed `## Review` section
- [ ] `brain/scorecard.md` rebuilt via `python3 tools/i4f.py scorecard`
- [ ] `brain/lessons.md` appended where a hit or miss warrants a post-mortem
- [ ] Playbook / world-model edits stated as a proposed diff in the output,
      not applied
