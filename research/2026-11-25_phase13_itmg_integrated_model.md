# Phase XIII — ITMG Integrated Predictive Operating Model

_Date: 2026-11-25._

_Code: `quant/itmg_c1_prospective.py`, `quant/itmg_ops_extract.py`, `quant/itmg_c2c3.py`, `quant/itmg_i1.py`; tests in `tests/test_phase13.py`._

_Specifications (each committed before its evaluation): C2/C3 `ITMG_C2_C3_preregistration.json` (205218e); integrated `ITMG_I1_preregistration.json` (8692b9a). C1 is frozen as evaluated (cb64a27)._

_Decisions: D-039 (C1 audit and freeze), D-040 (C2/C3), D-041 (I1). Palm oil NO TRADE, CPIN H2, MVP-B2 and all prior forecasts are unchanged._

**Three kinds of evidence are kept separate:** software tests (64 pass); forecasting accuracy (historical walk-forward); trading alpha (not tested).

> ## Summary
>
> | Experiment | Result | Classification |
> |---|---|---|
> | **C1 (ASP)** | Timing audit passed. Robust to delayed data. Survives programme-wide Holm across 16 tests (p 0.012). | **Frozen; prospective from 2026Q4** |
> | **C2 (sales volume)** | Best model +18% vs seasonal, p 0.50 | **NO-GO** |
> | **C3 (unit cost)** | Best model +6% vs last quarter, p 0.54 | **NO-GO** |
> | **I1 (integrated gross profit)** | C1 price + benchmark volume and cost beats the same structure without C1 by **19%** (p 0.034) and last-quarter GP by 32%. **Not significant programme-wide** (Holm p 0.51). | **CONDITIONAL GO**, prospective confirmation required |
>
> No alpha claim and no BUY.

## Workstream 1 — C1 freeze and audit (original results preserved)

**Publication dates of World Bank Newcastle prices:**
- Internet Archive vintages of `CMO-Historical-Data-Monthly.xlsx` (2026) show:
  - **June 2026 data present by 10 Jul 07:04 UTC** (exactly D+10 after the quarter end).
  - **September data present by 15 Oct.**
  - **October data by 4 Nov.**
  - January data by 9 Feb.
- Pink Sheet cover dates (e.g. 2 Dec 2025, 4 Mar 2025, 4 May 2026) are consistent with an early-month release.
- **The D+10 origin is supported, but tight.** Pre-2026 vintages were not checked (the URL code changes each year).

**Data available at D+10:**
- Newcastle data for the quarter's last month: available in the evidence above.
- ITMG's previous-quarter deck: published 39–57 days after that quarter's end, i.e. well before the next origin.

**Revision risk:** across six 2026 vintages, the maximum revision to 2018+ Newcastle values is **USD 0.05/t** (`CMO_newcastle_vintages.csv`). Negligible.

**Coefficient stability:** b0 ≈ 0.52, b1 ≈ 0.22, pass-through ≈ 0.74, stable since 2023 (Phase XII).

**Delayed-availability sensitivity (report-only):** if each quarter's third month were unavailable at the origin, M2 is still **−39% vs the strongest benchmark (Holm p 0.009)** (`ITMG_C1_sensitivity_delayed_month3.json`).

**Programme-wide multiplicity** (`programme_multiplicity_v2.csv`, 16 tests across CPIN, banking and ITMG):

| Test | Holm p | Bonferroni p |
|---|---|---|
| C1-M2 | **0.012** | 0.012 |
| Every other test except I1 | 1.0 | 1.0 |
| I1 | 0.51 | 0.55 |

**Freeze and prospective procedure:**
- `quant/itmg_c1_prospective.py` reads the CMO file **as downloaded on the origin date** (hashing it) and re-estimates M2 on the expanding window with the frozen procedure.
- The **2026Q4 forecast is made on 10 Jan 2027**. If December is not yet published, the forecast is made on the first day it is, flagged `late_origin`.
- The forecast is **resolved by ITMG's 4Q26 release (~late Feb 2027), not on the forecast date.**
- A dry run today correctly returns `late_origin`, because December 2026 is not yet published.

## Workstream 2 — C2 sales volume (NO-GO)

**Data:**
- **Target:** sales volume = FS coal revenue ÷ first-reported ASP. It reconciles to deck-reported sales within **0.4% median, 1.1% max** (8 quarters).
- **Guidance:** sales guidance extracted for **all 35 decks**, with page provenance. Types: FY range midpoints, plus the recent quarterly ("1Q26: 6.8 Mt") and half-year ("6M26: 12.8 Mt") forms. The deck of quarter q−1 is used for forecasting q.
- **Excluded (data quality):**
  - Production volume: automated extraction confuses mine-level and total figures.
  - Strip ratio: chart-only.
  - Mine rainfall: **coordinates not verified**; decks show regions only, so no satellite rainfall was used.
  - RKAB quotas and disruptions: text-only.
  - The production-to-sales benchmark: not testable, because it needs the production series.

**Results** (2022Q1–2026Q3, n = 19; Mt):

