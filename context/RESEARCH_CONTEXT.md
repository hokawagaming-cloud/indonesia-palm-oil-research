# Research Context

_Last updated: 2026-11-24 · Research as-of date: 24 November 2026 (no information published after this date is used)._

This file is the shared memory for the project. It consolidates every piece of palm oil research done so far: the original TAPG thesis, the Phase I stress-test, the Phase II TAPG vs LSIP review, the Phase III sector-wide alpha discovery, and the quant framework design. It does not add new research. Where two pieces of work disagree, the conflict is recorded in [§13](#13-conflicts-and-corrections) rather than silently resolved.

_Research only — not investment advice._

---

## How to read this file

Every claim carries one of these tags.

| Tag | Meaning |
|---|---|
| **[V-P]** | Verified from a primary source: an audited or interim filing, a regulation, or an official release that was opened and read. |
| **[V-S]** | Verified from a secondary source: reputable press or a broker summary of a primary release. Not yet checked against the primary document. |
| **[MKT]** | Market data from an aggregator or quote page (prices, multiples), with the date shown. |
| **[EST]** | My own calculation or estimate. The inputs and method are stated next to it. |
| **[HYP]** | A hypothesis: a view that has not yet been tested. Each one has a test or an invalidation condition in [§11](#11-hypothesis-register). |
| **[SPEC]** | A speculative catalyst with no announcement behind it. |
| **[REJ]** | A hypothesis that was tested and rejected or downgraded. See [§12](#12-rejected-and-downgraded-hypotheses). |

Units: Rp = Indonesian rupiah; tn = trillion; bn = billion; t = tonnes; Mt = million tonnes; ha = hectares; FFB = fresh fruit bunches; OER = oil extraction rate; HR = CPO reference price (Harga Referensi); JV = joint venture; NCI = non-controlling interests.

---

## Contents

0. [Current view](#0-current-view)
1. [Objective and scope](#1-objective-and-scope)
2. [Universe and investability](#2-universe-and-investability)
3. [Research timeline and documents](#3-research-timeline-and-documents)
4. [Original TAPG thesis (24 Nov 2026)](#4-original-tapg-thesis-24-nov-2026)
5. [Phase I — TAPG thesis stress-test](#5-phase-i--tapg-thesis-stress-test)
6. [Phase II — TAPG vs LSIP comparative review](#6-phase-ii--tapg-vs-lsip-comparative-review)
7. [Phase III — Sector-wide alpha discovery](#7-phase-iii--sector-wide-alpha-discovery)
8. [Quantitative research methodology](#8-quantitative-research-methodology)
9. [Verified facts register](#9-verified-facts-register)
10. [Assumptions used in the analysis](#10-assumptions-used-in-the-analysis)
11. [Hypothesis register](#11-hypothesis-register)
12. [Rejected and downgraded hypotheses](#12-rejected-and-downgraded-hypotheses)
13. [Conflicts and corrections](#13-conflicts-and-corrections)
14. [Data gaps](#14-data-gaps)
15. [Catalyst calendar](#15-catalyst-calendar)
16. [Next steps](#16-next-steps)
17. [Source references](#17-source-references)

---

## 0. Current view

**Governing brief from 24 Nov 2026: the Master Research Mandate** (D-003).
- **Primary coverage:** TAPG, DSNG, LSIP.
- **Priority questions:** Q-A (is TAPG's premium justified?), Q-B (is DSNG's discount a recovery or deserved?), Q-C (is LSIP's cash realisable?).
- **Phase:** 1 (verification). No rankings or ratings until Phase 6 (D-006); NO TRADE is a valid outcome.
- **Phase 0–1 audit:** `research/2026-11-24_phase1_verification_audit.md`.
- **Backlog:** `context/RESEARCH_BACKLOG.md`.
- **Claude Code spec:** `context/CLAUDE_CODE_TASKS.md`.

**What changed in Phase 0–1 (24 Nov 2026):**
- **LSIP buyback:** a Rp750bn buyback was **announced** on 23 Oct for 26 Oct–31 Dec 2026 [V-S]. It equals 6.9% of market cap and 11.8% of excess cash. Execution is unverified.
- **DSNG reference figures:** the mandate's numbers are internally inconsistent (C-11 to C-13).
- **TAPG ROE:** the ≈39% is an annualised 9M figure.
- **B50 2027:** set by a phasing decree, but under review.
- **El Niño:** historic scale, expected to weaken in early 2027 (NOAA, 12 Nov) [V-P].
- **BI rate:** surprise hike to 6.00% (18 Nov) [V-P].

The bullets below are the **Phase I–III view as of 24 Nov 2026**. They are kept as a record and are not current ratings.

- **TAPG:** initiate full coverage, but no BUY. It is the best operator in the group: FFB yield is 24.3 t/ha, OER is 23.3%, and operating ROIC is about 33% excluding cash and the JV. But at Rp1,750 (19 Nov 2026) the price capitalises 2026-level profit as permanent. The preliminary value range is Rp1,100–1,600 [EST]. The original thesis ("structurally underpriced re-rating") is rejected. What survives is a narrower one: "quality yield at a fair price".
- **LSIP:** watch list with defined triggers. Its cash is real, and about Rp6.4tn (Rp933/share) is genuinely excess [EST]. But the payout has been 30–35% for three years, part of the cash sits with Salim-group entities, and the operations are weak (13.4 t/ha). The probability-weighted value is Rp1,560–1,710 [EST], close to the price.
- **Sector:** the popular story, "El Niño + B50 → CPO up → planters re-rate", mostly fails for Indonesian growers. In the current price band, duty plus levy absorbed 98–99% of the last two monthly reference-price moves [EST from V-S data], and El Niño is a 2027 *volume* shock. The mispricings that the evidence supports come from ownership and index mechanics, not commodity beta.
- **Three names for forensic work and bottom-up modelling (Phase III):** **SIMP**, **SSMS** and **AALI**. **BWPT** and **LSIP** are next. Avoid TAPG on price, TBLA because its biodiesel capacity is capped, and JARR because it is not investable and trades at about 46x run-rate earnings.
- **Quant framework:** designed, with the data audit done. No data source was reachable from the cloud workspace. Rankings are locked until the data passes the quality gates ([§8](#8-quantitative-research-methodology)).

---

## 1. Objective and scope

_Carried over from the earlier version of this file. It is unchanged except for links to the work done since._

**Objective.** Identify underappreciated investment opportunities in Indonesian palm oil equities before fundamental catalysts are fully priced in, combining fundamental and quantitative research (quantamental).

**Scope.**
- **Market:** Indonesia Stock Exchange (IDX), plus Indonesian palm oil exposure listed elsewhere if relevant (to be decided).
- **Sector:** upstream plantations (primary), integrated upstream and downstream producers, and possibly downstream refiners and biodiesel names. Phase III covered the whole value chain. No listed palm logistics or fertiliser pure-play was found; that remains a gap.
- **Horizon:** to be defined. The original thesis used 12–24 months; the Phase III brief used the next 4–8 quarters.

**Key research questions (original).**
1. Which fundamental drivers (CPO price, production growth, tree age profile, cost per tonne, export levy and duty, biodiesel mandate, FX) explain the cross-section and time series of plantation equity returns?
2. Where is the market mispricing these drivers, for example production recovery from replanting, cost deflation, or mandate-driven demand?
3. Which upcoming catalysts (B40/B50 mandate changes, levy revisions, EUDR enforcement, El Niño/La Niña cycles, monthly production releases, earnings) are not yet reflected in prices or consensus?
4. Can quantitative signals (valuation, momentum, revisions, production surprises, weather) generate risk-adjusted excess returns out of sample?

**Partial answers so far.**
- Q1–Q2: the levy and duty mechanism, tree age, external FFB dependence and the capital-allocation discount matter more than the CPO futures price.
- Q3: see [§15](#15-catalyst-calendar).
- Q4: not yet tested; the data is not loaded.

**Open questions (still open).** Investment horizon and rebalancing frequency; benchmark; data sources and access (vendor vs public); long-only or long/short. The quant settings assume long-only, because shorting is not practically available on IDX ([D-002 note in §2](#2-universe-and-investability)).

---

## 2. Universe and investability

### 2.1 Universe recorded in the decision log (D-002, 2026-11-24)

Source: `research/industry/2026-11-24_universe_screen.md`. That screen used S-001 (the "saham" price dataset, weekly sampling, last updated 2026-11-07). Its liquidity figures are indicative.

- **Core (9):** DSNG, SSMS, TAPG, STAA, LSIP, MGRO, NSSS, GZCO, AALI. Used for quant signals, backtests and full fundamental coverage.
- **Extended (6):** ANJT, TBLA, SIMP, BWPT, CSRA, PSGO. Fundamental coverage only, flagged for liquidity.
- **Excluded:** SGRO, SMAR, TLDN, FAPA, CBUT, JAWA, UNSP, PGUN.
- **Screening rule:** core = approx. ≥ IDR 1.5bn average daily traded value; extended = IDR 0.25–1.5bn.

### 2.2 Investability overlay from Phase III (24 Nov 2026)

This does not change D-002. It is new evidence that should be logged as a decision before the universe is changed.

**[V-S]** In November 2026 the IDX widened its High Shareholding Concentration (HSC) list to any stock whose top 10 holders own at least 92.5%. It published 383 names and removed them from IHSG weighting from **13 Nov 2026 to 29 Jan 2027** (Peng-HSC-00088/BEI.WAS/11-2026). The IDX states that HSC status is not a sanction.

**[V-S]** MSCI's May 2026 review removed **AALI, DSNG, SSMS and TAPG** from the MSCI Small Cap index. The exact announcement date still needs verifying; the first press report is dated 13 May 2026.

**Market backdrop:**
- **[MKT]** IHSG closed at 5,194 on 18 Nov 2026, against about 8,400 in Nov 2025.
- **[V-S]** The rupiah was about Rp18,150/USD in early November. Phase I used Rp16,725 (20 Nov 2025, BI) → Rp18,254 (19 Nov 2026, Kontan).
- **[V-S]** MSCI has two reviews left in which it could move Indonesia to standalone status.

| Ticker | Value chain | Control / concentration | Index status | Price used (date) | Investable at fund size? |
|---|---|---|---|---|---|
| AALI | Upstream + refining | Astra | Out of MSCI SC (May 26) | Rp9,750 (20 Nov) [MKT] | Yes |
| TAPG | Upstream + JV mills | Triputra | Out of MSCI SC (May 26) | Rp1,750 (19 Nov, Ajaib); ≈Rp1,715 (20 Nov, derived) [MKT] | Yes |
| LSIP | Upstream | SIMP 59.51% [V-P] | — | Rp1,550 (19 Nov, derived); Rp1,560 (20 Nov); Rp1,605 (23 Nov) [MKT] | Yes |
| DSNG | Upstream + wood | Triputra / TP Rachmat | Out of MSCI SC (May 26) | ≈Rp1,280 (20 Nov, derived) [MKT] | Yes |
| SIMP | Upstream + edible oils + refining | IndoAgri 73.46%; public 12.96% [V-S] | Not on the HSC lists found | ≈Rp560 (late Nov, undated quote) [MKT] | Yes, but thin (about Rp5bn/day) |
| SSMS | Upstream + refining (CBUT) | Citra Borneo Indah 62.3% [V-S] | **HSC since 13 Oct 2026**; out of MSCI SC | Rp920 (20 Nov) [MKT] | Restricted (excluded from IHSG and passive flows) |
| BWPT | Upstream | Rajawali 37.7%; FICP (FELDA) 37% [V-S] | — | Rp96 (15 Oct; no newer quote found) [MKT] | Yes, with a 37% overhang |
| TBLA | Refining + biodiesel + sugar | Sungai Budi group ≈59.5% [V-S] | — | ≈Rp600 (late Nov, undated) [MKT] | Yes |
| SMAR | Refining + biodiesel | Purimas Sasmita 92.4% | **HSC 99.56%**; free float ≈7.5% | — | No |
| JARR | Biodiesel + estates | Eshan Agro (Haji Isam) | **HSC 98.02%**; suspended 11 Sep 2026 | ≈Rp2,300 (20 Oct) [MKT] | No |
| ANJT | Upstream (incl. Papua) | First Resources ≈96–99% | **HSC 99.132%** | Rp1,495 (Aug) | No |
| SGRO (now PT Prime Agri Resources) | Upstream | AGPA (POSCO International) 65.72% + MTO | HSC | MTO price Rp7,903 | No |
| STAA, CSRA, TLDN, PGUN (99.956%), PSGO, PNGO, CBUT, JAWA, FAPA (99.77%) | Mixed | Concentrated | **HSC** | — | No |

**Implications for D-002 (to decide and log):**
- **STAA (core) and CSRA and PSGO (extended) are now HSC [V-S].** Moving them out of the backtest universe should be considered, using point-in-time status rather than removing them from history.
- NSSS, MGRO, GZCO and UNSP were not analysed in Phase III.
- PALM is a holding company; check its current business before including it.

---

## 3. Research timeline and documents

| Date | Phase | Document | Outcome |
|---|---|---|---|
| 24 Nov 2026 | Original thesis | "Preliminary Equity Research Thesis — TAPG" (user-supplied) | Four pillars; rating not assigned |
| 24 Nov 2026 | Phase I | [TAPG Thesis Stress-Test — Buy-Side Review](https://claude.ai/artifact/AVP7koSabCSUYHNndFznq9) | No BUY; variant perception rejected; LSIP flagged as the better risk-adjusted name |
| 24 Nov 2026 | Phase II | [TAPG vs LSIP — Phase II Comparative Review](https://claude.ai/artifact/1QCMj3DF2KeeQvynGcPUtL) | Initiate TAPG; LSIP on watch; 10 Phase I corrections |
| 24 Nov 2026 | Phase III | [Indonesian Palm Oil — Sector Alpha Discovery](https://claude.ai/artifact/9pC6u7RDyMYb67ebr7ZCoK) | SIMP, SSMS, AALI to forensic work; BWPT, LSIP next |
| 24 Nov 2026 | Quant brief | "Indonesian Palm Oil Quantamental Research Engine" (user-supplied) | Data audit done; architecture, configs and seed data started; build interrupted before the modules were complete |
| 24 Nov 2026 | Mandate | "Master Research Mandate — Indonesian Palm Oil Quantamental Equity Research" (user-supplied) | Primary coverage TAPG / DSNG / LSIP; Phases 0–6; deliverables 1–18 |
| 24 Nov 2026 | Phase 0–1 | [`research/2026-11-24_phase1_verification_audit.md`](../research/2026-11-24_phase1_verification_audit.md) | Mandate figures reconciled; macro, policy and climate verified; data audit; backlog and Claude Code spec |

All three research documents are Claude Docs artifacts. They hold the full tables and source links. This file keeps the figures that later work depends on.

---

## 4. Original TAPG thesis (24 Nov 2026)

_Summarised from the user's preliminary thesis. These were the hypotheses under test, not findings._

- **Company:** PT Triputra Agro Persada Tbk (IDX: TAPG).
- **Horizon:** 12–24 months.
- **Rating:** not assigned.
- **Core hypothesis:** Indonesia's energy-security policy (B40 → B50 → possibly higher) creates government-induced domestic CPO demand. Combined with constrained supply, that tightens the market. TAPG, as a cost-competitive upstream producer, captures this through higher realised prices, efficiency, margin expansion and free cash flow, provided the market has not already priced it in.

| Pillar | Hypothesis | Transmission assumed |
|---|---|---|
| I. Structural biodiesel demand | B40 → B50 (and beyond) structurally raises domestic CPO use | Higher mandate → more domestic CPO use → smaller exportable surplus → tighter global supply → higher CPO price → higher realised price for upstream |
| II. Structural supply constraint | Little new land, ageing trees, slow smallholder replanting, climate and deforestation rules make supply inelastic | Inelastic supply amplifies the price effect of extra demand |
| III. TAPG operating advantage | Productivity, age profile, OER and cost make TAPG structurally better than peers | Benchmarked against AALI, DSNG, LSIP, SSMS |
| IV. Operating leverage and shareholder returns | Competitive cost plus higher prices → disproportionate profit → FCF, dividends, re-rating | Net of maintenance and replanting capex, working capital and tax |
| Macro tailwind | Rupiah depreciation lifts IDR selling prices | Net of imported fertiliser, FX liabilities and export deductions |
| Variant perception | The market values TAPG as a plain cyclical; policy creates a persistent demand floor | To be tested against valuation, history, consensus and reverse DCF |

- **Proposed valuation:** primary FCFF DCF (FY2026E–FY2031E), driver-based; terminal value at mid-cycle profitability.
- **Cross-checks:** forward P/E, EV/EBITDA, dividend yield, reverse DCF, historical multiples.
- **Sensitivities:** CPO, USD/IDR, FFB yield, OER, cash cost, levies, replanting capex, WACC and terminal growth.
- **Central question:** "Can Indonesia's expanding biodiesel ambitions create a structural demand floor for palm oil that enables TAPG to generate sustainable excess returns, and is this opportunity sufficiently underpriced by the market?"

---

## 5. Phase I — TAPG thesis stress-test

**Verdict.** No BUY on the thesis as written. The direction is right, because 2027 palm supply will be tight. But the cause is mostly weather, not policy, and most of the benefit is already in the price.

### 5.1 Scorecard

| Thesis | Verdict | Why | Earnings lever (Phase I estimate) [EST] |
|---|---|---|---|
| I. Biodiesel demand | Partially supported | B50 is enacted; the 2027 blend is not set and depends on crude; B60 is a target only | B40 → B50 adds ≈2.7 Mt CPO demand, ≈3.4% of world palm output |
| II. Supply constraint | Partially supported (cyclical until 2028) | 2027 tightness is mostly El Niño; smallholder replanting is the real structural problem | Each Rp1,000/kg on ASP ≈ Rp0.74tn net profit (≈20% of FY25) |
| III. Operating advantage | Partially supported | ROIC 28–35% is real but flattered by old book costs; average tree age 14.6 years, near plateau | Guided 6–10% volume growth not yet visible in 2026 |
| IV. Operating leverage / payouts | Supported mechanically, no upside | Payout ≈97% already | 2026 dividends Rp130 → 7.4% yield at Rp1,750 |
| Rupiah tailwind | Partially supported | Domestic price gains, but the 10-year SBN rose to 7.75% | 1% weaker rupiah ≈ +3% net profit before costs |
| Variant perception | **Rejected** | P/B at a record high; the price already assumes today's earnings last | Market-implied net profit Rp3.8–4.2tn vs ≈Rp2.6tn mid-cycle |

### 5.2 Supply and demand evidence

USDA, November 2026 (marketing year Oct–Sep, Mt) [V-P, USDA FAS]:

| Item | 2025/26 | 2026/27F | Change |
|---|---|---|---|
| Indonesia palm production | 47.00 | 45.00 | −2.00 |
| Indonesia palm exports | 25.03 | 21.60 | −3.43 |
| Indonesia domestic use | 22.83 | 23.38 | +0.55 |
| Malaysia palm production | 20.56 | 19.60 | −0.96 |
| World palm production | 82.10 | 78.92 | −3.18 |
| World palm ending stocks | 15.21 | 13.77 | −1.43 |
| Soy + rapeseed + sunflower oil output | 131.39 | 137.29 | +5.90 |
| World vegetable oil ending stocks | 30.50 | 29.67 | −0.83 |

**Supports a tight 2027:**
- USDA cut its Indonesia 2026/27 estimate from 48.0 Mt (April) to 47.2 Mt, then to 45.0 Mt (October) [V-P, USDA ERS].
- GAPKI projects 2027 CPO output down 3.7% to 51.73 Mt, domestic use up 11.4% to 30.2 Mt, and exports down 4.63 Mt to 26.49 Mt [V-S].
- BMKG calls the El Niño "very strong", with a Niño 3.4 anomaly of +2.63 in September [V-S].

**Contradicts it:**
- Malaysia's stocks hit a record 3.62 Mt in October 2026, against 2.46 Mt a year earlier [V-S].
- GAPKI's 2026 Indonesian output estimate is 53.73 Mt, up about 4% on 51.66 Mt in 2025 [V-S].
- Substitute oils add 5.9 Mt [V-P].
- CPO averaged RM4,424/t through October 2026, 37% above the 10-year average of RM3,224 [V-S].

**Structural vs not:**
- **Structural:** smallholders hold about 42% of planted area, and PSR replanting runs at about 50,000 ha a year against a 180,000 ha target [V-S].
- **Not structural:** El Niño yield losses usually reverse within one to two years [HYP, to check against MPOB and GAPKI history].
- **Open question:** what Agrinas Palma does with about 730,000 ha of planted land seized by the forestry task force.

**Scale check [EST]:** GAPKI's +2.71 Mt of extra biodiesel CPO in 2027 is 3.4% of world palm output and 1.1% of world vegetable oil output.

### 5.3 Biodiesel policy status (law vs target)

| Measure | Status | Date | Key number |
|---|---|---|---|
| 2026 allocation (B40 basis) | Enacted: Kepmen ESDM 439.K/EK.01/MEM.E/2025 [V-P] | 23 Dec 2025 | 15.65m kL (PSO 7.45m; non-PSO 8.19m); 32 fuel distributors (BU BBM), 26 biodiesel producers (BU BBN) |
| B50 mandate | Enacted (regulation); specification Kepmen 257.K/EK.01/MEM.E/2026 [V-S] | In force 1 Jul 2026; B40 stock usable to 30 Sep 2026 | Allocation raised to 16.75m kL; 13.84m kL delivered to Nov (83%) [V-S] |
| B50 for 2027 | **Target set by the phasing decree Kepmen 113.K/EK.05/MEM.E/2026 (B50 "from 2027 onwards") but under review; no 2027 allocation** [V-S] (corrected 24 Nov, C-16) | ESDM meeting the week after 13 Nov 2026; "I still have one month" (Eniya, ESDM) | — |
| B60 in 2027 | **Target only** [V-S] | Announced Sep 2026 | No allocation or regulation |
| B40, 2025 | Completed | 2025 | 14.94m kL, 95.7% of allocation [V-S] |

- GAPKI: biodiesel CPO demand goes from 14.69 Mt (2026) to 17.4 Mt (2027) if B50 runs all year [V-S].
- If B60 happened, scaling 17.4 Mt by 60/50 adds about 3.5 Mt [EST].
- **Who captures the value:** biodiesel makers sell FAME at a regulated index (HIP = CPO + conversion cost), so their margin is close to guaranteed. Only PSO volume (≈48% of the 2026 allocation) is subsidised. Growers gain only through the domestic CPO price, which equals export parity minus duty and levy.
- The March 2026 levy rise from 10% to 12.5% cost about Rp447/kg at the November HR and FX [EST].

### 5.4 Levy funding sustainability

2027 subsidy need (LPEM FEB UI, at Rp18,154/USD) [V-S]:

| Brent (USD/bbl) | Diesel reference (USD/t) | Biodiesel index (USD/t) | Gap (USD/t) | 2027 subsidy need |
|---|---|---|---|---|
| 100 | 850 | ≈930 | 80 | ≈USD 0.7bn |
| 80 | 710 | ≈930 | 220 | ≈USD 1.9bn |
| 70 | 630 | ≈930 | 300 | ≈USD 2.6bn |

- LPEM estimates 2027 levy revenue at USD 2.5–3.0bn on 26.5 Mt of exports [V-S].
- The levy went from 7.5% to 10% in May 2025, then to 12.5% on 1 Mar 2026 [V-S].
- 2026 levy collections were expected at Rp41.22tn (+31%) [V-S].
- BPDP paid about Rp17tn of subsidy in 1H26 (53% of its full-year projection), and none in Apr–Jun 2026 [V-S].
- Each USD 100/t rise in the biodiesel index adds about USD 0.86bn to the bill (≈30% of levy revenue) [EST].
- **Assessment:** sustainable with Brent at USD 90 or above, tight at USD 80, in deficit at USD 70 unless the levy rises. The government's levers are a higher levy, a lower blend, the state budget, or pushing cost onto non-PSO buyers. The budget is a weak backstop: the 10-year SBN is 7.75% after BI raised its rate to 6%, and each 10bp adds about Rp1.8tn to state spending [V-S].

### 5.5 Export governance (DSI)

- **[V-S] PP 24/2026** (signed 20 May 2026, in force 1 Jun 2026). Article 3 lets only the state export firm sell coal, palm oil and ferroalloys abroad, as owner or sole intermediary. The firm sets the price (Art. 3(2)) and may set a margin "within reasonable levels" (Art. 3(4)).
- **[V-S] Permendag 16/2026** covers CPO, RBDPO, RBD olein, used cooking oil and palm residue. The transition runs 1 Jun–31 Dec 2026; only DSI (PT Danantara Sumberdaya Indonesia) or designated state exporters may ship from **1 Jan 2027**.
- **[V-S]** The domestic market obligation (DMO) stays.
- **[V-S]** The DSI fee is indicated at "single-digit USD/t", with the final rate due in **December 2026**. Officials have given conflicting messages on whether DSI will be run for profit.
- **[V-S]** GAPKI said the May 2026 announcement pushed domestic CPO and FFB prices down. Indo Premier estimates each Rp100k/t of extra export cost cuts FY27–28 earnings by 1–4%, with AALI the most exposed.
- **Exposure:**
  - TAPG: no direct exports, by management statement.
  - SSMS: about 900kt exported in 9M26.
  - SMAR: 47% of 2025 sales were exports.
  - DSNG and BWPT: say they sell mainly domestically.
- **[HYP]** Because domestic price = export parity − duty − levy − costs, a slow or conservative DSI widens the domestic discount, as happened in the 2022 export ban. That makes this a governance discount for domestic sellers, not a premium.

### 5.6 TAPG operations (Phase I view)

- **Age:** average tree age 14.6 years; about 4,000 ha replanted a year [V-S, KB Valbury / Bareksa].
- **OER:** about 23.3% (9M25: 708kt CPO from 3.04 Mt FFB) [EST].
- **Bought-in fruit:** about 16% of FFB processed [EST].
- **2026 volume:** FFB guided +6–10%; Q1 revenue −4.9% on lower volume [V-S].
- **Q3 2026** [V-S]:
  - CPO sold 187,500 t (+20% y/y) at Rp15,565/kg (+9.5%).
  - Fertiliser spend fell 23% y/y because drought delayed application. KB Valbury expects it to catch up in Q4 26–Q1 27, so part of the margin gain is timing.
- **Fertiliser outlook conflicts** [V-S]: Ciptadana cut 2026–27 forecasts 21–23% on an expected 20–30% fertiliser price rise; the World Bank (via Phintraco) expects its index to fall about 12% in 2027.
- **Capex** [V-S]: Rp920bn in 2026 (usual Rp650–750bn), mainly a 45 t/hour mill due late 2027 to early 2028.
- **Peer ROIC** [MKT, stockanalysis]: TAPG 35.0%, DSNG 13.7%, AALI 9.5%.

### 5.7 TAPG financial history (Phase I, aggregator data)

[MKT, stockanalysis.com; Rp tn]. Phase II replaced several of these with audited figures ([§6.3](#63-financial-quality)).

| Year | Revenue | Op. profit | Op. margin | Net profit | EPS (Rp) | DPS (Rp) | OCF | FCF | FCF / NP | ROIC | Net cash |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TTM Jun-26 | 11.75 | 4.01 | 34.2% | 4.05 | 203.9 | — | 3.31 | 2.69 | 66% | 31.4% (Sep-26) | 2.13 |
| FY2025 | 11.40 | 3.67 | 32.2% | 3.70 | 186.5 | 180 | 3.43 | 2.81 | 76% | 28.0% | 1.08 |
| FY2024 | 9.67 | 3.06 | 31.7% | 3.12 | 157.2 | 152 | 3.24 | 2.65 | 85% | 22.6% | 0.28 |
| FY2023 | 8.33 | 1.39 | 16.7% | 1.61 | 81.0 | 91 | 1.57 | 0.77 | 48% | 10.7% | −0.08 |
| FY2022 | 9.35 | 2.97 | 31.8% | 2.98 | 150.2 | 38 | 3.18 | 2.44 | 82% | 24.1% | −0.38 |
| FY2021 | 6.28 | 1.22 | 19.5% | 1.16 | 59.0 | 25 | 1.46 | 0.98 | 85% | 10.7% | −2.04 |

- 9M2026: revenue Rp9.45tn (+15.1%); net profit Rp3.51tn (+30.8%) [V-S].
- FY2023 showed the cyclicality: revenue −11%, operating profit −53%.
- FY2024 audit key matter: impairment of mature bearer plants at certain estates [V-P].

### 5.8 Phase I valuation (TAPG)

- **Price:** Rp1,750 on 19 Nov 2026; market cap Rp34.74tn; trailing P/E 7.67x; P/B 2.97x vs 0.95–1.55x in FY2021–23 [MKT].
- **Range:** 52-week range Rp1,255–2,480; all-time high Rp2,480 on 9 Sep 2026 [MKT].
- **Consensus:** 9M26 profit was 85% of consensus, implying FY26 consensus of about Rp4.13tn and FY26 P/E of about 8.4x [V-S/EST]. In May 2026, 11 analysts: 9 Buy, 2 Hold, average target Rp2,388. KB Valbury Rp2,500 (30 Oct); Ciptadana Rp1,980 (June); Phintraco sector top pick (11 Nov) [V-S].
- **Dividends:** 2026 interims Rp60 (Aug) + Rp70 (ex 11 Nov) = Rp130 → 7.4% yield [V-S].
- **Insiders:** the president director sold 850,000 shares at Rp2,010 (Aug) and bought 200,000 at Rp1,875 (3 Nov) [V-S].

Reverse DDM (cost of equity 13.75% = 7.75% SBN + 6.0% ERP; 90% payout) [EST]. Phase II relabelled this from "reverse DCF".

| Long-run growth | Implied DPS (Rp) | Implied EPS (Rp) | Implied net profit (Rp tn) | Matching CPO (RM/t) |
|---|---|---|---|---|
| 4% | 171 | 190 | 3.76 | ≈4,400 |
| 3% | 188 | 209 | 4.15 | ≈4,600 |
| 2% | 206 | 229 | 4.54 | ≈4,800 |

Mid-cycle value (3% growth; FY25 base at an assumed RM4,350; 25% of costs move with CPO — corrected in Phase II; 22% tax) [EST]:

| Mid-cycle CPO (RM/t) | Net profit (Rp tn) | Value at 12% CoE (Rp) | Value at 13.75% (Rp) |
|---|---|---|---|
| 3,600 | 2.02 | 1,016 | 851 |
| 3,900 | 2.66 | 1,342 | 1,124 |
| 4,200 | 3.31 | 1,668 | 1,397 |

Adding ≈Rp150/share for above-normal 2026–28 profits gives a fair value of about Rp1,250–1,800 on a RM3,900–4,200 mid-cycle. The "margin of safety" entry is below about Rp1,400 [EST].

### 5.9 Phase I peer snapshot (dates differ by name)

[MKT, stockanalysis.com except where noted]

| Ticker | Price (date) | Mkt cap (Rp tn) | P/E | P/B | EV/EBITDA | ROIC | Net cash / (debt) Rp tn | Div. yield | Note |
|---|---|---|---|---|---|---|---|---|---|
| LSIP | 1,560 (20 Nov) | 10.64 | 4.5x | 0.70x | 0.75x | 32.0% | 8.52 (aggregator; corrected in Phase II) | 5.3% | Cash retained |
| TAPG | 1,750 (19 Nov) | 34.74 | 7.7x | 2.97x | 5.6x (5 Nov) | 35.0% | 1.63 (corrected in Phase II) | 7.4% | Fully valued |
| AALI | 8,400 (3 Sep); 9,900 (13 Nov) | 16.12 at 8,400 | 8.6x | 0.66x | 2.9x | 9.5% | 5.15 | 5.5% | 9M26 +78% |
| DSNG | 1,685 (8 Sep) | 17.60 | 9.1x | 1.45x | 5.0x | 13.7% | (2.76) | 2.9% | FFB −4.3% |
| SSMS | 1,180 (18 Sep) | 11.24 | 8.2x | 3.88x | 6.2x | 18.5% | (9.11) | 7.1% | D/E 3.4x; exports |
| SMAR | 6,575 (1 Sep) | 18.02 | 4.4x | 0.75x | 4.6x | 11.6% | (16.31) | 4.6% | 7.6% free float |
| TBLA | 590 (1 Oct) | 3.54 | 4.0x | 0.37x | 6.3x | 7.7% | (18.59) | 8.0% | D/E 2.0x |

### 5.10 Revised thesis and variant perception (Phase I)

- **Revised thesis:** TAPG is a domestic-only, net-cash (corrected in Phase II), ≈90%-payout grower with earnings near the top of the cycle. Its value turns on three things: mid-cycle CPO after a ≈25% state take; whether the 2027 El Niño costs more in volume than it adds in price; and the 2027 blend and how it is funded.
- **Strongest variant perception [HYP, test by 30 Jun 2027]:** consensus treats biodiesel as a demand floor that protects upstream margins. Through mid-2027, the policy mix instead moves value from growers to the state and to biodiesel makers, and 2027 consensus earnings are still too high.
  - **Confirmed if:** the levy stays at or above 12.5%; the KPBN discount is wider than its 2026 average; TAPG's 1H27 FFB is down y/y; FY27 consensus is cut.
  - **Disproved if:** B50 2027 is confirmed with no levy rise and Brent stays above USD 85; domestic prices track Bursa Malaysia; TAPG delivers 6%+ FFB growth.
- **Valuation method changes adopted:**
  - Build revenue bottom-up: mature ha by age × yield curve × OER × domestic price, where domestic price = (world − duty − levy − DSI fee) × USD/IDR.
  - Value the JV separately.
  - Set the terminal value at mid-cycle, with steady-state replanting at 1/25 of planted area a year, and fade ROIC to replacement cost.
  - Weight scenarios explicitly: CPO RM3,600/3,900/4,200/4,800; levy 12.5%/15%; blend B40/B50/B60; 2027 volume −10%/−5%/+5%.
  - Rebuild the discount rate from the 7.75% SBN. TAPG's 5-year beta of 0.12 is unusable.
  - Extend the forecast to FY2035.

---

## 6. Phase II — TAPG vs LSIP comparative review

**Valuation date for both:** 19 Nov 2026 close. TAPG Rp1,750 (Ajaib). LSIP Rp1,550, derived from its 20 Nov close of Rp1,560 (+0.6%, Sectors) and cross-checked with Stockbro (Rp1,555, +5).

**Recommendation:** initiate TAPG (it is measurable from filings and consensus is crowded long); put LSIP on the watch list. Neither is a BUY.

### 6.1 Primary source register (opened and read)

| Document | Period | Figures extracted (Rp million unless stated) [V-P] |
|---|---|---|
| TAPG interim FS, 30 Sep 2026 | 9M26 | Cash 1,937,038; bank loans 176,000 + 83,000 + 705,500; JV investment 2,697,108; equity attributable 11,716,496; total equity 12,228,199; revenue 9,446,621; op. profit 3,388,407; JV & associate share 918,878; PBT 4,382,744; NP to parent 3,505,620; OCF 2,947,167; capex 522,242; JV dividends received 900,000; dividends paid 2,997,734 |
| TAPG audited FS FY2025 (KAP Purwanto, Susanti dan Surja) | FY25 | Cash 1,651,433; bank loans 1,099,410; JV 2,640,217; JV share 1,066,889; JV dividends 958,807; revenue 11,402,198; op. profit 3,543,254; PBT 4,661,321; tax 815,974; NP 3,702,266; NCI 143,081; OCF 3,431,453; capex 622,694; dividends paid 3,275,669; USTP 50% |
| TAPG audited FS FY2024 | FY23–24 | FY23 revenue 8,325,887; op. profit 1,372,731; JV share 643,293; NP 1,608,217; OCF 1,569,363; capex 802,438; JV dividends 300,000. Key audit matter: impairment of mature bearer plants (Rp554,296) |
| TAPG Annual Report 2025, p. 12 | 2023–25 | Planted 159.7k ha incl. plasma and associates; nucleus FFB 3,040kt; plasma 384kt; processed 4,089kt; CPO 953kt; yield 24.3 t/ha; OER 23.3%; 19,852,540,000 shares |
| LSIP interim FS, 30 Jun 2026 | 1H26 | Cash 8,371,777 (Bank Ina Perdana 1,475,058); dividend payable 566,057; associates 1,260,924; equity 14,318,210; no borrowings; revenue 2,689,745; op. profit 918,058; finance income 143,159; NP 890,988; OCF 849,221; capex 162,704 |
| LSIP audited FS FY2025 | FY25 | Cash 7,597,470 (related party 1,639,556); associates 1,259,611 (share of loss 5,691); employee benefits 516,543 + 159,214; finance income 276,021; NP 1,887,756; OCF 3,015,733; dividends paid 443,234 |
| LSIP Annual Report 2025 | FY25 | 12 mills, 2.7 Mt FFB a year; ≈63% of sales to SIMP; SIMP holds 59.51%; DPS Rp65 (2025), Rp39 (2024); open capex commitments Rp71.8bn |
| LSIP five-year data (AR 2025) | 2021–25 | Nucleus FFB 1,139kt; CPO 292kt; mature 84,744 ha; immature 6,054 ha |
| LSIP FY2025 highlights | FY25 | External FFB 204kt (+19%); OER 21.9% |

Secondary sources used: KB Valbury TAPG initiation (7 May 2026) for age, mills, fertiliser and external-FFB cost; press coverage of LSIP's 9M26 results. Not retrieved: LSIP 30 Sep 2026 FS; TAPG FY2021–22 audited FS; TAPG Note 35 and LSIP Note 27 (related parties).

### 6.2 Operational benchmarking

| Metric (FY2025) | TAPG | LSIP |
|---|---|---|
| Oil palm planted | 159.7k ha (nucleus 132.8k, plasma 26.9k, incl. associates) [V-P] | Nucleus 90,798 ha (mature 84,744; immature 6,054) [V-P] |
| Age profile | Prime age 81.9%; average 14.6 years (1Q26) [V-S] | Not disclosed; immature 6.7% vs ≈12% for a 25-year cycle [EST] |
| FFB yield | 24.3 t/ha (group incl. associates) [V-P] | 13.4 t/ha nucleus (1,139kt ÷ 84,843 ha average mature) [EST] |
| OER | 23.3% (1Q26 24.1%) [V-P] | 21.9% [V-P] |
| Nucleus FFB | 3,040kt (+3%) | 1,139kt (−3%; −5% since 2021) |
| Bought-in FFB | ≈664kt, 16% of processed [EST] | 204kt, 15% of processed [V-P] |
| Bought-in FFB cost | Rp2,993bn = 43% of cost of sales [V-S, KB Valbury] | Not disclosed; assumed ≈Rp650bn [EST] |
| CPO | 953kt | 292kt |
| Mills | 18, ≈1,000 t/hour; 30–45 t/hour mill under construction [V-S] | 12, 2.7 Mt FFB a year [V-P] |
| Mill utilisation | ≈68% (assumes 20 h × 300 days) [EST] | ≈50% (1.34 ÷ 2.7 Mt) [EST] |
| Fertiliser | Rp754bn (−4.2%); FY26 ≈Rp792bn [V-S] | Not disclosed |
| Capex | Rp623bn; FY26 budget Rp923bn | Rp433bn |
| Replanting | ≈3,500 ha planned FY26 [V-S] | No plan disclosed |
| Related-party sales | Not found | ≈63% to SIMP (stated as arm's length) [V-P] |

### 6.3 Financial quality

TAPG (Rp bn) [V-P; ROIC and ratios EST]:

| Period | Revenue | Op. profit | Op. margin | JV share | NP | FCF (OCF − capex) | JV dividends | (FCF + JV div) ÷ NP | Dividend ÷ NP | Op. ROIC ex cash, ex JV | ROE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 9M2026 | 9,447 | 3,388 | 35.9% | 919 | 3,506 | 2,425 | 900 | 95% | — | — | — |
| FY2025 | 11,402 | 3,543 | 31.1% | 1,067 | 3,702 | 2,809 | 959 | 102% | 96.5% | 33.0% | 33.6% |
| FY2024 | 9,671 | 3,045 | 31.5% | 894 | 3,120 | 2,652 | 1,170 | 122% | 96.7% | 30.4% | 28.8% |
| FY2023 | 8,326 | 1,373 | 16.5% | 643 | 1,608 | 767 | 300 | 66% | 112% | 14.6% | — |

LSIP (Rp bn) [V-P; ratios EST]:

| Period | Revenue | Op. profit | Op. margin | Finance income | NP | FCF | FCF ÷ NP | Dividend ÷ prior-year NP | Op. ROIC ex cash, ex assoc. | ROE | Cash |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1H2026 | 2,690 | 918 | 34.1% | 143 | 891 | 687 | 77% | 30.0% (Rp83) | — | — | 8,372 |
| FY2025 | 5,512 | 2,008 | 36.4% | 276 | 1,888 | 2,582 | 137% (≈104% ex one-offs) | 30.0% (Rp65) | 28.5% | 14.2% | 7,597 |
| FY2024 | 4,563 | 1,551 | 34.0% | 217 | 1,477 | 1,189 | 81% | 34.9% (Rp39) | 20.7% | 12.3% | 5,454 |
| FY2023 | 4,190 | 759 | 18.1% | n/a | 762 | n/a | — | — | — | 6.8% | n/a |

- **ROIC method:** operating profit × (1 − tax) ÷ (equity + bank debt − cash − JV/associate investment). TAPG tax 22.7% = tax ÷ (PBT − JV share); LSIP uses the 22% statutory rate.
- **TAPG JV converts to cash** [V-P/EST]: FY2023–25 share of profit Rp2,604bn vs dividends received Rp2,429bn = **93%**. The JV investment fell from Rp3,215bn to Rp2,640bn, so it is being harvested.
- **LSIP FY25 FCF was flattered** by about Rp611bn of related-party working-capital release. After-tax interest of about Rp221bn is ≈12% of profit [EST]. Deposits earn 3.15–5.75% pre-tax [V-P].
- **LSIP 9M26:** net profit about Rp1.7tn, +40% [V-S, press]; FY2021–22 net profit Rp992bn and Rp1,036bn.
- **Capital allocation:**
  - TAPG paid dividends of Rp9.59tn in 2024–9M26 against Rp10.33tn of profit. Its ATP Bio biocoke venture lost Rp25bn in 9M25. An affiliate disclosure was filed on 29 Jul 2026 (not read).
  - LSIP paid out 30–35% and kept Rp1.26tn in four Salim associates [V-P]: Asian Assets Management (Singapore, 25%) Rp757bn; PT Aston Inti Makmur (office building, 25%) Rp364bn; two timber companies Rp139bn. Together they lost Rp5.7bn in 2025.
  - LSIP held Rp1.48tn (17.6% of cash) at PT Bank Ina Perdana (common control). A 2024 land sale to ICBP was refunded in July 2025.

### 6.4 LSIP cash: total vs distributable (Rp bn)

| Step | Amount | Basis |
|---|---|---|
| Cash, 30 Jun 2026 | 8,372 | [V-P] Rp6,520bn in time deposits at third-party banks; Rp1,851bn in current accounts; no borrowings |
| − FY2025 dividend payable | (566) | [V-P] |
| − Operating buffer | (765) | [EST] 3 months of cash costs = (sales 5,512 − EBITDA 2,452) ÷ 4 |
| − Employee obligations (debt-like) | (676) | [V-P] 517 + 159 |
| **= Excess cash** | **6,365 (Rp933/share)** | 60% of the Rp1,550 price |
| − Replanting catch-up | (1,053) | [EST] PV of Rp200bn a year for 10 years at 13.75% (≈1,600 ha a year at ≈Rp120m/ha) |
| **= Conservative excess** | **5,312 (Rp779/share)** | 50% of price |

About Rp1.8tn of deposits are in USD (mainly Bank Mega) [V-P]. Cash at 30 Sep 2026 was probably near Rp8.5tn [EST, not verified].

### 6.5 Commodity and policy transmission

How much of a world-price move growers keep [V-S data; share EST]:

| Month (2026) | HR (USD/t) | Duty | Levy (12.5%) | Total take | Share of the change taken by the state |
|---|---|---|---|---|---|
| November | 978.90 | 124 | 122.36 | 246.36 | 97.9% of the −USD 63.25 move |
| October | 1,042.15 | 178 | 130.27 | 308.27 | 99.1% of the +USD 34.64 move |
| September | 1,007.51 | 148 | 125.94 | 273.94 | — |

- November HR window (20 Sep–19 Oct 2026): Bursa CPO Indonesia USD 869.07, Bursa Malaysia USD 1,088.73, Rotterdam USD 1,443.90. Indonesian growers realised about **80%** of the Malaysian price [V-S].
- The duty moves in steps under PMK 38/2024 (as amended by PMK 68/2025); the levy under PMK 69/2025 (as amended by PMK 9/2026). The full duty schedule has not been seen (data gap).

Sensitivities (FY2025 base; net profit to parent) [EST]:

| Driver | TAPG | LSIP |
|---|---|---|
| Domestic realised price +10% | +24% (JV moves the same way) | +20% |
| World CPO +USD 50/t | ≈0 in the observed band (≈USD 1/t reaches growers) | Same |
| Levy +2.5 pts (≈−Rp447/kg) | −7% | −6% |
| Rupiah 1% weaker | +2.4% | +2.0%, plus ≈Rp18bn translation gain on Rp1.84tn of USD cash |
| Fertiliser +20% | ≈−Rp117bn after tax (−3%) | Similar per ha (not disclosed) |
| Own FFB −5% (El Niño) | −12% | −10% |

### 6.6 TAPG valuation (19 Nov 2026)

EV reconciliation (Rp bn) [V-P inputs; EST totals]:

| Item | Value |
|---|---|
| Market cap (Rp1,750 × 19,852.54m) | 34,742 |
| + Bank loans (30 Sep 2026) | 965 |
| − Cash (30 Sep 2026) | (1,937) |
| + Rp70 interim (ex 11 Nov, paid 27 Nov) | 1,390 |
| + NCI at book | 512 |
| = EV including JV | 35,671 |
| − JV at book | (2,697) |
| = EV of consolidated operations | 32,974 |

Net cash at 30 Sep 2026 was Rp973bn → **pro forma net debt Rp417bn** after the Rp70 interim.

Results by method (Rp/share; price index vs FY2025 realised; cost of equity 12.5–13.75%) [EST]:

| Method | Bear 0.8 | Base 0.9 (mid-cycle) | FY25 level 1.0 |
|---|---|---|---|
| Normalised FCFF + SOTP | 735–834 | 1,076–1,221 | 1,418–1,607 |
| DDM (90% payout) | 812–919 | 1,179–1,334 | 1,545–1,749 |
| Justified P/B (on Rp590 BVPS) | 737–834 (ROE 16.4%, 1.25–1.41x) | 1,145–1,296 (ROE 23.9%, 1.94–2.20x) | 1,552–1,757 (ROE 31.3%, 2.63–2.98x) |

- **SOTP at base** (0.9, 13.75%): operations 783 + JV 355 − net debt 21 − NCI 40 = **Rp1,076/share**. The JV is about one-third of equity value; at book (Rp136/share) it would be undervalued by more than half.
- **Reverse valuation of Rp1,750:**
  - Reverse DDM: Rp3.67tn (DPS Rp166) at 12.5% CoE; Rp4.15tn (DPS Rp188) at 13.75%.
  - Reverse FCFF + SOTP: a price index of 1.04 (profit Rp3.99tn) at 12.5%; 1.10 (Rp4.51tn) at 13.75%.
  - Trailing 12-month profit to Sep 2026 is Rp4.53tn.
- **P/B:** 2.97x is justified at normalised ROE of ≈31% (12.5% CoE) or ≈35% (13.75%). At mid-cycle ROE of ≈24%, justified P/B is 1.9–2.2x.
- **Elasticity:** +10% realised price ≈ +23.7% net profit.

### 6.7 LSIP valuation (19 Nov 2026)

EV reconciliation (Rp bn):

| Item | Value |
|---|---|
| Market cap (Rp1,550 × 6,819.96m) | 10,571 |
| − Cash (30 Jun 2026) | (8,372) |
| + Dividend payable | 566 |
| − Associates at book | (1,261) |
| + Employee obligations | 676 |
| = EV of the plantation business | **2,180** |

- **Multiples** [EST]: EV per mature ha Rp25.7m (≈USD 1,400); EV per nucleus planted ha Rp24.0m, against TAPG's ≈Rp269m (11x higher for ≈1.8x the yield); EV/EBITDA 0.9x; EV/NOPAT 1.4x.

Results by method (Rp/share; 2% growth) [EST]:

| Method | Bear 0.8 | Base 0.9 | FY25 1.0 |
|---|---|---|---|
| Operating FCFF DCF (less Rp1,053bn replanting catch-up) | 653–749 | 1,031–1,172 | 1,409–1,596 |
| Adjusted NAV (DCF + cash at face + associates at 50% − employee obligations) | 1,791–1,887 | 2,169–2,310 | 2,547–2,734 |
| Cash retained forever (cash at 0.2x) | 965–1,061 | 1,343–1,484 | 1,721–1,908 |

- **Reverse:** with cash at face, the market values the operations at Rp2.81tn (1.8x FY25 NOPAT). With operations at mid-cycle DCF, it values excess cash at **0.26–0.40 rupiah per rupiah**.

LSIP cash scenarios [EST weights]:

| Scenario | Status | Value per Rp of excess cash | Rp/share | Weight |
|---|---|---|---|---|
| Retained indefinitely | Current practice | 0.10–0.26 (0.2 used) | 1,343–1,484 | 55% |
| Deployed into lower-return or related-party assets | Precedent exists | ≈0.4 | 1,550–1,691 | 20% |
| Reinvested in replanting | [SPEC] no plan | ≈0.8 | 1,963–2,104 | 10% |
| Special dividend | [SPEC] not announced | ≈0.95 | 2,117–2,259 | 10% |
| Buyback | [SPEC] not announced | ≥1.0 | ≥2,169–2,310 | 5% |
| **Probability-weighted** | | **≈0.42** | **≈1,560–1,710** | |

- **Multiplier maths:** retained at 3.6% after tax with 30% of interest paid out → 0.3 × 3.6% ÷ (13.75% − 0.7 × 3.6%) ≈ 0.10. Full payout of interest → 3.6% ÷ 13.75% ≈ 0.26. Each 0.1 of multiplier ≈ Rp103/share.
- **Watch triggers:** a payout above 50% at the June 2027 AGM; a buyback or special dividend; a disclosed replanting plan with capex guidance; cash moved out of Bank Ina, or associates sold with the cash returned.
- **Trap confirmed if:** more cash goes into associates; payout stays at 30% while cash passes Rp9tn; nucleus FFB keeps falling.
- **Bear cases:** LSIP Rp965–1,061 (−32% to −38%); TAPG Rp735–834 (−52% to −58%).
- **Broker view:** Phillip Sekuritas Rp1,900 on 4.9x 2026 P/E [V-S].

---

## 7. Phase III — Sector-wide alpha discovery

**Prices:** 20 Nov 2026 closes unless noted. **Run-rate profit** = 9M26 attributable net profit × 4/3 [EST; ignores Q4 seasonality]. **Cost of equity** 13.75%; zero growth → steady-state P/E ≈ 7.3x.

### 7.1 Structural shifts: consensus vs second-order effects

| Consensus narrative | Evidence | Second-order effect | Favours / hurts |
|---|---|---|---|
| B50 tightens supply → CPO up → planters win | B50 in force; 13.84m of 16.75m kL delivered; 2027 under review; BPDP 2027 need USD 0.7–2.6bn [V-S] | Price gains go to the state; weak oil → higher levy or softer mandate [HYP] | Hurts price-beta stories |
| El Niño → higher prices → bullish | GAPKI 2027 output 51.73 Mt (−2 Mt); S&P −4.4 Mt; low cycle Feb–Nov 2027, worst in Central Kalimantan; smallholders deferring fertiliser; NOAA 63% chance of a very strong event Nov 26–Jan 27 [V-S] | A volume shock for Indonesian growers; 2027 smallholder FFB scarcity squeezes mills that buy in fruit (TAPG: 43% of COGS) [HYP] | Hurts Kalimantan-heavy estates (SSMS, AALI, BWPT, TAPG); relatively favours Sumatra-weighted (LSIP, much of SIMP) |
| DSI will crush margins | Fee single-digit USD/t, due Dec 2026; USD 5/t ≈ Rp91k/t [V-S/EST] | The fee is small; the wider domestic discount (80% of Bursa) is the real risk; a fee ≤ USD 5/t is a relief event [HYP] | Exporters (AALI; SSMS 900kt) most exposed |
| Forest enforcement is a one-off | AALI paid Rp571bn (Dec 2025); Salim group Rp2.34tn in escrow; NSSS provision Rp108bn; AGO cites Rp142tn of potential fines (palm + mining); Agrinas ≈1.7m ha (774k planted) [V-S] | Escrow creates binary outcomes; indebted parents pull cash from listed subsidiaries; Agrinas may sell FFB to mills with spare capacity [HYP] | Binary for SIMP; payout pressure on LSIP and AALI |
| Index exclusion = weak fundamentals | 383 HSC stocks removed from IHSG; MSCI cut 4 planters [V-S] | Mechanical selling unrelated to earnings [HYP] | SSMS; AALI, TAPG, DSNG |
| Parents are passive | Astra net cash ex-FS fell from Rp7.2tn to Rp1.8tn after a Rp10tn buyback; AALI Rp400bn buyback to 28 Dec; 60% payout; SIMP Rp9.2tn bank loans (Dec 2025) [V-S/V-P] | Higher subsidiary payouts more likely, but also more related-party risk [HYP] | Supports AALI; two-sided for LSIP minorities; favourable for SIMP |
| Weak rupiah is a tailwind | ≈Rp18,150/USD; duty and levy set in USD [V-S] | Lifts IDR revenue but also fertiliser cost and USD debt; INDF and ICBP booked FX losses in 9M26 [V-S] | Net-cash growers with IDR costs |

### 7.2 Leading-indicator dashboard (latest readings)

| Indicator | Latest reading | Read |
|---|---|---|
| HR / duty / levy (monthly) | Nov: HR USD 978.90, duty 124, levy 122.36; Oct HR 1,042.15, duty 178 [V-S] | HR −6% m/m; Dec HR due ≈1 Dec |
| Indonesia vs Bursa Malaysia | USD 869 vs 1,089 (80%) [V-S] | Key series under DSI |
| GAPKI supply and demand | Jan–Sep exports 27.29 Mt; domestic use 19.80 Mt (+7.3%); Sep stocks 2.01 Mt (Jun 2.84; Aug 2.21) [V-S] | Tightening |
| ENSO | NOAA 63% very strong Nov 26–Jan 27; BMKG El Niño to early 2027 [V-S] | Negative for 2027 volumes |
| Biodiesel | 13.84m kL to Nov (83% of 16.75m kL) [V-S] | B50 2027 decision mid-Dec |
| DSI fee | Due Dec 2026 [V-S] | Binary |
| Company production | DSNG 9M FFB −4.3% y/y, Q3 −5.7% q/q (fires cited); SIMP 9M nucleus FFB 2.0 Mt (+4%), CPO 580kt (+13%); BWPT 1H FFB 510kt [V-S] | Diverging by geography |
| Fines and escrow | AALI Rp571bn; Salim Rp2.34tn escrow; NSSS Rp108bn [V-S] | Further notices possible |
| Insider / large-holder trades | Lo Kheng Hong 796.6m SIMP shares (≈5.1%), bought 19.9m at Rp600 (May); JARR CFO bought at Rp3,310; JARR controller pledged shares to Mandiri [V-S] | Constructive for SIMP; red flag for JARR |
| Index plumbing | SSMS HSC from 13 Oct; HSC exclusion to 29 Jan 2027; next MSCI announcement 9 Feb 2027 [V-S] | Forced selling largely done |
| Consensus revisions | Not available; scattered targets only (TAPG Rp2,500 KB Valbury; TBLA Rp960 Ciptadana; AALI Rp8,000 Phintraco, Dec 2025) | **Gap** |

### 7.3 Market-implied expectations [EST from MKT prices and V-S/V-P earnings]

"Implied %" = P/E ÷ 7.27: the share of run-rate profit that the price can sustain forever at 13.75% and zero growth. Justified P/B = (ROE − 2%) ÷ (13.75% − 2%).

| Ticker | Price | Mkt cap (Rp tn) | Run-rate NP (Rp tn) | P/E | Implied % | P/B | ROE | Justified P/B |
|---|---|---|---|---|---|---|---|---|
| AALI | 9,750 | 18.77 | 2.55 | 7.4x | 101% | 0.75x | 10.2% | 0.70x |
| TAPG | ≈1,715 | 34.05 | 4.67 | 7.3x | 100% | — | — | — |
| DSNG | ≈1,280 | 13.57 | 1.95 | 7.0x | 96% | 1.12x | 16.0% | 1.20x |
| BWPT | 96 (Oct) | 2.99 | 0.42 (1H × 2) | 7.1x | 97% | — | — | — |
| TBLA | ≈600 | 3.62 | 0.86 (1H × 2) | 4.2x | 58% | — | — | — |
| SSMS | 920 | 8.76 | 2.12 | 4.1x | 57% | 2.43x | 58.7% (leverage) | n/m |
| SIMP | ≈560 | 8.68 | 2.73 | 3.2x | **44%** | 0.42x | 13.4% | 0.97x |
| LSIP | 1,560 | 10.64 | — | — | — | — | — | Phase II: cash valued at 0.26–0.40 |
| JARR | ≈2,300 (Oct) | 21.23 | 0.47 | 45.6x | 627% | 9.65x | 21.2% | 1.63x |

Earnings inputs for the table above:
- AALI 9M26 NP Rp1.91tn (+78%); equity ≈Rp25.0tn (assets Rp30.18tn − liabilities Rp5.18tn) [V-S].
- TAPG 9M26 NP Rp3.506tn [V-P].
- DSNG 9M26 NP Rp1.46tn (+9.8%); equity Rp12.13tn (Jun 2026); ≈10.6bn shares [V-S].
- SSMS 9M26 NP Rp1.59tn (+58%); revenue Rp14.83tn (+35%); op. profit Rp2.76tn (+43%); liabilities Rp15.10tn; equity Rp3.61tn; cash Rp0.904tn; 9.525bn shares [V-S].
- SIMP 9M26 NP Rp2.05tn (+45%); op. profit Rp3.86tn (+40%); EPS Rp132; 15.5bn shares [V-S]. Dec 2025 parent equity Rp20.44tn; NCI Rp6.15tn [V-P].
- BWPT 1H26 NP Rp211bn (+22.9%); FY25 Rp379bn; 31.12bn shares [V-S].
- TBLA 1H26 NP Rp430bn (−3.7%); FY25 Rp900bn; 6.03bn shares [V-S].
- JARR 9M26 NP Rp349bn (+56%); equity Rp2.20tn; 9.23bn shares [V-S].

**No public consensus or revision data was available.** The reverse valuation above is the proxy for market expectations and must be cross-checked against Bloomberg or FactSet.

### 7.4 Finalist summaries (opportunity cards)

**1. SIMP — Salim Ivomas Pratama** (weighted score 3.50)
- **Narrative:** a low-float Salim holdco with forestry and export-probe overhangs; LSIP is seen as the "clean" vehicle.
- **Variant [HYP]:** SIMP is the cheaper, more option-rich way to own LSIP's cash. It gets 59.5% of any LSIP payout, and it also benefits if LSIP's cash is used inside the group, which hurts LSIP minorities.
- **Stub maths [EST]:** LSIP stake = 0.5951 × Rp10.64tn = **Rp6.33tn** of SIMP's Rp8.68tn market cap. So the rest of SIMP is implied at **Rp2.35tn equity**. Net debt outside LSIP is ≈Rp8.93tn: bank loans Rp9.20tn − cash outside LSIP ≈Rp0.75tn (8.347 − 7.597) + Rp0.475tn due to shareholders and related parties, at Dec 2025. That gives an implied stub EV of ≈Rp11.3tn. Estimated stub run-rate profit is ≈Rp1.67tn (LSIP 9M profit assumed at 1H × 1.5), so the stub trades at ≈1.4x earnings. Consolidated EV/EBIT ≈2.5x.
- **Evidence:**
  - Dec 2025 cash Rp8.347tn, of which Rp1.898tn is related-party [V-P]; Sep 2026 cash Rp9.29tn; total equity Rp28.77tn; liabilities Rp14.98tn [V-S].
- **Catalysts:**
  - Escrow resolution of the Rp2.34tn forestry charge (paid 30 Dec 2025; disclosed via IndoAgri on SGX 23 Feb 2026) [SPEC, no timeline].
  - LSIP AGM, June 2027.
  - FY26 results, Feb–Mar 2027.
  - An IndoAgri capital action [SPEC].
- **Impact [EST]:**
  - 2027 profit range Rp2.2–2.9tn.
  - Each +10pp of LSIP payout ≈ +Rp113bn of cash to SIMP.
  - Each Rp100bn of escrow recovered ≈ Rp6.5/share.
  - The escrow equals **27% of market cap**; a full write-off would take P/B to about 0.48x.
- **Downside:** escrow forfeited, more fines, an export-probe penalty; retest of the 52-week low of Rp456–470 (−16% to −19%).
- **Invalidation:** further forest charges above Rp2tn; an under-invoicing finding; LSIP cash lent to related parties at low returns; stub operating profit below Rp1tn.
- **Risks noted:** Maybank bankers questioned in an export-transaction probe naming the Salim group (Jun 2026, SIMP said it cannot clarify) [V-S]. Thin liquidity.

**2. AALI — Astra Agro Lestari** (2.95)
- **Variant [HYP]:** Q3 shows a cost reset (Q3 alone Rp0.81tn vs Rp1.10tn for 1H). That puts it at 5.8x P/E on Q3 × 4 and 0.75x book.
- **Supports:** a Rp400bn buyback (2 Oct–28 Dec 2026); 60% payout (FY25 DPS Rp458); replanting doubled to 8,000 ha in 2026; 2027 capex Rp1.3–1.4tn [V-S].
- **Partly recognised:** the share price rose 26.5% in the month to 13 Nov (Rp9,900).
- **Risks:** most exposed to DSI; Q3 may include fair-value gains on produce (forensic item); Kalimantan and Sulawesi El Niño exposure.
- **2027 profit range:** Rp2.0–3.2tn [EST].
- **Invalidation:** Q4 profit below Rp0.55tn; DSI fee above USD 10/t.

**3. SSMS — Sawit Sumbermas Sarana** (2.85)
- **Variant [HYP]:** HSC and MSCI-driven selling took the price from Rp1,575 (17 Nov 2025) to Rp920 while profit rose 58%. That is 4.1x run-rate with a 9.1% trailing yield (FY25 DPS Rp83.99).
- **Against:**
  - Liabilities 4.2x equity.
  - Bought SML from parent CBI for Rp1.6tn (24 Nov 2025), backed by a Rp5.2tn BRI-led syndicated loan (18 Nov 2025) [V-S].
  - Assets rose by Rp5.12tn in 9M26 (unexplained).
  - Exports of 900kt (9M; target ≈1 Mt).
  - Central Kalimantan estates.
- **2027 profit range:** Rp1.4–2.3tn. Bear value ≈Rp590 (4x bear profit) [EST].
- **Invalidation:** net debt/EBITDA above 3x; another CBI deal; a dividend cut.

**4. BWPT — Eagle High Plantations** (2.75)
- **Facts** [V-S]:
  - Quasi-reorganisation approved at the 29 Jun 2026 EGM, eliminating a Rp3.71tn deficit.
  - Sukuk fully repaid.
  - Management plans an interim dividend [guidance].
  - 402.9m treasury shares to be resold.
- **FELDA dispute** [V-S]:
  - FICP holds 11.66bn shares (37%), bought in Dec 2016 for USD 505.4m (≈Rp580/share), with a put option at cost + 6% a year.
  - SIAC (June 2024) ordered Rajawali to buy the stake back. A Jakarta court ruled the award non-executable; it is now at kasasi (Supreme Court) and has been raised between governments.
  - The stock fell 10.28% to Rp96 on 26 Aug 2026.
- **Bear case:** FICP sells into a thin market.

**5. LSIP** (2.80 by score; listed 5th because it carries over from Phase II): see [§6](#6-phase-ii--tapg-vs-lsip-comparative-review). New link [HYP]: SIMP's cash needs raise the odds that LSIP cash moves up the group, either as dividends (good for minorities) or related-party use (bad).

### 7.5 Ranking (weights: mispricing 30%, surprise 25%, catalyst 20%, downside 15%, data quality 10%)

| Rank | Ticker | Mispricing | Surprise | Catalyst | Downside | Data | Weighted |
|---|---|---|---|---|---|---|---|
| 1 | SIMP | 5 | 3 | 3 | 3 | 2 | **3.50** |
| 2 | AALI | 2 | 3 | 3 | 4 | 4 | **2.95** |
| 3 | SSMS | 3 | 3 | 3 | 2 | 3 | **2.85** |
| 4 | LSIP | 3 | 2 | 2 | 4 | 4 | **2.80** |
| 5 | BWPT | 3 | 3 | 3 | 2 | 2 | **2.75** |
| 6 | DSNG | 2 | 2 | 2 | 3 | 4 | 2.35 |
| 7 | TBLA | 2 | 2 | 3 | 1 | 3 | 2.15 |
| 8 | TAPG | 1 | 2 | 2 | 2 | 5 | 2.00 |
| — | SMAR, JARR, ANJT, SGRO, other HSC | n/a | | | | | Not investable |

**Sensitivity:**
- Downside weighted at 30% (25/20/15/30/10): SIMP 3.40, AALI 3.15, LSIP 3.05, SSMS 2.70.
- Data quality weighted at 30% (25/20/15/10/30): SIMP 3.20, AALI 3.15, LSIP 3.05.
- SIMP's lead rests on its least-verified data.

### 7.6 Phase III conclusion

Take **SIMP, SSMS and AALI** to forensic analysis and bottom-up modelling; keep BWPT and LSIP next. Each forensic job has one question that decides it:
- **SIMP:** is the Rp2.34tn escrow an asset, and what does the business outside LSIP really earn?
- **SSMS:** are the related-party prices fair, and can the debt be serviced through a 2027 volume dip?
- **AALI:** is the Q3 profit level repeatable?

---

## 8. Quantitative research methodology

Source brief: "Indonesian Palm Oil Quantamental Research Engine" (24 Nov 2026). Its governing rules: begin with a data audit and the architecture; do not produce rankings from incomplete or unverified data; robust alpha discovery, not the highest backtest return.

### 8.1 Status (24 Nov 2026)

- **Done:**
  - Data availability audit.
  - Project skeleton.
  - `settings.yaml`, `universe.yaml` and `sources.yaml` (source register with 18 sources).
  - Verified seed CSVs: `policy_events` (17 events), `cpo_reference_price` (7 months), `universe_status` (15 rows: HSC and suspension), `gapki_stocks` (4 months), each with source URLs and publication dates.
  - The DuckDB point-in-time store module with validation.
- **Interrupted:** factor, regression, nowcast, event-study, backtest and dashboard modules; tests.
- **Where the files are (updated 24 Nov, D-005):**
  - In the repository: `quant/config/`, `quant/palmquant/`, `data/seed/` and `tests/test_store.py`.
  - 8 tests pass.
  - A YAML syntax error in `sources.yaml` was found and fixed when the tests were first run.
  - The remaining modules are specified as tasks T-01 to T-17 in `context/CLAUDE_CODE_TASKS.md`.

### 8.2 Data availability audit (24 Nov 2026)

From the cloud workspace, only PyPI was reachable. Every data source failed (HTTP 000/blocked): Yahoo Finance (`AALI.JK`), IDX, KSEI, FRED (Brent), MPOB, GAPKI, BMKG, NASA POWER, Bank Indonesia, Kemendag JDIH and ESDM.

The "saham" MCP connector on the user's computer (S-001) lists 958 tickers (last updated 2026-11-07), but on 24 Nov 2026 it returned **no history** for AALI, BWPT or LSIP. Its suitability for backtests is unproven ([§13](#13-conflicts-and-corrections)).

**Conclusion:** ingestion must run on a machine with internet access, or from vendor or manual CSVs. No price-based factor, regression or backtest output exists yet.

### 8.3 Data design

- **Two clocks for every value:** `obs_date` (the period the value refers to) and `published_at` (when it became public). Rows are append-only; revisions are new vintages. Point-in-time queries use the latest vintage with `published_at ≤ decision time`.
- **Validation rejects:** rows with no `source_id` in the register; null required fields; `published_at` after the study end (2026-11-24); and rows published before the period they describe.
- **Estimated timestamps:** where a publication time is unknown, a conservative OJK deadline lag is used and the row is flagged `published_at_estimated`. Defaults: quarterly unaudited 45 days; reviewed 75; annual audited 100; GAPKI 50; MPOB 12. Flagged rows are excluded from backtests by default.
- **Disclosures after the 16:00 WIB close** are tradeable from the next session.
- **Planned tables:** prices, corporate_actions, fundamentals, series, events, universe_status, ingest_log.
- **Preferred sources:**
  - Prices: IDX trading summary; Yahoo only as a cross-check, because its IDX adjusted closes are unreliable for dividends and rights issues.
  - CPO: Bursa FCPO via a vendor (no free API).
  - USD/IDR: BI JISDOR.
  - Brent: FRED DCOILBRENTEU.
  - Rainfall: NASA POWER (needs estate coordinates) and BMKG.
  - Monthly supply and demand: MPOB and GAPKI releases, stored as vintages.
  - Policy: Kemendag, ESDM and PMK texts.
  - Consensus: vendor only; otherwise labelled proxies.

### 8.4 Module design (fixed ex ante; not tuned to results)

| Module | Design |
|---|---|
| 1 Data pipeline | Adapters (IDX, Yahoo cross-check, FRED, NASA POWER, manual CSV) → validation → DuckDB; ingest log; audit report |
| 2 Factor screening | Cross-sectional percentile ranks, needing at least 5 investable names. Factors: normalised earnings yield, P/B, FCF yield (value); ROE, accruals, net debt/EBITDA (quality); 12-1 relative strength; 12-1 residual momentum; ADV liquidity; earnings-surprise potential. CPO beta is descriptive only. The combined score is an equal-weight of value, quality, momentum and surprise |
| 3 Commodity sensitivity | Weekly returns; 104-week rolling OLS (minimum 78 observations) on CPO, IHSG, USD/IDR and Brent; rolling betas, t-stats, R², residuals; residual momentum over 52 weeks skipping the last 4; stability diagnostics. Test whether abnormal underperformance predicts excess returns or reflects later fundamental deterioration |
| 4 Earnings nowcast | Drivers: mature ha × yield × OER; domestic price = (HR − duty − levy − DSI fee) × USD/IDR; external FFB cost; fertiliser; interest; tax; NCI; JV separately. Expectations: consensus only if genuinely available; otherwise explicitly labelled proxies (same quarter last year, trailing 4Q average, market-implied from reverse valuation) |
| 5 Event studies | Market model with estimation window [−250, −30]; windows [−10, −1], [0, 1], [2, 20]; minimum 120 estimation observations; drop overlapping same-entity events; sector-wide events (mandates, levies) analysed as calendar-time portfolios because all stocks share the event date |
| 6 Backtest | Monthly rebalance; signal at close t, trade at close t+1; costs: buy 0.15%, sell 0.25% (incl. 0.10% sales tax), slippage 20bps + 5bps per 1% of ADV; maximum participation 10% of 20-day ADV; minimum ADV Rp1bn; Rp50bn notional; long-only top tercile; suspended stocks frozen; point-in-time HSC and listing status; total return from corporate actions; walk-forward with 2016–18 as burn-in and annual out-of-sample test folds from 2019. Compare: value, momentum, earnings surprise, combined, equal-weight palm, IHSG |
| 7 Dashboard | Plotly HTML: rankings, factor scores, betas, implied vs fundamental expectations, nowcasts, catalysts, relative performance, backtests, risk, and data-quality warnings. Ranked views stay **LOCKED** until the quality gates pass |

**Quality gates (all must pass before rankings):**
- Price coverage ≥ 90% of trading days per investable ticker.
- At least 6 tickers with prices.
- At least 12 quarters of fundamentals.
- Actual (not estimated) FS publication dates.
- A CPO series and a benchmark loaded.
- Newest price within 7 days of the study end.

**Known statistical limits:**
- About 10–15 investable names gives low cross-sectional power.
- IHSG has a series break, because HSC stocks were excluded from 13 Nov 2026.
- Yahoo IDX adjustments are unreliable.
- No historical consensus data.

---

## 9. Verified facts register

Key facts that later work depends on. For full filing extracts see [§6.1](#61-primary-source-register-opened-and-read).

### 9.1 Policy and regulation

| Fact | Date | Level | Source |
|---|---|---|---|
| 2026 biodiesel allocation 15.65m kL (Kepmen 439.K/EK.01/MEM.E/2025) | 23 Dec 2025 | V-P | ESDM |
| B50 in force from 1 Jul 2026; specification Kepmen 257.K/EK.01/MEM.E/2026; B40 stock usable to 30 Sep 2026 | Jun 2026 | V-S | Bisnis |
| 2026 allocation revised to 16.75m kL; 13.84m kL delivered to Nov | Nov 2026 | V-S | Katadata |
| B50 for 2027 under review; decision expected within about a month | 13 Nov 2026 | V-S | Katadata, IDX Channel |
| B60 in 2027 is a target only | Sep 2026 | V-S | AHK, Katadata |
| Levy 10% → 12.5% of HR | 1 Mar 2026 | V-S | MPOB/OFI |
| Duty and levy: Sep HR 1,007.51 / duty 148 / levy 125.94; Oct 1,042.15 / 178 / 130.27; Nov 978.90 / 124 / 122.36; Dec 2025 926.14 / 74 / 92.61 (levy 10%); May 2026 HR 1,049.58 / duty 178 | Monthly | V-S | DDTCNews, Katadata |
| PP 24/2026 (single-door exports via state firm; sets price and margin) | Signed 20 May 2026; in force 1 Jun 2026 | V-S | DDTCNews, Detik |
| Permendag 16/2026; only DSI ships from 1 Jan 2027; DMO retained | 2026 | V-S | Gulf News/Antara, Fortune IDN |
| DSI fee single-digit USD/t, to be announced Dec 2026 | 13 Nov 2026 | V-S | Katadata |
| PP 45/2025 forest-area administrative fines (≈Rp25m/ha/yr) | 2025 | V-S | Kontan, Republika |
| HSC: 383 stocks out of IHSG 13 Nov 2026–29 Jan 2027 | 11 Nov 2026 | V-S | Bisnis |
| India cut its basic CPO import duty from 10% to 5% from 24 Sep 2026 | Sep 2026 | V-S | RCTI/GAPKI |

### 9.2 Market and industry

| Fact | Date | Level | Source |
|---|---|---|---|
| USDA 2026/27: world palm output 78.92 Mt (−3.18); Indonesia 45.00 Mt | Nov 2026 | V-P | USDA FAS |
| GAPKI: 2026 output 53.73 Mt; 2027 51.73 Mt; 2027 domestic use 30.2 Mt; biodiesel CPO 14.69 → 17.4 Mt | 29 Sep 2026 | V-S | Katadata |
| S&P: Indonesia 2027 output −4.4 Mt | 12 Nov 2026 | V-S | Katadata |
| GAPKI Jan–Sep 2026: exports 27.29 Mt; domestic use 19.80 Mt; Sep stocks 2.01 Mt; average CPO export price USD 1,144/t (Sep USD 1,171) | 19 Nov 2026 | V-S | Bisnis |
| Malaysia stocks record 3.62 Mt | Oct 2026 | V-S | The Star / Bernama |
| BMKG Niño 3.4 +2.63 ("very strong"); NOAA 63% chance of a very strong event, Nov 26–Jan 27 | Sep / Jul 2026 | V-S | Metro TV; Bisnis |
| CPO futures fell to a 25-week low ≈MYR 4,377 (5 Nov); Jan contract MYR 4,447 (13 Nov) | Nov 2026 | V-S | Kontan; IDX Channel |
| Agrinas Palma manages ≈1.7m ha (774k ha planted) | Jan 2026 | V-S | Bisnis |
| 10-year SBN 7.75%; BI rate 6% | Nov 2026 | V-S | IDX Channel |
| MSCI Nov 2026 review: no Indonesian palm changes; next announcement 9 Feb 2027 | 12 Nov 2026 | V-S | Bisnis; Investortrust |

### 9.3 Company

| Fact | Date | Level |
|---|---|---|
| TAPG financials and operations as in §6.1 | FY25, 9M26 | V-P |
| LSIP financials as in §6.1 | FY25, 1H26 | V-P |
| SIMP Dec 2025: cash Rp8,347,100m (related party 1,898,356); short-term bank loans 6,488,042; current long-term 2,334,820; long-term 377,892 (total 9,200,754); parent equity 20,443,837; NCI 6,150,837; liabilities 14,781,711 | FY25 | V-P |
| SIMP group paid Rp2.34tn forestry charges into government escrow (30 Dec 2025); accounting treatment not yet confirmed | SGX 23 Feb 2026 | V-S |
| AALI paid a Rp571bn Satgas PKH fine | Dec 2025 (disclosed 22 Jan 2026) | V-S |
| AALI 9M26 NP Rp1.91tn; EPS Rp989.77; assets Rp30.18tn; liabilities Rp5.18tn; Rp400bn buyback 2 Oct–28 Dec 2026 | Oct 2026 | V-S |
| SSMS 9M26 figures as in §7.3; HSC from 13 Oct 2026 | Nov 2026 | V-S |
| SGRO: AGPA bought 65.72% at Rp7,903 (19 Nov 2025); MTO 21 Jan–19 Feb 2026; renamed PT Prime Agri Resources | 2025–26 | V-S |
| ANJT: First Resources MTO at Rp1,813 completed 3 Oct 2025 (95.92% direct) | 2025 | V-S |
| JARR: suspended 11 Sep 2026; FAME capacity 495kt, no expansion planned; HSC 98.02% | 2026 | V-S |
| TBLA: FAME capacity 765kt/yr (two Lampung plants); FY25 FAME sales ≈771k kL; biodiesel ≈48% of FY25 revenue | 2026 | V-S |
| BWPT: quasi-reorganisation, sukuk repaid, FELDA dispute as in §7.4 | 2026 | V-S |
| DSNG 9M26 NP Rp1.46tn (+9.8%); FFB 1.5 Mt (−4.3%); OER 23.73%; FY25 dividend Rp47/share (Rp498.19bn) | Oct 2026 | V-S |
| NSSS Rp108bn provision for forest-area exposure (1,762 ha + 261 ha) | Jul 2026 | V-S |
| LSIP buyback up to Rp750bn, internal cash, 26 Oct–31 Dec 2026, ≤20% of paid-up capital; INDF and ICBP announced identical programmes the same day | 23 Oct 2026 | V-S |
| DSNG 9M26: revenue Rp9.10tn (+1.8%); palm ≈Rp8tn (88%); CPO 451kt (−1.5%); PK 85kt (−1%); FFA 2.95%; finance costs down on deleveraging | 30 Oct 2026 | V-S |
| DSNG net debt (aggregator): Dec-23 Rp5.19tn; Dec-24 Rp5.18tn; Dec-25 Rp3.51tn; Jun-26 Rp2.76tn | 2026 | MKT |
| TAPG 9M26: revenue Rp9.45tn vs Rp8.21tn; NP Rp3.51tn vs Rp2.68tn; EPS Rp177; OCF Rp2.95tn; cash Rp1.94tn; liabilities Rp3.23tn | 28 Oct 2026 | V-P (FS) / V-S |
| TAPG 1Q26 FFB −6% y/y; CPO −2% | 2026 | V-S |

### 9.4 Macro and climate (added 24 Nov 2026)

| Fact | Date | Level | Source |
|---|---|---|---|
| BI-Rate +25bp to 6.00% (DF 5.25%, LF 6.75%); rupiah Rp18,245/USD on 17 Nov | 18 Nov 2026 | V-P | BI release 28/254/DKom |
| 10-year SBN 7.73% | 18 Nov 2026 | V-S | Kontan (MNC) |
| Fed funds 3.75–4.00% held (10–2); +25bp in Sep 2026 | 28 Oct 2026 | V-S | Ajaib, Metro TV |
| US 10-year Treasury 4.90% | 4 Nov 2026 | V-S | Kontan |
| GDP Q3 2026 5.47% y/y; CPI Oct 3.23% y/y | 5 / 2 Nov 2026 | V-S | BPS via Bisnis |
| Brent USD 92.44 | 16 Nov 2026 | V-S | KabarBursa / Reuters |
| NOAA CPC: El Niño Advisory; Niño-3.4 +2.5 °C; strong-to-very strong >79% through JFM 2027; ≈60% chance of a historic event; weakening expected early 2027 | 12 Nov 2026 | V-P | NOAA CPC |
| PP 24/2026 set and promulgated 20 May 2026, in force 1 Jun 2026 (LN 2026/58), status in force | 2026 | V-P (metadata) | BPK JDIH |
| Kepmen ESDM 257.K/EK.01/MEM.E/2026 (B50) dated 17 Jun 2026 | 2026 | V-S | Detik |

---

## 10. Assumptions used in the analysis

_These should be registered in `context/ASSUMPTIONS.md` before they go into any model. Existing entries there (A-001, A-002) are unchanged._

| Area | Assumption | Value | Basis | Set in |
|---|---|---|---|---|
| Discount rate | Cost of equity | 13.75% (7.75% SBN + 6.0% ERP); flexed to 12.5% | Judgement | Phase I–III |
| Discount rate | Terminal growth | TAPG 3%; LSIP 2%; reverse P/E 0% | Judgement | Phase I–II |
| Mid-cycle | Realised price index vs FY2025 | 0.9 base; 0.8 bear; 1.0 FY25 | FY25 was above average; weak rupiah supports IDR prices | Phase II |
| Mid-cycle | CPO scenarios | RM3,600 / 3,900 / 4,200 / 4,800 | Phase I | Phase I |
| TAPG | Cost structure | External FFB Rp2,993bn moves with price; other costs Rp4,866bn fixed | KB Valbury + audited FS | Phase II (replaced Phase I's 25%-variable) |
| TAPG | Reinvestment | 20% of NOPAT (3% growth at 15% return on new capital) | Judgement | Phase II |
| TAPG | JV payout | 93% (three-year actual) | Audited FS | Phase II |
| TAPG | NCI | 5.15% of consolidated profit ex-JV | Audited FS | Phase II |
| TAPG | Tax | 22.7% effective (ex-JV) | Audited FS | Phase II |
| TAPG | Maintenance capex ≈ depreciation | Not yet checked | Judgement | Phase II |
| LSIP | External FFB cost | ≈Rp650bn (204kt × Rp3,200/kg) | Assumption | Phase II |
| LSIP | Operating buffer | 3 months of cash costs = Rp765bn | Judgement | Phase II |
| LSIP | Replanting catch-up | PV Rp1,053bn (Rp200bn a year for 10 years) | Judgement | Phase II |
| LSIP | Cash multipliers and scenario weights | 0.2 / 0.4 / 0.8 / 0.95 / 1.0; 55/20/10/10/5 | Judgement from payout history | Phase II |
| LSIP | Associates | 50% of book base; 0 in bear | Judgement | Phase II |
| Sector | Run-rate profit | 9M26 × 4/3 (1H × 2 for BWPT, TBLA) | Simplification; ignores seasonality | Phase III |
| Sector | Operating leverage on volume | ≈2–2.5x | Phase II TAPG elasticity | Phase III |
| Sector | El Niño 2027 bear volume | −8% (SIMP, AALI); −10% (SSMS) | Judgement | Phase III |
| SIMP | LSIP 9M26 profit | 1H26 × 1.5 = Rp1.34tn | Simplification | Phase III |
| Policy | DSI fee scenario | USD 5–10/t | DSI guidance "single digit" | Phase III |
| FX | Translation | Rp18,154/USD (LPEM); ≈Rp18,150 spot (Nov) | Press | Phase I/III |
| Quant | Costs, lags, gates, windows | See §8.4 | Fixed ex ante | Quant design |

---

## 11. Hypothesis register

| ID | Hypothesis | Status | Test / confirm | Invalidate |
|---|---|---|---|---|
| H-01 | Through mid-2027 the policy mix moves value from growers to the state and biodiesel makers; FY27 consensus is too high (Phase I variant) | Open | Levy ≥ 12.5%; KPBN discount wider than its 2026 average; TAPG 1H27 FFB down; FY27 consensus cut | B50 2027 confirmed with no levy rise and Brent > USD 85; domestic prices track Bursa; TAPG FFB +6% |
| H-02 | 2027 El Niño costs Indonesian growers more in volume than it adds in price | Open | GAPKI/BPS monthly output down y/y Feb–Nov 2027; company FFB releases | Malaysian stocks > 3 Mt into mid-2027 with prices flat; FFB flat |
| H-03 | 2027 smallholder FFB scarcity squeezes mills that buy in fruit (TAPG) | Open | Provincial FFB prices up relative to CPO; external FFB share and cost | External FFB margins stable |
| H-04 | Duty/levy capture leaves growers ≈1–2% of world-price moves in the current band | Partly verified (two months) | Full PMK 38/2024 schedule; longer monthly series | Pass-through much higher in other bands |
| H-05 | A DSI fee ≤ USD 5/t is a relief event; the domestic discount is the real risk | Open | Fee notice (Dec 2026); KPBN vs Bursa spread in 1Q27 | Fee > USD 10/t or discount narrows |
| H-06 | SIMP is mispriced because of an identifiable, resolvable item (escrow) | Open (top finalist) | Escrow accounting; stub EBIT; export-probe outcome | Escrow forfeited plus further fines > Rp2tn; stub EBIT < Rp1tn |
| H-07 | SIMP owns the LSIP cash "option" in either allocation path | Open | LSIP payout and related-party flows | Cash used in ways that harm SIMP as well (e.g. losses on associates) |
| H-08 | SSMS's discount is mainly forced selling, not fundamentals | Open | Debt schedule; SML appraisal; dividend continuity | Refinancing stress; another CBI deal |
| H-09 | AALI's Q3 margin is a durable cost reset | Open | Q3 bridge; Q4 profit ≥ Rp0.55tn | Q4 profit < Rp0.55tn; fair-value gains explain Q3 |
| H-10 | BWPT's dividend restart plus an off-market FELDA settlement re-rates the equity | Open | Interim dividend declared; kasasi ruling | FICP on-market sale; no dividend by FY26 results |
| H-11 | Parent cash needs (Astra, IndoAgri) raise subsidiary payouts | Open | AALI and LSIP payouts at 2027 AGMs | LSIP payout stays 30% |
| H-12 | LSIP cash re-rates if management distributes | Open (watch) | Phase II triggers (§6.7) | Payout 30% while cash > Rp9tn |
| H-13 | Agrinas becomes a supplier of FFB to mills with spare capacity | Open (speculative) | Agrinas offtake disclosures | — |
| H-14 | Abnormal underperformance predicts excess returns rather than fundamental decline (quant Module 3) | Untested | Needs price data | — |
| H-15 | TAPG mid-cycle net profit ≈Rp2.6tn (Phase I); the market implies a sustainable ROE of 34–38% against FY25 33.6% and a mid-cycle ≈24% | Open (mandate Q-A) | Normalised model (Phase 4); quarterly operations (B-04); JV split (B-05) | Mid-cycle ROE ≥ 30% supported by volume growth at normal prices |
| H-16 | DSNG's lower financing cost can offset 2027 operating pressure | Open; **weak on audit arithmetic**: the remaining deleveraging is worth ≤≈9% of NP, about one 5% FFB decline | 9M26 debt schedule and cost (B-01); 2027 FFB | Finance cost saving > 15% of NP, or FFB flat in 2027 |
| H-17 | LSIP's buyback marks a change in capital allocation that the market is underpricing | Open | IDX execution reports to 31 Dec 2026; treasury shares cancelled rather than resold; June 2027 payout | Little or no execution; treasury shares resold; payout stays 30% |
| H-18 | El Niño 2026–27 produces measurable earnings divergence between TAPG, DSNG and LSIP through estate geography, age and water management | Open (main differentiated angle, mandate §8) | Estate database (B-07); rainfall (T-05/T-06); lag model (T-07); event history (T-08) | No significant difference in historical climate sensitivity between the three |

---

## 12. Rejected and downgraded hypotheses

| Hypothesis | Verdict | Evidence |
|---|---|---|
| The market prices TAPG as a plain cyclical (original variant perception) | **Rejected** (Phase I) | P/B 2.97x vs 0.95–1.55x in FY21–23; reverse DDM capitalises Rp3.7–4.5tn; 9 Buy / 2 Hold |
| B50 creates a structural demand floor that upstream captures | **Downgraded** to partially supported | 2027 blend unset; subsidy funded by a levy on growers; duty absorbs most price gains |
| Supply constraint is structural for 2027 | **Downgraded** to cyclical until 2028 | Record Malaysian stocks; GAPKI 2026 +4%; substitutes +5.9 Mt |
| TAPG has net cash | **Corrected** (Phase II) | Net cash Rp973bn at 30 Sep 2026 → pro forma net debt Rp417bn after the Rp70 interim |
| TAPG ROIC is flattered by the JV | **Corrected** | Excluding the JV and cash, operating ROIC is still 33.0%; the flattering comes from historical-cost bearer plants |
| 25% of TAPG costs move with CPO | **Corrected** | External FFB alone is 43% of COGS; +10% price ≈ +24% profit |
| LSIP cash ≈ 80% of market cap and fully counts | **Corrected** | Excess cash ≈60% (Rp933/share), 50% conservative; 17.6% at a common-control bank |
| LSIP has no export exposure | **Corrected** | ≈63% of sales go to SIMP, a refiner and exporter |
| Rupiah weakness is a clean tailwind | **Downgraded** | It also lifts the discount rate (SBN 6.13% → 7.75%), fertiliser cost and USD debt; clean only for net-cash growers with IDR costs |
| TBLA is the B50 volume play | **Rejected** (Phase III) | FAME capacity 765kt is nearly full (≈680kt sold); 1H26 NP −3.7%; EV ≈5x market cap |
| JARR / SMAR as B50 plays | **Rejected** (not investable) | HSC 98.02% / 99.56%; JARR ≈46x run-rate P/E, suspension, pledged shares |
| An "El Niño price spike" basket of Indonesian planters | **Rejected** | Volume loss plus state capture of price; a poor instrument for a long-CPO view |
| DSNG as value | **Deprioritised** | Fair on P/B (1.12x vs 1.20x justified); FFB falling (fires) |
| ANJT / SGRO as quality plays | **Deprioritised** | HSC; tiny floats; required re-float could add supply |

---

## 13. Conflicts and corrections

| Item | Conflict | Resolution / action |
|---|---|---|
| SSMS 1-year return | The repo universe screen (S-001, weekly sampling) shows **+74%**. Price prints in the research show Rp1,575 (17 Nov 2025, Bisnis) → Rp1,180 (18 Sep 2026) → Rp920 (20 Nov 2026), about **−42%** | **Unresolved.** Check S-001 for a corporate-action or data error before using it. Rebuild from the IDX daily summary |
| S-001 reliability | It listed tickers but returned no history for AALI, BWPT or LSIP on 24 Nov 2026 | Treat S-001 as unverified; do not use it for backtests (consistent with its register note) |
| Universe D-002 | STAA (core), CSRA and PSGO (extended) are on the HSC list (11 Nov 2026) | Propose a D-003 decision: apply point-in-time HSC status as an investability filter |
| Salim forestry charge | Phase I/II cite Rp2.33tn (Bisnis); Phase III cites Rp2.34tn (IndoAgri SGX via Reuters brief) | Use Rp2.34tn (closer to primary); confirm in SGX filing Ref 08645FMJDAAR3NWQ |
| TAPG price | Phase I/II use Rp1,750 (19 Nov); Phase III uses ≈Rp1,715 (20 Nov, derived from the 23 Nov close of Rp1,725, +0.58%) | Both are kept with their dates; re-price on one date before modelling |
| LSIP price | Rp1,550 (19 Nov, derived), Rp1,560 (20 Nov), Rp1,605 (23 Nov, JournalArta) | Same as above |
| Phase I → II corrections | Ten items (reverse DCF → DDM; TAPG net cash; FY25 op. profit Rp3.67tn → Rp3.543tn; JV share; ROIC driver; cost variability; LSIP cash; price dates; LSIP export exposure; levy-only modelling) | Phase II figures supersede Phase I wherever they differ |
| Rupiah level | Rp18,254 (19 Nov, Kontan), ≈Rp18,150–18,160 (early Nov), Rp18,154 (LPEM) | Record the FX used in every model |
| Mixed price dates in Phase III | 20 Nov closes; SIMP and TBLA undated late-Nov quotes; BWPT 15 Oct | Re-price on one close before modelling |
| C-11 to C-19 (Phase 0–1) | Mandate reference figures vs filings and press: DSNG profit lines and growth; DSNG Q3 inventory arithmetic; unsourced DSNG nowcast and "consensus"; TAPG 2026 volume growth vs 1Q26 FFB −6%; LSIP cash (aggregator vs FS); B50 2027 status; NOAA probability; TAPG ROE annualisation; primary coverage vs Phase III finalists | See `research/2026-11-24_phase1_verification_audit.md` §7. All are open except C-16, C-17 (corrected here) and C-19 (D-003) |

---

## 14. Data gaps

**Blocking for TAPG initiation (Phase II priority):**
1. Consolidated vs JV split (USTP hectares, output, accounts; FY25 Note 14a).
2. D&A and capex split (maintenance / replanting / growth).
3. Realised CPO and kernel prices by quarter; the KPBN discount.
4. Mature ha by planting year; cash cost per tonne; fertiliser per ha.
5. Note 35 related parties; the 29 Jul 2026 affiliate disclosure.
6. HGU titles, plasma compliance, forest-area exposure; follow-up on the FY24 impairment flag.
7. FY2021–22 audited statements.
8. **The full PMK 38/2024 duty schedule** (needed by every model).

**Phase III finalists:**
- **SIMP:**
  - 9M26 FS: escrow accounting, debt at Sep 2026, segment EBIT, one-offs (FX, fair value).
  - Related-bank deposits (Rp1.90tn at Dec 2025).
  - Export-probe status.
  - IndoAgri debt maturities.
  - Liquidity (days to build a position).
- **SSMS:**
  - 9M26 debt schedule (currency, maturities, covenants).
  - Composition of the Rp5.12tn asset increase.
  - SML appraisal vs transaction benchmarks.
  - Estate rainfall (Kotawaringin Barat, Seruyan).
  - Dividend restrictions under the loan.
  - KSEI free float.
- **AALI:** Q3 bridge (volume / price / cost / fair value); export share; age profile after replanting; buyback execution.
- **BWPT:** current price, net debt at Sep 2026, age profile, legal timeline.
- **LSIP** (only if a trigger fires): 30 Sep 2026 FS; Note 27; age profile and replanting plan; associates' accounts; withholding tax.

**Cross-cutting:**
- One-date pricing for the whole universe.
- Consensus estimates and revisions (Bloomberg / FactSet).
- December HR and DSI fee.
- B50 2027 Kepmen and allocation.
- GAPKI October data.
- ENSO updates.
- Primary PDFs for GAPKI, BPDP and ministry figures (Phase I relied on press).
- Listed logistics and fertiliser names (not found).
- Listing dates marked "verify" in the quant universe config.

**Quant data:**
- 2016–2026 daily prices, volume and corporate actions (IDX).
- FCPO history (vendor).
- JISDOR; Brent.
- MPOB and GAPKI monthly vintages.
- Estate coordinates for rainfall.
- Point-in-time FS with filing timestamps.
- Biodiesel allocation history.
- Historical consensus (unavailable → proxies).

---

## 15. Catalyst calendar

| When | Event | Status | Affects |
|---|---|---|---|
| ≈1 Dec 2026 | December HR, duty and levy | Scheduled | All growers |
| Dec 2026 | DSI export fee announced | Announced process | Exporters (AALI, SSMS), domestic discount |
| Mid-Dec 2026 | B50 2027 decision; 2027 biodiesel allocation Kepmen (late Dec) | Process announced; outcome unknown | Sector; TBLA |
| 28 Dec 2026 | AALI buyback window ends | Enacted | AALI |
| 1 Jan 2027 | DSI single-door exports take effect | Enacted (PP 24/2026) | Sector |
| 29 Jan 2027 | HSC IHSG exclusion period ends (next evaluation) | Enacted | SSMS and HSC names |
| 9 Feb 2027 | MSCI next review announcement | Scheduled | Index flows |
| Feb–Mar 2027 | FY2026 results (TAPG volume vs 6–10% guidance; fertiliser catch-up; SIMP, SSMS, AALI) | Scheduled | Finalists |
| Monthly ≈10th / ≈6 weeks | MPOB; GAPKI | Scheduled | Supply and demand |
| Feb–Nov 2027 | El Niño low production cycle | Forecast | Volumes |
| Apr–Jun 2027 | AGMs: AALI, SSMS (FY25 DPS Rp83.99), LSIP (payout trigger), SIMP | Scheduled | Payout hypotheses |
| Late 2027–early 2028 | TAPG new 30–45 t/hour mill | Under construction | TAPG |
| By 30 Jun 2027 | Test date for Phase I variant perception (H-01) | — | TAPG / sector |
| No date | SIMP escrow resolution; BWPT kasasi ruling; BWPT interim dividend; LSIP distribution | [SPEC] / guidance | SIMP, BWPT, LSIP |

---

## 16. Next steps

**From 24 Nov 2026 the working list is `context/RESEARCH_BACKLOG.md`** (priority items B-01 to B-09 for Q-A, Q-B and Q-C) **and `context/CLAUDE_CODE_TASKS.md`** (T-01 to T-17). Done since the list below was written:
- D-003 and D-004 are logged.
- The quant skeleton is committed.
- The §10 assumptions are in `context/ASSUMPTIONS.md` (A-003 to A-028).
- The sources are in `data/SOURCE_REGISTER.csv` (S-002 to S-015).

The Phase III items below (SIMP, SSMS and AALI forensic work) are kept for the comparison watchlist.

**Research (Phase III list):**
1. Log D-003 (point-in-time HSC investability filter; review STAA, CSRA, PSGO) in `context/DECISION_LOG.md`, and resolve the SSMS return conflict in the universe screen.
2. **Forensic pass on SIMP:** 9M26 FS (escrow treatment, stub debt and EBIT, one-offs), the IndoAgri SGX filings, and the export-probe status. Stop if the escrow is a write-off risk with no offset.
3. **Forensic pass on SSMS:** debt schedule, the Rp5.12tn asset increase, the SML appraisal, dividend covenants.
4. **Forensic pass on AALI:** Q3 bridge and fair-value check; buyback execution; DSI exposure.
5. **TAPG initiation model:** close the eight blocking gaps (§14), then build FCFF + JV SOTP with the Phase I method changes (§5.10).
6. Monitor the LSIP triggers and BWPT dividend/legal events.
7. Re-price the whole universe on one close; obtain consensus.
8. Move the assumptions in §10 into `context/ASSUMPTIONS.md` and the sources into `data/SOURCE_REGISTER.csv`.

**Quant:**
1. Commit the framework skeleton (configs, source register, seed CSVs, point-in-time store) into `quant/`, `data/` and `tests/`.
2. Finish modules 2–7 and their unit tests: point-in-time filtering, no look-ahead in the backtest, costs, suspensions, event alignment.
3. Run ingestion on a machine with internet access or via vendor/manual CSVs; rerun the audit; keep rankings locked until the gates pass.

---

## 17. Source references

**Research documents (full tables and links):**
- [Phase I — TAPG Thesis Stress-Test](https://claude.ai/artifact/AVP7koSabCSUYHNndFznq9)
- [Phase II — TAPG vs LSIP Comparative Review](https://claude.ai/artifact/1QCMj3DF2KeeQvynGcPUtL)
- [Phase III — Sector Alpha Discovery](https://claude.ai/artifact/9pC6u7RDyMYb67ebr7ZCoK)

**Primary filings and regulators:**
- TAPG FS 30 Sep 2026; FY2025 and FY2024 audited FS; AR 2025 (via IDX filing mirrors: financialfilings.com; Indo Premier `TAPG_Q4_2025.pdf`, `TAPG_Q4_2024.pdf`).
- LSIP: londonsumatra.com DownloadFile/603 (1H26 FS), /579 (FY25 FS), /588 (AR 2025), /590 (five-year data), /580 (FY25 highlights).
- [SIMP FS 31 Dec 2025 (Indo Premier)](https://indopremier.com/xdir/news/LAPORAN%20KEUANGAN/2025/q4/SIMP_Q4_2025.pdf); [IndoAgri AR 2025, borrowings](https://investor.indofoodagri.com/misc/ar2025/136/).
- [ESDM 2026 biodiesel allocation](https://www.esdm.go.id/id/media-center/arsip-berita/pemerintah-tetapkan-alokasi-biodiesel-tahun-2026-sebesar-1565-juta-kl).
- USDA FAS Oilseeds: World Markets and Trade (Nov 2026); USDA ERS Oil Crops Outlook (Oct 2026).
- KB Valbury TAPG initiation (7 May 2026) — broker, secondary.

**Policy, industry and market (secondary):**
- [DDTCNews — Nov 2026 HR, duty, levy](https://news.ddtc.co.id/data-alat/pungutan-komoditas/1823759/harga-referensi-turun-tarif-bea-keluar-cpo-november-jadi-us124mt)
- [Katadata — B50 2027 review and BPDP need](https://katadata.co.id/berita/energi/6af672fb051a7/pemerintah-kaji-ulang-b50-ekspor-sawit-dan-beban-subsidi-jadi-taruhan)
- [Katadata — GAPKI 2027 outlook](https://katadata.co.id/berita/industri/6abb501a16c63/gapki-proyeksi-pasokan-cpo-2027-tertekan-el-nino-ekspor-turun-5-juta-ton)
- [Katadata — S&P 2027 forecast](https://katadata.co.id/berita/industri/6af56c2dac002/sp-ramal-produksi-sawit-ri-turun-4-4-juta-ton-tahun-depan-akibat-el-nino)
- [Bisnis — GAPKI Jan–Sep 2026](https://market.bisnis.com/read/20261119/94/2022726/ekspor-sawit-tembus-249-juta-ton-per-september-2026-harga-jual-naik)
- [Katadata — DSI implementation and fee](https://katadata.co.id/berita/industri/6af80a97ac822/gapki-soroti-tantangan-implementasi-ekspor-sawit-lewat-dsi-mulai-tahun-depan)
- [Bisnis — Indo Premier DSI sensitivity](https://market.bisnis.com/read/20260522/7/1975717/menimbang-dampak-ekspor-satu-pintu-danantara-ke-emiten-sawit)
- [Bisnis — 383 HSC stocks out of IHSG](https://market.bisnis.com/read/20261111/7/2020551/383-emiten-masuk-daftar-hsc-bei-resmi-keluar-dari-ihsg-mulai-jumat-1311)
- [InfoSAWIT — MSCI May 2026 removals](https://www.en.infosawit.com/news/17735/msci-removes-four-indonesian-palm-oil-stocks-from-small-cap-index)
- [Bisnis — AALI forest fine and Salim group payment](https://market.bisnis.com/read/20260122/192/1946243/astra-agro-aali-rogoh-kocek-rp57104-miliar-bayar-denda-satgas-pkh)
- [Tiger/Reuters brief — IndoAgri escrow](https://www.itiger.com/news/2613786372)
- Company result articles (Kontan, Bisnis, BCA Sekuritas/IQPlus, IDX Channel, EmitenNews) for AALI, SIMP, SSMS, DSNG, BWPT, TBLA, JARR, as listed in the Phase III document.

**Prices:** Ajaib (TAPG 19 Nov), Sectors and Stockbro (LSIP 19–20 Nov), JournalArta (AALI, SSMS, DSNG, TAPG, LSIP 20–23 Nov), Ajaib and carisaham (SIMP, TBLA, undated), Kontan and stockanalysis.com (BWPT 15 Oct; Phase I peer snapshot).

GAPKI, BPDP and ministry figures were mostly taken from press reports of their releases; the primary PDFs were not opened. Treat them as checks until they are confirmed.
