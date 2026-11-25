# PT Indo Tambangraya Megah Tbk (ITMG IJ) — Equity Research

**Fairly priced for a mid-cycle coal deck: cash and dividends cushion the downside, but the upside depends on long-run coal prices nobody can validate**

_Date: 25 November 2026. Research only; not investment advice._

> ## Recommendation: **HOLD / WATCH** (not BUY)
>
> | | |
> |---|---|
> | Price (25 Nov 2026) | **IDR 24,650** |
> | Base-case fair value (mine-life DCF) | **IDR 24,700** |
> | Central fair-value range | **IDR 20,300 – 32,000** |
> | Bear (stress) / bull | IDR 14,700 / IDR 67,700 |
> | 12-month target price (base, ex-dividend) | **IDR 25,400** |
> | Expected 12-month total return | **≈ 12%** (≈ 9% dividend yield + ≈ 3% price) |
> | Downside scenario | −41% (bear: permanent shutdown at Newcastle USD 100/t) |
> | Required entry price for BUY | **≤ IDR 19,800** |
> | Investment horizon | 12 months; re-assess at FY2026 results (~early Mar 2027) |
>
> **Market data**
> - Market cap USD 1.41bn; shares ex-treasury 1,048.4m; USD/IDR 18,295.
> - Net cash end-2026E: USD 768m (54% of market cap).
> - Market EV / FY2027E EBITDA: 1.6x. FY2027E P/E: 6.4x. FY2027E dividend yield: 9.3% (base case).

**Workbook:** `outputs/ITMG_model_valuation.xlsx`, 1,717 live formulas. Scenarios are selected on `Inputs!B3`.

**Code:**
- `valuation/itmg_model.py`
- `valuation/itmg_exhibits.py`
- `quant/itmg_financials_extract.py`
- `quant/itmg_market_snapshot.py`

**Exhibits:** `outputs/itmg/`.

**Decision:** D-046.

---

## Key points

1. **The market is pricing our base case almost exactly.**
   - A reverse DCF shows the share price implies a long-run Newcastle price of **USD 104.9/t** from 2029 (nominal, +2% a year). Our base assumption is USD 105/t.
   - With a single flat price from 2027, the implied level is **USD 109/t**, versus USD 152/t spot in October 2026 and USD 134/t averaged over January–October 2026.
   - The base DCF of IDR 24,700 is within 0.2% of the price.
   - At fair value, the expected return equals the cost of equity (≈ 12%), most of it paid as dividends.
2. **Our differentiated evidence is short-horizon only.**
   - The frozen ITMG-C1 model is the programme's only statistically surviving forecasting result (Holm p = 0.013 across 17 tests). It nowcasts next-quarter ASP. A provisional run on data to 25 Nov 2026 gives **USD 102.5/t for 4Q26**, against USD 94.8/t in 3Q26.
   - Combined with benchmark volume and cost, this puts **FY2026E EPS at USD 0.270, in line with consensus (USD 0.271)**. So C1 points to a strong 4Q26 but **no** earnings gap versus consensus.
   - **C1 is forecasting evidence, not trading alpha**, and it says nothing about FY2028+ prices, which drive most of the DCF.
3. **The payoff is asymmetric, but the asymmetry rests on unvalidated assumptions.**
   - **Floor:** net cash (USD 768m ≈ IDR 13,400/share), a shutdown option and a 60% payout.
   - **Upside:** bull case IDR 67,700 needs Newcastle to stay at USD 125–145/t.
   - A 20/60/20 probability weighting gives IDR 31,300. But the weights and the bull price deck are judgement, not evidence, so we do not base a BUY on them.
4. **Reserve life and licences limit long-duration value.**
   - Reserves at end-2025 are about 380 Mt across seven concessions.
   - **Indominco (IMM), about a third of output, has a CCOW contract that expires in March 2028** and only 31 Mt of reserves.
   - In the base case, own production peaks at 24 Mt in 2027–29 and production ends around 2038, when the remaining mines can no longer cover fixed costs. That leaves about 140 Mt unmined.
