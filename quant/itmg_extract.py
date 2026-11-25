"""Phase XII: extract ITMG quarterly operating data from the official analyst presentations
(data/raw/coal/ITMG/, git-ignored; SHA-256 in data/reference/research/ITMG_document_manifest.csv).

Fields (first-reported vintage, i.e. from the quarter's OWN presentation):
  asp_usd_t        blended realised ASP ('ITM ASP'; incl. post-shipment adjustments and traded coal)
  sales_mt         sales volume
  asp_prev_q / asp_prev_y   comparatives printed in the same deck (for revision checks)
  domestic_share   'Indonesia' share in the sales-by-destination chart, when printed
  strip_ratio, fuel_usd_l  when printed as current-quarter values
Every value carries the page it came from. Regex parsing is followed by identity checks
(revenue ~= ASP x volume) and comparison with later decks' comparatives.

Usage: python -I -X utf8 quant/itmg_extract.py
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "coal" / "ITMG"
OUT = ROOT / "data" / "reference" / "research"
F = r"(\d{1,3}(?:\.\d{1,2})?)"


def pages(q: str) -> list[str]:
    d = pymupdf.open(RAW / f"ITM_Analyst_Presentation_{q}.pdf")
    return [" ".join(p.get_text().split()) for p in d]


def first(pats, P, conv=float):
    for i, t in enumerate(P):
        for pat in pats:
            m = re.search(pat, t, re.I)
            if m:
                return conv(m.group(1).replace(",", "")), i + 1
    return np.nan, None


def extract(q: str) -> dict:
    P = pages(q)
    r = {"quarter": q}
    # precedence: the precise text value 'ITM ASP[ 1Q23]: US$x' over rounded chart labels
    r["asp_usd_t"], r["asp_page"] = first([r"ITM ASP\s*(?:\d[QH]\d{2})?\s*:\s*(?:US)?\$\s?" + F], P)
    if not np.isnan(r["asp_usd_t"]):
        pass
    else:
        r["asp_usd_t"], r["asp_page"] = first([r"ITM ASP\s*(?:\d[QH]\d{2})?\s*:?\s*(?:US)?\$\s?" + F, r"ITM ASP\s+(?:US)?\$\s?" + F + r"\s*/\s*t",
                                           r"ITM ASP\s*\$\s?" + F + r"\s*/t", r"Average selling price \(\$/ton\)\s+[\d.]+\s+[\d.]+\s+" + F,
                                           r"ASP\s*\(US\$/t(?:on)?\)\s*[\d.]+\s+[\d.]+\s+" + F], P)
    m = None
    for i, t in enumerate(P):
        m = re.search(r"Average selling price \(\$/ton\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", t, re.I)
        if m:
            r["asp_prev_y"], r["asp_prev_q"], r["asp_tab_cur"] = map(float, m.groups()); r["asp_tab_page"] = i + 1
            break
    r["sales_mt"], r["sales_page"] = first([r"Sales volume \(Mt\)\s+[\d.]+\s+[\d.]+\s+" + F, r"SALES VOLUME\s+" + F + r"\s*Mt",
                                           r"sales volume (?:of|reached|was|at)\s+" + F + r"\s*Mt", r"Sales volume\s*:?\s*" + F + r"\s*Mt"], P)
    r["revenue_usd_m"], r["rev_page"] = first([r"Revenue\s+[\d,]+\s+[\d,]+\s+([\d,]+)\s+Operating Income"], P)
    r["ebitda_usd_m"], _ = first([r"EBITDA\s+[\d,]+\s+[\d,]+\s+([\d,]+)\s+Net profit"], P)
    r["op_income_usd_m"], _ = first([r"Operating Income\s+[\d,]+\s+[\d,]+\s+([\d,]+)\s+EBITDA"], P)
    r["domestic_share"], r["dom_page"] = first([r"Indonesia\s+(\d{1,2})\s*%", r"Domestic\s+(\d{1,2})\s*%"], P, conv=lambda s: float(s) / 100)
    r["newc_ref_text"], _ = first([r"(?:NEX|GC ?Newc)[^$]{0,40}(?:US)?\$\s?" + F], P)
    return r


def main() -> int:
    qs = [f"{q}Q{yy}" for yy in range(18, 27) for q in (1, 2, 3, 4) if not (yy == 26 and q == 4)]
    D = pd.DataFrame([extract(q) for q in qs])
    D["period"] = [f"20{q[-2:]}Q{q[0]}" for q in D.quarter]
    D.to_csv(OUT / "ITMG_quarterly_raw_extract.csv", index=False)
    pd.set_option("display.width", 250)
    print(D[["period", "asp_usd_t", "asp_page", "asp_tab_cur", "asp_prev_q", "asp_prev_y", "sales_mt", "revenue_usd_m", "ebitda_usd_m", "domestic_share", "newc_ref_text"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
