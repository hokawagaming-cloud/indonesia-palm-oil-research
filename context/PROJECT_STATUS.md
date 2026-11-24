# Project Status

_Last updated: 2026-11-24_

## Current phase

**Phase II — round 2: quarterly operational data, levy/duty reconstruction, exploratory Q4 2026 nowcast.** No investment analysis, rankings or ratings have been produced. Nothing in the nowcast is validated.

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

- [ ] **User action:** download TAPG investor newsletters (Vol 15–24) in a browser (host unreachable from here, S-033). They date quarterly ops originally and add sales/ASP/cost history.
- [ ] Check for analyst forecasts revised after 29 Oct 2026, and the share-price reaction, before any surprise claim (D-013).
- [ ] Integrate the levy/duty schedule into the domestic-discount model; recompute the ASP ÷ world-price analysis net of levy and duty.
- [ ] Verify A-013 deadlines against POJK text (now needed only for filings without timestamps).
- [ ] Decide D-004; cross-check Yahoo prices; repeat Phase I/II for the other 14 names.

## Blockers

- Every primary source for company filings is blocked from this environment (IDX 403, tap-agri.com unreachable, financialfilings bot wall). They need a manual download or an approved account.
- No long, free, downloadable daily domestic CPO series exists among the sources tested.
