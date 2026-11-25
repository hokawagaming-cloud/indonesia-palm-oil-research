# PT PP London Sumatra Indonesia Tbk (LSIP) — Ageing Estate, Trapped Cash

_Institutional equity research · Phase XVII · 2026-11-26 · Price IDR 1,575 (close 25 Nov 2026) · IDR bn unless stated_
_Integrated model: `outputs/LSIP_model_valuation.xlsx` (live formulas) · Cohort model: `valuation/lsip_cohort.py` · All exhibits: `outputs/lsip/`_
_Not investment advice. Evidence classes: **REPORTED** (filings), **DERIVED** (our arithmetic on filings), **ANALYST** (assumption), **RECONSTRUCTED** (model-inferred, not disclosed)._

## Recommendation: HOLD / WATCH — BUY at ≤ IDR 1,473 or on verified capital return

| | |
|---|---|
| Price (25 Nov 2026) | IDR 1,575 |
| Fair value at 31 Dec 2026, bear / base / bull (scenario A, 80% cash credit) | IDR 1,203 / **1,790** / 2,491 |
| of which plantation operations / distributable surplus cash (base) | IDR 812 / 977 |
| Value with 100% / 60% cash credit (base) | IDR 2,034 / 1,545 |
| Minority cash-receipts value (DDM, 30% payout, base) | IDR 537 |
| 12-month target price (base, 80% credit) | **IDR 1,904** |
| Expected dividend (FY2027 DPS, base) / yield | IDR 100 / 6.4% |
| Expected 12-month total return: base / bear / bull | **27%** / -14% / 77% |
| 12-month return if the market's current cash credit (62%) persists | 12% |
| Cash credit needed to clear the 17.5% hurdle (18.1% proposed) | 69% (70%) |
| Entry price for the hurdle: base 80% credit / robust to 60% credit | IDR 1,706 / **IDR 1,473** (IDR 1,465 at 18.1%) |
| Downside scenario (bear price, 60% cash credit) | IDR 959 (-32%) |
| Investment horizon | 12-24 months (catalysts: buyback report Jan 2027, FY26 results Feb 2027, AGM Jun 2027) |

**Answer to the central question.** After accounting for plantation ageing, replanting needs and capital-allocation risk, LSIP **does offer a better risk-adjusted expected return than TAPG at prevailing prices** (base 27% vs -6%; bear -14% vs -31%; return per unit of volatility 0.84 vs -0.16), because LSIP's price already discounts weak plantation economics and trapped cash (it implies a long-run realised CPO price of about IDR 13,133/kg at 80% cash credit) while TAPG's price capitalises about IDR 4,278bn of sustainable profit (long-run CPO ≈ IDR 15,469/kg). **But LSIP clears our own hurdle only if minority shareholders can expect to realise at least ~69% of the distributable surplus cash**, and the market currently credits about 62%. The binding constraint is capital allocation, not biology: correcting the age profile (scenario B) adds only about IDR 69/share, whereas lifting the payout from 30% to 100% raises the minority cash-flow value from IDR 537 to IDR 1,521/share. We therefore rate LSIP **HOLD / WATCH** — a relative-value preference over TAPG, not an absolute BUY — and would buy below IDR 1,473 or on verified capital return.

LSIP-specific forecasting here is **not validated**: the earnings model and the Q4 nowcast have no out-of-sample record (first resolution: FY2026 results, ~Feb 2027). Nothing in this report is a claim of trading alpha.

## 1. Thesis in five points

1. **The estate is old, and disclosure has stopped.** At FY2023, 41% of the 91,759 ha nucleus oil-palm area was older than 20 years (REPORTED, AR2023 p7); the reported average age rose from 13.4 (Mar 2016) to 19 years (AR2023; SR2023 says 18). **No age profile has been published since** (AR2024, AR2025, SR2024, SR2025 all omit it).
2. **Replanting runs at half the replacement rate.** Reconstructed plantings average 1,839 ha/yr over 2017-2025 (RECONSTRUCTED; ensemble 1,790-1,874), an implied ~49-year cycle, versus 3,573 ha/yr for a 25-year cycle.
3. **Yields are low, and age explains only a third of it.** Nucleus yield fell from 17.4 t/ha (FY2018) to 13.4 t/ha (FY2025) against TAPG's 24.3. On a common standard curve, LSIP's age mix explains 3.7 t/ha of the 10.9 t/ha gap; the other 7.1 t/ha is a productivity shortfall (LSIP achieves 67% of the curve vs TAPG 103%).
4. **The cash is real, but most of it is not reaching minorities.** Cash was IDR 8,516bn at 30 Sep 2026 with no debt; distributable surplus after operating needs and debt-like items is IDR 6,863bn (1,006/share, 64% of the price). Payout has been 20-35%; the parent SIMP (59.51%) buys 63% of revenue; 15-22% of cash sat at the Salim-group Bank Ina Perdana in FY2021-25.
5. **Valuation already prices much of this.** Market EV ex cash is about IDR 52-67m per planted ha vs TAPG IDR 245m, although FY2025 operating profit per mature ha differs by only 16%.

## 2. Audit of previous LSIP research

Previous outputs were treated as hypotheses and recomputed from primary disclosures (`quant/lsip_phase17_analysis.py`, `LSIP_prior_audit.csv`). The Stage-1 nowcast and Phase VII figures are preserved unchanged in their original files.

