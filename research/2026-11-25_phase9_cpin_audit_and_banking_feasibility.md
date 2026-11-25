# Phase IX — Final CPIN PIT Audit and Indonesian Banking Feasibility

_Date: 2026-11-25._

_Code: `quant/cpin_pit_v2.py`, `quant/bank_feasibility.py`; tests in `tests/test_cpin.py` and `tests/test_bank_feasibility.py`._

_Decisions: D-032 (CPIN), D-033 (banking). Palm oil is unchanged: NO TRADE; TAPG, LSIP and DSNG on WATCH, STAA on AVOID._

**Three kinds of evidence are kept separate throughout:**
1. **Software tests** check that code is correct (48 pass).
2. **Forecast accuracy** is out-of-sample error against benchmarks. None is validated yet.
3. **Realised investment alpha** means returns earned. None is measured or claimed.

---

## Priority 1 — Final CPIN methodology audit (v1 results preserved; v2 written alongside)

| Issue | Finding | Correction |
|---|---|---|
| FY2023 from FY2024 comparatives | The 2023 Annual Report (S-061, filed on IDX 29 Apr 2024) gives rounded FY2023 segment results. Broiler −0.42tn and DOC −0.30tn agree with the comparatives, but **feed is 4.11tn in AR2023 vs 4.556tn in the FY2024 comparative**. FY2022 feed (3.33tn) matches its original exactly. | The FY2023 values cannot be independently verified, so they are dated to the **FY2024 filing (18 Mar 2025 20:35 WIB → available 19 Mar 2025)**, not 31 Mar 2024. |
| Deadline vs actual filing | IDX timestamps (jejaksaham mirror, S-060) exist only from **Jul 2023** (2023Q2 onward). | **Actual dates** for 2023Q2–2026Q3, using A-018 (filed after 09:00 → next trading day). Earlier quarters stay at the **regulatory deadline**, flagged "actual unverified". Actual availability fell 4 days before to 12 days after the deadline. |
| Predictor publication | PIHPS daily figures are final by 13:00 WIB, and there is no vintage archive, so revisions are **unverifiable**. The World Bank CMO is a single vintage (downloaded 2026-11-24) and is revised historically. | Every forecast date was checked to fall after the quarter's last CMO month was published (allowing 7 days): **0 violations in 35 quarters**. The revision risk is documented, not removable. |
| 2020 restated basis | Only available from the 2021 interim filings. | Unchanged (already enforced). |

**Rerun with the corrected dates** (`CPIN_walkforward_metrics_v2.csv`):

| | n | Ratio (MAE / benchmark MAE) | DM t | Verdict |
|---|---|---|---|---|
| H1 broiler (pre-registered) vs best benchmark (mean) | 18 | 1.24 | −0.73 | **Still fails** |
| H2 broiler (post-hoc) vs last quarter | 13 | 0.65 | 2.41 | Diagnostic only |
| H2 broiler vs seasonal | 13 | **1.15** | **−0.52** | **Worse than seasonal** |
| H2 broiler vs mean | 13 | 0.73 | 1.31 | Diagnostic only |

The PIT corrections **weaken** H2: against the mean, DM t falls from 2.04 to 1.31. Comparing against all benchmarks shows that H2 is worse than the simple seasonal rule. H2 was never evidence and is now even less promising.

**H2 frozen** (`CPIN_H2_frozen_spec.json`):
- **Model:** m = −0.5593 + 2.5847e-5 × spread (IDR/kg), fitted on 2020Q1–2026Q3 (n = 27).
- **Predictors and timing** are fixed as specified in the file.
- **Benchmarks:** last quarter, seasonal and expanding mean.
- **Pass rule:** at n ≥ 12 prospective quarters, MAE ≤ 0.85 × **each** benchmark **and** DM t ≥ 1.65 against the best.
- **Kill rule:** at n = 8, kill if worse than the best benchmark.
- **Journal:** 2026Q4 rows are appended for the seasonal benchmark (15.8%) and for the frozen-rule forecast, which is computed at its forecast date. The original 10.0% entry is kept.
- No re-estimation or re-specification on the historical sample.

---

## Priority 2 — Bank-only monthly data feasibility (tested, not listed)

### Access and coverage, 2018–2026 (`bank_monthly_coverage.csv`, `bank_monthly_inventory.csv`)

