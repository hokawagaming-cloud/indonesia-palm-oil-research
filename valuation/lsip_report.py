"""Render the Phase XVII LSIP deliverables from committed result files (no hand-typed model numbers).

    python -I -X utf8 valuation/lsip_report.py
Writes research/company/LSIP/2026-11-26_LSIP_equity_research.md, ..._executive_summary.md, ..._IC_memo.md
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
OUT = ROOT / "research" / "company" / "LSIP"
D = "2026-11-26"

R = json.loads((RES / "LSIP_valuation_results.json").read_text())
CS = json.loads((RES / "LSIP_cohort_summary.json").read_text())
T = json.loads((RES / "LSIP_TAPG_valuation.json").read_text())
RK = json.loads((RES / "LSIP_risk_stats.json").read_text())
SNAP = json.loads((RES / "LSIP_market_snapshot.json").read_text(encoding="utf-8"))
FIN = pd.read_csv(RES / "LSIP_financials_annual.csv", index_col=0)
OPS = pd.read_csv(RES / "LSIP_operational_annual.csv", index_col=0)
AGE = pd.read_csv(RES / "LSIP_age_profile.csv")
COGS = pd.read_csv(RES / "LSIP_cogs_breakdown.csv", index_col=0)
Q4 = pd.read_csv(RES / "LSIP_q4_2026_nowcast_v2.csv", index_col=0)
Q4v1 = pd.read_csv(RES / "LSIP_q4_2026_nowcast.csv", index_col=0)
CASH = pd.read_csv(RES / "LSIP_cash_decomposition.csv")
CR = pd.read_csv(RES / "LSIP_capital_return_history.csv")
AUD = pd.read_csv(RES / "LSIP_prior_audit.csv")
EVT = pd.read_csv(RES / "LSIP_event_reactions.csv")
VH = pd.read_csv(RES / "LSIP_valuation_history.csv")
TC = pd.read_csv(RES / "LSIP_TAPG_comparison.csv")
ENS = pd.read_csv(RES / "LSIP_cohort_ensemble.csv")
RPC = pd.read_csv(RES / "LSIP_related_party_cash.csv", index_col=0)
FIT = pd.read_csv(RES / "LSIP_cohort_fit.csv")
CAL = pd.read_csv(RES / "LSIP_cohort_calibration.csv")

PX = R["price"]; SH = 6819.963965
J = R["joint"]; S = R["sensitivity"]; V = R["reverse"]
SC = ["A_historical", "B_accelerated", "C_deferred", "D_intensive"]
SCL = {"A_historical": "A - historical pace", "B_accelerated": "B - accelerated", "C_deferred": "C - deferred", "D_intensive": "D - intensive"}
HUR, HUR2 = 0.175, RK["hurdle"]["proposed_hurdle"]
f0 = lambda x: f"{x:,.0f}"  # noqa: E731
f1 = lambda x: f"{x:,.1f}"  # noqa: E731
pc = lambda x: f"{x:.0%}"   # noqa: E731
pc1 = lambda x: f"{x:.1%}"  # noqa: E731
ke = 0.0774 + 0.9 * 0.06
g11 = (1 + ke) ** (11 / 12)


def j(s, c, cr, k):
    return J[f"{s}|{c}|{cr}"][k]


base = {k: j("A_historical", "base", 0.8, k) for k in ("ps", "ops_ps", "cash_ps", "ddm_ps", "tp12", "tr12", "entry")}
bear = {k: j("A_historical", "bear", 0.8, k) for k in ("ps", "tp12", "tr12")}
bull = {k: j("A_historical", "bull", 0.8, k) for k in ("ps", "tp12", "tr12")}
DPS27 = R["grid"]["A_historical|base"]["dps27"]
# breakeven cash credit for the hurdle (linear in credit)
ops, c1 = j("A_historical", "base", 1.0, "ops_ps"), j("A_historical", "base", 1.0, "cash_ps")
def be_credit(h):
    fv = PX * (1 + h) / g11
    return (fv - ops) / c1
BE, BE2 = be_credit(HUR), be_credit(HUR2)
# BUY entry: base return clears the hurdle even at 60% cash credit
ENTRY_BUY = j("A_historical", "base", 0.6, "entry")
ENTRY_BUY2 = (j("A_historical", "base", 0.6, "tp12") + DPS27) / (1 + HUR2)
mkt_credit = V["implied_cash_credit_at_base_ops"]
TR_at_mkt_credit = (ops + c1 * mkt_credit) * g11 / PX - 1
q4b = Q4.loc["base"]; cons26 = q4b.consensus_fy26_np; consq4 = q4b.consensus_implied_q4
cons27 = [c for c in SNAP["consensus"] if c["ticker"] == "LSIP" and c["fy"] == "FY27"][0]["eps_avg"] * SH / 1000
det = R["detail"]
ni27 = {c: det[f"A_historical|{c}"]["ni"]["2027"] for c in ("bear", "base", "bull")}
eps27 = {c: det[f"A_historical|{c}"]["eps"]["2027"] for c in ("bear", "base", "bull")}
a23 = AGE[AGE.date == "2023-12-31"].dropna(subset=["total"]).iloc[0]
o25 = OPS.loc["FY2025"]
yg = T["yield_gap_fy2025"]; evha = T["ev_per_planted_ha_idr_m"]; av = T["aging_value"]
surplus = float(CASH.loc[CASH.item == "Distributable surplus cash (before buyback)", "idr_bn"].iloc[0])
rk = RK["risk"]
pt = SNAP["lsip_price_targets"]
VERDICT = "HOLD / WATCH"


def tbl(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(x) for x in r.values) + " |")
    return "\n".join(out)


def scen_table():
    rows = []
    for s in SC:
        g = R["grid"]
        rows.append([SCL[s], f0(CS["steady_state"][s]["replant_ha"]), f1(CS["steady_state"][s]["cycle_years"]),
                     f0(det[f"{s}|base"]["ffb_n"]["2030"]), f0(det[f"{s}|base"]["ffb_n"]["2035"]), f0(det[f"{s}|base"]["ffb_n"]["2050"]),
                     f0(det[f"{s}|base"]["cx_rep"]["2030"]), f0(det[f"{s}|base"]["fcff"]["2030"]),
                     f0(j(s, "base", 0.8, "ops_ps")), f0(j(s, "bear", 0.8, "ps")), f0(j(s, "base", 0.8, "ps")), f0(j(s, "bull", 0.8, "ps")),
                     f0(g[f"{s}|base"]["ddm_ps"])])
    return tbl(pd.DataFrame(rows, columns=["Scenario", "LR planting ha/yr", "Cycle yrs", "FFB 2030 kt", "FFB 2035 kt", "FFB 2050 kt",
                                           "Replant capex 2030 IDR bn", "FCFF 2030 IDR bn", "Ops value /sh", "Value bear", "Value base", "Value bull", "DDM base"]))


def report() -> str:
    hist = []
    for p in ["FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9M26"]:
        f = FIN.loc[p] / 1000; o = OPS.loc[p] if p in OPS.index else None
        hist.append([p, f0(f.revenue), f0(f.gross_profit), f0(f.operating_profit), f0(f.profit), f0(f.cfo), f0(-f.capex), f0(-f.dividends_paid),
                     f0(f.cash_end), f0(o.ffb_nucleus) if o is not None else "", f1(o.yield_nucleus_t_ha) if o is not None and pd.notna(o.yield_nucleus_t_ha) else ""])
    H = tbl(pd.DataFrame(hist, columns=["Period", "Revenue", "Gross profit", "Op. profit", "Profit", "CFO", "Capex", "Dividends paid", "Cash", "Nucleus FFB kt", "Yield t/ha"]))
    ages = AGE.dropna(subset=["total"])
    A = tbl(pd.DataFrame([[r.date[:4], f0(r.immature), f0(r.a4_6), f0(r.a7_20), f0(r.gt20), f0(r.total), pc(r.gt20_share)] for _, r in ages.iterrows()],
                         columns=["FY", "Immature", "4-6 yrs", "7-20 yrs", ">20 yrs", "Total ha", ">20 share"]))
    avg = tbl(pd.DataFrame([[r.date, r.reported_avg_age, r.source] for _, r in AGE.dropna(subset=["reported_avg_age"]).iterrows()],
                           columns=["Date", "Reported avg age", "Source (phrase asserted in text)"]))
    cg = COGS.loc[["FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9M26"]]
    cogs_t = tbl(pd.DataFrame([[p, f0(r.ffb_purchases / 1000), f0(r.harvesting / 1000), f0(r.upkeep_fertiliser / 1000),
                                f1(r.upkeep_fertiliser / OPS.loc[p, "op_mature"]) if p.startswith("FY") else "", f0(r.indirect / 1000), f0(r.total_production_cost / 1000)]
                               for p, r in cg.iterrows()], columns=["Period", "FFB purchases", "Harvesting", "Upkeep & fertiliser", "Upkeep IDR m/mature ha", "Indirect", "Total production cost"]))
    cal = tbl(pd.DataFrame([[int(r.year), f0(r.reported_ffb_kt), f0(r.standard_curve_ffb_kt), f"{r.k:.3f}"] for _, r in CAL.iterrows()],
                           columns=["Year", "Reported nucleus FFB kt", "Standard-curve potential kt", "k"]))
    cashT = tbl(pd.DataFrame([[r["item"], f0(r.idr_bn) if abs(r.idr_bn) > 5 else (f"{r.idr_bn:.0%}" if abs(r.idr_bn) < 1.5 and r.idr_bn != 0 else f0(r.idr_bn)), r.basis] for _, r in CASH.iterrows()],
                             columns=["Item", "IDR bn", "Basis"]))
    crT = tbl(pd.DataFrame([[int(r.fy), f0(r.profit_bn), r.dps_declared, pc(r.payout), f0(r.cash_end_bn), pc1(r.cash_yield), f0(r.fcf_bn),
                             f0(r.dividends_paid_bn), f0(r.related_party_cash_bn) if pd.notna(r.related_party_cash_bn) else "n/a"] for _, r in CR.iterrows()],
                           columns=["FY", "Profit", "DPS (Rp)", "Payout", "Year-end cash", "Cash yield", "FCF", "Dividends paid", "Bank Ina Perdana"]))
    audT = tbl(AUD.assign(previous_value=AUD.previous_value.map(lambda x: "" if pd.isna(x) else (f"{x:.3f}" if abs(x) < 2 else f0(x))),
                          phase17_value=AUD.phase17_value.map(lambda x: "" if pd.isna(x) else (f"{x:.3f}" if abs(x) < 2 else f0(x)))))
    q4T = tbl(pd.DataFrame([[k, f"{Q4.loc[k, 'vol']:.2f}x", f"{Q4.loc[k, 'price']:+.0%}", f"{Q4.loc[k, 'release']:.0%}", f0(Q4.loc[k, 'upkeep_catchup']),
                             f0(Q4.loc[k, 'q4_np_owners']), f0(Q4.loc[k, 'fy26_np_owners']), f0(Q4v1.loc[k, 'q4_np_owners'])] for k in ("bear", "base", "bull")],
                           columns=["Case", "Volume vs Q3", "Price vs Q3", "Q3 build released", "Fertiliser catch-up", "Q4 profit v2", "FY26 profit v2", "Q4 profit v1 (preserved)"]))
    proj = []
    for y in ("2026", "2027", "2028", "2029", "2030", "2035"):
        d = det["A_historical|base"]
        proj.append([f"FY{y}E", f0(d["ffb_n"][y]), f0(d["price"][y]), f0(d["revenue"][y]), f0(d["ebitda"][y]), f0(d["ni"][y]), f0(d["eps"][y]),
                     f0(d["dps"][y]), f0(d["capex"][y]), f0(d["fcff"][y]), f0(d["cash"][y])])
    P = tbl(pd.DataFrame(proj, columns=["Year", "Nucleus FFB kt", "CPO IDR/kg", "Revenue", "EBITDA", "Profit", "EPS", "DPS paid", "Capex", "FCFF", "Cash"]))
    sensT = []
    for k, lab, keys in (("plrm", "Long-run CPO IDR/kg", None), ("yld", "FFB yield multiplier", None), ("fxm", "USD/IDR multiplier", None),
                         ("rpc", "Replant cost IDR m/ha", None), ("fert", "Fertiliser/upkeep multiplier", None), ("beta", "Beta (ke = 7.74% + b x 6%)", None),
                         ("cr", "Cash credit", None), ("rph", "Related-party cash haircut", None), ("bb", "Buyback executed IDR bn", None),
                         ("tvp", "Terminal productivity", None), ("g", "Terminal nominal growth", None), ("pay", "Payout (DDM only)", None)):
        for x, v in S[k].items():
            sensT.append([lab, x, f0(v["ps"]), f0(v["ddm_ps"]), pc(v["tr12"])])
    SENS = tbl(pd.DataFrame(sensT, columns=["Driver", "Value", "Value/sh (80% credit unless driver)", "DDM/sh", "12m return"]))
    tcT = TC[TC.fy == 2025].set_index("company")
    comp = []
    for lab, col, fmt in (("Planted oil palm ha", "planted_oil_palm_ha", f0), ("Mature ha", "mature_ha", f0), ("Share >20 years", "gt20_share", pc),
                          ("FFB yield t/ha", "yield_t_ha", f1), ("OER", "oer", pc1), ("Revenue IDR bn", "revenue_bn", f0), ("Operating margin", "op_margin", pc),
                          ("ROIC (NOPAT / equity ex cash)", "roic", pc), ("FCF IDR bn", "fcf_bn", f0), ("Dividends / FCF", "fcf_payout", pc),
                          ("Cash IDR bn", "cash_bn", f0), ("Sustainable replant ha/yr (25y)", "sustainable_replant_ha_25y", f0)):
        lv = tcT.loc["LSIP", col] if col in tcT.columns else float("nan")
        tv = tcT.loc["TAPG", col] if col in tcT.columns else float("nan")
        if col == "gt20_share":
            lv = a23.gt20_share
        comp.append([lab, fmt(lv) if pd.notna(lv) else "n/a", fmt(tv) if pd.notna(tv) else "n/a"])
    comp += [["EV per planted ha IDR m (market)", f"{f0(evha['LSIP_cash100'])}-{f0(evha['LSIP_cash80'])}", f0(evha["TAPG"])],
             ["Operating profit per mature ha IDR m", f1(T["op_profit_per_mature_ha_fy2025_idr_m"]["LSIP"]), f1(T["op_profit_per_mature_ha_fy2025_idr_m"]["TAPG"])],
             ["Price (25 Nov 2026)", f0(PX), f0(T["price"])],
             ["Value bear/base/bull (same price deck)", f"{f0(bear['ps'])} / {f0(base['ps'])} / {f0(bull['ps'])}",
              " / ".join(f0(T["cases"][c]["fv_ps"]) for c in ("bear", "base", "bull"))],
             ["12m total return bear/base/bull", " / ".join(pc(x) for x in (bear["tr12"], base["tr12"], bull["tr12"])),
              " / ".join(pc(T["cases"][c]["tr12"]) for c in ("bear", "base", "bull"))],
             ["Volatility (5y daily, annualised)", pc(rk["LSIP"]["ann_vol_daily_5y"]), pc(rk["TAPG"]["ann_vol_daily_5y"])],
             ["Base return / volatility", f"{T['LSIP_base_return_per_vol']:.2f}", f"{T['TAPG_base_return_per_vol']:.2f}"],
             ["Max drawdown since 2015 (TAPG since 2021 listing)", pc(rk["LSIP"]["max_drawdown_since_2015"]), pc(rk["TAPG"]["max_drawdown_since_2015"])],
             ["Market beta / sector beta (5y weekly, HAC)", f"{rk['LSIP']['beta_mkt_5y_weekly']:.2f} / {rk['LSIP']['beta_sector_5y_weekly']:.2f}",
              f"{rk['TAPG']['beta_mkt_5y_weekly']:.2f} / {rk['TAPG']['beta_sector_5y_weekly']:.2f}"],
             ["Market-implied long-run realised CPO", f"{f0(V['implied_long_run_cpo_full_cash_credit'])} (100% cash) / {f0(V['implied_long_run_cpo_idr_kg'])} (80%)", f0(T["implied_lr_price"])]]
    COMP = tbl(pd.DataFrame(comp, columns=["Metric (FY2025 unless stated)", "LSIP", "TAPG"]))
    evT = tbl(EVT.assign(car_0_1=EVT.car_0_1.map(pc1), car_0_5=EVT.car_0_5.map(pc1), car_0_20=EVT.car_0_20.map(lambda x: "" if pd.isna(x) else pc1(x))))
    vhT = tbl(VH.assign(**{c: VH[c].map(lambda x: "" if pd.isna(x) else (f"{x:.2f}" if abs(x) < 50 else f0(x))) for c in VH.columns if c != "fy"}))
    ens = ENS.groupby("scenario")[["ffb_2035", "ffb_2050", "ffb_cum_2026_2050"]].agg(["min", "median", "max"]).round(0)
    ensT = tbl(pd.DataFrame([[SCL[s]] + [f0(ens.loc[s, (c, q)]) for c in ("ffb_2035", "ffb_2050") for q in ("min", "median", "max")] for s in SC],
                            columns=["Scenario", "FFB 2035 min", "median", "max", "FFB 2050 min", "median", "max"]))
    rt = R["grid"]["A_historical|base"]

    return f"""# PT PP London Sumatra Indonesia Tbk (LSIP) — Ageing Estate, Trapped Cash

