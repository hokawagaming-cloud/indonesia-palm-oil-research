# Phase X — MVP-B1 Banking Predictive Earnings Validation (BBCA, BBRI)

_Date: 2026-11-25._

_Code: `quant/bank_extract.py` (data), `quant/bank_mvp_b1.py` (evaluation); tests in `tests/test_bank_mvp_b1.py`._

_Specification: `MVP_B1_preregistration.json`, **committed as 6fe91e3 before any model was run**. The data-layer completion was committed as 6a82b78, also before any performance was computed. The spec was not changed afterwards._

_Decision: D-034. Palm oil decisions and CPIN H2 are unchanged._

**Three kinds of evidence are kept separate:**
1. **Software tests** check that code is correct.
2. **Forecast accuracy** is measured in this memo.
3. **Trading alpha** is not tested (see §5).

> ## Result
> - **BBCA: NO-GO.**
> - **BBRI: NO-GO.**
>
> Monthly bank-only disclosures did **not** produce a ≥ 15%, statistically supported improvement in forecasting **quarterly consolidated profit attributable to owners** over the strongest information-matched benchmark, for either bank. For **net interest income** (secondary target), the public monthly data are highly informative, but the pre-registered model adds nothing beyond a simple run-rate rule.

## 1. Data acquired and verified

| | BBCA | BBRI |
|---|---|---|
| Monthly bank-only reports (2018–2026) | 81 (S-063) | 82 incl. revised and audited versions; 81 originals used (S-062) |
| Quarterly publications (bank-only + consolidated) | 29. **No own publication for 2019Q4, 2020Q1, 2020Q4, 2021Q1, 2021Q2, 2024Q4**; those quarters come from next year's prior-period column, dated to that document | 35, complete |
| Publication-date evidence | Filename date prefix 2020+ (56 monthly). The CMS `order_date` is **not** a publication date (it often equals the period end). Pre-2020 dates are unverified. | IR posting date for every report |
| Integrity checks | NII = interest income − expense: 100%. Net profit < PBT: 100%. Monthly quarter-end vs quarterly bank-only: **7/7 match** | NII identity 100%; NP < PBT 100%. Monthly vs quarterly: **9/11** (Jun-2019 and Jun-2020 monthly figures were revised in the quarterly publications) |
| Provenance issues found | API links point to the wrong month (Sep-2017 → Nov file; Jul-2019 → Jun file); a filename typo (`20280229`) | Template year error in a header (Feb-2026); restated 2021 comparatives after the Pegadaian/PNM common-control acquisition (pro forma) |

**Extracted fields** (`bank_monthly_extract.csv`, `bank_quarterly_extract.csv`):
- **Profit and loss:** interest income and expense, NII, impairment, operating profit, PBT and net profit. Pre-provision operating profit = operating profit + impairment (derived).
- **Balance sheet:** loans, current accounts, savings and time deposits (CASA derivable).
- **Quarterly publications:** each item for bank-only and consolidated; profit attributable to owners; NPL gross (where found).
- **Not extracted:** earning assets and coverage ratios are not consistently labelled across layouts. Credit cost can be derived (impairment ÷ loans).
- **Scope rule:** bank-only and consolidated values are never mixed. Consolidated figures are reached only through the explicit consolidation adjustment Adj = consolidated − bank-only.

## 2. Point-in-time design

- **Forecast origin:** the **verified** publication date of month 2 of each quarter (Feb, May, Aug, Nov).
- **Information set:** reports with availability ≤ origin, original vintages only.
- **Exclusions from the primary sample (BBCA):**
  - 2022Q1: the February-2022 date is unverified.
  - 2021Q2 and 2021Q3: the previous quarter-end bank-only figure exists only as a 2022 comparative.
- **Common evaluation sample:** quarters where every benchmark is defined. **BBCA n = 15** (below the 16 required); **BBRI n = 23**.
- **Conservative-date sensitivity:** identical results for both banks. The information sets did not change.

## 3. Walk-forward results (IDR bn, standalone quarter; full tables in `MVP_B1_metrics.csv`)

### Primary target T1: consolidated profit attributable to owners

**BBCA** (n = 15)

| Method | MAE | RMSE | Bias | Directional accuracy (YoY) | M1 MAE improvement vs this method |
|---|---|---|---|---|---|
| **M1 (pre-registered component model)** | **1,117** | 1,563 | −557 | 0.80 | — |
| IM1 (2 months × 1.5 + latest adjustment): best IM | 719 | 980 | −110 | 0.93 | **−55%** |
| IM4 (seasonal run-rate) | 738 | 896 | −325 | 0.87 | −51% |
| U1 (last quarter): best unconditional | **560** | 666 | −396 | 0.93 | −99% |
| U4 (AR(1)) | 607 | 700 | −183 | 0.93 | −84% |

- M1 vs best IM: MAE ratio 90% CI [1.07, 2.02]; DM t −1.81; Holm-adjusted p = 1.0.
- **Information value (best IM vs best unconditional): −28%**, i.e. the monthly-based benchmarks are *worse* than "last quarter".

**BBRI** (n = 23)