5. **Capital allocation is shareholder-friendly but cash-heavy.**
   - The payout was 55–60% in 2025, and a 7.2% buyback was completed in November 2026.
   - Still, about USD 0.8–1.2bn of cash is earning ~3–4% against a ~12% cost of equity.
   - A finite DDM at the current 60% payout is worth only **IDR 9,200**. Minority value depends on distributions continuing; the controlling shareholder is Banpu (65%).

---

## 1. Business model and operating assets

ITMG is an Indonesian thermal-coal producer. It also trades third-party coal, provides mining and port services, and is building a small renewables and minerals portfolio. **Banpu (Thailand) owns 65% and the public 35%; the company listed in 2007.** It reports in USD.

**Coal concessions** (3Q26 analyst deck, p24; JORC reserves at 31 Dec 2025):

| Mine | Licence (expiry) | Reserves (Mt) | Resources (Mt) | CV (kcal/kg GAR) | FY2026e production (Mt) | Base-case role |
|---|---|---|---|---|---|---|
| Indominco Mandiri (IMM) | CCOW Gen I (**Mar 2028**) | 31 | 683 | 5,600–6,200 | 7.1 | Extended as IUPK in base; depleted ~2030 |
| Trubaindo (TCM) | CCOW Gen II (Feb 2035) | 71 | 596 | 6,100–6,500 | 3.4 | Steady 3.4 Mt |
| Bharinto Ekatama (BEK) | CCOW Gen III (Jun 2041) | 95 | 485 | 6,100–6,500 | 8.0 | Largest mine; depleted ~2037 |
| Nusa Persada Resources (NPR) | IUP (May 2033) | 77 | 143 | 5,500–6,100 | 0.4 | First coal 2026; ramp to 2.5 Mt (base) |
| Graha Panca Karsa (GPK, 70%) | IUP (Sep 2029) | 99 | 121 | 3,900 | 2.0 | Low-CV; 2.5 Mt (base) |
| Tepian Indah Sukses (TIS) | IUP (Apr 2029) | 7 | 17 | 6,400 | 0.6 | Small |
| Jorong (JBG) | CCOW Gen II (May 2035) | 2 | 67 | 4,300–4,400 | – | Inactive / post-mining |

**Other businesses:**
- **Integrated support:** coal trading (EBBP), mining contracting (TRUST), coal transport (IBU), post-mining (Kitadin), Bontang and Bunyut ports, and the shared "Melak cluster" infrastructure (crushing plant, hauling road, Bunyut port) serving TCM, BEK, NPR, GPK and TIS.
- **Diversification:**
  - solar PV, with 144 MWp contracted at 1Q26;
  - a 9.62% stake in nickel company PT Adhi Kartiko Pratama (NICE), bought for USD 15.8m in July 2025.
- **Not modelled:** these are small relative to coal and excluded from the DCF (conservative).

## 2. Mine economics and reserve life

- **Unit economics (9M26, FS-derived, USD/t sold):**
  - ASP 85.7 (first-reported, decks)
  - royalty ≈ 9.5 (11.1% of revenue)
  - cost of revenue ex-royalty ≈ 53.4 (3Q26: 57.7)
  - selling ≈ 7.2
  - G&A ≈ 2.3
  - **operating margin ≈ 13 USD/t**
- Strip ratio rose to 10.8x in 9M26 (9.3x in 9M25), with fuel at USD 1.00/litre (9M25: 0.78).
- **Cost moves with price:** across 2019Q1–2026Q3, unit cost ex-royalty ≈ 35.4 + 0.17 × ASP (R² 0.61, n = 31). Fuel, strip-ratio choices and contractor rates are pro-cyclical. This partial hedge is why margins compress less than prices in downturns (FY2020: ASP USD 53/t, unit cost USD 40/t, still profitable).
- **Reserve life:** ≈ 380 Mt of reserves against ≈ 21.5 Mt/yr of own production is roughly 18 years on paper. But IMM (31 Mt, licence 2028) and BEK (95 Mt at 8 Mt/yr) deplete first.
  - **Base case:** own production of 24 Mt (2027–29) falls to 17 Mt (2031–36) and 8 Mt after 2037. Production stops in 2038, once the remaining TCM/NPR/GPK volumes can no longer cover fixed costs.
  - **The assets have no perpetuity:** the DCF ends at the last production year (horizon capped at 2050, no terminal value).

