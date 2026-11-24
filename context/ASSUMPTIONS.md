# Assumptions

Every assumption used in models, valuations or backtests goes here with its source and date. Update the entry when it changes, and keep the history in the Changes column. Market inputs are dated: re-check them before each model run.

| ID | Area | Assumption | Value | Source / basis | Date set | Changes |
|---|---|---|---|---|---|---|
| A-001 | Quant | Liquidity threshold for the core universe (approx. average daily traded value) | ≥ IDR 1.5bn | Judgement; screen in `research/industry/2026-11-24_universe_screen.md` (S-001) | 2026-11-24 | — |
| A-002 | Quant | Liquidity band for the extended universe | IDR 0.25–1.5bn | Same as A-001 | 2026-11-24 | — |
| A-003 | Quant | Minimum 20-day ADV for a backtest position | Rp1bn | `quant/config/settings.yaml` | 2026-11-24 | — |
| A-004 | Quant | Transaction costs | Buy 0.15%; sell 0.25% (incl. 0.10% sales tax); slippage 20bps + 5bps per 1% of ADV; max 10% of ADV | `settings.yaml`; IDX broker norms (judgement) | 2026-11-24 | — |
| A-005 | Quant | Publication lags where the actual filing time is unknown | Quarterly unaudited 45d; reviewed 75d; annual 100d; GAPKI 50d; MPOB 12d | OJK filing deadlines (conservative); `settings.yaml` | 2026-11-24 | — |
| A-006 | Quant | Execution | Signal at close t, trade at close t+1; disclosures after 16:00 WIB count as next day | `settings.yaml` | 2026-11-24 | — |
| A-007 | Quant | Walk-forward | 2016–18 burn-in; annual out-of-sample folds from 2019 | `settings.yaml` | 2026-11-24 | — |
| A-008 | Quant | Initial factor weights (hypothesis, not optimised) | Value 25 / earnings 25 / quality 20 / commodity 15 / market 15 | Mandate §11-B | 2026-11-24 | Supersedes the equal-weight composite in the quant brief; equal weight kept as a sensitivity |
| A-009 | Selection | Decision weights (research prior) | Mispricing 30 / surprise 25 / catalyst 20 / downside 15 / data quality 10 | Mandate §14; Phase III | 2026-11-24 | — |
| A-010 | Valuation | Cost of equity | 13.75% = 10-year SBN 7.75% + ERP 6.0%; flexed to 12.5% | SBN: IDX Channel (Nov 2026). ERP: judgement, source still needed (B-20) | 2026-11-24 | Checked 2026-11-24: SBN 7.73% (18 Nov, MNC via Kontan) → 13.73%; kept at 13.75% |
| A-011 | Valuation | Terminal growth | TAPG 3%; LSIP 2%; reverse P/E 0% | Judgement (Phase I–II) | 2026-11-24 | Audit §2.1: growth must match payout. TAPG at 96.5% payout implies ≈1.2% |
| A-012 | Valuation | Mid-cycle realised price index vs FY2025 | 0.9 base; 0.8 bear; 1.0 = FY25 | Phase II judgement | 2026-11-24 | — |
| A-013 | Valuation | CPO scenarios | RM3,600 / 3,900 / 4,200 / 4,800 per t | Phase I | 2026-11-24 | — |
| A-014 | TAPG | Cost structure | External FFB Rp2,993bn moves with price; other costs Rp4,866bn fixed | KB Valbury + FY25 audited FS | 2026-11-24 | Replaced Phase I's "25% variable" |
| A-015 | TAPG | Reinvestment | 20% of NOPAT (3% growth at 15% return on new capital) | Judgement | 2026-11-24 | — |
| A-016 | TAPG | JV payout / NCI / tax | 93% (3-year actual) / 5.15% of consolidated profit ex-JV / 22.7% effective ex-JV | FY23–25 audited FS | 2026-11-24 | — |
| A-017 | LSIP | External FFB cost | ≈Rp650bn (204kt × Rp3,200/kg) | Assumption | 2026-11-24 | — |
| A-018 | LSIP | Operating cash buffer | 3 months of cash costs = Rp765bn | Judgement | 2026-11-24 | — |
| A-019 | LSIP | Replanting catch-up | PV Rp1,053bn (Rp200bn a year for 10 years at 13.75%) | Judgement | 2026-11-24 | — |
| A-020 | LSIP | Cash multipliers and scenario weights | 0.2 / 0.4 / 0.8 / 0.95 / 1.0; weights 55 / 20 / 10 / 10 / 5 | Judgement from payout history | 2026-11-24 | **Under review:** the Rp750bn buyback was announced on 23 Oct 2026; execution is unverified (audit §2.3). Re-weight only on execution data |
| A-021 | LSIP | Associates | 50% of book in base; 0 in bear | Judgement | 2026-11-24 | — |
| A-022 | Sector | Run-rate profit | 9M26 × 4/3 (1H × 2 for BWPT, TBLA) | Simplification; ignores seasonality | 2026-11-24 | — |
| A-023 | Sector | El Niño 2027 bear volume | −8% (SIMP, AALI); −10% (SSMS) | Judgement (Phase III) | 2026-11-24 | To be replaced by the T-07 model |
| A-024 | Policy | DSI fee scenario | USD 5–10/t | DSI guidance "single digit" (Katadata, 13 Nov 2026) | 2026-11-24 | — |
| A-025 | FX | USD/IDR for translation | Rp18,245 | BI release, 17 Nov 2026 | 2026-11-24 | Previously Rp18,154 (LPEM) / ≈18,150 (press). Record the rate used in every model |
| A-026 | Macro | Brent reference | USD 92.44/bbl (16 Nov 2026); 2027 path USD 88 → 78 (Goldman, as reported) | KabarBursa / Reuters | 2026-11-24 | — |
| A-027 | DSNG | Pre-tax cost of debt (for the deleveraging estimate only) | 8% | **Placeholder**; replace with the FS finance cost ÷ average debt (B-01) | 2026-11-24 | — |
| A-028 | Climate | Water-deficit bucket capacity | 200mm | Placeholder for T-06; to be set from the literature review (B-16) | 2026-11-24 | — |

## Areas to cover

- **Macro:** CPO price deck (MYR/t, USD/t), full duty schedule, biodiesel mandate path.
- **Industry:** FFB yields by tree age, OER, cash cost per tonne, replanting rates.
- **Company:** planted and mature hectares, production growth, capex, dividend payout.
- **Valuation:** a sourced ERP, peer betas, EV per planted hectare.