| previous_finding | previous_value | phase17_value | status | evidence |
|---|---|---|---|---|
| Cash ~IDR 8.5tn (9M26) | 8,516 | 8,516 | CONFIRMED | 9M26 FS |
| Excess cash IDR 6.3tn | 6,324 | 6,113 | REVISED (method) | v1 deducted one quarter of cash costs + LT employee benefits + full buyback; v2 deducts 2 months' cash costs, a seasonal WC buffer, employee benefits and taxes payable (CIP is in forecast capex, so not deducted); the buyback is shown separately. Buyback is a distribution, not a cost: value per share is unaffected by it at fair prices. |
| Historical payout ~30% | 0.300 | 0.317 | CONFIRMED (30-35%) | Company dividend page: FY21-23 35%, FY24-25 30%; FY20 20% |
| Buyback up to IDR 750bn | 750 | 750 | CONFIRMED (authorisation) | Disclosure 23 Oct 2026; window 26 Oct-31 Dec 2026 |
| Buyback execution |  |  | UNVERIFIED | No execution report on londonsumatra.com (press/disclosure pages, 25 Nov 2026); IDX blocked from this environment |
| Q4 2026 nowcast IDR 468bn (v1 base) | 468 | 534 | REVISED (v2) | v1 assumed Q4 volume 0.95x Q3; Q4 is the seasonal peak (Q4'25 = 1.16x Q3'25). v2 base 1.05x, price -3% |
| Consensus-implied Q4 IDR 360bn | 360 | 360 | CONFIRMED | FY26 EPS 308.66 x 6,820mn - 9M 1,745bn (S-036, 25 Nov 2026) |
| Expected total return 17.6% (Phase VII) | 0.176 |  | SUPERSEDED | Market-calibrated multiple frame; Phase XVII replaces it with scenario DCF/DDM (see report) |
| Preferred entry IDR 1,340-1,460 | 1,400 |  | SUPERSEDED | Recomputed from Phase XVII value range and hurdle |
| Related-party bank exposure | 665 | 665 | CONFIRMED; history added | Bank Ina Perdana 15-22% of cash FY21-FY25 (peak 1.64tn, 21.6% at FY25), 7.8% at 9M26 |
| Sales to parent SIMP |  | 0.633 | CONFIRMED | FY25 FS: SIMP 3,487bn = 63.3% of revenue (v1 cited 76%: not reproduced; 76% unverified) |
| FY2023 average age ~19 years | 19 | 19 | CONFIRMED (AR); SR says 18 | AR2023 p41 'Average Age: 19 years'; SR2023: 18 years |
| FY2023 >20 years share 41% | 0.410 | 0.410 | CONFIRMED | AR2023 p7: 37,667 / 91,759 ha |

Notes: (i) the 76% parent-sales share in the Stage-1 note could not be reproduced; the FY2025 FS discloses SIMP at 63.26% of revenue (single customer >10%). (ii) Q4 v1 is kept as logged; v2 is a separate, newer estimate. (iii) Phase VII's 17.6% expected return and 1,340-1,460 entry range came from a market-calibrated multiple frame; they are superseded by the scenario DCF/DDM framework below, not revised retroactively.

## 3. Plantation age profile and biological economics

### 3.1 Reported age bands (nucleus oil palm, ha; REPORTED)

| FY | Immature | 4-6 yrs | 7-20 yrs | >20 yrs | Total ha | >20 share |
|---|---|---|---|---|---|---|
| 2017 | 9,905 | 7,262 | 43,059 | 35,396 | 95,622 | 37% |
| 2018 | 8,762 | 4,148 | 45,877 | 37,252 | 96,039 | 39% |
| 2019 | 9,900 | 2,761 | 45,763 | 37,213 | 95,637 | 39% |
| 2020 | 10,451 | 2,252 | 45,564 | 37,807 | 96,074 | 39% |
| 2021 | 8,223 | 2,161 | 45,590 | 37,878 | 93,853 | 40% |
| 2022 | 7,408 | 2,710 | 44,377 | 36,656 | 91,151 | 40% |
| 2023 | 6,561 | 3,229 | 44,302 | 37,667 | 91,759 | 41% |

Reported average ages (every phrase is asserted to appear in the cited document by `quant/lsip_ops_dataset.py`):

| Date | Reported avg age | Source (phrase asserted in text) |
|---|---|---|
| 2016-03-31 | 13.4 | PE2016: '13,4' |
| 2017-06-30 | 15.2 | PE2017: '15,2' |
| 2018-06-30 | 16.1 | PE2018: '16,1' |
| 2018-12-31 | 16.0 | SR2018: 'Average Age: 16 years' |
| 2019-06-30 | 17.0 | PE2019: 'Umur rata-rata : 17 tahun' |
| 2019-12-31 | 16.0 | SR2019: '16 years, of which 13% is under 7 years old' |
| 2021-12-31 | 18.0 | AR2021: 'approximately 18 years' |
| 2022-12-31 | 19.0 | AR2022: 'approximately 19 years' |
| 2023-12-31 | 19.0 | AR2023: 'Average Age: 19 years' |
| 2023-12-31 | 18.0 | SR2023: 'is 18 years, with 11% being under seven years' |

Inconsistencies kept visible: the Mar-2016 deck's 13.4 years is hard to reconcile with the FY2017 bands (37% > 20 years) — the 1995-96 expansion cohorts crossed 20 in 2016-17; AR2023 and SR2023 give 19 and 18 years for the same date. The ensemble uses both.

### 3.2 Operating history (REPORTED; yield DERIVED = nucleus FFB / mature ha)

| Period | Revenue | Gross profit | Op. profit | Profit | CFO | Capex | Dividends paid | Cash | Nucleus FFB kt | Yield t/ha |
|---|---|---|---|---|---|---|---|---|---|---|
| FY2020 | 3,537 | 1,076 | 816 | 695 | 1,338 | 378 | 102 | 1,959 | 1,295 | 15.1 |
| FY2021 | 4,525 | 1,808 | 1,191 | 990 | 1,879 | 308 | 136 | 3,368 | 1,204 | 14.1 |
| FY2022 | 4,585 | 1,491 | 1,206 | 1,035 | 1,087 | 321 | 348 | 3,847 | 1,174 | 14.0 |
| FY2023 | 4,190 | 1,151 | 759 | 761 | 1,411 | 369 | 361 | 4,511 | 1,177 | 13.8 |
| FY2024 | 4,563 | 1,992 | 1,551 | 1,476 | 1,565 | 376 | 266 | 5,454 | 1,173 | 13.8 |
| FY2025 | 5,512 | 2,261 | 2,008 | 1,886 | 3,016 | 433 | 443 | 7,597 | 1,139 | 13.4 |
| 9M26 | 4,327 | 1,786 | 1,857 | 1,744 | 1,618 | 264 | 566 | 8,516 | 850 |  |

