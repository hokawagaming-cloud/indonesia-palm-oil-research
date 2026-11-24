# TAPG — Phase II: Fundamental Data Completion (summary)

_Date: 2026-11-24 · No investment rating · All figures extracted from the supplied documents (S-021, S-025) unless marked DERIVED_

## Priority 1 — Extraction from existing documents

| Item | Result | Coverage | Validation | File |
|---|---|---|---|---|
| USTP standalone financials (100% basis) | **Done:** net sales, profit, current and non-current assets and liabilities, NCI, net assets, TCI | Sales and profit FY2020–25; net assets FY2023–25 (not printed earlier) | USTP profit × 50% = TAPG's share of USTP profit, **exactly, FY2021–25** | `TAPG_scope_jv.csv`, `USTP_history.csv` |
| JV earnings and dividends | **Done:** TAPG share, declared dividends, carrying value FY2021–25; cash received FY2020–25 and by quarter 2025–26 | FY2020–2026Q3 | See next row | `TAPG_scope_jv.csv`, `TAPG_quarterly_derived.csv` |
| Dividend receivables and timing | **Resolved:** the FY2025 gap of IDR 401bn between declared (1,373.0bn) and cash (958.8bn) is a **non-cash dividend of IDR 414.2bn received as marketable securities** (note 42, AR2025 p355). Cash + in-kind = declared exactly. No dividend receivable is disclosed. | FY2021–25 | PASS | `TAPG_phase2_checks.csv` |
| Capex split | **Done** at asset-class level (accrual additions, note 12). **Mills are not separately disclosed** (A-015). | FY2020–25 | Class additions = total additions, 10/10 PASS | `TAPG_scope_consolidated.csv` (`fa_additions_*`) |
| FFB production by region (nucleus) | **Done:** Sumatra, Central Kalimantan, East Kalimantan | FY2019–25 | Regions sum to total, 15/15 PASS | `TAPG_scope_groupwide.csv` |
| Cost breakdown FY2020–21 | **Done** (old presentation: upkeep, harvesting, indirect, depreciation, **purchased FFB**, processing). Purchased FFB = IDR 1,641.5bn / 2,357.6bn / 2,851.4bn (FY20/21/22). FY2023+ uses a coarser presentation that bundles purchased FFB with materials. | FY2020–22 (old), FY2022–25 (new) | Components sum to totals, PASS | `TAPG_scope_consolidated.csv` |
| Estate locations and geographic exposure | **Partial:** 29 subsidiaries with business line, total assets, status and reported location (AR2025 p81–83). Several operating estates show only their **Jakarta registered office**. Area and FFB tables give province-level exposure (Jambi/Sumatra, Central and East Kalimantan). No coordinates. | FY2025 | — | `TAPG_estates.csv` |
| Maturity and replanting schedule | **Partial:** age profile and mature/immature area FY2021–25 (round 3). Replanting is described **only qualitatively** (an East Kalimantan programme; a 4-year-old replant yielding 25.38 t/ha). **No forward replanting schedule in hectares.** The year-on-year change in >20-year area is provided as a DERIVED indicator, not a disclosed replanting figure. | FY2021–25 | — | `TAPG_scope_groupwide.csv` (`derived_*`) |

**USTP snapshot (IDR bn, 100% basis):** FY2025 sales 4,962.4, profit 2,119.5 (net margin 42.7%), net assets 5,224.6. Dividends to TAPG were 128% of TAPG's share of USTP profit in FY2025 and 131% in FY2024, so USTP has been returning more than it earns, and its net assets fell from 6,369bn to 5,225bn over FY2023–25.

**Capex FY2025 additions (IDR bn, 647.9 total):**

| Bucket | IDR bn |
|---|---|
| Plantation (immature oil palm 105.9, immature rubber 6.4, nursery 14.6, land 18.2) | 145.1 |
| Construction in progress (unallocated) | 305.4 |
| Vehicles and heavy equipment | 81.9 |
| Buildings and infrastructure | 54.1 |
| Machinery and installations | 38.8 |
| Equipment and furniture | 22.5 |

**Nucleus FFB by region (kt, group-wide):**

| Region | FY2021 | FY2025 |
|---|---|---|
| Central Kalimantan | 1,723 | 1,810 |
| East Kalimantan | 849 | 1,143 |
| Sumatra | 68 | 87 |

Group-wide FFB, yield (20.3 → 24.5 t/ha) and CPO output (850 → 999 kt) all stepped up sharply in FY2022 on near-flat planted area. Later reports repeat the same figures, so it is not a restatement, but the definitions should be confirmed before modelling yield trends.

## Priority 2 — Reporting scope (D-008)

