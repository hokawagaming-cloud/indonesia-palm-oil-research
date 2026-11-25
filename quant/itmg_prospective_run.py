"""ITMG prospective forecast run (Phase XIV, D-042). FROZEN models: ITMG-C1 M2 (cb64a27) and ITMG-I1 (8692b9a).

    python -I -X utf8 quant/itmg_prospective_run.py 2026Q4            # real run on the origin date
    python -I -X utf8 quant/itmg_prospective_run.py 2026Q4 --dry-run  # verification: writes only to a dry-run folder

Steps (no model is re-specified or tuned):
 1. Download the World Bank CMO monthly file AS OF NOW, save it with a timestamp under data/raw/macro/cmo_vintages/
    and record its SHA-256 (the 'origin vintage').
 2. If the quarter's third Newcastle month is present -> PRIMARY: C1-M2 exactly as evaluated (quarterly averages of
    3 months). If it is missing -> pre-specified FALLBACK (the delayed-availability sensitivity of Phase XIII,
    ITMG_C1_sensitivity_delayed_month3.json): all quarterly Newcastle averages use the first two months, M2 re-estimated
    the same way. The record states which was used.
 3. I1 gross profit = V x ASP x (1 - r) - V x UC with V = sales(q-4), UC = unit cost(q-1), r = royalty rate(q-1);
    benchmark G3 = same with ASP from B4 (last ASP x Newcastle change).
 4. Prediction intervals: empirical 10%/90% quantiles of the historical walk-forward errors of the same model
    (ITMG_C1_forecasts.csv for M2/B4; ITMG_I1_forecasts.csv for I1/G3).
 5. Write data/reference/prospective/ITMG_<q>_forecast_<UTC timestamp>.json (timestamp, vintage, hashes, git commit,
    spec ids, forecasts, intervals) and APPEND rows to data/reference/forecast_journal.csv (never edits existing rows).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import itmg_c1 as c1  # noqa: E402
import itmg_c2c3 as c23  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
RES = REF / "research"
CMO_URL = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_series(path: Path, name: str) -> pd.Series:
    df = pd.read_excel(path, "Monthly Prices", header=None)
    hdr, d = df.iloc[4], df.iloc[6:]
    col = [i for i, h in enumerate(hdr) if isinstance(h, str) and h.startswith(name)][0]
    idx = pd.PeriodIndex([pd.Period(str(x).replace("M", "-"), "M") for x in d[0]], freq="M")
    return pd.Series(pd.to_numeric(d[col], errors="coerce").to_numpy(), index=idx).dropna()


def c1_forecast(q: pd.Period, N: pd.Series, two_month: bool) -> dict:
    orig = c1.newcastle
    c1.newcastle = lambda: N
    try:
        P = c1.panel()
        allq = P.index.union(pd.PeriodIndex([q], freq="Q"))
        P = P.reindex(allq)
        m = 2 if two_month else 3
        P["N"] = [N.loc[x.asfreq("M", "start"):x.asfreq("M", "start") + (m - 1)].mean() for x in allq]
        P["N1"] = [N.loc[x.asfreq("M", "start") - 1:x.asfreq("M", "end") - 1].mean() for x in allq]
        P.loc[q, "asp"] = np.nan
        return c1.forecast(P, q)
    finally:
        c1.newcastle = orig


def interval(csv: str, model: str, point: float) -> list[float]:
    F = pd.read_csv(RES / csv)
    e = (F[model] - F["actual"]).dropna()
    return [float(point - np.quantile(e, 0.9)), float(point - np.quantile(e, 0.1))]   # actual = forecast - error


def run(quarter: str, dry: bool) -> dict:
    q = pd.Period(quarter, "Q")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    vdir = ROOT / "data" / "raw" / "macro" / "cmo_vintages"; vdir.mkdir(parents=True, exist_ok=True)
    cmo = vdir / f"CMO_origin_{ts}.xlsx"
    req = urllib.request.Request(CMO_URL, headers={"User-Agent": "research-client", "Accept-Encoding": "identity"})
    cmo.write_bytes(urllib.request.urlopen(req, timeout=180).read())
    N = read_series(cmo, "Coal, Australian")
    third = q.asfreq("M", "end")
    mode = "primary" if third in N.index else "fallback_two_month"
    f = c1_forecast(q, N, two_month=(mode != "primary"))
    asp_m2, asp_b4 = float(f["M2_distributed_lag"]), float(f["B4_price_scaled"])
    P = c23.panel()
    fs = pd.read_csv(RES / "ITMG_fs_costs.csv", index_col=0); fs.index = pd.PeriodIndex(fs.index, freq="Q")
    V, U = float(P.loc[q - 4, "sales"]), float(P.loc[q - 1, "uc"])
    r = float(fs.loc[q - 1, "royalty_q"] / fs.loc[q - 1, "coal_revenue_q"])
    gp = lambda a: V * a * (1 - r) - V * U  # noqa: E731
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    rec = {"quarter": quarter, "forecast_timestamp_utc": ts, "mode": mode, "dry_run": dry,
           "origin_vintage": {"file": str(cmo.relative_to(ROOT)), "sha256": sha(cmo), "url": CMO_URL, "last_newcastle_month": str(N.index[-1])},
           "inputs_sha256": {k: sha(RES / k) for k in ("ITMG_quarterly_raw_extract.csv", "ITMG_fs_costs.csv", "ITMG_C1_forecasts.csv", "ITMG_I1_forecasts.csv")},
           "git_commit": commit, "specs": {"C1": "ITMG_C1_preregistration.json (cb64a27)", "I1": "ITMG_I1_preregistration.json (8692b9a)",
                                            "fallback": "ITMG_C1_sensitivity_delayed_month3.json (Phase XIII)"},
           "C1": {"M2_asp": asp_m2, "M2_interval_10_90": interval("ITMG_C1_forecasts.csv", "M2_distributed_lag", asp_m2),
                  "B4_asp": asp_b4, "B4_interval_10_90": interval("ITMG_C1_forecasts.csv", "B4_price_scaled", asp_b4),
                  "interval_note": "empirical 10/90% of historical primary-model errors; for fallback mode this understates uncertainty slightly"},
           "I1": {"inputs": {"V_mt_q-4": V, "UC_usd_t_q-1": U, "royalty_rate_q-1": r},
                  "I1_gp_usd_m": gp(asp_m2), "I1_interval_10_90": interval("ITMG_I1_forecasts.csv", "I1", gp(asp_m2)),
                  "G3_gp_usd_m": gp(asp_b4), "G3_interval_10_90": interval("ITMG_I1_forecasts.csv", "G3_same_structure_without_C1", gp(asp_b4))},
           "resolves_with": f"ITMG {q.quarter}Q{str(q.year)[2:]} analyst presentation (first-reported ASP) and FY FS (gross profit), ~late Feb {q.year + 1}"}
    outdir = REF / "prospective" / ("dry_run" if dry else ""); outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"ITMG_{quarter}_forecast_{ts}.json"
    out.write_text(json.dumps(rec, indent=1, default=float), encoding="utf-8")
    if not dry:
        J = pd.read_csv(REF / "forecast_journal.csv")
        made = ts[:4] + "-" + ts[4:6] + "-" + ts[6:8]
        new = [dict(made_on=made, model_commit=commit[:7] + f"+{mode}", target=t, scenario=s, value_idr_bn=np.nan, status="open (forecast made)",
                    resolves_with=rec["resolves_with"], note=f"{v:.3f}; 10-90% [{lo:.2f}, {hi:.2f}]; record {out.name}")
               for t, s, v, (lo, hi) in [
                   (f"ITMG {quarter} first-reported ASP (USD/t)", "C1-M2 frozen", asp_m2, rec["C1"]["M2_interval_10_90"]),
                   (f"ITMG {quarter} first-reported ASP (USD/t)", "B4 benchmark", asp_b4, rec["C1"]["B4_interval_10_90"]),
                   (f"ITMG {quarter} gross profit coal basis (USD m)", "I1 frozen", rec["I1"]["I1_gp_usd_m"], rec["I1"]["I1_interval_10_90"]),
                   (f"ITMG {quarter} gross profit coal basis (USD m)", "G3 benchmark", rec["I1"]["G3_gp_usd_m"], rec["I1"]["G3_interval_10_90"])]]
        pd.concat([J, pd.DataFrame(new)], ignore_index=True).to_csv(REF / "forecast_journal.csv", index=False)
    return rec


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print(json.dumps(run(args[0] if args else "2026Q4", "--dry-run" in sys.argv), indent=1, default=float))
