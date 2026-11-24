"""LSIP Phase VI Stage 1: quarterly reconstruction, Q3 gross-profit bridge, Q4 nowcast,
excess cash, buyback and the 17.5% research gate. EXPLORATORY; tags OBS/DER/EST.

Primary sources (local, git-ignored; S-046..S-051): LSIP interim FS 30 Jun 2026 and 30 Sep 2026
(bilingual, p4-7 statements, p52 cash note, p92 cost of goods sold), Lonsum Highlights 1Q26, 9M26,
FY25, FY24, buyback disclosure (23 Oct 2026). IDX timestamps (S-027 mirror, LSIP pages):
  9M26 FS 2026-10-30 19:45 -> usable 2026-11-02; H1 FS 2026-07-31 16:22 -> 2026-08-03;
  1Q26 highlights 2026-04-30 20:00 -> 2026-05-04; buyback disclosure 2026-10-23 18:51 -> 2026-10-26.
Values in IDR bn.
Usage: python -I -X utf8 quant/lsip_stage1.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reference" / "research"
SHARES = 6819.96  # mn (Yahoo sharesOutstanding, 2026-11-24; matches EPS 256 = 1,745bn / 6,820mn)
PRICE = 1570.0     # S-002 close 2026-11-24

# ---------------------------------------------------------------- OBS: cumulative figures
CUM = {  # period: dict
    "Q1 2026": dict(revenue=1327, gross_profit=425, operating_profit=394, np_owners=394, core_profit=400, src="Highlights 1Q26"),
    "H1 2026": dict(revenue=2689.745, gross_profit=862.653, cogs=1827.092, fv_bio=37.734, selling=-26.828, ga=-138.583,
                    other_inc=208.863, other_exp=-25.781, fin_inc=143.159, fin_cost=-0.137, tax=-172.134, np_owners=890.988,
                    prod_cost=1792.572, fg_open=420.616, fg_close=372.515, fg_purch=0.0, ffb_purch=363.977, upkeep=311.657,
                    harvest=305.103, indirect=494.861, dep=193.321, mfg=123.653, src="H1 FS p6, p92"),
    "9M 2026": dict(revenue=4326.692, gross_profit=1786.361, cogs=2540.331, fv_bio=72.196, selling=-42.183, ga=-220.090,
                    other_inc=290.800, other_exp=-30.279, fin_inc=239.427, fin_cost=-0.174, tax=-353.828, np_owners=1744.886,
                    operating_profit=1856.805, pbt=2097.590, core_profit=1628, prod_cost=2693.683, fg_open=420.616, fg_close=593.244,
                    fg_purch=40.983, ffb_purch=576.888, upkeep=438.172, harvest=477.087, indirect=723.374, dep=292.398, mfg=185.764,
                    src="9M FS p6, p92; Highlights 9M26"),
    "9M 2025": dict(revenue=3956.904, gross_profit=1473.144, cogs=2483.760, operating_profit=1290.253, pbt=1489.836, np_owners=1247.373,
                    core_profit=1249, src="9M FS p6 comparative; Highlights 9M26"),
    "FY 2025": dict(revenue=5512, gross_profit=2261, operating_profit=2008, np_owners=1888, core_profit=1903, src="Highlights FY25"),
}
OPS = {"cpo_prod_kt": {"1Q25": 65, "2Q25": 65, "3Q25": 72, "4Q25": 90, "1Q26": 65, "2Q26": 71, "3Q26": 91},
       "ffb_nucleus_kt": {"1Q25": 251, "2Q25": 254, "3Q25": 293, "4Q25": 341, "1Q26": 243, "2Q26": 262, "3Q26": 345}}  # Highlights 9M26 charts


def quarters() -> pd.DataFrame:
    c = CUM
    q = {}
    q["Q1 2026"] = {k: c["Q1 2026"][k] for k in ("revenue", "gross_profit", "np_owners")}
    q["Q2 2026"] = {k: c["H1 2026"][k] - c["Q1 2026"][k] for k in ("revenue", "gross_profit", "np_owners")}
    q["Q3 2026"] = {k: c["9M 2026"][k] - c["H1 2026"][k] for k in ("revenue", "gross_profit", "np_owners", "cogs", "fv_bio", "selling", "ga",
                                                                    "other_inc", "other_exp", "fin_inc", "tax", "prod_cost", "ffb_purch", "upkeep", "harvest", "indirect", "dep", "mfg")}
    q["Q4 2025"] = {k: c["FY 2025"][k] - c["9M 2025"][k] for k in ("revenue", "gross_profit", "np_owners")}
    # H1 average quarter for the cost bridge
    h1 = {k: c["H1 2026"][k] / 2 for k in ("revenue", "gross_profit", "cogs", "prod_cost", "ffb_purch", "upkeep", "harvest", "indirect", "dep", "mfg")}
    h1["np_owners"] = c["H1 2026"]["np_owners"] / 2
    q["H1 2026 avg quarter"] = h1
    df = pd.DataFrame(q).T
    df["gross_margin"] = df.gross_profit / df.revenue
    return df


def q3_bridge(df: pd.DataFrame) -> pd.DataFrame:
    """Decompose Q3 gross profit vs the H1 average quarter (DER)."""
    c = CUM
    q3, h = df.loc["Q3 2026"], df.loc["H1 2026 avg quarter"]
    d_fg_q3 = c["9M 2026"]["fg_close"] - c["H1 2026"]["fg_close"]          # +220.7 inventory build in Q3
    d_fg_h1 = (c["H1 2026"]["fg_close"] - c["H1 2026"]["fg_open"]) / 2     # -24.1 per H1 quarter (drawdown)
    rows = [("Revenue change", q3.revenue - h.revenue),
            ("Production cost change (more volume, all cost lines)", -(q3.prod_cost - h.prod_cost)),
            ("  of which purchased FFB", -(q3.ffb_purch - h.ffb_purch)),
            ("  of which upkeep & fertiliser", -(q3.upkeep - h.upkeep)),
            ("Finished-goods inventory build (cost capitalised, not expensed)", d_fg_q3 - d_fg_h1),
            ("Other (WIP, purchases of finished goods, own use)", None)]
    gp_change = q3.gross_profit - h.gross_profit
    explained = rows[0][1] + rows[1][1] + rows[4][1]
    rows[5] = (rows[5][0], gp_change - explained)
    rows.append(("= Gross profit change", gp_change))
    return pd.DataFrame(rows, columns=["component", "idr_bn"])


def q4_nowcast(df: pd.DataFrame) -> pd.DataFrame:
    """Q4 2026 scenarios relative to Q3 (EST)."""
    q3 = df.loc["Q3 2026"]
    fg_build_q3 = CUM["9M 2026"]["fg_close"] - CUM["H1 2026"]["fg_close"]
    S = {"bear": dict(vol=0.85, price=-0.10, release=0.0, upkeep_catchup=120, other=40, fv=-30),
         "base": dict(vol=0.95, price=-0.05, release=0.5, upkeep_catchup=60, other=60, fv=0),
         "bull": dict(vol=1.00, price=-0.02, release=1.0, upkeep_catchup=20, other=80, fv=20)}
    rows = []
    for k, s in S.items():
        # revenue from current production and from releasing the Q3 build (release valued at Q3 revenue/cost markup)
        markup = q3.revenue / q3.prod_cost  # revenue per unit of production cost in Q3 (DER)
        rev_prod = q3.revenue * s["vol"] * (1 + s["price"]) * (1 - fg_build_q3 / q3.prod_cost)  # Q3 revenue excluded the built units
        rev_rel = s["release"] * fg_build_q3 * markup * (1 + s["price"])
        prod_cost = q3.prod_cost * s["vol"] + s["upkeep_catchup"]
        cogs = prod_cost * (1 - fg_build_q3 / q3.prod_cost) + s["release"] * fg_build_q3
        rev = rev_prod + rev_rel
        gp = rev - cogs
        pbt = gp + s["fv"] + q3.selling + q3.ga + s["other"] + q3.fin_inc
        np_ = pbt * (1 - 0.169)  # 9M effective tax 353.8 / 2,097.6 = 16.9% (DER)
        rows.append({"scenario": k, **s, "revenue": rev, "cogs": cogs, "gross_profit": gp, "gross_margin": gp / rev, "pbt": pbt,
                     "q4_np_owners": np_, "fy26_np_owners": CUM["9M 2026"]["np_owners"] + np_})
    return pd.DataFrame(rows).set_index("scenario")


def cash_and_buyback() -> dict:
    cash = 8516.274
    related = 115.016 + 550.0  # Bank Ina Perdana current + deposit (p52)
    liabilities = 1595.827
    emp_lt = 552.106
    quarterly_cash_cost = (CUM["9M 2026"]["prod_cost"] - CUM["9M 2026"]["dep"]) / 3 + 90  # DER/EST
    excess = cash - 1.0 * quarterly_cash_cost - emp_lt - 750.0
    bb_shares = 750.0 / PRICE * 1000  # mn shares at current price
    fin_yield = CUM["9M 2026"]["fin_inc"] / 3 * 4 / ((8516.274 + 7597.470) / 2)  # annualised yield on average cash
    lost_income = 750.0 * fin_yield * (1 - 0.2)  # final tax on deposit interest ~20% (EST)
    np_fwd = 2200.0
    eps_before = np_fwd / SHARES
    eps_after = (np_fwd - lost_income) / (SHARES - bb_shares)
    return dict(cash=cash, related_party_cash=related, related_share=related / cash, liabilities=liabilities, employee_benefits_lt=emp_lt,
                operating_buffer=quarterly_cash_cost, excess_cash_after_buyback=excess, excess_cash_per_share=excess / SHARES * 1000,
                buyback_max_bn=750.0, buyback_shares_mn_at_price=bb_shares, buyback_pct_shares=bb_shares / SHARES,
                cash_yield=fin_yield, lost_after_tax_income=lost_income, eps_accretion=eps_after / eps_before - 1)


def gate(nowcast: pd.DataFrame, cb: dict) -> dict:
    """12-month expected return. Price = (cash_t+12 x credit + EV/NP multiple x NP)/shares + dividend.
    Calibration (OBS/DER): FY2025 year-end price 1,195 = (cash 7,597 + 0.3 x NP 1,888)/6,820; now 1,570 = (8,516 + ~1.0 x FY26 cons 2,105)/6,820.
    So the market credits cash at about 100% and values operations at 0.3-1.0x profit."""
    np27 = {"bear": 1800.0, "base": 2200.0, "bull": 2400.0}            # EST (El Nino lag bear; FY26-like base; consensus-like bull)
    mult = {"bear": 0.3, "base": 1.0, "bull": 2.0}                    # EV/NP: FY25 trough / now / FY22-23 level (OBS history)
    prob = {"bear": 0.30, "base": 0.50, "bull": 0.20}                 # EST
    fy26 = nowcast.loc["base", "fy26_np_owners"]
    cash_12m = cb["cash"] + 1800.0 - 0.30 * fy26 - 750.0              # EST: 12m cash generation 1.8tn; FY26 dividend 30% payout; buyback
    shares_12m = SHARES - cb["buyback_shares_mn_at_price"]
    div = 0.30 * fy26 / SHARES * 1000
    res = {}
    for k in ("bear", "base", "bull"):
        px = (cash_12m + mult[k] * np27[k]) / shares_12m * 1000
        res[k] = (px + div) / PRICE - 1
    er = sum(prob[k] * res[k] for k in res)
    rng = np.random.default_rng(20261125)
    W = rng.dirichlet(np.array([0.3, 0.5, 0.2]) * 10, 20000)
    dist = W @ np.array([res["bear"], res["base"], res["bull"]])
    # no-buyback and 80% cash-credit sensitivities
    nb = sum(prob[k] * (((cb["cash"] + 1800 - 0.3 * fy26 + mult[k] * np27[k]) / SHARES * 1000 + div) / PRICE - 1) for k in res)
    c80 = sum(prob[k] * (((0.8 * cash_12m + mult[k] * np27[k]) / shares_12m * 1000 + div) / PRICE - 1) for k in res)
    return dict(scenario_returns=res, expected=er, p05=np.percentile(dist, 5), p95=np.percentile(dist, 95),
                p_gt_hurdle=float((dist > 0.175).mean()), expected_no_buyback=nb, expected_cash_credit_80=c80,
                cash_12m=cash_12m, div=div)


def main() -> int:
    df = quarters()
    br = q3_bridge(df)
    nc = q4_nowcast(df)
    cb = cash_and_buyback()
    g = gate(nc, cb)
    df.to_csv(OUT / "LSIP_quarterly_reconstruction.csv", float_format="%.1f")
    br.to_csv(OUT / "LSIP_q3_gp_bridge.csv", index=False, float_format="%.1f")
    nc.to_csv(OUT / "LSIP_q4_2026_nowcast.csv", float_format="%.2f")
    pd.Series({**cb, **{f"gate_{k}": v for k, v in g.items() if k != "scenario_returns"}, **{f"ret_{k}": v for k, v in g["scenario_returns"].items()}}).to_csv(OUT / "LSIP_stage1_summary.csv")
    print(df.round(1).to_string()); print(br.round(1).to_string()); print(nc.round(1).to_string())
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in cb.items()}); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in g.items() if k != "scenario_returns"}, {k: round(v, 3) for k, v in g["scenario_returns"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
