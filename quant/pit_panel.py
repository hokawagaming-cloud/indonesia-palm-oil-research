"""Vintage-aware point-in-time panel for TAPG financial statements (audit finding A).

Problem fixed: values taken from a LATER document (comparative columns, possibly
restated) were previously stamped with the EARLIER period's disclosure date. Example:
Q1 2025 figures come from the Q1 2026 filing's comparative column, but were dated to
the Q1 2025 filing (2025-04-30), which is not in hand.

Each row is one VINTAGE: (item, reporting_period, source document). Fields:
  reporting_period            the fiscal period the number describes
  source_doc / vintage_role   document providing the value; 'current' or 'comparative'
  original_publication_date   date the period's OWN original filing became available
                              (A-018 timestamp); that filing may not be in hand
  original_filing_in_hand     whether the value we hold comes from that original filing
  vintage_available_from      availability of the document that provides THIS value
  revision_date               availability date of a vintage whose value differs from
                              the earlier vintage (empty if no revision)
  earliest_verified_availability  first date on which the value WE HOLD is verifiably
                              public = vintage_available_from of the earliest vintage
                              in hand
Use `asof(item, period, date)` for backtests; never the original publication date
unless original_filing_in_hand is True.

Outputs: data/reference/TAPG_pit_vintages.csv, data/reference/TAPG_pit_quarterly.csv
Usage:   python -I -X utf8 quant/pit_panel.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
STOCK = {"cash", "total_assets", "total_equity", "investment_in_jv", "investment_in_associates", "fixed_assets_net"}
# document -> (own reporting period label, disclosure kind in TAPG_disclosure_dates.csv)
DOC_PERIOD = {
    "AR 2021.pdf": ("FY2021", "audited FS"), "AR_2022.pdf": ("FY2022", "audited FS"),
    "AR_2023.pdf": ("FY2023", "audited FS"), "AR_2024.pdf": ("FY2024", "audited FS"),
    "TAPG_-_AR_2025.pdf": ("FY2025", "audited FS"),
    "FinancialStatement-2026-I-TAPG.pdf": ("Q1 2026", "interim FS"),
    "FinancialStatement-2026-II-TAPG.pdf": ("H1 2026", "interim FS"),
    "FinancialStatement-2026-III-TAPG.pdf": ("9M 2026", "interim FS"),
}


def _dates() -> pd.DataFrame:
    d = pd.read_csv(REF / "TAPG_disclosure_dates.csv")
    return d[d.disclosure.isin(["interim FS", "audited FS"])].set_index("period")


def build_vintages() -> pd.DataFrame:
    st = pd.read_csv(REF / "TAPG_statements_extracted.csv")
    st = st[st.status == "extracted"].copy()
    dates = _dates()
    st["vintage_role"] = [("current" if DOC_PERIOD[d][0] == p else "comparative") for d, p in zip(st.source_doc, st.period)]
    st["vintage_available_from"] = [dates.at[DOC_PERIOD[d][0], "available_from"] for d in st.source_doc]
    st["vintage_basis"] = [dates.at[DOC_PERIOD[d][0], "basis"].split(":")[0] for d in st.source_doc]
    st["original_publication_date"] = [dates.at[p, "available_from"] if p in dates.index else None for p in st.period]
    st["original_filing_in_hand"] = st.vintage_role.eq("current")
    st = st.sort_values(["item", "period", "vintage_available_from"])
    out = []
    for (item, period), g in st.groupby(["item", "period"], sort=False):
        g = g.drop_duplicates(["source_doc"]).copy()
        first_val = g["value"].iloc[0]
        g["revision_vs_first_vintage"] = g["value"] - first_val
        g["revision_date"] = np.where(g["value"].ne(g["value"].shift()) & g.index.isin(g.index[1:]),
                                      g["vintage_available_from"], None)
        g["earliest_verified_availability"] = g["vintage_available_from"].iloc[0]
        out.append(g)
    v = pd.concat(out)
    cols = ["item", "period", "period_end", "months", "value", "unit", "source_doc", "pdf_page", "vintage_role",
            "original_publication_date", "original_filing_in_hand", "vintage_available_from", "vintage_basis",
            "revision_date", "revision_vs_first_vintage", "earliest_verified_availability", "basis"]
    v = v.rename(columns={"period": "period"})[cols].rename(columns={"period": "reporting_period"})
    return v


def asof(v: pd.DataFrame, item: str, period: str, date) -> float:
    """Latest vintage of (item, period) whose document was available on `date`; NaN if none."""
    d = pd.Timestamp(date)
    g = v[(v["item"] == item) & (v.reporting_period == period)]
    g = g[pd.to_datetime(g.vintage_available_from) <= d]
    return float(g.sort_values("vintage_available_from")["value"].iloc[-1]) if len(g) else float("nan")


def build_quarterly(v: pd.DataFrame) -> pd.DataFrame:
    """Discrete quarters as first computable from documents in hand. Each quarter's
    available_from is the latest availability among the input vintages used."""
    rows = []
    flows = sorted(set(v["item"]) - STOCK)
    for year in (2025, 2026):
        lab = {"Q1": f"Q1 {year}", "H1": f"H1 {year}", "9M": f"9M {year}", "FY": f"FY{year}"}
        for item in flows:
            g = v[v["item"] == item]
            # earliest vintage per cumulative period (what was first knowable)
            first = {k: g[g.reporting_period == p].sort_values("vintage_available_from").head(1) for k, p in lab.items()}
            def val(k):
                return None if first[k].empty else float(first[k]["value"].iloc[0])
            def av(*ks):
                ds = [first[k]["vintage_available_from"].iloc[0] for k in ks if not first[k].empty]
                return max(ds) if len(ds) == len(ks) else None
            def docs(*ks):
                return "; ".join(f"{first[k]['source_doc'].iloc[0]} p{int(first[k]['pdf_page'].iloc[0])} ({first[k]['vintage_role'].iloc[0]})"
                                 for k in ks if not first[k].empty)
            spec = [("Q1", ("Q1",), lambda: val("Q1")),
                    ("Q2", ("H1", "Q1"), lambda: None if val("H1") is None or val("Q1") is None else val("H1") - val("Q1")),
                    ("Q3", ("9M", "H1"), lambda: None if val("9M") is None or val("H1") is None else val("9M") - val("H1")),
                    ("Q4", ("FY", "9M"), lambda: None if val("FY") is None or val("9M") is None else val("FY") - val("9M"))]
            for q, ks, f in spec:
                x = f()
                if x is not None:
                    orig_q = {"Q1": "Q1", "Q2": "H1", "Q3": "9M", "Q4": "FY"}[q]
                    rows.append({"item": item, "quarter": f"{year}{q}", "value_idr_mn": round(x, 1),
                                 "inputs": docs(*ks), "available_from": av(*ks),
                                 "original_publication_date": None if first[orig_q].empty else first[orig_q]["original_publication_date"].iloc[0],
                                 "all_inputs_from_original_filings": all(bool(first[k]["original_filing_in_hand"].iloc[0]) for k in ks if not first[k].empty)})
    return pd.DataFrame(rows)


def main() -> int:
    v = build_vintages()
    v.to_csv(REF / "TAPG_pit_vintages.csv", index=False)
    q = build_quarterly(v)
    q.to_csv(REF / "TAPG_pit_quarterly.csv", index=False)
    rev = v[v.revision_date.notna()]
    print(f"{len(v)} vintages; {v.vintage_role.eq('comparative').sum()} comparative; revisions: {len(rev)}")
    print(rev[["item", "reporting_period", "source_doc", "revision_vs_first_vintage", "revision_date"]].to_string(index=False))
    leak = v[v.vintage_role.eq("comparative") & v.original_publication_date.notna()
             & (pd.to_datetime(v.original_publication_date) < pd.to_datetime(v.vintage_available_from))]
    print(f"comparative vintages whose original period date precedes the document holding the value: {len(leak)} (previous pipeline dated these too early)")
    print(q[q["item"] == "revenue"][["quarter", "available_from", "original_publication_date", "all_inputs_from_original_filings"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
