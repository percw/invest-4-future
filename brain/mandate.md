# Mandate — hard rules

These are not heuristics. They are filters. An idea that fails any of them
does not enter the portfolio.

## Investability filters (all must pass)

- [ ] Listed on US, EU, EØS, UK, or Nordic exchange
- [ ] Average daily volume > $5M USD equivalent
- [ ] Market cap > $500M USD equivalent
- [ ] ≥ 50 % revenue exposure to the thesis (`pure_play_pct ≥ 50`)
- [ ] Not up > 100 % LTM without proportional EPS / revenue revisions
- [ ] If equivalent exposure on Oslo / EU exchange exists → prefer it (ASK)

## ETF rule

ETF is acceptable **only** when no liquid single-stock pure-play exists.
Tag with `instrument_type: ETF` so it can be filtered.

## Asymmetry rule

`asymmetry = upside_pct / |downside_pct| ≥ 2.0`

Both sides must be estimated honestly. If downside is hard to bound,
the idea is not investable yet.

## Position sizing

| Tier | Conviction (1-5) | Size |
|---|---|---|
| Probe | 1-2 | Don't open |
| Standard | 3 | 1.5 % |
| High conviction | 4 | 2.0-2.5 % |
| Best idea | 5 | 3.0 % |
| Macro cap | — | 5.0 % per name |
| Sector cap | — | 35 % NAV |

## Process rules

- An idea is rejected unless it is **simultaneously** non-consensus, has
  a stated mechanism, and is investable. Two-of-three is not enough.
- "Diamandis said it" is not a reason. Mechanism is a reason.
- If a thesis is too early for public markets (private/seed only),
  reject it and note in the file. Don't loosen the rules.
- Numerical estimates carry uncertainty. State the assumption that
  drives upside and the assumption that drives downside.

## When to sell

- Tese falsified (one of the falsification triggers in the hypothesis file fires)
- Position grows past 5 % NAV (trim back to 3 %)
- Sector exposure past 35 % NAV (trim weakest conviction first)
- Better idea displaces it on asymmetry (force-rank)
