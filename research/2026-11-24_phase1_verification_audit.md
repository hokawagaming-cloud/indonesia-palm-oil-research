# Phase 0–1: Reconciliation, verification and data availability audit

_Research date: 24 November 2026. Uses only information published on or before this date. Research only — not investment advice._

**Governing brief:** "Master Research Mandate — Indonesian Palm Oil Quantamental Equity Research" (user-supplied, 24 Nov 2026), §19–20: Phase 0 (consolidate) and Phase 1 (verify). This document does **not** rank stocks or assign ratings (mandate §19, Phase 1).

**Tags** follow `context/RESEARCH_CONTEXT.md`: [V-P] primary document read · [V-S] reputable press or broker summary of a primary release · [MKT] quote page · [EST] my calculation (method shown) · [HYP] hypothesis · [UNV] claimed in the mandate but not verified this session · [CONFLICT] sources disagree.

---

## 1. Summary

1. **Most of the mandate's TAPG figures check out.** 9M26 revenue Rp9.45tn and net profit Rp3.51tn (+30.8%) match the interim statements [V-P]. The "ROE ≈39%" is 9M profit annualised on period-end equity. That overstates the sustainable level: FY2025 ROE was 33.6%.
2. **The LSIP Rp750bn buyback is real but has not been executed yet.** It was disclosed on 23 Oct 2026. The window runs 26 Oct–31 Dec 2026, funded from internal cash [V-S, several outlets quoting the disclosure]. No execution report was found. Phase II treated a buyback as speculative with a 5% weight. That needs revisiting, but only after we see shares actually bought.
3. **Three DSNG figures in the mandate fail basic checks:**
   - **Profit lines:** attributable profit (Rp1.465tn) is shown as larger than consolidated profit (Rp1.44tn). That implies negative NCI, but FY2025 NCI was positive.
   - **Inventory:** the Q3 inventory build doesn't add up. 23 + 151.9 − 127.1 = 47.8kt, not 52kt.
   - **Nowcast and consensus:** the Q4 nowcast (Rp1.81/2.07/2.31tn) and the "consensus Rp2.26tn" have no recorded source or date.

   Until the DSNG 9M26 statements are read, none of these may be used.
4. **The 2027 biodiesel blend was set, and is now being reconsidered.** A ministerial phasing decree (Kepmen ESDM 113.K/EK.05/MEM.E/2026, Apr 2026) set B50 from 2027 [V-S]. On 13 Nov 2026 ESDM said 2027 is under review, with a decision "within a month" [V-S]. No 2027 volume allocation has been issued. B60 is still only a target.
5. **PP 24/2026 is confirmed in force.** It was set and promulgated on 20 May 2026 (LN 2026 No. 58) and took effect on 1 Jun 2026; the BPK legal database lists its status as in force [V-P metadata]. The DSI fee is still unannounced, due in December.
6. **El Niño is confirmed at a historic scale but is expected to start weakening in early 2027** (NOAA CPC, 12 Nov 2026 [V-P]):
   - Niño-3.4 is +2.5 °C.
   - A strong-to-very-strong event is more than 79% likely through Jan–Mar 2027.
   - There is about a 60% chance of the strongest event since 1950.
   - That timing supports the "2027 volume shock, then a 2028 rebound" framing (H-02). The rebound still has to be tested.
7. **The macro backdrop is tighter than the mandate assumed:**
   - BI raised its rate by a surprise 25bp to 6.00% on 18 Nov; the 10-year SBN yield is 7.73%; the rupiah was Rp18,245/USD on 17 Nov [V-P BI; V-S].
   - The Fed hiked in September 2026 and held at 3.75–4.00% on 28 Oct. A December hike is priced in [V-S].
   - The cost of equity used so far (13.75%) is unchanged within ±2bp.
8. **No price, climate or vendor dataset is loaded.** The shell can't reach data hosts (§6). Quant modules C–I can't produce outputs until ingestion runs on a machine with internet access.

---

## 2. Reconciliation: mandate preliminary figures vs the record vs today's check

### 2.1 TAPG

