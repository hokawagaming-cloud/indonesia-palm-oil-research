# Research Backlog

_Last updated: 2026-11-24 · Governing brief: Master Research Mandate (24 Nov 2026) · Current phase: 1 (data verification)._

Each item is tagged with an **owner**:
- **Chat** — qualitative research, reading filings, thesis and interpretation.
- **Code** — data engineering, models and tests (spec in `context/CLAUDE_CODE_TASKS.md`).
- **User** — needs the user's access (a vendor licence, a networked machine, or a decision).

Priorities:
- **P1** blocks one of the three priority questions.
- **P2** blocks a module.
- **P3** is an improvement.

**The three priority questions (mandate §20):**
- **Q-A:** Is TAPG's premium justified by sustainable operating superiority and normalised returns?
- **Q-B:** Is DSNG's discount a real recovery opportunity, or justified by worsening production and earnings?
- **Q-C:** Is LSIP's cash realisable shareholder value, or a persistent capital-allocation discount?

**Standing rule:** no BUY, HOLD, SELL or ranking output until Phase 6. NO TRADE is a valid outcome.

---

## P1 — blocks Q-A, Q-B or Q-C

| ID | Task | Q | Owner | Input | Output | Done when |
|---|---|---|---|---|---|---|
| B-01 | Read the **DSNG 9M26 interim FS** and the 3Q26 operating release. Extract revenue by segment, EBITDA, consolidated vs attributable NP, NCI, inventory (t and Rp), CPO sales volume and ASP, debt by maturity / currency / fixed vs floating, finance cost | B | Chat | IDX filing PDF | `research/company/DSNG/2026-xx_9M26_extract.md` + rows in `data/manual/fundamentals_dsng.csv` | Conflicts C-11 and C-12 resolved |
| B-02 | Read the **LSIP 9M26 FS**: cash at 30 Sep, deposits by bank (including Bank Ina Perdana), related-party balances, associates, dividend payable, 9M NP | C | Chat | IDX / londonsumatra.com | `research/company/LSIP/` extract + CSV | C-15 resolved |
| B-03 | Track **LSIP buyback execution** (IDX reports): shares bought, average price, Rp spent; whether treasury shares are cancelled or held | C | Chat (monthly) | IDX disclosures | Event rows in `data/seed/policy_events.csv` | Reported to 31 Dec 2026 window end |
| B-04 | **TAPG quarterly operating history** 2021–3Q26 (nucleus and plasma FFB, external FFB, processed, CPO output and sales, yield, OER) | A | Chat → Code | Quarterly releases / presentations | `data/manual/operations_tapg.csv` | C-14 resolved; 2026 volume trend established |
| B-05 | **TAPG JV (USTP) accounts**: hectares, output, profit, dividends (FY25 Note 14a); split ROIC into book-cost, JV and operating effects | A | Chat | FY24–25 audited FS | Note in `research/company/TAPG/` | Mandate question 9.1-3 answered with numbers |
| B-06 | **Fertiliser timing**: TAPG and DSNG fertiliser expense by quarter 2023–3Q26 vs tonnes applied; estimate the deferred amount | A, B | Chat | FS notes, presentations | Table plus a FY26–27 catch-up estimate | Mandate question 9.1-5 answered |
| B-07 | **Estate location database** for TAPG, DSNG, LSIP (then AALI, SSMS, SIMP): estate, subsidiary, regency/province, planted / mature ha, planting years, mill. Record the source and the proxy level for each | A, B, C | Chat (collect) → Code (geocode) | ARs, RSPO / ISPO certificates, HGU or concession maps | `data/manual/estates.csv` | Each company ≥90% of planted ha assigned at least to regency level |
| B-08 | **Price every name on one close** (24 Nov 2026 or the latest available) with source | All | Chat | IDX / quote pages | `data/manual/prices_snapshot_20261124.csv` | Phase III and mandate prices reconciled |
| B-09 | **Find a source for the DSNG nowcast and the "consensus Rp2.26tn"**, or drop them | B | User / Chat | User's earlier notes | Source register row or deletion | C-13 resolved |

## P2 — blocks a quant or valuation module

| ID | Task | Owner | Output |
|---|---|---|---|
| B-10 | Full **PMK 38/2024 (as amended) export duty schedule**, plus monthly HR, duty and levy 2016–2026 | Chat (texts) → Code (series) | `data/seed/cpo_reference_price.csv` complete; `quant/palmquant/transmission.py` |
| B-11 | **Biodiesel allocations by producer** 2019–2027 (Kepmen annexes) and the B50 2027 decision when published | Chat | `data/manual/biodiesel_allocations.csv` |
| B-12 | **PP 24/2026 full text** (Art. 4–6) and **Permendag 16/2026**: scope, fees, payment terms, transition | Chat | `research/macro/2026-xx_dsi_regulation.md` |
| B-13 | **DSI fee notice** (December 2026) | Chat | Event row; update H-05 |
| B-14 | **Price and volume history 2013–2026** with corporate actions and suspensions | Code (networked) | Task T-02 |
| B-15 | **Rainfall and water deficit** per estate cluster (CHIRPS, ERA5, NASA POWER) | Code (networked) | Tasks T-05 / T-06 |
| B-16 | **Agronomic literature review** on drought → yield lag windows (0–3, 4–6, 7–12, 13–18, 19–30 months) and nonlinear thresholds | Chat | `research/industry/2026-xx_drought_yield_lags.md` with citations |
| B-17 | **Historical El Niño episodes** (2015–16, 2018–19, 2023–24): company FFB, ASP, unit cost, margin, share price, and when the market recognised each | Chat (fundamentals) + Code (prices) | Task T-08 |
| B-18 | **Broker estimates with dates** for TAPG, DSNG, LSIP (public PDFs); label each by date and broker | Chat | `data/manual/broker_estimates.csv` (never labelled "consensus") |
| B-19 | **Macro gaps**: DXY; China and India activity and vegetable-oil imports; IOD and BMKG regional outlook | Chat | Update audit §3 and §5 |
| B-20 | **Cost of equity**: verified risk-free rate, an equity risk premium with source, peer betas from weekly data (TAPG's 5-year beta of 0.12 is unusable) | Code (betas) + Chat (ERP source) | `context/ASSUMPTIONS.md` A-010 revised |

## P3 — improvements

| ID | Task | Owner |
|---|---|---|
| B-21 | Supply and demand model 2013–2030 (Indonesia, Malaysia, world stocks / use, substitutes) | Chat + Code |
| B-22 | Biodiesel funding model with scenarios (B40 / B50 / B60 × Brent × CPO × rupiah × exports × levy) | Code (T-10) |
| B-23 | Free float from KSEI; HSC history back to 2023 | Chat |
| B-24 | Listed logistics and fertiliser names in the value chain | Chat |

---

## Decision points for the user

1. **Data access.** Who runs the networked ingestion (T-02, T-05, T-06), and is any vendor available (Bloomberg/FactSet/LSEG for FCPO, KPBN and consensus)? Without a vendor, consensus stays a labelled proxy.
2. **Study start.** Use 2013 if company quarterly operating data is retrievable back that far; otherwise 2016 (mandate §11-A). Default: **2016**, with 2013–2015 where available.
3. **Phase III finalists.** SIMP, SSMS and AALI are now comparison names (D-003). Confirm, or restore them as primary coverage.