_Institutional equity research · Phase XVII · {D} · Price IDR {f0(PX)} (close 25 Nov 2026) · IDR bn unless stated_
_Integrated model: `outputs/LSIP_model_valuation.xlsx` (live formulas) · Cohort model: `valuation/lsip_cohort.py` · All exhibits: `outputs/lsip/`_
_Not investment advice. Evidence classes: **REPORTED** (filings), **DERIVED** (our arithmetic on filings), **ANALYST** (assumption), **RECONSTRUCTED** (model-inferred, not disclosed)._

## Recommendation: {VERDICT} — BUY at ≤ IDR {f0(ENTRY_BUY)} or on verified capital return

| | |
|---|---|
| Price (25 Nov 2026) | IDR {f0(PX)} |
| Fair value at 31 Dec 2026, bear / base / bull (scenario A, 80% cash credit) | IDR {f0(bear['ps'])} / **{f0(base['ps'])}** / {f0(bull['ps'])} |
| of which plantation operations / distributable surplus cash (base) | IDR {f0(base['ops_ps'])} / {f0(base['cash_ps'])} |
| Value with 100% / 60% cash credit (base) | IDR {f0(j('A_historical','base',1.0,'ps'))} / {f0(j('A_historical','base',0.6,'ps'))} |
| Minority cash-receipts value (DDM, 30% payout, base) | IDR {f0(base['ddm_ps'])} |
| 12-month target price (base, 80% credit) | **IDR {f0(base['tp12'])}** |
| Expected dividend (FY2027 DPS, base) / yield | IDR {f0(DPS27)} / {pc1(DPS27 / PX)} |
| Expected 12-month total return: base / bear / bull | **{pc(base['tr12'])}** / {pc(bear['tr12'])} / {pc(bull['tr12'])} |
| 12-month return if the market's current cash credit ({pc(mkt_credit)}) persists | {pc(TR_at_mkt_credit)} |
| Cash credit needed to clear the {pc1(HUR)} hurdle ({pc1(HUR2)} proposed) | {pc(BE)} ({pc(BE2)}) |
| Entry price for the hurdle: base 80% credit / robust to 60% credit | IDR {f0(base['entry'])} / **IDR {f0(ENTRY_BUY)}** (IDR {f0(ENTRY_BUY2)} at {pc1(HUR2)}) |
| Downside scenario (bear price, 60% cash credit) | IDR {f0(j('A_historical','bear',0.6,'ps'))} ({pc(j('A_historical','bear',0.6,'tr12'))}) |
| Investment horizon | 12-24 months (catalysts: buyback report Jan 2027, FY26 results Feb 2027, AGM Jun 2027) |