| Bank | IR source | How listed / accessed | Monthly reports 2018–26 | Non-quarter-end months | Publication timestamp | Median lag after month end |
|---|---|---|---|---|---|---|
| BBRI | ir-bri.com yearly pages (S-062) | Static HTML; PDFs scriptable | 79 | 69 | **IR posting date, 2018+** (79 dated) | 27 days (≈ 25 days since 2024) |
| BBCA | bca.co.id report list (S-063) | Next.js server action (browser); PDFs scriptable | 81 | 70 | **Filename date prefix, 2020+** (56 dated); none before 2020 | 29 days before 2024 → **13.5 days since Jul 2024** |
| BMRI | bankmandiri.co.id monthly-financials (S-064) | Static HTML per year; PDFs scriptable | **106 (all 12 months)** | 71 | Upload epoch `?t=` (last-modified, a conservative upper bound), 2021+ | 23–27 days (2026: 9 days for non-quarter-end months) |
| BBNI | bni.co.id financial-reports (S-065) | JS page; **scripted download times out on a redirect**, browser works | 80 | 70 | **None** in the listing; Last-Modified dates are a 2022 migration (only 2026 plausible) | Unknown → use the regulatory deadline (end of the following month) |

- **Format:** POJK 37/2019 / SE OJK 9/2020. From 2021, BBCA, BBRI and BBNI publish **only non-quarter-end months** monthly; quarter-end months come with the quarterly publication. BMRI still publishes all 12 months.
- **Gaps:** a few months are missing (e.g. BBCA Jul-2019, listed as a duplicate June), plus Oct-2026 not yet posted for BBNI and BBRI.
- **Revisions exist:** e.g. BRI "January 2020 – Revised" and "June 2019 (audited)", and BMRI "REV 8 … Februari 2026". Every vintage must be dated.

### Content (sample PDFs: 2018-02 and 2026-02 for BBCA, BBRI, BMRI; BBNI verified via browser)

| Item | Monthly report (bank-only, "INDIVIDUAL") | Quarterly publication |
|---|---|---|
| Interest income, interest expense, NII | ✔ (YTD cumulative) | ✔ bank-only **and** consolidated |
| Impairment / provision expense | ✔ ("impairment losses on assets") | ✔ |
| Operating profit; pre-provision operating profit | ✔ operating profit; PPOP **derivable** (operating profit + impairment) | ✔ |
| Net profit (current-period profit) | ✔ | ✔ |
| Loans; deposits (current / savings / time), so CASA | ✔ balance sheet | ✔ |
| Earning assets | Partly (line-level) | ✔ |
| NPL, coverage, NIM, CAR | ✘ **not in the monthly format** | ✔ ratios (bank-only) |
| Consolidated figures | ✘ | ✔ |

### Monthly-to-quarterly reconciliation (BBRI 1Q26 example)

- **Within bank-only:** Feb-26 YTD bank-only NII is 19.14tn; the Q1 bank-only NII is 29.47tn. Month 3 is therefore derivable as 10.32tn, against a 2-month average of 9.57tn. Bank-only YTD figures chain consistently.
- **Bank-only vs consolidated:** **BBRI bank-only NII is 73% of consolidated** (29.47 vs 40.16tn), because Pegadaian, PNM and other subsidiaries are material. The monthly data therefore cannot observe about 27% of BBRI's NII. The gap is expected to be small for BBCA and BBNI, and material for BMRI (BSI and other subsidiaries); this needs to be measured in the MVP.
- **Data-quality note:** the Feb-26 BRI P&L header says "January 1 to February 28, **2025**", a template error. Values must be cross-checked against later comparatives.

### Timing (is the monthly data early enough?)

- **Consolidated quarterly filings** (IDX timestamps, 2024+): median 22 days after quarter end (BBCA), 26.5 (BBNI), 29 (BMRI), 30 (BBRI).
- **Month 2 of each quarter** is published about 13–28 days after that month ends, i.e. roughly at or before quarter end. That is **3–7 weeks before the consolidated quarterly results**, with 2 of 3 months of bank-only P&L already known.
- **Month 3** is not published monthly (except by BMRI), so the third month must be forecast.

### Historical analyst expectations

- **Not available historically.** Yahoo/S&P provides only a current snapshot. BMRI's IR site has a consensus page, but it shows the current table only (its history is unverified).
- Monthly bank results are **reported by the press within about a day** (Kontan and Bisnis headlines such as "Laba BBNI … per Agustus 2026"), so the information is widely disseminated.

---

## Priority 3 — Predictive hypotheses (specified, not tested)

| # | Target (quarterly, consolidated unless stated) | Mechanism | Information available at forecast time | Horizon | Benchmark | Main confounders |
|---|---|---|---|---|---|---|
| B1 | Net profit | YTD bank-only months 1–2 capture ~2/3 of bank-only quarterly profit; third month ≈ run-rate | Month-2 report (≈ quarter end) | 3–7 weeks before results | Same quarter last year × YTD growth; last quarter; consensus (forward only) | Subsidiary share (BBRI ~27% of NII), month-3 one-offs (provision true-ups, tax, dividend income), quarter-end accounting |
| B2 | Net interest income | Balance-sheet volumes × spread move slowly; NII is the least noisy line | Same | Same | Last quarter; seasonal | Rate changes (BI hikes 2026), asset-yield repricing lags |
| B3 | NIM | Derived: annualised NII ÷ average earning assets (bank-only) | Same | Same | Last quarter's NIM | Earning-asset definition differs from the reported NIM; subsidiaries |
| B4 | Provision expense | Monthly impairment run-rate | Same | Same | Last quarter; seasonal | **Quarter-end provisioning** (ECL model runs, management overlays) concentrates in month 3 |
| B5 | Credit cost | Provision ÷ average loans | Same | Same | Last quarter | As for B4; NPL only quarterly |
| B6 | Analyst EPS revisions | Analysts update after monthly releases; a gap between the nowcast and consensus predicts revisions | Requires consensus **history** | Weeks | No revision | **Untestable historically** (no consensus history); forward logging only |

