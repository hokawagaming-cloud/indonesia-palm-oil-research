# Project Status

_Last updated: 2026-11-24_

## Current phase

**Phase V — Predictive alpha discovery and monitoring (started 2026-11-24).** Decision: **NO TRADE** (D-022, D-025).
- **TAPG:** WATCH / NO BUY; entry trigger ≈ IDR 1,525 (D-024).
- **LSIP:** selected for deeper research only.
- **Monitoring:** run `quant/tapg_monitor.py` after refreshing prices, macro data and levy/duty.

## Done

- [x] Workspace set up; universe confirmed (D-002); methodology finalised (D-003).
- [x] Daily OHLCV for 25 palm tickers plus IHSG, USD/IDR and Brent (S-002); PIT universe built.
- [x] Source register: 24 sources, each with a verification status.
- [x] **TAPG gap resolution** (`research/company/TAPG/2026-11-24_data_gap_resolution.md`):
  - Financial statements: partial, from Yahoo (S-020). FY2021–FY2025 and Q1'25–Q3'26, but Q3'25 is missing. A = L + E passes for all periods. No filing dates.
  - Dividends received from JVs/associates: FY2022–FY2025 annual, plus quarterly from Q2'25.
  - Corporate actions: 10 cash dividends (ex-dates 2022–2026).
  - Domestic CPO (KPBN tender, secondary via S-023): only Aug–Nov 2026.
- [x] CHIRPS v3.0 monthly rainfall for 8 palm provinces, 2015-01 to 2026-10, no gaps (S-007). Regional proxy, not TAPG estates.
- [x] Quant modules (have enough data):
  - `quant/ohlcv_quality.py` → `data/reference/ohlcv_quality.csv`
  - `quant/benchmarks.py` → `data/reference/benchmarks_daily.csv` (IHSG and EW core PIT, 2016 onward)
  - `quant/fetch_company_fundamentals.py` (fundamentals and corporate actions with integrity checks)
  - `quant/fetch_chirps.py` (regional rainfall)
  - `tests/test_benchmarks.py` (3 tests, passing)

- [x] **TAPG official documents** (AR2021–AR2025 and Q1/H1/9M 2026 interims, supplied by the user):
  - `quant/pdf_to_text.py`: per-page text with citations.
  - `quant/extract_tapg_statements.py`: 372 audited and interim statement points; all identities PASS.
  - `quant/extract_tapg_highlights.py`: multi-year highlight tables, reconciled across reports.
  - `quant/tapg_operational_dataset.py`: 208 operational, cost and JV points; 41/41 checks PASS.
  - `quant/tapg_quarterly.py`: discrete quarters 2025Q1–2026Q3, by subtraction.
  - `quant/reconcile_yahoo_tapg.py`: Yahoo matches official on 36/36 overlapping values.
  - Findings: FY2022 equity typo in the AR highlights; FY2022 finance-line reclassification; production is reported incl. associates while sales are consolidated; USTP JV is ~99% of JV profit and ~23% of FY2025 PBT.

