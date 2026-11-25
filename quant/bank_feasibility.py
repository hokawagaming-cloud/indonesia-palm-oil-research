"""Phase IX, Priority 2: Indonesian bank monthly (bank-only) report feasibility — inventory only.
Builds a month-by-bank inventory from IR listings saved in data/raw/banking/listings/ (git-ignored):
  BBRI  bri_YYYY.html   (ir-bri.com yearly pages; posting date per report)          S-062
  BBCA  bca_inventory.txt (bca.co.id report-list server action; filename date prefix) S-063
  BMRI  bmri_YYYY.html  (bankmandiri.co.id monthly-financials; ?t= upload epoch)      S-064
  BBNI  bbni_inventory.txt (bni.co.id financial-reports; no dates in listing)        S-065
Quarterly consolidated filing timestamps: jejaksaham mirror (S-060), Jul-2023+ only.
Timestamp quality per bank is recorded explicitly ('posted', 'filename', 'upload_epoch', 'none').

Usage: python -I -X utf8 quant/bank_feasibility.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / "data" / "raw" / "banking" / "listings"
OUT = ROOT / "data" / "reference" / "research"
ID_MONTHS = {"januari": 1, "februari": 2, "februarii": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
             "september": 9, "oktober": 10, "november": 11, "desember": 12, "january": 1, "february": 2, "march": 3, "may": 5,
             "june": 6, "july": 7, "august": 8, "october": 10, "december": 12}


def _month_from_text(s: str) -> pd.Period | None:
    s0 = s.lower()
    s = re.sub(r"^20\d{6}", "", s0)           # drop a leading publication-date prefix (YYYYMMDD)
    if not re.search(r"20(1[5-9]|2\d)", s) and re.match(r"^20\d{6}", s0):
        pub = pd.to_datetime(s0[:8], format="%Y%m%d", errors="coerce")   # no period year in name: month before publication
        mm = re.search(r"(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)", s)
        if pd.notna(pub) and mm:
            p = pd.Period(f"{pub.year}-{ID_MONTHS[mm.group(1)]:02d}", "M")
            return p if p <= pub.to_period("M") else p - 12
    m = re.search(r"(januari|februarii|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember|january|february|march|may|june|july|august|october|december)[^\d]{0,3}(20\d\d)?", s)
    if not m:
        return None
    yr = m.group(2) or (re.search(r"20(1[5-9]|2\d)", s) or [None])[0]
    if not yr:
        return None
    return pd.Period(f"{yr}-{ID_MONTHS[m.group(1)]:02d}", "M")


def bri() -> pd.DataFrame:
    rows = []
    for y in range(2018, 2027):
        t = (L / f"bri_{y}.html").read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"<td>(\d{1,2} \w{3} \d{4})</td>\s*<td>([^<]*Monthly Publication[^<]*)</td>", t, re.S):
            title = m.group(2).strip()
            if re.search(r"(?i)audited\)|revised", title):
                continue
            per = pd.to_datetime(re.sub(r".*Publication\s+", "", title), errors="coerce")
            if pd.isna(per):
                continue
            rows.append({"bank": "BBRI", "month": per.to_period("M"), "published": pd.to_datetime(m.group(1)), "ts_quality": "posted (IR listing date)"})
    return pd.DataFrame(rows)


def bca() -> pd.DataFrame:
    rows = []
    for line in (L / "bca_inventory.txt").read_text(encoding="utf-8").splitlines():
        if "|" not in line:
            continue
        _, path = line.split("|", 1)
        name = path.split("/")[-1]
        per = _month_from_text(name)
        d = re.match(r"(20\d{6})", name)
        pub = pd.to_datetime(d.group(1), format="%Y%m%d", errors="coerce") if d else pd.NaT
        if pd.notna(pub) and per is not None and (pub - per.to_timestamp(how="end")).days > 120:
            pub = pd.NaT                       # obvious filename typo (e.g. 20280229 for Jan-2024)
        rows.append({"bank": "BBCA", "month": per, "published": pub,
                     "ts_quality": "filename date prefix" if pd.notna(pub) else "none (pre-2020 names)"})
    return pd.DataFrame(rows).dropna(subset=["month"]).drop_duplicates(["bank", "month"])


def bmri() -> pd.DataFrame:
    rows = []
    for y in range(2018, 2027):
        t = (L / f"bmri_{y}.html").read_text(encoding="utf-8", errors="ignore")
        for href in set(html.unescape(h) for h in re.findall(r'href="([^"]*/documents/[^"]*\.pdf[^"]*)"', t)):
            name = href.split("/")[-2] if href.rstrip("/").count("/") > 4 else href
            fn = re.search(r"/documents/\d+/\d+/([^/]+)\.pdf", href)
            fn = fn.group(1).replace("+", " ") if fn else ""
            per = _month_from_text(fn)
            if per is None:
                m = re.search(r"(20\d\d)\s+(\d{2})\s", fn)
                per = pd.Period(f"{m.group(1)}-{m.group(2)}", "M") if m else None
            ep = re.search(r"\?t=(\d{13})", href)
            pub = pd.to_datetime(int(ep.group(1)), unit="ms") if ep else pd.NaT
            rows.append({"bank": "BMRI", "month": per, "published": pub,
                         "ts_quality": "upload epoch (?t=, last modified)" if ep else "none"})
    return pd.DataFrame(rows).dropna(subset=["month"]).sort_values("published").drop_duplicates(["bank", "month"], keep="first")


def bni() -> pd.DataFrame:
    rows = [{"bank": "BBNI", "month": pd.Period(line.split("|")[0], "M"), "published": pd.NaT, "ts_quality": "none (listing undated)"}
            for line in (L / "bbni_inventory.txt").read_text(encoding="utf-8").splitlines() if "|" in line]
    return pd.DataFrame(rows)


def main() -> int:
    inv = pd.concat([bri(), bca(), bmri(), bni()], ignore_index=True)
    inv = inv[(inv.month >= pd.Period("2018-01", "M")) & (inv.month <= pd.Period("2026-12", "M"))]
    inv["lag_days"] = [(p - m.to_timestamp(how="end")).days if pd.notna(p) else None for p, m in zip(inv.published, inv.month)]
    inv["quarter_end_month"] = [m.month in (3, 6, 9, 12) for m in inv.month]
    inv = inv.sort_values(["bank", "month"])
    inv.to_csv(OUT / "bank_monthly_inventory.csv", index=False)
    cov = inv.groupby(["bank", inv.month.dt.year]).size().unstack(0).fillna(0).astype(int)
    lag = inv.dropna(subset=["lag_days"]).groupby("bank").lag_days.describe()[["count", "50%", "min", "max"]]
    q = pd.read_csv(ROOT / "data" / "raw" / "banking" / "jejaksaham" / "quarterly_filings.csv")
    ql = q.groupby("ticker").days_after_qend.agg(["count", "median", "min", "max"])
    summ = cov.T.assign(total_2018_2026=cov.T.sum(axis=1))
    summ = summ.join(lag.rename(columns={"count": "n_dated", "50%": "median_lag_days", "min": "min_lag", "max": "max_lag"}))
    summ = summ.join(ql.rename(columns={"count": "n_quarterly_dated", "median": "quarterly_median_days", "min": "q_min", "max": "q_max"}))
    summ.to_csv(OUT / "bank_monthly_coverage.csv")
    pd.set_option("display.width", 250)
    print(cov.to_string()); print(summ.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
