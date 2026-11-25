"""LSIP vs TAPG on one price deck and one discount rate (Phase XVII).

    python -I -X utf8 valuation/lsip_tapg_compare.py   (after valuation/lsip_model.py and quant/lsip_phase17_analysis.py)

TAPG is valued with a deliberately simple, transparent frame (it is not the subject of a full model in this phase):
  sustainable profit NP(P) from an OLS of TAPG reported profit to owners on its realised CPO price
  (TAPG_statements_extracted.csv, TAPG_operational_extracted.csv; FY2020-25, n = 6, DESCRIPTIVE only),
  x ageing/replanting haircut (TAPG's 7-20 cohort, 87% of area, starts crossing 20 years in the 2030s; ANALYST 0.90)
  x cash conversion 0.90 (TAPG pays out ~100% of profit; ANALYST), capitalised at (ke - g) with the SAME ke and g as
  LSIP, plus net cash (9M26). Price deck = LSIP long-run realised CPO bear/base/bull (12.0k/14.0k/16.5k IDR/kg).
Output: data/reference/research/LSIP_TAPG_valuation.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
REF = ROOT / "data" / "reference"


def main():
    op = pd.read_csv(REF / "TAPG_operational_extracted.csv")
    st = pd.read_csv(REF / "TAPG_statements_extracted.csv")
    asp = op[op.item == "asp_cpo_idr_per_kg"].set_index("fiscal_year").value
    npo = st[(st.item == "profit_attrib_owners") & st.period.str.startswith("FY")].drop_duplicates("period")
    npo = npo.set_index(npo.period.str[2:].astype(int)).value / 1000
    d = pd.concat([asp.rename("p"), npo.rename("np")], axis=1).dropna().sort_index().loc[2020:2025]
    b, a = np.polyfit(d.p, d.np, 1)                       # np = a + b p  (IDR bn per IDR/kg)
    resid = d.np - (a + b * d.p)
    snap = json.loads((RES / "LSIP_market_snapshot.json").read_text(encoding="utf-8"))
    info = snap["tapg_info"]
    px, sh = float(snap["tapg_last_close"]["close"]), info["sharesOutstanding"] / 1e6
    net_cash = (info["totalCash"] - info["totalDebt"]) / 1e9
    V = json.loads((RES / "LSIP_valuation_results.json").read_text())
    ke = 0.0774 + 0.9 * 0.06; g = 0.025; hc, conv = 0.90, 0.90
    risk = json.loads((RES / "LSIP_risk_stats.json").read_text())["risk"]
    out = {"regression": {"intercept_bn": a, "slope_bn_per_idr_kg": b, "n": len(d), "r2": float(1 - (resid ** 2).sum() / ((d.np - d.np.mean()) ** 2).sum()),
                          "data": d.round(1).to_dict("index")},
           "price": px, "shares_mn": sh, "net_cash_bn": net_cash, "ke": ke, "g": g, "haircut": hc, "conversion": conv, "cases": {}}
    for case, P in (("bear", 12000), ("base", 14000), ("bull", 16500)):
        np_lr = a + b * P
        eq = np_lr * hc * conv / (ke - g) + net_cash
        fv = eq * 1000 / sh
        tr = fv * (1 + ke) ** (11 / 12) / px - 1
        out["cases"][case] = {"lr_price": P, "np_sustainable_bn": np_lr, "fv_ps": fv, "tr12": tr, "implied_dividend_yield": np_lr * conv / (px * sh / 1000)}
    # market-implied sustainable profit for TAPG in the same frame
    out["implied_np_at_price"] = (px * sh / 1000 - net_cash) * (ke - g) / (hc * conv)
    out["implied_lr_price"] = (out["implied_np_at_price"] - a) / b
    J = V["joint"]
    lsip = {c: {"fv_ps": J[f"A_historical|{c}|0.8"]["ps"], "tr12": J[f"A_historical|{c}|0.8"]["tr12"]} for c in ("bear", "base", "bull")}
    out["lsip_cases_credit80_scenA"] = lsip
    for t, cases in (("LSIP", lsip), ("TAPG", out["cases"])):
        vol = risk[t]["ann_vol_daily_5y"]
        out[f"{t}_base_return_per_vol"] = cases["base"]["tr12"] / vol
        out[f"{t}_bear_return"] = cases["bear"]["tr12"]
        out[f"{t}_bull_return"] = cases["bull"]["tr12"]
    # --- yield-gap decomposition (standard curve, same assumption for both) and EV per hectare ---
    import sys as _s
    _s.path.insert(0, str(ROOT / "valuation"))
    import lsip_cohort as LC
    yc = LC.yield_curve()
    band = {"a4_6": yc[[5, 6, 7]].mean(), "a7_20": yc[np.arange(8, 22)].mean(), "gt20": yc[np.arange(22, 30)].mean()}
    g = pd.read_csv(REF / "TAPG_scope_groupwide.csv").pivot_table(index="item", columns="period", values="value")["FY2025"]
    t_pot = (g["age_4_6_ha_nucleus"] * band["a4_6"] + g["age_7_20_ha_nucleus"] * band["a7_20"] + g["age_gt20_ha_nucleus"] * band["gt20"]) /         (g["age_4_6_ha_nucleus"] + g["age_7_20_ha_nucleus"] + g["age_gt20_ha_nucleus"])
    cal = pd.read_csv(RES / "LSIP_cohort_calibration.csv").set_index("year")
    ops = pd.read_csv(RES / "LSIP_operational_annual.csv", index_col=0)
    l_pot = cal.loc[2025, "standard_curve_ffb_kt"] * 1000 / ops.loc["FY2025", "op_mature"]
    l_act, t_act = ops.loc["FY2025", "yield_nucleus_t_ha"], g["avg_ffb_yield"]
    out["yield_gap_fy2025"] = {"lsip_actual": l_act, "tapg_actual": t_act, "lsip_standard_potential_for_age_mix": l_pot,
                               "tapg_standard_potential_for_age_mix": t_pot, "gap_total": t_act - l_act, "gap_due_to_age_mix": t_pot - l_pot,
                               "gap_due_to_productivity_factor": (t_act - l_act) - (t_pot - l_pot), "k_lsip": l_act / l_pot, "k_tapg": t_act / t_pot,
                               "note": "TAPG age bands and yield are group-wide incl. associates; LSIP is nucleus. Standard curve is an assumption."}
    lp = V["price"]; lsh = 6819.963965
    cashd = pd.read_csv(RES / "LSIP_cash_decomposition.csv")
    surplus = float(cashd.loc[cashd.item == "Distributable surplus cash (before buyback)", "idr_bn"].iloc[0])
    debt_like = 552.106 + 208.8
    ev_l = {c: (lp * lsh / 1000 - c * surplus + debt_like) for c in (1.0, 0.8)}
    ev_t = px * sh / 1000 - net_cash
    out["ev_per_planted_ha_idr_m"] = {"LSIP_cash100": ev_l[1.0] * 1000 / 89331, "LSIP_cash80": ev_l[0.8] * 1000 / 89331,
                                      "TAPG": ev_t * 1000 / g["age_total_ha_nucleus"],
                                      "LSIP_model_base_ops": V["joint"]["A_historical|base|0.8"]["ops_ps"] * lsh / 1000 * 1000 / 89331}
    tc = pd.read_csv(RES / "LSIP_TAPG_comparison.csv").set_index(["company", "fy"])
    out["op_profit_per_mature_ha_fy2025_idr_m"] = {c: tc.loc[(c, 2025), "operating_profit_bn"] * 1000 / tc.loc[(c, 2025), "mature_ha"] for c in ("LSIP", "TAPG")}
    out["aging_value"] = {"B_minus_A_ops_per_share": V["joint"]["B_accelerated|base|0.8"]["ops_ps"] - V["joint"]["A_historical|base|0.8"]["ops_ps"],
                          "D_minus_A_ops_per_share": V["joint"]["D_intensive|base|0.8"]["ops_ps"] - V["joint"]["A_historical|base|0.8"]["ops_ps"],
                          "C_minus_A_ops_per_share": V["joint"]["C_deferred|base|0.8"]["ops_ps"] - V["joint"]["A_historical|base|0.8"]["ops_ps"],
                          "value_of_10pct_yield_per_share": V["sensitivity"]["yld"]["1.1"]["ps"] - V["sensitivity"]["yld"]["1.0"]["ps"],
                          "age_mix_yield_deficit_vs_25y_steady_state": 1 - l_pot / float(yc[np.arange(4, 26)].mean())}
    out["note"] = ("TAPG frame is a single-stage perpetuity on a 5-point regression; it is a like-for-like price-deck check, not "
                   "a TAPG target price. Earlier TAPG work (Phases II-V, reverse_valuation.md) is unchanged.")
    (RES / "LSIP_TAPG_valuation.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