Company-owned (nucleus) FFB is separated from purchased plasma and third-party FFB (FY2025: 204kt, 15% of FFB processed; 9M26 166kt). Plasma (35,861 ha) is smallholder land and is not valued as company land. OER (CPO / all FFB processed): FY2025 21.9% reported, 9M26 22.4%; KER 6.0-6.2%. Estate-level productivity is not disclosed (regional planted area only).

### 3.3 Cost structure and fertiliser (REPORTED, COGS note)

| Period | FFB purchases | Harvesting | Upkeep & fertiliser | Upkeep IDR m/mature ha | Indirect | Total production cost |
|---|---|---|---|---|---|---|
| FY2020 | 318 | 565 | 368 | 4.3 | 630 | 2,456 |
| FY2021 | 392 | 578 | 395 | 4.6 | 654 | 2,611 |
| FY2022 | 584 | 596 | 692 | 8.3 | 652 | 3,126 |
| FY2023 | 436 | 611 | 623 | 7.3 | 543 | 2,810 |
| FY2024 | 489 | 588 | 453 | 5.3 | 680 | 2,825 |
| FY2025 | 672 | 604 | 531 | 6.3 | 746 | 3,175 |
| 9M26 | 577 | 477 | 438 |  | 723 | 2,694 |

Upkeep & fertiliser per mature hectare fell from IDR 8.3m (FY2022) to 5.3m (FY2024), then recovered to 6.3m in FY2025; the FY2025 yield was the lowest in the series. The fertiliser-catch-up hypothesis from Stage 1 is consistent with this (9M26 run-rate 438bn), but fertiliser is not disclosed separately from upkeep, so the split is not verifiable.

### 3.4 Replanting evidence

LSIP discloses no annual replanting hectares, targets or replanting capex. What exists: immature bearer-plant additions of IDR 217bn (FY2023), 185bn (FY2024) and 178bn (FY2025) (FS note 13; includes rubber and capitalised immature upkeep); "replanted area monitored by drones" of 940 ha (2020) and 3,843 ha (2023) (SR; cumulative or annual not stated); the SR2025 states a long-term goal "to gradually increase average oil palm yields by accelerating replanting". Planted oil-palm area also shrank: 96,074 ha (FY2020) → 90,798 ha (FY2025) → **89,331 ha (30 Sep 2026)**, with East Kalimantan down 3,548 ha since FY2020; the reasons are not disclosed (FY2024 impairment of IDR 296bn related to the rubber CGU).

## 4. Age-cohort model (RECONSTRUCTED; `valuation/lsip_cohort.py`)

**Reconstruction.** Planting-year areas 1997-2025 are solved by non-negative least squares with a smoothness penalty so that the reported bands (immature = ages 0-3, 4-6, 7-20, >20) for FY2017-23 and the immature area for FY2024-25 are matched; pre-1997 "old stock" is set to match the reported average age. Mean absolute band residual 1,061 ha, max 3,726 ha (FY2021: 2,228 ha of immature area disappeared with the East Kalimantan contraction — the identities cannot hold exactly). Old stock mean age in 2023: 28.4 years.

**Dynamics.** A(a+1, t+1) = A(a, t) − R(a, t); A(0, t+1) = hectares replanted in t; FFB(t) = Σ_a A(a, t)·y(a)·k(cohort). Replanting removes the oldest palms first; cleared blocks lose their full-year output; replanted blocks enter at age 0 on improved material (k × 1.15, ANALYST).

**Yield curve.** A literature-shaped standard curve (ANALYST, shape referenced to S-078) scaled to LSIP by k fitted on FY2017-25 nucleus FFB. **This is not an empirically validated LSIP age-yield relationship**: LSIP does not disclose yield by age. k fell from ~0.8 (FY2018-19) to ~0.66 (FY2021-25); the base uses the recent mean k = 0.664.

| Year | Reported nucleus FFB kt | Standard-curve potential kt | k |
|---|---|---|---|
| 2017 | 1,279 | 1,847 | 0.693 |
| 2018 | 1,516 | 1,854 | 0.818 |
| 2019 | 1,466 | 1,862 | 0.787 |
| 2020 | 1,295 | 1,837 | 0.705 |
| 2021 | 1,204 | 1,821 | 0.661 |
| 2022 | 1,174 | 1,802 | 0.651 |
| 2023 | 1,177 | 1,771 | 0.664 |
| 2024 | 1,173 | 1,760 | 0.666 |
| 2025 | 1,139 | 1,689 | 0.674 |

**Uncertainty propagation.** 36 feasible reconstructions (smoothing 0.05/0.5/5 × average age 18/19 × old-stock shape front/spread × post-18 decline 0.75/1.0/1.25) × 4 scenarios:

| Scenario | FFB 2035 min | median | max | FFB 2050 min | median | max |
|---|---|---|---|---|---|---|
| A - historical pace | 900 | 969 | 1,025 | 860 | 948 | 1,025 |
| B - accelerated | 979 | 1,003 | 1,035 | 1,223 | 1,283 | 1,351 |
| C - deferred | 830 | 912 | 982 | 796 | 895 | 983 |
| D - intensive | 998 | 1,034 | 1,087 | 1,263 | 1,336 | 1,421 |

## 5. Replanting scenarios (base price case; value per share at 80% cash credit)

| Scenario | LR planting ha/yr | Cycle yrs | FFB 2030 kt | FFB 2035 kt | FFB 2050 kt | Replant capex 2030 IDR bn | FCFF 2030 IDR bn | Ops value /sh | Value bear | Value base | Value bull | DDM base |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A - historical pace | 1,839 | 48.6 | 1,021 | 976 | 958 | 213 | 800 | 812 | 1,203 | 1,790 | 2,491 | 537 |
| B - accelerated | 3,573 | 25.0 | 989 | 1,010 | 1,289 | 401 | 575 | 881 | 1,225 | 1,855 | 2,613 | 590 |
| C - deferred | 1,839 | 48.6 | 1,037 | 918 | 904 | 93 | 931 | 779 | 1,188 | 1,761 | 2,446 | 520 |
| D - intensive | 3,573 | 25.0 | 962 | 1,041 | 1,343 | 580 | 370 | 821 | 1,142 | 1,783 | 2,555 | 594 |

