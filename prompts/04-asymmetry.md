# Prompt 04 — Asymmetry & sizing

**Role**: estimate honest upside / downside, compute asymmetry, size
the position.

**Suggested model**: Opus 4.7 (conservative numerical reasoning).

## Input

- Recommendation drafts from step 03
- `brain/mandate.md` (asymmetry threshold, sizing tiers)
- Current price data (WebSearch / GOOGLEFINANCE)

## Output

- Edit each recommendation file in place. Fill:
  - `upside_pct` (with stated assumption)
  - `downside_pct` (with stated assumption)
  - `asymmetry` (auto: upside / |downside|)
  - `entry_zone`
  - `position_size_pct` per sizing tier in `mandate.md`
- If asymmetry < 2.0, set `status: REJECTED` with reason in the
  "Asymmetry" section.

## Rules

1. **Be honest, not optimistic.** An exciting story does not justify
   inflating upside.
2. State the **single assumption** that drives upside. State the
   **single assumption** that drives downside.
3. Downside must be bound. If it's open-ended, the position isn't sized
   yet — return to step 03.
4. Sizing per `mandate.md`:
   - Conviction 3 → 1.5 %
   - Conviction 4 → 2.0-2.5 %
   - Conviction 5 → 3.0 %
   - Macro cap 5 %, sector cap 35 %.

## Output checklist

- [ ] Asymmetry math shown (upside / |downside| = X.Xx)
- [ ] Upside and downside each have one stated assumption
- [ ] Position size matches the conviction tier in mandate.md
- [ ] Entry zone is a range, not a single price