**Answer to the central question.** After accounting for plantation ageing, replanting needs and capital-allocation risk, LSIP **does offer a better risk-adjusted expected return than TAPG at prevailing prices** (base {pc(base['tr12'])} vs {pc(T['cases']['base']['tr12'])}; bear {pc(bear['tr12'])} vs {pc(T['cases']['bear']['tr12'])}; return per unit of volatility {T['LSIP_base_return_per_vol']:.2f} vs {T['TAPG_base_return_per_vol']:.2f}), because LSIP's price already discounts weak plantation economics and trapped cash (it implies a long-run realised CPO price of about IDR {f0(V['implied_long_run_cpo_idr_kg'])}/kg at 80% cash credit) while TAPG's price capitalises about IDR {f0(T['implied_np_at_price'])}bn of sustainable profit (long-run CPO ≈ IDR {f0(T['implied_lr_price'])}/kg). **But LSIP clears our own hurdle only if minority shareholders can expect to realise at least ~{pc(BE)} of the distributable surplus cash**, and the market currently credits about {pc(mkt_credit)}. The binding constraint is capital allocation, not biology: correcting the age profile (scenario B) adds only about IDR {f0(av['B_minus_A_ops_per_share'])}/share, whereas lifting the payout from 30% to 100% raises the minority cash-flow value from IDR {f0(S['pay']['0.3']['ddm_ps'])} to IDR {f0(S['pay']['1.0']['ddm_ps'])}/share. We therefore rate LSIP **{VERDICT}** — a relative-value preference over TAPG, not an absolute BUY — and would buy below IDR {f0(ENTRY_BUY)} or on verified capital return.

LSIP-specific forecasting here is **not validated**: the earnings model and the Q4 nowcast have no out-of-sample record (first resolution: FY2026 results, ~Feb 2027). Nothing in this report is a claim of trading alpha.

## 1. Thesis in five points