Scenario definitions: A continues the reconstructed pace (1,839 ha/yr); B ramps to the sustainable rate (3,573 ha/yr = planted area / 25-year economic life, the accounting life of bearer plants) by 2028; C defers to 800 ha/yr to 2030; D replants 5,000 ha/yr oldest-first until no palms older than 25 remain, then the sustainable rate. Terminal values use each scenario's own long-run planting rate as a steady state (uniform ages over the implied cycle; productivity does not persist without reinvestment).

Readings: (1) under A and C, nucleus FFB declines ~1.5-2% a year to the mid-2030s; (2) B and D depress output and free cash flow for 8-10 years before recovering — peak funding is in 2030-2035 (D: replanting capex ~IDR 672bn in 2035, FCFF trough ~IDR 370bn) and is easily funded from cash; (3) at LSIP's current productivity, replanting earns little more than the cost of equity (13.1%): B adds IDR 69/share, D 9, while deferral (C) destroys IDR 33/share. The steady-state replacement rate is the right long-run policy (higher value, avoids the post-2035 cliff) but not a reason to front-load replanting (D).

## 6. Cash and capital allocation

### 6.1 What is genuinely surplus (30 Sep 2026)

| Item | IDR bn | Basis |
|---|---|---|
| Cash and equivalents, 30 Sep 2026 | 8,516 | 9M26 FS |
|   of which at related-party bank (Bank Ina Perdana, Salim group) | 665 | 9M26 FS note 5 |
| Restricted cash | 0 | none disclosed in cash note |
| Minimum operating cash (~2 months of cash costs) | -592 | 9M26 cash costs 2,664bn / 9 x 2 |
| Seasonal working-capital buffer (finished-goods swing) | -300 | FG 421 -> 593bn in 9M26; Q3 build 221bn |
| Committed capex in progress (CIP balance) - memo | 0 | FY25 CIP 102bn is inside forecast maintenance capex (DCF); not deducted twice |
| Employee benefits liability (debt-like) | -552 | 9M26 FS |
| Taxes payable (FY25 level) | -209 | FY25 FS |
| Replanting funding | 0 | inside the DCF (FCFF); NOT reserved here to avoid double counting |
| Distributable surplus cash (before buyback) | 6,863 | sum of the above (related-party line is a memo) |
|   per share (IDR) | 1,006 | 6,820.0mn shares |
|   as % of share price | 64% | price 1,575 |
| Buyback authorised (Oct-Dec 2026), max | -750 | disclosure 23 Oct 2026; execution UNVERIFIED |

Replanting is funded inside the operating DCF (FCFF after replanting capex), so no replanting reserve is deducted from cash — the same cost is never subtracted twice. Interest income is excluded from FCFF and cash is added once in the bridge.

### 6.2 History of cash accumulation and distribution (REPORTED / DERIVED)

| FY | Profit | DPS (Rp) | Payout | Year-end cash | Cash yield | FCF | Dividends paid | Bank Ina Perdana |
|---|---|---|---|---|---|---|---|---|
| 2020 | 695 | 20.0 | 20% | 1,959 | 3.3% | 959 | 102 | n/a |
| 2021 | 990 | 51.0 | 35% | 3,368 | 2.2% | 1,570 | 136 | 519 |
| 2022 | 1,035 | 53.0 | 35% | 3,847 | 2.2% | 767 | 348 | 674 |
| 2023 | 761 | 39.0 | 35% | 4,511 | 3.7% | 1,043 | 361 | 847 |
| 2024 | 1,476 | 65.0 | 30% | 5,454 | 4.3% | 1,189 | 266 | 907 |
| 2025 | 1,886 | 83.0 | 30% | 7,597 | 4.2% | 2,582 | 443 | 1,640 |

- Cash rose from IDR 1.96tn (FY2020) to 8,516bn (9M26) because only ~20% of FY2020-25 free cash flow was paid out. Deposits yield 2-4.4% pre-tax (3.15-6.50% quoted ranges), i.e. ~3.2% after the 20% final tax — far below a 13.1% cost of equity. Every year of retention at 30% payout transfers value away from minorities.
- **Buyback:** authorised up to IDR 750bn (26 Oct-31 Dec 2026, POJK 13/2023 market-volatility route, no shareholder vote). **Execution is UNVERIFIED** (no report on the company site at 25 Nov 2026; IDX blocked from this environment). If fully executed at IDR 1,575, value per remaining share rises by about IDR 40 (buying below intrinsic value). At a 20% participation in a median IDR 11.9bn daily value, 750bn would take ~314 trading days — it cannot be completed in the window; partial execution is the realistic best case. LSIP cancelled treasury shares in Sep 2024 (precedent).
- **Related party:** Bank Ina Perdana (Salim group) held IDR 1,640bn (22% of cash) at FY2025, down to 665bn (8%) at 9M26. A 100% haircut on this balance costs IDR 78/share.
- **Parent incentives:** SIMP (59.51%) is LSIP's main customer (63% of FY2025 revenue). The cash is useful to the group as liquidity; minorities only receive it through dividends or buybacks. This is the structural reason the market credits only part of it.

### 6.3 Value of alternative capital-allocation policies (base, scenario A)

| Policy | Minority value per share (DDM unless stated) |
|---|---|
| Status quo: 30% payout, cash retained at deposit yields | IDR 537 |
| 50% payout | IDR 853 |
| 70% payout | IDR 1,139 |
| 100% payout of profit | IDR 1,521 |
| Intrinsic (DCF + 100% of surplus cash, as if fully distributable) | IDR 2,034 |
| Market price | IDR 1,575 |

The DDM gap (IDR 1,253/share between DCF + surplus cash at 80% credit and the 30%-payout DDM) measures value that exists in the company but does not reach minority holders under the current policy.

## 7. Earnings: near-term catalysts vs structural productivity

