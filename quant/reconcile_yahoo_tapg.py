"""Reconcile Yahoo (S-020) TAPG values against the official statements extracted by
quant/extract_tapg_statements.py. Output: data/reference/TAPG_yahoo_vs_official.csv
Usage: python -I quant/reconcile_yahoo_tapg.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
MAP = {  # official item -> (yahoo statement kind, yahoo row)
    "revenue": "Total Revenue", "gross_profit": "Gross Profit", "profit_before_tax": "Pretax Income",
    "profit_attrib_owners": "Net Income Common Stockholders", "total_assets": "Total Assets",
    "total_equity": "Total Equity Gross Minority Interest", "capex_fixed_assets": "Capital Expenditure",
    "dividends_received_jv": "Dividends Received Cfi", "cash": "Cash And Cash Equivalents",
}


def main() -> int:
    off = pd.read_csv(REF / "TAPG_statements_extracted.csv")
    off = off[(off.status == "extracted") & off.period.str.startswith("FY")].drop_duplicates(["item", "period"], keep="last")
    y = pd.read_csv(REF / "TAPG_fundamentals_validation.csv")
    y = y[(y.kind == "value") & (y.frequency == "annual")]
    y["period"] = "FY" + y.period_end.str[:4]
    rows = []
    for item, yrow in MAP.items():
        for _, r in off[off.item == item].iterrows():
            m = y[(y["item"] == yrow) & (y.period == r.period)]
            if m.empty or pd.isna(m.value.iloc[0]):
                rows.append({"item": item, "period": r.period, "official_idr_mn": r.value, "yahoo_idr_mn": None, "result": "NOT IN YAHOO"})
                continue
            yv = m.value.iloc[0] / 1e6
            diff = yv - r.value
            rows.append({"item": item, "period": r.period, "official_idr_mn": r.value, "yahoo_idr_mn": round(yv, 1),
                         "diff_idr_mn": round(diff, 1), "result": "MATCH" if abs(diff) <= 1 else "DIFFERS",
                         "official_source": f"{r.source_doc} p{int(r.pdf_page)}"})
    out = pd.DataFrame(rows)
    out.to_csv(REF / "TAPG_yahoo_vs_official.csv", index=False)
    print(out.result.value_counts().to_string())
    print(out[out.result == "DIFFERS"].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