| Mandate figure | Recorded in `RESEARCH_CONTEXT.md` | Check on 24 Nov 2026 | Status |
|---|---|---|---|
| Price ≈ Rp1,700 | Rp1,750 (19 Nov, Ajaib); ≈Rp1,715 (20 Nov, derived) | — | [MKT] Consistent. Re-price everything on one close (backlog item C-01) |
| 9M26 revenue Rp9.45tn | Rp9,446,621m [V-P] | Rp9.45tn vs Rp8.21tn, +15.09% (BCA Sekuritas/IQPlus, 28 Oct) | **Verified** [V-P] |
| 9M26 NP Rp3.51tn, +30.8% | Rp3,505,620m [V-P] | Rp3.51tn vs Rp2.68tn; EPS Rp177 vs Rp135 | **Verified** [V-P] |
| ROE ≈ 39% | FY25 33.6% [EST from V-P] | 3,506 × 4/3 ÷ 11,716 = **39.9%**, annualised 9M on period-end equity [EST] | Arithmetically right, but it annualises a cyclical-high 9M. Use FY ROE and a mid-cycle ROE for valuation |
| ROIC ≈ 35% | Aggregator 35.0%; operating ROIC ex cash, ex JV 33.0% (FY25) [EST] | — | Consistent; the definitions differ |
| P/B ≈ 2.9x | 2.97x at Rp1,750 | Rp1,715 × 19,852.54m = Rp34.05tn ÷ Rp11.716tn = **2.91x** [EST] | Verified |
| P/E ≈ 7.5x | 7.67x trailing at Rp1,750 | Rp34.05tn ÷ TTM Sep-26 Rp4.53tn = **7.5x** [EST] | Verified |
| Average tree age 14.6 years | [V-S] KB Valbury / Bareksa | — | Secondary only; needs AR planting-year table (gap T-04) |
| Nucleus FFB +3% | FY2025 nucleus FFB 3,040kt (+3%), AR 2025 p.12 [V-P] | — | Verified **for FY2025, not 2026** |
| FFB productivity +6%, CPO output +7%, CPO sales +7% | Not recorded | Not found. **Contrary 2026 evidence:** 1Q26 FFB −6% y/y and CPO −2% (Kontan); Indo Premier expected Q3 output −5% q/q; 3Q26 CPO sales 187.5kt, +20% y/y (KB Valbury) [V-S] | [UNV]. The 2026 volume trend is not established. Needs the quarterly operating releases |
| Mid-cycle NP Rp2.6tn | Phase I mid-cycle at RM3,900: Rp2.66tn [EST] | — | Remains a **hypothesis** (H-15), as the mandate says |
| Justified P/B: Rp1,700 needs ROE ≈34% (ke 13.75%, g 3%, BVPS ≈Rp590) | Phase II: ≈35% at 13.75% | BVPS = 11,716,496 ÷ 19,852.54 = **Rp590.2**. At Rp1,700, P/B 2.88x → ROE = 3% + 2.88 × 10.75% = **34.0%** [EST] | Verified. **But g = 3% is inconsistent with a 96.5% payout:** retention of 3.5% × ROE 34% ≈ 1.2% growth. At g = 1.2% the required ROE is **37.7%** (1.2% + 2.906 × 12.55%) [EST]. The market-implied sustainable ROE is therefore 34–38%, against FY25 33.6% and a Phase II mid-cycle of ≈24% |

### 2.2 DSNG (new primary coverage; Phase III ranked it 6th)