### 7.1 Q4 2026 nowcast v2 (EXPLORATORY; v1 preserved)

| Case | Volume vs Q3 | Price vs Q3 | Q3 build released | Fertiliser catch-up | Q4 profit v2 | FY26 profit v2 | Q4 profit v1 (preserved) |
|---|---|---|---|---|---|---|---|
| bear | 0.95x | -8% | 0% | 120 | 293 | 2,038 | 238 |
| base | 1.05x | -3% | 50% | 60 | 534 | 2,279 | 468 |
| bull | 1.15x | +1% | 100% | 20 | 766 | 2,511 | 654 |

v2 changes only two parameters, each tied to new evidence: Q4 is the seasonal peak (Q4'25 nucleus FFB 1.16× Q3'25 — one year of quarterly data, weak evidence) and the November CPO reference price fell ~2% vs the Q3 average. Consensus-implied Q4 is IDR 360bn (FY26 consensus 2,105bn, 5 analysts, S-036). **The Q4 beat, if any, is a timing item** (inventory release and seasonality), not structural.

### 7.2 Forecasts (scenario A, base price case; IDR bn)

| Year | Nucleus FFB kt | CPO IDR/kg | Revenue | EBITDA | Profit | EPS | DPS paid | Capex | FCFF | Cash |
|---|---|---|---|---|---|---|---|---|---|---|
| FY2026E | 1,180 | 15,200 | 5,920 | 2,663 | 2,279 | 334 | 83 | 439 | 1,690 | 9,223 |
| FY2027E | 1,065 | 14,600 | 5,212 | 2,009 | 1,609 | 236 | 100 | 462 | 1,247 | 10,131 |
| FY2028E | 1,050 | 14,300 | 5,045 | 1,797 | 1,470 | 216 | 71 | 480 | 1,022 | 11,046 |
| FY2029E | 1,035 | 14,000 | 4,882 | 1,587 | 1,331 | 195 | 65 | 494 | 845 | 11,856 |
| FY2030E | 1,021 | 14,350 | 4,947 | 1,569 | 1,340 | 196 | 59 | 509 | 800 | 12,690 |
| FY2035E | 976 | 16,236 | 5,387 | 1,539 | 1,425 | 209 | 62 | 590 | 702 | 16,914 |

FY2027E profit: bear 1,109 / base **1,609** / bull 2,061 vs consensus 2,210 (base -27%). Our base is well below consensus because it combines a normalised (cohort-model) production path — FY2026's weather-assisted recovery to ~1,180kt is not extrapolated; FY2027E 1,065kt — with a lower realised price (IDR 14,600/kg vs ~15,300 in 9M26). **This is the main near-term risk to the share price:** consensus FY2027 EPS of 324 looks too high on our numbers. The model has no out-of-sample record; treat the gap as a hypothesis to be tested by FY2026-27 results.

## 8. Integrated model (`outputs/LSIP_model_valuation.xlsx`)

