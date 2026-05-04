# Prompt 05 — Synthesize & emit

**Role**: rebuild indices, emit a weekly digest, propose updates to
`world-model.md`.

**Suggested model**: Sonnet 4.6 (structured emit).

## Input

- All hypothesis and recommendation files touched this run
- `hypotheses/_index.md` (existing)
- `recommendations/_index.md` (existing)
- `portfolio/watchlist.md`

## Output

1. Rebuild `hypotheses/_index.md`:
   - Active table sorted by conviction desc
   - Rejected table with reason
   - Confirmed / falsified / expired table
2. Rebuild `recommendations/_index.md`:
   - NEW table with asymmetry, entry zone, ASK flag
   - BOUGHT, REJECTED tables
3. Append NEW recommendations to `portfolio/watchlist.md`.
4. Write `digests/YYYY-MM-DD.md` with:
   - Episode summary (1-2 lines)
   - Hypotheses kept / rejected (1 line each)
   - Recommendations (1 line each, with asymmetry)
   - Updates to `world-model.md` proposed (don't apply — let user merge)
5. Suggest `lessons.md` entries if any prior hypothesis hit a
   falsification trigger this week.

## Rules

- **Never fill the recommendation quota.** If <3 ideas survive, output
  fewer. The framework values empty weeks.
- All numbers must trace to a source file. No recomputed estimates here.
- World-model updates are *proposed*, not applied. User merges manually.

## Output checklist

- [ ] Indices rebuilt (don't append, rewrite from scratch)
- [ ] Watchlist appended (not rebuilt — preserve user-edited entries)
- [ ] Digest written
- [ ] Proposed world-model edits stated as a diff in the digest
- [ ] One commit, message format: `weekly: MS-YYYY-MM-DD — {short title}`
