# Research Methodology

_Finalised 2026-11-24 (D-003); amended 2026-11-24 (D-008, D-009, D-010). Change only by logging a new decision in `DECISION_LOG.md`._

## 1. Objective

Find **earnings surprises and underappreciated catalysts** in Indonesian palm oil equities **before they are fully priced in**.

## 2. Mandate parameters

| Parameter | Setting |
|---|---|
| Strategy | Long-only, catalyst-driven quantamental |
| Investment horizon | 3–12 months per position |
| Benchmarks | (1) IHSG / Jakarta Composite (`^JKSE`); (2) equal-weight core palm oil universe, rebalanced monthly using point-in-time membership |
| Market data frequency | Daily (prices, volume, FX, Brent, CPO where available) |
| Factor screening | Weekly, using the last completed trading week's data |
| Portfolio rebalancing | Monthly, at month-end |
| Fundamental updates | When disclosed publicly (financial statements, operational releases, regulations), timestamped by publication date |
| Historical backtest | From 2016, subject to actual data availability per series (see the Phase I audit) |

## 3. Universe

- **Coverage universe** (D-002): 9 core and 6 extended names, kept as-is. See `RESEARCH_CONTEXT.md`.
- **Point-in-time (PIT) investable universe:** rebuilt each month-end by `quant/build_universe.py` from `data/reference/listings.csv`. A name is eligible at date *t* only if, with data up to *t*:
  1. it has traded at least 60 sessions since listing (A-004),
  2. it traded in the last 20 sessions (excludes suspended names),
  3. its median 63-day traded value is ≥ IDR 1.5bn for the core liquidity band, or IDR 0.25–1.5bn for the extended band (A-001, A-002, A-003).
- The candidate list includes excluded, delisted and historical-only palm names (GOLL, MAGP, PALM, BTEK) so the history isn't limited to today's survivors. Names with no price history are reported as gaps, not dropped silently.
- Backtests trade only names in the **core liquidity band at the rebalance date**. Coverage tier never overrides PIT eligibility.

## 4. Research pipeline

1. **Macro / industry drivers:** CPO price (USD/mt, IDR/kg), USD/IDR, Brent (biodiesel economics, POGO spread), rainfall and ENSO (yields with a 6–24 month lag), industry production and stocks, biodiesel mandate and allocation, export levy and duty.
2. **Company fundamentals:** production (FFB, CPO), yields, planted and mature area, age profile, cash cost per tonne, margins, balance sheet, dividends.
3. **Earnings surprise engine:** a driver-based estimate of next-quarter earnings (realised CPO price net of levy and duty × volume − cost) compared with the market-implied or consensus estimate where available. The surprise signal is our estimate minus the expected figure.
4. **Catalyst map:** dated events (policy decisions, levy and reference-price resets, mandate changes, earnings dates, production releases, weather regimes) with expected direction and magnitude.
5. **Quant layer:** weekly factor screen (e.g. estimate-driven surprise, valuation versus history and peers, price momentum and reversal, liquidity) on PIT data. Signals are only used after an out-of-sample test.
6. **Portfolio construction:** monthly, long-only, with position limits and liquidity limits based on traded value (to be set as assumptions before the first backtest).

## 5. Point-in-time and bias controls

- Every record carries an **as-of (publication) date**. Signals use only records published before the signal date.
- Financial statements are available from their IDX filing date, not the period-end date. Where the filing date is unknown, apply a conservative lag (A-005).
- Revised series (e.g. USDA PSD) need archived vintages. Without them, mark the series "not PIT" and use it for context only, not in signals.
- Survivorship: PIT universe as in §3. Delisted names need IDX price history (gap: GOLL, MAGP).
- Backtests: include transaction costs and liquidity limits; report results gross and net; use walk-forward or holdout testing; no parameter tuning on the test period.

## 5a. Reporting scope (D-008)

- **Consolidated:** TAPG and subsidiaries. Covers the financial statements, realised ASP, sales volumes, cost notes and capex.
- **Joint ventures:** USTP (50%) and small JVs, on a 100% basis, plus TAPG's equity-method share and dividends.
- **Group-wide:** operational statistics reported "including associate companies" (area, age profile, FFB, CPO/PK output, yield, OER).
- Ratios are computed **only within one scope** (enforced by `quant/tapg_scope.ratio`). The consolidated share of group-wide volumes is not disclosed, so consolidated unit costs per tonne cannot be computed yet.

## 5b. Disclosure dating (D-009)

- Each disclosure's `available_from` comes from `data/reference/TAPG_disclosure_dates.csv` (A-012/A-013) and carries a basis label: EVIDENCE (dated press report) or ASSUMPTION (statutory deadline).
- Where an IDX timestamp exists (S-027), `available_from` follows A-018. Quarterly operating figures from broker reports are usable from `first_seen` only (D-011).
- Backtests must use `available_from`, never document dates. Results that depend on dates labelled ASSUMPTION are reported as such.

## 5c. Nowcasting (D-010)

- Revenue = Σ product volume × realised price, where realised price = world price × domestic discount (levy/duty schedule).
- Earnings = revenue − cost model (purchased-FFB cost tied to the FFB price; carried upkeep and fertiliser with timing) + USTP share modelled separately + finance and tax.
- Exploratory scenario nowcasts (D-013) may be run before validation, but must tag every input (OBS/BRK/GUID/DER/EST) and report break-even sensitivities rather than point claims.
- Fit on 2021–2024 and validate out of sample on 2025–2026. Until quarterly volumes exist, only naive benchmarks are reported, labelled as such.

## 5d. Expectations-gap workflow (Phase III)