## 3. Production, sales, quality and markets

| | FY2024 | FY2025 | 9M26 | FY2026 guidance / basis |
|---|---|---|---|---|
| Production (Mt) | 20.2 | 21.2 | 15.9 | 21.5 target (4Q26 5.6) |
| Sales (Mt) | 24.1 | 24.6 | 18.7 | Guidance 27.2–27.6; **model 25.5** (seasonal benchmark for 4Q) |
| ASP (USD/t) | 95.7 | 76.0 | 85.7 | 4Q26 C1 nowcast 102.5 |

**Quality and mix:**
- Mostly mid- to high-CV coal: 5,600–6,500 kcal/kg from IMM, TCM, BEK and NPR; plus low-CV GPK at 3,900.
- **NPR coal is marketed to premium buyers** in Japan, Korea and Hong Kong (3Q26 deck).

**Markets:**

| Destination | FY2025 sales (Mt) | 3Q26 share |
|---|---|---|
| China | 8.4 | 27% |
| Indonesia (domestic market obligation, DMO) | 5.5 | 29% |
| Japan | 4.4 | 21% |
| India | 2.3 | — |
| Philippines | — | 7% |
| Others | 4.1 | rest |

**Contract pricing:**
- Sales are a mix of index-linked and fixed-price contracts:
  - 4Q25: indexed 54% / fixed 45%;
  - FY2026 indicative book (3Q26 deck): indexed 14% / fixed 83% / unsold 3%.
- ITMG realises a discount to Newcastle (6,000 kcal), because of lower CV and the domestic price cap:
  - ASP/Newcastle averaged **0.69 since 2023** (0.72 over 2018–2026);
  - the ratio fell to 0.56 in the 2022 spike. That is why ITMG under-earns in price spikes and why C1 models partial pass-through (≈ 0.74 with a lag).

## 4. Competitive positioning

**Peer multiples** (Yahoo snapshot, 25 Nov 2026):

| Ticker | Trailing P/E | EV/EBITDA (corrected) | Dividend yield |
|---|---|---|---|
| ITMG | 7.1x | 4.2x (trailing) | 7.1% |
| PTBA | 5.7x | 5.1x | 3.9% |
| AADI | 5.3x | 3.0x | 10.1% |
| ADRO | 5.9x | 3.4x | 10.1% |
| BSSR | 5.7x | 3.9x | 20.2% |
| HRUM | 7.1x | 1.1x | 0% |
| INDY | 17.1x | 2.1x | 0.7% |
| GEMS | 7.4x | 4.4x | 12.3% |
| **Peer median (ex-ITMG)** | **5.9x** | **3.4x** | **3.9%** |

- **Multiples:** Yahoo's EV/EBITDA and P/B for USD reporters divide IDR values by USD fundamentals. They are corrected by USD/IDR in the workbook.
- **Strengths:**
  - mid- to high-CV coal;
  - shared infrastructure in the Melak cluster;
  - net cash and no leverage (debt/equity 0.03x);
  - an integrated trading and logistics platform;
  - ESG ratings at the top of the coal sub-industry (Sustainalytics 2025, per company). This may matter for buyer and lender access but is not modelled.
- **Weaknesses:**
  - smaller scale than AADI/ADRO and BUMI;
  - concentration in East Kalimantan;
  - **shorter licence and reserve tail** than peers with large IUPK reserves.

## 5. Regulatory exposure

Primary-source verification levels are in `coal_regulatory_regimes.csv`.

