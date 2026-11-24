"""Download company financial statements and corporate actions from Yahoo Finance
(source S-020, secondary) and run integrity checks.

Outputs (raw, git-ignored):   data/raw/company/<TICKER>/yahoo_<statement>.csv
Outputs (tracked, derived):   data/reference/<TICKER>_fundamentals_validation.csv
                              data/reference/<TICKER>_corporate_actions.csv

Yahoo statements carry period-end dates only, not filing dates, so they are NOT
point-in-time. Use them with the publication lag in A-005 until official IDX filing
dates are available.

Usage:  python -I quant/fetch_company_fundamentals.py TAPG
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]

STATEMENTS = ["income_stmt", "quarterly_income_stmt", "balance_sheet",
              "quarterly_balance_sheet", "cashflow", "quarterly_cashflow"]
KEY_ROWS = {
    "income": ["Total Revenue", "Cost Of Revenue", "Gross Profit", "Operating Income",
               "Earnings From Equity Interest Net Of Tax", "Earnings From Equity Interest",
               "Pretax Income", "Tax Provision", "Net Income Common Stockholders",
               "Basic EPS", "EBITDA"],
    "balance": ["Total Assets", "Total Liabilities Net Minority Interest",
                "Total Equity Gross Minority Interest", "Investments In Other Ventures Under Equity Method",
                "Long Term Equity Investment", "Total Debt", "Cash And Cash Equivalents"],
    "cashflow": ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
                 "Cash Dividends Paid", "Dividends Received Cfi", "Dividend Received Cfo"],
}


def check_rows(df: pd.DataFrame, kind: str) -> list[dict]:
    out = []
    for col in df.columns:
        for row in KEY_ROWS[kind]:
            if row in df.index:
                v = df.at[row, col]
                out.append({"statement": kind, "period_end": col.date(), "item": row,
                            "value": None if pd.isna(v) else float(v),
                            "missing": bool(pd.isna(v))})
    return out


def main(ticker: str) -> int:
    raw = ROOT / "data" / "raw" / "company" / ticker
    ref = ROOT / "data" / "reference"
    raw.mkdir(parents=True, exist_ok=True)
    t = yf.Ticker(f"{ticker}.JK")
    frames = {}
    for name in STATEMENTS:
        df = getattr(t, name)
        frames[name] = df
        df.to_csv(raw / f"yahoo_{name}.csv")

    checks = []
    for name, kind in [("income_stmt", "income"), ("quarterly_income_stmt", "income"),
                       ("balance_sheet", "balance"), ("quarterly_balance_sheet", "balance"),
                       ("cashflow", "cashflow"), ("quarterly_cashflow", "cashflow")]:
        for r in check_rows(frames[name], kind):
            r["frequency"] = "quarterly" if name.startswith("quarterly") else "annual"
            checks.append(r)
    val = pd.DataFrame(checks)

    # Integrity tests
    tests = []
    for name in ["balance_sheet", "quarterly_balance_sheet"]:
        b = frames[name]
        need = ["Total Assets", "Total Liabilities Net Minority Interest",
                "Total Equity Gross Minority Interest"]
        if all(n in b.index for n in need):
            for c in b.columns:
                a, l, e = (b.at[n, c] for n in need)
                if pd.notna(a) and pd.notna(l) and pd.notna(e):
                    gap = abs(a - (l + e)) / a
                    tests.append({"test": f"{name}: assets = liabilities + equity",
                                  "period_end": c.date(), "result": "PASS" if gap < 1e-3 else "FAIL",
                                  "detail": f"rel. gap {gap:.2e}"})
    inc_a, inc_q = frames["income_stmt"], frames["quarterly_income_stmt"]
    for row in ["Total Revenue", "Net Income Common Stockholders"]:
        if row in inc_a.index and row in inc_q.index:
            for c in inc_a.columns:
                qs = [q for q in inc_q.columns if q.year == c.year]
                if len(qs) == 4:
                    s = inc_q.loc[row, qs].sum(min_count=4)
                    a = inc_a.at[row, c]
                    res = "PASS" if pd.notna(s) and abs(s - a) / abs(a) < 0.005 else "FAIL"
                    tests.append({"test": f"sum of 4 quarters = annual ({row})",
                                  "period_end": c.date(), "result": res, "detail": f"{s:.4g} vs {a:.4g}"})
                else:
                    tests.append({"test": f"sum of 4 quarters = annual ({row})",
                                  "period_end": c.date(), "result": "NOT TESTABLE",
                                  "detail": f"{len(qs)} quarters available"})
    expected_q = pd.period_range("2025Q1", pd.Period(inc_q.columns.max(), "Q"), freq="Q")
    have_q = {pd.Period(c, "Q") for c in inc_q.columns}
    missing_q = [str(p) for p in expected_q if p not in have_q]
    tests.append({"test": "quarterly income statement continuity", "period_end": None,
                  "result": "FAIL" if missing_q else "PASS",
                  "detail": "missing: " + (", ".join(missing_q) or "none")})

    pd.concat([val.assign(kind="value"), pd.DataFrame(tests).assign(kind="test")],
              ignore_index=True).to_csv(ref / f"{ticker}_fundamentals_validation.csv", index=False)

    div = t.dividends
    ca = pd.DataFrame({"ex_date": div.index.date, "event": "cash dividend",
                       "amount_idr_per_share": div.values, "source": "S-020 Yahoo (secondary)"})
    for d, r in t.splits.items():
        ca.loc[len(ca)] = [d.date(), f"split {r}", None, "S-020 Yahoo (secondary)"]
    ca.sort_values("ex_date").to_csv(ref / f"{ticker}_corporate_actions.csv", index=False)

    print(pd.DataFrame(tests).to_string(index=False))
    print(f"\n{len(ca)} corporate actions; statement periods:")
    for n, f in frames.items():
        print(f"  {n}: {[c.date().isoformat() for c in f.columns]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "TAPG"))
