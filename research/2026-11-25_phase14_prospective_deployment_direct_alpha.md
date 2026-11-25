# Phase XIV — Prospective Deployment and Direct Alpha Research Design

_Date: 2026-11-25._

_Code: `quant/itmg_prospective_run.py`, `quant/itmg_prospective_eval.py`; tests in `tests/test_phase14.py`._

_Decisions: D-042 (deployment), D-043 (audit clarifications), D-044 (direct-return design)._

**Unchanged and preserved:**
- C1: historical GO.
- I1: CONDITIONAL GO.
- C2/C3: NO-GO.
- MVP-B2, CPIN H2, palm-oil NO TRADE and all journal rows.

**Three kinds of evidence are kept separate:** software tests; forecasting accuracy; trading alpha. No alpha is claimed.

## Workstream 1 — Prospective deployment

**Forecast script:** `quant/itmg_prospective_run.py` (frozen C1-M2 and I1).
- Downloads the World Bank CMO file **at run time**, saves it with a UTC timestamp and records its **SHA-256**.
- Uses the **primary** model if the quarter's third Newcastle month is present. Otherwise it uses the **pre-specified fallback** (two-month quarterly averages, M2 re-estimated identically; Phase XIII sensitivity).
- Computes I1 and G3 gross profit with the frozen inputs.
- **Prediction intervals** are empirical 10/90% from historical walk-forward errors. They are noted as slightly understating uncertainty in fallback mode.
- **Records:** writes a JSON record (timestamp, vintage, all input hashes, git commit, spec ids, point forecasts, benchmarks, intervals) and **appends** 4 journal rows.

**Evaluation script:** `quant/itmg_prospective_eval.py`.
- Downloads and hashes ITMG's 4Q26 deck and FY FS (handling both file-naming variants) and extracts the first-reported ASP and Q4 gross profit.
- Appends resolution rows to the journal.
- If the documents are not yet published, it changes nothing.

**Scheduling** (one-time tasks in the Claude desktop app, saved in **Auto** permission mode):

