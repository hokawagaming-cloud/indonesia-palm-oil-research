# Phase VII — Institutional Investment Decision

_Date: 2026-11-25 · Prices: IDX close 24 Nov 2026 · Code: `quant/final_decision.py` (tests `tests/test_final_decision.py`)._

_Outputs in `data/reference/research/`: `final_market_assessment.csv`, `LSIP_valuation_methods.csv`, `LSIP_joint_adverse.csv`, `final_opportunity_cost.csv`, `final_scorecard.csv`, `final_decision_summary.csv`._

_Tags: OBS = filing or market data · DER = derived · EST = assumption or judgement. This is research analysis, not personal advice._

> **Final decision: NO TRADE.**
> - TAPG: **WATCH**
> - LSIP: **WATCH**
> - DSNG: **WATCH**
> - STAA: **AVOID**
>
> No name meets all three BUY conditions: the return hurdle, the evidence quality and an acceptable downside.

---

## 1. Fundamental and predictive edge

**Our differentiated view vs consensus (S&P via Yahoo, S-036):**

| | Q4 2026 profit to owners: ours (base) vs consensus-implied | FY2027 gap | Where the value debate really is |
|---|---|---|---|
| TAPG | 1,209 vs ≈ 720bn (**+68%**) | **−9%** (4,062 vs 4,473) | FY27 earnings normalisation. Q4 is a timing item. |
| LSIP | 468 vs ≈ 360bn (**+30%**) | **≈ 0%** (2,200 vs 2,210) | **How much the market credits the 8.5tn cash.** Earnings matter less. |
| DSNG | ≈ 600 vs ≈ 796bn (**−25%**) | n/a | Consensus already prices the shipment catch-up. |
| STAA | ≈ 590–720 vs 469bn (+26–54%) | n/a | One analyst, refinery data missing. |

**Where our view differs:**
- On LSIP, earnings are not where the edge is. The Q4 beat comes from inventory release and seasonality, and FY27 is in line with consensus.
- What drives 12-month value is whether the market keeps valuing the cash at about 100%. That depends on governance and capital return, and we have no predictive evidence on either.
- In the 12 months to 24 Nov, LSIP's residual return after market and sector was already **+26%** (§2). Much of the 2026 re-rating has happened.

**Leading indicators and their measured reliability** (penalised below for small samples):

| Indicator | Evidence | Reliability verdict |
|---|---|---|
| TAPG Q4 nowcast (product-level) | PIT validation n = 2; MAPE for profit 23–27%; biased low (under-forecasts) | **Unvalidated.** n = 2 is not evidence. |
| LSIP Q4 nowcast | n = 0 (no history yet) | **Unvalidated** |
| Earnings surprise → share reaction | Rank correlation +0.21, n = 8 events; CAR σ 4.4% | **No tradable reaction** |
| Residual momentum (sector cross-section) | Mean IC +0.04, t = 0.93, 100 months, about 7.5 names | **Not significant** |
| CPO price lead → TAPG excess return | R² 0.04, n = 64 | **No usable lead** |
| Consensus EPS revisions → post-results returns | Rank correlation 0.02, n = 7 | **No explanatory power** |
| Sector CPO beta (shown in §2) | t = 1.2–2.1 | Weak, contemporaneous only |

**Penalty applied.** No indicator in this project has a validated out-of-sample record, so predictive-edge scores are capped at 3 (TAPG) and 1–2 (the others). The scenario probabilities (30/50/20) are judgement, not estimates.

## 2. Quantitative market assessment