| Item | Exposure | Model treatment |
|---|---|---|
| **IMM CCOW expiry (Mar 2028)** | Continuation as an IUPK requires government approval. Converted IUPKs pay progressive, HBA-linked royalties (PP 15/2022; knowledge-only, not verified here). | Base/bull: extended, with +3pp/+2pp royalty on IMM revenue. **Bear: production stops.** Value at stake: ≈ IDR 1,500/share (base, extension vs not). |
| Royalty | CCOW share 13.5% of revenue; IUP tiered by CV. Effective rate 10.5–12.7% (2024–26). | 11.5% base (11–12% across scenarios) |
| DMO and power price cap | 25% DMO; USD 70/t cap for power-plant sales (Kepmen 2018–2021 series) | Embedded in the realised ASP/Newcastle ratio |
| RKAB production quotas | Annual approvals; 2026 revisions delayed (company decks 1Q–3Q26) | Volume benchmark; quota risk in bear |
| Export levy and export centralisation | Coal export tax "implementation remains delayed" (1Q26 deck); centralised export oversight (3Q26 deck) | Not modelled; downside risk |
| Energy transition | Seaborne thermal demand risk in Japan, Korea and China | Cost escalation of 2.5% vs flat nominal price in bear |

## 6. Capital allocation, dividend sustainability and governance

**Dividends paid** (USD m, cash flow statement):

| 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 9M26 |
|---|---|---|---|---|---|---|---|---|
| 249 | 214 | 65 | 107 | 538 | 674 | 216 | 203 | 65 |

- **Payout:** declared payout was 55% for the 2025 interim and 60% for the 2025 final (USD 115m).
- **Buyback:** 81.5m shares (7.2%) repurchased between November 2025 and 4 November 2026, out of an approved maximum of IDR 2.49tn.

**Dividend sustainability (base case):**
- FY2027E FCFE is USD 235m against USD 132m of dividends at 60% payout. FY2028–30 FCFE (USD 100–185m) still covers dividends.
- Net cash grows from USD 768m to USD 1.08bn by 2030 under a 60% payout. **Dividends are sustainable; the issue is under-distribution, not over-distribution.**
- **Watch item:** 9M26 operating cash flow fell to USD 107m from USD 269m, because inventory (+USD 39m), receivables and tax payments rose. That is temporary if it reverses in 4Q26.

**Capex:**
- Low intensity: USD 76m (FY2025); USD 37m (9M26).
- Model: USD 85m a year in 2027–30 for NPR/GPK development, then maintenance at USD 3.5 per own tonne.

**Governance:**
- Banpu controls the board and capital allocation.
- **Positives:**
  - a Sustainability Development and GCG committee was separated from Nomination and Compensation in 2025;
  - PROPER Green ratings for IMM and JBG;
  - consistent IR disclosure. We used 69 IR documents, all hashed.
- **Minority risks:**
  - related-party trading and services with Banpu;
  - the retention policy;
  - diversification capex (renewables, nickel) with unproven returns.

## 7. Financial history

USD m, audited FS. Parsed statements pass every identity: assets = liabilities + equity, the gross-profit identity, the profit identity, and no restatement in the next year's comparatives.

| | FY18 | FY19 | FY20 | FY21 | FY22 | FY23 | FY24 | FY25 | 9M26 |
|---|---|---|---|---|---|---|---|---|---|
| Revenue | 2,008 | 1,716 | 1,185 | 2,077 | 3,636 | 2,374 | 2,304 | 1,881 | 1,601 |
| Gross margin | 29% | 19% | 17% | 44% | 52% | 31% | 30% | 26% | 26% |
| Profit to owners | 262 | 129 | 39 | 476 | 1,200 | 500 | 374 | 191 | 163 |
| Operating cash flow | 355 | 89 | 173 | 618 | 1,325 | 221 | 452 | 285 | 107 |
| Capex (PPE + exploration) | 98 | 77 | 27 | 22 | 44 | 81 | 90 | 120 | 48 |
| Dividends paid | 249 | 214 | 65 | 107 | 538 | 674 | 216 | 203 | 65 |
| Net cash | 368 | 159 | 167 | 639 | 1,380 | 797 | 918 | 719 | 674 |
| ROE | 27% | 15% | 5% | 40% | 62% | 28% | 19% | 10% | 9% (9M) |

