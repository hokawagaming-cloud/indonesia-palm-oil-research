"""Phase IX, Priority 1: final CPIN point-in-time audit (v2). Original v1 outputs are NOT modified
(CPIN_segments_quarterly.csv, CPIN_walkforward_*.csv stay as committed in 48b33ca).

Corrections:
 1. Reporting deadline vs ACTUAL filing: IDX filing timestamps from the jejaksaham.id mirror
    (S-060; covers Jul 2023 onward only). Availability = filing day if filed before 09:00 WIB, else
    next IDX trading day (A-018). Earlier quarters keep the regulatory deadline, flagged 'deadline'.
 2. FY2023: the original FY2023 FS is not on cp.co.id. The 2023 Annual Report (S-061) MD&A gives
    rounded FY2023 segment results: broiler -0.42tn and DOC -0.30tn agree with the FY2024 comparative,
    but feed 4.11tn vs 4.556tn comparative does NOT (restated/reclassified). So the FY2023 values are
    comparative-vintage only and become available from the FY2024 filing (18 Mar 2025 20:35 WIB).
 3. Predictor publication: PIHPS daily final by 13:00 WIB (monthly mean after month end; no vintage
    archive, revisions unverifiable); World Bank CMO monthly, ~2nd business day of the next month
    (single vintage downloaded 2026-11-24; historical revisions possible); USD/IDR Yahoo. Every forecast
    date (day before actual availability) is checked to be after the last predictor month's publication.
Then reruns H1 (pre-registered) and H2 (post-hoc levels) diagnostics against ALL benchmarks, and
writes the frozen H2 specification.

Usage: python -I -X utf8 quant/cpin_pit_v2.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpin_segments as seg  # noqa: E402
import cpin_walkforward as wf  # noqa: E402
from stats_utils import ols_nw  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
OUT = REF / "research"
JJ = ROOT / "data" / "raw" / "company" / "CPIN" / "jejaksaham"
FREEZE_DATE = "2026-11-25"
CMO_PUB_LAG_DAYS = 7   # conservative: Pink Sheet ~2nd business day; 7 calendar days allowed


def trading_days() -> pd.DatetimeIndex:
    d = pd.read_csv(ROOT / "data" / "raw" / "ohlcv" / "IHSG.csv", index_col=0, parse_dates=True)
    return d.index.normalize()


def filings() -> pd.DataFrame:
    """FS filing timestamps (WIB) parsed from the mirror; mapped to reporting period."""
    rows = []
    for f in sorted(JJ.glob("p*.html")):
        t = f.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'aria-label="CPIN: ([^"]*)" href="[^"]*id=(\d{14})', t):
            title = html.unescape(m.group(1))
            if re.search(r"Laporan Keuangan (Interim|Tahunan)", title) and "Laporan Informasi" not in title:
                rows.append({"ts": pd.Timestamp(m.group(2)[:8] + " " + m.group(2)[8:]), "title": title})
    F = pd.DataFrame(rows).drop_duplicates().sort_values("ts")
    # period = last quarter END strictly before the filing (interim) / previous year-end (annual)
    F["period"] = [((pd.Period(ts, "Q") - 1) if "Tahunan" not in ti else pd.Period(f"{ts.year - 1}Q4", "Q")) for ts, ti in zip(F.ts, F.title)]
    F["correction"] = F.title.str.contains("KOREKSI")
    first = F[~F.correction].groupby("period").ts.min().rename("filed_ts")
    corr = F[F.correction].groupby("period").ts.max().rename("correction_ts")
    return pd.concat([first, corr], axis=1)


def avail_from_ts(ts: pd.Timestamp, td: pd.DatetimeIndex) -> pd.Timestamp:
    day = ts.normalize()
    if ts.hour < 9 and day in td:
        return day
    nxt = td[td > day]
    return nxt[0] if len(nxt) else day + pd.Timedelta(days=1)


def build_v2() -> pd.DataFrame:
    q1 = pd.read_csv(OUT / "CPIN_segments_quarterly.csv", parse_dates=["available_from"])   # v1 (unchanged)
    q1["period"] = pd.PeriodIndex(q1.period, freq="Q")
    F, td = filings(), trading_days()
    q = q1.set_index("period").copy()
    q["deadline"] = [seg.deadline(p) for p in q.index]
    q["filed_ts"] = F.filed_ts.reindex(q.index)
    q["date_basis"] = np.where(q.filed_ts.notna(), "actual IDX filing (S-060)", "regulatory deadline (actual unverified)")
    q["available_from"] = [avail_from_ts(ts, td) if pd.notna(ts) else dl for ts, dl in zip(q.filed_ts, q.deadline)]
    # 2020 new-basis values: only from the 2021 interim filings (comparatives) -> keep v1 dates (deadlines of 2021 reports)
    for p in ["2020Q1", "2020Q2", "2020Q3"]:
        q.loc[pd.Period(p, "Q"), ["available_from", "date_basis"]] = [q1.set_index("period").loc[pd.Period(p, "Q"), "available_from"],
                                                                      "comparative in 2021 interim (deadline of host report)"]
    # FY2023 -> 2023Q4 standalone = FY23 (comparative in FY2024 FS) - 9M23: available from the FY2024 filing
    fy24 = F.filed_ts.get(pd.Period("2024Q4", "Q"))
    q.loc[pd.Period("2023Q4", "Q"), ["available_from", "date_basis"]] = [avail_from_ts(fy24, td),
                                                                         "FY2023 comparative in FY2024 FS (original unverified; AR2023 feed differs)"]
    q["available_from"] = pd.to_datetime(q.available_from)
    q["deadline_minus_available_days"] = (q.deadline - q.available_from).dt.days
    return q


def predictor_check(q: pd.DataFrame) -> pd.DataFrame:
    """Last predictor month = quarter's last month; CMO published by month end + 7 days."""
    out = []
    for p, r in q.iterrows():
        fdate = r.available_from - pd.Timedelta(days=1)
        last_m = p.asfreq("M", "end")
        cmo_pub = last_m.to_timestamp(how="end").normalize() + pd.Timedelta(days=CMO_PUB_LAG_DAYS)
        out.append({"period": str(p), "forecast_date": fdate.date(), "cmo_last_month_published_by": cmo_pub.date(), "ok": fdate >= cmo_pub})
    return pd.DataFrame(out)