Data:
- Weekly returns over 3 years for market and sector betas.
- Monthly returns over 5 years for factor exposures (IHSG, World Bank CPO in USD, USD/IDR).
- Prices are Yahoo adjusted closes (S-002, unofficial).
- IHSG is a price index, so alphas are overstated by about 2–3pp a year (IHSG's dividend yield).
- The sector index is the equal-weight core PIT index (about 11 names) and includes each stock itself.

| | TAPG | LSIP | DSNG | STAA |
|---|---|---|---|---|
| Market beta (IHSG, t-stat) | 0.53 (4.0) | 0.76 (6.1) | 0.59 (3.8) | 0.46 (3.6) |
| Sector beta (excess of IHSG, t-stat) | 0.96 (9.3) | 1.01 (11.0) | 1.14 (9.0) | 0.90 (8.9) |
| R² (market + sector) | 0.42 | **0.55** | 0.40 | 0.39 |
| CPO beta, monthly (t-stat) | 0.22 (1.2) | 0.28 (1.8) | 0.54 (2.1) | 0.08 (0.5) |
| USD/IDR beta (t-stat) | 0.11 (0.1) | −0.09 (−0.1) | 0.12 (0.1) | −0.63 (−0.9) |
| Factor-adjusted alpha, annualised (t-stat) | 42% (2.6)* | 13% (0.95) | 38% (1.7) | 22% (1.6) |
| Residual return, last 12m | −23% | **+26%** | −33% | −18% |
| Momentum, 12-1 | +19% | +14% | −11% | −16% |
| Relative strength vs sector, 6m | +1% | +7% | −13% | −10% |
| Realised volatility, 1y | 52% | 40% | 53% | 38% |
| Median traded value, 20d (IDR bn/day) | 15.8 | 11.9 | 3.2 | 1.2 |
| Traded value, 20d vs Jul–Sep | 0.53× | 1.00× | 0.45× | 0.22× |
| Turnover z-score, 20d vs 1y | −0.7 | −0.3 | −0.7 | −0.9 |
| Correlation with TAPG, daily 1y | 1.00 | 0.63 | 0.65 | 0.51 |

\* TAPG's alpha is dominated by its 2021–24 post-IPO re-rating and the missing IHSG dividends. It is not evidence of persistent company-specific alpha.

**Alpha vs systematic risk:**
- All four names are mainly **sector bets**: sector beta is about 1 and t-stats are 9–11.
- LSIP's residual alpha over 5 years is not significant (t = 0.95). Its strong last 12 months (+26% residual) is a re-rating that has already happened, not an edge we can forecast.
- **Crowding:** none is visible. Turnover is below its 1-year average for every name.
- **Investor positioning and foreign flows:** unavailable; no reliable free source was found (Phase IV). No inference is drawn.

## 3. Catalysts and investment horizon

| Catalyst | Date | Repricing mechanism | Leading indicator | P(realised) EST | Expected reaction EST | If delayed or failed |
|---|---|---|---|---|---|---|
| **LSIP C-019:** buyback execution (≥ 25% of 750bn) | Programme runs 26 Oct–31 Dec; report early Jan 2027 | Fewer shares (up to −7%); a signal of capital return supports cash credit | Daily volume footprint (none so far: 1.00×); IDX treasury-share disclosures | 45% | +0–5% | Expected return 17.1%. Confirms cash is trapped; cash credit at risk. |
| **LSIP C-020:** FY26 results, Q4 > 450bn | ~late Feb 2027 | Q4 beat → FY27 upgrades | KPBN/MPOB prices for Nov–Dec; TAPG Q4 as a read-across | 50% | 0 to +3% (results reactions are untested for LSIP; TAPG analogue shows none) | A Q4 below 360bn risks FY27 cuts. Bear case. |
| **LSIP C-021:** payout ≥ 50% at the AGM | ~Jun 2027 | Cash becomes accessible → cash credit rises, operations re-rate toward peers | Board or parent (SIMP) commentary; SIMP's own cash needs | 15% | +15–30% | Status quo (30%). No repricing. |
| **TAPG C-020-equivalent:** FY26 results | by ~31 Mar 2027 | Q4 beat offset by the FY27 gap | Q4 newsletter (S-033), HRef decrees | n/a | ≈ 0 (n = 8 shows no reaction) | n/a |
| **Sector C-013:** B50 review outcome | Undated (2027) | Domestic CPO demand and levy | Ministry of Energy (ESDM) statements | Unknown | Sector-wide ±5–10% | Not company-specific |

**Short-term vs long-term:**
- **Tactical (≤ 3 months):** no opportunity. Results-reaction evidence is nil (n = 8, ρ = 0.21), and LSIP's Q4 beat is a timing item.
- **Fundamental (12 months+):** the only large catalyst is a change in LSIP's capital allocation (C-021). It is low-probability, controlled by the majority shareholder and not forecastable from our data.

## 4. Valuation robustness (LSIP; IDR per share, 12 months forward)

Rules applied to avoid double counting:
- Profit is **stripped of after-tax interest income** (≈ 255bn a year: 9M finance income of 239bn, annualised, less the 20% final tax) whenever cash is added separately.
- The FY26 dividend is deducted from cash once and added to return once, net of 10% tax.
- The buyback reduces both cash and the share count.
- Cash in 12 months ≈ 8,516 + 1,800 generated − 664 dividend − 750 buyback ≈ 8.9tn.

| Method | Bear | Base | Bull | Probability-weighted return |
|---|---|---|---|---|
| **Cash-adjusted, market-calibrated** (cash 100% + 0.33/1.2/2.3× operating profit) | 1,484 | 1,772 | 2,182 | **+18.2%** |
| FCFE of operations (ke 12.5%, g 2%, conversion 0.85) + cash | 3,415 | 3,936 | 4,196 | +150% |
| DDM at the observed 30% payout (what a minority holder receives) | 811 | 991 | 1,081 | −34% |
| Normalised profit (FY22–26 average 1,475bn) × historical P/E (4.3/5.6/6.7×) | 900 | 1,303 | 2,324 | −6% |
| Peer P/E on operations (5.5×) + cash | 2,744 | 3,090 | 3,264 | +98% |

**Reverse valuation:**
- Market cap is 10.7tn, or 4.8× FY26 profit.
- If the cash is credited at 100%, the operations are valued at only **1.1×** their profit, i.e. an FCFE-implied sustainable operating profit of **265bn** against ≈ 1,960bn actual.
- If the operations are instead valued like peers (5.5×), the market is crediting the cash at **≈ 0%**.
- The split is not identified, but either way the market applies a governance and trapped-cash discount of ≈ 8–9tn (≈ IDR 1,250/share).

**What this means:**
- FCFE and peer methods show what LSIP would be worth to a controlling owner. A minority holder receives only the 30% payout (DDM ≈ 990).
- The 12-month return depends on the **market's** multiple, so the market-calibrated frame is the decision metric (+18.2% gross). The other methods bound long-run value: ≈ 990 to ≈ 3,900.
- **No extra governance discount is applied** on top of the market-calibrated frame. The market's discount already *is* that discount, and adding another would double count.

**Joint adverse scenarios** (`LSIP_joint_adverse.csv`):

| Joint scenario | Return |
|---|---|
| FY27 bear + 80% cash credit | **−18%** |
| FY27 base + 80% cash credit + no buyback | −1% |
| FY27 bear + 60% cash credit + no buyback | **−36%** |
| FY27 profit 1,500 + trough multiple + no buyback + 60% cash credit | **−37%** (normalised P/E method: −41%) |

The bear case alone (+0%) gives a misleading sense of safety. The cash floor protects only if the market keeps crediting the cash in full, and in FY22–23 it credited much less (EV/NP of 2–3× with cash at 56–74% of market cap).

**Probability-weight uncertainty** (Dirichlet, concentration 10):
- 5–95% range: **+11% to +26%**.
- P(> 17.5% hurdle) = **54%**; P(> ke 12.5%) = 90%.

**Hurdle sensitivity:**
- Since the hurdle was set (A-024), the 10-year SBN yield has risen to 7.7% (+154bp year to date) and BI has hiked to 6.00%.
- A ke 1pp higher (13.5%, i.e. an 18.5% hurdle) would **fail** LSIP outright.

## 5. Management and governance (LSIP)

| Dimension | Evidence | Assessment |
|---|---|---|
| Controlling shareholder | Majority-controlled by SIMP (Salim group); 75.8% of 9M26 sales go to SIMP (OBS, 9M FS) | Transfer-pricing risk; minority interests depend on the parent's cash needs |
| Capital allocation | Cash grew from 3.8tn (FY22) to 8.5tn (Sep-26) while the payout stayed ≈ 30%. Cash earns ≈ 4.0% pre-tax (≈ 3.2% after tax) against ke 12.5%. | **Poor for minorities.** Retaining ≈ 6tn of excess cash costs about 9pp a year in opportunity cost. |
| Related-party transactions | 665bn (7.8%) deposited at related-party Bank Ina Perdana, down from 1,640bn at Dec-25 | Improving, but still present |
| Buybacks | Earlier treasury shares cancelled in Sep 2024 (positive precedent); 2026 programme of 750bn with execution unverified | Some credibility; small relative to cash (9%) |
| Dividends | ≈ 30% payout, with no sign of change | Minorities' cash access is limited |
| Reinvestment returns | Not assessed: capex/replanting returns require Stage 2 | **Evidence gap** |
| Management credibility | Clear disclosure (core profit reconciliation, highlights); no guidance record to test | Neutral; untested |

Governance score: **2/5**. The governance discount is reflected through the market-calibrated frame, not added again.

TAPG (Triputra group; payout 85–105%; JV dividends of 959bn) scores **4/5**.

## 6. Opportunity cost (12 months, after tax and costs)

Rates and tax assumptions:
- **Rates:** 10-year SBN 7.735% (ADB AsianBondsOnline, 17 Nov 2026, S-052); BI-Rate 6.00% (Bank Indonesia, 18 Nov 2026, S-053).
- **Taxes (statutory, resident individual):** 20% on deposit interest, 10% on bond coupons, 10% on dividends.
- **Equity costs (EST):** 0.55% round trip, comprising 0.20% to buy, 0.25% to sell including the 0.10% sales tax, and 0.10% slippage.

| Asset | Expected net return | Volatility | Excess vs money-market fund | Excess per unit of volatility |
|---|---|---|---|---|
| Cash | 0.0% | 0 | −5.5pp | — |
| 12m IDR time deposit (EST 4.75% gross) | 3.8% | 0 | −1.7pp | — |
| Money-market fund (EST) | 5.5% | ≈ 0 | 0 | — |
| 10y SBN held for coupon (no price change) | 7.0% | ≈ 8% (EST) | +1.5pp | 0.18 |
| IHSG (rf + 5.5pp equity risk premium; EST, not a forecast) | 12.9% | ≈ 20% (EST) | +7.4pp | 0.37 |
| TAPG @1,710 | 4.3% | 52% | −1.3pp | −0.02 |
| DSNG @1,275 (uniform rule) | 15.4% | 53% | +9.9pp | 0.19 |
| STAA @1,015 (uniform rule) | 7.0% | 38% | +1.5pp | 0.04 |
| **LSIP @1,570 (market-calibrated)** | **17.6%** | 40% | +12.1pp | **0.30** |

LSIP's expected excess return per unit of risk (0.30) is **below a passive IHSG assumption (0.37)**. That comparison depends on an assumed equity risk premium, so it is indicative only. Even so, LSIP's extra return over the market is about 4.7pp a year for roughly twice the volatility, and it depends on governance.

**Conclusion:** none of the covered equities beats the alternatives on a risk-adjusted basis by a margin that would survive the evidence penalties. Money-market or SBN yields (5.5–7.0% net) are the default while waiting.

## 7. Portfolio construction

No investment qualifies, so the **recommended position is 0%**.

Rules for a **hypothetical** diversified IDR equity portfolio, to apply only if LSIP later passes the gate. These are not weights for any investor: we do not know their capital, holdings or risk tolerance.

- **Initial position:** 1.5%.
- **Maximum position:** 4%.
- **Risk budget:** at 40% volatility, a 4% position contributes ≈ 1.6pp of standalone volatility. Cap the name at ≤ 10% of the portfolio's tracking-error budget.
- **Concentration:**
  - Total palm-oil exposure (all names) ≤ 8%.
  - LSIP and TAPG correlate at 0.63, and both have sector beta ≈ 1 and positive CPO beta, so they count as one risk bucket.
- **Liquidity:** at 11.9bn/day median, trading ≤ 20% of daily volume allows ≈ 2.4bn/day. A 4% position in a hypothetical IDR 100bn portfolio takes about 2 days.

## 8. Trade execution (LSIP, conditional; no trade now)

- **Maximum entry price: IDR 1,579.** This is the 17.5% hurdle with cash credited at 100%, and applies **only if** C-019 shows material buyback execution.
- **Preferred entry range: IDR 1,340–1,460.** At these prices the hurdle is still met with cash credited at 80–90%, which makes the entry robust to the main fragility.
- **Staged entry:**
  - ⅓ at ≤ 1,460.
  - ⅓ at ≤ 1,400.
  - ⅓ only after C-019 or C-020 confirms.
- **Microstructure:**
  - The IDX tick at this price level is IDR 5 (≈ 0.32%). The spread is typically one tick, but there is **no order-book data**, so no precise spread is claimed.
  - Costs are EST at ≈ 0.55% round trip.
- **Do not execute if any of these holds:**
  - The buyback was not executed and the price is above 1,460.
  - FY27 consensus has been cut by more than 10%.
  - Median traded value is below 5bn/day.
  - Within 5 trading days before results.
  - The related-party bank share of cash rises again.

## 9. Exit and thesis invalidation (LSIP, if held)

- **Fundamental invalidation (permanent):**
  - Cash leaks to the parent (new related-party loans or deposits, or related-party cash above 15%).
  - The payout is cut below 25%.
  - Sales terms with SIMP worsen.
  - Operating profit falls below 1,500bn on a cost-structure change, as opposed to price.
- **Earnings downgrade threshold:** FY27 consensus EPS revision worse than −10% over 90 days → halve the position. Worse than −20% → exit.
- **Valuation exits:**
  - Take ½ at ≥ 1,850 (the base-case value).
  - Exit at ≥ 2,150 (the bull-case value).
- **Catalyst failure:** no material buyback execution (C-019) **and** no payout change at the AGM (C-021) → exit or re-underwrite by **Jun 2027**. Maximum review horizon: **12 months (Nov 2027)**.
- **Risk-based reduction:**
  - −15% from entry with no fundamental change → review; not an automatic sale.
  - −25%, or any invalidation trigger → exit.
- **Temporary vs permanent:**
  - A decline with cash intact (≈ IDR 927/share of excess cash) and consensus stable is **temporary**: a change in the multiple or cash credit.
  - Cash leakage, related-party abuse or cost inflation is **permanent impairment**.

## 10. Final scorecard

Scores are 1–5 judgements against stated criteria (`quant/final_decision.py: SCORE_RULES`). They are **not probabilities** and have not been validated empirically.

| Criterion (what a 5 requires) | TAPG | LSIP | DSNG | STAA |
|---|---|---|---|---|
| Fundamental quality (low cost, net cash, stable ROE) | 4 | 4 | 3 | 3 |
| Predictive edge (validated PIT indicator, n ≥ 12) | 3 | 2 | 2 | 1 |
| Expectations gap (> 15% on the year that drives value) | 2 | 2 | 1 | 3 |
| Valuation (E[R] > 25% across methods) | 2 | 3 | 3 | 2 |
| Catalyst quality (dated, high probability, mechanism shown) | 2 | 2 | 2 | 2 |
| Governance (aligned owner, high payout, no RPT) | 4 | 2 | 3 | 3 |
| Downside protection (bear > 0 under joint adverse) | 2 | 4 | 2 | 2 |
| Liquidity (> IDR 20bn/day) | 4 | 3 | 2 | 1 |
| Evidence quality (primary PIT + validated forecasts) | 4 | 3 | 3 | 2 |
| Portfolio suitability (diversifying) | 3 | 3 | 3 | 3 |
| **Total / 50** | **30** | **28** | **24** | **22** |

LSIP's downside-protection score of 4 reflects the isolated bear case (+0%). Under joint adverse scenarios it would be 1–2. We kept the higher score to avoid stacking that penalty on top of the governance score, since both come from the same cash-credit risk.

## Final recommendations

| | **TAPG** | **LSIP** | **DSNG** | **STAA** |
|---|---|---|---|---|
| **Recommendation** | **WATCH** | **WATCH** | **WATCH** | **AVOID** |
| Current price (24 Nov) | 1,710 | 1,570 | 1,275 | 1,015 |
| Fair-value range | 1,525–1,800 (EV 1,803) | 1,480–2,180 market-calibrated (base 1,770); long-run bounds 990 (DDM) to 3,940 (FCFE) | ≈ 1,140–1,770 (bear–bull, uniform rule) | ≈ 830–1,360 (bear–bull, uniform rule) |
| Probability-weighted net 12m return | +4.3% | +17.6% (P > hurdle 54%) | +15.4% (+11–12% using our Q4 estimate) | +7.0% |
| Downside scenario | −16% to −22% | +0% bear; **−18% to −37% joint adverse** | −11% | −18% |
| Entry range | ≤ 1,525 | 1,340–1,460 (max 1,579 after buyback verified) | Only if consensus is cut to our Q4 level while the price holds | n/a |
| Horizon | 12m | 12m (review Jun 2027) | 12m | n/a |
| Indicative size | 0% | 0% (hypothetical 1.5% starter, 4% max) | 0% | 0% |
| Catalysts | FY26 results (~Mar 2027), B50, HRef | C-019 buyback (Jan), C-020 FY26 (Feb), C-021 payout (Jun) | C-011 consensus reset | C-012 refinery data |
| Exit / invalidation | §9 analogue: FY27 consensus −10% | §9 | n/a | n/a |
| Confidence | Medium | Low–medium | Low | Low |

**Why LSIP is not a BUY:**
1. **Hurdle:** it clears only in one valuation frame, by +0.7pp, with a 54% probability. It fails if ke rises by 1pp.
2. **Evidence:** the nowcast is unvalidated (n = 0), and the value driver (cash credit) has no forecastable indicator.
3. **Downside:** joint adverse scenarios give −18% to −37%.
4. **Risk-adjusted excess return:** below an assumed passive IHSG return.
5. **Catalysts:** the dated ones (buyback, results) are small. The large one (payout) is a 15% probability event controlled by the majority shareholder.

> ## **NO TRADE.**
> - Hold cash or money-market instruments (≈ 5.5% net) or short SBN while waiting.
> - Keep TAPG (trigger ≤ IDR 1,525) and LSIP (re-test on C-019, C-020 or C-021; preferred entry 1,340–1,460) under active monitoring.
> - **Confidence in NO TRADE: medium–high.** The main way this could be wrong is LSIP executing the full buyback while the market keeps crediting the cash at 100%. That case is worth about +18% and is covered by the C-019 re-test.

_Sources: S-002, S-003, S-036, S-046–S-051 (LSIP filings), S-052 (ADB AsianBondsOnline SBN yields), S-053 (Bank Indonesia BI-Rate release). Assumptions A-024, A-028, A-029, A-032–A-034._
