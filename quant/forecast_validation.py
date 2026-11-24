"""Predictive validation of TAPG quarterly earnings methods (Phase III, P5) + forecast journal.

Targets: profit to owners and revenue per discrete quarter (data/reference/TAPG_quarterly_derived.csv).
Methods (simple, reproducible benchmarks):
  last_q     y_q = y_{q-1}
  seasonal   y_q = y_{q-4}
  price_last y_q = y_{q-1} x P_q / P_{q-1}   (P = World Bank palm oil IDR/kg, quarterly avg)
  price_seas y_q = y_{q-4} x P_q / P_{q-4}
Two evaluations:
  PIT       a forecast for quarter q may use only quarters whose PIT availability
            (quant/pit_panel.py, strict) is strictly before q's own availability date,
            and price data available under A-014.
  hindsight all quarters in hand regardless of availability (NOT a valid test; reported
            only to show the scale of errors).
The Q4 2026 scenario model itself cannot be back-tested: it relies on broker-reported
Q3 operating inputs that exist only for 3Q26. It is classified EXPLORATORY, and forecasts
are logged in data/reference/forecast_journal.csv for forward testing.

Usage: python -I -X utf8 quant/forecast_validation.py
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"


def quarterly_prices() -> pd.Series:
    m = pd.read_csv(REF / "macro_monthly.csv", index_col=0)
    m.index = pd.PeriodIndex(m.index, freq="M")
    return m["palm_oil_idr_kg"].groupby(m.index.asfreq("Q")).mean()


def evaluate() -> tuple[pd.DataFrame, pd.DataFrame]:
    q = pd.read_csv(REF / "TAPG_quarterly_derived.csv")
    p = quarterly_prices()
    out = []
    for item in ["profit_attrib_owners", "revenue"]:
        s = q[q["item"] == item].copy()
        s["per"] = pd.PeriodIndex(s.quarter.str[:4] + "Q" + s.quarter.str[-1], freq="Q")
        s = s.set_index("per")
        for t in s.index:
            # a real-time forecast must be made before the target was FIRST public (original filing),
            # not before the date we happen to hold it
            orig = s.at[t, "original_publication_date"] if "original_publication_date" in s.columns else None
            avail_t = pd.Timestamp(orig) if isinstance(orig, str) else pd.Timestamp(s.at[t, "available_from"])
            for name, lag, scaled in (("last_q", 1, False), ("seasonal", 4, False), ("price_last", 1, True), ("price_seas", 4, True)):
                b = t - lag
                if b not in s.index:
                    continue
                pit_ok = pd.Timestamp(s.at[b, "available_from"]) < avail_t
                yhat = s.at[b, "value_idr_mn"] * (p[t] / p[b] if scaled else 1.0)
                out.append({"item": item, "quarter": str(t), "method": name, "pit_valid": pit_ok,
                            "actual": s.at[t, "value_idr_mn"] / 1e3, "forecast": yhat / 1e3})
    E = pd.DataFrame(out)
    E["err"] = E.forecast - E.actual
    E["pct_err"] = E.err / E.actual
    rows = []
    for (item, method, mode), g in [((i, m, "PIT"), E[(E["item"] == i) & (E.method == m) & E.pit_valid]) for i in E["item"].unique() for m in E.method.unique()] + \
                                   [((i, m, "hindsight"), E[(E["item"] == i) & (E.method == m)]) for i in E["item"].unique() for m in E.method.unique()]:
        rows.append({"item": item, "method": method, "evaluation": mode, "n": len(g),
                     "MAE_bn": g.err.abs().mean() if len(g) else np.nan,
                     "RMSE_bn": float(np.sqrt((g.err ** 2).mean())) if len(g) else np.nan,
                     "bias_bn": g.err.mean() if len(g) else np.nan,
                     "MAPE": g.pct_err.abs().mean() if len(g) else np.nan})
    return E, pd.DataFrame(rows)


def journal() -> pd.DataFrame:
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    sc = pd.read_csv(REF / "research" / "TAPG_q4_2026_scenarios.csv", index_col=0)
    fy27 = pd.read_csv(REF / "research" / "TAPG_fy2027_quarterly.csv")
    made = "2026-11-24"
    rows = []
    for s in ["bear", "base", "bull"]:
        rows.append(dict(made_on=made, model_commit=sha, target="TAPG 2026Q4 profit to owners", scenario=s, value_idr_bn=round(sc.loc[s, "net_profit_owners"], 1)))
        rows.append(dict(made_on=made, model_commit=sha, target="TAPG FY2026 profit to owners", scenario=s, value_idr_bn=round(sc.loc[s, "fy26_net_profit"], 1)))
        rows.append(dict(made_on=made, model_commit=sha, target="TAPG FY2027 profit to owners", scenario=s, value_idr_bn=round(fy27[fy27.scenario == s].net_profit_owners.sum(), 1)))
        for _, r in fy27[fy27.scenario == s].iterrows():
            rows.append(dict(made_on=made, model_commit=sha, target=f"TAPG {r.quarter} profit to owners", scenario=s, value_idr_bn=round(r.net_profit_owners, 1)))
    for tgt, v in [("TAPG 2026Q4 profit to owners", 714.4), ("TAPG FY2026 profit to owners", 4220.0), ("TAPG FY2027 profit to owners", 4473.0)]:
        rows.append(dict(made_on=made, model_commit="external", target=tgt, scenario="consensus (S&P, S-036/S-040)", value_idr_bn=v))
    # superseded versions of our Q4 base, kept for the audit trail
    for v, note, tag in [(1341.2, "superseded: inventory double-count (D-015)", "pre-fix-D015"), (1267.8, "superseded: other operating items at Q3 level (D-018)", "pre-fix-D018")]:
        rows.append(dict(made_on=made, model_commit=tag, target="TAPG 2026Q4 profit to owners", scenario="base", value_idr_bn=v, status=note))
    J = pd.DataFrame(rows)
    J["status"] = J.get("status").fillna("open") if "status" in J else "open"
    J["resolves_with"] = J.target.map(lambda t: "FY2026 audited FS (IDX, expected by ~31 Mar 2027)" if ("2026" in t) else "2027 interim/annual filings")
    J["actual_idr_bn"] = np.nan
    path = REF / "forecast_journal.csv"
    if path.exists():
        old = pd.read_csv(path)
        # append-only: never drop an existing row; only add rows not already present (full-key match)
        key = ["made_on", "target", "scenario", "value_idr_bn"]  # same forecast re-logged under a new commit is not new
        new = J.merge(old[key].drop_duplicates(), on=key, how="left", indicator=True)
        J = pd.concat([old, new[new["_merge"] == "left_only"].drop(columns="_merge")], ignore_index=True)
    J.to_csv(path, index=False)
    return J


def main() -> int:
    E, M = evaluate()
    E.to_csv(REF / "research" / "TAPG_validation_errors.csv", index=False, float_format="%.2f")
    M.to_csv(REF / "research" / "TAPG_validation_metrics.csv", index=False, float_format="%.3f")
    J = journal()
    md = ["# TAPG — Predictive Validation (Phase III, P5)", "",
          "_Generated by `quant/forecast_validation.py`. IDR bn. 'PIT' = forecast uses only data whose verified availability (strict vintage rule) precedes the target quarter's ORIGINAL publication date. 'Hindsight' is NOT a valid test._", "",
          "| Target | Method | Evaluation | n | MAE | RMSE | Bias | MAPE |", "|---|---|---|---|---|---|---|---|"]
    for _, r in M.sort_values(["item", "evaluation", "method"]).iterrows():
        md.append(f"| {r['item']} | {r.method} | {r.evaluation} | {r.n} | {r.MAE_bn:,.0f} | {r.RMSE_bn:,.0f} | {r.bias_bn:+,.0f} | {r.MAPE:.1%} |" if r.n else f"| {r['item']} | {r.method} | {r.evaluation} | 0 | – | – | – | – |")
    md += ["", "## Classification", "",
           f"- **Point-in-time sample:** at most {int(M[M.evaluation == 'PIT'].n.max())} quarterly forecasts can be evaluated. The 2025 quarters are only verifiable from the 2026 filings (D-014), so seasonal benchmarks have no PIT observations at all.",
           "- **The Q4 2026 scenario model cannot be back-tested.** It depends on broker-reported Q3 operating inputs that exist only for 3Q26.",
           "- **Classification: EXPLORATORY.** No predictive accuracy is claimed.",
           f"- **Forward testing:** {len(J)} dated forecasts are logged in `data/reference/forecast_journal.csv`. They cover Q4 2026, FY2026, FY2027 and each 2027 quarter, our three scenarios and consensus, plus superseded versions. They resolve against the FY2026 audited FS (expected by about 31 Mar 2027) and the 2027 filings.",
           "- **To enable real validation:**",
           "  - Obtain the 2021–2025 interim filings and newsletters (original vintages), which would give about 20 quarters.",
           "  - Then re-run this module with the scenario model in place of the benchmarks."]
    (ROOT / "research" / "company" / "TAPG" / "validation.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
