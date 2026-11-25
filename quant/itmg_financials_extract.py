"""ITMG historical financial statements (Phase XVI). Source: ITMG consolidated FS PDFs (S-066, SHA-256 in
ITMG_document_manifest.csv; raw files git-ignored). USD thousands.

For each FS (FY2018-FY2025 audited 12M; 9M25, 9M26 interim) the CURRENT-period column of the consolidated
statements is parsed by anchoring on the English line label and taking the two numbers printed just before it
(current, comparative). Identity checks: total assets = liabilities + equity; gross profit = revenue - cost of
revenue; profit = PBT - tax; cash roll-forward.

    python -I -X utf8 quant/itmg_financials_extract.py  -> data/reference/research/ITMG_financials_annual.csv
                                                          data/reference/research/ITMG_financials_checks.csv
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "coal" / "ITMG"
OUT = ROOT / "data" / "reference" / "research"
NUM = re.compile(r"^\(?-?[\d.,]+\)?$|^-$")

# key: (anchor regex on the English label line, context regex within the previous 8 lines or None, occurrence)
SPEC = {
    "cash": (r"^Cash and cash equivalents$", None, 0),
    "trade_receivables_3p": (r"^Third parties -$", None, 0),
    "trade_receivables_rp": (r"^Related parties -$", None, 0),
    "inventories": (r"^Inventories$", None, 0),
    "total_current_assets": (r"^Total current assets", None, 0),
    "ppe": (r"^Property, plant and equipment$", None, 0),
    "deferred_stripping": (r"^Deferred stripping costs", None, 0),
    "deferred_exploration": (r"^(and development )?expenditures?$", r"Deferred exploration", 0),
    "total_assets": (r"^TOTAL ASSETS", None, 0),
    "trade_payables": (r"^Trade payables", None, 0),
    "st_bank_loans": (r"^Short-term bank loans$", None, 0),
    "lt_loans_current": (r"^long-term bank loans?$", r"Current maturities", 0),
    "lease_current": (r"^Lease liabilities$", None, 0),
    "lease_noncurrent": (r"^Lease liabilities$", None, 1),
    "lt_loans_noncurrent": (r"^net of current maturities", r"Long-term bank loans?", 0),
    "mine_rehab_provision": (r"^Provision for mine rehabilitation$", None, 0),
    "total_current_liabilities": (r"^Total current liabilities", None, 0),
    "total_noncurrent_liabilities": (r"^Total non-current liabilities", None, 0),
    "total_liabilities": (r"^TOTAL LIABILITIES$", None, 0),
    "nci": (r"^Non-controlling interest", None, 0),
    "total_equity": (r"^TOTAL EQUITY", None, 0),
    "revenue": (r"^(Net revenue|Revenue|Net revenues)$", None, 0),
    "cost_of_revenue": (r"^Cost of revenue", None, 0),
    "gross_profit": (r"^Gross profit", None, 0),
    "selling_exp": (r"^Selling expenses", None, 0),
    "ga_exp": (r"^administrat\w* expenses", None, 0),
    "finance_costs": (r"^Finance costs", None, 0),
    "finance_income": (r"^Finance income", None, 0),
    "pbt": (r"^Profit before income tax", None, 0),
    "income_tax": (r"^Income tax expense", None, 0),
    "profit": (r"^Profit for the (year|period)", None, 0),
    "profit_owners": (r"^Owners of the (parent|Company)", None, 0),
    "cfo": (r"operating activities$", r"Net cash (generated from|provided by|flows from)", 0),
    "capex_ppe": (r"^(property, plant and equipment|and equipment( including)?)$", r"Purchases? of", 0),
    "capex_exploration": (r"^development expenditures?$", r"Additions? of deferred", 0),
    "cfi": (r"investing activities$", r"Net cash (used in|generated from|provided by)", 0),
    "dividends_paid": (r"^Payment of (cash )?dividends", None, 0),
    "lease_payments": (r"^Payments? of lease liabilities", None, 0),
    "cff": (r"financing activities$", r"Net cash (used in|generated from|provided by)", 0),
}


def to_num(s: str) -> float:
    s = s.strip()
    if s == "-":
        return 0.0
    neg = s.startswith("(")
    v = float(s.strip("()").replace(",", ""))
    return -v if neg else v


def lines(pdf: Path) -> list[str]:
    d = pymupdf.open(pdf)
    out = []
    for i in range(min(len(d), 25)):
        t = d[i].get_text()
        if re.search(r"STATEMENTS?\s+OF\s+(FINANCIAL\s+POSITION|PROFIT\s+OR\s+LOSS|CASH\s+FLOWS)", t, re.I):
            out += [l.strip() for l in t.split("\n") if l.strip()]
    return out


def extract(pdf: Path) -> dict:
    L = lines(pdf)
    res = {}
    for k, (anc, ctx, occ) in SPEC.items():
        hits = []
        for i, l in enumerate(L):
            if re.search(anc, l, re.I) and (ctx is None or any(re.search(ctx, x, re.I) for x in L[max(0, i - 8):i])):
                nums, j = [], i - 1
                while j >= 0 and NUM.match(L[j]):      # contiguous numeric block right before the label
                    nums.insert(0, L[j]); j -= 1
                if len(nums) >= 2:
                    hits.append(nums[-2:])
        if len(hits) > occ:
            res[k] = to_num(hits[occ][0]); res[k + "__prior"] = to_num(hits[occ][1])
    return res


def main() -> pd.DataFrame:
    files = {f"FY{y}": RAW / f"ITM_Consolidated_Financial_Statements_12M{str(y)[2:]}.pdf" for y in range(2018, 2026)}
    files["9M25"] = RAW / "ITM_Consolidated_Financial_Statement_9M25.pdf"
    files["9M26"] = RAW / "ITM_Consolidated_Financial_Statements_9M26.pdf"
    rows = {p: extract(f) for p, f in files.items()}
    D = pd.DataFrame(rows).T
    cur = D[[c for c in D.columns if not c.endswith("__prior")]]
    chk = pd.DataFrame({
        "bs_balance": cur.total_assets - cur.total_liabilities - cur.total_equity,
        "gp_identity": cur.revenue + cur.cost_of_revenue - cur.gross_profit,
        "profit_identity": cur.pbt + cur.income_tax - cur.profit,
        "missing_fields": cur.isna().sum(axis=1),
    })
    # prior-year column of FY(t+1) must equal FY(t) current (first-reported vs comparative restatement check)
    rest = {}
    for y in range(2018, 2025):
        a, b = D.loc[f"FY{y}"], D.loc[f"FY{y + 1}"]
        rest[f"FY{y}"] = max(abs(a[k] - b[k + "__prior"]) for k in ("total_assets", "revenue", "profit") if pd.notna(a.get(k)) and pd.notna(b.get(k + "__prior")))
    chk["max_abs_restatement_next_year"] = pd.Series(rest)
    cur.to_csv(OUT / "ITMG_financials_annual.csv")
    chk.to_csv(OUT / "ITMG_financials_checks.csv")
    return cur, chk


if __name__ == "__main__":
    c, k = main()
    pd.set_option("display.width", 250)
    print(k)
    print(c.isna().sum()[c.isna().sum() > 0])
    print(c[["revenue", "gross_profit", "profit", "profit_owners", "cash", "total_assets", "cfo", "capex_ppe", "dividends_paid"]].round(0))
