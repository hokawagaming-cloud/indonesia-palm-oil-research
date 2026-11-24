# Phase V — Predictive Catalyst Screen of the Palm Universe (lightweight)

_Date: 2026-11-24 · Files: `data/reference/research/universe_catalyst_screen_20261124.csv`, `universe_implied_q4_20261124.csv`, `data/reference/consensus_history.csv` (first snapshot) · Sources: S&P consensus via Yahoo (S-036), Yahoo quarterly statements (secondary), S-002 prices · No full models, no rating_

## Coverage

- Only **8 of 17** screened names have consensus (TAPG, DSNG, STAA, AALI, LSIP, SIMP, TBLA, NSSS).
- SSMS, BWPT, MGRO, GZCO, ANJT, SGRO, SMAR, CSRA and PSGO have none, so **no expectations gap can be measured** for them. They are excluded from selection, not judged.

## Screen (24 Nov 2026)

| Name | P/E FY26 / FY27 | FY27 growth (cons.) | 30-day FY26 revision | Analysts (dispersion) | Implied Q4 vs Q1–Q3 avg | Return since 28 Oct | Median traded value (IDR bn) |
|---|---|---|---|---|---|---|---|
| LSIP | 5.1 / 4.8 | +5% | +10% | 5 (12%) | **−38%** (360 vs 582) | +6.8% | 13.6 |
| AALI | 7.7 / 8.2 | −5% | +26% | 8 (29%) | −27% | −2.6% | 20.6 |
| TAPG | 8.0 / 7.6 | +6% | +2% | 4 (8%) | −38% | −8.2% | 21.5 |
| DSNG | 6.0 / 5.8 | +3% | −3% | 4 (44%) | +63% | −13.0% | 5.1 |
| STAA | 5.7 / 5.2 | +9% | +18% | **1** | −5% | −4.7% | 4.1 |
| SIMP | 4.5 / 4.2 | +8% | −26% | **1** | n/m (consensus below 9M actual: stale) | +8.7% | 5.1 |
| TBLA | 2.9 / 2.5 | +16% | +18% | **1** | +149% | −7.1% | 0.7 (extended band) |
| NSSS | 24.9 / 24.0 | +4% | n/a | **1** | −5% | +36.6% | 2.5 |

## Leading indicators checked

- **Fertiliser prices** (WB, S-003): urea +6.5%, DAP +6.5%, MOP +1.6% YoY (Oct 2026). There is no price shock, so guided FY27 fertiliser increases (+25% at TAPG) are mainly volume and timing.
- **Netback:** the Nov levy/duty cut cushions domestic prices; KPBN tenders are −4% Oct→Nov.
- **ENSO:** ONI 2.46 and the Jun–Sep rainfall deficit point to FY27 volume risk for Kalimantan-heavy names (TAPG, DSNG, AALI, SSMS). Exposure by name is not yet mapped from primary data.
- **A sector pattern, not a stock signal:** consensus implies a weak Q4 for the well-covered upstream names (LSIP, TAPG −38%; AALI −27%). This is either a shared seasonal or cost assumption (fertiliser catch-up, lower prices) or staleness.
  - It is testable at the FY2026 filings with the new surprise framework (`quant/surprise_study.py`).
  - It is **not** tradable evidence: TAPG's history shows no predictable reaction to surprises (n = 8).

## Selection for deeper research

- **LSIP — SELECTED (research only; not a trade).**
  - Liquid (IDR 13.6bn/day); 5 analysts with low dispersion; consensus rising (+10%).
  - 5.1× FY26 P/E, and **net cash ≈ IDR 8.5tn with zero debt** (Yahoo balance sheet, Sep-26, to verify) against a market cap of about 10.7tn. That makes EV about 2.2tn, roughly 1× FY26 earnings.
  - Q3 gross profit doubled QoQ (924 vs 438bn on revenue +20%), with no unusual items flagged. Its composition (biological-asset fair value? price/cost?) must be checked in the primary 9M26 FS.
  - **The asymmetry question:** is the cash a value trap (payout about 25–30%; dividend IDR 83/share = 5.3% yield) or a re-rating catalyst? Group context (SIMP/Indofood parent) is relevant.
- **AALI — WATCH.** Large upgrades (+26%) were already priced (+25% in Oct). Consensus FY27 decline −5%.
- **Not selected:**
  - STAA, SIMP, TBLA, NSSS: single-analyst consensus, too thin to define expectations. TBLA is also illiquid.
  - DSNG: catalyst already in consensus.
  - TAPG: remains primary coverage on WATCH.

**Decision unchanged: NO TRADE** (D-025).
