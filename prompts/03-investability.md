# Prompt 03 — Investability screen

**Role**: for each surviving (non-consensus) hypothesis, find instruments
that pass the mandate filters.

**Suggested model**: Sonnet 4.6 (precise rule application).

## Input

- All hypothesis files where `verdict: non-consensus` and `status: ACTIVE`
- `brain/mandate.md` (filters)

## Output

- Draft files at `recommendations/{TICKER}.md` using
  `recommendations/_template.md`.
- Leave `upside_pct`, `downside_pct`, `asymmetry`, `position_size_pct`
  empty — step 04 fills them.
- Set `status: NEW`.

## Rules

For each candidate ticker, check:

- [ ] Listed on US, EU, EØS, UK, or Nordic exchange
- [ ] ADV > $5M USD-equivalent
- [ ] Market cap > $500M USD-equivalent
- [ ] `pure_play_pct` ≥ 50 to the specific hypothesis (state in file)
- [ ] Not up > 100 % LTM without proportional EPS / revenue revision
- [ ] **Prefer Oslo / EU listing** if equivalent exposure exists (ASK)

If no single-stock passes, consider one ETF. Tag `instrument_type: ETF`
in front-matter.

If neither single-stock nor ETF passes, mark the hypothesis itself
`verdict: too-early` and `status: REJECTED` with a "no investable
expression" note. Don't force a pick.

## Output checklist

- [ ] Each recommendation file states `pure_play_pct` with justification
- [ ] Each lists ≤2 alternative tickers considered and why this one won
- [ ] ASK eligibility (`ask_eligible: true/false`) is filled
- [ ] Recommendations linked to hypothesis via `hypothesis_id`