| Mandate figure | Recorded | Check on 24 Nov 2026 | Status |
|---|---|---|---|
| Price ≈ Rp1,265 | ≈Rp1,280 (20 Nov, derived) | Rp1,550 (30 Oct, +9.93% on results day, 2.7× 20-day volume); Rp1,325 (6 Nov, −14.5% in 5 sessions); Rp1,310 (16 Nov). 52-week range Rp1,045–1,875 [MKT: JournalArta; Investing.com] | Rp1,265 not found. Re-price on one close |
| 9M26 revenue Rp9.11tn | — | Rp9.10tn, +1.8% y/y (Rp8.94tn); palm segment ≈Rp8tn (88%) [V-S Kontan, 1 Nov] | Verified (rounding) |
| 9M26 consolidated profit Rp1.44tn; attributable Rp1.465tn | NP Rp1.46tn, +9.8% [V-S] | Press: "Rp1.46tn, +9.8% vs Rp1.31tn". But 1.46 ÷ 1.31 = **+11.5%**, so the stated growth does not match the stated figures | **[CONFLICT]** Attributable above consolidated implies negative NCI, yet FY25 NCI share was +Rp11.7bn [MKT]. Read the FS before any comparison |
| NP growth ≈9.8% | [V-S] | Same | Stated by the company, but the arithmetic doesn't reconcile (see above) |
| EBITDA growth ≈1.3% | — | Not disclosed in the press releases found | [UNV] |
| Net debt Rp2.67tn; ND/EBITDA 0.7x | (Rp2.76tn), Phase I aggregator | Aggregator: Jun-26 Rp2.757tn; Dec-25 Rp3.513tn; Dec-24 Rp5.176tn; Dec-23 Rp5.187tn. Debt repaid: Rp1.68tn in 2025, Rp1.72tn in 1H26 [MKT stockanalysis] | Jun-26 figure supported; Sep-26 Rp2.67tn [UNV]. **Note:** the deleveraging happened in 2025–1H26, not gradually since 2023 |
| FFB −4.3% | [V-S] | 1.5 Mt 9M26, −4.3% y/y; Q3 −5.7% q/q; El Niño cited, especially Kalimantan [V-S] | Verified |
| OER 23.73% | [V-S] | 23.73% 9M26; FFA 2.95% (3.03%); CPO 451kt (−1.5%); PK 85kt (−1%) [V-S] | Verified. CPO falls less than FFB because OER rose |
| Q2 inventory 23kt → Q3 52kt; Q3 output 151.9kt; sales 127.1kt; ASP Rp15,520/kg | — | Not found | **[UNV] + internal inconsistency:** 23.0 + 151.9 − 127.1 = **47.8kt**, so 4.2kt is unexplained (purchased CPO, a different basis, or an error). For reference, FY25 CPO ASP was Rp14,474/kg (+13.2%) [V-S] |
| FY26 nowcast Rp1.81 / 2.07 / 2.31tn; consensus ≈Rp2.26tn | Not recorded | — | **No provenance.** Not used. Calling Rp2.26tn "consensus" breaks mandate §11-E until a dated source is found. For scale: run-rate 9M × 4/3 = Rp1.95tn; the base case implies Q4 = Rp0.61tn vs a 9M quarterly average of Rp0.49tn [EST] |

### 2.3 LSIP

| Mandate figure | Recorded | Check on 24 Nov 2026 | Status |
|---|---|---|---|
| Price ≈ Rp1,600 | Rp1,605 (23 Nov) [MKT] | Rp1,470 at the buyback announcement (23 Oct) → Rp1,605 (+9.2%) | Consistent |
| Cash Rp8.52tn | Phase II flagged this as an aggregator figure; Rp8.372tn at 30 Jun 2026 [V-P] | 30 Sep 2026 FS not found | [UNV] for Sep-26. Keep Rp8.372tn (Jun) until the 9M FS are read |
| P/B ≈ 0.7x | 0.70x (aggregator) | Rp1,605 × 6,819.96m = Rp10.95tn ÷ Rp14.318tn (Jun equity) = **0.76x** [EST] | Approximately right |
| P/E ≈ 4.5x | Aggregator | 9M26 NP ≈Rp1.7tn [V-S] × 4/3 = Rp2.27tn → **4.8x** [EST] | Approximately right; the 9M FS are unverified |
| Buyback, maximum Rp750bn | Phase II: buyback [SPEC], 5% weight | Announced 23 Oct 2026 (disclosure by Corporate Secretary Fajar Triadi). Window 26 Oct–31 Dec 2026; internal cash; ≤20% of paid-up capital; no daily cap. INDF and ICBP announced identical Rp750bn programmes the same day (Salim group total Rp2.25tn) [V-S: Kontan, BCA Sekuritas/IQPlus, EmitenNews, Ajaib] | **Authorisation verified; execution [UNV].** Rp750bn = **6.9% of market cap** and **11.8% of Phase II excess cash** (Rp6,365bn) [EST]. At Rp1,470 it buys ≈510m shares (7.5%) |