def run_diagnostics(qv2: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rerun H1 walk-forward and H2 levels walk-forward with v2 availability; all benchmarks."""
    tmp = OUT / "_cpin_q_v2_tmp.csv"
    qv2.reset_index().assign(available_from=qv2.available_from.values).to_csv(tmp, index=False)
    orig = wf.load_target

    def load_v2(segname: str) -> pd.DataFrame:
        d = pd.read_csv(tmp, parse_dates=["available_from"])
        d["period"] = pd.PeriodIndex(d.period, freq="Q")
        d = d.set_index("period").sort_index()
        return pd.DataFrame({"m": d[f"margin_{segname}"], "basis": d.basis, "avail": d.available_from})

    wf.load_target = load_v2
    rows, fc = [], []
    X = wf.features()
    try:
        for s, role in wf.TARGETS.items():
            h1 = wf.walk_forward(s)
            M, v = wf.evaluate(h1)
            h1.insert(0, "target", s); h1.insert(1, "hypothesis", "H1"); fc.append(h1)
            for meth, r in M.iterrows():
                rows.append({"target": s, "role": role, "hypothesis": "H1 (pre-registered)", "method": meth, **r.to_dict()})
            rows.append({"target": s, "role": role, "hypothesis": "H1 (pre-registered)", "method": "VERDICT", "n": v["n_common"],
                         "best_benchmark": v["best_benchmark"], "mae_ratio": v["mae_ratio"], "dm_t": v["dm_t"], "pass": v["pass"]})
            # H2 levels: forecasts + all benchmarks on the common set
            y = load_v2(s); recs = []
            for p in y.index:
                t = y.loc[p, "avail"] - pd.Timedelta(days=1)
                known = y[(y.avail < t) & (y.index < p) & (y.basis == y.loc[p, "basis"])]
                known = known[known.index.isin(X.index)]
                if len(known) < wf.MIN_TRAIN or p not in X.index or pd.isna(X.loc[p, "spread"]) or (p - 1) not in known.index:
                    continue
                A = np.column_stack([np.ones(len(known)), X.loc[known.index, "spread"]])
                b, *_ = np.linalg.lstsq(A, known.m.to_numpy(), rcond=None)
                recs.append({"period": str(p), "actual": y.loc[p, "m"], "H2": b[0] + b[1] * X.loc[p, "spread"],
                             "last_q": known.loc[p - 1, "m"], "seasonal": known.loc[p - 4, "m"] if (p - 4) in known.index else np.nan,
                             "mean": known.m.mean(), "n_train": len(known)})
            H = pd.DataFrame(recs)
            Hc = H.dropna()
            for bm in ("last_q", "seasonal", "mean"):
                d = (Hc.H2 - Hc.actual).abs() - (Hc[bm] - Hc.actual).abs()
                nw = ols_nw(pd.Series(d.to_numpy()), pd.DataFrame(index=range(len(d)))) if len(d) > 3 else None
                rows.append({"target": s, "role": role, "hypothesis": "H2 (post-hoc levels, diagnostic)", "method": f"H2_vs_{bm}",
                             "n": len(Hc), "MAE_pp": (Hc.H2 - Hc.actual).abs().mean() * 100, "best_benchmark": bm,
                             "mae_ratio": (Hc.H2 - Hc.actual).abs().mean() / (Hc[bm] - Hc.actual).abs().mean(),
                             "dm_t": float(-nw.loc["const", "t_nw"]) if nw is not None else np.nan})
            H.insert(0, "target", s); H.insert(1, "hypothesis", "H2"); fc.append(H)
    finally:
        wf.load_target = orig
        tmp.unlink(missing_ok=True)
    return pd.DataFrame(rows), pd.concat(fc, ignore_index=True)


def freeze_h2(qv2: pd.DataFrame) -> dict:
    X = wf.features()
    y = qv2[qv2.basis == "new"]
    y = y[(y.available_from <= pd.Timestamp(FREEZE_DATE)) & y.index.isin(X.index)]
    A = np.column_stack([np.ones(len(y)), X.loc[y.index, "spread"]])
    b, *_ = np.linalg.lstsq(A, y.margin_broiler.to_numpy(), rcond=None)
    spec = {
        "id": "CPIN-H2", "status": "FROZEN exploratory hypothesis (post-hoc origin; NOT validated)", "frozen_on": FREEZE_DATE,
        "target": "CPIN broiler segment margin = segment result / total broiler segment sales, standalone quarter, new (FY2020) basis",
        "model": "m_q = a + b * spread_q", "a": float(b[0]), "b_per_idr_kg": float(b[1]),
        "fit_sample": f"{y.index.min()}..{y.index.max()} (n={len(y)}, values available by {FREEZE_DATE})",
        "predictors": {"spread_q": "mean over the 3 months of q of [PIHPS national producer 'Daging Ayam Ras Segar' (IDR/kg) "
                       "- (0.55*WB CMO maize + 0.25*WB CMO soybean meal, USD/t) * monthly-average USD/IDR / 1000]",
                       "sources": ["S-054 PIHPS", "S-003 World Bank CMO", "S-002 USD/IDR"]},
        "forecast_timing": "day before CPIN's actual IDX filing for q (availability rule A-018); predictors must be published by then",
        "benchmarks": ["last_q: m_(q-1)", "seasonal: m_(q-4)", "mean: expanding mean of new-basis actuals known at forecast date"],
        "parameters_frozen": True, "re_estimation": "none (a, b fixed); benchmarks update with new actuals as they become available",
        "evaluation": {"first_quarter": "2026Q4", "interim_review_n": 8, "final_n": 12,
                       "pass_rule": "on n>=12 prospective quarters: MAE(H2) <= 0.85 x MAE of EACH benchmark AND Diebold-Mariano t (HAC, absolute loss) >= 1.65 vs the best benchmark",
                       "kill_rule": "fails pass_rule at n=12, or MAE(H2) > MAE(best benchmark) at the n=8 interim review"},
        "journal_note": "The 2026-11-25 journal entry (10.0%) used a partial-quarter spread and is kept as logged; the frozen-rule forecast for 2026Q4 is computed at its forecast date.",
    }
    return spec


def main() -> int:
    qv2 = build_v2()
    pc = predictor_check(qv2)
    diag, fcs = run_diagnostics(qv2)
    spec = freeze_h2(qv2)
    keep = ["basis", "deadline", "filed_ts", "available_from", "date_basis", "deadline_minus_available_days", "source"]
    qv2.reset_index().to_csv(OUT / "CPIN_segments_quarterly_v2.csv", index=False, float_format="%.4f")
    pc.to_csv(OUT / "CPIN_predictor_timing_check.csv", index=False)
    diag.to_csv(OUT / "CPIN_walkforward_metrics_v2.csv", index=False, float_format="%.4f")
    fcs.to_csv(OUT / "CPIN_walkforward_forecasts_v2.csv", index=False, float_format="%.5f")
    (OUT / "CPIN_H2_frozen_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    pd.set_option("display.width", 250)
    print(qv2[keep].to_string())
    print("predictor timing violations:", int((~pc.ok).sum()), "of", len(pc))
    print(diag[diag.method.isin(["VERDICT", "H2_vs_last_q", "H2_vs_seasonal", "H2_vs_mean"])][["target", "hypothesis", "method", "n", "best_benchmark", "mae_ratio", "dm_t", "pass"]].round(3).to_string())
    print(json.dumps({k: spec[k] for k in ("a", "b_per_idr_kg", "fit_sample")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