1. **The estate is old, and disclosure has stopped.** At FY2023, {pc(a23.gt20_share)} of the {f0(a23.total)} ha nucleus oil-palm area was older than 20 years (REPORTED, AR2023 p7); the reported average age rose from 13.4 (Mar 2016) to 19 years (AR2023; SR2023 says 18). **No age profile has been published since** (AR2024, AR2025, SR2024, SR2025 all omit it).
2. **Replanting runs at half the replacement rate.** Reconstructed plantings average {f0(CS['hist_planting_rate_2017_2025_ha'])} ha/yr over 2017-2025 (RECONSTRUCTED; ensemble {f0(CS['hist_planting_rate_range_ensemble'][0])}-{f0(CS['hist_planting_rate_range_ensemble'][1])}), an implied ~{CS['implied_cycle_years_at_hist_rate']:.0f}-year cycle, versus {f0(CS['sustainable_rate_ha_25y'])} ha/yr for a 25-year cycle.
3. **Yields are low, and age explains only a third of it.** Nucleus yield fell from {f1(OPS.loc['FY2018','yield_nucleus_t_ha'])} t/ha (FY2018) to {f1(o25.yield_nucleus_t_ha)} t/ha (FY2025) against TAPG's {f1(yg['tapg_actual'])}. On a common standard curve, LSIP's age mix explains {f1(yg['gap_due_to_age_mix'])} t/ha of the {f1(yg['gap_total'])} t/ha gap; the other {f1(yg['gap_due_to_productivity_factor'])} t/ha is a productivity shortfall (LSIP achieves {pc(yg['k_lsip'])} of the curve vs TAPG {pc(yg['k_tapg'])}).
4. **The cash is real, but most of it is not reaching minorities.** Cash was IDR {f0(FIN.loc['9M26','cash_end']/1000)}bn at 30 Sep 2026 with no debt; distributable surplus after operating needs and debt-like items is IDR {f0(surplus)}bn ({f0(surplus*1000/SH)}/share, {pc(surplus*1000/SH/PX)} of the price). Payout has been 20-35%; the parent SIMP (59.51%) buys {pc(0.6326)} of revenue; 15-22% of cash sat at the Salim-group Bank Ina Perdana in FY2021-25.
5. **Valuation already prices much of this.** Market EV ex cash is about IDR {f0(evha['LSIP_cash100'])}-{f0(evha['LSIP_cash80'])}m per planted ha vs TAPG IDR {f0(evha['TAPG'])}m, although FY2025 operating profit per mature ha differs by only {pc(1 - T['op_profit_per_mature_ha_fy2025_idr_m']['LSIP'] / T['op_profit_per_mature_ha_fy2025_idr_m']['TAPG'])}.

## 2. Audit of previous LSIP research

Previous outputs were treated as hypotheses and recomputed from primary disclosures (`quant/lsip_phase17_analysis.py`, `LSIP_prior_audit.csv`). The Stage-1 nowcast and Phase VII figures are preserved unchanged in their original files.

{audT}

Notes: (i) the 76% parent-sales share in the Stage-1 note could not be reproduced; the FY2025 FS discloses SIMP at 63.26% of revenue (single customer >10%). (ii) Q4 v1 is kept as logged; v2 is a separate, newer estimate. (iii) Phase VII's 17.6% expected return and 1,340-1,460 entry range came from a market-calibrated multiple frame; they are superseded by the scenario DCF/DDM framework below, not revised retroactively.

## 3. Plantation age profile and biological economics

### 3.1 Reported age bands (nucleus oil palm, ha; REPORTED)

{A}

Reported average ages (every phrase is asserted to appear in the cited document by `quant/lsip_ops_dataset.py`):

{avg}

Inconsistencies kept visible: the Mar-2016 deck's 13.4 years is hard to reconcile with the FY2017 bands (37% > 20 years) — the 1995-96 expansion cohorts crossed 20 in 2016-17; AR2023 and SR2023 give 19 and 18 years for the same date. The ensemble uses both.

### 3.2 Operating history (REPORTED; yield DERIVED = nucleus FFB / mature ha)

{H}

Company-owned (nucleus) FFB is separated from purchased plasma and third-party FFB (FY2025: {f0(o25.ffb_total - o25.ffb_nucleus)}kt, {pc(o25.external_share)} of FFB processed; 9M26 {f0(OPS.loc['9M26','ffb_external'])}kt). Plasma (35,861 ha) is smallholder land and is not valued as company land. OER (CPO / all FFB processed): FY2025 {o25.oer}% reported, 9M26 {OPS.loc['9M26','oer']}%; KER 6.0-6.2%. Estate-level productivity is not disclosed (regional planted area only).

### 3.3 Cost structure and fertiliser (REPORTED, COGS note)

{cogs_t}

Upkeep & fertiliser per mature hectare fell from IDR {f1(COGS.loc['FY2022','upkeep_fertiliser']/OPS.loc['FY2022','op_mature'])}m (FY2022) to {f1(COGS.loc['FY2024','upkeep_fertiliser']/OPS.loc['FY2024','op_mature'])}m (FY2024), then recovered to {f1(COGS.loc['FY2025','upkeep_fertiliser']/OPS.loc['FY2025','op_mature'])}m in FY2025; the FY2025 yield was the lowest in the series. The fertiliser-catch-up hypothesis from Stage 1 is consistent with this (9M26 run-rate {f0(COGS.loc['9M26','upkeep_fertiliser']/1000)}bn), but fertiliser is not disclosed separately from upkeep, so the split is not verifiable.

### 3.4 Replanting evidence

LSIP discloses no annual replanting hectares, targets or replanting capex. What exists: immature bearer-plant additions of IDR 217bn (FY2023), 185bn (FY2024) and 178bn (FY2025) (FS note 13; includes rubber and capitalised immature upkeep); "replanted area monitored by drones" of 940 ha (2020) and 3,843 ha (2023) (SR; cumulative or annual not stated); the SR2025 states a long-term goal "to gradually increase average oil palm yields by accelerating replanting". Planted oil-palm area also shrank: 96,074 ha (FY2020) → 90,798 ha (FY2025) → **89,331 ha (30 Sep 2026)**, with East Kalimantan down 3,548 ha since FY2020; the reasons are not disclosed (FY2024 impairment of IDR 296bn related to the rubber CGU).

## 4. Age-cohort model (RECONSTRUCTED; `valuation/lsip_cohort.py`)

**Reconstruction.** Planting-year areas 1997-2025 are solved by non-negative least squares with a smoothness penalty so that the reported bands (immature = ages 0-3, 4-6, 7-20, >20) for FY2017-23 and the immature area for FY2024-25 are matched; pre-1997 "old stock" is set to match the reported average age. Mean absolute band residual {f0(CS['fit_mean_abs_residual_ha'])} ha, max {f0(CS['fit_max_abs_residual_ha'])} ha (FY2021: 2,228 ha of immature area disappeared with the East Kalimantan contraction — the identities cannot hold exactly). Old stock mean age in 2023: {CS['old_stock_mean_age_2023']:.1f} years.

**Dynamics.** A(a+1, t+1) = A(a, t) − R(a, t); A(0, t+1) = hectares replanted in t; FFB(t) = Σ_a A(a, t)·y(a)·k(cohort). Replanting removes the oldest palms first; cleared blocks lose their full-year output; replanted blocks enter at age 0 on improved material (k × 1.15, ANALYST).

**Yield curve.** A literature-shaped standard curve (ANALYST, shape referenced to S-078) scaled to LSIP by k fitted on FY2017-25 nucleus FFB. **This is not an empirically validated LSIP age-yield relationship**: LSIP does not disclose yield by age. k fell from ~0.8 (FY2018-19) to ~0.66 (FY2021-25); the base uses the recent mean k = {CS['k_hist_2021_2025_base']:.3f}.