Sheets: Cover, Inputs (blue inputs with sources; selectors for scenario and price case), Cohort (production by scenario from the Python model, including each scenario's steady state), Model (FY2026E-FY2050E income statement, cash flow, balance sheet and balance check; FY2051 steady state), Valuation (FCFF DCF, equity bridge, DDM, multiples, 12-month target and entry price), Historical (audited FY2020-9M26 and operating data). FY2026E reconciles to 9M26 reported profit plus the Q4 v2 base. 1,567 formulas; **0 evaluation errors and a zero balance check in every year under all 12 scenario × price-case combinations**. Limitation: built with openpyxl and verified with the repository's own evaluator (`valuation/xlsx_eval.py`); it has not been recalculated in Excel or LibreOffice (unavailable in this environment), so open it with automatic calculation on. The balance sheet is condensed (cash, working capital, net fixed assets incl. bearer plants, other net assets held at the FY2025 plug, employee benefits, equity); biological assets (produce on trees) are inside working capital, and fair-value changes are not forecast.

## 9. Valuation

Cost of equity 13.1% = 10-year SBN 7.74% (S-052) + 0.9 × 6.0% ERP (no debt; WACC = ke). Valuation date 31 Dec 2026.

| Method (scenario A, base price) | IDR/share |
|---|---|
| 1. FCFF operating DCF + adjusted surplus cash (80% credit) | 1,790 |
| 6. Cash-adjusted operating value: operations only | 812 |
| 3. SOTP: operations 812 + surplus cash at 100% 1,222 − related-party haircut 0 | 2,034 |
| 2. DDM (30% payout) | 537 |
| 4. Relative: P/E FY2027E at current price | 6.7x (palm peers: see `palm_peers_snapshot.csv`; TAPG 9.6x sustainable) |
| 4. Relative: market EV/EBITDA FY2027E (EV ex surplus cash) | 1.6x |
| 4. Relative: EV per planted ha (market) | IDR 67m (TAPG 245m) |
| 5. Reverse DCF | see §10 |

### 9.1 Scenario × price × cash credit (value per share; 12-month return)

| Scenario | Price case | 60% credit | 80% credit | 100% credit |
|---|---|---|---|---|
| A - historical pace | bear | 959 (-32%) | 1,203 (-14%) | 1,447 (3%) |
| A - historical pace | base | 1,545 (10%) | 1,790 (27%) | 2,034 (45%) |
| A - historical pace | bull | 2,247 (60%) | 2,491 (77%) | 2,736 (95%) |
| B - accelerated | bear | 981 (-30%) | 1,225 (-13%) | 1,468 (4%) |
| B - accelerated | base | 1,612 (15%) | 1,855 (32%) | 2,099 (49%) |
| B - accelerated | bull | 2,369 (68%) | 2,613 (86%) | 2,856 (103%) |
| C - deferred | bear | 942 (-33%) | 1,188 (-16%) | 1,433 (2%) |
| C - deferred | base | 1,516 (8%) | 1,761 (25%) | 2,007 (43%) |
| C - deferred | bull | 2,201 (56%) | 2,446 (74%) | 2,692 (91%) |
| D - intensive | bear | 901 (-36%) | 1,142 (-19%) | 1,382 (-2%) |
| D - intensive | base | 1,543 (10%) | 1,783 (27%) | 2,024 (44%) |
| D - intensive | bull | 2,315 (65%) | 2,555 (82%) | 2,796 (99%) |

Price cases (realised CPO, IDR/kg): FY2027 12,500 / 14,600 / 16,500; long-run (FY2029, then +2.5%/yr nominal) 12,000 / 14,000 / 16,500 (ANALYST). Terminal growth 2.5% nominal = 0% real; the terminal value is a small part of value (PV IDR 397bn of an operating EV of 6,301bn).

### 9.2 Sensitivities (scenario A, base price, 80% credit)

| Driver | Value | Value/sh (80% credit unless driver) | DDM/sh | 12m return |
|---|---|---|---|---|
| Long-run CPO IDR/kg | 11000 | 1,047 | 297 | -26% |
| Long-run CPO IDR/kg | 12500 | 1,418 | 417 | 1% |
| Long-run CPO IDR/kg | 14000 | 1,790 | 537 | 27% |
| Long-run CPO IDR/kg | 15500 | 2,161 | 657 | 54% |
| Long-run CPO IDR/kg | 17000 | 2,532 | 776 | 80% |
| FFB yield multiplier | 0.85 | 1,319 | 385 | -6% |
| FFB yield multiplier | 0.9 | 1,476 | 436 | 5% |
| FFB yield multiplier | 1.0 | 1,790 | 537 | 27% |
| FFB yield multiplier | 1.1 | 2,103 | 638 | 50% |
| FFB yield multiplier | 1.15 | 2,260 | 689 | 61% |
| USD/IDR multiplier | 0.9 | 1,379 | 405 | -2% |
| USD/IDR multiplier | 0.95 | 1,584 | 471 | 13% |
| USD/IDR multiplier | 1.0 | 1,790 | 537 | 27% |
| USD/IDR multiplier | 1.05 | 1,995 | 603 | 42% |
| USD/IDR multiplier | 1.1 | 2,200 | 669 | 56% |
| Replant cost IDR m/ha | 70 | 1,872 | 550 | 33% |
| Replant cost IDR m/ha | 85 | 1,831 | 544 | 30% |
| Replant cost IDR m/ha | 100 | 1,790 | 537 | 27% |
| Replant cost IDR m/ha | 120 | 1,735 | 528 | 23% |
| Replant cost IDR m/ha | 140 | 1,680 | 519 | 19% |
| Fertiliser/upkeep multiplier | 0.8 | 1,912 | 576 | 36% |
| Fertiliser/upkeep multiplier | 0.9 | 1,851 | 557 | 32% |
| Fertiliser/upkeep multiplier | 1.0 | 1,790 | 537 | 27% |
| Fertiliser/upkeep multiplier | 1.1 | 1,728 | 518 | 23% |
| Fertiliser/upkeep multiplier | 1.2 | 1,667 | 498 | 19% |
| Beta (ke = 7.74% + b x 6%) | 0.7 | 1,877 | 595 | 32% |
| Beta (ke = 7.74% + b x 6%) | 0.8 | 1,831 | 565 | 30% |
| Beta (ke = 7.74% + b x 6%) | 0.9 | 1,790 | 537 | 27% |
| Beta (ke = 7.74% + b x 6%) | 1.0 | 1,752 | 512 | 25% |
| Beta (ke = 7.74% + b x 6%) | 1.1 | 1,718 | 490 | 23% |
| Cash credit | 0.4 | 1,301 | 537 | -8% |
| Cash credit | 0.6 | 1,545 | 537 | 10% |
| Cash credit | 0.8 | 1,790 | 537 | 27% |
| Cash credit | 1.0 | 2,034 | 537 | 45% |
| Related-party cash haircut | 0.0 | 1,790 | 537 | 27% |
| Related-party cash haircut | 0.5 | 1,751 | 537 | 24% |
| Related-party cash haircut | 1.0 | 1,712 | 537 | 22% |
| Buyback executed IDR bn | 0.0 | 1,790 | 537 | 27% |
| Buyback executed IDR bn | 375.0 | 1,809 | 552 | 29% |
| Buyback executed IDR bn | 750.0 | 1,829 | 568 | 30% |
| Terminal productivity | 0.8 | 1,740 | 520 | 24% |
| Terminal productivity | 0.9 | 1,765 | 528 | 25% |
| Terminal productivity | 1.0 | 1,790 | 537 | 27% |
| Terminal productivity | 1.1 | 1,814 | 546 | 29% |
| Terminal nominal growth | 0.0 | 1,779 | 529 | 26% |
| Terminal nominal growth | 0.01 | 1,782 | 532 | 27% |
| Terminal nominal growth | 0.025 | 1,790 | 537 | 27% |
| Payout (DDM only) | 0.3 | 1,790 | 537 | 27% |
| Payout (DDM only) | 0.5 | 1,790 | 853 | 27% |
| Payout (DDM only) | 0.7 | 1,790 | 1,139 | 27% |
| Payout (DDM only) | 0.9 | 1,790 | 1,400 | 27% |
| Payout (DDM only) | 1.0 | 1,790 | 1,521 | 27% |

The value is most sensitive to the long-run CPO price, FFB yield and the rupiah (each ±10% moves value by IDR 300-400/share), then to cash credit; replanting cost, fertiliser intensity, ke and terminal productivity matter far less.

## 10. Reverse valuation: what the price implies

At IDR 1,575 (scenario A unless stated):
- **Long-run realised CPO price:** IDR 12,145/kg with 100% cash credit, IDR 13,133/kg at 80% (base 14,000; FY2025 realised ~14,600; 9M26 ~15,300).
- **Cash realisation:** 62% of surplus cash at our base operations; at bear operations the price needs 110% credit — i.e. the market is either pricing a bear commodity case with full cash credit or a base case with a governance discount.
- **Sustainable FFB yield:** a -7% change to the cohort path (k ≈ 0.62) — i.e. a further decline in productivity.
- **Replanting cost:** IDR 178m/ha (base 100) or fertiliser/upkeep intensity 1.35× base — implausible on their own.
- **Cost of equity:** 17.6% (beta 1.65).
- **Payout:** the DDM reaches the price only at a 105% payout of profit.

**Is the discount justified?** Partly. The market's discount relative to TAPG (IDR 67m vs 245m EV per planted ha) is larger than the operating gap (operating profit per mature ha 23.7m vs 28.3m). The ageing estate explains part of it (age-mix yield deficit 9% vs a 25-year steady state; a 10% yield change is worth IDR 314/share gross), but correcting it costs nearly what it earns. The larger, persistent component is minority access to cash.

Historical valuation dispersion (year-end; DERIVED):

| fy | price_ye | mcap_bn | pe | pb | cash_pct_mcap | ev_ex_cash_bn | ev_over_np_ex_interest |
|---|---|---|---|---|---|---|---|
| 2020 | 1,375 | 9,377 | 13.48 | 1.01 | 0.21 | 7,419 | 11.33 |
| 2021 | 1,185 | 8,082 | 8.16 | 0.79 | 0.42 | 4,714 | 5.00 |
| 2022 | 1,015 | 6,922 | 6.69 | 0.63 | 0.56 | 3,075 | 3.17 |
| 2023 | 890 | 6,070 | 7.98 | 0.53 | 0.74 | 1,558 | 2.45 |
| 2024 | 975 | 6,649 | 4.51 | 0.53 | 0.82 | 1,196 | 0.92 |
| 2025 | 1,195 | 8,150 | 4.32 | 0.58 | 0.93 | 552 | 0.33 |
| current | 1,575 | 10,741 | 5.10 | 0.71 | 0.79 | 2,225 |  |

## 11. LSIP versus TAPG (like-for-like; FY2025)

| Metric (FY2025 unless stated) | LSIP | TAPG |
|---|---|---|
| Planted oil palm ha | 90,798 | 132,814 |
| Mature ha | 84,744 | 125,201 |
| Share >20 years | 41% | 3% |
| FFB yield t/ha | 13.4 | 24.3 |
| OER | 21.7% | 23.3% |
| Revenue IDR bn | 5,512 | 11,402 |
| Operating margin | 36% | 31% |
| ROIC (NOPAT / equity ex cash) | 23% | 28% |
| FCF IDR bn | 2,582 | 2,809 |
| Dividends / FCF | 17% | 117% |
| Cash IDR bn | 7,597 | 1,651 |
| Sustainable replant ha/yr (25y) | 3,632 | 5,313 |
| EV per planted ha IDR m (market) | 52-67 | 245 |
| Operating profit per mature ha IDR m | 23.7 | 28.3 |
| Price (25 Nov 2026) | 1,575 | 1,720 |
| Value bear/base/bull (same price deck) | 1,203 / 1,790 / 2,491 | 1,059 / 1,440 / 1,916 |
| 12m total return bear/base/bull | -14% / 27% / 77% | -31% / -6% / 25% |
| Volatility (5y daily, annualised) | 32% | 39% |
| Base return / volatility | 0.84 | -0.16 |
| Max drawdown since 2015 (TAPG since 2021 listing) | -70% | -38% |
| Market beta / sector beta (5y weekly, HAC) | 0.82 / 0.99 | 0.55 / 0.93 |
| Market-implied long-run realised CPO | 12,145 (100% cash) / 13,133 (80%) | 15,469 |

Definitions: LSIP operating data are nucleus; TAPG's are group-wide incl. associates (TAPG's own scope), so TAPG yield and age shares are not strictly like-for-like. ROIC uses book equity less cash, which flatters LSIP's old, depreciated estate. TAPG's value uses a single-stage perpetuity on a 6-point profit-on-price regression (R² 0.94) with a 10% ageing haircut and 90% cash conversion (`valuation/lsip_tapg_compare.py`); it is a price-deck consistency check, not a TAPG target price.

