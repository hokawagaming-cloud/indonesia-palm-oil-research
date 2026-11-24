"""Canonical scope-separated TAPG datasets and a scope-safe ratio helper (D-008).

Scopes
  consolidated : TAPG and subsidiaries (financial statements, ASP, sales volumes,
                 cost notes, fixed-asset roll-forward)
  jv           : joint ventures, chiefly PT Union Sampoerna Triputra Persada (USTP),
                 on a 100% basis, plus TAPG's equity-method share and dividends
  groupwide    : operational statistics the company reports "including associate
                 companies" (planted/mature area, age profile, FFB, CPO/PK output,
                 yield, OER). The consolidated share of these is NOT disclosed.

Builds data/reference/TAPG_scope_{consolidated,jv,groupwide}.csv from the extraction
outputs. `ratio()` refuses to divide items from different scopes.
Usage: python -I quant/tapg_scope.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
COLS = ["scope", "item", "period", "value", "unit", "source_doc", "pdf_page", "basis", "note"]


class ScopeError(ValueError):
    pass


def build() -> dict[str, pd.DataFrame]:
    st = pd.read_csv(REF / "TAPG_statements_extracted.csv")
    st = st[st.status == "extracted"].assign(scope="consolidated", note=lambda d: d.publication_date_basis)
    op = pd.read_csv(REF / "TAPG_operational_extracted.csv")
    op["scope"] = op["scope"].map(lambda s: "groupwide" if "associates" in s else ("jv" if "JV" in s else "consolidated"))
    op["basis"] = "annual report"
    hl = pd.read_csv(REF / "TAPG_extracted_highlights.csv")
    hl = hl[(hl.status == "extracted") & (hl.unit != "IDR mn") & (hl["item"] != "eps")].assign(
        scope="groupwide", basis="annual report highlights", note="incl. associates")
    hl["period"] = "FY" + hl.fiscal_year.astype(int).astype(str)
    parts = [st, op, hl] + [pd.read_csv(REF / f"TAPG_phase2_{s}.csv").assign(scope=s)
                            for s in ("consolidated", "jv", "groupwide")]
    allr = pd.concat([p.reindex(columns=COLS) for p in parts], ignore_index=True)
    allr = allr.drop_duplicates(["scope", "item", "period"], keep="last")
    out = {}
    for s, g in allr.groupby("scope"):
        g.sort_values(["item", "period"]).to_csv(REF / f"TAPG_scope_{s}.csv", index=False)
        out[s] = g
    return out


def load(scope: str) -> pd.DataFrame:
    return pd.read_csv(REF / f"TAPG_scope_{scope}.csv")


def ratio(num: tuple[str, str], den: tuple[str, str], period: str) -> float:
    """num/den given as (scope, item). Raises ScopeError when the scopes differ."""
    if num[0] != den[0]:
        raise ScopeError(f"refusing {num} / {den}: different reporting scopes")
    d = load(num[0]).set_index(["item", "period"])["value"]
    return d[(num[1], period)] / d[(den[1], period)]


if __name__ == "__main__":
    o = build()
    for s, g in o.items():
        print(s, len(g), "rows,", g["item"].nunique(), "items")