{cal}

**Uncertainty propagation.** 36 feasible reconstructions (smoothing 0.05/0.5/5 × average age 18/19 × old-stock shape front/spread × post-18 decline 0.75/1.0/1.25) × 4 scenarios:

{ensT}

## 5. Replanting scenarios (base price case; value per share at 80% cash credit)

{scen_table()}

Scenario definitions: A continues the reconstructed pace ({f0(CS['hist_planting_rate_2017_2025_ha'])} ha/yr); B ramps to the sustainable rate ({f0(CS['sustainable_rate_ha_25y'])} ha/yr = planted area / 25-year economic life, the accounting life of bearer plants) by 2028; C defers to 800 ha/yr to 2030; D replants 5,000 ha/yr oldest-first until no palms older than 25 remain, then the sustainable rate. Terminal values use each scenario's own long-run planting rate as a steady state (uniform ages over the implied cycle; productivity does not persist without reinvestment).

Readings: (1) under A and C, nucleus FFB declines ~1.5-2% a year to the mid-2030s; (2) B and D depress output and free cash flow for 8-10 years before recovering — peak funding is in 2030-2035 (D: replanting capex ~IDR {f0(det['D_intensive|base']['cx_rep']['2035'])}bn in 2035, FCFF trough ~IDR {f0(det['D_intensive|base']['fcff']['2030'])}bn) and is easily funded from cash; (3) at LSIP's current productivity, replanting earns little more than the cost of equity ({pc1(ke)}): B adds IDR {f0(av['B_minus_A_ops_per_share'])}/share, D {f0(av['D_minus_A_ops_per_share'])}, while deferral (C) destroys IDR {f0(-av['C_minus_A_ops_per_share'])}/share. The steady-state replacement rate is the right long-run policy (higher value, avoids the post-2035 cliff) but not a reason to front-load replanting (D).

## 6. Cash and capital allocation

### 6.1 What is genuinely surplus (30 Sep 2026)

{cashT}

Replanting is funded inside the operating DCF (FCFF after replanting capex), so no replanting reserve is deducted from cash — the same cost is never subtracted twice. Interest income is excluded from FCFF and cash is added once in the bridge.

### 6.2 History of cash accumulation and distribution (REPORTED / DERIVED)

{crT}

- Cash rose from IDR 1.96tn (FY2020) to {f0(FIN.loc['9M26','cash_end']/1000)}bn (9M26) because only ~{pc(CR.dividends_paid_bn.sum()/CR.fcf_bn.sum())} of FY2020-25 free cash flow was paid out. Deposits yield 2-4.4% pre-tax (3.15-6.50% quoted ranges), i.e. ~{pc1(0.04*0.8)} after the 20% final tax — far below a {pc1(ke)} cost of equity. Every year of retention at 30% payout transfers value away from minorities.
- **Buyback:** authorised up to IDR 750bn (26 Oct-31 Dec 2026, POJK 13/2023 market-volatility route, no shareholder vote). **Execution is UNVERIFIED** (no report on the company site at 25 Nov 2026; IDX blocked from this environment). If fully executed at IDR {f0(PX)}, value per remaining share rises by about IDR {f0(S['bb']['750.0']['ps'] - S['bb']['0.0']['ps'])} (buying below intrinsic value). At a 20% participation in a median IDR {f1(rk['LSIP']['median_daily_value_6m_bn'])}bn daily value, 750bn would take ~{f0(rk['LSIP']['days_to_trade_750bn_at_20pct_adv'])} trading days — it cannot be completed in the window; partial execution is the realistic best case. LSIP cancelled treasury shares in Sep 2024 (precedent).
- **Related party:** Bank Ina Perdana (Salim group) held IDR {f0(RPC.loc['FY2025','bank_ina_perdana']/1000)}bn ({pc(RPC.loc['FY2025','share'])} of cash) at FY2025, down to {f0(RPC.loc['9M26','bank_ina_perdana']/1000)}bn ({pc(RPC.loc['9M26','share'])}) at 9M26. A 100% haircut on this balance costs IDR {f0(S['rph']['0.0']['ps'] - S['rph']['1.0']['ps'])}/share.
- **Parent incentives:** SIMP (59.51%) is LSIP's main customer ({pc(0.6326)} of FY2025 revenue). The cash is useful to the group as liquidity; minorities only receive it through dividends or buybacks. This is the structural reason the market credits only part of it.

### 6.3 Value of alternative capital-allocation policies (base, scenario A)

| Policy | Minority value per share (DDM unless stated) |
|---|---|
| Status quo: 30% payout, cash retained at deposit yields | IDR {f0(S['pay']['0.3']['ddm_ps'])} |
| 50% payout | IDR {f0(S['pay']['0.5']['ddm_ps'])} |
| 70% payout | IDR {f0(S['pay']['0.7']['ddm_ps'])} |
| 100% payout of profit | IDR {f0(S['pay']['1.0']['ddm_ps'])} |
| Intrinsic (DCF + 100% of surplus cash, as if fully distributable) | IDR {f0(j('A_historical','base',1.0,'ps'))} |
| Market price | IDR {f0(PX)} |

The DDM gap (IDR {f0(rt['trapped'])}/share between DCF + surplus cash at 80% credit and the 30%-payout DDM) measures value that exists in the company but does not reach minority holders under the current policy.

## 7. Earnings: near-term catalysts vs structural productivity

### 7.1 Q4 2026 nowcast v2 (EXPLORATORY; v1 preserved)

{q4T}

v2 changes only two parameters, each tied to new evidence: Q4 is the seasonal peak (Q4'25 nucleus FFB 1.16× Q3'25 — one year of quarterly data, weak evidence) and the November CPO reference price fell ~2% vs the Q3 average. Consensus-implied Q4 is IDR {f0(consq4)}bn (FY26 consensus {f0(cons26)}bn, 5 analysts, S-036). **The Q4 beat, if any, is a timing item** (inventory release and seasonality), not structural.

### 7.2 Forecasts (scenario A, base price case; IDR bn)

{P}

FY2027E profit: bear {f0(ni27['bear'])} / base **{f0(ni27['base'])}** / bull {f0(ni27['bull'])} vs consensus {f0(cons27)} (base {pc(ni27['base']/cons27-1)}). Our base is well below consensus because it combines a normalised (cohort-model) production path — FY2026's weather-assisted recovery to ~1,180kt is not extrapolated; FY2027E {f0(det['A_historical|base']['ffb_n']['2027'])}kt — with a lower realised price (IDR 14,600/kg vs ~15,300 in 9M26). **This is the main near-term risk to the share price:** consensus FY2027 EPS of {f0(cons27*1000/SH)} looks too high on our numbers. The model has no out-of-sample record; treat the gap as a hypothesis to be tested by FY2026-27 results.

## 8. Integrated model (`outputs/LSIP_model_valuation.xlsx`)

