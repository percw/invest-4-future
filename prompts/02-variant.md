# Prompt 02 — Variant perception test

**Role**: stress-test each hypothesis against current consensus.

**Suggested model**: Opus 4.7 + WebSearch (contrarian reasoning, fresh data).

## Input

- All hypothesis files created in step 01
- `brain/world-model.md` (current views and assumptions)
- WebSearch (sell-side notes, recent news, stock moves)

## Output

- Edit each hypothesis file in place. Fill the `verdict` field:
  - `non-consensus` — gap is real, mechanism present, not yet priced
  - `priced-in` — consensus has updated; divergence stale
  - `hype` — divergence with no mechanism
  - `too-early` — investable case requires private markets
- For non-`non-consensus` verdicts, set `status: REJECTED` and add a
  "Why rejected" section explaining which of (b) priced-in, (c) hype,
  or (too-early) applies.
- Append an entry to `Update log`.

## Rules

1. Three forced questions per hypothesis:
   - What does median sell-side believe today?
   - Where does the speaker diverge?
   - Is the gap genuine, stale, or hype?
2. Use WebSearch to verify consensus framing — don't guess from memory.
3. If a hypothesis has run +100 % LTM with no proportional EPS revision,
   default to `priced-in` unless evidence is strong.
4. Be honest. Killing a hypothesis is a feature.

## Output checklist

- [ ] Every hypothesis has a `verdict` field set
- [ ] Rejected hypotheses have a "Why rejected" section
- [ ] `Consensus view` and `Variant perception` sections cite sources
      (or note "not verified" honestly)