See Exhibits 1 and 2: `outputs/itmg/ex1_history.png`, `ex2_asp_cost.png`.

## 8. Integrated forecasts, FY2026E–FY2030E (base case)

**Evidence classes:**

| Component | Class | Basis |
|---|---|---|
| 4Q26 ASP | **VALIDATED** (frozen C1-M2) | Provisional run 25 Nov 2026 (fallback mode, October data only). The official frozen run is on 10 Jan 2027. |
| 4Q26 volume, unit cost, royalty | **BENCHMARK** | C2 and C3 failed validation, so their strongest benchmarks are used: seasonal 4Q25 volume of 6.8 Mt; last-quarter cost of USD 57.7/t; 3Q26 royalty rate of 11.1%. |
| 4Q26 gross-profit structure | I1 (**CONDITIONAL GO**) | Same structure. Not treated as validated. |
| FY2027 unit cost | BENCHMARK | 57.7 adjusted by 0.17 × (ASP − 94.8) |
| FY2027+ Newcastle path, ASP ratio, cost-price fit, mine rates, licence extensions, capex, payout, discount rate | **ANALYST** | **Not validated.** C1's short-horizon skill is **not** extrapolated. |

**Base-case forecasts:**

| USD m | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---|---|---|---|---|
| Newcastle (USD/t) | 134 (actual year to date) | 125 | 110 | 107 | 109 |
| ASP (USD/t) | 90.0 | 86.2 | 75.9 | 73.9 | 75.4 |
| Sales volume (Mt) | 25.5 | 27.5 | 27.5 | 27.5 | 23.4 |
| Unit cost ex-royalty (USD/t) | 54.6 | 56.2 | 50.3 | 50.9 | 52.2 |
| Revenue | 2,298 | 2,372 | 2,087 | 2,032 | 1,764 |
| Gross profit | 650 | 552 | 448 | 382 | 333 |
| EBITDA (company definition) | 498 | 392 | 283 | 212 | 171 |
| Profit to owners | 283 | 220 | 146 | 98 | 83 |
| EPS (USD) | 0.270 | 0.210 | 0.139 | 0.093 | 0.079 |
| DPS declared at 60% (IDR) | 2,958 | 2,304 | 1,525 | 1,022 | 863 |
| Operating cash flow ¹ | 134 (4Q) | 320 | 268 | 203 | 186 |
| Capex ¹ | 12 (4Q) | 85 | 85 | 85 | 85 |
| FCFE ¹ | 122 (4Q) | 235 | 183 | 118 | 101 |
| Dividends paid ¹ | 0 (4Q) | 132 | 87 | 59 | 50 |
| Net cash (year end) | 768 | 871 | 967 | 1,027 | 1,078 |
| Total equity | 2,004 | 2,097 | 2,159 | 2,201 | 2,236 |

¹ The FY2026E cash-flow column covers 4Q26 only, because the opening balance sheet is 30 September 2026.

**Model mechanics:**
- **Balance sheet:**
  - net of trade payables;
  - debt and leases held flat;
  - other assets and liabilities held constant;
  - the balance check is ≤ 10⁻¹¹ in every year and scenario.
- **Working capital:** 7% of revenue.
- **Tax rate:** 28%.
- **Interest income:** 3% on opening cash.

See Exhibit 7 (`ex7_forecast.png`) and Exhibit 4 (`ex4_production.png`).

## 9. Valuation

**Methods:**

