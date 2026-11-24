# TAPG — Phase I Data Gap Resolution

_Date: 2026-11-24 · Scope: data for TAPG modelling plus macro inputs · Source IDs refer to `data/SOURCE_REGISTER.csv`_

A dataset counts as **resolved** only if it was downloaded, parsed, checked and is usable. "Reachable" (the site loads) is never enough.

## Summary

| # | Dataset | Status | Source (class) | Coverage | Frequency | Publication dates? | Missing | Validation | Local path |
|---|---|---|---|---|---|---|---|---|---|
| 1a | TAPG annual reports 2023, 2024; SR 2025 (official) | **NOT RESOLVED — host unreachable** | S-021 tap-agri.com (primary) | — | — | — | All | TCP connection refused/timed out on ports 443 and 80 (curl, and WebFetch independently: ECONNREFUSED 8.215.29.110:443). The main site www.tap-agri.com does respond. | — |
| 1b | AR 2025, 9M2026 statements, filing history (financialfilings.com) | **NOT RESOLVED — bot wall** | S-022 (secondary aggregator) | — | — | — | All | HTTP 403 to scripts. WebFetch got an interstitial requiring an API account signup (email → API key). Not followed: account creation needs the user. | — |
| 1c | TAPG financial statements (substitute) | **PARTIALLY RESOLVED** | S-020 Yahoo Finance via yfinance (secondary) | Annual FY2021–FY2025 (FY2021 mostly empty); quarterly Q1'25–Q3'26 | Annual, quarterly | **No** — period-end only | Q3'25 missing entirely; Q1'25 has only EPS; several rows absent in some periods | Balance-sheet identity (A = L + E) passes for all 9 periods. Quarterly-vs-annual sum not testable (no complete year of quarters). Equity-method earnings line absent. | `data/raw/company/TAPG/yahoo_*.csv` (ignored); checks in `data/reference/TAPG_fundamentals_validation.csv` |
| 2 | Operational metrics (FFB yield, mature ha, OER, production, realised ASP, unit cost) | **NOT RESOLVED** | Needs S-021 annual reports or IDX quarterly releases (primary) | — | — | — | All | No accessible source gives these. **Not estimated.** | — |
| 3 | JV / associate earnings | **NOT RESOLVED** | S-020 has no equity-method earnings line | — | — | — | All | Pretax minus operating income is NOT used as a proxy: it mixes finance income and other items. | — |
| 3b | Dividends received from JVs/associates | **PARTIALLY RESOLVED** | S-020 `Dividends Received Cfi` (secondary) | FY2022–FY2025; quarterly Q2'25–Q3'26 | Annual, quarterly | No | Q1'25, Q3'25 | Annual: 150.0 / 300.0 / 1,170.0 / 958.8 IDR bn (FY22–FY25). Counterparty split (which JV) not available. Long-term equity investments ~IDR 2.7tn (Q3'26). | as 1c |
| 4 | Domestic CPO price history | **PARTIALLY RESOLVED (short history)** | S-023 infokomoditas public JSON feed (secondary; compiles KPBN/Inacom via InfoSAWIT, plus World Bank) | KPBN tender 2026-08-10 → 2026-11-19 (≈57 observations across 3 labelled feeds) | Daily (tender days) | **Yes** (`published_at` per observation) | Everything before Aug 2026; non-tender days | Per-observation source URL and publication timestamp present. History far too short for a backtest. | `data/raw/macro/infokomoditas_prices_snapshot_2026-11-24.json` (ignored) |
| 4b | KPBN official tender history | **NOT RESOLVED** | S-009 KPBN (primary) | — | — | — | All | The e-tender page is protected by reCAPTCHA. Not bypassed. | — |
| 4c | IPOSS daily CPO (ICDX) and palm oil balance | **NOT RESOLVED (preview only)** | S-024 IPOSS (secondary; compiles GAPKI) | Pages show only the last 5 observations (e.g. ICDX IDR 15,760/kg on 2026-11-04; GAPKI CPO output 4,880 kt Aug 2026) | Daily / monthly | Partial | Full history | "Downloading the full file requires an approved account" (review up to 2 weeks). Needs user signup. | — |
| 4d | MPOB | **NOT RESOLVED** | S-017 MPOB (primary) | — | Monthly | — | All | Portal loads; export button is locked; subscription notice ("data langganan"). | — |
| 5 | Regional rainfall | **RESOLVED (regional proxy)** | S-007 CHIRPS v3.0 (primary, satellite-gauge blend) | 2015-01 → 2026-10, 8 palm provinces | Monthly | Not in files; conservative lag of month-end + 45 days (A-010) | None in range; 2026-11 not yet published | 142/142 months parsed; 2,397–10,058 land pixels per region; dry-season low in Jul–Aug; El Niño years 2015/2019 lowest annual totals in all regions. **Flag:** steady rise 2023–2025 to be checked against BMKG. Boxes are approximate, not TAPG estates (A-009). | `data/reference/chirps_monthly_regions.csv` |
| 6 | Earnings announcement dates | **NOT RESOLVED** | S-020 returns no earnings dates for TAPG.JK | — | — | — | All | — | — |
| 6b | Corporate actions (dividends, splits) | **RESOLVED (secondary)** | S-020 | 10 cash dividends, ex-dates 2022-06-06 → 2026-11-11; no splits | Event | Ex-date only (not announcement date) | Announcement dates; AGM and other events | Amounts are plausible against cash dividends paid in S-020 cash flow (FY24 IDR 3.3tn). To cross-check with IDX. | `data/reference/TAPG_corporate_actions.csv` |

## Key TAPG figures available (S-020, IDR bn, secondary; not yet cross-checked with an official filing)

| | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|
| Revenue | 9,345.6 | 8,325.9 | 9,671.5 | 11,402.2 |
| Gross profit | 3,715.9 | 2,217.3 | 3,722.8 | 4,497.6 |
| Pretax income | 3,689.3 | 1,941.1 | 3,926.9 | 4,661.3 |
| Net income to owners | 2,981.1 | 1,608.2 | 3,120.3 | 3,702.3 |
| Dividends received (CFI) | 150.0 | 300.0 | 1,170.0 | 958.8 |
| Cash dividends paid | 496.3 | 754.4 | 3,315.4 | 3,275.7 |

Quarterly revenue: Q2'25 2,888.3 · Q4'25 3,194.4 · Q1'26 2,492.2 · Q2'26 3,365.0 · Q3'26 3,589.5. Q3'25 is missing.

## What unblocks TAPG modelling

1. **User downloads** the AR 2023/2024 and SR 2025 PDFs in a browser (tap-agri.com IR page) and the 2025 AR and 9M2026 statements from IDX. Save them to `data/raw/company/TAPG/`. I can then extract operational metrics, JV earnings and filing dates from the PDFs.
2. Or the user approves a data account: financialfilings API, IPOSS access request, or an installed vendor connector (LSEG, FactSet, S&P) via `/mcp`.
