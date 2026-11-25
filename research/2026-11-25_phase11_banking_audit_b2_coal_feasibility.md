# Phase XI — Banking Audit, MVP-B2 Registration and Coal Feasibility

_Date: 2026-11-25._

_Code: `quant/bank_audit_b1.py`. Outputs: `MVP_B1_audit*.{json,csv}`, `MVP_B1_results_corrected.json`, `MVP_B2_preregistration.json`, `MVP_B2_economic_relevance.json`, `coal_feasibility.csv`._

_Decisions: D-035 (audit), D-036 (MVP-B2), D-037 (coal)._

**Unchanged:** MVP-B1 NO-GO, the original outputs, palm oil NO TRADE, CPIN H2 frozen.

**Three kinds of evidence are kept separate:** software tests; forecasting accuracy (historical = discovery, prospective = confirmation); trading alpha (not tested).

---

## Workstream 1 — Final banking data audit (MVP-B1 originals preserved)

| Check | Finding | Consequence |
|---|---|---|
| **(a) `abs()` on impairment** | 5 documents had negative raw impairment. **2 BBRI** cases (Jul and Aug 2020) are a sign convention: all expense lines are in parentheses, including salaries. **3 BBCA** cases (Jan-2022, Jan-2023, Feb-2023) are **genuine net reversals** ("ADDITION (REVERSAL) OF IMPAIRMENT … (184,162)"), and `abs()` wrongly turned them into expenses. Negative standalone monthly impairments from YTD differences (8 months) were never affected. | **Error confirmed** (limited). Corrected extract `bank_monthly_extract_v2.csv`, rerun in `MVP_B1_results_corrected.json`: BBCA T1 M1 improves from −55% to **−41%** vs best IM and **still fails**. BBRI is unchanged. Classifications unchanged. |
| **(b) PBT used as operating profit** | Used in 37 BBCA documents whose layout has no non-operating section. In **37/37**, NII + net non-interest operational result = PBT **exactly** (gap 0). | Substitution **supported** by accounting reconciliation. |
| **(c) Filename / IR timestamps** | Internet Archive check, sample of 40. **BCA's PDF host (pustaka.bca.co.id) is not archived** (0/20), so its filename dates cannot be independently confirmed. BBRI: 16/20 archived; **0 captures before the claimed date**; 3 within 0–2 days (independent confirmation); the rest months later (uninformative). | BBRI dates are consistent with independent evidence. BBCA filename dates are **unconfirmed but not contradicted**; one known prefix error exists (Mar-2022 quarterly file `20210421`). **BBCA's PIT status is downgraded to "plausible, unconfirmed".** |
| **(d) Multiplicity of the NII result** | The original claim compared the *best* of 4 IM rules with the *best* of 4 unconditional rules, both chosen ex post. Re-tested all 16 pairs per bank with Holm, then Bonferroni ×4 (2 banks × 2 targets). Against the strongest relevant benchmark (U1, last quarter): **BBCA IM4 p = 0.042 (survives)**, BBCA IM1 p = 0.087 (does not); **BBRI best (IM1) p = 0.38 (does not survive)**. Pairs against the trending expanding mean are trivially significant and uninformative. | The NII information value is **robust only for BBCA**, and only marginally. **BBRI's p = 0.013 was an artefact of selection.** |

## Workstream 2 — MVP-B2 (frozen prospective NII hypothesis)

