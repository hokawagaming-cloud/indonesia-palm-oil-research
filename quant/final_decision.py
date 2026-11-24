"""Institutional decision pass (Phase VII): market/factor assessment, LSIP valuation cross-checks,
joint adverse scenarios, opportunity cost and the transparent scorecard.

Reuses existing data only: Yahoo adjusted closes (S-002), EW core PIT benchmark (benchmarks_daily),
World Bank CPO + USD/IDR (macro_monthly, S-003), LSIP Stage 1 outputs, TAPG/DSNG/STAA Phase IV-V outputs.
New external inputs (S-052/S-053): 10y SBN 7.735% (ADB AsianBondsOnline, 17 Nov 2026), BI-Rate 6.00%
(Bank Indonesia, 18 Nov 2026). Tags: OBS / DER / EST.

Usage: python -I -X utf8 quant/final_decision.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
OUT = REF / "research"
OHLCV = ROOT / "data" / "raw" / "ohlcv"
NAMES = ["TAPG", "LSIP", "DSNG", "STAA"]
ASOF = "2026-11-24"

# --- rates, taxes, costs (S-052/S-053 OBS; statutory rates and costs EST) -----------------
SBN10 = 0.07735          # OBS 10y SBN, 17 Nov 2026
BI_RATE = 0.0600         # OBS BI-Rate after 18 Nov 2026 hike
DEPOSIT_NET = 0.0475 * (1 - 0.20)  # EST 12m IDR time deposit ~4.75% gross, 20% final tax
MM_FUND_NET = 0.0550     # EST money-market fund net yield (fund returns are not taxed at unit-holder level)
SBN_NET = SBN10 * (1 - 0.10)       # 10% final tax on resident bond coupons; price risk ignored at 12m hold-to-yield
DIV_TAX = 0.10           # resident individual final dividend tax (exempt if reinvested domestically) - conservative
ROUND_TRIP = 0.0055      # EST: ~0.20% buy + ~0.25% sell incl 0.10% sales tax + ~0.10% slippage for liquid names
IHSG_EXP = SBN10 + 0.055  # EST: rf + 5.5pp ERP -> ~13.2% gross expected IHSG return; no forecast skill claimed


def adj(t: str) -> pd.Series:
    d = pd.read_csv(OHLCV / f"{t}.csv", index_col=0, parse_dates=True)
    return pd.to_numeric(d["Adj Close"], errors="coerce").dropna()


def ols(y: pd.Series, X: pd.DataFrame) -> dict:
    df = pd.concat([y.rename("y"), X], axis=1).dropna()
    A = np.column_stack([np.ones(len(df)), df[X.columns].to_numpy()])
    b, *_ = np.linalg.lstsq(A, df["y"].to_numpy(), rcond=None)
    e = df["y"].to_numpy() - A @ b
    s2 = e @ e / (len(df) - A.shape[1])
    se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    r2 = 1 - (e @ e) / ((df["y"] - df["y"].mean()) ** 2).sum()
    return {"n": len(df), "coef": dict(zip(["alpha"] + list(X.columns), b)), "t": dict(zip(["alpha"] + list(X.columns), b / se)),
            "r2": r2, "resid": pd.Series(e, index=df.index)}


def market_assessment() -> pd.DataFrame:
    bm = pd.read_csv(REF / "benchmarks_daily.csv", index_col=0, parse_dates=True)
    mac = pd.read_csv(REF / "macro_monthly.csv", index_col=0)
    mac.index = pd.PeriodIndex(mac.index, freq="M")
    ihsg_w = (1 + bm.ihsg_ret.fillna(0)).cumprod().resample("W-FRI").last().pct_change(fill_method=None)
    sect_w = (1 + bm.ew_core_pit_ret.fillna(0)).cumprod().resample("W-FRI").last().pct_change(fill_method=None)
    ihsg_m = (1 + bm.ihsg_ret.fillna(0)).cumprod().resample("ME").last().pct_change(fill_method=None)
    sect_m = (1 + bm.ew_core_pit_ret.fillna(0)).cumprod().resample("ME").last().pct_change(fill_method=None)
    ihsg_m.index = ihsg_m.index.to_period("M"); sect_m.index = sect_m.index.to_period("M")
    cpo_m = mac.palm_oil_usd_t.pct_change(fill_method=None)
    fx_m = mac.usdidr_month_end.pct_change(fill_method=None)
    rows, daily = [], {}
    for t in NAMES:
        p = adj(t)
        d = pd.read_csv(OHLCV / f"{t}.csv", index_col=0, parse_dates=True)
        tv = (pd.to_numeric(d.Close, errors="coerce") * pd.to_numeric(d.Volume, errors="coerce") / 1e9).dropna()
        r_d = p.pct_change(fill_method=None)
        daily[t] = r_d
        w = p.resample("W-FRI").last().pct_change(fill_method=None)
        w3 = w.loc["2023-11-24":ASOF]
        mkt = ols(w3, pd.DataFrame({"ihsg": ihsg_w}))
        two = ols(w3, pd.DataFrame({"ihsg": ihsg_w, "sector_x": sect_w - ihsg_w}))
        m = p.resample("ME").last().pct_change(fill_method=None); m.index = m.index.to_period("M")
        m5 = m.loc["2021-11":"2026-10"]
        fac = ols(m5, pd.DataFrame({"ihsg": ihsg_m, "cpo_usd": cpo_m, "usdidr": fx_m}))
        res12 = two["resid"].loc["2025-11-24":].sum()
        mom_12_1 = p.loc[:"2026-10-24"].iloc[-1] / p.loc[:"2025-11-24"].iloc[-1] - 1
        rel6 = (p.iloc[-1] / p.loc[:"2026-05-24"].iloc[-1]) / (bm.ew_core_pit_level.iloc[-1] / bm.ew_core_pit_level.loc[:"2026-05-24"].iloc[-1]) - 1
        ill = (r_d.abs() / tv.reindex(r_d.index)).loc["2026-05-24":].replace(np.inf, np.nan).median()
        tv20, tv_q3 = tv.loc["2026-10-27":].median(), tv.loc["2026-07-01":"2026-09-30"].median()
        tv_1y = tv.loc["2025-11-24":]
        rows.append({"ticker": t, "price": float(pd.to_numeric(d.Close).iloc[-1]),
                     "beta_ihsg_3y_w": mkt["coef"]["ihsg"], "beta_ihsg_t": mkt["t"]["ihsg"], "r2_mkt": mkt["r2"],
                     "beta_sector_x": two["coef"]["sector_x"], "beta_sector_t": two["t"]["sector_x"], "r2_two": two["r2"],
                     "beta_cpo_m": fac["coef"]["cpo_usd"], "t_cpo": fac["t"]["cpo_usd"], "beta_fx_m": fac["coef"]["usdidr"], "t_fx": fac["t"]["usdidr"],
                     "alpha_m_ann": fac["coef"]["alpha"] * 12, "alpha_t": fac["t"]["alpha"], "n_months": fac["n"], "r2_fac": fac["r2"],
                     "resid_ret_12m": res12, "mom_12_1": mom_12_1, "rel_strength_6m_vs_sector": rel6,
                     "vol_ann_1y": r_d.loc["2025-11-24":].std() * np.sqrt(244),
                     "tv_median_20d_bn": tv20, "tv_median_q3_bn": tv_q3, "tv_ratio": tv20 / tv_q3,
                     "tv_median_1y_bn": tv_1y.median(), "turnover_z_20d": (tv.loc["2026-10-27":].mean() - tv_1y.mean()) / tv_1y.std(),
                     "amihud_6m": ill})
    A = pd.DataFrame(rows).set_index("ticker")
    C = pd.DataFrame(daily).loc["2025-11-24":].corr()
    for t in NAMES:
        A.loc[t, "corr_1y_TAPG"] = C.loc[t, "TAPG"]
    return A


# --- LSIP valuation cross-checks (IDR bn; per-share IDR) ----------------------------------
SH0 = 6819.96
PX = 1570.0
CASH = 8516.3              # OBS 30 Sep 2026
FIN_INC_9M = 239.0         # OBS 9M finance income
INT_AT = FIN_INC_9M / 0.75 * (1 - 0.20)   # DER ~255bn/yr after 20% final tax: strip from NP to avoid double count with cash
BUYBACK = 750.0
NP26_BASE = 2213.0         # our base (Stage 1)
NP27 = {"bear": 1800.0, "base": 2200.0, "bull": 2400.0}
PROB = {"bear": 0.30, "base": 0.50, "bull": 0.20}
NORM_NP = np.mean([1036, 762, 1477, 1888, 2213])   # OBS FY22-25 + FY26 base: through-cycle reported profit
PAYOUT = 0.30


def lsip_valuation(buyback_done: float = 1.0, np27: dict | None = None, cash_credit: float = 1.0,
                   pe_ops: dict | None = None) -> dict:
    """12-month value per share from five methods, all on operating (ex-interest) profit + cash once.
    buyback_done: share of the 750bn executed at 1,570. Dividends paid out of cash are added to return only."""
    np27 = np27 or NP27
    bb = BUYBACK * buyback_done
    sh = SH0 - bb / PX * 1000
    div_ps = PAYOUT * NP26_BASE / SH0 * 1000
    cash12 = CASH + 1800.0 - PAYOUT * NP26_BASE - bb          # EST 12m cash generation incl. interest
    ops = {k: v - INT_AT for k, v in np27.items()}             # operating profit ex after-tax interest
    out = {}
    # (1) cash-adjusted with market-calibrated ops multiple (Stage 1 frame, now ex-interest): 0.33 / 1.2 / 2.3x
    m = pe_ops or {"bear": 0.33, "base": 1.2, "bull": 2.3}
    out["cash_adjusted"] = {k: (cash_credit * cash12 + m[k] * ops[k]) / sh * 1000 for k in ops}
    # (2) FCFE of operations (ke 12.5%, g 2%, conversion 0.85; A-024) + cash credited
    out["fcfe_ops"] = {k: (cash_credit * cash12 + ops[k] * 0.85 * 1.02 / 0.105) / sh * 1000 for k in ops}
    # (3) DDM at the observed 30% payout (minority only receives dividends): D1/(ke-g); cash not separately added
    out["ddm_30pct"] = {k: PAYOUT * np27[k] / sh * 1000 / 0.105 for k in np27}
    # (4) normalised earnings x historical total P/E (FY22-25: 6.7/8.0/4.5/4.3; trough/median/upper)
    pe = {"bear": 4.3, "base": 5.6, "bull": 6.7}
    out["normalised_pe"] = {k: pe[k] * {"bear": NORM_NP * 0.9, "base": NORM_NP, "bull": np27["base"]}[k] / sh * 1000 for k in pe}
    # (5) peer multiple on ops (DSNG/STAA/TAPG FY26 P/E 6.0/5.7/8.0 -> 5.5x after LSIP size/governance) + cash at credit
    out["peer_ops_plus_cash"] = {k: (cash_credit * cash12 + 5.5 * ops[k]) / sh * 1000 for k in ops}
    rets = {meth: {k: (v + div_ps * (1 - DIV_TAX)) / PX - 1 for k, v in d.items()} for meth, d in out.items()}
    er = {meth: sum(PROB[k] * r[k] for k in r) for meth, r in rets.items()}
    return {"values": out, "returns": rets, "expected": er, "div_ps": div_ps, "shares": sh, "cash12": cash12}


def reverse_lsip() -> dict:
    """What the price implies under two identifying assumptions (the decomposition is not identified)."""
    mcap = PX * SH0 / 1000
    ops26 = NP26_BASE - INT_AT
    return {"mcap": mcap, "pe_total_fy26": mcap / NP26_BASE,
            "implied_ops_multiple_if_cash_100": (mcap - CASH) / ops26,
            "implied_cash_credit_if_ops_at_5_5x": (mcap - 5.5 * ops26) / CASH,
            "implied_sustainable_ops_np_fcfe_if_cash_100": (mcap - CASH) / (0.85 * 1.02 / 0.105)}


def joint_adverse() -> pd.DataFrame:
    rows = []
    grid = [(bb, cc, k) for bb in (1.0, 0.25, 0.0) for cc in (1.0, 0.8, 0.6) for k in ("bear", "base")]
    for bb, cc, k in grid:
        v = lsip_valuation(buyback_done=bb, cash_credit=cc)
        rows.append({"buyback_executed": bb, "cash_credit": cc, "np27_case": k,
                     "ret_cash_adjusted": v["returns"]["cash_adjusted"][k], "ret_normalised_pe": v["returns"]["normalised_pe"][k]})
    # explicit joint adverse: FY27 bear + El Nino-lag profit 1,500 + trough multiple + no buyback + 60% cash credit
    worst = lsip_valuation(buyback_done=0.0, cash_credit=0.6, np27={"bear": 1500.0, "base": 1800.0, "bull": 2200.0})
    rows.append({"buyback_executed": 0.0, "cash_credit": 0.6, "np27_case": "joint: NP 1,500, trough mult",
                 "ret_cash_adjusted": worst["returns"]["cash_adjusted"]["bear"], "ret_normalised_pe": worst["returns"]["normalised_pe"]["bear"]})
    return pd.DataFrame(rows)


def opportunity_cost(lsip_er_gross: float, vol: dict | None = None) -> pd.DataFrame:
    vol = vol or {}
    alts = [("Cash (0%)", 0.0, 0.0), ("IDR time deposit 12m (net of 20% tax)", DEPOSIT_NET, 0.0),
            ("Money-market fund (net)", MM_FUND_NET, 0.0), ("10y SBN, hold for coupon (net of 10% tax)", SBN_NET, 0.08),
            ("IHSG (rf + 5.5pp ERP, EST; less 0.3% cost)", IHSG_EXP - 0.003, 0.20)]
    rows = [{"asset": a, "expected_net_12m": r, "vol_EST": v} for a, r, v in alts]
    tapg = pd.read_csv(OUT / "TAPG_entry_summary.csv", index_col=0).iloc[:, 0]
    tri = pd.read_csv(OUT / "three_name_uniform_valuation.csv").set_index("ticker")
    rows += [{"asset": "TAPG @1,710 (our model)", "expected_net_12m": float(tapg["expected_return_at_1710"]) - ROUND_TRIP, "vol_EST": vol.get("TAPG", 0.30)},
             {"asset": "DSNG @1,275 (uniform rule)", "expected_net_12m": tri.loc["DSNG", "expected_return"] - ROUND_TRIP, "vol_EST": vol.get("DSNG", 0.35)},
             {"asset": "STAA @1,015 (uniform rule)", "expected_net_12m": tri.loc["STAA", "expected_return"] - ROUND_TRIP, "vol_EST": vol.get("STAA", 0.35)},
             {"asset": "LSIP @1,570 (market-calibrated, after costs)", "expected_net_12m": lsip_er_gross - ROUND_TRIP, "vol_EST": vol.get("LSIP", 0.30)}]
    df = pd.DataFrame(rows)
    df["excess_vs_mmf"] = df.expected_net_12m - MM_FUND_NET
    df["excess_per_vol"] = np.where(df.vol_EST > 0, df.excess_vs_mmf / df.vol_EST.replace(0, np.nan), np.nan)
    return df


SCORE_RULES = {  # 1 (poor) .. 5 (strong); criteria stated so scores are auditable, not probabilities
    "fundamental_quality": "5: low-cost, net cash, stable ROE>15%; 3: average cost/leverage; 1: high cost or leverage",
    "predictive_edge": "5: validated PIT indicator with n>=12 and IC/hit significantly >0; 3: plausible model, n<6 PIT; 1: no model",
    "expectations_gap": "5: >15% gap on the earnings year that drives value (FY27); 3: gap only on a near quarter; 1: none or negative",
    "valuation": "5: E[R] >25% across methods; 4: 17.5-25%; 3: 10-17.5%; 2: 0-10%; 1: <0",
    "catalyst_quality": "5: dated, high-probability, repricing mechanism shown; 3: dated but weak mechanism; 1: undated",
    "governance": "5: aligned owner, high payout, no RPT; 3: some RPT, fair payout; 1: trapped cash/RPT-heavy",
    "downside_protection": "5: bear-case return >0 under joint adverse; 3: -10 to 0; 1: < -20%",
    "liquidity": "5: >IDR 20bn/day; 4: 10-20; 3: 5-10; 2: 1-5; 1: <1",
    "evidence_quality": "5: primary PIT filings + validated forecasts; 3: primary filings, unvalidated forecasts; 1: secondary only",
    "portfolio_suitability": "5: low corr to holdings, diversifying; 3: moderate; 1: duplicates existing exposure",
}
SCORES = {  # EST judgement applying SCORE_RULES to the evidence in this module and prior phases
    "TAPG": dict(fundamental_quality=4, predictive_edge=3, expectations_gap=2, valuation=2, catalyst_quality=2, governance=4,
                 downside_protection=2, liquidity=4, evidence_quality=4, portfolio_suitability=3),
    "LSIP": dict(fundamental_quality=4, predictive_edge=2, expectations_gap=2, valuation=3, catalyst_quality=2, governance=2,
                 downside_protection=4, liquidity=3, evidence_quality=3, portfolio_suitability=3),
    "DSNG": dict(fundamental_quality=3, predictive_edge=2, expectations_gap=1, valuation=3, catalyst_quality=2, governance=3,
                 downside_protection=2, liquidity=2, evidence_quality=3, portfolio_suitability=3),
    "STAA": dict(fundamental_quality=3, predictive_edge=1, expectations_gap=3, valuation=2, catalyst_quality=2, governance=3,
                 downside_protection=2, liquidity=1, evidence_quality=2, portfolio_suitability=3),
}


def main() -> int:
    A = market_assessment()
    V = lsip_valuation()
    R = reverse_lsip()
    J = joint_adverse()
    methods = pd.DataFrame({m: {**{f"value_{k}": V["values"][m][k] for k in PROB}, **{f"ret_{k}": V["returns"][m][k] for k in PROB},
                                "expected": V["expected"][m]} for m in V["values"]}).T
    # 12m return is set by the MARKET multiple, so the market-calibrated cash-adjusted frame is the decision
    # metric; FCFE/peer/DDM bound long-run value to a minority (they need governance to unlock, see memo).
    tri = V["expected"]["cash_adjusted"]
    rng = np.random.default_rng(20261125)
    W = rng.dirichlet(np.array([0.3, 0.5, 0.2]) * 10, 20000)
    dist = W @ np.array([V["returns"]["cash_adjusted"][k] for k in ("bear", "base", "bull")])
    ev_val = {c: sum(PROB[k] * (lsip_valuation(cash_credit=c)["values"]["cash_adjusted"][k] + V["div_ps"] * (1 - DIV_TAX)) for k in PROB) for c in (1.0, 0.9, 0.8)}
    entry = {f"entry_hurdle_cash{int(c*100)}": v / 1.175 for c, v in ev_val.items()}
    entry.update({f"entry_ke_cash{int(c*100)}": v / 1.125 for c, v in ev_val.items()})
    O = opportunity_cost(tri, A.vol_ann_1y.to_dict())  # equities: realised 1y vol
    S = pd.DataFrame(SCORES).T
    S["total_of_50"] = S.sum(axis=1)
    A.to_csv(OUT / "final_market_assessment.csv", float_format="%.4f")
    methods.to_csv(OUT / "LSIP_valuation_methods.csv", float_format="%.3f")
    J.to_csv(OUT / "LSIP_joint_adverse.csv", index=False, float_format="%.3f")
    O.to_csv(OUT / "final_opportunity_cost.csv", index=False, float_format="%.4f")
    S.to_csv(OUT / "final_scorecard.csv")
    pd.Series({**R, "int_after_tax": INT_AT, "norm_np": NORM_NP, "triangulated_er": tri, "div_ps": V["div_ps"],
               "fair_low": methods[["value_bear", "value_base"]].stack().quantile(0.25), "fair_mid": methods.value_base.median(),
               "fair_high": methods.value_base.quantile(0.75), "p05": np.percentile(dist, 5), "p95": np.percentile(dist, 95),
               "p_gt_hurdle": float((dist > 0.175).mean()), "p_gt_ke": float((dist > 0.125).mean()), **entry,
               **{f"ev_value_cash{int(c*100)}": v for c, v in ev_val.items()}}).to_csv(OUT / "final_decision_summary.csv")
    pd.set_option("display.width", 220)
    print(A.round(3).T.to_string()); print(methods.round(3).to_string()); print(R); print(J.round(3).to_string())
    print(O.round(4).to_string()); print(S.to_string()); print("decision metric", tri, entry, np.percentile(dist,[5,95]), (dist>0.175).mean())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
