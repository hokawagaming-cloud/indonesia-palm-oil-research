"""MVP-B1 walk-forward evaluation, implementing data/reference/research/MVP_B1_preregistration.json
(committed 6fe91e3 BEFORE this module was run). Do not change the specification here; variants must be
registered separately.

Usage: python -I -X utf8 quant/bank_mvp_b1.py
"""
from __future__ import annotations

import calendar
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reference" / "research"
SPEC = json.loads((OUT / "MVP_B1_preregistration.json").read_text(encoding="utf-8"))
PL = ["nii", "net_profit", "op_profit", "impairment", "pbt"]
BCA_MISSING = ["2019Q4", "2020Q1", "2020Q4", "2021Q1", "2021Q2"]
TEST_FROM, TEST_TO = pd.Period("2021Q1", "Q"), pd.Period("2026Q3", "Q")
REGIMES = {"R1": ("2021Q1", "2022Q2"), "R2": ("2022Q3", "2023Q4"), "R3": ("2024Q1", "2025Q4"), "R4": ("2026Q1", "2026Q3")}
MONTHLY_FILE = "bank_monthly_extract.csv"   # Phase XI correction runs point this to the _v2 file
IM = ["IM1_x1.5", "IM2_hist_avg_m3", "IM3_last_year_m3", "IM4_seasonal_runrate"]
UNC = ["U1_last_quarter", "U2_seasonal", "U3_expanding_mean", "U4_AR1"]