**Is TAPG's premium justified?** By plantation economics, largely yes: TAPG has a prime-age estate (87% aged 7-20 years), 24.3 t/ha yields and pays out more than its free cash flow. By price, no: at IDR 1,720 TAPG capitalises about IDR 4,278bn of sustainable profit (FY2025: 3,702bn), so its base return on our price deck is -6%. Of LSIP's discount, the age mix accounts for roughly a third of the yield gap and little of the value gap; the rest is productivity and capital allocation.

## 12. Quantitative risk and entry

| Metric | LSIP | TAPG |
|---|---|---|
| Annualised volatility, 5y / 1y | 32% / 40% | 39% / 52% |
| Max drawdown (date) | -70% (2020-03-19) | -38% (2023-06-05) |
| Monthly return 5th / 1st percentile (2016+) | -15% / -20% | -10% / -18% |
| Worst 12 months; share of negative 12m windows | -41%; 49% | -19%; 25% |
| Market beta (t), sector beta (t), weekly 5y HAC | 0.82 (5.7), 0.99 (9.1) | 0.55 (3.8), 0.93 (9.5) |
| CPO beta (monthly, IDR CPO, controlling for IHSG) (t) | 0.48 (3.5) | 0.23 (1.3) |
| Liquidity: median daily value 6m | IDR 11.9bn (p10 6.1bn) | see Phase I |
| Weekly return correlation LSIP-TAPG | 0.61 | |

Price reactions around dated events (market-adjusted, descriptive, n = 9):

| event | date | day0 | car_0_1 | car_0_5 | car_0_20 |
|---|---|---|---|---|---|
| FY2024 results | 2025-02-28 | 2025-03-03 | 4.1% | 8.8% | 10.3% |
| H1 2025 results | 2025-07-31 | 2025-08-01 | -2.9% | -4.9% | -8.7% |
| FY2025 results | 2026-02-27 | 2026-03-02 | 11.6% | 23.4% | 39.1% |
| Q1 2026 highlights | 2026-04-30 | 2026-05-04 | -8.1% | -10.8% | -17.8% |
| H1 2026 results | 2026-07-31 | 2026-08-03 | 0.4% | -0.7% | 6.6% |
| Buyback disclosure | 2026-10-23 | 2026-10-26 | 4.2% | 4.1% | 13.1% |
| 9M 2026 results | 2026-10-30 | 2026-11-02 | 3.7% | 6.1% |  |
| Ex-dividend FY2024 | 2025-07-01 | 2025-07-01 | 7.0% | 6.0% | 0.6% |
| Ex-dividend FY2025 | 2026-07-06 | 2026-07-06 | -1.2% | 1.8% | 9.3% |