| Method | Bear | **Base** | Bull | Notes |
|---|---|---|---|---|
| Mine-life DCF (FCFF 2027–2050 at 12.1% + net cash) | 14,658 | **24,710** | 67,707 | No terminal value; production stops when cash margin × volume no longer covers G&A + capex |
| Finite DDM (60% payout; residual cash returned 2050) | 3,049 | 9,235 | 39,244 | Lower bound for minorities if cash is retained |
| Peer P/E 5.9x × FY2027E EPS | n.m. | 22,770 | 60,378 | Peer medians are trailing; mixed fiscal periods |
| Peer EV/EBITDA 3.4x × FY2027E EBITDA + net cash | 13,407 | 36,482 | 67,339 | ITMG trades at 1.6x |
| Analyst price targets (n = 17) | low 19,118 | mean 28,640 | high 36,480 | 9 buy / 7 hold / 1 strong sell |

**Discount rate:** cost of equity 12.1% (= WACC, since the company is net cash), built as:
- risk-free rate 4.92% (US 10-year, FRED, 23 Nov 2026);
- plus Indonesia country risk premium 2.2%;
- plus 1.0 × equity risk premium 5.0%.

**Base-case EV is small:** PV of FCFF is USD 648m, against USD 768m of net cash, so cash is more than half of equity value. Valuation is therefore insensitive to the discount rate (IDR 24.2k–25.4k for 10–14%) and very sensitive to coal price and cost assumptions.

**Scenario levers** (bear / base / bull):

| Lever | Bear | Base | Bull |
|---|---|---|---|
| Newcastle 2027 (USD/t) | 100 | 125 | 145 |
| Newcastle 2028 (USD/t) | 90 | 110 | 130 |
| Newcastle 2029+ (USD/t) | 85 | 105 | 125 |
| Price escalation per year | 0% | 2% | 2.5% |
| Cost escalation per year | 2.5% | 2.0% | 2.0% |
| ASP/Newcastle | 0.66 | 0.69 | 0.72 |
| Royalty | 12% | 11.5% | 11% |
| IMM extended | no | yes | yes |
| NPR / GPK rates (Mt) | 1.5 / 2.0 | 2.5 / 2.5 | 3.5 / 3.0 |
| Traded coal (Mt) | 2.5 | 3.5 | 4.5 |

- **The bear case is a stress test:** at USD 100/t, cash margins do not cover fixed costs. The model closes operations permanently in 2027, leaving mainly net cash.
- **The real-world bear case would be a partial curtailment** with cost deflation, worth somewhere between the bear and base values.

**Reverse DCF:**
- **The price implies a long-run Newcastle of USD 104.9/t** from 2029 (+2% a year, with the base path for 2027–28), or a **flat USD 109/t from 2027**.
- Equivalent historical reference: the median 2016–2025 annual average is USD 108/t (World Bank CMO).

**Sensitivity:**
- **DCF (IDR/share) by long-run Newcastle and cost of equity** (Exhibit 6):

  | Long-run Newcastle | 10% | 12% | 14% |
  |---|---|---|---|
  | USD 85–95 (closure ~2029) | 20,400 | 20,300 | 20,200 |
  | USD 105 | 25,400 | 24,700 | 24,200 |
  | USD 115 | 33,600 | 32,000 | 30,600 |
  | USD 125 | 42,600 | 39,800 | 37,500 |

- **ASP/Newcastle ratio from 0.66 to 0.72:** IDR 20,300 – 29,200 (IMM extended); IDR 18,300 – 27,400 (not extended).
- **Largest one-at-a-time ranges:**
  - long-run price USD 95–115: IDR 20.3k – 31.9k;
  - cost intercept ±3 USD/t: IDR 19.8k – 30.2k;
  - ASP ratio: IDR 20.3k – 29.2k;
  - royalty 10.5–12.5%: IDR 23.2k – 26.2k;
  - IMM extension: IDR 23.2k – 24.7k.
- **The floor near IDR 20,300 for long-run prices below about USD 100** reflects net cash plus 2027–28 cash flows followed by closure.

**Exhibit 5** (`ex5_football.png`) summarises the valuation ranges.

## 10. Market expectations

**Consensus** (S&P via Yahoo; forward snapshot retrieved 25 Nov 2026; no historical consensus exists in this project, and none was reconstructed):

