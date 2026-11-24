"""Feasibility study for a TAPG quarterly revenue and earnings nowcast (Phase II, P5).

Only transparent, accounting-driven forms; no machine learning. No quarterly
operational data exists in the filings, so quarterly volume is NOT observed and none is
fabricated. Three things are tested:

  A. Annual price pass-through: realised CPO ASP (consolidated, AR) vs the World Bank
     palm oil price converted to IDR/kg (S-003 x IDR=X). The ratio captures the domestic
     discount (export levy and duty, freight, basis). Is it stable enough to map an
     observable price into an ASP?
  B. Quarterly revenue vs price: price-deflated revenue (revenue_q / price_q) shows the
     implied volume pattern (an index, not tonnes).
  C. Naive nowcasts, evaluated pseudo-out-of-sample on the few quarters available:
       N1 revenue_q = revenue_{q-4} x price_q / price_{q-4}   (same-quarter volume)
       N2 revenue_q = revenue_{q-1} x price_q / price_{q-1}   (last-quarter volume)
     The same price ratio is applied to the JV share; cost of sales is carried at its
     q-4 level to give a gross-profit nowcast. These are benchmarks for future models,
     not validated forecasts: n = 3 to 6 quarters.

Price availability: World Bank monthly averages are published early in the following
month (A-014), i.e. before TAPG's interim filing (about a month after quarter-end).

Outputs: data/reference/research/TAPG_nowcast_*.csv
         research/company/TAPG/nowcast_feasibility.md
Usage:   python -I -X utf8 quant/tapg_nowcast_feasibility.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
OUT = REF / "research"


def main() -> int:
    mac = pd.read_csv(REF / "macro_monthly.csv", index_col=0)
    mac.index = pd.PeriodIndex(mac.index, freq="M")
    p_m = mac["palm_oil_idr_kg"]
    p_q = p_m.groupby(p_m.index.asfreq("Q")).mean()
    p_y = p_m.groupby(p_m.index.year).mean()

    cons = pd.read_csv(REF / "TAPG_scope_consolidated.csv")
    v = cons.set_index(["item", "period"])["value"]

    # A. annual ASP vs world price ------------------------------------------------------
    rows = []
    for y in range(2020, 2026):
        asp = v.get(("asp_cpo_idr_per_kg", f"FY{y}"))
        if asp is not None:
            rows.append({"year": y, "asp_cpo_idr_kg": asp, "wb_palm_idr_kg": p_y.get(y),
                         "ratio_asp_to_world": asp / p_y.get(y)})
    A = pd.DataFrame(rows)
    A.to_csv(OUT / "TAPG_nowcast_asp_passthrough.csv", index=False, float_format="%.4f")

    # B/C. quarterly ----------------------------------------------------------------------
    q = pd.read_csv(REF / "TAPG_quarterly_derived.csv")
    piv = q.pivot(index="quarter", columns="item", values="value_idr_mn")
    piv.index = pd.PeriodIndex([f"{s[:4]}Q{s[-1]}" for s in piv.index], freq="Q")
    # FY2024 quarters are not in hand; get Q4 2024 etc. only if available (they are not)
    df = pd.DataFrame({"revenue": piv["revenue"], "cost_of_sales": piv["cost_of_sales"],
                       "gross_profit": piv["gross_profit"], "share_jv": piv.get("share_of_profit_jv"),
                       "price_idr_kg": p_q.reindex(piv.index)})
    df["deflated_revenue_index"] = df.revenue / df.price_idr_kg
    df["deflated_revenue_index"] /= df["deflated_revenue_index"].mean()

    res = []
    for i, t in enumerate(df.index):
        for name, lag in (("N1_same_quarter", 4), ("N2_last_quarter", 1)):
            b = t - lag
            if b in df.index and pd.notna(df.loc[b, "revenue"]):
                ratio = df.loc[t, "price_idr_kg"] / df.loc[b, "price_idr_kg"]
                rev_hat = df.loc[b, "revenue"] * ratio
                gp_hat = rev_hat + df.loc[b, "cost_of_sales"]  # cost carried (negative sign)
                jv_hat = df.loc[b, "share_jv"] * ratio if pd.notna(df.loc[b, "share_jv"]) else np.nan
                res.append({"quarter": str(t), "model": name, "base_quarter": str(b), "price_ratio": ratio,
                            "revenue_actual": df.loc[t, "revenue"], "revenue_nowcast": rev_hat,
                            "revenue_err_pct": rev_hat / df.loc[t, "revenue"] - 1,
                            "gp_actual": df.loc[t, "gross_profit"], "gp_nowcast": gp_hat,
                            "gp_err_pct": gp_hat / df.loc[t, "gross_profit"] - 1,
                            "jv_actual": df.loc[t, "share_jv"], "jv_nowcast": jv_hat,
                            "jv_err_pct": jv_hat / df.loc[t, "share_jv"] - 1 if pd.notna(df.loc[t, "share_jv"]) else np.nan})
    R = pd.DataFrame(res)
    R.to_csv(OUT / "TAPG_nowcast_pseudo_oos.csv", index=False, float_format="%.4f")
    df.to_csv(OUT / "TAPG_nowcast_quarterly_panel.csv", float_format="%.4f")

    def summ(m, col):
        s = R[R.model == m][col].dropna()
        return f"n={len(s)}, mean abs error {s.abs().mean():.1%}, worst {s.abs().max():.1%}" if len(s) else "n=0"

    md = ["# TAPG — Earnings Nowcast Feasibility (Phase II, P5)", "",
          "_Generated by `quant/tapg_nowcast_feasibility.py`. Nothing here is a validated forecast. The samples are tiny, and no quarterly operational data was available or fabricated._", "",
          "## A. Does the world CPO price map into TAPG's realised ASP? (annual, consolidated scope)", "",
          "| Year | Realised CPO ASP (IDR/kg) | World Bank palm oil (IDR/kg, annual avg) | ASP ÷ world |", "|---|---|---|---|"]
    md += [f"| {int(r.year)} | {r.asp_cpo_idr_kg:,.0f} | {r.wb_palm_idr_kg:,.0f} | {r.ratio_asp_to_world:.2f} |" for r in A.itertuples()]
    md += ["", f"Ratio range {A.ratio_asp_to_world.min():.2f}–{A.ratio_asp_to_world.max():.2f} (mean {A.ratio_asp_to_world.mean():.2f}). It moves with export levy and duty policy, so a nowcast must model the levy/duty schedule (S-010/S-011, still uncompiled) rather than assume a constant discount.", "",
           "## B. Quarterly revenue vs price (consolidated)", "",
           "| Quarter | Revenue (IDR bn) | WB price (IDR/kg, qtr avg) | Price-deflated revenue index |", "|---|---|---|---|"]
    md += [f"| {t} | {r.revenue/1e3:,.1f} | {r.price_idr_kg:,.0f} | {r.deflated_revenue_index:.2f} |" for t, r in df.iterrows()]
    md += ["", "The deflated index stands in for sales volume (and timing of sales). Without quarterly production or sales volumes (gap G1) it cannot be split into harvest seasonality, inventory timing (the H1 2026 'earlier revenue recognition' cited by brokers), and product mix.", "",
           "## C. Naive pseudo-out-of-sample nowcasts", "",
           f"- **N1 (same-quarter volume, price-scaled):** revenue {summ('N1_same_quarter','revenue_err_pct')}; gross profit {summ('N1_same_quarter','gp_err_pct')}; JV share {summ('N1_same_quarter','jv_err_pct')}.",
           f"- **N2 (last-quarter volume, price-scaled):** revenue {summ('N2_last_quarter','revenue_err_pct')}; gross profit {summ('N2_last_quarter','gp_err_pct')}; JV share {summ('N2_last_quarter','jv_err_pct')}.",
           "",
           "| Quarter | Model | Revenue actual | Revenue nowcast | Error | GP error | JV-share error |", "|---|---|---|---|---|---|---|"]
    md += [f"| {r.quarter} | {r.model} | {r.revenue_actual/1e3:,.1f} | {r.revenue_nowcast/1e3:,.1f} | {r.revenue_err_pct:+.1%} | {r.gp_err_pct:+.1%} | {r.jv_err_pct:+.1%} |" for r in R.itertuples()]
    md += ["", "Gross-profit errors are larger than revenue errors because costs are carried unchanged while revenue moves (operating leverage); fertiliser timing within the year adds noise.", "",
           "## Verdict", "",
           "1. **A transparent revenue nowcast is feasible in structure** (volume × realised price, plus PK/PKO), and the inputs it needs are published before TAPG reports. With price alone, and no quarterly volume, the error is too large and too poorly estimated (n ≤ 6) for anything to be claimed.",
           "2. **Binding constraints:**",
           "   - Quarterly production and sales volumes (G1). Company presentations or broker notes are needed; Q1 2026 press coverage quotes FFB production, which shows the company does disclose these quarterly somewhere.",
           "   - The levy and duty schedule, to model the domestic discount.",
           "   - A daily or monthly domestic CPO price (KPBN) with history (G10).",
           "3. **Earnings nowcast:** needs a cost model (fertiliser timing, purchased-FFB cost tied to the FFB price) and a separate USTP model, because the JV share is about 23% of PBT and scales with USTP's own volume and price. Accounting identities are ready (scope-separated datasets, quarterly derivation).",
           "4. **Next step:** obtain quarterly operational data for 2021–2026. Then fit the volume × price × discount model on 2021–2024 and validate out of sample on 2025–2026 before any use."]
    (ROOT / "research" / "company" / "TAPG" / "nowcast_feasibility.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