| Task | Runs | Does |
|---|---|---|
| `itmg-prospective-forecast-2026q4` | **10 Jan 2027, 10:00 WIB** | Run, check, commit and push the forecast |
| `itmg-prospective-evaluation-2026q4` | **8 Mar 2027, 10:00 WIB** | Evaluation (after ITMG's historical FY release window of day 52–57) |

- Tasks run only while the desktop app is open; if it is closed, they run at the next launch.
- The evaluation task reports "not yet published" and changes nothing if the documents are late.

**Verified operational:** an ad-hoc task (`itmg-scheduler-verification`, manual-only) was run as a real scheduled session. It reached the repository at commit adb5fab and ran both scripts in dry-run mode (exit 0). The forecast run reported mode `fallback_two_month`, because the latest month in the vintage today is 2026-10, and M2 ASP of USD 102.5/t. The evaluation reported "not yet published". **No tracked file changed.** The scripts are now committed, so the January run will use the committed versions.

**Not verified:**
- That the app will be open on 10 Jan.
- Network availability on that day.
- That `git push` credentials work non-interactively inside a scheduled session. The run will report a push failure rather than retry.

## Workstream 2 — Independent statistical audit: clarifications

| Item | Clarification |
|---|---|
| **World Bank availability** | Only **one** archived observation establishes availability **at D+10**: June 2026 data were present on 10 Jul 2026 07:04 UTC. The **September** archive shows availability by **15 Oct (D+15), not D+10**. October data by 4 Nov and January by 9 Feb are not quarter ends. Pink Sheet cover dates suggest an early-month release, but **D+10 availability at every historical quarter end is not proven**. |
| Delayed-availability sensitivity | **Maintained as the conservative case**: −39% vs the strongest benchmark (Holm p 0.009) if each quarter's last month is unavailable. **It is now the operational fallback.** |
| Classifications | C1 historical GO and I1 CONDITIONAL GO preserved. |

### Residual risk register

1. **Vintage risk:**
   - Pre-2026 CMO vintages were not inspected (the URL code changes each year).
   - Revisions seen in 2026 vintages are ≤ USD 0.05/t, but earlier methodology changes cannot be excluded.
2. **Target-vintage risk:** first-reported ASP is taken from today's copies of the historical decks. If ITMG replaced a deck after first publication, the "first-reported" value may differ.
3. **Model-selection risk:**
   - C1's lag structure (0–1 quarters) was chosen with domain knowledge after the ASP and Newcastle history had been viewed during extraction.
   - Three models were tested (Holm-corrected), but the space of models *considered* was larger than the space tested.
   - I1's component choices followed C1–C3 results (pre-registered before I1 ran, but conditional on them).
4. **Single-company and short-sample risk:** n = 22 historical quarters; one regime spike (2021–22).
5. **Benchmark-definition risk:** "strongest benchmark" is chosen ex post among the registered benchmarks. This is conservative for pass/fail, but the selection itself is data-dependent.
6. **Programme multiplicity:** 16 tests so far. Only C1 survives Holm (p 0.012). I1 does not.

## Workstream 3 — Direct return prediction: feasibility (descriptive only; no backtest run)

**Existing data** (`direct_return_feasibility.json`):

| Dimension | Finding |
|---|---|
| Universe in repo | 23 palm-related equities + IHSG (Yahoo daily, 2015–2026). **Only 9 names have median traded value ≥ IDR 5bn/day** (TAPG 26.9bn; LSIP, DSNG, AALI 10–12bn; BWPT, SSMS ≈ 9.7bn; NSSS, STAA, SIMP 5–7bn). Twelve names trade < IDR 1.5bn/day. |
| Sample | ≈ 128 months (2016-03 to 2026-10) for time-series tests. Cross-sections of 5–11 names per month (PIT core band). |
| Survivorship | Listings include suspended/delisted GOLL and MAGP with no Yahoo prices (suspended for most of the sample). For a broad IDX universe, Yahoo lacks delisted stocks, so the bias must be quantified. |
| Liquidity and costs | Large caps ≈ 0.45% round trip (incl. 0.10% sales tax). Illiquid names ≥ 1% plus impact. IDX auto-rejection limits and 100-share lots constrain small accounts. |
| Factor exposures | Only IHSG and constructed sector/commodity factors are available. There is no Indonesian factor library, so "alpha" must be shown net of market, sector and commodity beta. |
| PIT fundamentals | **Not available** (Yahoo statements are restated and short), so valuation dispersion and quality are not testable with integrity. |
| Earnings revisions | **No history** (consensus log starts 2026-11-24), so forward only. |
| Commodity series | CPO, Newcastle and Brent monthly (World Bank, publication lag ≈ 2 business days) are suitable for impulse signals. |
| Multiple-testing risk | 16 programme tests already. Any new family must be small and Holm-corrected. Residual momentum on palm has **already been explored** (IC t 0.93), so it is not re-registered. |

**Pre-registered hypotheses (design only)** (`DR_preregistration.json`):

| Hypothesis | Signal → position (long-only, monthly) | Primary benchmark | Data status |
|---|---|---|---|
| **R1** Palm CPO impulse | CPO (IDR) change of month t−1 > 0 → hold EW PIT-liquid palm basket for t+1, else money market | Buy-and-hold palm basket | In repo |
| **R2** Coal Newcastle impulse | Newcastle change of t−1 > 0 → hold EW liquid coal basket, else money market | Buy-and-hold coal basket | Needs coal OHLCV and corporate-action checks |
| **R3** Liquid IDX 12-1 momentum | Top 20 of the 100 most liquid IDX names by 12-1 return, EW | EW liquid universe | Needs ~300 tickers; survivorship to quantify; lowest priority |

**Common rules:**
- **Pass:** net annualised excess ≥ 3% vs the primary benchmark, Holm-adjusted HAC p ≤ 0.05, positive in both sample halves, and max drawdown no worse than the benchmark.
- **Alpha** must be reported net of IHSG and sector beta.
- **Passing** leads only to 12 months of prospective paper tracking. No BUY from any backtest.
- **Not registered:** valuation, quality, earnings revisions, palm cross-sectional or residual momentum (reasons in the JSON).

## Next milestone

| Order | What |
|---|---|
| 1 | Execute R1 (data already in the repo) exactly as registered |
| 2 | Acquire coal OHLCV for R2 |
| 3 | R3 only after a survivorship assessment |

Calendar: Dec 2026 MVP-B2 origins; **10 Jan 2027** ITMG forecast run; **8 Mar 2027** evaluation.
