# Phase XII — ITMG Predictive Operating Model Pilot (ITMG-C1: realised ASP nowcast)

_Date: 2026-11-25._

_Code: `quant/itmg_extract.py`, `quant/itmg_c1.py`; tests in `tests/test_itmg_c1.py`._

_Specification: `ITMG_C1_preregistration.json`, **committed cb64a27 before any model or benchmark error was computed**. Decision: D-038._

**Three kinds of evidence are kept separate:** software tests; forecasting accuracy (this memo: historical walk-forward, now also tracked prospectively); trading alpha (not tested; not claimed).

> ## Result: **GO under the pre-registered rule, for ASP forecasting only**
> **M2 (distributed-lag Newcastle pass-through)** reduces the nowcast error of ITMG's first-reported blended ASP by **40%** against the strongest benchmark (last ASP × Newcastle change): MAE **USD 6.38/t vs 10.71/t**, n = 22, Holm p = 0.002, 90% CI of the error ratio [0.42, 0.71].
>
> It is economically material: ≈ USD 4.3/t, or 4.5% of ASP, ≈ USD 27m revenue and ≈ USD 23m EBITDA forecast error per quarter.
>
> This is **not** a claim of earnings predictability or alpha.

## 1. Data and verification

- **Documents:** 35 analyst presentations (1Q18–3Q26) and 34 quarterly consolidated FS (9M25 not on the site under the standard name), all from itmg.co.id. 247 MB, git-ignored; **SHA-256 for every file** in `ITMG_document_manifest.csv`.
- **Target:** "ITM ASP" is the **blended** realised price (footnote: includes post-shipment adjustments and traded coal).
  - **Export-only ASP is not consistently disclosed**, so it is *not* the target. The domestic (Indonesia) share of sales from the destination charts is used as a covariate (M4).
  - Values are first-reported, from each quarter's own deck, with page provenance (`ITMG_quarterly_raw_extract.csv`). Where a deck printed both a rounded chart label and a precise text value, the precise text value was used (e.g. 2020Q3: $48.8 vs $49).
- **Revisions confirmed:** later decks restate ASP (post-shipment adjustments), e.g. 2024Q2 94.0 → 95.8, 2025Q1 81.0 → 81.7. First-reported values are used for both targets and lags.
- **Publication timing:** ITMG files results **39–57 days after quarter end** (IDX timestamps 2023Q2+). The forecast origin (quarter end + 10 days) always precedes the release, and the previous quarter is always published before the origin.
- **Not extracted consistently:** per-quarter sales volumes before 2023Q4, calorific mix, export ASP, strip ratio and fuel series (printed as charts with varying layouts). Volumes for the economic translation use the median of verified deck values (6.2 Mt/quarter).
- **Newcastle benchmark:** World Bank CMO "Coal, Australian" (monthly). A single vintage was downloaded on 2026-11-24, so historical revisions cannot be ruled out. ICI and HBA are unavailable; the hypothesis was explicitly narrowed to measurable variables.

## 2. Regulatory reconstruction (`data/reference/coal_regulatory_regimes.csv`)

Each row records its verification level: primary JDIH link found / secondary (official release or press) / knowledge-only.

| Area | Key instruments |
|---|---|
| DMO quota | 25% DMO (2018 onward: Kepmen 23 K/30/MEM/2018; continued by Kepmen 255.K/2020 and 139.K/2021) |
| Domestic price cap | USD 70/t (GAR 6,322) for public power plants, or HBA if lower. Kepmen 1395 K/30/MEM/2018, effective **12 Mar 2018** (Kepmen 1410); amended 1925 K/2018; continued by 255.K/2020 and 139.K/2021. |
| Royalties | PKP2B 13.5% (contractual) → IUPK progressive (PP 15/2022, revised by PP 18/2025). IUP: PP 81/2019 → PP 26/2022 (HBA-linked progressive) → **PP 19/2025** (effective 26 Apr 2025, higher tiers). |
| HBA | Kepmen 41.K/2023 (27 Feb 2023) → revoked by 227.K/2023 (11 Aug 2023) → **72.K/2025: HBA mandatory export floor from 1 Mar 2025** → revoked by **268.K/2025 (8 Aug 2025)**, which allows contract prices, with royalties on HPB. |

**Reference vs realised prices:**
- HBA and HPB are regulatory reference prices for royalties and floors. They are **not** ITMG's realised selling price.
- No regime dummies were added to the models (pre-registration). The table explains residual risk, e.g. the Mar–Aug 2025 HBA-floor episode and the PP 19/2025 royalty step-up.

## 3. Walk-forward results (USD/t; 2021Q2–2026Q3, n = 22; `ITMG_C1_metrics.csv`)

