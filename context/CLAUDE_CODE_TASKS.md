# Claude Code Task Specification

_Last updated: 2026-11-24 · Applies to: this repository · Read `CLAUDE.md`, `context/RESEARCH_CONTEXT.md` §8 and `context/RESEARCH_BACKLOG.md` first._

This spec turns the mandate's modules A–I into tasks that can be built and tested. Tasks are ordered by dependency. Each one lists its inputs, outputs, acceptance tests and what it must **not** do.

## 0. Ground rules (apply to every task)

1. **Point in time.** Every stored value has `obs_date` (or `period_end`) and `published_at`, plus `source_id` (from `quant/config/sources.yaml`) and `ingest_run`. Use `palmquant.store.ingest`, which rejects rows that break these rules. Never bypass it.
2. **No fabrication.** Missing data stays missing. Never interpolate fundamentals, and never forward-fill a value before its `published_at`.
3. **Estimated timestamps.** Where a publication time is unknown, use the conservative lag in `quant/config/settings.yaml` and set `published_at_estimated = True`. Backtests exclude these rows by default.
4. **Execution timing.** A signal computed at close *t* trades at the close of *t+1*. A disclosure after 16:00 WIB counts as next-day information.
5. **Raw data is immutable.** Downloads go to `data/raw/<source>/<yyyymmdd>/` (git-ignored). Transformations go in code; outputs go to `data/processed/` or DuckDB (`data/palmquant.duckdb`, git-ignored).
6. **Rankings stay locked.** Ranking and strategy outputs stay locked until the quality gates in `settings.yaml` pass (≥90% price coverage, ≥6 tickers, ≥12 quarters of fundamentals, actual filing dates, a CPO series and a benchmark, newest price ≤7 days old). Locked outputs print `LOCKED: <failed gates>`.
7. **Secrets.** API keys (for example Copernicus CDS) go in `.env` only.
8. **Tests.** Every module ships with pytest tests under `tests/`. Run `python -m pytest -q` before committing.
9. **Network.** The Claude cloud workspace cannot reach data hosts (audit, 24 Nov 2026). Run T-02, T-05 and T-06 **on a machine with internet access**. If a host refuses, log the failure in `ingest_log` and the audit report. Do not substitute another source silently.

## Existing code (do not rebuild)

| Path | What it does | Status |
|---|---|---|
| `quant/config/settings.yaml` | Study period, storage paths, publication lags, backtest costs, walk-forward, factor and regression settings, gates | Done |
| `quant/config/universe.yaml` | Tickers with Yahoo codes, listing dates (some marked `verify`), notes | Done; listing dates need verification |
| `quant/config/sources.yaml` | 19 sources with access, reliability, timestamp quality and limitations | Done |
| `quant/palmquant/config.py` | `load_config()` → `Config` | Done |
| `quant/palmquant/store.py` | DuckDB schema (prices, corporate_actions, fundamentals, series, events, universe_status, ingest_log); `validate_frame`, `ingest`, `connect`, `table_counts` | Done; 8 tests pass |
| `data/seed/*.csv` | Hand-collected, press-sourced: 22 policy events, 7 HR months, 15 universe-status rows, 4 GAPKI stock months | Done; extend, don't overwrite |
| `tests/test_store.py` | Provenance and look-ahead tests | Passing (24 Nov 2026) |

Run from the repo root: `pip install -r requirements.txt && python -m pytest -q` (`pyproject.toml` puts `quant/` on the path).

---

## T-01 Seed loader and audit report — Module A

- **Build:**
  - `quant/palmquant/seed.py` loads `data/seed/*.csv` into the store. Map `announced_at` to `published_at` where needed.
  - `quant/palmquant/audit.py` writes `outputs/reports/data_audit_<date>.md`. For each source and table it shows rows, date range, share of estimated timestamps, gate status and probe reachability (use `probe_url`).
- **Tests:**
  - Seed rows round-trip.
  - The audit marks gates as failed when tables are empty.
  - A probe failure is reported, not raised.
- **Not allowed:** editing seed CSVs from code.

## T-02 Price, volume and corporate-action ingestion — Module A (networked)

- **Build:**
  - Adapter `quant/palmquant/sources/idx_prices.py` for the IDX daily trading summary, 2013-01-01 (or 2016-01-01) to 2026-11-24, for every ticker ever in `universe.yaml`, including names delisted or suspended in the period.
  - Store open, high, low, close, volume, **value traded** and a suspension flag.
  - Corporate actions (dividends with ex-date, splits, rights) come from IDX/KSEI into `corporate_actions`.
  - Yahoo (`S_YAHOO`) is a cross-check only. Report differences of more than 2% on unadjusted closes.
- **Derived:** `data/processed/total_return_index.parquet`, built from unadjusted closes plus corporate actions in our own code. Do not use Yahoo adjusted closes.
- **Tests:**
  - A synthetic dividend gives the correct total return on the ex-date.
  - Suspended days have no return and are not tradeable.
  - No row has `published_at` before the end of its trading day.
- **Acceptance:** the coverage gate is computed per ticker. Resolve conflict C-01: the SSMS 1-year return (S-001 screen +74% vs about −42% from price prints).