Sheets: Cover, Inputs (blue inputs with sources; selectors for scenario and price case), Cohort (production by scenario from the Python model, including each scenario's steady state), Model (FY2026E-FY2050E income statement, cash flow, balance sheet and balance check; FY2051 steady state), Valuation (FCFF DCF, equity bridge, DDM, multiples, 12-month target and entry price), Historical (audited FY2020-9M26 and operating data). FY2026E reconciles to 9M26 reported profit plus the Q4 v2 base. {R['formulas']:,} formulas; **0 evaluation errors and a zero balance check in every year under all 12 scenario × price-case combinations**. Limitation: built with openpyxl and verified with the repository's own evaluator (`valuation/xlsx_eval.py`); it has not been recalculated in Excel or LibreOffice (unavailable in this environment), so open it with automatic calculation on. The balance sheet is condensed (cash, working capital, net fixed assets incl. bearer plants, other net assets held at the FY2025 plug, employee benefits, equity); biological assets (produce on trees) are inside working capital, and fair-value changes are not forecast.

## 9. Valuation

Cost of equity {pc1(ke)} = 10-year SBN 7.74% (S-052) + 0.9 × 6.0% ERP (no debt; WACC = ke). Valuation date 31 Dec 2026.

| Method (scenario A, base price) | IDR/share |
|---|---|
| 1. FCFF operating DCF + adjusted surplus cash (80% credit) | {f0(base['ps'])} |
| 6. Cash-adjusted operating value: operations only | {f0(base['ops_ps'])} |
| 3. SOTP: operations {f0(base['ops_ps'])} + surplus cash at 100% {f0(j('A_historical','base',1.0,'cash_ps'))} − related-party haircut 0 | {f0(j('A_historical','base',1.0,'ps'))} |
| 2. DDM (30% payout) | {f0(base['ddm_ps'])} |
| 4. Relative: P/E FY2027E at current price | {rt['pe27']:.1f}x (palm peers: see `palm_peers_snapshot.csv`; TAPG {T['price']/(T['cases']['base']['np_sustainable_bn']*1000/T['shares_mn']):.1f}x sustainable) |
| 4. Relative: market EV/EBITDA FY2027E (EV ex surplus cash) | {rt['ev_ebitda27']:.1f}x |
| 4. Relative: EV per planted ha (market) | IDR {f0(evha['LSIP_cash80'])}m (TAPG {f0(evha['TAPG'])}m) |
| 5. Reverse DCF | see §10 |

### 9.1 Scenario × price × cash credit (value per share; 12-month return)

| Scenario | Price case | 60% credit | 80% credit | 100% credit |
|---|---|---|---|---|
""" + "\n".join(f"| {SCL[s]} | {c} | {f0(j(s,c,0.6,'ps'))} ({pc(j(s,c,0.6,'tr12'))}) | {f0(j(s,c,0.8,'ps'))} ({pc(j(s,c,0.8,'tr12'))}) | {f0(j(s,c,1.0,'ps'))} ({pc(j(s,c,1.0,'tr12'))}) |"
                 for s in SC for c in ("bear", "base", "bull")) + f"""

Price cases (realised CPO, IDR/kg): FY2027 12,500 / 14,600 / 16,500; long-run (FY2029, then +2.5%/yr nominal) 12,000 / 14,000 / 16,500 (ANALYST). Terminal growth 2.5% nominal = 0% real; the terminal value is a small part of value (PV IDR {f0(rt['pv_tv'])}bn of an operating EV of {f0(rt['ev'])}bn).

### 9.2 Sensitivities (scenario A, base price, 80% credit)

{SENS}

The value is most sensitive to the long-run CPO price, FFB yield and the rupiah (each ±10% moves value by IDR 300-400/share), then to cash credit; replanting cost, fertiliser intensity, ke and terminal productivity matter far less.

## 10. Reverse valuation: what the price implies

At IDR {f0(PX)} (scenario A unless stated):
- **Long-run realised CPO price:** IDR {f0(V['implied_long_run_cpo_full_cash_credit'])}/kg with 100% cash credit, IDR {f0(V['implied_long_run_cpo_idr_kg'])}/kg at 80% (base 14,000; FY2025 realised ~14,600; 9M26 ~15,300).
- **Cash realisation:** {pc(mkt_credit)} of surplus cash at our base operations; at bear operations the price needs {pc(V['implied_cash_credit_bear_ops'])} credit — i.e. the market is either pricing a bear commodity case with full cash credit or a base case with a governance discount.
- **Sustainable FFB yield:** a {pc(V['implied_yield_multiplier']-1)} change to the cohort path (k ≈ {CS['k_hist_2021_2025_base']*V['implied_yield_multiplier']:.2f}) — i.e. a further decline in productivity.
- **Replanting cost:** IDR {f0(V['implied_replant_cost_m_per_ha'])}m/ha (base 100) or fertiliser/upkeep intensity {V['implied_fert_multiplier']:.2f}× base — implausible on their own.
- **Cost of equity:** {pc1(V['implied_ke'])} (beta {V['implied_cost_of_equity_beta']:.2f}).
- **Payout:** the DDM reaches the price only at a {pc(V['implied_payout_ddm'])} payout of profit.

**Is the discount justified?** Partly. The market's discount relative to TAPG (IDR {f0(evha['LSIP_cash80'])}m vs {f0(evha['TAPG'])}m EV per planted ha) is larger than the operating gap (operating profit per mature ha {f1(T['op_profit_per_mature_ha_fy2025_idr_m']['LSIP'])}m vs {f1(T['op_profit_per_mature_ha_fy2025_idr_m']['TAPG'])}m). The ageing estate explains part of it (age-mix yield deficit {pc(av['age_mix_yield_deficit_vs_25y_steady_state'])} vs a 25-year steady state; a 10% yield change is worth IDR {f0(av['value_of_10pct_yield_per_share'])}/share gross), but correcting it costs nearly what it earns. The larger, persistent component is minority access to cash.

Historical valuation dispersion (year-end; DERIVED):

{vhT}

## 11. LSIP versus TAPG (like-for-like; FY2025)

{COMP}

Definitions: LSIP operating data are nucleus; TAPG's are group-wide incl. associates (TAPG's own scope), so TAPG yield and age shares are not strictly like-for-like. ROIC uses book equity less cash, which flatters LSIP's old, depreciated estate. TAPG's value uses a single-stage perpetuity on a 6-point profit-on-price regression (R² {T['regression']['r2']:.2f}) with a 10% ageing haircut and 90% cash conversion (`valuation/lsip_tapg_compare.py`); it is a price-deck consistency check, not a TAPG target price.

**Is TAPG's premium justified?** By plantation economics, largely yes: TAPG has a prime-age estate ({pc(TC[(TC.company=='TAPG')&(TC.fy==2025)].a7_20_share.iloc[0])} aged 7-20 years), {f1(yg['tapg_actual'])} t/ha yields and pays out more than its free cash flow. By price, no: at IDR {f0(T['price'])} TAPG capitalises about IDR {f0(T['implied_np_at_price'])}bn of sustainable profit (FY2025: 3,702bn), so its base return on our price deck is {pc(T['cases']['base']['tr12'])}. Of LSIP's discount, the age mix accounts for roughly a third of the yield gap and little of the value gap; the rest is productivity and capital allocation.

## 12. Quantitative risk and entry

