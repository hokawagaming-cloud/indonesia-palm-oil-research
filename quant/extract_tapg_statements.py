"""Extract line items from TAPG's AUDITED consolidated statements (annual reports) and
the unaudited interim statements (IDX XBRL-rendered PDFs), with page citations.

Annual reports: statement rows are laid out as
    <Indonesian label> | <current> | [note ref] | <prior> | <English label>
so each AR yields FY and FY-1 values. Interim reports are laid out as
    <Indonesian label> | <current period> | <prior period> | <English label>

Every row records the source document, PDF page, period, unit and publication-date
anchor. Annual reports use the auditor's report date; interim reports use the
Board of Directors' statement date printed in the filing.

Outputs: data/reference/TAPG_statements_extracted.csv
         data/reference/TAPG_statements_checks.csv
Usage:   python -I quant/extract_tapg_statements.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "data" / "processed" / "text" / "TAPG"
REF = ROOT / "data" / "reference"

ANNUAL = {  # stem -> (pdf name, fiscal year)
    "AR_2021": ("AR 2021.pdf", 2021), "AR_2022": ("AR_2022.pdf", 2022),
    "AR_2023": ("AR_2023.pdf", 2023), "AR_2024": ("AR_2024.pdf", 2024),
    "TAPG_-_AR_2025": ("TAPG_-_AR_2025.pdf", 2025),
}
INTERIM = {  # stem -> (pdf, period label current, period label prior, period end, months)
    "FinancialStatement-2026-I-TAPG": ("FinancialStatement-2026-I-TAPG.pdf", "Q1 2026", "Q1 2025", "2026-03-31", 3),
    "FinancialStatement-2026-II-TAPG": ("FinancialStatement-2026-II-TAPG.pdf", "H1 2026", "H1 2025", "2026-06-30", 6),
    "FinancialStatement-2026-III-TAPG": ("FinancialStatement-2026-III-TAPG.pdf", "9M 2026", "9M 2025", "2026-09-30", 9),
}

# item -> (statement, Indonesian label regex in annual reports)
ANNUAL_ITEMS = {
    "revenue": ("IS", r"^(PENDAPATAN DARI KONTRAK|PENJUALAN|PENDAPATAN)$"),
    "cost_of_sales": ("IS", r"^BEBAN POKOK PENJUALAN"),
    "gross_profit": ("IS", r"^LABA BRUTO$"),
    "fv_change_biological_assets": ("IS", r"perubahan nilai wajar aset biologis$|^Keuntungan \(kerugian\) dari$"),
    "selling_marketing_exp": ("IS", r"^Beban penjualan"),
    "general_admin_exp": ("IS", r"^Beban umum dan administrasi"),
    "other_operating_income": ("IS", r"^Pendapatan (operasi )?lain(nya)?$"),
    "other_operating_expense": ("IS", r"^Beban (operasi )?lain(nya)?$"),
    "operating_profit": ("IS", r"^LABA USAHA$"),
    "finance_costs": ("IS", r"^Biaya keuangan$"),
    "finance_income": ("IS", r"^Pendapatan keuangan$"),
    "share_of_profit_jv_associates": ("IS", r"^Bagian (atas )?laba"),
    "profit_before_tax": ("IS", r"^LABA SEBELUM"),
    "income_tax_expense": ("IS", r"^(Beban|Manfaat \(beban\)) pajak penghasilan"),
    "profit_for_year": ("IS", r"^LABA TAHUN BERJALAN$"),
    "profit_attrib_owners": ("IS2", r"^Pemilik entitas induk$"),
    "cfo": ("CF", r"^Kas neto yang diperoleh dari$|^Kas bersih yang diperoleh dari$"),
    "dividends_received_jv": ("CF", r"^Penerimaan (pendapatan )?dividen"),
    "capex_fixed_assets": ("CF", r"^Perolehan aset tetap"),
    "dividends_paid": ("CF", r"^Pembayaran dividen"),
    "investment_in_jv": ("BS", r"^(Investasi (dalam|pada)|Kepentingan dalam) ventura bersama"),
    "investment_in_associates": ("BS", r"^Investasi (pada|dalam) entitas asosiasi"),
    "fixed_assets_net": ("BS", r"^Aset tetap$"),
    "cash": ("BS", r"^Kas dan setara kas$"),
    "total_assets": ("BS", r"^(TOTAL|JUMLAH) ASET$"),
    "total_equity": ("BS", r"^(TOTAL|JUMLAH) EKUITAS$"),
}

# item -> (regex on the English label that FOLLOWS the two value tokens, regex on the
# Indonesian label that PRECEDES them or None). Interim XBRL layout.
INTERIM_ITEMS = {
    "revenue": (r"^Sales and revenue", None),
    "cost_of_sales": (r"^Cost of sales and revenue", None),
    "gross_profit": (r"^Total gross profit", None),
    "selling_marketing_exp": (r"^Selling expenses", None),
    "general_admin_exp": (r"^General and administrative", None),
    "finance_income": (r"^Finance income", None),
    "finance_costs": (r"^Interest and finance costs", None),
    "share_of_profit_associates": (r"^Share of profit \(loss\) of associates", None),
    "share_of_profit_jv": (r"^Share of profit \(loss\) of joint", None),
    "profit_before_tax": (r"^Total profit \(loss\) before", None),
    "income_tax_expense": (r"^Tax benefit \(expenses\)", None),
    "profit_for_year": (r"^Total profit \(loss\) from continuing", None),
    "profit_attrib_owners": (r"^Profit \(loss\) attributable to parent", None),
    "cfo": (r"^Total net cash flows received from \(used in\) operating", None),
    "dividends_received_jv": (r"^Dividends received from (investing|joint)", None),
    "capex_fixed_assets": (r"^Payments for acquisition of property", None),
    "dividends_paid": (r"^Dividends paid from financing", None),
    "cash": (r"^Cash and cash equivalents", r"Kas dan setara kas$"),
    "total_assets": (r"^Total assets", None),
    "total_equity": (r"^Total equity", r"Jumlah ekuitas$"),
}
NEGATE = {"cost_of_sales", "selling_marketing_exp", "general_admin_exp", "finance_costs",
          "capex_fixed_assets", "dividends_paid"}  # normalise expenses/outflows to negative

VAL = re.compile(r"^\(?-?\d{1,3}([.,]\d{3})+\)?$|^\(?-?\d+\)?$|^-$")
NOTE = re.compile(r"^\d{1,2}[a-z]?(,\s?\d{1,2}[a-z]?)*$")


def load(stem):
    lines, pages, page = [], [], 0
    for ln in open(TXT / f"{stem}.txt", encoding="utf-8"):
        m = re.match(r"=== PAGE (\d+) ===", ln)
        if m:
            page = int(m.group(1)); continue
        s = re.sub(r"\s+", " ", ln).strip().strip("|").strip()
        if s:
            lines.append(s); pages.append(page)
    return lines, pages


def num(tok, thousands="."):
    if tok == "-":
        return 0.0
    neg = tok.startswith("(") or tok.startswith("-")
    t = tok.strip("()-")
    t = t.replace(thousands, "")
    return -float(t) if neg else float(t)


def find_page(lines, pages, regex, after=0):
    rx = re.compile(regex)
    for i, s in enumerate(lines):
        if pages[i] > after and rx.search(s):
            return pages[i]
    return None


def annual_rows(stem, pdf, fy):
    lines, pages = load(stem)
    audit_page = find_page(lines, pages, r"Laporan Auditor Independen|INDEPENDENT AUDITOR", 150)
    audit_date = None
    for i, s in enumerate(lines):
        if audit_page and audit_page <= pages[i] <= audit_page + 12:
            m = re.search(r"(\w+ \d{1,2}, 20\d\d)$", s)
            if m and re.search(r"/", s):
                audit_date = pd.to_datetime(m.group(1), errors="coerce")
    basis = "auditor report date"
    if audit_date is None or pd.isna(audit_date):
        # fallback: date the Directors authorised the statements for issue
        for s in lines:
            m = re.search(r"Directors on (\w+ \d{1,2}, 20\d\d)", s)
            if m:
                audit_date, basis = pd.to_datetime(m.group(1)), "FS authorised-for-issue date (Directors)"
                break
    is_p = find_page(lines, pages, r"^BEBAN POKOK PENJUALAN", audit_page or 150)
    bs_p = find_page(lines, pages, r"^ASET LANCAR$", audit_page or 150)
    cf_p = find_page(lines, pages, r"^LAPORAN ARUS KAS KONSOLIDASIAN", audit_page or 150)
    spans = {"BS": (bs_p, bs_p + 2), "IS": (is_p, is_p), "IS2": (is_p, is_p + 1),
             "CF": (cf_p, cf_p + 1)}
    rows = []
    for item, (stmt, pat) in ANNUAL_ITEMS.items():
        lo, hi = spans[stmt]
        rx = re.compile(pat, re.I if stmt == "CF" else 0)
        got = None
        for i, s in enumerate(lines):
            if not (lo <= pages[i] <= hi) or not rx.search(s):
                continue
            toks, j, skipped = [], i + 1, 0
            while j < len(lines) and len(toks) < 3:
                t = lines[j].replace(" ", "")
                if VAL.match(t) or NOTE.match(t):
                    toks.append(t)
                elif toks:
                    break
                else:
                    skipped += 1
                    if skipped > 4:
                        break
                j += 1
            vals = [t for k, t in enumerate(toks) if not (len(toks) == 3 and k == 1)]
            if len(vals) >= 2 and all(VAL.match(v) for v in vals[:2]):
                got = (pages[i], vals[:2])
                break
        if got is None:
            rows.append({"item": item, "source_doc": pdf, "status": "NOT FOUND", "statement": stmt})
            continue
        p, (cur, prior) = got
        for period, tok in ((fy, cur), (fy - 1, prior)):
            rows.append({
                "item": item, "statement": stmt, "period": f"FY{period}",
                "period_end": f"{period}-12-31", "months": 12, "value": num(tok), "raw_token": tok,
                "unit": "IDR mn", "basis": "audited (comparative)" if period != fy else "audited",
                "source_doc": pdf, "pdf_page": p,
                "publication_date": audit_date.date().isoformat() if audit_date is not None and not pd.isna(audit_date) else None,
                "publication_date_basis": basis, "status": "extracted"})
    return rows


def interim_tokens(stem):
    lines, pages = load(stem)
    toks, tpages = [], []
    i = 0
    while i < len(lines):
        t = lines[i]
        # a negative value is rendered as "( |)" or "(" ")" followed by the number
        if t.replace(" ", "") in {"(|)", "()"} and i + 1 < len(lines) and VAL.match(lines[i + 1].replace(" ", "")):
            toks.append("(" + lines[i + 1].replace(" ", "") + ")"); tpages.append(pages[i]); i += 2; continue
        if t == "(" and i + 2 < len(lines) and lines[i + 1] == ")" and VAL.match(lines[i + 2].replace(" ", "")):
            toks.append("(" + lines[i + 2].replace(" ", "") + ")"); tpages.append(pages[i]); i += 3; continue
        toks.append(t); tpages.append(pages[i]); i += 1
    return toks, tpages, lines


def interim_rows(stem, pdf, cur_lbl, prior_lbl, pend, months):
    toks, tpages, lines = interim_tokens(stem)
    pub = None
    for i, s in enumerate(lines):
        if s.startswith("Tanggal Surat Pernyataan"):
            for t in lines[i:i + 4]:
                d = pd.to_datetime(t, errors="coerce", format="%B %d, %Y")
                if not pd.isna(d):
                    pub = d.date().isoformat(); break
            break
    isval = lambda t: bool(VAL.match(t.replace(" ", "")))
    rows = []
    for item, (after_pat, before_pat) in INTERIM_ITEMS.items():
        ra, rb = re.compile(after_pat), re.compile(before_pat) if before_pat else None
        got = None
        for i in range(1, len(toks) - 2):
            if isval(toks[i]) and isval(toks[i + 1]) and not isval(toks[i + 2]) and not isval(toks[i - 1]):
                after = " ".join(toks[i + 2:i + 5])
                before = " ".join(toks[max(0, i - 2):i])
                if ra.search(after) and (rb is None or rb.search(before)):
                    if item == "total_equity" and "attributable" in after:
                        continue
                    got = (tpages[i], toks[i], toks[i + 1]); break
        if got is None:
            rows.append({"item": item, "source_doc": pdf, "status": "NOT FOUND", "statement": "interim"})
            continue
        p, cur, prior = got
        bs = item in {"cash", "total_assets", "total_equity"}
        for lbl, pe, tok in ((cur_lbl, pend, cur),
                             ("FY2025" if bs else prior_lbl, "2025-12-31" if bs else pend.replace("2026", "2025"), prior)):
            v = num(tok.replace(" ", ""), thousands=",")
            if item in NEGATE:
                v = -abs(v)
            rows.append({
                "item": item, "statement": "interim", "period": lbl, "period_end": pe,
                "months": 0 if bs else months, "value": v, "raw_token": tok,
                "unit": "IDR mn", "basis": "unaudited interim" if lbl != "FY2025" else "audited (comparative in interim)",
                "source_doc": pdf, "pdf_page": p,
                "publication_date": pub, "publication_date_basis": "Board of Directors' statement date",
                "status": "extracted"})
    return rows


def main() -> int:
    rows = []
    for stem, (pdf, fy) in ANNUAL.items():
        rows += annual_rows(stem, pdf, fy)
    for stem, args in INTERIM.items():
        rows += interim_rows(stem, *args)
    df = pd.DataFrame(rows)
    df.to_csv(REF / "TAPG_statements_extracted.csv", index=False)

    ok = df[df.status == "extracted"]
    # Cross-document consistency: the same period reported in two documents
    chk = []
    for (item, period), g in ok.groupby(["item", "period"]):
        if g["value"].nunique() > 1:
            chk.append({"check": "same period, different documents", "item": item, "period": period,
                        "result": "DIFFERS", "detail": "; ".join(f"{d} p{p}: {v:,.0f}" for d, p, v in
                                                              zip(g.source_doc, g.pdf_page, g.value))})
        elif len(g) > 1:
            chk.append({"check": "same period, different documents", "item": item, "period": period,
                        "result": "MATCH", "detail": f"{len(g)} documents"})
    # Arithmetic identities
    piv = ok.drop_duplicates(["item", "period"], keep="last").pivot(index="period", columns="item", values="value")
    for period, r in piv.iterrows():
        def ident(name, lhs, rhs, tol=2):
            if pd.notna(lhs) and pd.notna(rhs):
                chk.append({"check": name, "item": "", "period": period,
                            "result": "PASS" if abs(lhs - rhs) <= tol else "FAIL",
                            "detail": f"{lhs:,.0f} vs {rhs:,.0f}"})
        g = r.get
        ident("revenue + cost of sales = gross profit", g("revenue", float("nan")) + g("cost_of_sales", float("nan")), g("gross_profit"))
        if pd.notna(g("operating_profit")):
            ident("op. profit + fin. inc + fin. cost + share JV&assoc = PBT",
                  g("operating_profit") + g("finance_income", 0) + g("finance_costs", 0) + g("share_of_profit_jv_associates", 0),
                  g("profit_before_tax"))
        ident("PBT + tax = profit", g("profit_before_tax", float("nan")) + g("income_tax_expense", float("nan")), g("profit_for_year"))
    pd.DataFrame(chk).to_csv(REF / "TAPG_statements_checks.csv", index=False)

    print("NOT FOUND:", df[df.status == "NOT FOUND"][["item", "source_doc"]].values.tolist())
    c = pd.DataFrame(chk)
    print(c[c.result.isin(["FAIL", "DIFFERS"])].to_string(index=False))
    print(c.result.value_counts().to_string())
    pd.set_option("display.width", 250)
    print((piv.T / 1e3).round(1).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