# ----------------------------------------------------------------------------- data
def load(mode: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """mode 'primary' uses verified dates (unverified -> NaT except quarterly docs, which get the conservative date);
    'conservative' uses the conservative dates throughout."""
    M = pd.read_csv(OUT / MONTHLY_FILE, parse_dates=["avail_verified", "avail_conservative"])
    Q = pd.read_csv(OUT / "bank_quarterly_extract.csv", parse_dates=["avail_verified", "avail_conservative"])
    M["period"] = pd.PeriodIndex(M.period, freq="M")
    Q["period"] = pd.PeriodIndex(Q.period, freq="Q")
    if mode == "primary":
        M["avail"] = M.avail_verified
        Q["avail"] = Q.avail_verified.fillna(Q.avail_conservative)
    else:
        M["avail"] = M.avail_conservative
        Q["avail"] = Q.avail_conservative
    # BBCA quarters without own publication: prior-period column of next year's same-quarter document
    add = []
    for qs in BCA_MISSING:
        p = pd.Period(qs, "Q")
        host = Q[(Q.bank == "BBCA") & (Q.period == p + 4)]
        if host.empty or not Q[(Q.bank == "BBCA") & (Q.period == p)].empty:
            continue
        h = host.iloc[0]
        row = {"bank": "BBCA", "period": p, "source": h.source + " (prior-period column)", "avail": h.avail, "vintage": "comparative"}
        for it in PL + ["np_owners"]:
            row[f"bo_{it}"] = h.get(f"bo_{it}_prior"); row[f"cons_{it}"] = h.get(f"cons_{it}_prior")
        add.append(row)
    Q["vintage"] = "original"
    Q = pd.concat([Q, pd.DataFrame(add)], ignore_index=True).sort_values(["bank", "period"])
    return M, Q


def quarterly_panel(Q: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for b, g in Q.groupby("bank"):
        g = g.set_index("period").sort_index()
        for p in g.index:
            prev = p - 1
            first = p.quarter == 1
            if not first and prev not in g.index:
                continue
            r = {"bank": b, "q": p, "avail": g.loc[p, "avail"] if first else max(g.loc[p, "avail"], g.loc[prev, "avail"])}
            for it in PL:
                r[f"BOQ_{it}"] = g.loc[p, f"bo_{it}"] - (0 if first else g.loc[prev, f"bo_{it}"])
                r[f"BOYTD_{it}"] = g.loc[p, f"bo_{it}"]
            r["T1"] = g.loc[p, "cons_np_owners"] - (0 if first else g.loc[prev, "cons_np_owners"])
            r["T2"] = g.loc[p, "cons_nii"] - (0 if first else g.loc[prev, "cons_nii"])
            r["qdoc_avail"] = g.loc[p, "avail"]
            rows.append(r)
    P = pd.DataFrame(rows)
    P["Adj1"] = P.T1 - P.BOQ_net_profit
    P["Adj2"] = P.T2 - P.BOQ_nii
    return P


def months_of(q: pd.Period) -> tuple[pd.Period, pd.Period, pd.Period]:
    m3 = q.asfreq("M", "end")
    return m3 - 2, m3 - 1, m3


def build_quarter_rows(M: pd.DataFrame, P: pd.DataFrame) -> pd.DataFrame:
    """Per bank-quarter: month-1/2 standalone values, BO2, m3_hist, availability of each piece."""
    rows = []
    for b in P.bank.unique():
        Mb = M[M.bank == b].set_index("period")
        Pb = P[P.bank == b].set_index("q")
        for q in Pb.index.union(pd.PeriodIndex([TEST_TO], freq="Q")):
            m1, m2, m3 = months_of(q)
            if m1 not in Mb.index or m2 not in Mb.index:
                continue
            r = {"bank": b, "q": q, "m2_avail": Mb.loc[m2, "avail"], "m1_avail": Mb.loc[m1, "avail"]}
            # previous quarter-end bank-only YTD
            if q.quarter == 1:
                prev = {it: 0.0 for it in PL}; prev_avail = pd.Timestamp("1900-01-01")
            elif (q - 1) in Pb.index:
                prev = {it: Pb.loc[q - 1, f"BOYTD_{it}"] for it in PL}; prev_avail = Pb.loc[q - 1, "qdoc_avail"]
            elif (m1 - 1) in Mb.index:
                prev = {it: Mb.loc[m1 - 1, f"bo_{it}"] for it in PL}; prev_avail = Mb.loc[m1 - 1, "avail"]
            else:
                continue
            r["prev_avail"] = prev_avail
            for it in PL:
                y1, y2 = Mb.loc[m1, f"bo_{it}"], Mb.loc[m2, f"bo_{it}"]
                r[f"m1_{it}"] = y1 - prev[it]
                r[f"m2_{it}"] = y2 - y1
                r[f"BO2_{it}"] = y2 - prev[it]
                if q in Pb.index:
                    r[f"m3h_{it}"] = Pb.loc[q, f"BOYTD_{it}"] - y2
            r["loan_g"] = (Mb.loc[m2, "bo_loans"] / Mb.loc[m1, "bo_loans"] - 1) if Mb.loc[m1, "bo_loans"] else 0.0
            r["d3_d2"] = calendar.monthrange(m3.year, m3.month)[1] / calendar.monthrange(m2.year, m2.month)[1]
            if q in Pb.index:
                for c in ("T1", "T2", "Adj1", "Adj2", "BOQ_net_profit", "BOQ_nii", "avail"):
                    r[c if c != "avail" else "q_avail"] = Pb.loc[q, c]
            rows.append(r)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- forecasts
def _ratio_med(K: pd.DataFrame, item: str, qoy: int) -> float:
    den = (K[f"m1_{item}"] + K[f"m2_{item}"]) / 2
    rr = (K[f"m3h_{item}"] / den).replace([np.inf, -np.inf], np.nan)
    same = rr[K.q.apply(lambda p: p.quarter) == qoy].dropna()
    use = same if len(same) >= 2 else rr.dropna()
    return float(use.median()) if len(use) else 1.0


def forecast_one(R: pd.DataFrame, row: pd.Series, origin: pd.Timestamp) -> dict | None:
    q = row.q
    K = R[(R.bank == row.bank) & (R.q < q) & R.q_avail.notna() & (R.q_avail <= origin)].copy()
    K = K.dropna(subset=["T1", "T2", "Adj1", "Adj2", "m3h_net_profit", "m3h_nii"]).sort_values("q")
    if len(K) < 4:                                   # spec: minimum_history = 4 quarters
        return None
    last4 = K.tail(4)
    out = {}
    for tgt, np_it, adj, T in (("T1", "net_profit", "Adj1", "T1"), ("T2", "nii", "Adj2", "T2")):
        bo2 = row[f"BO2_{np_it}"]
        adj_last = K[adj].iloc[-1]
        lastyear = K[K.q == q - 4]
        # unconditional
        hist = K.set_index("q")[T]
        out[f"{tgt}|U1_last_quarter"] = hist.iloc[-1]
        out[f"{tgt}|U2_seasonal"] = hist.get(q - 4, np.nan)
        out[f"{tgt}|U3_expanding_mean"] = hist.mean()
        pairs = [(hist.get(p - 1), hist.get(p)) for p in hist.index if (p - 1) in hist.index]
        if len(pairs) >= 8:
            x, y = np.array(pairs).T
            bb, aa = np.polyfit(x, y, 1)
            out[f"{tgt}|U4_AR1"] = aa + bb * hist.iloc[-1]
        else:
            out[f"{tgt}|U4_AR1"] = np.nan
        # information-matched
        out[f"{tgt}|IM1_x1.5"] = 1.5 * bo2 + adj_last
        out[f"{tgt}|IM2_hist_avg_m3"] = bo2 + K[f"m3h_{np_it}"].mean() + adj_last
        if len(lastyear):
            ly = lastyear.iloc[0]
            out[f"{tgt}|IM3_last_year_m3"] = bo2 + ly[f"m3h_{np_it}"] + adj_last
            ratio_c = (last4[T] / last4[f"BOQ_{np_it}"]).mean()
            s = ly[f"m3h_{np_it}"] / ly[f"BO2_{np_it}"] if ly[f"BO2_{np_it}"] else np.nan
            out[f"{tgt}|IM4_seasonal_runrate"] = bo2 * (1 + s) * ratio_c
        else:
            out[f"{tgt}|IM3_last_year_m3"] = out[f"{tgt}|IM4_seasonal_runrate"] = np.nan
    # M1 component model
    g = float(np.clip(row.loan_g if pd.notna(row.loan_g) else 0.0, -0.03, 0.03))
    nii3 = row.m2_nii * row.d3_d2 * (1 + g)
    K["m1_core"] = K.m1_op_profit - K.m1_nii + K.m1_impairment
    K["m2_core"] = K.m2_op_profit - K.m2_nii + K.m2_impairment
    K["m3h_core"] = K.m3h_op_profit - K.m3h_nii + K.m3h_impairment
    rho_core = _ratio_med(K, "core", q.quarter)
    rho_imp = _ratio_med(K, "impairment", q.quarter)
    core12 = ((row.m1_op_profit - row.m1_nii + row.m1_impairment) + (row.m2_op_profit - row.m2_nii + row.m2_impairment)) / 2
    imp12 = (row.m1_impairment + row.m2_impairment) / 2
    core3, imp3 = core12 * rho_core, imp12 * rho_imp
    tax = 1 - row.BO2_net_profit / row.BO2_pbt if row.BO2_pbt else 0.2
    out["T1|M1"] = row.BO2_net_profit + (nii3 + core3 - imp3) * (1 - tax) + last4.Adj1.mean()
    out["T2|M1"] = row.BO2_nii + nii3 + last4.Adj2.mean()
    out["_params"] = dict(rho_core=rho_core, rho_imp=rho_imp, tax=tax, g=g, n_hist=len(K))
    return out


def walk_forward(mode: str) -> pd.DataFrame:
    M, Q = load(mode)
    P = quarterly_panel(Q)
    R = build_quarter_rows(M, P)
    recs = []
    for _, row in R.iterrows():
        if not (TEST_FROM <= row.q <= TEST_TO) or pd.isna(row.get("T1")):
            continue
        if mode == "primary":
            if pd.isna(row.m2_avail):
                recs.append({"bank": row.bank, "q": str(row.q), "excluded": "month-2 date unverified"}); continue
            origin = row.m2_avail
        else:
            m2 = months_of(row.q)[1]
            dl = (m2 + 1).to_timestamp(how="end").normalize()
            origin = max(row.m2_avail, dl) if pd.notna(row.m2_avail) else dl
        if pd.isna(row.prev_avail) or row.prev_avail > origin or (pd.notna(row.m1_avail) and row.m1_avail > origin):
            recs.append({"bank": row.bank, "q": str(row.q), "excluded": "previous quarter-end or month-1 not yet available at origin"}); continue
        f = forecast_one(R, row, origin)
        if f is None:
            recs.append({"bank": row.bank, "q": str(row.q), "excluded": "insufficient history"}); continue
        prm = f.pop("_params")
        rec = {"bank": row.bank, "q": str(row.q), "origin": origin.date(), "excluded": "", "actual_T1": row.T1, "actual_T2": row.T2, **prm}
        rec.update(f)
        # T(q-4) for directional accuracy, as known in the panel
        ly = R[(R.bank == row.bank) & (R.q == row.q - 4)]
        rec["T1_q-4"] = ly.T1.iloc[0] if len(ly) else np.nan
        rec["T2_q-4"] = ly.T2.iloc[0] if len(ly) else np.nan
        recs.append(rec)
    return pd.DataFrame(recs)


# ----------------------------------------------------------------------------- inference
def dm_test(e_m: np.ndarray, e_b: np.ndarray) -> tuple[float, float]:
    d = np.abs(e_m) - np.abs(e_b)
    n = len(d); h = int(np.floor(n ** (1 / 3)))
    dc = d - d.mean()
    v = dc @ dc / n
    for L in range(1, h + 1):
        v += 2 * (1 - L / (h + 1)) * (dc[L:] @ dc[:-L]) / n
    dm = d.mean() / np.sqrt(v / n) if v > 0 else np.nan
    dm_hln = dm * np.sqrt((n - 1) / n)          # HLN correction for 1-step horizon
    p = stats.t.cdf(dm_hln, df=n - 1)            # one-sided: model better if d.mean() < 0
    return float(-dm_hln), float(p)


def holm(ps: dict) -> dict:
    items = sorted(ps.items(), key=lambda kv: kv[1]); m = len(items); out = {}; run = 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p)); out[k] = run
    return out