| Method | MAE | RMSE | Bias | Directional accuracy | M1 improvement |
|---|---|---|---|---|---|
| **M1** | **1,391** | 1,933 | −1,130 | 0.74 | — |
| IM1: best IM | 1,555 | 2,124 | −1,092 | 0.65 | **+10.6%** |
| U1: best unconditional | 1,462 | 1,833 | −534 | 0.78 | +4.8% |

- M1 vs best IM: ratio CI [0.72, 1.09]; DM t 0.73; Holm-adjusted p = 0.24.
- **Pass rule failed:** the improvement is below 15% and not significant.
- Information value: −6%.

### Secondary target T2: consolidated NII

| | M1 MAE | Best IM (MAE) | Best unconditional (MAE) | M1 vs best IM | **Information value (best IM vs best unconditional)** |
|---|---|---|---|---|---|
| BBCA (n 15) | 169 | IM4 (129) | U1 (546) | −31% (DM p 0.93) | **−76% error, DM t 3.76, p = 0.001** |
| BBRI (n 23) | 1,677 | IM1 (1,941) | U1 (2,814) | +14% (Holm p 0.39) | **−31% error, DM t 2.37, p = 0.013** |

### Robustness and diagnostics

- **Sensitivity (BBCA, 2024Q4 added under the same comparative rule; my enumeration in the spec had omitted it):**
  - n = 16.
  - T1: M1 is −49% vs the best IM. Pass rule still fails.
  - T2: information value −76% (p 0.001).
  - Conclusion unchanged (`MVP_B1_sensitivity_BBCA_2024Q4.json`).
- **Regimes (descriptive, T1 MAE, M1 vs IM1):**
  - BBCA: M1 is better only in R1 (3 quarters) and R4 (3 quarters).
  - BBRI: M1 is better in R1, R3 and R4 and worse in R2 (2022Q3–2023Q4, the BI hiking cycle).
  - Not stable across monetary regimes (`MVP_B1_regimes.csv`).
- **Cross-bank dependence:** the correlation of M1 T1 errors is 0.28 over 19 common quarters. Results are not pooled.
- **Post-hoc error decomposition (descriptive only; best-IM-style rule):**
  - **Consolidation-adjustment errors exceed bank-only errors**: BBCA 887 vs 631bn; BBRI 1,376 vs 1,150bn.
  - The adjustment swings seasonally. For BBCA, bank-only profit exceeds consolidated in Q1 by up to 1.5tn, consistent with subsidiary dividends booked as bank-only income and eliminated on consolidation.
  - BBRI's third month averages **38.5%** of the quarter (BBCA 31.7%). Quarter-end provisioning and accruals make "×1.5" biased low (−943bn).

## 4. Attribution: where any improvement comes from

| | Additional public information (best IM vs best unconditional) | Superior model (M1 vs best IM) |
|---|---|---|
| T1 profit, BBCA | **None** (−28%) | **None** (−55%) |
| T1 profit, BBRI | **None** (−6%) | Small, insignificant (+10.6%, p 0.24) |
| T2 NII, BBCA | **Large and significant** (−76%, p 0.001) | None (−31%) |
| T2 NII, BBRI | **Significant** (−31%, p 0.013) | Small, insignificant (+14%) |

**Interpretation:**
- Two months of bank-only data pin down **NII** well, because NII accrues smoothly.
- For **profit**, the third month (quarter-end provisions, tax true-ups, accruals) and the **consolidation adjustment** (subsidiaries, dividend eliminations, minorities) dominate the error. Neither is observable in the monthly reports.
- The NII information is public, press-covered within about a day and mechanical to use. It is **not** evidence of alpha.

## 5. Investment relevance

- **Precondition not met:** predictive accuracy on the primary target was not demonstrated, so the event study is **designed but not executed** (`MVP_B1_event_study_design.json`).
- **Design:** events are monthly releases. Abnormal returns are measured against an equal-weight large-bank index and IHSG, over CAR[0,+1] and drift windows [+2,+10] up to the quarterly result. It covers consensus revisions (forward only), costs (0.45% round trip, EST), HAC or bootstrap inference, Holm across windows and ≥ 40 events per bank.
- **No BUY, no valuation model, no trading system.**

## 6. Decision (D-034)

| Bank | Classification | Reason |
|---|---|---|
| **BBCA** | **NO-GO** | T1 pass rule fails (n 15 < 16; M1 −55% vs best IM). Monthly-based benchmarks do not beat "last quarter" for profit. |
| **BBRI** | **NO-GO** | T1 improvement +10.6% < 15%, Holm p 0.24. Consolidation complexity (subsidiary share) dominates. |

The pre-registered CONDITIONAL GO route (a) is evaluated on the primary target T1 (as implemented before results) and is not met. The **T2 information-value result** is recorded as a descriptive finding only. Pursuing it would require a **new, separately registered** NII nowcast hypothesis evaluated prospectively. Even then it would be a forecasting result, not alpha.

**Preserved:**
- All forecasts (`MVP_B1_forecasts_primary.csv`, `MVP_B1_forecasts_conservative.csv`).
- Metrics, regimes and sensitivity outputs.
- The unsuccessful model, unchanged.
- No BMRI or BBNI expansion.

_Sources: S-062 (BRI IR), S-063 (BCA IR incl. report-list API), S-060 (IDX mirror), S-002 (prices, design only)._