**Caution:** an accurate nowcast is not alpha. The data are public, press-covered and followed by sell-side analysts. A trading edge would require that consensus or prices **lag** the monthly information. That cannot be tested historically without consensus history; prices can be tested with an event study around the dated monthly releases (BBRI 2018+, BBCA 2020+).

---

## Priority 4 — Research decision gate

| Criterion | Assessment |
|---|---|
| Historical completeness | **High.** ~80 monthly reports per bank, 2018–26 (106 for BMRI); quarterly publications available. |
| PIT reliability | **Medium.** BBRI is dated 2018+, BBCA 2020+, BMRI 2021+ (conservative epochs); **BBNI is undated** (deadline proxy). Revised vintages exist. Quarterly IDX timestamps exist only from 2023/24. |
| Independent forecast periods | Consistent format and accounting (SE OJK 9/2020; PSAK 71 from 2020) supports **≈ 23 quarters per bank (2021Q1–2026Q3)**. Pooled across 4 banks that is ~92 bank-quarters, but macro shocks are shared, so the effective number of independent periods is **≈ 23**. |
| Accounting consistency | Breaks: PSAK 71 (2020); the 2020–21 format change; BBRI holding restructure (Pegadaian/PNM, 2021); the BSI merger (2021); COVID restructuring (2020–23). Using 2021+ avoids most of them. |
| Collection cost | **Moderate.** ~370 small, standardised PDFs (0.1–1.2 MB). BBNI and the BCA listing need the browser; PDF parsing has to handle 2–3 layouts. |
| Information advantage | **Low a priori.** The data are public and press-covered within a day. Any edge would come from systematic **modelling** of month 3 and subsidiaries, not from access. |

### Decision: **CONDITIONAL GO** for one minimal, pre-registered forecasting experiment (D-033)

This is **not** a GO on alpha, a valuation model or a trading system.

**MVP-B1 (pre-registered 2026-11-25; not started).**
- **Universe:** BBCA (bank-only ≈ consolidated) and BBRI (large subsidiary gap: the contrast case), 2021Q1–2026Q3, about 23 quarters each.
- **Data:**
  - Monthly bank-only months 1–2.
  - Quarterly bank-only and consolidated publications.
  - BBRI posting dates and BCA filename dates; quarterly IDX timestamps where available.
- **Targets:** quarterly consolidated net profit (primary) and NII (secondary).
- **Model (fixed in advance, no ML):**
  - Bank-only quarter = YTD(m2) − YTD(prior quarter end) + 0.5 × (that difference), i.e. month 3 = average of months 1–2.
  - Consolidated forecast = bank-only forecast × (consolidated / bank-only ratio from the latest reported quarter).
- **Benchmarks:** (a) same quarter last year × (1 + YTD year-on-year growth known at the forecast date); (b) last quarter.
- **Forecast date:** the later of the month-2 publication date and quarter end.
- **Pass rule (per bank):** on ≥ 16 out-of-sample quarters, MAE ≤ 0.85 × best benchmark **and** DM t (HAC) ≥ 1.65. Results are reported by bank, not pooled.
- **Kill rule:** the banking track stops if neither bank passes on net profit.
- **What a pass would and would not show:**
  - A pass shows **forecast accuracy only**.
  - Any alpha claim needs a second, separately pre-registered stage: an event study of returns around monthly releases and quarterly results, plus forward consensus logging.
- **Prerequisite started now:** BBCA, BBRI, BMRI and BBNI are added to the append-only consensus-snapshot universe (`quant/tapg_monitor.py`). This builds the forward consensus history that B6 needs, at no extra infrastructure cost.

**Not in scope:** BMRI and BBNI in the MVP (subsidiary gap; undated BBNI), any valuation model, trading system, dashboard or database.

_Sources:_
- _S-060 jejaksaham.id mirror (CPIN, BBCA, BBRI, BMRI, BBNI)_
- _S-061 CPIN Annual Report 2023_
- _S-062 BRI IR_
- _S-063 BCA IR_
- _S-064 Bank Mandiri IR_
- _S-065 BNI IR_
- _S-054 PIHPS; S-003 World Bank CMO_