def block_boot_ratio(e_m, e_b, block=4, reps=5000, seed=20261125):
    rng = np.random.default_rng(seed); n = len(e_m); idx0 = np.arange(n); out = []
    for _ in range(reps):
        starts = rng.integers(0, n, int(np.ceil(n / block)))
        idx = np.concatenate([(s + np.arange(block)) % n for s in starts])[:n]
        out.append(np.abs(e_m[idx]).mean() / np.abs(e_b[idx]).mean())
    return np.percentile(out, [5, 95])


def evaluate(F: pd.DataFrame, bank: str, tgt: str) -> tuple[pd.DataFrame, dict]:
    D = F[(F.bank == bank) & (F.excluded == "")].copy()
    cols = [f"{tgt}|{m}" for m in ["M1"] + IM + UNC]
    D = D.dropna(subset=cols + [f"actual_{tgt}"])
    act = D[f"actual_{tgt}"].to_numpy() / 1e3                     # IDR bn
    E = {m: D[f"{tgt}|{m}"].to_numpy() / 1e3 - act for m in ["M1"] + IM + UNC}
    sse_u3 = (E["U3_expanding_mean"] ** 2).sum()
    ly = D[f"{tgt}_q-4"].to_numpy() / 1e3
    rows = []
    for m, e in E.items():
        da = np.mean(np.sign(e + act - ly) == np.sign(act - ly)) if np.isfinite(ly).all() else np.nan
        rows.append({"bank": bank, "target": tgt, "method": m, "n": len(e), "MAE": np.abs(e).mean(), "RMSE": np.sqrt((e ** 2).mean()),
                     "bias": e.mean(), "OOS_R2_vs_U3": 1 - (e ** 2).sum() / sse_u3, "dir_acc_yoy": da})
    T = pd.DataFrame(rows).set_index("method")
    best_im = T.loc[IM, "MAE"].idxmin(); best_u = T.loc[UNC, "MAE"].idxmin()
    ps = {}; dms = {}
    for b in IM:
        dms[b], ps[b] = dm_test(E["M1"], E[b])
    hp = holm(ps)
    for b in IM + UNC:
        T.loc[b, "M1_MAE_improvement"] = 1 - T.loc["M1", "MAE"] / T.loc[b, "MAE"]
    T["OOS_R2_vs_bestIM"] = 1 - (np.array([(E[m] ** 2).sum() for m in T.index]) / (E[best_im] ** 2).sum())
    ci = block_boot_ratio(E["M1"], E[best_im])
    dm_info, p_info = dm_test(E[best_im], E[best_u])
    res = {"bank": bank, "target": tgt, "n": len(act), "best_IM": best_im, "best_unconditional": best_u,
           "M1_MAE": T.loc["M1", "MAE"], "bestIM_MAE": T.loc[best_im, "MAE"], "bestU_MAE": T.loc[best_u, "MAE"],
           "model_value_improvement": 1 - T.loc["M1", "MAE"] / T.loc[best_im, "MAE"],
           "M1_vs_bestIM_ratio_CI90": [float(ci[0]), float(ci[1])],
           "DM_vs_bestIM": dms[best_im], "p_raw_vs_bestIM": ps[best_im], "p_holm_vs_bestIM": hp[best_im],
           "info_value_improvement": 1 - T.loc[best_im, "MAE"] / T.loc[best_u, "MAE"], "DM_info": dm_info, "p_info": p_info,
           "pass_rule": bool(len(act) >= 16 and T.loc["M1", "MAE"] <= 0.85 * T.loc[best_im, "MAE"] and hp[best_im] <= 0.05)}
    return T.reset_index(), res


