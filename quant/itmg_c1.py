"""ITMG-C1 walk-forward evaluation implementing data/reference/research/ITMG_C1_preregistration.json
(committed cb64a27 BEFORE this module was run). Specification must not be changed here.

Usage: python -I -X utf8 quant/itmg_c1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bank_mvp_b1 import block_boot_ratio, dm_test, holm  # noqa: E402  (same inference code as MVP-B1)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reference" / "research"
BENCH = ["B1_last", "B2_seasonal", "B3_mean", "B4_price_scaled", "B5_rolling_discount", "B6_lagged_newc_reg"]
MODELS = ["M1_fixed_lag", "M2_distributed_lag", "M4_dom_export_decomposition"]
REGIMES = {"R1_spike": ("2021Q2", "2022Q4"), "R2_normalisation": ("2023Q1", "2026Q3")}


def newcastle() -> pd.Series:
    df = pd.read_excel(ROOT / "data" / "raw" / "macro" / "CMO-Historical-Data-Monthly.xlsx", "Monthly Prices", header=None)
    hdr, d = df.iloc[4], df.iloc[6:]
    col = [i for i, h in enumerate(hdr) if isinstance(h, str) and h.startswith("Coal, Australian")][0]
    idx = pd.PeriodIndex([pd.Period(str(x).replace("M", "-"), "M") for x in d[0]], freq="M")
    return pd.Series(pd.to_numeric(d[col], errors="coerce").to_numpy(), index=idx).dropna()


def panel() -> pd.DataFrame:
    E = pd.read_csv(OUT / "ITMG_quarterly_raw_extract.csv")
    E["q"] = pd.PeriodIndex(E.period, freq="Q")
    N = newcastle()
    P = E.set_index("q")[["asp_usd_t", "domestic_share", "sales_mt"]].rename(columns={"asp_usd_t": "asp", "domestic_share": "s"})
    allq = pd.period_range("2017Q1", "2026Q3", freq="Q")
    P = P.reindex(allq)
    P["N"] = [N.loc[q.asfreq("M", "start"):q.asfreq("M", "end")].mean() for q in allq]
    P["N1"] = [N.loc[q.asfreq("M", "start") - 1:q.asfreq("M", "end") - 1].mean() for q in allq]
    P["s_known"] = P.s.ffill()                      # last available domestic share (missing -> last available)
    return P


def ols(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b


def forecast(P: pd.DataFrame, q: pd.Period) -> dict | None:
    hist = P.loc[:q - 1].dropna(subset=["asp"])          # quarters reported before the origin (q-1 and earlier)
    hist = hist.loc[pd.Period("2018Q1", "Q"):]
    if len(hist) < 4 or (q - 1) not in hist.index:
        return None
    a1, N_q, N_p, N1_q, N1_p = hist.loc[q - 1, "asp"], P.loc[q, "N"], P.loc[q - 1, "N"], P.loc[q, "N1"], P.loc[q - 1, "N1"]
    f = {"B1_last": a1, "B2_seasonal": hist.asp.get(q - 4, np.nan), "B3_mean": hist.asp.mean(),
         "B4_price_scaled": a1 * N_q / N_p, "B5_rolling_discount": N_q * (hist.asp / hist.N).tail(4).mean()}
    # B6: ASP_t = a + b N_(t-1)
    rows = [(hist.loc[t, "asp"], P.loc[t - 1, "N"]) for t in hist.index]
    if len(rows) >= 8:
        y, x = np.array(rows).T
        b = ols(y, np.column_stack([np.ones(len(x)), x])); f["B6_lagged_newc_reg"] = b[0] + b[1] * N_p
    else:
        f["B6_lagged_newc_reg"] = np.nan
    # M1: one-month-lag price scaling
    f["M1_fixed_lag"] = a1 * N1_q / N1_p
    # M2: dlogASP_t = a + b0 dlogN_t + b1 dlogN_(t-1)
    rr = []
    for t in hist.index:
        if (t - 1) in hist.index:
            rr.append((np.log(hist.loc[t, "asp"] / hist.loc[t - 1, "asp"]), np.log(P.loc[t, "N"] / P.loc[t - 1, "N"]),
                       np.log(P.loc[t - 1, "N"] / P.loc[t - 2, "N"])))
    if len(rr) >= 12:
        y, x0, x1 = np.array(rr).T
        b = ols(y, np.column_stack([np.ones(len(y)), x0, x1]))
        f["M2_distributed_lag"] = a1 * np.exp(b[0] + b[1] * np.log(N_q / N_p) + b[2] * np.log(N_p / P.loc[q - 2, "N"]))
    else:
        f["M2_distributed_lag"] = np.nan
    # M4: ASP_t = k (1-s_t) N_t + D s_t
    h4 = hist.dropna(subset=["s"])
    if len(h4) >= 12:
        b = ols(h4.asp.to_numpy(), np.column_stack([(1 - h4.s) * h4.N, h4.s]))
        s_prev = P.loc[q - 1, "s_known"]
        f["M4_dom_export_decomposition"] = b[0] * (1 - s_prev) * N_q + b[1] * s_prev
        f["M4_k"], f["M4_D"] = b[0], b[1]
    else:
        f["M4_dom_export_decomposition"] = np.nan
    return f


def main() -> int:
    P = panel()
    recs = []
    for q in pd.period_range("2019Q1", "2026Q3", freq="Q"):
        if pd.isna(P.loc[q, "asp"]):
            continue
        f = forecast(P, q)
        if f is None:
            continue
        recs.append({"q": str(q), "actual": P.loc[q, "asp"], "asp_prev": P.loc[q - 1, "asp"], **f})
    F = pd.DataFrame(recs)
    F.to_csv(OUT / "ITMG_C1_forecasts.csv", index=False, float_format="%.3f")
    D = F.dropna(subset=BENCH + MODELS).copy()
    act = D.actual.to_numpy()
    E = {m: D[m].to_numpy() - act for m in BENCH + MODELS}
    mae = {m: np.abs(e).mean() for m, e in E.items()}
    strongest = min(BENCH, key=lambda m: mae[m])
    sse_b3, sse_s = (E["B3_mean"] ** 2).sum(), (E[strongest] ** 2).sum()
    rows = []
    for m, e in E.items():
        rows.append({"method": m, "n": len(e), "MAE": mae[m], "RMSE": np.sqrt((e ** 2).mean()), "bias": e.mean(),
                     "OOS_R2_vs_B3": 1 - (e ** 2).sum() / sse_b3, "OOS_R2_vs_strongest": 1 - (e ** 2).sum() / sse_s,
                     "dir_acc": np.mean(np.sign(D[m] - D.asp_prev) == np.sign(D.actual - D.asp_prev)),
                     "improvement_vs_strongest": 1 - mae[m] / mae[strongest]})
    T = pd.DataFrame(rows)
    ps, dms, cis = {}, {}, {}
    for m in MODELS:
        dms[m], ps[m] = dm_test(E[m], E[strongest])
        cis[m] = [float(x) for x in block_boot_ratio(E[m], E[strongest])]
    hp = holm(ps)
    res = {"n": len(D), "test_window": f"{D.q.iloc[0]}..{D.q.iloc[-1]}", "strongest_benchmark": strongest,
           "strongest_MAE": mae[strongest],
           "models": {m: {"MAE": mae[m], "improvement": 1 - mae[m] / mae[strongest], "DM": dms[m], "p_raw": ps[m], "p_holm": hp[m],
                          "ratio_CI90": cis[m], "pass": bool(len(D) >= 16 and mae[m] <= 0.85 * mae[strongest] and hp[m] <= 0.05)} for m in MODELS}}
    # regimes (descriptive)
    D["qq"] = pd.PeriodIndex(D.q, freq="Q"); reg = []
    for r, (a, b) in REGIMES.items():
        s = D[(D.qq >= pd.Period(a, "Q")) & (D.qq <= pd.Period(b, "Q"))]
        reg.append({"regime": r, "n": len(s), **{m: float((s[m] - s.actual).abs().mean()) for m in BENCH + MODELS}})
    # economic materiality vs strongest benchmark for the best model
    best = min(MODELS, key=lambda m: mae[m])
    vol = float(P.sales_mt.dropna().median())
    gain = mae[strongest] - mae[best]
    res["economics"] = {"best_model": best, "MAE_reduction_usd_t": gain, "median_verified_sales_mt": vol,
                        "revenue_error_reduction_usd_m_per_q": gain * vol, "ebitda_error_reduction_usd_m_per_q": gain * vol * (1 - 0.135),
                        "median_asp_test": float(np.median(act)), "reduction_pct_of_median_asp": gain / float(np.median(act)),
                        "material": bool(gain / float(np.median(act)) >= 0.02)}
    any_pass = any(v["pass"] for v in res["models"].values())
    mat = res["economics"]["material"]
    passing = [m for m, v in res["models"].items() if v["pass"]]
    ci_ok = all(res["models"][m]["ratio_CI90"][1] < 1.0 for m in passing) if passing else False
    res["classification"] = "GO" if (any_pass and mat and ci_ok) else ("CONDITIONAL GO" if any_pass else "NO-GO")
    T.to_csv(OUT / "ITMG_C1_metrics.csv", index=False, float_format="%.4f")
    pd.DataFrame(reg).to_csv(OUT / "ITMG_C1_regimes.csv", index=False, float_format="%.2f")
    (OUT / "ITMG_C1_results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    pd.set_option("display.width", 220)
    print(T.round(3).to_string()); print(pd.DataFrame(reg).round(1).to_string()); print(json.dumps(res, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
