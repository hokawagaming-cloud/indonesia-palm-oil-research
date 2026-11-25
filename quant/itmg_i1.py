"""ITMG-I1 integrated gross-profit walk-forward implementing ITMG_I1_preregistration.json (committed 8692b9a
before this module was run). Uses the stored C1/C2/C3 walk-forward forecasts (same origins, same info set).

Usage: python -I -X utf8 quant/itmg_i1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bank_mvp_b1 import block_boot_ratio, dm_test  # noqa: E402
import itmg_c2c3 as c23  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "reference" / "research"


def main() -> int:
    P = c23.panel()
    F = pd.read_csv(OUT / "ITMG_coalrev_royalty.csv", index_col=0) if (OUT / "ITMG_coalrev_royalty.csv").exists() else None
    fs = pd.read_csv(OUT / "ITMG_fs_costs.csv", index_col=0)
    rr = (fs.royalty_q / fs.coal_revenue_q); rr.index = pd.PeriodIndex(rr.index, freq="Q")
    c1 = pd.read_csv(OUT / "ITMG_C1_forecasts.csv").set_index("q")
    c2 = pd.read_csv(OUT / "ITMG_C2_forecasts.csv").set_index("q")
    c3 = pd.read_csv(OUT / "ITMG_C3_forecasts.csv").set_index("q")
    rows = []
    for q in P.index:
        s = str(q)
        if q < pd.Period("2021Q1", "Q") or s not in c1.index or s not in c2.index or s not in c3.index or pd.isna(P.loc[q, "gp"]):
            continue
        hist = P.loc[:q - 1].gp.dropna()
        if (q - 1) not in hist.index or (q - 1) not in rr.index:
            continue
        V, U, r = c2.loc[s, "B2_seasonal"], c3.loc[s, "B1_last"], rr.loc[q - 1]
        def gp(asp):
            return V * asp * (1 - r) - V * U                                    # Mt x USD/t = USD m
        rows.append({"q": s, "actual": P.loc[q, "gp"], "I1": gp(c1.loc[s, "M2_distributed_lag"]),
                     "G1_last": hist.iloc[-1], "G2_seasonal": hist.get(q - 4, np.nan), "G3_same_structure_without_C1": gp(c1.loc[s, "B4_price_scaled"]),
                     "G4_mean": hist.mean(), "gp_prev": hist.iloc[-1]})
    D = pd.DataFrame(rows).dropna()
    D.to_csv(OUT / "ITMG_I1_forecasts.csv", index=False, float_format="%.3f")
    a = D.actual.to_numpy()
    B = ["G1_last", "G2_seasonal", "G3_same_structure_without_C1", "G4_mean"]
    E = {m: D[m].to_numpy() - a for m in ["I1"] + B}
    mae = {m: float(np.abs(e).mean()) for m, e in E.items()}
    strongest = min(B, key=lambda m: mae[m])
    dm_s, p_s = dm_test(E["I1"], E[strongest]); dm_g3, p_g3 = dm_test(E["I1"], E["G3_same_structure_without_C1"])
    res = {"n": len(D), "window": f"{D.q.iloc[0]}..{D.q.iloc[-1]}", "MAE_usd_m": mae,
           "RMSE": {m: float(np.sqrt((e ** 2).mean())) for m, e in E.items()}, "bias": {m: float(e.mean()) for m, e in E.items()},
           "dir_acc_vs_prev": {m: float(np.mean(np.sign(D[m] - D.gp_prev) == np.sign(D.actual - D.gp_prev))) for m in ["I1"] + B},
           "strongest_benchmark": strongest, "improvement_vs_strongest": 1 - mae["I1"] / mae[strongest], "DM_vs_strongest": dm_s, "p_vs_strongest": p_s,
           "ratio_CI90_vs_strongest": [float(x) for x in block_boot_ratio(E["I1"], E[strongest])],
           "C1_translation_improvement_vs_G3": 1 - mae["I1"] / mae["G3_same_structure_without_C1"], "DM_vs_G3": dm_g3, "p_vs_G3": p_g3,
           "I1_error_q10_q90_usd_m": [float(np.quantile(E["I1"], 0.1)), float(np.quantile(E["I1"], 0.9))],
           "median_actual_gp_usd_m": float(np.median(a))}
    res["pass"] = bool(len(D) >= 16 and mae["I1"] <= 0.85 * mae[strongest] and p_s <= 0.05)
    res["C1_translates"] = bool(mae["I1"] <= 0.85 * mae["G3_same_structure_without_C1"] and p_g3 <= 0.05)
    (OUT / "ITMG_I1_results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