def regimes(F: pd.DataFrame, bank: str, best_im: str) -> pd.DataFrame:
    D = F[(F.bank == bank) & (F.excluded == "")].dropna(subset=["T1|M1", f"T1|{best_im}", "actual_T1"]).copy()
    D["qq"] = pd.PeriodIndex(D.q, freq="Q"); rows = []
    for r, (a, b) in REGIMES.items():
        s = D[(D.qq >= pd.Period(a, "Q")) & (D.qq <= pd.Period(b, "Q"))]
        if len(s):
            rows.append({"bank": bank, "regime": r, "n": len(s), "MAE_M1": (s["T1|M1"] - s.actual_T1).abs().mean() / 1e3,
                         f"MAE_{best_im}": (s[f"T1|{best_im}"] - s.actual_T1).abs().mean() / 1e3})
    return pd.DataFrame(rows)


def classify(prim: dict, cons: dict, t2: dict) -> str:
    if prim["pass_rule"] and cons["model_value_improvement"] >= 0.15:
        return "GO"
    if prim["pass_rule"] or t2["pass_rule"] or (prim["info_value_improvement"] >= 0.15 and prim["p_info"] <= 0.05):
        return "CONDITIONAL GO"
    return "NO-GO"


def main() -> int:
    Fp, Fc = walk_forward("primary"), walk_forward("conservative")
    Fp.to_csv(OUT / "MVP_B1_forecasts_primary.csv", index=False, float_format="%.1f")
    Fc.to_csv(OUT / "MVP_B1_forecasts_conservative.csv", index=False, float_format="%.1f")
    tables, results, regs = [], [], []
    for bank in ("BBCA", "BBRI"):
        Tp1, rp1 = evaluate(Fp, bank, "T1"); Tp2, rp2 = evaluate(Fp, bank, "T2"); Tc1, rc1 = evaluate(Fc, bank, "T1")
        for T, s in ((Tp1, "primary"), (Tp2, "primary"), (Tc1, "conservative")):
            tables.append(T.assign(sample=s))
        cls = classify(rp1, rc1, rp2)
        results.append({**{f"primary_T1_{k}": v for k, v in rp1.items()}, **{f"primary_T2_{k}": v for k, v in rp2.items() if k not in ("bank", "target")},
                        **{f"conservative_T1_{k}": v for k, v in rc1.items() if k not in ("bank", "target")}, "classification": cls})
        regs.append(regimes(Fp, bank, rp1["best_IM"]))
    # cross-bank error correlation (M1, T1, common quarters)
    a = Fp[(Fp.bank == "BBCA") & (Fp.excluded == "")].set_index("q"); b = Fp[(Fp.bank == "BBRI") & (Fp.excluded == "")].set_index("q")
    common = a.index.intersection(b.index)
    corr = float(np.corrcoef((a.loc[common, "T1|M1"] - a.loc[common, "actual_T1"]).astype(float), (b.loc[common, "T1|M1"] - b.loc[common, "actual_T1"]).astype(float))[0, 1]) if len(common) > 3 else np.nan
    pd.concat(tables).to_csv(OUT / "MVP_B1_metrics.csv", index=False, float_format="%.4f")
    pd.concat(regs).to_csv(OUT / "MVP_B1_regimes.csv", index=False, float_format="%.3f")
    summ = {"results": results, "cross_bank_M1_error_corr_T1": corr, "n_common_quarters": len(common),
            "excluded_primary": Fp[Fp.excluded != ""][["bank", "q", "excluded"]].to_dict("records")}
    (OUT / "MVP_B1_results.json").write_text(json.dumps(summ, indent=2, default=str), encoding="utf-8")
    pd.set_option("display.width", 250)
    print(pd.concat(tables).round(3).to_string())
    print(json.dumps(summ, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
