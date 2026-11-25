# M-VIII-1 — CPIN Segment-Margin Walk-Forward Test (pre-registered, D-029)

_Date: 2026-11-25._

_Code: `quant/cpin_segments.py`, `quant/cpin_walkforward.py`; tests in `tests/test_cpin.py`._

_Data: 34 CPIN interim/annual FS PDFs (2018Q1–2026Q3) from cp.co.id (S-055; downloads approved by the user; git-ignored in `data/raw/company/CPIN/`), plus PIHPS (S-054) and the World Bank CMO (S-003)._

> **Result: H1 FAILS the pre-registered kill rule. The poultry pilot stops (D-031).** NO TRADE is unchanged.

## 1. Dataset built

- **Source:** the segment note ("Informasi Segmen") in each report. Segments are feed, broiler, DOC, processed chicken and others; for each we extract sales and segment result (gross profit less allocated selling and G&A).
- **Reconciliation:** all 38 extracted tables (34 current plus 4 comparatives) reconcile to consolidated figures within IDR 1m (test).
- **Basis break:** the FY2020 FS restated the segment presentation.
  - FY2019 consolidated sales fall from 58.6tn to 42.5tn.
  - Results are reallocated between segments (FY2019 broiler result moves from −1,565bn to −528bn).
  - So 2018Q1–2019Q4 are on the **old** basis, and 2020Q1 onward on the **new** basis.
  - 2020Q1–Q3 on the new basis come from the comparatives in the 2021 interims, which were available only from 2021.
  - No margin change is computed across the break.
- **Missing file:** FY2023 is not on cp.co.id. It is taken from the FY2024 comparatives and treated as available on its own regulatory deadline, 31 Mar 2024 (A-038).
- **Result:** 35 standalone quarters (`CPIN_segments_quarterly.csv`). Broiler margin ranges from −25.4% (2021Q3) to +15.8% (2025Q4).

## 2. Pre-registered test (specified before fitting)

**Model (H1):**
- Δm_q = a + b₁·Δspread_q + b₂·Δlog(USD/IDR)_(q−1) + e.
- Forecast m̂_q = m_(q−1) + Δm̂.
- spread = PIHPS producer chicken price − feed proxy.

**PIT and walk-forward design:**
- Each forecast is made the day before quarter q's filing deadline.
- Only observations available before that date are used, with an expanding window and a minimum of 12 training pairs.
- **20 out-of-sample quarters, 2021Q4–2026Q3.**

**Kill rule:** model MAE ≤ 0.85 × the best benchmark's MAE **and** Diebold-Mariano t (HAC) ≥ 1.65, on n ≥ 16 quarters.

| Target | Model MAE | Best benchmark (MAE) | Ratio | DM t | Pass? | In-sample spread t (HAC) |
|---|---|---|---|---|---|---|
| **Broiler margin (primary)** | 7.06pp | expanding mean (5.80pp) | **1.22** | **−0.76** | **No** | 2.74 (R² 0.27, n 33) |
| Consolidated segment margin | 3.37pp | expanding mean (3.93pp) | 0.86 | 0.66 | No | 3.36 (R² 0.45) |
| DOC margin | 9.86pp | expanding mean (9.95pp) | 0.99 | 0.05 | No | 3.46 |
| Feed margin | 1.90pp | last quarter (1.77pp) | 1.07 | −1.28 | No | −1.36 |

Other benchmarks for broiler: last quarter 7.92pp, same quarter last year 6.88pp. All MAE, RMSE and bias figures are in `CPIN_walkforward_metrics.csv`.

**Interpretation:**
- The chicken-minus-feed spread is **economically and statistically associated** with segment margins in sample (t 2.7–3.5).
- It does **not** forecast better than naive rules out of sample. The first-difference form anchors on last quarter's margin, which is the weakest anchor because margins mean-revert.
- This is exactly the "plausible ≠ predictive" case the methodology guards against.

## 3. Post-hoc diagnostic (not decision-relevant)

A levels model (m_q = a + b·spread_q, same PIT walk-forward, new basis only) was **specified after H1 failed**:

| Target | Levels-model MAE | Mean MAE | DM t | n |
|---|---|---|---|---|
| Broiler | 4.34pp | 6.42pp | 2.04 | 15 |
| Feed | 1.08pp | 1.53pp | 2.48 | 15 |
| Consolidated | — | — | 0.23 | 15 |
| DOC | — | — | −0.16 | 15 |

These results are **not evidence**: the same data informed the specification, and n = 15 is below the 16-quarter minimum. They justify only a new hypothesis, **H2 (levels)**, to be tested on data it has not seen:
- **(a) Forward on CPIN.** First forecast logged in the journal:
  - **CPIN 2026Q4 broiler margin, H2: 10.0%.** The spread uses partial data (chicken Oct–Nov, feed proxy Oct only).
  - Benchmarks: expanding mean 2.2%; last quarter 11.1%.
  - Resolves with the FY2026 FS (~Mar 2027).
- **(b) Independent replication on JPFA's commercial-farm segment.** This needs JPFA's 2018–2026 quarterly statements, which are only available from IDX by manual download.

## 4. Decision and next step

- **D-031:**
  - H1 is killed and the poultry pilot stops under the pre-registered rule.
  - H2 is registered for forward and independent tests only.
  - No capital, rating or position is implied. NO TRADE (D-028) stands.
- **Next-milestone options** (the user's choice):
  1. **JPFA replication of H2.** Low cost; the user supplies about 35 JPFA quarterly FS from IDX. Pre-registered rule: levels-model MAE ≤ 0.85 × mean and DM t ≥ 1.65 on ≥ 16 quarters.
  2. **Banking feasibility.** The alternative named in D-029, now that the poultry kill test has failed. Starts with testing monthly bank-only report access for 4 large banks.
- **Palm oil:** unchanged. First out-of-sample resolutions arrive in Feb–Mar 2027 (C-020); TAPG and LSIP monitoring continues.