## T-03 Point-in-time universe — Module A

- **Build:** `quant/palmquant/universe.py` with `investable(date) -> list[str]`. Use listing and delisting dates, suspensions, HSC status from `universe_status`, 20-day ADV ≥ Rp1bn (settings) and the business-exposure flag. Apply D-004: history is not truncated, and HSC names are not investable while flagged.
- **Tests:**
  - A ticker with HSC from 2026-11-11 is investable on 2026-11-10 and not on 2026-11-12.
  - A ticker is not investable before its listing date.

## T-04 Fundamentals and operations store — Module A

- **Build:**
  - Load `data/manual/fundamentals_<ticker>.csv` and `operations_<ticker>.csv` (filled by Chat tasks B-01, B-02, B-04). Use long format: ticker, period_end, period_type, item, value, unit, audit_status, published_at, source_id, url.
  - Use a controlled vocabulary of items in `quant/config/items.yaml`, for example `revenue`, `np_parent`, `np_consolidated`, `nci_profit`, `ebitda`, `cash`, `bank_debt`, `ffb_nucleus_t`, `ffb_plasma_t`, `ffb_external_t`, `cpo_output_t`, `cpo_sales_t`, `cpo_asp_idr_kg`, `inventory_cpo_t`, `fertiliser_exp`, `mature_ha`.
  - Restatements become new vintages.
- **Function:** `pit_fundamental(ticker, item, as_of)` returns the latest vintage published at or before `as_of`.
- **Tests:**
  - A value is invisible before `published_at`.
  - A restatement replaces the old value only from its own `published_at`.
  - Identity checks: sales = opening inventory + output + purchases − closing inventory, within tolerance, and flag any break (this catches C-12-type errors).

## T-05 Estate geocoding and rainfall extraction — Module D (networked)

- **Input:** `data/manual/estates.csv` (Chat B-07), with `geo_level` ∈ {boundary, point, regency, province}.
- **Build:**
  - `quant/palmquant/climate/geo.py` geocodes to regency centroids or polygons (GADM level 2) where no coordinates exist.
  - Download CHIRPS v2 monthly 0.05° for 1990–2026, NASA POWER monthly (precipitation, ET0) per point, and ERA5-Land soil moisture where a CDS key is available.
  - Compute the area-weighted monthly rainfall and its anomaly versus 1991–2020 for each company, weighted by mature ha.
  - Store as `series` with `series_id = rain_<ticker>_<cluster>`.
- **Tests:**
  - Weights sum to 1 per company.
  - A province-level proxy is flagged in the output.
  - No value is published before its month ends plus the source lag.
- **Not allowed:** treating a province proxy as estate-level data in any report.

## T-06 Water-deficit series — Module D

- **Build:** monthly water deficit = max(0, ET0 − effective rainfall), with a simple bucket for soil water (capacity a parameter, default 200mm), per company cluster. Also build cumulative 3-, 6- and 12-month deficits.
- **Tests:**
  - Known synthetic inputs give the expected deficit.
  - The bucket never goes negative or above capacity.

## T-07 Distributed-lag yield model — Module D

- **Data:** company-level quarterly (or monthly, where available) FFB yield = nucleus FFB ÷ average mature ha. **Do not fit estate-level models without estate-level output.**
- **Model:** `yield(i,t) = company FE + quarter/season FE + Σ_g β_g · deficit(lag group g) + age controls + fertiliser (if available) + ε`, with lag groups 0–3, 4–6, 7–12, 13–18 and 19–30 months. Add a nonlinear term (deficit above the 90th percentile).
- **Estimation:** pooled OLS with company-clustered SEs (statsmodels). Use ridge as a robustness check only. Report the number of observations per coefficient and stop with a warning if there are fewer than 10 per parameter.
- **Validation:** rolling-origin forecasts vs seasonal naive, previous year, trailing 4-quarter average, and management guidance. Report MAE, RMSE, bias and directional accuracy.
- **Tests:**
  - A synthetic panel with a known lag-12 effect recovers it.
  - No future rainfall enters a forecast.

## T-08 Historical El Niño event study — Modules D + F

- **Episodes:** 2015–16, 2018–19, 2023–24, and 2026–27 to date. Dates come from NOAA ONI/RONI (`S_NOAA_CPC`), stored as series.
- **Output per company:** rainfall anomaly, FFB yield change at the lags, CPO output, ASP, unit cost, margin, net profit, and the share price relative to IHSG and the palm benchmark. Show the date of the first market reaction against the first visible production decline.
- **Tests:** episode windows use only data available at each date.

## T-09 Domestic price transmission — Modules E + G

- **Build:** `quant/palmquant/transmission.py`. Domestic realised CPO (Rp/kg) = (benchmark USD/t − duty − levy − DSI fee − logistics − quality discount) × USD/IDR ÷ 1000.
  - Benchmark choice is configurable: Kemendag HR, Bursa Malaysia, or Rotterdam.
  - Keep units and currencies explicit, and record the FX date.
  - Calibrate the residual discount to the reported company ASP.
