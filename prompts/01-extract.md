# Prompt 01 — Hypothesis extraction

**Role**: extract testable investment hypotheses from a Moonshots episode.

**Suggested model**: Sonnet 4.6 (high recall over long transcripts).

## Input

- `episodes/MS-YYYY-MM-DD.md` (the episode file)
- `brain/playbook.md` (Step 1 rules)

## Output

- N draft files at `hypotheses/MS-YYYY-MM-DD-H{n}.md`, using
  `hypotheses/_template.md`.
- Set `verdict: ` field empty (next step fills it).
- Set `status: ACTIVE` for now.

## Rules

1. Identify 3-7 hypotheses. Each must be falsifiable in 12-24 months,
   have an explicit mechanism, and at least one observable catalyst.
2. Reject vague themes ("AI will change everything"). Be specific:
   numbers, deadlines, named companies.
3. If the episode has fewer than 3 testable claims, output what you find.
   Don't invent.
4. Quote the source: include a one-line quote in the `Variant perception`
   section so the speaker's framing is preserved.
5. Don't pre-screen for investability or pricing — that's later steps.

## Output checklist

- [ ] Each hypothesis has a number + deadline in the claim
- [ ] Each has a mechanism paragraph (not a slogan)
- [ ] Each lists 2+ catalysts with date windows
- [ ] Each lists 2+ falsification triggers
- [ ] Update log shows `created` line with today's date