1. Our forecast (scenarios with tagged inputs), challenged by a joint downside grid (`quant/tapg_q4_downside.py`).
2. Dated consensus on a stated basis (`TAPG_expectations_snapshots.csv`, D-016), with duplicate vendor feeds counted once (D-019).
3. Market-implied sustainable earnings (`valuation/reverse_valuation.py`).
4. Price-in evidence (`quant/tapg_price_in.py`): never read as mispricing on its own.
5. PIT validation against naive benchmarks (`quant/forecast_validation.py`), cut off at the target's original publication date. Below about 12 PIT observations a model stays EXPLORATORY and is forward-tested via `forecast_journal.csv`.
6. Catalysts tracked in `catalyst_register.csv`.
7. Phase V additions: forward dividend capacity (not trailing yield); reported scenario-weight uncertainty; dated, append-only monitoring and consensus logs; expectation-adjusted surprises (not growth proxies) for any event-study inference.
8. Challenger valuation: start with the uniform consensus-anchored rule (A-029); replace it with company-specific drivers (refinery margins for STAA, cash and payout for LSIP, wood segment for DSNG) only for names selected for deeper research.

## 5e. Evidence classification and new-sector pilots (Phase VIII, D-029/D-030)

- **Engineering tests** (`tests/`) check code correctness: identities, PIT ordering, idempotency, bounds. They are never cited as evidence of forecasting skill.
- **Empirical validation** means out-of-sample (PIT, walk-forward) errors against naive benchmarks, reporting MAE, RMSE, bias, n and HAC/Diebold-Mariano uncertainty. Below 12 out-of-sample observations a model is EXPLORATORY.
- Regression t-stats use Newey-West standard errors (`quant/stats_utils.ols_nw`).
- **New-sector pilots** must pass a tested (not listed) data-feasibility screen first. Each needs a pre-registered hypothesis, benchmarks and a kill criterion before modelling. No machine learning unless a simple model beats the benchmarks.
- Post-hoc specifications (chosen after seeing a failed test on the same data) are never evidence. They may only be registered for forward testing or for replication on independent data (D-031).
- **Three kinds of evidence are always reported separately:** (1) automated software tests; (2) predictive forecasting accuracy (out of sample, against benchmarks); (3) realised investment alpha (returns earned after costs). Neither (1) nor (2) implies (3).
- **Availability dates:** record the regulatory deadline and the actual filing timestamp separately; use the actual date only where verified (A-018 rule), else the deadline, flagged. Comparative (restated) figures are dated to the document that publishes them unless the original is independently verified.
- **Frozen hypotheses:** a frozen spec (parameters, predictors, benchmarks, pass/kill rules) is stored as JSON and evaluated prospectively only; every pre-registered benchmark is compared, not just the weakest.
- **Pre-registration order:** the specification is committed before any model is run; data-layer fixes may follow only before results are computed and are committed separately. Variants are registered anew and evaluated prospectively.
- **Information-matched benchmarks:** when a model uses a new data source, it must beat simple rules using the SAME information (e.g. 2 months × 1.5), not only unconditional benchmarks; report information value and model value separately.
- **Discovery vs confirmation:** a rule selected on historical data (even a simple one) is registered as a frozen prospective hypothesis; historical results are discovery evidence only. Multiplicity across all compared pairs (Holm) and across banks/targets (Bonferroni) is applied before any 'information value' claim.
- **Commodity-linked hypotheses:** the benchmark must already contain the commodity signal (price-scaled naive); correlation with a public benchmark price is not incremental information.
- **Document provenance:** every downloaded source file gets a SHA-256 in a committed manifest; raw files stay git-ignored. First-reported values are used where later documents revise history.
- **A historical pass is not the end:** even a pre-registered GO is tracked prospectively in the journal before any use beyond research.
- Methodology map: `outputs/quant_methodology_2026-11-25.png` (regenerate with `outputs/make_methodology_diagram.py`).

## 6. Data integrity rules

- No fabricated or interpolated data presented as observed. Gaps stay gaps and are documented.
- Every series must have a `SOURCE_REGISTER.csv` entry with its verification status.
- Unofficial sources (e.g. Yahoo) are cross-checked against an official source on a sample before backtests.

## 7. Phases

| Phase | Scope | Status |
|---|---|---|
| 0 | Workspace setup | Done |
| I | Data availability audit | Done for TAPG; other 14 names pending |
| II | TAPG fundamental data completion and preliminary quant | Done (audit remediated) |
| III | Expectations gap and predictive validation | First pass done (IC memo 2026-11-24); forward-testing journal open |
| III | Driver research (macro, industry, company) | Not started |
| IV | Signal design and backtests | Not started |
| V | Synthesis: catalysts and theses | Not started |
| VI–VII | LSIP deep-dive; institutional decision | Done: NO TRADE (D-027, D-028) |
| VIII | Audit, methodology map, poultry feasibility | Done: conditional GO, CPIN only (D-029); H1 killed (D-031) |
| IX | CPIN PIT audit v2; banking feasibility | Done: H2 frozen (D-032); banking CONDITIONAL GO for MVP-B1 (D-033) |
| X | MVP-B1 banking validation (BBCA, BBRI) | Done: both NO-GO on profit (D-034); NII information value documented |
| XI | Banking audit; MVP-B2; coal feasibility | Done: audit (D-035); MVP-B2 frozen prospective (D-036); ITMG conditional GO, PTBA NO-GO (D-037) |
| XII | ITMG-C1 ASP nowcast | Done: GO for ASP forecasting (D-038); prospective tracking; C2/C3 proposed |