**What the buyback changes (analysis, not a rating):**
- One Phase II watch trigger, "a buyback or special dividend", has partly fired: the buyback is authorised but not yet executed.
- Three dates carry information: the IDX execution reports, the 31 Dec window end, and whether the treasury shares are cancelled or resold. LSIP resold treasury shares in 2023 [V-S, Kontan 19 Oct 2023].
- A buyback also raises SIMP's 59.51% stake without SIMP spending any cash. That is relevant to H-07.

---

## 3. Macro verification (mandate §4)

| Variable | Latest reading | Date | Level | Mandate premise | Verdict |
|---|---|---|---|---|---|
| Fed funds | 3.75–4.00%, held (10–2; two dissents for a hike); last move +25bp in Sep 2026; a December hike is priced in | 28 Oct 2026 | V-S | "Restrictive" | **Confirmed, and tightening** |
| US 10-year Treasury | 4.90% | 4 Nov 2026 | V-S (Kontan) | — | High |
| DXY | Not checked | — | — | — | Gap M-01 |
| USD/IDR | Rp18,245 (−0.66% vs end-Oct); one year earlier Rp16,725 (20 Nov 2025) | 17 Nov 2026 | V-P (BI) | Depreciation | **Confirmed: −8.3% for the rupiah y/y** [EST] |
| BI-Rate | 6.00% (+25bp; DF 5.25%, LF 6.75%); consensus expected a hold at 5.75% | 18 Nov 2026 | V-P (BI release 28/254/DKom) | Elevated financing costs | **Confirmed; surprise hike** |
| Indonesia 10-year SBN | 7.73% (+5.5bp after BI); 4-year high 7.75% in early November | 18 Nov 2026 | V-S (MNC via Kontan) | Higher required return | **Confirmed** |
| GDP | 5.47% y/y in Q3 (Q2 5.29%, Q1 5.61%); BI 2026 range 4.9–5.7% | 5 Nov 2026 | V-S (BPS via several outlets) | Resilient | **Confirmed** |
| CPI | 3.23% y/y Oct (food 4.82%, transport 4.87%); 0.22% m/m | 2 Nov 2026 | V-S (BPS) | — | Inside the 2.5 ± 1% target, upper half |
| China / India activity | Not checked; the India CPO import duty cut to 5% from 24 Sep 2026 is recorded | — | — | — | Gap M-02 |
| Brent | USD 92.44 (16 Nov); about USD 111.7 on 1 Nov after the October rally; Goldman: USD 88 in 2027, USD 78 by Dec 2027 | 16 Nov 2026 | V-S | Geopolitical volatility | **Confirmed. Volatile, now falling** |
| Urea | Middle East granular about USD 425–435/t (paper, 6 Nov); Egypt USD 535/t FOB in Nov (+17% vs Sep). World Bank (Apr 2026): fertiliser index +31% in 2026, urea +60%, easing slightly in 2027 | Nov 2026 | V-S | Higher input costs | **Confirmed for 2026; 2027 direction disputed** (Ciptadana expects +20–30%) |

### 3.1 How these feed into company value [EST; inputs as tagged]

