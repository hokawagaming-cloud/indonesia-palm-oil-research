"""ITMG-C2 (sales volume) and ITMG-C3 (unit cost ex-royalty) walk-forward evaluation implementing
data/reference/research/ITMG_C2_C3_preregistration.json (committed 205218e BEFORE this module was run).

Usage: python -I -X utf8 quant/itmg_c2c3.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bank_mvp_b1 import block_boot_ratio, dm_test, holm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reference" / "research"


def cmo(name: str) -> pd.Series:
    df = pd.read_excel(ROOT / "data" / "raw" / "macro" / "CMO-Historical-Data-Monthly.xlsx", "Monthly Prices", header=None)
    hdr, d = df.iloc[4], df.iloc[6:]
    col = [i for i, h in enumerate(hdr) if isinstance(h, str) and h.startswith(name)][0]
    idx = pd.PeriodIndex([pd.Period(str(x).replace("M", "-"), "M") for x in d[0]], freq="M")
    return pd.Series(pd.to_numeric(d[col], errors="coerce").to_numpy(), index=idx).dropna()


def panel() -> pd.DataFrame:
    F = pd.read_csv(OUT / "ITMG_fs_costs.csv", index_col=0)
    O = pd.read_csv(OUT / "ITMG_ops_extract.csv").set_index("period")
    idx = pd.PeriodIndex(F.index, freq="Q")
    P = pd.DataFrame(index=idx)
    P["sales"] = F.implied_sales_mt.to_numpy()
    P["uc"] = ((F.cost_of_revenue_q - F.royalty_q) / (F.implied_sales_mt * 1000)).to_numpy()
    P["pc"] = (F.coal_purchase_q / (F.implied_sales_mt * 1000)).to_numpy()
    P["gp"] = ((F.coal_revenue_q - F.cost_of_revenue_q) / 1000).to_numpy()        # USD m (coal revenue basis)
    P["asp"] = F.asp_first.to_numpy()
    for c in ("guid_type", "guid_year", "guid_quarter", "guid_value_mt"):
        P[c] = O[c].reindex(F.index).to_numpy()
    N, B = cmo("Coal, Australian"), cmo("Crude oil, Brent")
    P["N"] = [N.loc[q.asfreq("M", "start"):q.asfreq("M", "end")].mean() for q in P.index]
    P["Brent"] = [B.loc[q.asfreq("M", "start"):q.asfreq("M", "end")].mean() for q in P.index]
    return P


def guidance_forecasts(P: pd.DataFrame, q: pd.Period, hist_sales: pd.Series) -> tuple[float, float]:
    """B4 (even run-rate of remaining guidance) and M1 (seasonal allocation) using deck q-1 only."""
    g = P.loc[q - 1] if (q - 1) in P.index else None
    if g is None or pd.isna(g.guid_type):
        return np.nan, np.nan
    Y, k = q.year, q.quarter
    ytd = sum(hist_sales.get(pd.Period(f"{Y}Q{j}", "Q"), np.nan) for j in range(1, k))
    if g.guid_type == "Q" and int(g.guid_year) == Y and int(g.guid_quarter) == k:
        return g.guid_value_mt, g.guid_value_mt
    if g.guid_type == "H1" and int(g.guid_year) == Y and k == 2:
        v = g.guid_value_mt - hist_sales.get(pd.Period(f"{Y}Q1", "Q"), np.nan)
        return v, v
    if g.guid_type == "FY" and int(g.guid_year) == Y:
        rem = g.guid_value_mt - (ytd if k > 1 else 0.0)
        r = 4 - k + 1
        b4 = rem / r
        shares = []
        for yy in sorted({p.year for p in hist_sales.index}):
            qs = [pd.Period(f"{yy}Q{j}", "Q") for j in range(k, 5)]
            if all(x in hist_sales.index and pd.notna(hist_sales[x]) for x in qs) and yy < Y:
                shares.append(hist_sales[qs[0]] / sum(hist_sales[x] for x in qs))
        m1 = rem * float(np.mean(shares)) if shares else np.nan
        return b4, m1
    return np.nan, np.nan


def walk(P: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    c2, c3 = [], []
    for q in P.index:
        if q < pd.Period("2019Q1", "Q") or pd.isna(P.loc[q, "sales"]):
            continue
        H = P.loc[:q - 1]
        hs = H.sales.dropna()
        if (q - 1) not in hs.index:
            continue
        # ---------------- C2
        b4, m1 = guidance_forecasts(P, q, hs)
        r2 = {"q": str(q), "actual": P.loc[q, "sales"], "B1_last": hs.iloc[-1], "B2_seasonal": hs.get(q - 4, np.nan),
              "B3_mean": hs.mean(), "B4_guidance_runrate": b4, "C2_M1_guidance_seasonal_allocation": m1}
        rows = []
        for t in hs.index:
            if (t - 1) in hs.index:
                bt, _ = guidance_forecasts(P, t, P.loc[:t - 1].sales.dropna())
                if pd.notna(bt):
                    rows.append((hs[t], bt, hs[t - 1]))
        if len(rows) >= 12 and pd.notna(b4):
            y, x1, x2 = np.array(rows).T
            b, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(y)), x1, x2]), y, rcond=None)
            r2["C2_M2_guidance_regression"] = b[0] + b[1] * b4 + b[2] * hs.iloc[-1]
        else:
            r2["C2_M2_guidance_regression"] = np.nan
        c2.append(r2)
        # ---------------- C3
        hu = H.uc.dropna()
        if pd.isna(P.loc[q, "uc"]) or (q - 1) not in hu.index:
            continue
        u1, pc1 = hu.iloc[-1], H.loc[q - 1, "pc"]
        r3 = {"q": str(q), "actual": P.loc[q, "uc"], "B1_last": u1, "B2_seasonal": hu.get(q - 4, np.nan), "B3_mean": hu.mean(),
              "B4_rolling4": hu.tail(4).mean(), "B5_brent_scaled": u1 * P.loc[q, "Brent"] / P.loc[q - 1, "Brent"],
              "C3_M2_component_scaling": (u1 - pc1) + pc1 * P.loc[q, "N"] / P.loc[q - 1, "N"]}
        rr = [(np.log(hu[t] / hu[t - 1]), np.log(P.loc[t, "N"] / P.loc[t - 1, "N"]), np.log(P.loc[t, "Brent"] / P.loc[t - 1, "Brent"]))
              for t in hu.index if (t - 1) in hu.index]
        if len(rr) >= 12:
            y, a1, a2 = np.array(rr).T
            b, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(y)), a1, a2]), y, rcond=None)
            r3["C3_M1_commodity_regression"] = u1 * np.exp(b[0] + b[1] * np.log(P.loc[q, "N"] / P.loc[q - 1, "N"]) + b[2] * np.log(P.loc[q, "Brent"] / P.loc[q - 1, "Brent"]))
        else:
            r3["C3_M1_commodity_regression"] = np.nan
        c3.append(r3)
    return pd.DataFrame(c2), pd.DataFrame(c3)


def evaluate(F: pd.DataFrame, bench: list, models: list, P: pd.DataFrame, kind: str) -> dict:
    D = F[pd.PeriodIndex(F.q, freq="Q") >= pd.Period("2021Q1", "Q")].dropna(subset=bench + models).copy()
    a = D.actual.to_numpy()
    E = {m: D[m].to_numpy() - a for m in bench + models}
    mae = {m: float(np.abs(e).mean()) for m, e in E.items()}
    strongest = min(bench, key=lambda m: mae[m])
    ps, dms, cis = {}, {}, {}
    for m in models:
        dms[m], ps[m] = dm_test(E[m], E[strongest]); cis[m] = [float(x) for x in block_boot_ratio(E[m], E[strongest])]
    hp = holm(ps)
    qq = pd.PeriodIndex(D.q, freq="Q")
    gp_med = float(P.loc[qq, "gp"].median())
    res = {"n": len(D), "window": f"{D.q.iloc[0]}..{D.q.iloc[-1]}" if len(D) else None, "strongest_benchmark": strongest, "MAE": mae,
           "RMSE": {m: float(np.sqrt((e ** 2).mean())) for m, e in E.items()}, "bias": {m: float(e.mean()) for m, e in E.items()},
           "OOS_R2_vs_strongest": {m: float(1 - (E[m] ** 2).sum() / (E[strongest] ** 2).sum()) for m in models},
           "models": {}}
    for m in models:
        gain = mae[strongest] - mae[m]
        if kind == "C2":
            econ = gain * float(P.loc[qq - 1, "asp"].median()) * (1 - 0.12)          # USD m per quarter (Mt x USD/t)
        else:
            econ = gain * float(P.loc[qq, "sales"].median())                          # USD m per quarter (USD/t x Mt)
        res["models"][m] = {"MAE": mae[m], "improvement": 1 - mae[m] / mae[strongest], "DM": dms[m], "p_raw": ps[m], "p_holm": hp[m],
                            "ratio_CI90": cis[m], "econ_usd_m_per_q": econ, "median_gp_usd_m": gp_med,
                            "material": bool(econ >= 0.02 * gp_med),
                            "pass": bool(len(D) >= 16 and mae[m] <= 0.85 * mae[strongest] and hp[m] <= 0.05)}
    return res


def main() -> int:
    P = panel()
    C2, C3 = walk(P)
    C2.to_csv(OUT / "ITMG_C2_forecasts.csv", index=False, float_format="%.4f"); C3.to_csv(OUT / "ITMG_C3_forecasts.csv", index=False, float_format="%.4f")
    r2 = evaluate(C2, ["B1_last", "B2_seasonal", "B3_mean", "B4_guidance_runrate"], ["C2_M1_guidance_seasonal_allocation", "C2_M2_guidance_regression"], P, "C2")
    r3 = evaluate(C3, ["B1_last", "B2_seasonal", "B3_mean", "B4_rolling4", "B5_brent_scaled"], ["C3_M1_commodity_regression", "C3_M2_component_scaling"], P, "C3")
    for r in (r2, r3):
        passing = [m for m, v in r["models"].items() if v["pass"]]
        r["classification"] = ("GO" if any(r["models"][m]["material"] and r["models"][m]["ratio_CI90"][1] < 1 for m in passing)
                               else ("CONDITIONAL GO" if passing else "NO-GO"))
    res = {"C2": r2, "C3": r3}
    (OUT / "ITMG_C2_C3_results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