| | FY2026 | FY2027 |
|---|---|---|
| Consensus EPS (USD), n | 0.271 (6) | 0.228 (14) |
| Consensus EPS range | 0.222–0.332 | 0.118–0.319 |
| Model EPS (base) | 0.270 | 0.210 |
| **EPS gap** | **−0.4% (in line)** | **−8%** |
| Consensus revenue (USD m) | 2,240 | 2,099 |
| Model revenue | 2,298 | 2,372 |

- **Embedded commodity price:**
  - With our cost structure, consensus FY2027 EPS implies a **Newcastle of USD 127/t in 2027**, versus USD 125/t in our base case.
  - Consensus revenue is lower but its margins are higher than ours. That suggests consensus assumes lower volumes and lower unit costs than our benchmark-based costs.
  - The share price itself implies a long-run price near USD 105–109/t.
- **What appears to be priced in:**
  - a normalisation from USD 150/t spot towards USD 105–110/t over 2–3 years;
  - IMM continuing;
  - continued 55–60% payouts.
- **What is not priced in:** neither a sustained high-price regime (bull) nor a structural collapse (bear).

## 11. Catalysts and risks

**Catalysts:**

| When | Event |
|---|---|
| **10 Jan 2027** | Frozen C1/I1 prospective forecast for 4Q26 (scheduled; recorded before results) |
| ~early Mar 2027 | 4Q26/FY2026 results and FY2027 guidance; C1/I1 resolution (scheduled evaluation 8 Mar 2027) |
| Apr 2027 | FY2026 final dividend at the AGM. At 60% payout, total FY2026 DPS ≈ IDR 2,960 (≈ 12% yield) less any interim already paid. |
| 2027 | RKAB 2027 quota approvals; **IMM IUPK decision ahead of Mar 2028**; export-levy implementation; winter 2026/27 demand |

**Downside risks:**
1. Newcastle falls back to below USD 100/t (Chinese domestic supply, Indian imports, LNG prices).
2. Rising strip ratios and fuel costs: 3Q26 unit cost was USD 57.7/t.
3. IMM non-extension or heavier IUPK royalties.
4. RKAB cuts, DMO and price-cap changes, export tax.
5. Lower payouts or value-destructive diversification.
6. The working-capital build in 9M26 persists.

**Upside risks:**
1. Prices stay above USD 125/t.
2. NPR premium-coal ramp-up.
3. Special dividends or further buybacks from a USD 0.9–1.2bn cash pile.
4. A lower royalty or a favourable IUPK outcome.

## 12. Investment decision

**HOLD / WATCH.**
- The price (IDR 24,650) sits on our base-case fair value (IDR 24,700). The expected 12-month total return (≈ 12%, mostly dividends) only matches the cost of equity.
- Our one validated edge (C1) confirms near-term earnings that consensus already expects. **We see no evidence-based mispricing**, so we do not recommend BUY.
- We also do not recommend SELL. Net cash and the payout give a value floor near IDR 20,000 in all but the stress scenario, and the high dividend yield makes waiting inexpensive.

| | |
|---|---|
| Fair-value range | IDR 20,300 – 32,000 (central); IDR 14,700 – 67,700 (bear to bull) |
| 12-month target price | IDR 25,400 (base fair value rolled forward at the cost of equity, less FY2027 dividends) |
| Required entry price for BUY | **≤ IDR 19,800**: a 20% discount to base value, close to the value floor at long-run prices of USD 85–95; ≈ 40% expected 12-month total return in the base case |
| Horizon | 12 months, with formal reviews at the C1/I1 resolution (Mar 2027) and the IMM licence decision |

**Thesis invalidation (re-rate to SELL/AVOID if any occur):**
- IMM extension refused, or an IUPK royalty above 18% of IMM revenue;
- Newcastle below USD 100/t for two consecutive quarters with no cost relief (unit cost ex-royalty above USD 58/t);
- payout cut below 50% without a value-accretive use of cash;
- operating cash flow below 60% of EBITDA for a second consecutive quarter.