| Channel | Calculation | Size | Read |
|---|---|---|---|
| Cost of equity | 7.73% SBN + 6.0% ERP = 13.73% (vs 13.75% assumed) | −2bp | Assumption A-010 holds. Each +25bp on ke cuts the zero-growth P/E from 7.27x to 7.14x (−1.8%) and TAPG's justified P/B (ROE 34%, g 3%) from 2.88x to 2.82x (−2.3%) |
| Rupiah | −8.3% y/y × the Phase II elasticity (1% weaker rupiah → TAPG NP +2.4%, LSIP +2.0%) | TAPG ≈ +20%, LSIP ≈ +17% of FY25 NP, before cost pass-through | Upper bound. Duty and levy are in USD, and fertiliser and the discount rate move against it |
| Biodiesel funding vs Brent | Linear interpolation of the LPEM table (§5.4 of the context): Brent 92 → gap ≈ USD 136/t → 2027 subsidy ≈ **USD 1.2bn**; Brent 88 → ≈USD 1.4bn; Brent 78 → ≈USD 2.0bn. Levy revenue USD 2.5–3.0bn | Funded at current Brent; tight below ≈USD 80 | Pressure to raise the levy builds only if Brent keeps falling toward the Dec 2027 Goldman path |
| DSNG financing cost | Deleveraging since Dec-24: (5.18 − 2.76) Rp tn × an assumed 8% cost of debt × (1 − 22%) | ≈Rp151bn after tax ≈ **8% of run-rate NP** | Already in the numbers. Paying off all remaining net debt adds at most ≈Rp172bn (≈9%) |
| DSNG rate shock | +25bp on ≈Rp3tn of debt if it is all floating | ≈Rp6bn after tax (0.3% of NP) | Negligible |
| DSNG volume | Phase II elasticity for growers: own FFB −5% → NP −10% to −12% | — | **One 5% FFB decline roughly cancels the whole remaining deleveraging benefit.** Thesis B (lower financing cost offsets 2027 operating pressure) is weak on its own |
| Fertiliser | Phase II: +20% → TAPG −Rp117bn after tax (−3%) | −3% per +20% | Second order compared with volume and price |

---

## 4. Policy and regulatory verification (mandate §6–7)

| Item | Finding | Level | Status |
|---|---|---|---|
| B40 | Ran through 2025 (14.94m kL, 95.7% of allocation); 2026 allocation 15.65m kL (Kepmen 439.K/EK.01/MEM.E/2025, 23 Dec 2025) | V-P (ESDM) | Verified |
| B50 2026 | Kepmen ESDM 257.K/EK.01/MEM.E/2026, dated **17 Jun 2026**; in force 1 Jul 2026; evaluated every 3 months | V-S (Detik, Bisnis) + V-P citation in a Ditjen Migas decree | Verified |
| B50 2027 | Kepmen 113.K/EK.05/MEM.E/2026 (Apr 2026) sets B40 for 2026 and B50 "from 2027 onwards" [V-S]; Reuters: B50 the standard for all users by 2028. On 13 Nov 2026 ESDM (Eniya) said 2027 was under review, "I still have one month". Delivered 13.84m of 16.75m kL to Nov | V-S | **Phasing decree sets the target; the 2027 level and allocation are not decided.** Correct the context (it said "not decided" without the decree) |
| B60 | Target only; no allocation or regulation | V-S | Unchanged |
| PSO / non-PSO split; per-producer allocations | 2026: PSO 7.45m kL, non-PSO 8.19m kL; 26 biodiesel producers, 32 fuel distributors | V-P | **Per-producer volumes are in the Kepmen annex; not extracted** (gap P-02) |
| BPDP subsidy need 2027 | Rp12.7–47.2tn at Rp18,154/USD (LPEM via Katadata) | V-S | Verified as reported |
| PP 24/2026 | Set and promulgated 20 May 2026; in force 1 Jun 2026; LN 2026 (58), TLN 7178; status in force (BPK JDIH). Art. 3: export only via the export SOE (as owner or sole intermediary), which sets the price (3(2)) and may set a margin (3(4)). Art. 7: transition to 31 Dec 2026. Art. 8: contracts signed before 1 Jun 2026 to be evaluated by the export SOE | V-P (metadata); V-S (article text as quoted) | **Verified.** Open the full PDF for Art. 4–6 (fees, payment terms) — gap P-03 |
| Permendag 16/2026 | Commodity scope and DSI-only shipments from 1 Jan 2027 | V-S | Not re-checked; primary text still needed (gap P-03) |
| DSI fee | "Single-digit USD/t", to be announced in December 2026 | V-S | Pending |
| Duty schedule (PMK 38/2024 as amended) | Not seen | — | **Gap P-01: blocks the domestic price model** |

---

## 5. Climate verification (mandate §8.1)

