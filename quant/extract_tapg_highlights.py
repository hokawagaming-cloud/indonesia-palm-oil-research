"""Extract TAPG multi-year highlight tables (financial and operational) from the annual
reports, with full citations, and reconcile overlapping years across reports.

Each annual report shows the current year and two prior years. A label regex
locates the row on the highlight pages, and the next three numeric tokens are read
as [Y, Y-1, Y-2]. Indonesian number format: '.' = thousands separator, ',' = decimal.

Inputs:  data/processed/text/TAPG/*.txt   (from quant/pdf_to_text.py)
Outputs: data/reference/TAPG_extracted_highlights.csv  (one row per data point)
         data/reference/TAPG_highlights_reconciliation.csv

Usage: python -I quant/extract_tapg_highlights.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "data" / "processed" / "text" / "TAPG"
REF = ROOT / "data" / "reference"

# document -> (fiscal year, highlight PDF pages, publication-date proxy, proxy basis)
DOCS = {
    "AR 2021.pdf": ("AR_2021", 2021, range(10, 13), "2022-04-26", "PDF creation date"),
    "AR_2022.pdf": ("AR_2022", 2022, range(10, 13), "2023-03-31", "PDF creation date"),
    "AR_2023.pdf": ("AR_2023", 2023, range(10, 13), "2024-03-28", "PDF creation date"),
    "AR_2024.pdf": ("AR_2024", 2024, range(10, 13), "2025-04-09", "PDF creation date"),
    "TAPG_-_AR_2025.pdf": ("TAPG_-_AR_2025", 2025, range(12, 15), "2026-04-21", "PDF creation date"),
}

# (item, unit, regex on the English or Indonesian label, scale note)
ITEMS = [
    ("total_assets", "IDR mn", r"^(Total|Jumlah) Aset$"),
    ("total_liabilities", "IDR mn", r"^(Total|Jumlah) Liabilit(ies|as)$"),
    ("total_equity", "IDR mn", r"^(Total|Jumlah) Ekuitas$"),
    ("revenue", "IDR mn", r"^Penjualan$"),
    ("gross_profit", "IDR mn", r"^Laba Bruto$"),
    ("profit_for_year", "IDR mn", r"^Laba Tahun Berjalan$"),
    ("profit_attrib_owners", "IDR mn", r"Pemilik entitas induk$"),
    ("eps", "IDR per share", r"^Laba \(Rugi\) per Saham$"),
    ("planted_nucleus_oilpalm", "thousand ha", r"Planted Area of Nucleus Oil Palm"),
    ("planted_plasma_oilpalm", "thousand ha", r"Planted Area of Plasma Oil Palm"),
    ("planted_total_oilpalm", "thousand ha", r"^Total Planted Area of Oil Palm"),
    ("ffb_harvested_nucleus", "thousand t", r"FFB Harvested from Nucleus"),
    ("ffb_harvested_plasma", "thousand t", r"FFB Harvested from Plasma"),
    ("ffb_harvested_total", "thousand t", r"^Total FFB Harvested from Oil Palm"),
    ("ffb_processed_total", "thousand t", r"^Total Processed FFB"),
    ("cpo_production", "thousand t", r"^CPO Production"),
    ("pk_production", "thousand t", r"^(PK|Palm Kernel) Production"),
    ("avg_ffb_yield", "t/ha", r"^Average FFB Yield"),
    ("oer_cpo", "%", r"^Oil Extraction Rate"),
    ("ker_pk", "%", r"^Kernel Extraction Rate"),
    ("pko_production", "thousand t", r"^PKO Production"),
]
NUM = re.compile(r"^(\(?-?[\d.]+(,\d+)?\)?\*?|-)$")


def parse_num(tok: str) -> float:
    if tok == "-":
        return float("nan")  # reported as "-" (nil / not applicable)
    neg = tok.startswith("(")
    t = tok.strip("()*").replace(".", "").replace(",", ".")
    v = float(t)
    return -v if neg else v


def load_pages(stem: str) -> dict[int, list[str]]:
    pages, cur = {}, 0
    for ln in open(TXT / f"{stem}.txt", encoding="utf-8"):
        m = re.match(r"=== PAGE (\d+) ===", ln)
        if m:
            cur = int(m.group(1)); pages[cur] = []; continue
        s = ln.strip()
        if s:
            pages.setdefault(cur, []).append(s)
    return pages


def printed_folio(lines: list[str]) -> str:
    for s in lines[::-1]:
        if re.fullmatch(r"\d{1,3}", s):
            return s
    return ""


def extract() -> pd.DataFrame:
    rows = []
    for pdf, (stem, fy, pages_rng, pub, pub_basis) in DOCS.items():
        pages = load_pages(stem)
        for item, unit, pat in ITEMS:
            rx = re.compile(pat, re.I)
            hit = None
            for p in pages_rng:
                lines = pages.get(p, [])
                for i, s in enumerate(lines):
                    # labels can wrap: test the line and the line joined with the next one
                    joined = s + " " + (lines[i + 1] if i + 1 < len(lines) else "")
                    if rx.search(s) or rx.search(joined):
                        nums = []
                        for t in lines[i + 1:i + 14]:
                            if NUM.match(t) and not re.fullmatch(r"20\d\d", t):
                                nums.append(t)
                            if len(nums) == 3:
                                break
                        if len(nums) == 3:
                            hit = (p, printed_folio(lines), nums)
                            break
                if hit:
                    break
            if not hit:
                rows.append({"item": item, "unit": unit, "fiscal_year": None, "value": None,
                             "source_doc": pdf, "pdf_page": None, "printed_page": None,
                             "status": "NOT FOUND"})
                continue
            p, folio, nums = hit
            for k, tok in enumerate(nums):
                rows.append({
                    "item": item, "unit": unit, "fiscal_year": fy - k,
                    "period": f"FY{fy - k} (Jan-Dec)", "value": parse_num(tok), "raw_token": tok,
                    "source_doc": pdf, "pdf_page": p, "printed_page": folio,
                    "report_fiscal_year": fy, "publication_date_proxy": pub,
                    "publication_date_basis": pub_basis,
                    "scope_note": "includes associates" if unit != "IDR mn" and item != "eps" else "consolidated",
                    "status": "extracted",
                })
    return pd.DataFrame(rows)


def reconcile(df: pd.DataFrame) -> pd.DataFrame:
    ok = df[df["status"] == "extracted"]
    out = []
    for (item, fy), g in ok.groupby(["item", "fiscal_year"]):
        vals = g.sort_values("report_fiscal_year")
        latest = vals.iloc[-1]
        spread = vals["value"].max() - vals["value"].min()
        rel = spread / abs(latest["value"]) if latest["value"] else 0
        out.append({
            "item": item, "fiscal_year": int(fy), "unit": latest["unit"], "n_reports": len(vals),
            "values_by_report": "; ".join(f"AR{int(r)}={v:g}" for r, v in
                                          zip(vals["report_fiscal_year"], vals["value"])),
            "latest_value": latest["value"], "latest_source": f"{latest['source_doc']} p{latest['pdf_page']}",
            "max_rel_diff": round(rel, 5),
            "status": "single source" if len(vals) == 1 else ("consistent" if (spread == 0 or vals["value"].isna().all()) else "DIFFERS (restated or revised)"),
        })
    return pd.DataFrame(out)


def checks(df: pd.DataFrame) -> list[str]:
    msgs = []
    ok = df[df["status"] == "extracted"]
    latest = ok.sort_values("report_fiscal_year").groupby(["item", "fiscal_year"])["value"].last().unstack(0)
    for fy, r in latest.iterrows():
        def chk(name, lhs, rhs, tol):
            if pd.notna(lhs) and pd.notna(rhs):
                gap = abs(lhs - rhs)
                msgs.append(f"FY{int(fy)} {name}: {lhs:g} vs {rhs:g} -> {'PASS' if gap <= tol else 'FAIL'}")
        chk("A = L + E (IDR mn)", r.get("total_assets"), r.get("total_liabilities", float("nan")) + r.get("total_equity", float("nan")), 2)
        chk("planted nucleus + plasma = total (k ha)", r.get("planted_nucleus_oilpalm", float("nan")) + r.get("planted_plasma_oilpalm", float("nan")), r.get("planted_total_oilpalm"), 0.15)
        chk("FFB nucleus + plasma = total (kt)", r.get("ffb_harvested_nucleus", float("nan")) + r.get("ffb_harvested_plasma", float("nan")), r.get("ffb_harvested_total"), 2)
        if pd.notna(r.get("cpo_production")) and pd.notna(r.get("ffb_processed_total")) and pd.notna(r.get("oer_cpo")):
            implied = 100 * r["cpo_production"] / r["ffb_processed_total"]
            msgs.append(f"FY{int(fy)} OER check: CPO/processed FFB = {implied:.2f}% vs reported {r['oer_cpo']:g}% -> "
                        f"{'PASS' if abs(implied - r['oer_cpo']) <= 0.15 else 'FAIL'}")
    return msgs


def main() -> int:
    df = extract()
    df.to_csv(REF / "TAPG_extracted_highlights.csv", index=False)
    rec = reconcile(df)
    rec.to_csv(REF / "TAPG_highlights_reconciliation.csv", index=False)
    nf = df[df["status"] == "NOT FOUND"]
    print("not found:", nf[["item", "source_doc"]].values.tolist())
    print(rec[rec["status"].str.startswith("DIFF")].to_string(index=False))
    print("\n".join(checks(df)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
