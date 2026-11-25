# Phase XV — First Direct Return Experiment: DR-R1 Palm CPO-Impulse Timing

_Date: 2026-11-25._

_Code: `quant/dr_r1_audit.py`, `quant/dr_r1_backtest.py`; tests in `tests/test_phase15.py`._

**Order of work, each step committed before the next:**
1. Specification `DR_preregistration.json` (4a94d00).
2. Point-in-time audit and implementation note `DR_R1_implementation.json` (e56ed1a), **committed before any return was computed**.
3. Results.

_Decision: D-045._

> ## Decision: **NO-GO**
>
> R1 fails **all four** registered pass conditions. Per the registration, the experiment stops: no parameter changes, no paper tracking.
>
> | Registered condition | Required | Result |
> |---|---|---|
> | Annualised net excess vs palm basket | ≥ +3% | **−5.0%** (CAGR difference −3.7pp) |
> | Holm-adjusted HAC p (family R1–R3) | ≤ 0.05 | **1.00** (raw one-sided p 0.85, t −1.02) |
> | Positive in both halves | both > 0 | **−7.8% / −2.3%** |
> | Max drawdown no worse than benchmark | ≥ −54.7% | **−56.9%** |
>
> Every robustness variant also fails.
>
> **Preserved unchanged:** ITMG C1/I1, CPIN H2, MVP-B2 and palm-oil NO TRADE.

## 1. Point-in-time audit (`DR_R1_pit_audit.json`)

| Item | Finding | Status |
|---|---|---|
| **CPO publication** | Eight archived CMO vintages (2026): month m−1 was present 3–24 days after month end. The signal for holding month t+1 uses CPO(t−1)/CPO(t−2) at the **close of the last trading day of t**, at least a week after publication. | OK (2026 evidence only; pre-2026 release dates not archived) |
| **Vintage revisions** | 2026 vintages revised recent months by up to USD 58/t (Mar 2026 first release). The sign of the first-released change matched the final sign in 6 of 6 vintages. History uses the current vintage. | **Limitation:** residual revision look-ahead before 2026 |
| Signal and execution dates | Formation date = execution close = last IHSG trading day of t. PIT membership dates coincide with it. | OK |
| Universe and liquidity | Membership comes from `pit_universe_monthly.csv`, using only data up to t: seasoning ≥ 60 sessions, traded in the last 20 sessions, 63-session median traded value ≥ IDR 1.5bn. 3–16 names per month. | OK |
| Corporate actions | Yahoo Adj Close (split- and dividend-adjusted, **gross** of the 10% dividend tax). BTEK shows ±50–100% one-tick moves at very low prices (2024). | **Limitation:** dividend-tax drag not modelled; BTEK data quality |
| Missing or suspended | 158 of 1,045 member-months contain zero-volume sessions, mostly liquid names (holiday rows in Yahoo). These are treated as 0% return days. | Diagnostic run (below) |
| **Survivorship** | GOLL (suspended 2019) and MAGP (suspended 2022) have no prices. The suspension filter would have excluded them while suspended, but earlier trading is unobserved. Palm names delisted before 2015 or missing from Yahoo are unknown. BTEK and PALM have unverified palm exposure. | **Limitation (unresolved)** |
| IHSG total return | Not available (^JKSE is a price index). | Supplementary comparisons are price-only |
| Cash | BI-Rate decisions from Bank Indonesia (S-072). March–April 2016 use the first BI 7-day reverse repo value (5.50%; the old BI Rate was 6.75%). | Flagged; immaterial |

**Engine check:** the gross basket reproduces the existing `benchmarks_daily.csv` palm basket to within 4×10⁻⁶ per month over all 128 months.

## 2. Registered strategy and primary benchmark (net, 2016-03 to 2026-10, 128 months)

| | R1 strategy | Palm basket (registered benchmark) |
|---|---|---|
| Final wealth (start 1.0) | 0.86 | 1.27 |
| CAGR | −1.4% | +2.3% |
| Annualised volatility | 21.6% | 27.5% |
| Sharpe (vs cash) | −0.16 | 0.05 |
| Sortino | −0.22 | 0.08 |
| Max drawdown | −56.9% | −54.7% |
| Calmar | −0.03 | 0.04 |
| Turnover (per year, traded value / NAV) | 546% | 245% |
| Transaction costs (per year) | 2.07% | 0.73% |
| Time invested | 58.6% (49 switches) | 100% |
| Monthly return: mean, median | +0.08%, +0.03% | +0.50%, −0.11% |
| Monthly return: 5% / 95% | −9.1% / +8.5% | −9.8% / +16.2% |
| Monthly hit rate; skew | 51%; −0.18 | 48%; +0.28 |