| Item | Finding | Level |
|---|---|---|
| ENSO status | NOAA CPC, 12 Nov 2026: **El Niño Advisory**. Niño-3.4 +2.5 °C, Niño-3 +3.6 °C, Niño-1+2 +4.4 °C. Strong-to-very-strong likely through JFM 2027 (>79%). About 60% chance of a historic event (3-month RONI ≥ +2.5 °C) for OND and NDJ. Expected to **begin weakening in early 2027**. Next discussion 10 Dec 2026 | V-P |
| Index change | NOAA has used the Relative ONI (RONI) officially since Feb 2026. 3-month values to October: ONI +2.46, RONI +1.97 (2015/16: ONI +2.59, RONI +2.25) | V-S (secondary summary of the NOAA files) — check against the CPC file |
| Earlier record | The context cites "NOAA 63% chance of a very strong event, Nov 26–Jan 27 (Jul)" via Bisnis. NOAA's own July discussion gave 81% for a very strong event in OND | **[CONFLICT]** — superseded by the November reading |
| BMKG, IOD, regional rainfall, CHIRPS, ERA5, NASA POWER | **Not accessed this session.** The shell cannot reach these hosts | Gaps K-01 to K-04 |
| Estate-level exposure | No estate coordinates collected yet. DSNG cites El Niño "especially in Kalimantan" for lower FFB | Gap K-05 |

**What this means for the research design:** an El Niño of this scale is in the price everywhere. The only remaining edge is the one the mandate names in §8: estimating **which company's estates lose how much, and when**. That requires items K-01 to K-06 and company FFB history (D-07) before any claim can be made.

---

## 6. Data availability audit

**Access from this environment (24 Nov 2026):**
- **Web search and page fetch work.** Press, regulator pages, the NOAA CPC page and BI releases can be read.
- **The workspace shell cannot download files** from IDX, KSEI, Yahoo, FRED, NASA POWER, BMKG, MPOB, GAPKI or the ministries. This was tested in the earlier audit; only PyPI was reachable.
- **The "saham" connector (S-001)** listed 958 tickers but returned no history for AALI, BWPT or LSIP.
- **Consequence:** bulk ingestion must run on a machine with internet access, such as the user's computer running Claude Code, or from vendor or manual CSVs.

| ID | Dataset | Needed for | Best source | Access | Status | Priority |
|---|---|---|---|---|---|---|
| D-01 | DSNG 9M26 interim FS + 3Q26 operating release (inventory, sales volume, ASP, NCI, debt schedule) | Q-B | IDX filings; dsn.co.id | PDF download | **Missing** | **P1** |
| D-02 | LSIP 9M26 interim FS; IDX buyback execution reports | Q-C | IDX; londonsumatra.com | PDF | **Missing** | **P1** |
| D-03 | TAPG quarterly operating data 2021–3Q26 (nucleus/plasma FFB, yield, CPO output and sales); USTP JV accounts (FY25 Note 14a) | Q-A | IDX; tap-agri.com presentations | PDF | Partial (FY totals only) | **P1** |
| D-04 | Daily OHLCV, value traded, suspensions, corporate actions 2013–2026 for the universe, including delisted names | Modules A, C, F, H, I | IDX trading summary; KSEI; Yahoo only as a cross-check | Download (per day) or vendor | **Missing** | **P1** |
| D-05 | Estate list per company (name, regency/province, ha, mature ha, planting years) | Module D, §8.2 | Annual reports; RSPO/ISPO certificates; HGU maps; GFW concessions | PDF / GIS | **Missing** | **P1** |
| D-06 | Monthly rainfall 1990–2026 (CHIRPS 0.05°), ERA5 soil moisture / ET, NASA POWER | Module D | UCSB CHC; Copernicus CDS (API key); NASA POWER API | API / download | **Missing** | **P1** |
| D-07 | Company FFB / CPO history (quarterly, monthly if available) 2013–2026 | Lag model, nowcast | Quarterly reports, presentations | PDF | **Missing** | **P1** |
| D-08 | HR, duty and levy monthly 2016–2026 + the full PMK 38/2024 schedule | Price transmission | Kemendag Kepmendag HR; PMK texts (JDIH Kemenkeu) | PDF | 7 months seeded | P1 |
| D-09 | KPBN tender daily; Bursa FCPO continuous; Rotterdam CIF | Price model, regression | KPBN; Bursa Malaysia (vendor); press | Vendor / manual | **Missing** | P2 |
| D-10 | GAPKI and MPOB monthly vintages; USDA PSD | Supply and demand | gapki.id; mpob.gov.my; USDA FAS PSD | Download | 4 GAPKI months seeded | P2 |
| D-11 | JISDOR, Brent, SBN 10-year, BI-Rate, UST, DXY, urea | Module C, cost of capital | BI; FRED; World Bank Pink Sheet | API / download | Single readings only | P2 |
| D-12 | Broker estimates with dates; any consensus history | Module E surprise | Vendor (Bloomberg/FactSet) or broker PDFs | Vendor | **Unavailable** → labelled proxies | P2 |
| D-13 | Biodiesel allocation by producer (Kepmen annexes 2019–2026); BPDP reports | §6 value distribution | ESDM; BPDP | PDF | **Missing** | P2 |
| D-14 | Point-in-time HSC, suspension, listing and delisting history | Universe | IDX announcements | PDF / manual | 15 rows seeded | P2 |
| D-15 | Free float (KSEI monthly) | Investability | KSEI | Download | **Missing** | P3 |

