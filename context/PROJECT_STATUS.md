# Project Status

_Last updated: 2026-11-24_

## Current phase

**Phase I — Data Availability Audit, gap resolution round 2.** TAPG modelling has **not** started: its operational data is not yet available. No investment analysis or rankings have been produced.

## Done

- [x] Workspace set up; universe confirmed (D-002); methodology finalised (D-003).
- [x] Daily OHLCV for 25 palm tickers plus IHSG, USD/IDR and Brent (S-002); PIT universe built.
- [x] Source register: 24 sources, each with a verification status.
- [x] **TAPG gap resolution** (`research/company/TAPG/2026-11-24_data_gap_resolution.md`):
  - Financial statements: partial, from Yahoo (S-020). FY2021–FY2025 and Q1'25–Q3'26, but Q3'25 is missing. A = L + E passes for all periods. No filing dates.
  - Dividends received from JVs/associates: FY2022–FY2025 annual, plus quarterly from Q2'25.
  - Corporate actions: 10 cash dividends (ex-dates 2022–2026).
  - Domestic CPO (KPBN tender, secondary via S-023): only Aug–Nov 2026.
- [x] CHIRPS v3.0 monthly rainfall for 8 palm provinces (S-007); details in the Phase I notes.
- [x] Quant modules (have enough data):
  - `quant/ohlcv_quality.py` → `data/reference/ohlcv_quality.csv`
  - `quant/benchmarks.py` → `data/reference/benchmarks_daily.csv` (IHSG and EW core PIT, 2016 onward)
  - `quant/fetch_company_fundamentals.py` (fundamentals and corporate actions with integrity checks)
  - `quant/fetch_chirps.py` (regional rainfall)
  - `tests/test_benchmarks.py` (3 tests, passing)

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

- [ ] **User action:** download the TAPG PDFs (AR2023, AR2024, SR2025, AR2025, 9M2026) in a browser into `data/raw/company/TAPG/`. Or approve an account: financialfilings API, IPOSS access, or a vendor connector via `/mcp`.
- [ ] Once the PDFs are in place: extract operating metrics, JV earnings, filing dates and estate locations (to replace the A-009 rainfall boxes).
- [ ] **Decide D-004** (re-tiering on verified liquidity).
- [ ] Cross-check Yahoo prices against an official source. Flags: IHSG fell 39% in 2026 YTD on S-002 (8,647 → 5,242), and some liquid names show zero-volume days that IHSG doesn't.
- [ ] Compile the levy, duty and biodiesel regulation tables (S-010–S-012).
- [ ] Next quant step with existing data: rainfall-lag and ENSO features (S-006/S-007) and the CPO monthly driver panel (S-003).

## Blockers

- Every primary source for company filings is blocked from this environment (IDX 403, tap-agri.com unreachable, financialfilings bot wall). They need a manual download or an approved account.
- No long, free, downloadable daily domestic CPO series exists among the sources tested.
