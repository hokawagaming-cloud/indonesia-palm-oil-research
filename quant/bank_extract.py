"""MVP-B1 data layer (Phase X): extract BBCA / BBRI monthly (bank-only, YTD) and quarterly publication
(bank-only + consolidated, YTD) line items from the official IR PDFs in data/raw/banking/<BANK>/ (git-ignored),
reconstruct standalone months and quarters, and attach point-in-time availability dates.

Scope discipline: bank-only ('INDIVIDUAL'/'INDIVIDU') and consolidated ('CONSOLIDATED'/'KONSOLIDASIAN') figures are
kept in separate columns and never mixed. Quarterly publications have 4 columns:
[bank-only current, bank-only prior-period, consolidated current, consolidated prior-period].

Availability (A-041):
  BBRI: IR posting date of the report (S-062).
  BBCA: YYYYMMDD filename prefix when present and plausible (5..75 days after period end); otherwise 'unverified'.
  Conservative (sensitivity): end of the month following the period (monthly, POJK 37/2019 deadline) or
  end of the month following quarter end (quarterly publication), whichever is LATER than any verified date.
Revisions: where an IR lists an original and a revised/audited version, the ORIGINAL (earliest) is used.

Outputs (data/reference/research/): bank_monthly_extract.csv, bank_quarterly_extract.csv, bank_extract_checks.csv
Usage: python -I -X utf8 quant/bank_extract.py
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "banking"
OUT = ROOT / "data" / "reference" / "research"
NUM = r"\(?-?\d{1,3}(?:[.,]\d{3})+\)?|\(?-?\d+\)?|-(?=\s)"
MONTHS = {"JANUARY": 1, "JANUARI": 1, "FEBRUARY": 2, "FEBRUARI": 2, "FEBRUARII": 2, "MARCH": 3, "MARET": 3, "APRIL": 4,
          "MAY": 5, "MEI": 5, "JUNE": 6, "JUNI": 6, "JULY": 7, "JULI": 7, "AUGUST": 8, "AGUSTUS": 8, "SEPTEMBER": 9,
          "OCTOBER": 10, "OKTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12, "DESEMBER": 12, "DES": 12, "SEP": 9, "JUN": 6,
          "MAR": 3, "DEC": 12}


def _n(tok: str) -> float:
    tok = tok.strip()
    if tok in ("-", ""):
        return 0.0
    neg = tok.startswith("(") or tok.startswith("-")
    v = float(re.sub(r"[^\d]", "", tok) or 0)
    return -v if neg else v


def nums_after(t: str, pos: int, k: int, window: int = 400) -> list[float] | None:
    seg = t[pos:pos + window]
    toks = re.findall(NUM, seg)
    toks = [x for x in toks if not re.fullmatch(r"\(?\d{1,2}\)?", x.strip("."))]  # drop list numbering like 2.
    if len(toks) < k:
        return None
    return [_n(x) for x in toks[:k]]


def find(t: str, pattern: str, start: int = 0) -> int:
    m = re.compile(pattern).search(t, start)
    return m.end() if m else -1


def extract_doc(path: Path, k: int) -> dict:
    t = " ".join(" ".join(p.get_text() for p in pymupdf.open(path)).split()).upper()
    t = re.sub(r"(\d) (\d{3})\)", r"\1,\2)", t)          # '(488 063)' typo -> '(488,063)'
    out = {}
    # P&L section starts at the first interest-income heading
    pl = find(t, r"INTEREST INCOME AND (?:INTEREST )?EXPENSES|PENDAPATAN DAN BEBAN BUNGA|PENDAPATAN BUNGA")
    pl = max(pl, 0)
    p = find(t, r"NET INTEREST INCOME(?: \(EXPENSES?\))?(?:/NET RETURN)?|PENDAPATAN \(BEBAN\) BUNGA BERSIH", pl)
    out["nii"] = nums_after(t, p, k) if p > 0 else None
    for key, pat in (("int_inc", r"1\. (?:INTEREST INCOME(?:/RETURN)?|PENDAPATAN BUNGA)"),
                     ("int_exp", r"2\. (?:INTEREST EXPENSES?(?:/RETURN)?|BEBAN BUNGA)")):
        q = find(t, pat, pl)
        if q > 0:
            head = t[q:q + 25]
            if "RUPIAH" in head:                                   # split into a. Rupiah / b. foreign currency
                r1 = find(t, r"RUPIAH", q); r2 = find(t, r"(?:FOREIGN CURRENC\w*|VALUTA ASING)", q)
                a, b = nums_after(t, r1, k), nums_after(t, r2, k)
                out[key] = [x + y for x, y in zip(a, b)] if a and b else None
            else:
                out[key] = nums_after(t, q, k)
    q = find(t, r"(?:\(IMPAIRMENT\)|(?:LOSS )?IMPAIRMENT (?:LOSSES? )?(?:ON|OF|FOR) (?:FINANCIAL )?ASSETS|PENURUNAN NILAI ASET KEUANGAN \(IMPAIRMENT\))(?= \(?\d)", max(p, 0))
    out["impairment"] = nums_after(t, q, k) if q > 0 else None
    if out["impairment"] is None:   # older layout: 'E. IMPAIRMENT I. SECURITIES x II. LOANS y III. SHARIA z IV. OTHER w' (no total)
        q = find(t, r"E\. IMPAIRMENT(?: (?:ON|OF) FINANCIAL ASSETS)? (?=I\. )", max(p, 0))
        if q > 0:
            v = nums_after(t, q, 4 * k, window=600)
            out["impairment"] = list(np.array(v).reshape(4, k).sum(axis=0)) if v else None
    q = find(t, r"(?<!NON )(?<!NON-)(?:OPERATIONAL|OPERATING) (?:PROFIT|INCOME) \(LOSS\)(?= \(?\d)|(?<!NON )LABA \(RUGI\) OPERASIONAL(?= \(?\d)"
                r"|(?:INCOME|PROFIT)(?: \(LOSS\))? FROM OPERATIONS(?= \(?\d)", max(p, 0))
    out["op_profit"] = nums_after(t, q, k) if q > 0 else None
    pbt = find(t, r"BEFORE (?:INCOME )?TAX(?:ES)?(?= \(?\d)|SEBELUM PAJAK(?: PENGHASILAN)?(?= \(?\d)", max(p, 0))
    out["pbt"] = nums_after(t, pbt, k) if pbt > 0 else None
    out["op_from_pbt"] = None
    if out["impairment"] is not None:   # expense line: some months print expenses in parentheses
        out["impairment"] = [abs(x) for x in out["impairment"]]
    if out["op_profit"] is None and out["pbt"] is not None and not re.search(r"NON[ -]OPERA(?:TING|TIONAL|SIONAL)", t):
        out["op_profit"] = list(out["pbt"]); out["op_from_pbt"] = [1.0] * k   # layout without a non-operating section
    q = find(t, r"(?:NET )?PROFIT(?: \(LOSS\))? (?:AFTER (?:INCOME )?TAX(?: - NET)?|CURRENT PERIOD|CURRENT YEAR|FOR THE (?:CURRENT )?(?:PERIOD|YEAR))(?= \(?\d)"
                r"|LABA \(RUGI\) BERSIH(?: PERIODE BERJALAN| TAHUN BERJALAN)?(?= \(?\d)|NET INCOME(?: \(LOSS\))?(?: FOR THE (?:CURRENT )?PERIOD| CURRENT PERIOD)?(?= \(?\d)", max(pbt, 0))
    out["net_profit"] = nums_after(t, q, k) if q > 0 else None
    if k == 4:
        a = find(t, r"AT+RIBUT+ABLE TO ?:?|DIATRIBUSIKAN KEPADA ?:?", max(pbt, 0))
        q = find(t, r"OWNERS?(?: OF (?:THE )?PARENT(?: ENTITY| COMPANY)?)?(?= \(?\d)|-? ?PARENT (?:COMPANY|ENTITY)(?= \(?\d)|PEMILIK(?: ENTITAS INDUK)?(?= \(?\d)", max(a, 0)) if a > 0 else -1
        out["np_owners"] = nums_after(t, q, 4) if q > 0 else None
    q = find(t, r"(?:\b9\. )?LOANS(?: AND FINANCING)?(?= \(?\d)|\bKREDIT(?= \(?\d)")
    out["loans"] = nums_after(t, q, k) if q > 0 else None
    for key, pat in (("dep_ca", r"(?:CURRENT ACCOUNTS?|DEMAND DEPOSITS|\bGIRO)(?= \(?\d)"),
                     ("dep_sa", r"(?:SAVINGS? (?:ACCOUNTS?|DEPOSITS)|SAVING ACCOUNT|\bTABUNGAN)(?= \(?\d)"),
                     ("dep_td", r"(?:TIME DEPOSITS?|SIMPANAN BERJANGKA|DEPOSITO BERJANGKA)(?= \(?\d)")):
        q = find(t, pat)
        out[key] = nums_after(t, q, k) if q > 0 else None
    if k == 4:
        q = find(t, r"\bNPL(?: GROSS)?(?= \d)|NON PERFORMING LOANS?(?: GROSS)?(?= \d)")
        v = re.findall(r"\d+[.,]\d+", t[q:q + 40]) if q > 0 else []
        out["npl_gross_pct"] = [float(v[0].replace(",", ".")), np.nan, np.nan, np.nan] if v else None
    return out


def period_of(bank: str, kind: str, title: str, url: str) -> pd.Period | None:
    s = (title + " " + url.split("/")[-1]).upper().replace("-", " ").replace("_", " ")
    s = re.sub(r"\b20\d{6}\b", " ", s)
    y = re.findall(r"\b(20[12]\d)\b", s)
    mo = [MONTHS[w] for w in re.findall(r"\b(" + "|".join(MONTHS) + r")\b", s)]
    if not y or not mo:
        m = re.search(r"\b(MAR|JUN|SEP|DES|DEC)(\d{2})\b", s)
        if m:
            return pd.Period(f"20{m.group(2)}-{MONTHS[m.group(1)]:02d}", "M")
        return None
    return pd.Period(f"{y[0]}-{mo[0]:02d}", "M")


def availability(bank: str, kind: str, listed: str, url: str, per: pd.Period) -> tuple[pd.Timestamp, str]:
    pend = per.to_timestamp(how="end").normalize()
    if bank == "BBRI":
        return pd.Timestamp(listed), "BBRI IR posting date"
    m = re.search(r"/(20\d{6})", url)
    if m:
        d = pd.to_datetime(m.group(1), format="%Y%m%d", errors="coerce")
        if pd.notna(d) and 5 <= (d - pend).days <= 75:
            return d, "BBCA filename date prefix"
    return pd.NaT, "unverified"


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    man = pd.read_csv(RAW / "download_manifest.csv")
    man = man[man.file.notna()].copy()
    man["revised"] = man.title.str.contains(r"(?i)revised|audited\)|rev\d")
    mrows, qrows = [], []
    for r in man.itertuples():
        per = period_of(r.bank, r.kind, r.title, r.url)
        if per is None:
            continue
        k = 1 if r.kind == "M" else 4
        try:
            v = extract_doc(Path(r.file), k)
        except Exception as e:  # noqa: BLE001
            print("parse error", r.file, e); continue
        avail, basis = availability(r.bank, r.kind, r.listed_date, r.url, per)
        lag_m = 1 if r.kind == "M" else 1
        cons = (per + lag_m).to_timestamp(how="end").normalize()
        base = {"bank": r.bank, "period": per, "source": Path(r.file).name, "listed_date": r.listed_date, "revised_version": r.revised,
                "avail_verified": avail, "avail_basis": basis, "avail_conservative": max(cons, avail) if pd.notna(avail) else cons}
        if k == 1:
            mrows.append({**base, **{f"bo_{c}": (x[0] if x else np.nan) for c, x in v.items()}})
        else:
            row = dict(base)
            for c, x in v.items():
                row[f"bo_{c}"] = x[0] if x else np.nan
                row[f"bo_{c}_prior"] = x[1] if x else np.nan
                row[f"cons_{c}"] = x[2] if x else np.nan
                row[f"cons_{c}_prior"] = x[3] if x else np.nan
            qrows.append(row)
    M = pd.DataFrame(mrows).sort_values(["bank", "period", "revised_version", "listed_date"])
    M = M.drop_duplicates(["bank", "period"], keep="first")              # original (non-revised) vintage first
    Q = pd.DataFrame(qrows).sort_values(["bank", "period", "revised_version", "listed_date"]).drop_duplicates(["bank", "period"], keep="first")
    Q["period"] = Q.period.apply(lambda p: p.asfreq("Q"))
    return M, Q


def checks(M: pd.DataFrame, Q: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for df, scope in ((M, "monthly_bo"), (Q, "quarterly")):
        for b, g in df.groupby("bank"):
            rows.append({"bank": b, "scope": scope, "n": len(g),
                         "nii_identity_ok": float(((g.bo_int_inc - g.bo_int_exp - g.bo_nii).abs() <= 0.002 * g.bo_nii.abs() + 2).mean()),
                         "np_lt_pbt_ok": float(((g.bo_net_profit <= g.bo_pbt + 1) & (g.bo_net_profit > 0.5 * g.bo_pbt)).mean()),
                         "missing_np": int(g.bo_net_profit.isna().sum()), "missing_nii": int(g.bo_nii.isna().sum()),
                         "missing_cons_owner": int(g.get("cons_np_owners", pd.Series(dtype=float)).isna().sum()) if scope == "quarterly" else 0})
    # monthly quarter-end (2018-2020) vs quarterly bank-only current column
    mq = M[M.period.apply(lambda p: p.month in (3, 6, 9, 12))].copy()
    mq["q"] = mq.period.apply(lambda p: p.asfreq("Q"))
    j = mq.merge(Q[["bank", "period", "bo_net_profit", "bo_nii"]].rename(columns={"period": "q"}), on=["bank", "q"], suffixes=("_m", "_q"))
    for b, g in j.groupby("bank"):
        rows.append({"bank": b, "scope": "monthly_qe_vs_quarterly_bo", "n": len(g),
                     "np_match_share": float(((g.bo_net_profit_m - g.bo_net_profit_q).abs() <= 0.005 * g.bo_net_profit_q.abs()).mean()),
                     "nii_match_share": float(((g.bo_nii_m - g.bo_nii_q).abs() <= 0.005 * g.bo_nii_q.abs()).mean())})
    return pd.DataFrame(rows)


def main() -> int:
    M, Q = build()
    C = checks(M, Q)
    M.to_csv(OUT / "bank_monthly_extract.csv", index=False)
    Q.to_csv(OUT / "bank_quarterly_extract.csv", index=False)
    C.to_csv(OUT / "bank_extract_checks.csv", index=False)
    pd.set_option("display.width", 250)
    print(C.to_string())
    print(M.groupby("bank").avail_basis.value_counts())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