**Datasets that can be built now in this environment (web tools):** D-02 buyback status, D-08 monthly HR, duty and levy rows from press, D-13 Kepmen texts, and D-14 HSC lists. Everything marked "download / API" needs a networked Claude Code run (see `context/CLAUDE_CODE_TASKS.md`).

---

## 7. Inconsistencies found and how they are recorded

| ID | Inconsistency | Action |
|---|---|---|
| C-11 | DSNG attributable vs consolidated profit; stated +9.8% vs computed +11.5% | Read the 9M26 FS (D-01). Use no DSNG profit comparison until then |
| C-12 | DSNG Q3 inventory build doesn't reconcile (4.2kt gap) | Same |
| C-13 | DSNG nowcast and "consensus Rp2.26tn" have no source | Do not use; rebuild in Module E with labelled proxies |
| C-14 | TAPG 2026 operating growth (+6% / +7% / +7%) vs 1Q26 FFB −6% | Get quarterly operating data (D-03) |
| C-15 | LSIP cash Rp8.52tn (aggregator) vs Rp8.372tn (Jun FS) | Use the FS figure; get the 9M FS |
| C-16 | B50 2027 described as "not decided" in the context, but a phasing decree sets B50 from 2027 | Context corrected: target set by decree; level and allocation under review |
| C-17 | NOAA probability cited via Bisnis (63%) vs NOAA July (81% very strong OND) | Superseded by NOAA 12 Nov |
| C-18 | The mandate lists ROE ≈39% as a reference figure; it is an annualised 9M | Use FY and mid-cycle ROE in valuation |
| C-19 | Primary coverage (TAPG, DSNG, LSIP) differs from the Phase III finalists (SIMP, SSMS, AALI) | Logged as D-003. Phase III finalists move to the comparison watchlist; the Phase III ranking is kept as a historical record, not a current view |

## 8. Sources

