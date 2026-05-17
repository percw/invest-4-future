---
ticker: ""
exchange: ""                        # NASDAQ | NYSE | OSL | AMS | STO | LON | EPA | FRA
company: ""
hypothesis_id: ""
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: NEW                         # NEW | WATCHING | BOUGHT | TRIMMED | EXITED | REJECTED
pure_play_pct: 0
conviction: 3                       # 1-5
horizon_months: 18
upside_pct: 0
downside_pct: 0
asymmetry: 0.0
entry_zone: ""                      # e.g. "260-285 USD"
position_size_pct: 0.0
ask_eligible: false
realized_pct:                       # set at exit - actual % return
exit_date:                          # YYYY-MM-DD - set at exit
---

## One-line thesis

What is the bet, in one sentence.

## Why this instrument

Why this ticker over alternatives. Pure-play justification. ASK fit if applicable.

## Asymmetry

- **Upside scenario**: assumption + magnitude
- **Downside scenario**: assumption + magnitude
- **Math**: upside / |downside| = X.Xx

## Entry & sizing

- Entry zone: ___
- Position size: ___ % NAV
- Conditions for upsizing / downsizing

## Status log

- YYYY-MM-DD: NEW — created
- 

## Review

Filled at exit (status -> EXITED). The review cycle (`prompts/06-review.md`)
writes this; `i4f scorecard` reads `realized_pct` to score the call.

- **Realized**: `realized_pct` vs the estimated upside / downside.
- **Asymmetry check**: was the asymmetry estimate honest in hindsight?
- **Lesson**: one line - propose for `brain/lessons.md`.