| Metric | LSIP | TAPG |
|---|---|---|
| Annualised volatility, 5y / 1y | {pc(rk['LSIP']['ann_vol_daily_5y'])} / {pc(rk['LSIP']['ann_vol_daily_1y'])} | {pc(rk['TAPG']['ann_vol_daily_5y'])} / {pc(rk['TAPG']['ann_vol_daily_1y'])} |
| Max drawdown (date) | {pc(rk['LSIP']['max_drawdown_since_2015'])} ({rk['LSIP']['max_drawdown_date']}) | {pc(rk['TAPG']['max_drawdown_since_2015'])} ({rk['TAPG']['max_drawdown_date']}) |
| Monthly return 5th / 1st percentile (2016+) | {pc(rk['LSIP']['monthly_ret_p5'])} / {pc(rk['LSIP']['monthly_ret_p1'])} | {pc(rk['TAPG']['monthly_ret_p5'])} / {pc(rk['TAPG']['monthly_ret_p1'])} |
| Worst 12 months; share of negative 12m windows | {pc(rk['LSIP']['worst_12m'])}; {pc(rk['LSIP']['share_negative_12m'])} | {pc(rk['TAPG']['worst_12m'])}; {pc(rk['TAPG']['share_negative_12m'])} |
| Market beta (t), sector beta (t), weekly 5y HAC | {rk['LSIP']['beta_mkt_5y_weekly']:.2f} ({rk['LSIP']['beta_mkt_t']:.1f}), {rk['LSIP']['beta_sector_5y_weekly']:.2f} ({rk['LSIP']['beta_sector_t']:.1f}) | {rk['TAPG']['beta_mkt_5y_weekly']:.2f} ({rk['TAPG']['beta_mkt_t']:.1f}), {rk['TAPG']['beta_sector_5y_weekly']:.2f} ({rk['TAPG']['beta_sector_t']:.1f}) |
| CPO beta (monthly, IDR CPO, controlling for IHSG) (t) | {rk['LSIP']['beta_cpo_idr_monthly']:.2f} ({rk['LSIP']['beta_cpo_t']:.1f}) | {rk['TAPG']['beta_cpo_idr_monthly']:.2f} ({rk['TAPG']['beta_cpo_t']:.1f}) |
| Liquidity: median daily value 6m | IDR {f1(rk['LSIP']['median_daily_value_6m_bn'])}bn (p10 {f1(rk['LSIP']['p10_daily_value_6m_bn'])}bn) | see Phase I |
| Weekly return correlation LSIP-TAPG | {rk['LSIP']['corr_LSIP_TAPG_weekly_5y']:.2f} | |

Price reactions around dated events (market-adjusted, descriptive, n = 9):

{evT}

**Hurdle (open item A6 / D-030).** The 17.5% hurdle was set as ke 12.5% + 5pp when the 10y SBN yielded ~6.2%; it now yields 7.74%, so an unchanged hurdle implies an ERP of only {pc1(RK['hurdle']['erp_implied_now_if_unchanged'])}. We **propose** restating it as ke + 5pp = {pc1(HUR2)} (A-049, documented separately; not adopted here). The recommendation is the same under both.

**Entry (valuation-based, not statistically validated):** base value at 80% credit → IDR {f0(base['entry'])}; base value robust to a 60% credit → **IDR {f0(ENTRY_BUY)}** at 17.5% (IDR {f0(ENTRY_BUY2)} at {pc1(HUR2)}). We do not estimate a probability of reaching the target price.