**Upgrade triggers (re-assess for BUY):**
- price ≤ IDR 19,800 without deterioration in the above;
- an IMM IUPK approved at or below our base royalty, together with Newcastle forwards above USD 115/t for 2028;
- a special distribution or buyback above USD 200m.

**Monitoring indicators:**

| Area | Indicator |
|---|---|
| Prices | Monthly World Bank Newcastle and ICI prices; ITMG ASP/Newcastle ratio (base 0.69) |
| Costs | Quarterly strip ratio and fuel price (deck) |
| Volumes | RKAB approvals; quarterly sales versus guidance (27.2–27.6 Mt FY2026) |
| Expectations | Consensus EPS revisions (logged monthly in `consensus_history.csv`) |
| Regulation | IMM licence news; export-levy regulation |
| Cash | Dividend declarations and buybacks; the working-capital trend |

---

## Appendix A — How the quantitative evidence is used

- **ITMG-C1** (frozen M2 distributed lag on World Bank Newcastle) passed its pre-registered historical test: **−40% MAE vs the strongest benchmark**, robust to delayed data (−39%). It is the only test of 17 that survives programme-wide Holm (p = 0.013). It is used **only** for the next-quarter ASP. Its historical record is in Exhibit 3 (`ex3_c1_record.png`).
- **Prospective confirmation is pending** (scheduled for 10 Jan / 8 Mar 2027). One resolved quarter will not be evidence of skill; the pre-registered tests need 8 (interim) and 12 (final) quarters.
- **ITMG-I1** (integrated gross profit) remains **CONDITIONAL GO** (Holm p 0.55). Its structure is used for the 4Q26 bridge only.
- **C2** (volume) and **C3** (unit cost) are **NO-GO**. Their strongest benchmarks are used, as instructed.
- **No alpha claim:** forecasting accuracy is not trading alpha, and the programme's only direct-return test (DR-R1, palm) failed.

## Appendix B — Data, methods and limitations

**Financial statements:**
- `quant/itmg_financials_extract.py` parses the consolidated statements of FY2018–FY2025 (audited) plus 9M25 and 9M26 from 70 hashed ITMG PDFs (`ITMG_financials_annual.csv`, `ITMG_financials_checks.csv`).
- Missing lines are genuine absences (no bank loans or leases before 2020).

**Sales volumes:** FS coal revenue ÷ first-reported ASP (reconciled within ≤ 1.1% to deck volumes). FY2018 is incomplete.

**Model verification:** LibreOffice/Excel are not available in this environment. Every one of the 1,717 formulas was evaluated by an independent Python evaluator (`valuation/xlsx_eval.py`): no errors, and the balance sheet balances. Excel recalculates on open. The scenario, sensitivity and reverse-DCF tables are static outputs of the script.

**Limitations:**
1. **Share count:** 1,048.4m assumes the 81.5m bought-back shares are held in treasury.
2. **Licence assumptions:**
   - extensions for TCM, BEK, NPR, GPK and TIS are assumed in all scenarios;
   - royalty regimes for IUPK are knowledge-only.
3. **Single blended cost curve:** per-mine costs are not disclosed in machine-readable form, so mix effects (high-strip IMM vs low-strip BEK) are not modelled.
4. **Non-coal assets** (renewables, NICE stake, other financial investments in other current assets) are excluded.
5. **Peer multiples** are vendor (Yahoo) data with mixed fiscal periods.
6. **Consensus** is a single forward snapshot; the EPS share basis is not disclosed.
7. **IHSG/dividend tax:** valuation is pre-dividend-tax (10% withholding for residents is not deducted).
8. **The 4Q26 C1 nowcast is provisional:** it uses October data only. The official frozen forecast will be made on 10 Jan 2027 and may differ.

**Sources:**
- S-066 ITMG FS and analyst presentations (itmg.co.id; SHA-256 manifest)
- S-003 World Bank CMO
- S-002 Yahoo Finance
- S-036 S&P consensus via Yahoo
- S-074 FRED DGS10
- S-071 regulation table

The source register is `data/SOURCE_REGISTER.csv`; the workbook also has a `Sources` sheet.
