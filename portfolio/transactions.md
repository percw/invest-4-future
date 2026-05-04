---
updated: 2026-05-04
---

# Transactions log

Append-only. Status enum: Filled | Pending | Cancelled.

| Date | Ticker | Exchange | Action | Qty | Price | Ccy | Brutto | Fee | FX→NOK | Net NOK | Hyp-ID | Rationale | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-06-15 | EQNR | OSL | Buy | 100 | 290.00 | NOK | 29,000.00 | 29 | 1.0000 | 29,029 | — | Energy exposure | Filled |
| 2024-08-20 | NVDA | NASDAQ | Buy | 10 | 450.00 | USD | 4,500.00 | 49 | 9.2629 | 41,732 | MS-2025-01-13-H1 | AI infra | Filled |
| 2024-09-10 | ASML | AMS | Buy | 5 | 700.00 | EUR | 3,500.00 | 49 | 10.8514 | 38,029 | — | EUV monopoly | Filled |
| 2025-01-15 | TSLA | NASDAQ | Buy | 5 | 380.00 | USD | 1,900.00 | 49 | 9.2629 | 17,648 | MS-2025-01-13-H2 | Robotaxi | **Pending — recommend Cancel** |

## Open actions

- TSLA pending order (2025-01-15): hypothesis MS-2025-01-13-H2 was
  rejected as priced-in. Recommend status → Cancelled unless new
  mechanism emerges.