**Stop-loss (risk-budget-based, not quantitatively validated):** for a position sized at a 1% portfolio risk budget, a review/exit level ~25% below entry corresponds to a 4% position (LSIP's 5th-percentile monthly return is {pc(rk['LSIP']['monthly_ret_p5'])}; the 2020 drawdown was {pc(rk['LSIP']['max_drawdown_since_2015'])}). Thesis-based exits (§13) take precedence over price-based ones.

## 13. Recommendation detail

- **Rating: {VERDICT}.** Base fair value IDR {f0(base['ps'])} (bear {f0(bear['ps'])}, bull {f0(bull['ps'])}); 12-month target IDR {f0(base['tp12'])}; expected dividend IDR {f0(DPS27)} ({pc1(DPS27/PX)}); expected total return {pc(base['tr12'])} in the base case but only {pc(TR_at_mkt_credit)} if the market's current cash discount persists, and {pc(j('A_historical','bear',0.6,'tr12'))} in the joint downside (bear CPO, 60% credit).
- **Why not BUY now:** (1) the return depends on a governance outcome minorities cannot influence (cash credit ≥ {pc(BE)}); (2) our FY2027E profit is {pc(ni27['base']/cons27-1)} vs consensus — negative revisions are more likely than positive; (3) the ageing/productivity trend is down (k 0.80 → 0.66) and disclosure of the age profile has stopped; (4) buyback execution is unverified.
- **Why not SELL:** the bear case with 80-100% cash credit is IDR {f0(bear['ps'])}-{f0(j('A_historical','bear',1.0,'ps'))}, close to the price; surplus cash is {pc(surplus*1000/SH/PX)} of the market value; and LSIP ranks above TAPG on risk-adjusted expected return.
- **Take-profit framework:** trim above IDR {f0(base['ps'])} (base value, 80% credit); exit above IDR {f0(j('A_historical','base',1.0,'ps'))} (base value with full cash credit) unless payout policy has changed.
- **Risk management:** treat LSIP and TAPG as one palm risk bucket (correlation {rk['LSIP']['corr_LSIP_TAPG_weekly_5y']:.2f}, sector beta ~1); liquidity caps a position at roughly 20% of ~IDR {f1(rk['LSIP']['median_daily_value_6m_bn'])}bn daily value.
- **Position sizing (hypothetical diversified IDR equity portfolio):** 0% now; up to 2-3% at ≤ IDR {f0(ENTRY_BUY)}; up to 4% after verified capital return. No investor-specific sizing.
- **Upgrade to BUY if:** price ≤ IDR {f0(ENTRY_BUY)}; or an IDX report shows ≥ IDR 375bn of buyback executed; or the FY2026 payout (AGM ~Jun 2027) is ≥ 50% or includes a special dividend; or LSIP publishes an age profile and replanting plan consistent with scenario B.
- **Downgrade / thesis invalidation:** payout below 30% or new related-party placements raising Bank Ina Perdana above 20% of cash; cash used for a related-party acquisition; FY2026 nucleus FFB below 1,130kt or 9M27 yields below FY2025 levels with fertiliser restored (productivity decline is structural); long-run CPO expectations below IDR 12,000/kg.

## 14. Catalysts (Exhibit 13)

| Date (expected) | Event | What would change |
|---|---|---|
| 31 Dec 2026 | Buyback window closes | Execution size and price |
| Early Jan 2027 | IDX buyback report (C-019) | Evidence of capital return |
| ~26 Feb 2027 | FY2026 results (C-020) | Q4 vs {f0(consq4)}bn consensus-implied; inventory release |
| ~30 Apr 2027 | AR/SR 2026 | Whether an age profile / replanting plan is disclosed |
| ~Jun 2027 | AGM payout (C-021) | Payout ≥ 50% would move the cash credit |
| Jul-Oct 2027 | H1 / 9M 2027 | El Niño lag on FFB; fertiliser normalisation |

## 15. Data gaps, assumptions and uncertainties

| Area | Gap / assumption | Effect |
|---|---|---|
| Age profile FY2024-26 | Not disclosed; reconstructed | Cohort model starting state |
| Replanting hectares, targets, capex | Not disclosed; reconstructed from bands and immature additions | Historical rate ±~50 ha/yr across the ensemble; cost per ha calibrated (IDR 100m/ha, ANALYST) |
| Yield by age | Not disclosed; standard curve × k (ANALYST) | Production path; tested by the decline and k ensemble |
| Fertiliser | Combined with upkeep in the COGS note | Catch-up hypothesis unverifiable |
| Estate-level productivity | Regional area only | No estate ranking for scenario D |
| Land changes | Oil palm −1,467 ha in 9M26; reasons undisclosed | Treated as disposal of the oldest area |
| Buyback execution | Unverified | Base assumes 0 executed |
| Consensus | Forward snapshots only (from 24 Nov 2026); 5 analysts | No historical expectations analysis |
| Financial statements FY2018-19 | Only five-year highlights (ARs before 2021 not on the company site) | History table starts FY2020 for full statements |
| Workbook | No Excel/LibreOffice recalculation; independent evaluator only | Open with automatic calculation |
| TAPG valuation | Simple perpetuity, regression n = 6, group-wide scope | Relative comparison only |
| Models | No out-of-sample validation of the LSIP earnings model or Q4 nowcast | Treat forecasts as hypotheses |

Integrity: ITMG C1/I1 prospective runs and all registered experiments are untouched (`tests/test_phase17.py` checks the frozen files); no factor mining; R2/R3 not run; previous LSIP files preserved.

_Sources: S-002, S-036, S-046–S-052, S-076–S-078 (data/SOURCE_REGISTER.csv); assumptions A-049–A-057 (context/ASSUMPTIONS.md); decision D-047._
"""


def summary() -> str:
    return f"""# LSIP — Executive Investment Summary ({D})

**{VERDICT}** · Price IDR {f0(PX)} · Fair value IDR {f0(bear['ps'])} / **{f0(base['ps'])}** / {f0(bull['ps'])} (bear/base/bull) · 12m target IDR {f0(base['tp12'])} · BUY at ≤ IDR {f0(ENTRY_BUY)} or on verified capital return.

- **Question:** is LSIP's IDR {f0(FIN.loc['9M26','cash_end']/1000)}bn cash genuinely excess, or needed to regenerate an ageing estate? **Answer: it is genuinely excess** — even the sustainable replanting programme (scenario B, ~{f0(CS['sustainable_rate_ha_25y'])} ha/yr) needs IDR {f0(det['B_accelerated|base']['cx_rep']['2030'])}-{f0(det['B_accelerated|base']['cx_rep']['2040'])}bn of replanting capex a year (nominal, 2030-2040), fully funded from operating cash flow. Distributable surplus is IDR {f0(surplus)}bn ({f0(surplus*1000/SH)}/share). The problem is access, not need.
- **Ageing is real but not the main value driver.** >20-year palms were {pc(a23.gt20_share)} of the estate at FY2023 (last disclosure); replanting runs at ~{f0(CS['hist_planting_rate_2017_2025_ha'])} ha/yr vs {f0(CS['sustainable_rate_ha_25y'])} needed. Yields fell to {f1(o25.yield_nucleus_t_ha)} t/ha (TAPG {f1(yg['tapg_actual'])}); age explains ~{pc(yg['gap_due_to_age_mix']/yg['gap_total'])} of the gap. Accelerating replanting adds only ~IDR {f0(av['B_minus_A_ops_per_share'])}/share at LSIP's productivity.
- **Capital allocation is the binding constraint.** 30% payout leaves minorities a cash-flow value of IDR {f0(base['ddm_ps'])}/share vs intrinsic IDR {f0(j('A_historical','base',1.0,'ps'))}; 100% payout would lift it to IDR {f0(S['pay']['1.0']['ddm_ps'])}. The market credits ~{pc(mkt_credit)} of surplus cash at our base operations.
- **Versus TAPG:** LSIP base return {pc(base['tr12'])} vs TAPG {pc(T['cases']['base']['tr12'])}; bear {pc(bear['tr12'])} vs {pc(T['cases']['bear']['tr12'])}. TAPG has far better plantation economics, but its price capitalises ~IDR {f0(T['implied_np_at_price'])}bn of sustainable profit. **LSIP offers the better risk-adjusted return, conditional on cash realisation ≥ ~{pc(BE)}.**
- **Earnings risk:** our FY2027E profit {f0(ni27['base'])}bn is {pc(ni27['base']/cons27-1)} vs consensus {f0(cons27)}bn; Q4 2026E {f0(q4b.q4_np_owners)}bn vs consensus-implied {f0(consq4)}bn (timing item). Unvalidated models.
- **Catalysts:** buyback report (Jan 2027), FY2026 results (Feb 2027), AGM payout (Jun 2027).
- **Invalidation:** payout cut or more related-party deposits; structural yield decline with fertiliser restored; long-run CPO < IDR 12,000/kg.
"""


def ic_memo() -> str:
    return f"""# Investment Committee Memorandum — LSIP ({D})

**To:** Investment Committee · **From:** Research (Phase XVII) · **Subject:** LSIP flagship review — undervaluation or value trap?

## Recommendation
**{VERDICT}.** No position at IDR {f0(PX)}. Pre-approved BUY (2-3% of a hypothetical diversified IDR equity portfolio) at ≤ IDR {f0(ENTRY_BUY)}, or up to 4% after verified capital return (≥ IDR 375bn buyback executed or ≥ 50% payout). LSIP preferred over TAPG on relative value; both remain one palm risk bucket.

## Decision summary
| | Bear | Base | Bull |
|---|---|---|---|
| Fair value/share (80% cash credit, scenario A) | {f0(bear['ps'])} | {f0(base['ps'])} | {f0(bull['ps'])} |
| 12-month total return at IDR {f0(PX)} | {pc(bear['tr12'])} | {pc(base['tr12'])} | {pc(bull['tr12'])} |
| TAPG 12-month return (same price deck) | {pc(T['cases']['bear']['tr12'])} | {pc(T['cases']['base']['tr12'])} | {pc(T['cases']['bull']['tr12'])} |

Hurdle 17.5% (proposed {pc1(HUR2)}, A-049). Base clears it only if minority cash realisation ≥ {pc(BE)}; at the market-implied {pc(mkt_credit)} the base return is {pc(TR_at_mkt_credit)}. Joint downside (bear CPO, 60% credit): {pc(j('A_historical','bear',0.6,'tr12'))}.

## Key judgements for the committee
1. **Cash credit (80% base)** — the single most important assumption. Evidence against full credit: 20-35% payout for six years, SIMP buys 63% of revenue, 8-22% of cash at a Salim-group bank, buyback unverified. Evidence for: zero debt, buyback authorised, treasury shares cancelled in 2024.
2. **Long-run realised CPO IDR 14,000/kg** — below 2025-26 realised (14,600-15,300). The price implies ~{f0(V['implied_long_run_cpo_idr_kg'])}.
3. **Productivity k = {CS['k_hist_2021_2025_base']:.2f} of a standard curve** — assumption scaled to reported FFB; not an LSIP-specific validated curve.
4. **No validated forecasting edge.** LSIP models have no out-of-sample record.

## What we are watching
Buyback report (early Jan 2027) · FY2026 results (~26 Feb 2027) · AR2026 age disclosure (~Apr 2027) · AGM payout (~Jun 2027) · El Niño lag on 2027 FFB.

## Integrity statement
Previous LSIP outputs preserved (Q4 v1, Stage-1 gate, Phase VII decision); ITMG C1/I1 and all registered experiments untouched; no factor mining. Full report: `research/company/LSIP/{D}_LSIP_equity_research.md`; model `outputs/LSIP_model_valuation.xlsx`.
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{D}_LSIP_equity_research.md").write_text(report(), encoding="utf-8")
    (OUT / f"{D}_LSIP_executive_summary.md").write_text(summary(), encoding="utf-8")
    (OUT / f"{D}_LSIP_IC_memo.md").write_text(ic_memo(), encoding="utf-8")
    print("written", D, "verdict", VERDICT, "base", round(base["ps"]), "tr", round(base["tr12"], 3), "BE credit", round(BE, 3), "entry", round(ENTRY_BUY))


if __name__ == "__main__":
    main()