- **Datasets:** `TAPG_scope_consolidated.csv` (529 rows), `TAPG_scope_jv.csv` (88), `TAPG_scope_groupwide.csv` (230).
- **Guard:** `quant/tapg_scope.ratio()` raises `ScopeError` on any cross-scope ratio (tested).
- **USTP module:** `valuation/ustp_module.py` provides the history plus P/E, P/B and DDM look-through functions. Every input is `None` until assumptions are documented, so the module produces **no valuation** yet.
- **Consequence:** consolidated FFB yield, unit cash cost per tonne and consolidated OER **cannot be computed**. The consolidated share of group-wide volumes is not disclosed (gap G11).

## Priority 3 — Publication dates (D-009, A-012, A-013)

- `data/reference/TAPG_disclosure_dates.csv` lists every disclosure with its document date, press evidence, assumed deadline, `available_from` and basis.
- **6 disclosures have dated press evidence:** FY2024 (2025-02-28), Q1 2024, H1 2024, H1 2025, 9M 2025 and Q1 2026 (2026-04-28). The rest are **ASSUMPTION**-based.
- **No exact IDX timestamps were found**, so nothing is claimed as verified point-in-time.
- Quarterly derived data now carries `available_from` and its basis.

## Priority 4 — Preliminary quantitative research

Results are in `research/company/TAPG/quant_prelim_results.md`. These are descriptive associations only:

- **Relative performance:** TAPG's total return since listing is +1,093%, against IHSG −11.9% (price index) and peers EW +33.9%. The April 2021 listing (from IDR 270, five daily limit-up sessions) and IDR 631 per share of dividends dominate.
- **Market factor:** daily beta to IHSG is 0.77 but R² is only 0.09. Once the peer factor is added, IHSG beta falls to 0.14 (t 1.5) and peer beta is 0.82 (t 12): the sector factor matters more than the market.
- **CPO sensitivity:** the monthly regression on the World Bank CPO change has coefficient 0.15 (NW t 1.1, n = 66), which is not distinguishable from zero. The monthly-average price series weakens this test.
- **Lead-lag:** the largest correlations are at k = −1 (TAPG leads the monthly-average CPO). That is consistent with averaging mechanics, not with TAPG predicting CPO. 5 of 56 correlations fall outside ±2 s.e., against about 3 expected by chance.
- **Residual momentum:** TAPG's latest score is +1.31. The cross-sectional IC is +0.04 (t 0.9) across about 7.5 names per month, which is noise-level.
- **Drawdowns:** TAPG's maximum is −38% (Mar 2022 → Jun 2023, recovered Aug 2024). IHSG fell −46% in 2026 YTD on S-002 data, which still needs an official cross-check.

## Priority 5 — Nowcasting feasibility

Results are in `research/company/TAPG/nowcast_feasibility.md`.

- **Domestic discount:** realised CPO ASP ÷ world price (IDR) ranged from 0.57 to 0.86 over FY2020–25 and moves with levy and duty policy. A constant discount is not acceptable.
- **Naive price-scaled benchmarks:**

| Benchmark | Revenue mean abs error | n | Gross profit mean abs error |
|---|---|---|---|
| Same quarter last year, price-scaled | 9.7% | 3 | 17% |
| Last quarter, price-scaled | 18.5% | 6 | 35% |

- **Verdict:** the structure is feasible, but without quarterly volumes (G1) and the levy/duty schedule the error is too large and too poorly measured. No accuracy is claimed.

## Remaining gaps (updated)

| # | Gap | Status |
|---|---|---|
| G1 | Quarterly production and sales volumes | **Open.** Blocks the nowcast. Press coverage quotes Q1 2026 FFB of about 698 kt, so a quarterly company disclosure exists somewhere. |
| G2 | Unit cash cost | **Open.** Also blocked by G11. |
| G3 | USTP financials | **Closed.** Operations (hectares, production) are still not disclosed. |
| G4 | Capex split | **Closed at class level.** Mills not separable. |
| G5 | FFB by region | **Closed.** Age profile before FY2021 still open (IPO prospectus). |
| G6 | COGS FY2020–21 | **Closed.** |
| G7 | IDX timestamps | **Open.** Mitigated by A-012 evidence where available. |
| G8 | Sustainability Report 2025 | **Open.** |
| G9 | Estate coordinates | **Open.** Only province-level and registered offices. |
| G10 | Long KPBN CPO history | **Open.** |
| G11 | **New:** consolidated vs group-wide volume split | **Open.** Needed for consolidated yields and unit costs. |
| G12 | **New:** levy and duty schedule table (S-010/S-011) | **Open.** Needed to model the domestic discount. |
