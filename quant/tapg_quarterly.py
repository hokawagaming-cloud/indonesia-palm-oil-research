"""Derive discrete-quarter flow values for TAPG from cumulative official figures
(Q1, H1, 9M, FY), e.g. Q3 = 9M - H1 and Q4 = FY - 9M. This is arithmetic on reported
numbers, not estimation. Balance-sheet items are point-in-time and are not differenced.

available_from comes from data/reference/TAPG_disclosure_dates.csv (A-012); its basis is
EVIDENCE or ASSUMPTION.

Output: data/reference/TAPG_quarterly_derived.csv
Usage:  python -I quant/tapg_quarterly.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
STOCK = {"cash", "total_assets", "total_equity", "investment_in_jv", "investment_in_associates", "fixed_assets_net"}


def main() -> int:
    d = pd.read_csv(REF / "TAPG_statements_extracted.csv")
    d = d[d.status == "extracted"].drop_duplicates(["item", "period"], keep="last")
    dates = pd.read_csv(REF / "TAPG_disclosure_dates.csv")
    dates = dates[dates.disclosure.isin(["interim FS", "audited FS"])].set_index("period")
    avail = lambda lbl: (dates.at[lbl, "available_from"], dates.at[lbl, "basis"].split(":")[0]) if lbl in dates.index else (None, "UNKNOWN")
    cum = {p: f"{p.split()[0]}" for p in d.period.unique()}
    rows = []
    for year in (2025, 2026):
        lab = {"Q1": f"Q1 {year}", "H1": f"H1 {year}", "9M": f"9M {year}", "FY": f"FY{year}"}
        for item in sorted(set(d.item) - STOCK):
            s = d[d.item == item].set_index("period")
            get = lambda k: s.value.get(lab[k]) if lab[k] in s.index else None
            q1, h1, m9, fy = get("Q1"), get("H1"), get("9M"), get("FY")
            src = lambda k: f"{s.source_doc[lab[k]]} p{int(s.pdf_page[lab[k]])}" if lab[k] in s.index else ""
            pub = lambda k: avail(lab[k])
            for q, val, how, p in (("Q1", q1, "reported (Q1)", pub("Q1")),
                                   ("Q2", None if h1 is None or q1 is None else h1 - q1, "H1 - Q1", pub("H1")),
                                   ("Q3", None if m9 is None or h1 is None else m9 - h1, "9M - H1", pub("9M")),
                                   ("Q4", None if fy is None or m9 is None else fy - m9, "FY - 9M", pub("FY"))):
                if val is not None:
                    rows.append({"item": item, "quarter": f"{year}{q}", "value_idr_mn": round(val, 1),
                                 "derivation": how, "inputs": "; ".join(x for x in (src("Q1"), src("H1"), src("9M"), src("FY")) if x),
                                 "available_from": p[0], "available_basis": p[1]})
    out = pd.DataFrame(rows)
    out.to_csv(REF / "TAPG_quarterly_derived.csv", index=False)
    pv = out.pivot(index="item", columns="quarter", values="value_idr_mn")
    print((pv / 1e3).round(1).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