Primary and official:
- [NOAA CPC ENSO Diagnostic Discussion, 12 Nov 2026](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml)
- [Bank Indonesia, BI-Rate raised 25bp to 6.00% (18 Nov 2026)](https://www.bi.go.id/en/iru/highlight-news/Pages/BI-Rate-Raised-25-bps-to-6.00-percent-Strengthening-Stability,-Supporting-Economic-Growth.aspx)
- [BPK JDIH — PP 24/2026 metadata](https://peraturan.bpk.go.id/Details/349945/pp-no-24-tahun-2026)
- [ESDM — 2026 biodiesel allocation](https://www.esdm.go.id/id/media-center/arsip-berita/pemerintah-tetapkan-alokasi-biodiesel-tahun-2026-sebesar-1565-juta-kl)
- TAPG interim FS 30 Sep 2026 (via the Phase II register in `context/RESEARCH_CONTEXT.md` §6.1)

Secondary:
- [Kontan — LSIP buyback up to Rp750bn (23 Oct 2026)](https://investasi.kontan.co.id/news/london-sumatra-lsip-bakal-buyback-saham-maksimal-rp-750-miliar)
- [BCA Sekuritas/IQPlus — LSIP buyback terms](https://bcasekuritas.co.id/latest-news/news/lsip-siapkan-dana-rp750-miliar-untuk-buyback-saham)
- [Ajaib — Salim group buybacks](https://ajaib.co.id/belajar/berita/grup-salim-siapkan-rp225-t-untuk-buyback-indf-icbp-lsip)
- [Kontan — DSNG 9M26 results (1 Nov 2026)](https://industri.kontan.co.id/news/dharma-satya-dsng-bukukan-laba-rp-146-triliun-pada-kuartal-iii-2026)
- [Kontan — DSNG deleveraging (30 Oct 2026)](https://industri.kontan.co.id/news/laba-dsng-tumbuh-98-jadi-rp-14-triliun-ini-penopang-kinerjanya)
- [BCA Sekuritas — TAPG 9M26](https://bcasekuritas.co.id/latest-news/news/pendapatan-tapg-tumbuh-1509-hingga-september-2026)
- [Kontan — TAPG 1Q26 FFB −6%](https://insight.kontan.co.id/news/strategi-mitigasi-tapg-hadapi-cuaca-ekstrem-prospek-tetap-positif)
- [Katadata — B50 2027 review](https://katadata.co.id/berita/energi/6af672fb051a7/pemerintah-kaji-ulang-b50-ekspor-sawit-dan-beban-subsidi-jadi-taruhan)
- [Listrik Indonesia — Kepmen 113.K/2026 phasing](https://listrikindonesia.com/detail/19708/bedah-kepmen-pemanfaatan-bbn-jalan-panjang-menuju-b50)
- [Detik — Kepmen 257.K/2026 (B50)](https://finance.detik.com/energi/d-8554334/bahlil-terbitkan-aturan-b50-berlaku-mulai-1-juli)
- [Kontan — SBN 10-year 7.73% after BI](https://investasi.kontan.co.id/news/bi-rate-naik-jadi-6-yield-sun-tenor-10-tahun-melonjak-55-bps)
- [Kontan — UST 10-year 4.90%](https://investasi.kontan.co.id/news/permintaan-obligasi-menguat-yield-sun-10-tahun-bertahan-di-772)
- [Ajaib — FOMC 28 Oct 2026](https://ajaib.co.id/belajar/saham-as/the-fed-tahan-suku-bunga-3754-inflasi-masih-tinggi)
- [Bisnis — Q3 2026 GDP 5.47%](https://ekonomi.bisnis.com/read/20261105/9/2018647/breaking-pertumbuhan-ekonomi-kuartal-iii2026-capai-547)
- [Bisnis — October 2026 inflation](https://ekonomi.bisnis.com/read/20261102/9/2017534/breaking-inflasi-oktober-2026-melandai-ke-022)
- [KabarBursa — Brent USD 92.44 (16 Nov)](https://www.kabarbursa.com/market-hari-ini/aliran-dari-selat-hormuz-dinilai-aman-harga-minyak-anjlok-lebih-dari-tiga-persen)
- [UkrAgroConsult — Egyptian urea USD 535/t](https://ukragroconsult.com/en/news/egyptian-urea-prices-rise-to-535-per-ton-amid-gas-supply-restrictions/)
- [Katadata — World Bank fertiliser outlook](https://katadata.co.id/berita/industri/69f2e634d69c8/harga-pupuk-global-diprediksi-naik-31-tahun-ini-bisa-ancam-ketahanan-pangan)
- [stockanalysis.com — DSNG balance sheet (aggregator)](https://stockanalysis.com/quote/idx/DSNG/financials/balance-sheet/)
- [JournalArta — DSNG price, 6 Nov](https://journalarta.com/news/2026/11/09/teknikal-saham-dsng-melemah-3-28-pada-jumat-momentum-melemah/)
- [Investing.com — DSNG, 16 Nov](https://kr.investing.com/equities/dharma-satya-n)