- [x] **Phase II (2026-11-24):**
  - PDFs untracked from Git and all local copies kept (D-007); the PDFs remain in Git history. Manifest: `data/reference/document_manifest.csv`.
  - Extracted: USTP standalone FY2020–25 (ties exactly to TAPG's 50% share); JV dividends incl. the FY2025 in-kind dividend of IDR 414bn (explains the declared vs cash gap); capex by asset class FY2020–25; nucleus FFB by region FY2019–25; COGS FY2020–22 incl. purchased FFB; subsidiary/estate table.
  - Scope-separated datasets with a mixed-scope guard (D-008); USTP valuation-input module (no valuation yet).
  - Disclosure-date table with evidence vs assumption labels (D-009, A-012/A-013).
  - Preliminary quant: relative performance, rolling beta, CPO sensitivity, residual momentum, drawdowns, lead-lag (`quant_prelim_results.md`).
  - Nowcast feasibility (`nowcast_feasibility.md`): feasible in structure, blocked on G1/G12 (D-010).
  - Tests: 11 passing.

- [x] **Phase II round 2 (2026-11-24):**
  - Quarterly ops 3Q24–3Q26 (S-028/S-029). Group-wide scope verified: FY2025 quarterly sums = AR2025.
  - Consolidated sales/ASP/fertiliser for 3Q26/9M26 only.
  - Public Expose FY2025 (IDX, S-032) gives the FY2021–25 subsidiary/associate split, which closes G11 annually.
  - Q1 2026 revision found and kept both ways (D-011). Broker definitional conflicts documented (D-012).
  - IDX disclosure timestamps for H1 2023 to 9M 2026 via the S-027 mirror (A-018); G7 largely closed.
  - Exploratory Q4 2026 scenarios (D-013): `research/company/TAPG/q4_2026_nowcast.md`.
  - Levy/duty reconstruction: see `research/macro/2026-11-24_levy_duty_reconstruction.md`.
  - Notes: `research/company/TAPG/2026-11-24_quarterly_operational_extraction.md`.

- [x] **Audit remediation (2026-11-24):**
  - Levy/duty regimes from primary PMK texts plus 116 HRef periods (S-034/S-035), with 7 tests.
  - Netback: the Nov charge cut offsets 98% of the HRef fall on the reference basis, but KPBN tenders still fell 3.8%.
  - PIT vintage panel with regression tests (D-014).
  - Product-level inventory model; Q4 profit bear/base/bull 882/1,268/1,651bn (D-015).
  - Dated expectations: Yahoo FY26 EPS 212.9, implying Q4 ~720bn (D-016).
  - Event study: no immediate 9M26 reaction, then −13% to −15% CAR by 24 Nov.
  - DSNG check: `research/challengers/2026-11-24_dsng_inventory_check.md`.
  - Tests: 26 passing.

- [x] **Phase III (2026-11-24):**
  - Astra files reconciled (D-019): DSNG 23→52kt inventory VERIFIED; S&P snapshot verified and deduplicated.
  - Strict AR vintage rule (D-017).
  - Q4 joint downside: no combination without an extreme driver reaches the consensus-implied 720bn; all drivers stressed gives ≈ 728bn. Base revised to 1,209bn (D-018).
  - FY27 model: base 4,062bn vs consensus 4,473bn.
  - Reverse valuation: the price implies ≈ 4.1tn sustainable profit.
  - PIT validation n = 2 (exploratory); forecast journal (25 entries; one superseded record later restored, D-023); catalyst register (9 entries).
  - DSNG assessment: catalyst already in consensus.
  - IC memo. Tests: 30 passing.

- [x] **Phase IV (2026-11-24):**
  - Sell-off diagnosis: not sector-wide; commodity headwind on thin liquidity plus name-specific FY27 concerns.
  - EPS basis reconciled (reported, D-021).
  - STAA assessment.
  - Tactical Q4 beat not supported (n = 8).
  - TAPG entry range: probability-weighted return +5% at 1,710.
  - Three-name uniform scorecard. Journal 31 rows (append-only, D-023); catalysts 14. Tests 31 passing.

- [x] **Phase V (2026-11-24):**
  - Fertiliser prices added (WB urea/DAP/MOP).
  - TAPG monitor plus forward consensus history for 17 names (first snapshot).
  - Forward dividend capacity and weight uncertainty: expected return +4.8%, P(> hurdle) ≈ 2%.
  - Expectation-adjusted surprise framework (`quant/surprise_study.py`) with a test.
  - Universe screen: consensus covers 8 of 17 names; consensus-implied Q4 is weak across LSIP, TAPG and AALI; LSIP selected for research.
  - Journal 32 rows; catalysts 18. Tests 32 passing.

## Not resolved (sources tried and failed)

| Need | Tried | Why it failed |
|---|---|---|
| TAPG AR2023, AR2024, SR2025 | admin-web.tap-agri.com (S-021) | Host refuses connections from this environment |
| TAPG AR2025, 9M2026, filing history | financialfilings.com (S-022) | Bot wall; needs an API account signup |
| Operational metrics (FFB yield, mature ha, OER, production, ASP, unit cost) | — | Only available in annual reports and IDX releases |
| JV / associate earnings (equity method) | S-020 | Not reported by Yahoo |
| Earnings announcement dates | S-020 | None returned for TAPG.JK |
| Long domestic CPO history | KPBN (reCAPTCHA), IPOSS (account), MPOB (subscription), infokomoditas (~3.5 months) | See the register |
| Free float, palm-revenue share (all 15 names) | IDX | 403 to scripts |

## Next

- [ ] **LSIP deeper research (C-016):** fetch the 9M26 FS; explain the Q3 gross-profit jump; verify net cash; payout policy and parent context; cash-adjusted valuation; expectations gap.
- [ ] Run `tapg_monitor.py` on each data refresh (December HRef decree, monthly WB prices, consensus). Re-evaluate when the trigger hits or assumptions change.
- [ ] FY2026 results (~Feb–Mar 2027): first expectation-adjusted surprise test across names (C-017); resolve the forecast journal.
- [ ] Map name-level ENSO exposure from primary sources (estate provinces) before using rainfall as a cross-sectional indicator.
- [ ] Standing gaps: original-vintage TAPG interims and newsletters (S-033), fertiliser application levels, foreign-flow data, STAA refinery capacity.

## Blockers

- Every primary source for company filings is blocked from this environment (IDX 403, tap-agri.com unreachable, financialfilings bot wall). They need a manual download or an approved account.
- No long, free, downloadable daily domestic CPO series exists among the sources tested.