**Hurdle (open item A6 / D-030).** The 17.5% hurdle was set as ke 12.5% + 5pp when the 10y SBN yielded ~6.2%; it now yields 7.74%, so an unchanged hurdle implies an ERP of only 4.8%. We **propose** restating it as ke + 5pp = 18.1% (A-049, documented separately; not adopted here). The recommendation is the same under both.

**Entry (valuation-based, not statistically validated):** base value at 80% credit → IDR 1,706; base value robust to a 60% credit → **IDR 1,473** at 17.5% (IDR 1,465 at 18.1%). We do not estimate a probability of reaching the target price.

**Stop-loss (risk-budget-based, not quantitatively validated):** for a position sized at a 1% portfolio risk budget, a review/exit level ~25% below entry corresponds to a 4% position (LSIP's 5th-percentile monthly return is -15%; the 2020 drawdown was -70%). Thesis-based exits (§13) take precedence over price-based ones.

## 13. Recommendation detail

- **Rating: HOLD / WATCH.** Base fair value IDR 1,790 (bear 1,203, bull 2,491); 12-month target IDR 1,904; expected dividend IDR 100 (6.4%); expected total return 27% in the base case but only 12% if the market's current cash discount persists, and -32% in the joint downside (bear CPO, 60% credit).
- **Why not BUY now:** (1) the return depends on a governance outcome minorities cannot influence (cash credit ≥ 69%); (2) our FY2027E profit is -27% vs consensus — negative revisions are more likely than positive; (3) the ageing/productivity trend is down (k 0.80 → 0.66) and disclosure of the age profile has stopped; (4) buyback execution is unverified.
- **Why not SELL:** the bear case with 80-100% cash credit is IDR 1,203-1,447, close to the price; surplus cash is 64% of the market value; and LSIP ranks above TAPG on risk-adjusted expected return.
- **Take-profit framework:** trim above IDR 1,790 (base value, 80% credit); exit above IDR 2,034 (base value with full cash credit) unless payout policy has changed.
- **Risk management:** treat LSIP and TAPG as one palm risk bucket (correlation 0.61, sector beta ~1); liquidity caps a position at roughly 20% of ~IDR 11.9bn daily value.
- **Position sizing (hypothetical diversified IDR equity portfolio):** 0% now; up to 2-3% at ≤ IDR 1,473; up to 4% after verified capital return. No investor-specific sizing.
- **Upgrade to BUY if:** price ≤ IDR 1,473; or an IDX report shows ≥ IDR 375bn of buyback executed; or the FY2026 payout (AGM ~Jun 2027) is ≥ 50% or includes a special dividend; or LSIP publishes an age profile and replanting plan consistent with scenario B.
- **Downgrade / thesis invalidation:** payout below 30% or new related-party placements raising Bank Ina Perdana above 20% of cash; cash used for a related-party acquisition; FY2026 nucleus FFB below 1,130kt or 9M27 yields below FY2025 levels with fertiliser restored (productivity decline is structural); long-run CPO expectations below IDR 12,000/kg.

## 14. Catalysts (Exhibit 13)

| Date (expected) | Event | What would change |
|---|---|---|
| 31 Dec 2026 | Buyback window closes | Execution size and price |
| Early Jan 2027 | IDX buyback report (C-019) | Evidence of capital return |
| ~26 Feb 2027 | FY2026 results (C-020) | Q4 vs 360bn consensus-implied; inventory release |
| ~30 Apr 2027 | AR/SR 2026 | Whether an age profile / replanting plan is disclosed |
| ~Jun 2027 | AGM payout (C-021) | Payout ≥ 50% would move the cash credit |
| Jul-Oct 2027 | H1 / 9M 2027 | El Niño lag on FFB; fertiliser normalisation |

## 15. Data gaps, assumptions and uncertainties

| Area | Gap / assumption | Effect |
|---|---|---|
| Age profile FY2024-26 | Not disclosed; reconstructed | Cohort model starting state |
| Replanting hectares, targets, capex | Not disclosed; reconstructed from bands and immature additions | Historical rate ±~50 ha/yr across the ensemble; cost per ha calibrated (IDR 100m/ha, ANALYST) |
| Yield by age | Not disclosed; standard curve × k (ANALYST) | Production path; tested by the decline and k ensemble |
| Fertiliser | Combined with upkeep in the COGS note | Catch-up hypothesis unverifiable |
| Estate-level productivity | Regional area only | No estate ranking for scenario D |
| Land changes | Oil palm −1,467 ha in 9M26; reasons undisclosed | Treated as disposal of the oldest area |
| Buyback execution | Unverified | Base assumes 0 executed |
| Consensus | Forward snapshots only (from 24 Nov 2026); 5 analysts | No historical expectations analysis |
| Financial statements FY2018-19 | Only five-year highlights (ARs before 2021 not on the company site) | History table starts FY2020 for full statements |
| Workbook | No Excel/LibreOffice recalculation; independent evaluator only | Open with automatic calculation |
| TAPG valuation | Simple perpetuity, regression n = 6, group-wide scope | Relative comparison only |
| Models | No out-of-sample validation of the LSIP earnings model or Q4 nowcast | Treat forecasts as hypotheses |

Integrity: ITMG C1/I1 prospective runs and all registered experiments are untouched (`tests/test_phase17.py` checks the frozen files); no factor mining; R2/R3 not run; previous LSIP files preserved.

_Sources: S-002, S-036, S-046–S-052, S-076–S-078 (data/SOURCE_REGISTER.csv); assumptions A-049–A-057 (context/ASSUMPTIONS.md); decision D-047._
