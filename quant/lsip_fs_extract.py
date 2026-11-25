"""Extract LSIP consolidated financial statements (Phase XVII).

    python -I -X utf8 quant/lsip_fs_extract.py

Inputs: per-page text from quant/pdf_to_text.py in data/processed/LSIP_text/ (PDFs are local only, git-ignored).
The bilingual statements print "Indonesian label | current | [note] | prior | English label". Each item is found by
its English label inside the statement pages only (before the notes start), and the numeric block immediately
before the label is read (note references such as "21,27" or "1d" are dropped).

Outputs (IDR million):
  data/reference/research/LSIP_financials_annual.csv   one row per period (FY2020-FY2025, 9M25, 9M26, H1 26)
  data/reference/research/LSIP_financials_checks.csv   accounting identities and prior-year restatement checks
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "data" / "processed" / "LSIP_text"
OUT = ROOT / "data" / "reference" / "research"

# document -> (current period, prior period)
DOCS = {
    "LSIP_bilingual_31_des_2025_released": ("FY2025", "FY2024"),
    "pp_london_sumatra_indonesia_bilingual_31_des_2024_released": ("FY2024", "FY2023"),
    "AR2023": ("FY2023", "FY2022"),
    "AR2022": ("FY2022", "FY2021"),
    "AR2021": ("FY2021", "FY2020"),
    "LSIP_bilingual_30_Sep_2026_Released": ("9M26", "9M25"),
    "LSIP_bilingual_30_Jun_2026_Released": ("H126", "H125"),
}

# item -> (statement, English-label regex). Statement: B balance sheet, P profit or loss, C cash flow.
SPEC = {
    "trade_receivables_3p": ("B", r"Trade receivables\s*\|?\s*\|?\s*Third parties|Third parties(?=.{0,80}Related parties.{0,200}Other receivables)"),
    "inventories": ("B", r"Inventories"),
    "biological_assets": ("B", r"Biological assets"),
    "total_current_assets": ("B", r"Total Current Assets"),
    "fixed_assets_net": ("B", r"Fixed assets"),
    "total_noncurrent_assets": ("B", r"Total Non-current Assets"),
    "total_assets": ("B", r"Total Assets"),
    "trade_payables_3p": ("B", r"Third parties(?=\|?\s*\|?\s*Pihak berelasi.{0,60}Related parties\|Utang lain)"),
    "total_current_liabilities": ("B", r"Total Current Liabilities"),
    "employee_benefits_lt": ("B", r"Employee benefits liability(?=[\s\|]*Total Liabilitas)"),
    "total_liabilities": ("B", r"Total Liabilities(?! and)"),
    "treasury_shares": ("B", r"Treasury shares"),
    "retained_unappropriated": ("B", r"Unappropriated"),
    "equity_owners": ("B", r"(?<=\|)(?=[\d\.\(\)\s\|]+\|\s*Kepentingan Nonpengendali)"),
    "total_equity": ("B", r"Total Equity"),
    "total_liab_equity": ("B", r"Total Liabilities and Equity"),
    "revenue": ("P", r"customers|Net sales|Sales"),
    "cogs": ("P", r"Cost of goods sold"),
    "gross_profit": ("P", r"Gross profit"),
    "fv_bio": ("P", r"fair value of biological assets"),
    "selling": ("P", r"Selling and distribution expenses"),
    "ga": ("P", r"General and administrative expenses"),
    "other_income": ("P", r"Other operating income"),
    "other_expense": ("P", r"Other operating expenses"),
    "operating_profit": ("P", r"Operating profit|Income from operations"),
    "finance_income": ("P", r"Finance income"),
    "finance_cost": ("P", r"Finance costs?"),
    "associates": ("P", r"Share in .{0,30}associates?"),
    "pbt": ("P", r"Profit before income tax"),
    "tax": ("P", r"Income tax expense"),
    "profit": ("P", r"Profit for the (?:year|period)(?!\s*attributable)"),
    "profit_owners": ("P", r"(?<=Pemilik entitas induk\|)(?=)|Owners of the parent"),
    "cash_from_customers": ("C", r"Cash received from customers"),
    "paid_employees": ("C", r"Payments to employees"),
    "paid_suppliers": ("C", r"and other operating expenses"),
    "interest_received": ("C", r"Receipts? of interest income|Interest (?:income )?received"),
    "tax_paid": ("C", r"Payments? of corporate income tax"),
    "cfo": ("C", r"Operating Activities(?=[\s\|]*Arus Kas dari)"),
    "capex": ("C", r"Additions to fixed assets|Acquisitions? of fixed assets"),
    "plasma_receivables": ("C", r"Additions to plasma receivables"),
    "cfi": ("C", r"Investing Activities(?=[\s\|]*Arus Kas dari)"),
    "dividends_paid": ("C", r"Payments? of cash dividends|Cash dividends paid|Dividends paid"),
    "buyback_paid": ("C", r"(?:Purchases?|Acquisitions?) of treasury shares|Payments? for treasury shares"),
    "cff": ("C", r"Financing Activities(?=[\s\|]*(?:Kenaikan|Penurunan))"),
    "fx_on_cash": ("C", r"Cash and Cash Equivalents(?=[\s\|]*Kas dan Setara Kas[\s\|]*Cash and Cash Equivalents[\s\|]*Awal)"),
    "cash_begin": ("C", r"at Beginning of (?:Year|Period)"),
    "cash_end": ("C", r"at End of (?:Year|Period)"),
}

NUM = re.compile(r"^\(?-?[\d\.]+\s*\)?$")
NOTE = re.compile(r"^\d{1,2}[a-z]?(,\d{1,2}[a-z]?)*$")


def to_num(tok: str) -> float:
    neg = tok.startswith("(") or tok.startswith("-")
    v = float(tok.strip("()- ").replace(".", ""))
    return -v if neg else v


def pages(stem: str) -> list[str]:
    raw = (TXT / f"{stem}.txt").read_text(encoding="utf-8")
    return [p for p in re.split(r"\n=== PAGE \d+ ===\n", raw)]


def statement_pages(stem: str) -> dict[str, str]:
    """Pages of each primary statement, joined with '|' (only the first FS in the document)."""
    P = pages(stem)
    heads = {"B": r"CONSOLIDATED STATEMENTS? OF\s*\|?\s*FINANCIAL POSITION|STATEMENT OF FINANCIAL POSITION",
             "P": r"PROFIT OR LOSS AND OTHER",
             "C": r"STATEMENTS? OF CASH FLOWS"}
    out = {}
    for k, h in heads.items():
        hits = [i for i, p in enumerate(P) if re.search(h, p.replace("\n", "|").upper()) and
                "CATATAN ATAS LAPORAN" not in p and len(re.findall(r"\d{1,3}(?:\.\d{3})+", p)) > 15]
        if not hits:
            continue
        first = hits[0]
        # statements span consecutive pages; take the header page and the following page(s) with the same header
        idx = [first] + [i for i in hits[1:] if i - first <= 3]
        out[k] = "|".join(P[i].replace("\n", "|") for i in idx)
    return out


def block_before(s: str, pos: int) -> list[float]:
    toks = [t.strip() for t in s[:pos].split("|")]
    nums = []
    for t in reversed(toks):
        if t == "":
            continue
        if NUM.match(t) or NOTE.match(t):
            nums.append(t)
            continue
        if re.fullmatch(r"[\d\.\(\)\s]+", t):          # '681.996 capital' style splits handled elsewhere
            nums.append(t.split()[0])
            continue
        break
    nums = list(reversed(nums))
    vals = [n for n in nums if not (NOTE.match(n) and "." not in n and len(nums) > 2 and n is not nums[0] and n is not nums[-1])]
    if len(vals) > 2:
        vals = [v for v in vals if "." in v or v.startswith("(") or not NOTE.match(v)]
    return [to_num(v) for v in vals[:2]] if len(vals) >= 2 else []   # 3-column restated sheets: current, prior, opening


def extract(stem: str) -> dict[str, tuple[float, float]]:
    S = statement_pages(stem)
    res = {}
    for item, (st, rx) in SPEC.items():
        s = S.get(st, "")
        for m in re.finditer(rx, s):
            v = block_before(s, m.start())
            if v:
                res[item] = (v[0], v[1])
                break
    return res


def main() -> None:
    rows, prior = {}, {}
    for stem, (cur, pri) in DOCS.items():
        if not (TXT / f"{stem}.txt").exists():
            print("missing", stem); continue
        r = extract(stem)
        rows[cur] = {k: v[0] for k, v in r.items()}
        prior[(stem, pri)] = {k: v[1] for k, v in r.items()}
        # balance sheet comparatives of interims are the previous year-end, not the prior-year period
    df = pd.DataFrame(rows).T
    order = ["FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "H126", "9M26"]
    for (stem, pri), d in prior.items():
        if pri == "FY2020":
            df.loc["FY2020", list(d)] = pd.Series(d)
        if pri == "9M25":
            pl = {k: v for k, v in d.items() if SPEC[k][0] != "B"}
            df.loc["9M25", list(pl)] = pd.Series(pl)
    df = df.reindex([o for o in order[:6] + ["9M25", "H126", "9M26"] if o in df.index])
    df.index.name = "period"
    df = df[[c for c in SPEC if c in df.columns]]
    df.to_csv(OUT / "LSIP_financials_annual.csv", float_format="%.0f")

    checks = []
    for p, r in df.iterrows():
        def g(k):
            return r.get(k, float("nan"))
        checks += [
            (p, "A = L + E", g("total_assets") - g("total_liabilities") - g("total_equity")),
            (p, "L + E = total", g("total_liab_equity") - g("total_assets")),
            (p, "GP = rev + cogs", g("gross_profit") - g("revenue") - g("cogs")),
            (p, "PBT - tax = profit", g("pbt") + g("tax") - g("profit")),
            (p, "OP + fin + assoc = PBT", g("operating_profit") + g("finance_income") + g("finance_cost") + g("associates") - g("pbt")),
            (p, "cash begin + flows = end", g("cash_begin") + g("cfo") + g("cfi") + g("cff") + g("fx_on_cash") - g("cash_end")),
            (p, "cash end = BS cash", g("cash_end") - g("cash")),
        ]
    for (stem, pri), d in prior.items():
        if pri in df.index:
            for k, v in d.items():
                if k in df.columns and pd.notna(df.loc[pri, k]) and (SPEC[k][0] != "B" or pri.startswith("FY")):
                    if not pri.startswith("FY") and SPEC[k][0] == "B":
                        continue
                    checks.append((pri, f"restatement {k} ({stem})", v - df.loc[pri, k]))
    C = pd.DataFrame(checks, columns=["period", "check", "difference"])
    C.to_csv(OUT / "LSIP_financials_checks.csv", index=False, float_format="%.1f")
    print(df.T.to_string())
    bad = C[C.difference.abs() > 1.5]
    print("checks:", len(C), "non-zero (>1.5mn):", len(bad))
    if len(bad):
        print(bad.to_string())


if __name__ == "__main__":
    main()