| Method | MAE | Bias |
|---|---|---|
| Seasonal (strongest) | 0.49 | −0.29 |
| Last quarter | 0.60 | −0.06 |
| Guidance run-rate | 0.79 | **+0.78** (guidance is optimistic) |
| M1 guidance with seasonal allocation | 0.59 | +0.58 |
| **M2 guidance regression** | **0.41** | +0.08 |

M2 is +18% vs seasonal, but Holm p = 0.50 and the 90% CI is [0.57, 1.29]. **It fails the rule.**

## Workstream 3 — C3 unit cost (NO-GO)

**Data:**
- **Source:** FS cost-of-revenue note, all 35 quarters. The missing **9M25 FS was found under a different file name and hashed**.
- **Lines:** mining costs, royalty, coal purchases, transport, fuel, salaries, inventory change.
- **Target:** (cost of revenue − royalty) ÷ sales volume. Purchased coal and inventory change are included on a sold-tonne basis, so numerator and denominator are consistent. Royalty is excluded to avoid double-counting.
- **Definitional breaks noted:**
  - 2018 had a separate fuel line.
  - The 2020Q3 fuel line is negative (reclassification).
  - Transport roughly halves from 2023 (reclassification).
  - These are inside the total, so the target is unaffected.

**Royalty** (descriptive): the effective rate is ≈ 12% (2018–21), 14–16% (2022–23), and ≈ 11–12% (2024–26). This is consistent with CCOW 13.5% of revenue net of deductions, plus period-specific effects. Per-entity regime detail is in `coal_regulatory_regimes.csv`, with verification levels.

**Results** (n = 19; USD/t):

| Method | MAE |
|---|---|
| Last quarter (strongest) | 5.03 |
| Brent-scaled | 5.98 |
| M1 commodity regression | 5.16 |
| **M2 component scaling** | **4.71** (+6%, Holm p 0.54) |

**Fails.**

## Workstream 5 — Integrated gross profit (I1)

**Design:**
- **Components:** the validated component only (C1-M2 ASP), with benchmarks for the failed ones: seasonal volume, last-quarter unit cost, and last-quarter royalty rate. No actual future volumes or costs are used.
- **Target:** quarterly gross profit on a coal-revenue basis (FS).
- **Narrowed scope:** EBITDA, operating profit and net profit to owners are **not** tested (D&A, SG&A, other income and tax not extracted).

**Results** (2021Q2–2026Q3, n = 22; USD m):

| Method | MAE | RMSE | Bias | Directional accuracy |
|---|---|---|---|---|
| **I1** | **49.2** | 69.0 | +4.1 | 0.82 |
| G3: same structure without C1 (strongest) | 60.8 | 84.1 | +7.1 | 0.77 |
| G1: last-quarter GP | 72.1 | 97.7 | −4.0 | 0.00 |
| G4: expanding mean | 121.1 | — | — | — |
| G2: seasonal | 161.0 | — | — | — |

- I1 vs G3: **−19%**, DM t 1.92, p 0.034, CI [0.68, 0.94]. The pre-registered pass rule is met, and **C1 translates into GP forecasting**.
- **Joint uncertainty:** I1's 10–90% error band is −59 to +95 USD m against a median GP of 162 USD m. Wide.
- **Classification: CONDITIONAL GO.**
  - I1 does not survive programme-wide Holm (p 0.51).
  - I1 is not independent of C1.
  - Prospective confirmation is required.

## Workstream 6 — Investment relevance (designed, not executed)

`ITMG_ES1_event_study_design.json`:
- **Gap:** I1 nowcast vs consensus-implied quarter.
- **Revisions:** analyst revisions after results.
- **Returns:** factor-adjusted CARs, with IHSG, coal peers ex-self and Newcastle as factors. Windows are pre-results, announcement and post (+2..+20 days).
- **Costs:** 0.45% round trip.
- **Inference:** Holm across windows; ≥ 12 events.
- **Preconditions:** prospective confirmation of C1/I1, and ≥ 8 quarters of forward consensus snapshots (no historical consensus exists).

## Next steps

| When | What |
|---|---|
| **10 Jan 2027** | C1 and I1 prospective forecasts for 2026Q4 (journal rows) |
| ~late Feb 2027 | Resolution at ITMG's 4Q26 release |

C2 and C3 are stopped. Retrospective respecification is not allowed. The excluded data (production, strip ratio, rainfall with verified coordinates) could support a **new** registration only after manual, verified transcription. No ITMG valuation, no BUY.

_Sources:_
- _S-066 ITMG IR (69 documents + 9M25 FS; SHA-256)_
- _S-003 World Bank CMO (with Internet Archive vintages, S-070)_
- _S-071 regulations_
- _[World Bank Pink Sheet](https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/world-bank-commodities-price-data-the-pink-sheet)_

---

## Clarification (Phase XIV audit, 2026-11-25)

**Only the June 2026 archive (10 Jul 07:04 UTC) shows World Bank data available at D+10.**
- The September archive shows availability by **15 Oct (D+15), not D+10**.
- The Oct/Jan observations are not quarter ends.
- D+10 availability is therefore **not proven for every historical quarter**.

The delayed-month sensitivity (−39%, Holm p 0.009) is maintained as the conservative case and is now the operational fallback (D-043). Classifications are unchanged.
