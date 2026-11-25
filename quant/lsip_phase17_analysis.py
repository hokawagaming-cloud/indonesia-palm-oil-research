"""Phase XVII analytics for LSIP (run BEFORE valuation/lsip_model.py, which reads the Q4 v2 nowcast).

    python -I -X utf8 quant/lsip_phase17_analysis.py

1. Q4 2026 nowcast v2 (the Stage-1 v1 nowcast is preserved unchanged in LSIP_q4_2026_nowcast.csv).
2. Audit of previous LSIP research figures against primary disclosures.
3. Cash decomposition (operating needs vs distributable surplus) and capital-return history.
4. Quantitative risk: volatility, drawdown, downside distribution, liquidity, market / sector / CPO beta (HAC),
   valuation dispersion (year-end P/E, P/B, EV/NP), price reactions around results and corporate actions.
5. LSIP vs TAPG like-for-like operating comparison (FY2021-FY2025).
Outputs: data/reference/research/LSIP_q4_2026_nowcast_v2.csv, LSIP_prior_audit.csv, LSIP_cash_decomposition.csv,
         LSIP_risk_stats.json, LSIP_event_reactions.csv, LSIP_valuation_history.csv, LSIP_TAPG_comparison.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
RAW = ROOT / "data" / "raw" / "ohlcv"
sys.path.insert(0, str(ROOT / "quant"))
from lsip_stage1 import CUM, quarters  # noqa: E402
from stats_utils import ols_nw  # noqa: E402

FIN = pd.read_csv(RES / "LSIP_financials_annual.csv", index_col=0)
OPS = pd.read_csv(RES / "LSIP_operational_annual.csv", index_col=0)
COGS = pd.read_csv(RES / "LSIP_cogs_breakdown.csv", index_col=0)
RPC = pd.read_csv(RES / "LSIP_related_party_cash.csv", index_col=0)
SNAP = json.loads((RES / "LSIP_market_snapshot.json").read_text(encoding="utf-8"))
PRICE = float(SNAP["lsip_last_close"]["close"])
SHARES = 6819.963965


def q4_v2() -> pd.DataFrame:
    """Same mechanics as Stage-1 q4_nowcast (Q3 base, inventory release, fertiliser catch-up) with parameters
    updated for evidence not used in v1:
      - seasonality: Q4 has been LSIP's peak nucleus-FFB quarter (Q4'25 341kt = 1.16x Q3'25 293kt; Highlights 9M26).
        v1 assumed 0.85/0.95/1.00x Q3. v2: 0.95/1.05/1.15x (only ONE year of quarterly history: weak evidence).
      - price: Nov-26 CPO reference price 978.9 USD/t vs Q3 average 1,001.6 (-2%) and Oct 1,042; WB CPO Oct 1,120 vs
        Q3 avg 1,148 (-2.4%). v2: -8% / -3% / +1% vs Q3 realised.
      - inventory release and fertiliser catch-up unchanged from v1 (no new evidence).
    """
    q3 = quarters().loc["Q3 2026"]
    fg_build = CUM["9M 2026"]["fg_close"] - CUM["H1 2026"]["fg_close"]
    S = {"bear": dict(vol=0.95, price=-0.08, release=0.0, upkeep_catchup=120, other=40, fv=-30),
         "base": dict(vol=1.05, price=-0.03, release=0.5, upkeep_catchup=60, other=60, fv=0),
         "bull": dict(vol=1.15, price=0.01, release=1.0, upkeep_catchup=20, other=80, fv=20)}
    rows = []
    markup = q3.revenue / q3.prod_cost
    share_built = fg_build / q3.prod_cost
    for k, s in S.items():
        rev = q3.revenue * s["vol"] * (1 + s["price"]) * (1 - share_built) / (1 - share_built) * (1 - share_built) \
            + s["release"] * fg_build * markup * (1 + s["price"])
        prod_cost = q3.prod_cost * s["vol"] + s["upkeep_catchup"]
        cogs = prod_cost * (1 - share_built) + s["release"] * fg_build
        gp = rev - cogs
        pbt = gp + s["fv"] + q3.selling + q3.ga + s["other"] + q3.fin_inc
        np_ = pbt * (1 - 0.169)
        rows.append({"scenario": k, **s, "revenue": rev, "cogs": cogs, "gross_profit": gp, "pbt": pbt, "q4_np_owners": np_,
                     "fy26_np_owners": CUM["9M 2026"]["np_owners"] + np_})
    D = pd.DataFrame(rows).set_index("scenario")
    cons = pd.read_csv(ROOT / "data" / "reference" / "consensus_history.csv")
    c = cons[(cons.ticker == "LSIP") & (cons.fy == "FY26")].sort_values("retrieved").iloc[-1]
    D["consensus_fy26_np"] = c.eps_avg * SHARES / 1000
    D["consensus_implied_q4"] = D.consensus_fy26_np - CUM["9M 2026"]["np_owners"]
    D.to_csv(RES / "LSIP_q4_2026_nowcast_v2.csv", float_format="%.2f")
    return D


def cash_decomposition() -> pd.DataFrame:
    f = FIN.loc["9M26"] / 1000
    c9 = COGS.loc["9M26"]
    cash_cost_9m = (c9.total_production_cost - c9.depreciation) / 1000 + (-f.selling - f.ga)
    monthly = cash_cost_9m / 9
    rows = [
        ("Cash and equivalents, 30 Sep 2026", f.cash_end, "9M26 FS"),
        ("  of which at related-party bank (Bank Ina Perdana, Salim group)", RPC.loc["9M26", "bank_ina_perdana"] / 1000, "9M26 FS note 5"),
        ("Restricted cash", 0.0, "none disclosed in cash note"),
        ("Minimum operating cash (~2 months of cash costs)", -2 * monthly, f"9M26 cash costs {cash_cost_9m:,.0f}bn / 9 x 2"),
        ("Seasonal working-capital buffer (finished-goods swing)", -300.0, "FG 421 -> 593bn in 9M26; Q3 build 221bn"),
        ("Committed capex in progress (CIP balance) - memo", 0.0, "FY25 CIP 102bn is inside forecast maintenance capex (DCF); not deducted twice"),
        ("Employee benefits liability (debt-like)", -f.employee_benefits_lt, "9M26 FS"),
        ("Taxes payable (FY25 level)", -208.8, "FY25 FS"),
        ("Replanting funding", 0.0, "inside the DCF (FCFF); NOT reserved here to avoid double counting"),
    ]
    D = pd.DataFrame(rows, columns=["item", "idr_bn", "basis"])
    surplus = D.idr_bn.sum() - D.idr_bn.iloc[1]
    D.loc[len(D)] = ["Distributable surplus cash (before buyback)", surplus, "sum of the above (related-party line is a memo)"]
    D.loc[len(D)] = ["  per share (IDR)", surplus * 1000 / SHARES, f"{SHARES:,.1f}mn shares"]
    D.loc[len(D)] = ["  as % of share price", surplus * 1000 / SHARES / PRICE, f"price {PRICE:,.0f}"]
    D.loc[len(D)] = ["Buyback authorised (Oct-Dec 2026), max", -750.0, "disclosure 23 Oct 2026; execution UNVERIFIED"]
    D.to_csv(RES / "LSIP_cash_decomposition.csv", index=False, float_format="%.2f")
    return D


def capital_return_history() -> pd.DataFrame:
    dps = {2019: 15, 2020: 20, 2021: 51, 2022: 53, 2023: 39, 2024: 65, 2025: 83}   # FY -> Rp/share (company dividends page / Yahoo)
    rows = []
    for fy in range(2020, 2026):
        p = f"FY{fy}"
        npo = FIN.loc[p, "profit"] / 1000
        rows.append({"fy": fy, "profit_bn": npo, "dps_declared": dps[fy], "dividend_bn": dps[fy] * SHARES / 1000,
                     "payout": dps[fy] * SHARES / 1000 / npo, "cash_end_bn": FIN.loc[p, "cash_end"] / 1000,
                     "finance_income_bn": FIN.loc[p, "finance_income"] / 1000,
                     "cash_yield": FIN.loc[p, "finance_income"] / ((FIN.loc[p, "cash_begin"] + FIN.loc[p, "cash_end"]) / 2),
                     "cfo_bn": FIN.loc[p, "cfo"] / 1000, "capex_bn": -FIN.loc[p, "capex"] / 1000,
                     "fcf_bn": (FIN.loc[p, "cfo"] + FIN.loc[p, "capex"]) / 1000, "dividends_paid_bn": -FIN.loc[p, "dividends_paid"] / 1000,
                     "related_party_cash_bn": RPC.loc[p, "bank_ina_perdana"] / 1000 if p in RPC.index else np.nan})
    D = pd.DataFrame(rows)
    D["retained_fcf_bn"] = D.fcf_bn - D.dividends_paid_bn
    D.to_csv(RES / "LSIP_capital_return_history.csv", index=False, float_format="%.4f")
    return D


def prices() -> pd.DataFrame:
    def ld(f, col="Adj Close"):
        d = pd.read_csv(RAW / f, parse_dates=["Date"], index_col="Date")
        return d[col]
    P = pd.DataFrame({"LSIP": ld("LSIP_yf_full.csv"), "TAPG": ld("TAPG_yf_full.csv"), "IHSG": ld("IHSG.csv")})
    V = pd.read_csv(RAW / "LSIP_yf_full.csv", parse_dates=["Date"], index_col="Date")
    P["LSIP_value_bn"] = V.Close * V.Volume / 1e9
    P["LSIP_close"] = V.Close
    peers = {}
    for t in ["AALI", "SSMS", "DSNG", "SIMP", "SGRO", "BWPT", "TAPG", "STAA", "TBLA"]:
        try:
            peers[t] = ld(f"{t}.csv")
        except FileNotFoundError:
            pass
    P = P.join(pd.DataFrame(peers).add_prefix("peer_"), how="left")
    return P.loc["2015-01-01":]


def risk(P: pd.DataFrame) -> dict:
    r = P[["LSIP", "TAPG", "IHSG"]].pct_change(fill_method=None)
    peer = P.filter(like="peer_").drop(columns=["peer_TAPG"], errors="ignore").pct_change(fill_method=None).mean(axis=1)   # ex-self (LSIP not in list)
    out = {}
    for t in ("LSIP", "TAPG"):
        x = r[t].dropna()
        lvl = P[t].dropna()
        dd = lvl / lvl.cummax() - 1
        m = (1 + x).resample("ME").prod() - 1
        out[t] = {"ann_vol_daily_5y": float(x.loc["2021-11-25":].std() * np.sqrt(244)), "ann_vol_daily_1y": float(x.loc["2025-11-25":].std() * np.sqrt(244)),
                  "max_drawdown_since_2015": float(dd.min()), "max_drawdown_date": str(dd.idxmin().date()),
                  "drawdown_now": float(dd.iloc[-1]), "monthly_ret_p5": float(m.loc["2016":].quantile(0.05)),
                  "monthly_ret_p1": float(m.loc["2016":].quantile(0.01)), "worst_month": float(m.loc["2016":].min()),
                  "worst_12m": float(((1 + m).rolling(12).apply(np.prod, raw=True) - 1).loc["2016":].min()),
                  "share_negative_12m": float((((1 + m).rolling(12).apply(np.prod, raw=True) - 1).loc["2016":] < 0).mean())}
    # weekly HAC betas, 5 years: market (IHSG), sector (EW peers ex-self), CPO (WB monthly, monthly regression)
    w = (1 + pd.concat([r, peer.rename("SECTOR")], axis=1)).resample("W-FRI").prod() - 1
    w = w.loc["2021-11-25":]
    for t in ("LSIP", "TAPG"):
        mk = ols_nw(w[t], w[["IHSG"]], lags=4)
        sc = ols_nw(w[t], w[["SECTOR"]], lags=4)
        out[t] |= {"beta_mkt_5y_weekly": float(mk.loc["IHSG", "coef"]), "beta_mkt_t": float(mk.loc["IHSG", "t_nw"]),
                   "beta_sector_5y_weekly": float(sc.loc["SECTOR", "coef"]), "beta_sector_t": float(sc.loc["SECTOR", "t_nw"])}
    mm = pd.read_csv(ROOT / "data" / "reference" / "macro_monthly.csv", index_col=0)
    cpo = mm["palm_oil_idr_kg"].dropna(); cpo.index = pd.PeriodIndex(cpo.index, freq="M")
    mret = (1 + r).resample("ME").prod() - 1; mret.index = mret.index.to_period("M")
    d = pd.concat([mret, cpo.pct_change().rename("CPO")], axis=1).loc["2016-01":"2026-10"].dropna()
    for t in ("LSIP", "TAPG"):
        b = ols_nw(d[t], d[["IHSG", "CPO"]], lags=3)
        out[t] |= {"beta_cpo_idr_monthly": float(b.loc["CPO", "coef"]), "beta_cpo_t": float(b.loc["CPO", "t_nw"])}
    v = P["LSIP_value_bn"].loc["2026-05-25":]
    out["LSIP"] |= {"median_daily_value_6m_bn": float(v.median()), "p10_daily_value_6m_bn": float(v.quantile(0.1)),
                    "days_to_trade_750bn_at_20pct_adv": float(750 / (0.2 * v.median())),
                    "corr_LSIP_TAPG_weekly_5y": float(w[["LSIP", "TAPG"]].corr().iloc[0, 1])}
    return out


def event_reactions(P: pd.DataFrame) -> pd.DataFrame:
    """Market-adjusted (IHSG) cumulative returns around dated LSIP events (usable date = next trading day).
    Small n: descriptive only."""
    ev = [("FY2024 results", "2025-02-28"), ("H1 2025 results", "2025-07-31"), ("FY2025 results", "2026-02-27"),
          ("Q1 2026 highlights", "2026-04-30"), ("H1 2026 results", "2026-07-31"), ("Buyback disclosure", "2026-10-23"),
          ("9M 2026 results", "2026-10-30"), ("Ex-dividend FY2024", "2025-07-01"), ("Ex-dividend FY2025", "2026-07-06")]
    r = P[["LSIP", "IHSG"]].pct_change(fill_method=None).dropna()
    ab = r.LSIP - r.IHSG
    rows = []
    for name, d in ev:
        idx = ab.index.searchsorted(pd.Timestamp(d), side="right")       # first trading day after the evening release
        if name.startswith("Ex-dividend"):
            idx = ab.index.searchsorted(pd.Timestamp(d))
        rows.append({"event": name, "date": d, "day0": str(ab.index[idx].date()) if idx < len(ab) else None,
                     "car_0_1": float(ab.iloc[idx:idx + 2].sum()) if idx + 1 < len(ab) else np.nan,
                     "car_0_5": float(ab.iloc[idx:idx + 6].sum()) if idx + 5 < len(ab) else np.nan,
                     "car_0_20": float(ab.iloc[idx:idx + 21].sum()) if idx + 20 < len(ab) else np.nan})
    D = pd.DataFrame(rows); D.to_csv(RES / "LSIP_event_reactions.csv", index=False, float_format="%.4f")
    return D


def valuation_history(P: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fy in range(2020, 2026):
        p = f"FY{fy}"
        px = P["LSIP_close"].loc[:f"{fy}-12-31"].iloc[-1]
        mcap = px * SHARES / 1000
        npo = FIN.loc[p, "profit"] / 1000; eq = FIN.loc[p, "total_equity"] / 1000; cash = FIN.loc[p, "cash_end"] / 1000
        fi = FIN.loc[p, "finance_income"] / 1000 * 0.8
        rows.append({"fy": fy, "price_ye": px, "mcap_bn": mcap, "pe": mcap / npo, "pb": mcap / eq, "cash_pct_mcap": cash / mcap,
                     "ev_ex_cash_bn": mcap - cash, "ev_over_np_ex_interest": (mcap - cash) / (npo - fi)})
    rows.append({"fy": "current", "price_ye": PRICE, "mcap_bn": PRICE * SHARES / 1000,
                 "pe": PRICE * SHARES / 1000 / (CUM["9M 2026"]["np_owners"] + 360),
                 "pb": PRICE * SHARES / 1000 / (FIN.loc["9M26", "total_equity"] / 1000),
                 "cash_pct_mcap": FIN.loc["9M26", "cash_end"] / 1000 / (PRICE * SHARES / 1000),
                 "ev_ex_cash_bn": PRICE * SHARES / 1000 - FIN.loc["9M26", "cash_end"] / 1000})
    D = pd.DataFrame(rows); D.to_csv(RES / "LSIP_valuation_history.csv", index=False, float_format="%.4f")
    return D


def tapg_comparison() -> pd.DataFrame:
    g = pd.read_csv(ROOT / "data" / "reference" / "TAPG_scope_groupwide.csv").pivot_table(index="item", columns="period", values="value")
    ts = pd.read_csv(ROOT / "data" / "reference" / "TAPG_statements_extracted.csv")
    ts = ts[ts.basis.fillna("").str.startswith("audited") & ts.period.str.startswith("FY")].drop_duplicates(["item", "period"]).pivot_table(index="item", columns="period", values="value")
    rows = []
    for fy in range(2021, 2026):
        p = f"FY{fy}"
        lo, lf = OPS.loc[p], FIN.loc[p]
        a = {"company": "LSIP", "fy": fy, "planted_oil_palm_ha": lo.oil_palm, "mature_ha": lo.op_mature,
             "immature_share": lo.op_immature / lo.oil_palm, "ffb_nucleus_kt": lo.ffb_nucleus, "yield_t_ha": lo.yield_nucleus_t_ha,
             "cpo_kt": lo.cpo, "oer": lo.cpo / lo.ffb_total, "revenue_bn": lf.revenue / 1000, "operating_profit_bn": lf.operating_profit / 1000,
             "op_margin": lf.operating_profit / lf.revenue, "profit_bn": lf.profit / 1000, "cfo_bn": lf.cfo / 1000, "capex_bn": -lf.capex / 1000,
             "fcf_bn": (lf.cfo + lf.capex) / 1000, "dividends_paid_bn": -lf.dividends_paid / 1000, "cash_bn": lf.cash_end / 1000,
             "equity_bn": lf.total_equity / 1000,
             "invested_capital_bn": (lf.total_equity - lf.cash_end + lf.employee_benefits_lt) / 1000,
             "nopat_bn": lf.operating_profit * 0.78 / 1000}
        ag = AGE_LSIP.get(fy)
        if ag is not None:
            a |= {"gt20_share": ag["gt20"] / ag["total"], "a7_20_share": ag["a7_20"] / ag["total"]}
        rows.append(a)
        if p in g.columns:
            t = g[p]; s = ts[p] if p in ts.columns else pd.Series(dtype=float)
            b = {"company": "TAPG", "fy": fy, "planted_oil_palm_ha": t.get("age_total_ha_nucleus"), "mature_ha": t.get("mature_ha_nucleus_total"),
                 "immature_share": t.get("immature_ha_nucleus_total", np.nan) / t.get("age_total_ha_nucleus", np.nan),
                 "ffb_nucleus_kt": t.get("ffb_nucleus_total_kt"), "yield_t_ha": t.get("avg_ffb_yield"), "cpo_kt": t.get("cpo_production"),
                 "oer": t.get("oer_cpo") / 100 if pd.notna(t.get("oer_cpo")) else np.nan,
                 "gt20_share": t.get("age_gt20_ha_nucleus") / t.get("age_total_ha_nucleus"),
                 "a7_20_share": t.get("age_7_20_ha_nucleus") / t.get("age_total_ha_nucleus"),
                 "revenue_bn": s.get("revenue", np.nan) / 1000, "operating_profit_bn": s.get("operating_profit", np.nan) / 1000,
                 "op_margin": s.get("operating_profit", np.nan) / s.get("revenue", np.nan), "profit_bn": s.get("profit_for_year", np.nan) / 1000,
                 "cfo_bn": s.get("cfo", np.nan) / 1000, "capex_bn": abs(s.get("capex_fixed_assets", np.nan)) / 1000,
                 "fcf_bn": (s.get("cfo", np.nan) - abs(s.get("capex_fixed_assets", np.nan))) / 1000,
                 "dividends_paid_bn": abs(s.get("dividends_paid", np.nan)) / 1000, "cash_bn": s.get("cash", np.nan) / 1000,
                 "equity_bn": s.get("total_equity", np.nan) / 1000,
                 "invested_capital_bn": (s.get("total_equity", np.nan) - s.get("cash", np.nan)) / 1000,
                 "nopat_bn": s.get("operating_profit", np.nan) * 0.78 / 1000}
            rows.append(b)
    D = pd.DataFrame(rows)
    D["roic"] = D.nopat_bn / D.invested_capital_bn
    D["fcf_payout"] = D.dividends_paid_bn / D.fcf_bn
    D["sustainable_replant_ha_25y"] = D.planted_oil_palm_ha / 25
    D.to_csv(RES / "LSIP_TAPG_comparison.csv", index=False, float_format="%.4f")
    return D


AGE_LSIP = {int(r.date[:4]): r for _, r in pd.read_csv(RES / "LSIP_age_profile.csv").dropna(subset=["total"]).iterrows()}


def prior_audit(q4: pd.DataFrame, cashd: pd.DataFrame, cr: pd.DataFrame) -> pd.DataFrame:
    s1 = pd.read_csv(RES / "LSIP_stage1_summary.csv", index_col=0).iloc[:, 0]
    surplus = float(cashd.loc[cashd.item == "Distributable surplus cash (before buyback)", "idr_bn"].iloc[0])
    rows = [
        ("Cash ~IDR 8.5tn (9M26)", 8516.274, FIN.loc["9M26", "cash_end"] / 1000, "CONFIRMED", "9M26 FS"),
        ("Excess cash IDR 6.3tn", s1["excess_cash_after_buyback"], surplus - 750,
         "REVISED (method)", "v1 deducted one quarter of cash costs + LT employee benefits + full buyback; v2 deducts 2 months' cash costs, a seasonal WC buffer, employee benefits and taxes payable (CIP is in forecast capex, so not deducted); the buyback is shown separately. Buyback is a distribution, not a cost: value per share is unaffected by it at fair prices."),
        ("Historical payout ~30%", 0.30, float(cr.payout.iloc[-3:].mean()), "CONFIRMED (30-35%)",
         "Company dividend page: FY21-23 35%, FY24-25 30%; FY20 20%"),
        ("Buyback up to IDR 750bn", 750.0, 750.0, "CONFIRMED (authorisation)", "Disclosure 23 Oct 2026; window 26 Oct-31 Dec 2026"),
        ("Buyback execution", np.nan, np.nan, "UNVERIFIED", "No execution report on londonsumatra.com (press/disclosure pages, 25 Nov 2026); IDX blocked from this environment"),
        ("Q4 2026 nowcast IDR 468bn (v1 base)", 468.11, float(q4.loc["base", "q4_np_owners"]), "REVISED (v2)",
         "v1 assumed Q4 volume 0.95x Q3; Q4 is the seasonal peak (Q4'25 = 1.16x Q3'25). v2 base 1.05x, price -3%"),
        ("Consensus-implied Q4 IDR 360bn", 360.0, float(q4.loc["base", "consensus_implied_q4"]), "CONFIRMED", "FY26 EPS 308.66 x 6,820mn - 9M 1,745bn (S-036, 25 Nov 2026)"),
        ("Expected total return 17.6% (Phase VII)", 0.176, np.nan, "SUPERSEDED", "Market-calibrated multiple frame; Phase XVII replaces it with scenario DCF/DDM (see report)"),
        ("Preferred entry IDR 1,340-1,460", 1400.0, np.nan, "SUPERSEDED", "Recomputed from Phase XVII value range and hurdle"),
        ("Related-party bank exposure", 665.016, RPC.loc["9M26", "bank_ina_perdana"] / 1000, "CONFIRMED; history added",
         "Bank Ina Perdana 15-22% of cash FY21-FY25 (peak 1.64tn, 21.6% at FY25), 7.8% at 9M26"),
        ("Sales to parent SIMP", np.nan, 0.6326, "CONFIRMED", "FY25 FS: SIMP 3,487bn = 63.3% of revenue (v1 cited 76%: not reproduced; 76% unverified)"),
        ("FY2023 average age ~19 years", 19.0, 19.0, "CONFIRMED (AR); SR says 18", "AR2023 p41 'Average Age: 19 years'; SR2023: 18 years"),
        ("FY2023 >20 years share 41%", 0.41, float(AGE_LSIP[2023].gt20_share), "CONFIRMED", "AR2023 p7: 37,667 / 91,759 ha"),
    ]
    D = pd.DataFrame(rows, columns=["previous_finding", "previous_value", "phase17_value", "status", "evidence"])
    D.to_csv(RES / "LSIP_prior_audit.csv", index=False, float_format="%.4f")
    return D


def hurdle() -> dict:
    """A6 / D-030 open item: hurdle reassessment, documented independently of the conclusion."""
    rf_then, rf_now = 0.062, 0.07735
    return {"current_hurdle": 0.175, "implied_ke_then": 0.125, "rf_when_set": rf_then, "rf_now": rf_now,
            "erp_implied_then": 0.125 - rf_then, "erp_implied_now_if_unchanged": 0.125 - rf_now,
            "alpha_margin": 0.05,
            "proposal": "Restate the hurdle as ke + 5pp with ke = 10y SBN + 0.9 x 6.0% ERP = 13.1% -> 18.1%; adopt only by a "
                        "separate decision (logged as A-049 proposal), the recommendation is tested at both 17.5% and 18.1%.",
            "proposed_hurdle": round(rf_now + 0.9 * 0.06 + 0.05, 4)}


def main():
    q4 = q4_v2(); cashd = cash_decomposition(); cr = capital_return_history()
    P = prices(); rk = risk(P); ev = event_reactions(P); vh = valuation_history(P); tp = tapg_comparison()
    au = prior_audit(q4, cashd, cr); hd = hurdle()
    (RES / "LSIP_risk_stats.json").write_text(json.dumps({"risk": rk, "hurdle": hd}, indent=1), encoding="utf-8")
    for name, d in (("Q4 v2", q4), ("cash", cashd), ("capital return", cr), ("events", ev), ("valuation history", vh), ("audit", au)):
        print("==", name); print(d.round(3).to_string())
    print(json.dumps(rk, indent=1)); print(json.dumps(hd, indent=1))
    print(tp.round(3).to_string())


if __name__ == "__main__":
    main()
