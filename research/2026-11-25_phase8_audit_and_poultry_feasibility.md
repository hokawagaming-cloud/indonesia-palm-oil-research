# Phase VIII — Checkpoint Audit, Methodology Map and Poultry Pilot Feasibility

_Date: 2026-11-25._

_Code: `quant/poultry_feasibility.py`, `quant/final_decision.py` (audit fix), `outputs/make_methodology_diagram.py`._

_Outputs:_
- _`outputs/quant_methodology_2026-11-25.png` (4000×2700 px)_
- _`data/reference/poultry_prices_monthly.csv`_
- _`data/reference/research/poultry_feasibility.csv`_
- _`data/reference/research/poultry_coverage.csv`_

## 0. Decisions carried forward (unchanged)

**NO TRADE** (D-028):
- **TAPG: WATCH.** Trigger at IDR ≤ 1,525.
- **LSIP: WATCH.** Re-test on C-019, C-020 or C-021; preferred entry 1,340–1,460.
- **DSNG: WATCH.** Revisit on C-011.
- **STAA: AVOID.**

All dated forecasts (39 journal rows) and earlier decisions are preserved.

## 1. Audit of the research checkpoint

| # | Finding | Severity | Action taken |
|---|---|---|---|
| A1 | The Phase VII factor regressions used plain OLS t-stats, although the repo already has a Newey-West helper (`stats_utils.ols_nw`). | Medium | **Fixed.** `final_decision.py` now reports HAC t-stats. LSIP market-beta t fell from 5.9 to 4.3 and sector-beta t from 10.9 to 7.8. Alpha t-stats: TAPG 2.6 → 2.9, LSIP 1.0 → 1.2, DSNG 1.7 → 2.0. **No conclusion changes**: LSIP alpha remains insignificant, and all four names are sector bets. |
| A2 | The Phase VII memo figures came from a run before a fill-method fix (pad-fill in `pct_change`). | Low | The re-run differs slightly: LSIP β 0.76 → 0.74, LSIP 12m residual +26% → +24%, DSNG −33% → −36%. The memo is preserved with an erratum appended; the CSVs carry the corrected values. |
| A3 | The sector index includes the stock itself (≈ 1/11 weight), which biases sector beta toward 1. | Low | Planned: use an ex-self peer index (`tapg_quant_research.peer_index` already does this for TAPG). |
| A4 | IHSG is a price index, while the stocks are total return, so alphas are overstated by about 2–3pp a year. | Low (disclosed) | Planned: a total-return IHSG proxy. |
| A5 | **No empirically validated signal exists.** The 39 tests are **engineering tests** (identities, PIT ordering, idempotent journal, bounds). The only forecast validation is TAPG PIT with n = 2 (MAPE 23–27%, biased low). | High (interpretation) | Made explicit in METHODOLOGY §5e and in the diagram. Nothing may be called "validated" before n ≥ 12 out-of-sample observations. |
| A6 | The 17.5% hurdle (ke 12.5%) was set when the 10-year SBN yielded about 6.2%. It now yields 7.735% (S-052), so the implied equity risk premium has fallen to about 4.8%. | Medium | Logged as an **open reassessment item** (D-030); the hurdle is unchanged this session. LSIP fails at 18.5%. |
| A7 | The scenario weights (30/50/20) are judgement. The Dirichlet analysis is a sensitivity check, not an estimate. | Disclosed | No change. |
| A8 | Consensus history starts on 2026-11-24, so a historical expectation-gap backtest is impossible for every sector. | Structural | Snapshots continue forward. This limitation also applies to poultry (§3). |
| A9 | The event study has n = 8 and used a growth proxy before Phase V. | Disclosed | Unchanged; the forward surprise framework is in place. |

## 2. Quantitative methodology visualisation

`outputs/quant_methodology_2026-11-25.png` maps nine stages, from data sources to monitoring:
- Each box shows the formulas **as coded** and cites its module.
- **Status colours:**
  - Implemented: 7 stages.
  - Exploratory: 2 stages (predictive models; statistical validation).
  - Empirically validated: **none**.
  - Planned: 4 items.
- No accuracy figures or thresholds appear beyond those measured in the repository.

## 3. Poultry historical-data feasibility (tested, not listed)

