# LSIP (PP London Sumatra) — Phase VI Stage 1 Findings and Research Gate

_Date: 2026-11-25 · Code: `quant/lsip_stage1.py` (tests `tests/test_lsip.py`) · Outputs: `data/reference/research/LSIP_*.csv` · Tags: OBS = filing, DER = derived, EST = assumption · No rating_

## 0. Document inventory (all supplied locally; copied to `data/raw/company/LSIP/`, git-ignored; manifest updated)

| Document | Period | IDX timestamp (S-051 mirror) | Usable from |
|---|---|---|---|
| Interim FS 30 Sep 2026 (111 p) | 9M26 | 2026-10-30 19:45 | 2026-11-02 |
| Highlights 9M26 | 9M26 | 2026-10-30 20:01 | 2026-11-02 |
| Buyback disclosure | Oct–Dec 2026 | 2026-10-23 18:51 | 2026-10-26 |
| Interim FS 30 Jun 2026 (111 p) | H1 26 | 2026-07-31 16:22 | 2026-08-03 |
| Highlights 1Q26 | Q1 26 | 2026-04-30 20:00 | 2026-05-04 |
| Audited FS FY2025 (122 p), Highlights FY25 | FY25 | 2026-02-27 | 2026-03-02 |
| Audited FS FY2024 (119 p), Highlights FY24 | FY24 | 2025-02-28 | 2025-03-03 |
| Sustainability Report 2025 (142 p) | FY25 | filed with AR, 2026-04-30 19:50 | 2026-05-04 |

- **Gaps:** there is no Q1 2026 FS (only highlights), so Q2 is derived as H1 − highlights Q1 for revenue, gross profit and profit only.
- The user's scraper (`download_lsip.py`) and `data/raw/LSIP/failed_downloads.csv` are left untouched and uncommitted.

## 1–2. Standalone quarters (IDR bn; Q2 = H1 − Q1; Q3 = 9M − H1; Q4'25 = FY25 − 9M25)

| | Q4 2025 | Q1 2026 | Q2 2026 | **Q3 2026** |
|---|---|---|---|---|
| Revenue | 1,555 | 1,327 | 1,363 | **1,637** |
| Gross profit (margin) | 788 (51%) | 425 (32%) | 438 (32%) | **924 (56%)** |
| Profit to owners | 641 | 394 | 497 | **854** |
| CPO production (kt) | 90 | 65 | 71 | **91** |
| Nucleus FFB (kt) | 341 | 243 | 262 | **345** |

9M26 core profit, per the company (excluding FX, biological-asset FV, plasma amortisation, one-offs): **1,628bn vs 1,745bn reported**.

## 3. Why Q3 gross profit doubled on revenue +22% (DER, from FS note 22)

| Component (vs H1 average quarter) | IDR bn |
|---|---|
| Revenue increase | +292 |
| Total production cost: unchanged (−5) despite ≈ 37% more nucleus FFB | −5 |
| — purchased FFB higher | −31 |
| — upkeep & fertiliser lower (deferral) | +29 |
| Finished-goods inventory build: cost of unsold Q3 output capitalised (FG 373 → 593bn) | +245 |
| Other (WIP, purchases of finished goods, own use) | −40 |
| **Gross profit change** | **+492** |

- **Reading:** the seasonal production peak (nucleus FFB +37% vs the H1 average) was produced at a flat total cost. Unit cost fell about 25%, so sold units carried low cost.
- The rest of the cheap output sits in inventory (+221bn), to be sold at Q3-level margins.
- Fertiliser and upkeep ran 29bn below the H1 run-rate, the same dry-weather deferral as TAPG.
- **Not one-off accounting:** biological-asset FV was only +34.5bn in Q3 and sits below gross profit. The company's core profit confirms the result is largely operational.
- **Sustainability:** the margin is partly seasonal (Q3/Q4 peak) and partly timing (deferred fertiliser, inventory). An El Niño lag on 2027 volumes is a risk.

## 4. Preliminary Q4 2026 nowcast (EST scenarios relative to Q3)

| | Bear | Base | Bull | Consensus-implied (S&P, 5 analysts) |
|---|---|---|---|---|
| Volume vs Q3 / price vs Q3 | 0.85 / −10% | 0.95 / −5% | 1.00 / −2% | |
| Q3 inventory build released | 0% | 50% | 100% | |
| Fertiliser catch-up (IDR bn) | 120 | 60 | 20 | |
| **Q4 profit to owners** | **238** | **468** | **654** | **≈ 360** |
| FY26 profit to owners | 1,983 | 2,213 | 2,399 | 2,105 |

