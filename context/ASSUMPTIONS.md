# Assumptions

Every assumption used in models, valuations or backtests goes here with its source and date. Update the entry when it changes, and keep the history in the Changes column.

| ID | Area | Assumption | Value | Source / basis | Date set | Changes |
|---|---|---|---|---|---|---|
| A-001 | Quant | Core liquidity threshold: median daily traded value (close × volume) | ≥ IDR 1.5bn | Judgement. Measured on S-002 daily data in `quant/build_universe.py` | 2026-11-24 | 2026-11-24: measurement moved from S-001 (weekly, deprecated) to S-002 daily median |
| A-002 | Quant | Extended liquidity band | IDR 0.25–1.5bn | Same as A-001 | 2026-11-24 | As A-001 |
| A-003 | Quant | Liquidity lookback window | 63 trading days (~3 months), median | Judgement: robust to one-off block trades | 2026-11-24 | — |
| A-004 | Quant | IPO seasoning before PIT eligibility | 60 trading days | Judgement: avoids IPO price-discovery period | 2026-11-24 | — |
| A-005 | Quant | Fallback publication lag for financial statements when the filing date is unknown | Q1–Q3: period-end + 30 days (unaudited); FY: period-end + 90 days (audited) | OJK reporting deadlines, to be confirmed against the regulation text; conservative use | 2026-11-24 | — |
| A-006 | Quant | Suspension / stale filter | Ineligible if zero volume in all of the last 20 sessions | Judgement | 2026-11-24 | — |
| A-007 | Portfolio | Benchmarks | IHSG (`^JKSE`) and an equal-weight core PIT universe, rebalanced monthly | User mandate (D-003) | 2026-11-24 | — |
| A-009 | Weather | Regional rainfall regions | Approximate lat/lon rectangles for 8 palm provinces (see `quant/fetch_chirps.py`); not polygons; overlapping edges | Judgement; to be replaced by estate-weighted areas from annual reports | 2026-11-24 | — |
| A-010 | Weather / PIT | CHIRPS monthly availability lag | Usable from month-end + 45 days | Conservative judgement; CHIRPS files carry no release date — verify against CHC release notes | 2026-11-24 | — |
| A-011 | Fundamentals / PIT | Yahoo (S-020) statements have no filing date | Apply the A-005 lags | A-005 | 2026-11-24 | — |
| A-008 | Backtest | Backtest start | 2016-01 or the first month all required inputs exist, whichever is later | User mandate (D-003); see the Phase I audit | 2026-11-24 | — |

## Still to set (before the first backtest)

- **Macro:** CPO price deck, levy and duty schedule, biodiesel mandate path.
- **Industry:** FFB yields by tree age, oil extraction rate, cash cost per tonne.
- **Valuation:** risk-free rate, equity risk premium, country risk premium, terminal growth, EV per planted hectare.
- **Quant / portfolio:** transaction costs (commission, levy, VAT, bid-ask), position caps, a liquidity cap as a % of ADV, and the minimum number of holdings.