**The shortfall is not mainly costs:** the gross-of-cost excess is also negative (**−3.7% a year**).

Block-bootstrap 95% CI of the annualised excess: **[−15.9%, +2.9%]**. P(mean ≤ 0) = 0.90.

Charts and data:
- Equity curve and drawdowns: `outputs/DR_R1_equity_drawdown.png`.
- Monthly signal and portfolio history: `DR_R1_monthly.csv`.

## 3. Supplementary comparisons (not part of the decision)

| Portfolio | CAGR | Max drawdown |
|---|---|---|
| Passive palm basket, gross of costs | +3.0% | −53.5% |
| IHSG (price only) | +0.5% | −41.5% |
| Money market (BI-Rate − 0.5pp) | **+4.6%** | 0% |
| Constant mix: 58.6% basket / 41.4% cash, monthly rebalanced | +4.0% | −31.5% |

- R1 underperforms the constant-mix portfolio with the **same average equity exposure** by **4.3% a year** (t −1.11).
- Its lower volatility comes from **holding less equity**, not from timing.
- Over this decade, palm equities did not beat cash.

## 4. Risk attribution (net strategy return over cash, Newey-West lag 3)

| Model | Exposures | Alpha (annual) |
|---|---|---|
| Basket beta | β = 0.62 (t 6.1) | −4.5% (t −1.16) |
| CAPM (IHSG) | β = 0.71 (t 3.9) | −1.6% (t −0.31) |
| Market + sector + commodity | IHSG 0.68 (t 5.7); sector 0.61 (t 5.7); contemporaneous CPO −0.07 (t −1.2) | −3.8% (t −1.02) |
| Treynor-Mazuy timing | γ = −1.05 (t −2.05) | — |
| Henriksson-Merton timing | up-market −0.38 (t −1.91) | — |

**Where the performance comes from:**
- Returns are explained by **reduced equity exposure** (β ≈ 0.6) plus market and sector beta. There is no positive timing ability and no commodity exposure beyond the basket.
- The basket's average excess over cash was **−0.26% a month when R1 was invested** and **+0.67% a month when R1 was in cash**, so the signal mildly mistimed.
- Both timing coefficients are negative. This is **not** a licence to trade the reversed signal: that would be a post-hoc specification selected on this sample (D-031), and could only be registered for independent prospective testing.

## 5. Robustness (report-only; none replaces the primary result)

| Variant | Annual excess vs basket | Holm p | Passes? |
|---|---|---|---|
| Execution delayed 1 trading day | −3.7% | 1.0 | No |
| Costs ×2 | −6.4% | 1.0 | No |
| Exclude BTEK and PALM (unverified palm) | −5.4% | 1.0 | No |
| Exclude member-months with ≥ 3 zero-volume days (ex-post diagnostic) | −4.7% | 1.0 | No |
| Cash = BI-Rate | −4.8% | 1.0 | No |
| Cash = interbank call money (FRED/OECD) | −4.9% | 1.0 | No |
| Cash = 0 | −6.9% | 1.0 | No |

The survivorship bias (unobserved delisted names) cannot be quantified with the data available. It would mostly affect the level of both portfolios, not the timing difference.

## 6. Multiple testing

- **Registered family (R1–R3):** R2 and R3 are untested and enter as p = 1. The family is **not** reduced, so the adjusted p(R1) = min(1, 3p) = 1.0.
- **Programme-wide** (`programme_multiplicity_v3.csv`, 17 tests): ITMG C1 still survives (Holm p 0.013); R1 is p = 1.0.

## 7. Decision and next steps

- **NO-GO.** All results and code are preserved, and the specification is unchanged. No paper trading. The experiment stops.
- R2 (coal Newcastle impulse) and R3 (liquid IDX 12-1 momentum) remain registered and untested. This milestone did not execute them.
- **What the result says:** a public, monthly, one-month-lagged CPO impulse is not a usable long-only timing signal for liquid Indonesian palm equities after costs.
- **Prospective calendar unchanged:**
  - Dec 2026: MVP-B2 origins.
  - 10 Jan 2027: ITMG forecast run.
  - 8 Mar 2027: ITMG evaluation.

_Sources:_
- _S-002 Yahoo (prices)_
- _S-003 World Bank CMO (CPO), with vintages_
- _S-072 Bank Indonesia BI-Rate_
- _S-073 FRED/OECD call money (robustness only)_

_This is a historical backtest. It is not evidence of alpha and not investment advice._
