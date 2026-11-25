"""M-VIII-1: pre-registered walk-forward test of CPIN segment margins (D-029).

H1 (primary, pre-registered 2026-11-25 before any fit):
    dm_q = a + b1 * d(spread)_q + b2 * dlog(USDIDR)_(q-1) + e,  forecast m_q = m_(q-1) + dm_hat
    m = broiler segment result / broiler segment sales (standalone quarter, CPIN_segments_quarterly.csv)
    spread = PIHPS producer chicken price - feed proxy (A-037), IDR/kg, quarterly mean of monthly values
Benchmarks: last_q (m_(q-1)); seasonal (m_(q-4)); expanding mean (same basis).
PIT: forecast for q is made the day before q's filing deadline (A-038). Only observations whose
available_from precedes that date are used; dm only within one reporting basis (FY2020 restatement).
Kill rule: continue only if, on >= 16 common out-of-sample quarters, model MAE <= 0.85 x best benchmark
MAE AND Diebold-Mariano t (HAC, absolute loss) >= 1.65. Secondary targets are reported, not decisive.

Usage: python -I -X utf8 quant/cpin_walkforward.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_utils import ols_nw  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
OUT = REF / "research"
MIN_TRAIN = 12
KILL = dict(min_n=16, mae_ratio=0.85, dm_t=1.65)
TARGETS = {"broiler": "primary", "consolidated": "secondary", "doc": "secondary", "feed": "secondary"}


def features() -> pd.DataFrame:
    m = pd.read_csv(REF / "poultry_prices_monthly.csv", index_col=0)
    m.index = pd.PeriodIndex(m.index, freq="M")
    m["spread"] = m.chicken_producer - m.feed_proxy_idr_kg
    q = m[["chicken_producer", "feed_proxy_idr_kg", "spread", "usdidr"]].groupby(m.index.asfreq("Q")).mean()
    q["n_months_price"] = m.chicken_producer.notna().groupby(m.index.asfreq("Q")).sum()
    q["d_spread"] = q.spread.diff()
    q["dlog_fx_lag"] = np.log(q.usdidr).diff().shift(1)
    return q


def load_target(seg: str) -> pd.DataFrame:
    d = pd.read_csv(OUT / "CPIN_segments_quarterly.csv", parse_dates=["available_from"])
    d["period"] = pd.PeriodIndex(d.period, freq="Q")
    d = d.set_index("period").sort_index()
    return pd.DataFrame({"m": d[f"margin_{seg}"], "basis": d.basis, "avail": d.available_from})


def walk_forward(seg: str) -> pd.DataFrame:
    y = load_target(seg)
    X = features()
    rows = []
    for q in y.index:
        t = y.loc[q, "avail"] - pd.Timedelta(days=1)                  # forecast date
        known = y[(y.avail < t) & (y.index < q)]
        if (q - 1) not in known.index or known.loc[q - 1, "basis"] != y.loc[q, "basis"]:
            continue
        # training pairs: consecutive, same basis, both known
        tr = []
        for p in known.index:
            if (p - 1) in known.index and known.loc[p - 1, "basis"] == known.loc[p, "basis"] and p in X.index:
                tr.append({"p": p, "dm": known.loc[p, "m"] - known.loc[p - 1, "m"],
                           "d_spread": X.loc[p, "d_spread"], "dlog_fx_lag": X.loc[p, "dlog_fx_lag"]})
        tr = pd.DataFrame(tr).dropna()
        if len(tr) < MIN_TRAIN or q not in X.index or X.loc[q, ["d_spread", "dlog_fx_lag"]].isna().any():
            continue
        A = np.column_stack([np.ones(len(tr)), tr.d_spread, tr.dlog_fx_lag])
        b, *_ = np.linalg.lstsq(A, tr.dm.to_numpy(), rcond=None)
        dm_hat = b[0] + b[1] * X.loc[q, "d_spread"] + b[2] * X.loc[q, "dlog_fx_lag"]
        m1 = known.loc[q - 1, "m"]
        same = known[known.basis == y.loc[q, "basis"]]
        seas = same.loc[q - 4, "m"] if (q - 4) in same.index else np.nan
        rows.append({"period": str(q), "forecast_date": t.date().isoformat(), "actual": y.loc[q, "m"], "n_train": len(tr),
                     "model": m1 + dm_hat, "last_q": m1, "seasonal": seas, "mean": same.m.mean(),
                     "b_spread_per_1000idr": b[1] * 1000, "b_fx": b[2]})
    return pd.DataFrame(rows)


def evaluate(wf: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    meth = ["model", "last_q", "seasonal", "mean"]
    c = wf.dropna(subset=meth)
    met = []
    for k in meth:
        e = c[k] - c.actual
        met.append({"method": k, "n": len(e), "MAE_pp": e.abs().mean() * 100, "RMSE_pp": np.sqrt((e ** 2).mean()) * 100,
                    "bias_pp": e.mean() * 100})
    M = pd.DataFrame(met).set_index("method")
    best = M.drop("model").MAE_pp.idxmin()
    d = (c["model"] - c.actual).abs() - (c[best] - c.actual).abs()
    nw = ols_nw(pd.Series(d.to_numpy()), pd.DataFrame(index=range(len(d))), lags=None) if len(d) > 3 else None
    dm_t = float(-nw.loc["const", "t_nw"]) if nw is not None else np.nan   # >0 means the model is better
    ratio = M.loc["model", "MAE_pp"] / M.loc[best, "MAE_pp"]
    verdict = {"n_common": len(c), "best_benchmark": best, "mae_ratio": ratio, "dm_t": dm_t,
               "pass": bool(len(c) >= KILL["min_n"] and ratio <= KILL["mae_ratio"] and dm_t >= KILL["dm_t"])}
    return M, verdict


def in_sample(seg: str) -> pd.DataFrame:
    y, X = load_target(seg), features()
    pairs = [{"dm": y.loc[p, "m"] - y.loc[p - 1, "m"], "d_spread": X.loc[p, "d_spread"] / 1000, "dlog_fx_lag": X.loc[p, "dlog_fx_lag"]}
             for p in y.index if (p - 1) in y.index and y.loc[p - 1, "basis"] == y.loc[p, "basis"] and p in X.index]
    P = pd.DataFrame(pairs).dropna()
    r = ols_nw(P.dm, P[["d_spread", "dlog_fx_lag"]])
    r.attrs["n"] = len(P)
    return r


def posthoc_levels(seg: str) -> dict:
    """POST-HOC diagnostic (specified AFTER seeing H1 fail; not decision-relevant):
    m_q = a + b * spread_q within the current basis, same PIT walk-forward, vs the expanding mean."""
    y, X = load_target(seg), features()
    e_mod, e_mean = [], []
    for q in y.index:
        t = y.loc[q, "avail"] - pd.Timedelta(days=1)
        known = y[(y.avail < t) & (y.index < q) & (y.basis == y.loc[q, "basis"])]
        known = known[known.index.isin(X.index)]
        if len(known) < MIN_TRAIN or q not in X.index or pd.isna(X.loc[q, "spread"]):
            continue
        A = np.column_stack([np.ones(len(known)), X.loc[known.index, "spread"]])
        b, *_ = np.linalg.lstsq(A, known.m.to_numpy(), rcond=None)
        e_mod.append(b[0] + b[1] * X.loc[q, "spread"] - y.loc[q, "m"]); e_mean.append(known.m.mean() - y.loc[q, "m"])
    e_mod, e_mean = np.array(e_mod), np.array(e_mean)
    d = np.abs(e_mod) - np.abs(e_mean)
    nw = ols_nw(pd.Series(d), pd.DataFrame(index=range(len(d))))
    return {"n": len(d), "MAE_levels_pp": np.abs(e_mod).mean() * 100, "MAE_mean_pp": np.abs(e_mean).mean() * 100,
            "dm_t": float(-nw.loc["const", "t_nw"])}


def main() -> int:
    summ, allwf = [], []
    for seg, role in TARGETS.items():
        wf = walk_forward(seg)
        M, v = evaluate(wf)
        ins = in_sample(seg)
        wf.insert(0, "target", seg); allwf.append(wf)
        for meth, r in M.iterrows():
            summ.append({"target": seg, "role": role, "method": meth, **r.to_dict()})
        summ.append({"target": seg, "role": role, "method": "VERDICT", "n": v["n_common"], "best_benchmark": v["best_benchmark"],
                     "mae_ratio": v["mae_ratio"], "dm_t": v["dm_t"], "pass": v["pass"],
                     "insample_b_spread_per_1000": ins.loc["d_spread", "coef"], "insample_t_spread": ins.loc["d_spread", "t_nw"],
                     "insample_t_fx": ins.loc["dlog_fx_lag", "t_nw"], "insample_r2": ins.attrs["r2"], "insample_n": ins.attrs["n"]})
        ph = posthoc_levels(seg)
        summ.append({"target": seg, "role": "POST-HOC diagnostic (levels)", "method": "levels_vs_mean", "n": ph["n"],
                     "MAE_pp": ph["MAE_levels_pp"], "best_benchmark": "mean",
                     "mae_ratio": ph["MAE_levels_pp"] / ph["MAE_mean_pp"], "dm_t": ph["dm_t"]})
        print(f"\n== {seg} ({role}) ==\n{M.round(2).to_string()}\nverdict {v}")
        print("POST-HOC levels:", {k: round(float(x), 3) for k, x in ph.items()})
        print(f"in-sample: b_spread/1000IDR={ins.loc['d_spread','coef']:.4f} t={ins.loc['d_spread','t_nw']:.2f}; t_fx={ins.loc['dlog_fx_lag','t_nw']:.2f}; R2={ins.attrs['r2']:.2f}; n={ins.attrs['n']}")
    pd.concat(allwf).to_csv(OUT / "CPIN_walkforward_forecasts.csv", index=False, float_format="%.5f")
    pd.DataFrame(summ).to_csv(OUT / "CPIN_walkforward_metrics.csv", index=False, float_format="%.4f")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