| Method | MAE | RMSE | Bias | OOS R² vs mean | OOS R² vs strongest | Directional accuracy | Improvement vs strongest |
|---|---|---|---|---|---|---|---|
| B1 last ASP | 14.06 | 20.62 | −1.2 | 0.85 | −1.10 | 0.00 | −31% |
| B2 same quarter last year | 46.77 | 61.64 | −5.0 | −0.38 | — | 0.32 | — |
| B3 expanding mean | 35.31 | 52.40 | −21.3 | 0 | — | 0.46 | — |
| **B4 last ASP × Newcastle change (strongest)** | **10.71** | 14.22 | +1.5 | 0.93 | 0 | 0.82 | — |
| B5 rolling discount | 14.64 | 20.76 | +6.5 | 0.84 | −1.13 | 0.82 | −37% |
| B6 lagged Newcastle regression | 18.31 | 29.81 | +10.9 | 0.68 | −3.39 | 0.64 | −71% |
| M1 fixed one-month lag | 10.05 | 15.41 | +3.1 | 0.91 | −0.18 | 0.73 | +6% (Holm p 0.48) ✗ |
| **M2 distributed lag** | **6.38** | **10.62** | +0.9 | **0.96** | **0.44** | **0.86** | **+40% (Holm p 0.002)** ✓ |
| M4 domestic/export decomposition | 9.15 | 11.23 | +7.1 | 0.95 | 0.38 | 0.77 | +15% (Holm p 0.48) ✗ |

- **Not testable:** M3 (product-mix-adjusted), because calorific mix is not consistently disclosed (registered as not testable).
- **Regimes (MAE):**

| Regime | M2 | B4 |
|---|---|---|
| Price spike (2021Q2–2022Q4, n = 7) | 13.9 | 18.4 |
| Normalisation (2023Q1–2026Q3, n = 15) | **2.9** | 7.1 |

  The gain is not driven by the spike.
- **Coefficient stability** (`ITMG_C1_M2_coefficients.csv`):
  - Immediate Newcastle elasticity b0 is about 0.52 (range 0.49–0.57).
  - The one-quarter lag b1 is about 0.22 (range 0.12–0.32).
  - Total pass-through is about 0.74, stable from 2023.
  - This is economically consistent with partly fixed or annually priced tonnage (e.g. the JPU reference contract) plus lagged index pricing.

## 4. Economic significance

| | Value |
|---|---|
| MAE reduction vs strongest benchmark | USD 4.33/t (4.5% of the median test ASP of $96.4/t), which meets the pre-registered ≥ 2% threshold |
| × median verified sales volume (6.2 Mt/quarter) | ≈ USD 27m quarterly revenue forecast error avoided |
| × (1 − 13.5% royalty approximation) | ≈ USD 23m quarterly EBITDA forecast error avoided |

**Limits:**
- These are reductions in *forecast error*, not profits.
- Volumes, unit costs and royalties also drive earnings and are not forecast here.
- Newcastle is public daily data, and sell-side analysts can apply similar pass-through rules.
- There is **no historical consensus**, so whether market expectations lag this information is untested. Forward consensus logging for ITMG started on 2026-11-24.

## 5. Decision (D-038) and caveats

**Classification: GO** under the pre-registered rule (pass, material, bootstrap CI upper bound < 1). Scope: **ASP nowcasting only.**

**Caveats recorded:**
1. This is a historical walk-forward on 22 quarters of one company. Although pre-registered, the lag structure (0–1 quarters) was chosen with general domain knowledge, and the ASP/benchmark history had been seen during extraction.
2. The CMO vintage may revise.
3. The blended target mixes export and domestic tonnage.

**Prospective tracking (append-only journal):**
- The ITMG 2026Q4 M2 forecast and the B4 benchmark will be computed at the origin, **10 Jan 2027**, once December CMO prices are published.
- The result resolves with ITMG's FY2026 release (~late Feb 2027).
- A prospective record (≥ 8 quarters) is required before any use beyond research.

**Proposed next experiment** (separate pre-registration, not started): **ITMG-C2/C3, volume and unit cost.**
- **C2:** quarterly sales volume vs guidance ÷ 4 and seasonal benchmarks, using CHIRPS rainfall at **verified** pit coordinates (from IUP or annual-report maps) and the prior-quarter production/sales gap.
- **C3:** unit cash cost ex-royalty vs last-quarter and fuel-scaled benchmarks, using company fuel price, guidance strip ratio and Brent with a fixed 1-quarter lag.
- **Prerequisites:** per-quarter volumes, strip ratio and fuel from FS notes or decks (the extraction must be completed and reconciled to FS revenue), and verified mine coordinates.
- **Pass rule:** the same ≥ 15% / n ≥ 16 / Holm rule.

**No ITMG valuation and no BUY.** Palm oil NO TRADE, CPIN H2 and MVP-B2 are unchanged.

_Sources:_
- _S-066 ITMG IR (documents + SHA-256)_
- _S-003 World Bank CMO_
- _S-060 jejaksaham IDX mirror_
- _S-071 JDIH ESDM / ESDM releases and press, as listed in `coal_regulatory_regimes.csv`_