| Dataset | Source tested | Verdict | Evidence (2026-11-25) |
|---|---|---|---|
| Livebird price | PINSAR (pinsar.id/harga) | **NOT AVAILABLE** | Month-to-date provincial averages only (blank on test day); history only on request |
| Livebird price | Bapanas Panel Harga ("Ayam Ras Pedaging Hidup") | **NOT VERIFIED** | API returns 401 "Invalid or missing API key"; front end showed no prices; no export found |
| DOC price | PINSAR / Bapanas / PIHPS | **NOT AVAILABLE** | No free series; JPFA investor presentations (2024–26 only) are the sole candidate |
| Domestic corn | Bapanas ("Jagung Pipilan Kering") | **NOT VERIFIED** | Same API-key barrier; PIHPS has no corn |
| World maize, soybean meal | World Bank CMO (local) | **AVAILABLE** | Monthly 1960-01 to 2026-10 |
| USD/IDR | Repository (`macro_monthly.csv`) | **AVAILABLE** | Monthly |
| Chicken meat and egg prices | **PIHPS, Bank Indonesia** (retail / wholesale / producer) | **AVAILABLE** | Scripted (session cookie). National monthly series: retail from 2017-03 (117 months), wholesale from 2017-06 (114), producer from 2018-03 (105). Producer "daging ayam" is **carcass-level, not livebird**. |
| Poultry production | BPS WebAPI | PARTIAL | Annual only; registered key required (no account created) |
| Supply-control policy | Kementan circulars | PARTIAL | Unstructured; needs manual event coding |
| Quarterly segment financials | CPIN website | **AVAILABLE (header-checked)** | Interim FS PDFs return HTTP 200 for every Sep-quarter tested, 2018–2026. Segment-note content is **not yet verified** (nothing downloaded). |
| Quarterly segment financials | JPFA website / IDX | PARTIAL | Website shows 2025–26 only. The IDX API sits behind a Cloudflare challenge (not bypassed), so history must be downloaded manually. |
| PIT filing timestamps | jejaksaham.id | AVAILABLE | CPIN, JPFA and MAIN listings reachable |
| Historical analyst expectations | Yahoo / S&P | **NOT AVAILABLE** | Snapshot only. Current analyst counts: CPIN 7 (FY26) / 9 (FY27); JPFA 9 / 14; MAIN 1 / 1. |
| Liquidity (60-day median traded value) | Yahoo | — | CPIN IDR 53bn/day; JPFA 31bn/day; **MAIN 0.7bn/day (uninvestable at scale)** |
| Alternative: monthly bank-only statements | OJK CFS / bank websites | PARTIAL | OJK publishes with a 3-month lag (POJK 37/2019) and omits quarter-end months. Banks self-publish about 1 month after period end, so per-bank collection would be needed. Not tested further. |

**First look (not a predictive test):** quarterly changes in the PIHPS producer chicken price and the IDR feed-cost proxy (0.55 maize + 0.25 soybean meal, A-037) correlate at only **r = 0.18 (n = 35)**. Output prices are not a pass-through of world feed costs. The spread is the economically relevant variable, but whether it predicts anything is **untested**.

## 4. GO / NO-GO recommendation

Criteria fixed before deciding. A pilot needs **all** of G1–G3 and G5, plus G4 or an explicit plan to substitute for it.

| Criterion | Status |
|---|---|
| G1. Output-price driver, ≥ 24 PIT-safe quarters | **Partial.** Carcass producer price: 35 quarters. Livebird and DOC: none. |
| G2. Relevant input-cost driver | **Partial.** World maize and soybean meal yes; domestic corn unverified, and Indonesia's import controls make world prices a weak proxy. |
| G3. Target series (segment margin), ≥ 24 quarters | **Likely for CPIN** (≈ 33 quarters, URLs live; content unverified). Partial for JPFA. |
| G4. Historical expectations | **Fail.** Same structural gap as palm oil. |
| G5. Liquidity ≥ IDR 10bn/day | CPIN and JPFA pass; MAIN fails |

### Recommendation: **CONDITIONAL GO, narrowed to a CPIN fundamental-nowcast test.**

**NO-GO for:**
- Livebird/DOC margin models (no data).
- MAIN (illiquid; n = 1 consensus).
- Any expectations-gap backtest (no history).
- Banking for now (partial; reconsider only if the poultry kill test fails).

**Why GO at all:** PIHPS provides a long, official, scriptable output-price series, and CPIN's quarterly filings appear to cover 2018–26. That is enough to test, falsifiably, whether observable prices predict segment margins better than naive benchmarks. Palm oil cannot run that test today (n = 2).

**Conditions before any work starts:**
1. **User approval** to download about 33 CPIN interim FS PDFs from cp.co.id (a few MB each), or the user supplies them.
2. A one-file check confirms that quarterly segment disclosures (feed, DOC/broiler, processed food) exist and are consistent.

## 5. Next research milestone: M-VIII-1 (CPIN segment-margin walk-forward test)

**Hypothesis H1 (falsifiable):**
- Δ broiler-segment margin(q) = α + β₁ Δ(producer chicken price − feed proxy)(q) + β₂ Δ USD/IDR(q−1) + ε.
- Inputs are known **before** the filing date, using PIHPS monthly averages and IDX timestamps (A-018).

**Benchmarks:**
- Last quarter's margin.
- Same quarter last year (seasonal).
- Last margin scaled by the price change (the analogue of `price_last`).

**Protocol:**
- Expanding-window walk-forward from 2018Q1, with the first forecast at about 2021Q1, giving about 20 out-of-sample quarters.
- Report MAE, RMSE, bias, n and Diebold-Mariano t (HAC).

**Kill criterion:** if the model's out-of-sample MAE is not at least 15% below the best benchmark over ≥ 16 quarters, with a DM t ≥ 1.65, **stop the poultry pilot**. No ML unless H1 passes.

**Scope guard:** reuse `forecast_validation.py`'s journal and metrics and `stats_utils.ols_nw`. No new databases or dashboards.

**Palm oil in parallel (no new work needed):**
- FY2026 results (Feb–Mar 2027) resolve the first TAPG and LSIP forecast-journal rows (C-020). This will be the first genuine out-of-sample error measurement.
- TAPG and LSIP monitoring continues via `quant/tapg_monitor.py` and catalysts C-019 to C-021.

_Sources:_
- _S-003 World Bank CMO_
- _S-002 / S-036 Yahoo_
- _S-052 ADB AsianBondsOnline_
- _S-054 PIHPS_
- _S-055 CPIN investor relations_
- _S-056 JPFA investor relations_
- _S-057 Bapanas (not verified)_
- _S-058 PINSAR (not available)_
- _S-059 OJK CFS_