- Base Q4 is about **+30% above** the consensus-implied figure (FY26 +5%).
- For comparison, Q4 2025 was 641bn.
- FY27 consensus is ≈ 2,210bn, vs our 1.8 / 2.2 / 2.4tn (bear / base / bull), so **no FY27 gap** in the base case.

## 5. Net cash and genuinely excess cash (OBS, 9M FS p4–5, p52)

- **Cash & equivalents: IDR 8,516bn (VERIFIED). Zero borrowings.** Total liabilities are 1,596bn, including 552bn of long-term employee-benefit obligations.
- **Where the cash sits:**
  - Third-party banks: OCBC NISP (1.5tn deposits), Bank Mega (2.4tn), CIMB Niaga, SMBC, BCA and others.
  - **Related party PT Bank Ina Perdana (Salim group): 665bn (7.8%)**, down from 1,640bn at Dec-25.
- **Excess cash (EST):** 8,516 − one quarter's cash costs (≈ 890) − long-term employee benefits (552) − buyback (750) ≈ **IDR 6.3tn ≈ IDR 927/share** (59% of the share price).
- **Cash yield:** ≈ 4.0% pre-tax (finance income 239bn over 9M).

## 6. IDR 750bn share buyback (OBS: disclosure, 23 Oct 2026)

- **Terms:** up to IDR 750bn from internal cash, on-exchange from 26 Oct to 31 Dec 2026. It uses the OJK market-volatility rule (POJK 13/2023; OJK letter S-112/D.04/2026), so no shareholder vote is needed. The cap is 20% of paid-up capital, subject to free-float rules.
- **Company pro-forma (H1 basis):** EPS 131 → 141.
- **At IDR 1,570:** up to about 478mn shares (7.0%). Lost after-tax interest is about 24bn/yr, so **EPS accretion ≈ +6.4%** (DER).
- **Execution status: UNVERIFIED.** There is no execution report in the IDX listing to 20 Nov. Traded value since 28 Oct is 0.78× the Jul–Sep level, which shows no visible buying footprint.
- **Precedent:** LSIP cancelled treasury shares in Sep 2024 (IDX 2024-09-05).
- **Value implication:** buying back below the cash-plus-operations value is accretive to remaining holders. At 750bn it is still only about 9% of cash: it signals intent but does not resolve the cash overhang.

## 7. Independent vs consensus

| | Ours (base) | Consensus | Gap |
|---|---|---|---|
| Q4 2026 | 468 | ≈ 360 | +30% |
| FY2026 | 2,213 | 2,105 | +5% |
| FY2027 | 2,200 | ≈ 2,210 | ≈ 0 |

Consensus: 5 analysts, low dispersion (12%), up 10% in 30 days. **The edge is a Q4 timing item, not a structural earnings gap.**

## 8. Research gate (17.5% expected 12-month return)

- **Valuation frame (OBS calibration):**
  - Year-end FY2025 price (1,195) = cash + 0.3× profit.
  - Today (1,570) = cash + ≈ 1.0× FY26 consensus profit.
  - So the market credits cash at about 100% and values the operations at 0.3–1.0× profit (historical EV/NP: 3.0× in FY22, 2.0× in FY23, 0.8× in FY24, 0.3× in FY25).
- **Scenarios** (EST probabilities 30/50/20; cash in 12m ≈ 8.9tn after FY26 dividend and buyback; dividend ≈ IDR 97):

| Scenario | EV/profit multiple | Profit (IDR bn) | 12-month return |
|---|---|---|---|
| Bear | 0.3× | 1,800 | +1% |
| Base | 1.0× | 2,200 | +18% |
| Bull | 2.0× | 2,400 | +44% |

- **Expected return 17.9%.** Weight uncertainty (Dirichlet) gives a 5–95% range of 11–26%, and **P(> 17.5%) = 51%**.
- **Fragility:**
  - Without the buyback: 17.1%.
  - If the market credits cash at 80% instead of 100%: **≈ 0%**.
  - The base case needs the 2026 re-rating (0.3× → 1.0×) to hold; the bull case needs a payout or governance catalyst that is not in evidence (payout has been about 30% for years, and 76% of sales go to the parent SIMP).

**GATE DECISION: NOT PASSED (borderline).** The point estimate (17.9%) only marginally exceeds the hurdle, with a 51% probability, and it depends on unverified buyback execution and full credit for cash. **Do not proceed to Stage 2.**

**Re-test when either:**
1. An IDX buyback execution report shows material purchases.
2. Payout or capital-return policy changes (AGM ~Jun 2027).
3. FY2026 results confirm a Q4 above about 450bn, with consensus FY27 not cut.

LSIP has strong **downside protection** (bear ≈ +1%) because cash backs about 59% of the price. It goes on WATCH as a low-risk, low-catalyst name.
