# Assumptions

Every assumption used in models, valuations or backtests goes here with its source and date. Update the entry when it changes, and keep the history in the Changes column.

| ID | Area | Assumption | Value | Source / basis | Date set | Changes |
|---|---|---|---|---|---|---|
| A-001 | Quant | Core liquidity threshold: median daily traded value (close × volume) | ≥ IDR 1.5bn | Judgement. Measured on S-002 daily data in `quant/build_universe.py` | 2026-11-24 | 2026-11-24: measurement moved from S-001 (weekly, deprecated) to S-002 daily median |
| A-002 | Quant | Extended liquidity band | IDR 0.25–1.5bn | Same as A-001 | 2026-11-24 | As A-001 |
| A-003 | Quant | Liquidity lookback window | 63 trading days (~3 months), median | Judgement: robust to one-off block trades | 2026-11-24 | — |
| A-004 | Quant | IPO seasoning before PIT eligibility | 60 trading days | Judgement: avoids IPO price-discovery period | 2026-11-24 | — |
| A-005 | Quant | Fallback publication lag for financial statements when the filing date is unknown | Q1–Q3: period-end + 30 days (unaudited); FY: period-end + 90 days (audited) | OJK reporting deadlines, to be confirmed against the regulation text; conservative use | 2026-11-24 | 2026-11-24: superseded for TAPG by A-012/A-013 |
| A-006 | Quant | Suspension / stale filter | Ineligible if zero volume in all of the last 20 sessions | Judgement | 2026-11-24 | — |
| A-007 | Portfolio | Benchmarks | IHSG (`^JKSE`) and an equal-weight core PIT universe, rebalanced monthly | User mandate (D-003) | 2026-11-24 | — |
| A-009 | Weather | Regional rainfall regions | Approximate lat/lon rectangles for 8 palm provinces (see `quant/fetch_chirps.py`); not polygons; overlapping edges | Judgement; to be replaced by estate-weighted areas from annual reports | 2026-11-24 | — |
| A-010 | Weather / PIT | CHIRPS monthly availability lag | Usable from month-end + 45 days | Conservative judgement; CHIRPS files carry no release date — verify against CHC release notes | 2026-11-24 | — |
| A-011 | Fundamentals / PIT | Yahoo (S-020) statements have no filing date | Apply the A-005 lags | A-005 | 2026-11-24 | — |
| A-012 | PIT dating | Availability date of a disclosure | Next weekday after the earliest DATED press report (S-026) if one exists, otherwise next weekday after the assumed statutory deadline (A-013). Annual-report operational tables: later of the AR deadline and PDF creation date, +1 weekday. Weekdays, not the IDX holiday calendar. | No IDX upload timestamps available (S-013 blocked); see `data/reference/TAPG_disclosure_dates.csv` | 2026-11-24 | Replaces the document-date proxies used in round 3 (auditor / Directors / PDF dates are not disclosure dates) |
| A-013 | PIT dating | Assumed statutory filing deadlines | Unaudited interim: end of month after period-end; audited annual: end of 3rd month; annual report: end of 4th month | Working assumption based on OJK rules; **not yet verified against the POJK text** | 2026-11-24 | — |
| A-014 | PIT dating | World Bank Pink Sheet monthly price availability | Usable from the 5th weekday of the following month | Conservative; the Pink Sheet is typically released in the first days of the month | 2026-11-24 | — |
| A-015 | Capex | Mapping of fixed-asset classes to plantation / mill / other | Plantation = immature bearer plants + nursery + land; mills are NOT separately disclosed (machinery & installations used only as a labelled proxy); buildings & infrastructure and construction in progress are unallocated | TAPG note 12 classes (S-021) | 2026-11-24 | — |
| A-016 | Quant | Residual momentum specification | 36-month rolling market model (min 24 obs) vs IHSG; score = sum of residuals over t-12..t-2 divided by their std | Standard academic form; untuned | 2026-11-24 | — |
| A-017 | Quant | Regression conventions | Daily: 252-day rolling OLS, step 5 days; monthly: log returns, Newey-West 3 lags | Judgement | 2026-11-24 | — |
| A-018 | PIT dating | Availability from an IDX announcement timestamp | Filed before 09:00 WIB → same trading day; otherwise next trading day (IHSG calendar from S-002) | Conservative for intraday filings; timestamps from S-027 mirror | 2026-11-24 | Supersedes A-012/A-013 wherever a timestamp exists |
| A-019 | Nowcast | Q4 2026 scenario inputs (CPO volume factor, inventory release, ASP change, fertiliser, JV share, purchased-FFB pass-through 50%) | See `data/reference/research/TAPG_q4_2026_inputs.csv` and `quant/tapg_q4_2026_nowcast.py` (all tagged EST) | Judgement anchored on Q3 2026 observed values | 2026-11-24 | — |
| A-020 | Nowcast | Finished-goods cost per kg (to convert the inventory build into tonnes) | IDR 9,000/kg | Rough: 9M26 COGM ÷ estimated subsidiary CPO+PK output | 2026-11-24 | — |
| A-021 | Nowcast | Product allocation and carrying cost of the finished-goods build | Allocated by Q3 2026 revenue mix (CPO 81%, PK 13%, other 6%); unit carrying cost = 0.578 × ASP for every product (from A-020) | Judgement; replaces the earlier all-CPO treatment (D-015) | 2026-11-24 | — |
| A-022 | Quant | Event-study specification | Market model on IHSG and on PIT core peers ex-TAPG; estimation days −260..−11; CAR windows [0,0], [0,1], [0,5], [0,10]; abnormal volume vs days −60..−11 | Standard; untuned | 2026-11-24 | — |
| A-023 | Nowcast | Q4 2026 base CPO ASP change vs Q3 | −5.5% (KPBN tender average Q4-to-date vs Q3; few observations, secondary); bear −10%, bull −2% | S-023 snapshot; netback analysis | 2026-11-24 | Base was −4% before 2026-11-24 |
| A-024 | Valuation | Reverse valuation | ke 11–14% (central 12.5%), g 0–4% (central 2%), FCFE conversion 0.80–0.90 (central 0.85) | Judgement for an IDR large-cap plantation; risk-free and ERP not separately sourced | 2026-11-24 | — |
| A-025 | FY27 model | Drivers | Group CPO FY26 1,016kt (guidance); FY27 production bear −12% / base −7.5% / bull 0%; consolidated share 68.4%; seasonality = 2025 quarters; world CPO USD 1,000/1,100/1,200; USDIDR 18,000; HRef = 0.873 × WB; basis −53 IDR/kg; fertiliser FY26 ≈ 692bn (from a broker FY25 ≈ 800bn), FY27 × 1.25 (bull × 1.10); non-fertiliser COGS 50% price pass-through + 3–5% inflation; JV scales with TAPG gross profit | `quant/tapg_fy2027_model.py` docstring; mixed OBS/BRK/GUID/EST | 2026-11-24 | — |
| A-026 | Nowcast | Joint downside grid levels | See `quant/tapg_q4_downside.py` (plausible / stressed / extreme per driver) | Evidence-anchored judgement | 2026-11-24 | — |
| A-027 | Challenger | DSNG inventory release profit | 29kt × ASP 15,520 × 9M EBITDA margin 32%, 22% tax | Rough proxy; DSNG cost not modelled | 2026-11-24 | — |
| A-028 | Allocation | TAPG entry analysis | Scenario sustainable profit 2,810 / 4,062 / 4,969bn with probabilities 30 / 50 / 20%; 12m dividends IDR 160 / 200 / 230; hurdle = ke + 5pp = 17.5% | Judgement (probabilities not estimated) | 2026-11-24 | — |
| A-029 | Allocation | Uniform challenger valuation rule | bear 0.8 × last FY profit; base = average(last FY, consensus FY26); bull = consensus FY27; FCFE conversion TAPG 0.85 / DSNG 0.80 / STAA 0.70; ke 12.5%, g 2%; weights 30 / 50 / 20 | Judgement; consensus-anchored so the names are comparable | 2026-11-24 | — |
| A-008 | Backtest | Backtest start | 2016-01 or the first month all required inputs exist, whichever is later | User mandate (D-003); see the Phase I audit | 2026-11-24 | — |

## Still to set (before the first backtest)

- **Macro:** CPO price deck, levy and duty schedule, biodiesel mandate path.
- **Industry:** FFB yields by tree age, oil extraction rate, cash cost per tonne.
- **Valuation:** risk-free rate, equity risk premium, country risk premium, terminal growth, EV per planted hectare.
- **Quant / portfolio:** transaction costs (commission, levy, VAT, bid-ask), position caps, a liquidity cap as a % of ADV, and the minimum number of holdings.