**Registered specification** (`MVP_B2_preregistration.json`):
- **Formula:** consolidated NII forecast = **1.5 × bank-only NII for months 1–2 + latest consolidation adjustment**. This is IM1, the simplest information-matched rule, fixed for **both** banks. There is no bank-specific selection, and IM4 is deliberately *not* used, even though it was best for BBCA in sample.
- **Inputs:** fixed as specified.
- **Origin:** the verified month-2 publication date. Each forecast is **journaled before the quarterly result**.
- **Benchmarks:** last quarter, same quarter last year, AR(1).
- **Kill at n = 8:** if MAE ≥ the best benchmark.
- **Pass at n = 12:** MAE ≤ 0.85 × **each** benchmark **and** Holm-adjusted DM p ≤ 0.05.
- **Timing:** first quarter 2026Q4 (BBCA's November report is expected mid-December 2026). The **final verdict comes no earlier than 2029Q3**.
- **Status of historical results:** MVP-B1's T2 results are recorded as **discovery evidence only**.

**Economic relevance (descriptive; `MVP_B2_economic_relevance.json`):**

| | NII / net profit (last 4 quarters) | Profit elasticity to NII (×(1−tax)) | Median NII error: run-rate vs last quarter | Implied profit error from NII alone |
|---|---|---|---|---|
| BBCA | 1.46× | 1.19 | 1.1% vs 2.4% | 1.3% vs 2.9% |
| BBRI | 2.48× | 1.94 | 2.5% vs 4.9% | 4.9% vs 9.5% |

**What this means:**
- For BBRI, NII leverage on profit is high, but the profit error is dominated by provisions and consolidation (MVP-B1).
- An NII nowcast removes only part of the profit uncertainty.
- Whether consensus or prices already reflect the monthly NII cannot be measured historically (no consensus history). Forward consensus logs for the four banks started on 2026-11-24.
- **No alpha claim and no BUY.**

## Workstream 3 — Coal feasibility (tested; `coal_feasibility.csv`)

| Dataset | ITMG | PTBA |
|---|---|---|
| Realised ASP, volumes, strip ratio, fuel price, cost and royalty lines | **AVAILABLE**: analyst presentations 1Q18–3Q26 (35/35 quarters, HTTP 200, PDF content verified on 1Q18 and 3Q26) | **PARTIAL**: the company site hosts no quarterly FS or presentations (API: announcements, AGM documents and 63 disclosures only). History needs manual IDX download (Cloudflare). |
| Quarterly consolidated FS | **AVAILABLE** 2018–2026 (one file under another name) | Manual IDX |
| IDX filing timestamps | Aug-2023+ (mirror) | Oct-2024+ (mirror) |
| Newcastle benchmark | **AVAILABLE** (World Bank CMO "Coal, Australian", monthly 1970–2026) | same |
| ICI (Indonesian Coal Index) | **NOT AVAILABLE** (Argus/Coalindo subscription) | same |
| HBA (ESDM reference price) | **NOT VERIFIED** (minerba.esdm.go.id under maintenance); regime changes 2023, 2025 | same |
| DMO, price caps, royalty regimes | Document-based (Kepmen / PP); **not yet compiled** | same; PTBA is far more exposed (PLN domestic sales) |
| Calorific value / product mix | Partial (CV ranges by mine) | not tested |
| Rainfall at mines | CHIRPS infrastructure exists, but **mine coordinates not yet verified** from IUP / annual-report documents | same |
| Analyst expectations | Snapshot only (6/14 analysts FY26/27) | Snapshot only (13/14) |
| Liquidity (60-day median traded value) | IDR 38bn/day | IDR 107bn/day |

## Workstream 4 — Economic hypotheses (specified, not tested)

| # | Target | Mechanism | Information at forecast time | Benchmarks (information-matched first) | Key confounders |
|---|---|---|---|---|---|
| C1 | **ITMG export ASP** (quarterly) | Index-linked contracts priced off GC Newcastle / ICI with ~1-month lag, plus fixed-price tonnage; mix by CV | Newcastle monthly up to quarter end (CMO, published early the next month); prior-quarter ASP | **Last ASP × (Newcastle quarterly change)** (price-scaled naive, already using the commodity signal); last ASP | ICI unavailable (the true reference for lower CV); CV mix shifts; contract-type mix; DMO tonnage at the cap |
| C2 | Sales / production volumes | Rainfall disrupts hauling and barging; company FY guidance | CHIRPS at verified pits; guidance | Guidance ÷ 4; seasonal | Mine coordinates unverified; river levels; barge logistics |
| C3 | Unit cash cost | Strip ratio × fuel use; fuel price; royalty = rate(HBA/ASP) × ASP | Brent, company fuel price, guidance strip ratio, royalty regime | Last unit cost; last × fuel change | Annual strip-ratio guidance only; regime changes (PP 26/2022, PP 19/2025) |
| C4 | Gross profit / EBITDA | C1 × volume − C3 | as above | Last quarter; price-scaled naive | Compounding errors |
| C5 | Earnings revisions | Gap between a C4 nowcast and consensus | **No consensus history** | — | Forward logs only |

**Domestic vs export pricing:**
- The DMO share (~25%) sold to power at the USD 70/t cap is **regulated and must be modelled separately** from export pricing.
- PTBA's large PLN share makes its ASP structurally less index-driven.
- **Caution:** a high correlation between ASP and Newcastle is expected and **is not incremental information**. The test is whether contract-lag and mix modelling beats the price-scaled naive rule.

## Decision gate (D-037)

| Criterion | ITMG | PTBA |
|---|---|---|
| Historical completeness | **High** (35 quarters of KPIs + FS) | Low (manual IDX needed) |
| PIT reliability | Medium (IDX timestamps 2023+; earlier at deadlines) | Low–medium |
| Usable out-of-sample quarters (walk-forward from ~2021) | ≈ 20 | n/a |
| Accounting / regime consistency | Breaks: 2021–22 price spike, DMO cap, royalty regimes 2022 and 2025 | Same, plus heavier regulated exposure |
| Collection cost | Low–moderate (≈ 35 presentations, ≈ 3 MB each, scriptable) | High (manual) |
| Potential information advantage | **Low.** Newcastle is public daily; any edge would come from modelling lags and mix, not from data access. | Lower |

### Recommendation

- **ITMG: CONDITIONAL GO** for one narrow pre-registered experiment, **C1 (export ASP nowcast)**. Conditions:
  1. User approval to download about 35 ITMG presentations (and the FS) from itmg.co.id.
  2. A regime table for DMO, royalty and HBA compiled from official decrees before registration.
  3. The pre-registration must make the **price-scaled naive rule** the benchmark to beat, with the same ≥ 15% / n ≥ 16 / Holm rule.
  4. No volume or cost hypotheses until C1 passes.
- **PTBA: NO-GO for now.** The site has no quarterly history, IDX needs manual download, and regulated domestic pricing dominates.
- **Expectation:** given the CPIN and banking outcomes, a **pass is not the base case**. The experiment is worth running only because ITMG data is cheap and clean.
- **No valuation model or trading system.** ITMG and PTBA are added to the forward consensus snapshots.

_Sources:_
- _S-003 World Bank CMO_
- _S-060 jejaksaham mirror_
- _S-062 / S-063 bank IR sites_
- _S-066 ITMG IR_
- _S-067 PTBA IR API_
- _S-068 Argus/Coalindo ICI (subscription)_
- _S-069 Minerba ESDM HBA (unavailable)_
- _S-070 Internet Archive CDX_