- **Tests:**
  - The November 2026 HR (978.90), duty (124) and levy (122.36) reproduce the recorded 97.9% state capture of the m/m change (see §6.5 of the context).
  - A unit mismatch raises an error.

## T-10 Biodiesel funding model — §6 of the mandate

- **Build:**
  - Subsidy = eligible PSO volume × max(0, biodiesel HIP − diesel reference).
  - Levy revenue = Σ export volume × levy rate × HR.
  - Scenarios: blend (B40 / B50 / B60), Brent, CPO, USD/IDR, export volume and levy rate.
  - Output a surplus/deficit grid.
- **Calibration check:** reproduce the LPEM table (Brent 100 / 80 / 70 → subsidy USD 0.7 / 1.9 / 2.6bn at Rp18,154).
- **Tests:** the calibration reproduces within ±10%.

## T-11 Factor screen — Module B (locked until gates pass)

- **Factors:** as in `settings.yaml` and mandate §11-B. Use cross-sectional percentile ranks among investable names at each month-end, needing at least 5 names.
- **Missing data:** a factor is missing (not zero) when its inputs are missing. The composite needs at least 60% of its weight available.
- **Weights:** initial weights are the mandate's hypothesis (25/25/20/15/15). Do not optimise them. Report sensitivity to equal weights.
- **Tests:**
  - Ranks use only point-in-time inputs.
  - A missing input is not imputed.

## T-12 Commodity and macro regressions — Module C

- **Spec:**
  - Weekly (primary) and daily returns.
  - Rolling windows of 60 / 120 / 252 days (daily) and 104 weeks (weekly, minimum 78).
  - Regressors: CPO, IHSG, USD/IDR, Brent.
  - HAC (Newey–West) SEs; VIFs; rolling betas with CIs; Chow / CUSUM stability.
  - Residual momentum = 52-week cumulative residual skipping the last 4 weeks.
  - Handle the IHSG series break from 13 Nov 2026 (HSC exclusion) explicitly.
- **Predictive test:** does residual underperformance predict 1–3 month excess returns out of sample? Report the t-stat and the number of independent observations. Do not presume mean reversion.

## T-13 Earnings nowcast — Module E

- **Build** a bottom-up quarterly model for TAPG, DSNG and LSIP:
  - Mature ha × yield = FFB, then × OER = CPO.
  - Inventory identity → sales volume; sales × ASP (T-09) → revenue.
  - Cost lines (variable, fixed, fertiliser, external FFB, D&A), interest, JV share (TAPG), tax and NCI.
- **Expectations:** use only clearly labelled proxies (`proxy_seasonal`, `proxy_guidance`, `broker_<name>_<date>`, `market_implied`). The word "consensus" is reserved for vendor data.
- **Back-test:** rolling origin. Report MAE, RMSE, bias and directional accuracy vs reported results.

## T-14 Event studies — Module F

- **Spec:** market model estimated on [−250, −30]. Windows: [−20, −1], [0, +1], [+2, +5], [+6, +20], up to +60. Minimum 120 estimation observations.
- **Overlaps:** drop overlapping same-entity events. Sector-wide events are tested as calendar-time portfolios.
- **Events:** start from `data/seed/policy_events.csv`.
- **Report:** pre-event drift is reported as anticipation, not as evidence of informed trading.

## T-15 Market-implied expectations — Module G

- **Build:** reverse DDM, reverse FCFF and reverse residual income, kept as separate functions.
  - Market-implied normalised NP, sustainable ROE and CPO price.
  - Every input comes from `context/ASSUMPTIONS.md` IDs.
- **Tests:**
  - TAPG at Rp1,715 with BVPS Rp590.2, ke 13.75% and g 3% gives an implied ROE of 34.2%.
  - The g = payout-consistent variant gives ≈37.7% (audit §2.1).

## T-16 Backtests — Module I (locked until gates pass)

- **Strategies:** value, momentum, nowcast, commodity residual, climate resilience, catalyst and combined. Benchmarks: point-in-time equal-weight palm and IHSG total return.
- **Rules:**
  - Monthly rebalance; t+1 execution.
  - Costs and slippage from `settings.yaml`; maximum 10% of ADV; suspensions frozen.
  - Walk-forward with 2016–18 as burn-in and annual out-of-sample folds.
- **Report:** CAGR, volatility, Sharpe, Sortino, maximum drawdown, alpha, IR, turnover, hit rate, profit factor, and a bootstrap CI on excess return. Count the strategies tried and apply a multiple-testing adjustment (deflated Sharpe or Holm).

## T-17 Dashboard — §15 of the mandate

- **Build:** a Streamlit or static Plotly HTML dashboard in `dashboard/`. Every figure shows its source_id and as-of date. Data-quality warnings and LOCKED states are prominent.

---

## Suggested order

T-01 → T-02 → T-03 → T-04 → T-09 → T-10 → T-05 → T-06 → T-07 → T-08 → T-12 → T-13 → T-14 → T-15 → T-11 → T-16 → T-17.

T-09, T-10 and T-15 need no networked data and can be built now against seeds and manual CSVs.
