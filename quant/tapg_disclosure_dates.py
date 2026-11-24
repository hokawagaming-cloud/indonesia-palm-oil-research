"""Point-in-time availability dates for TAPG disclosures (A-012, A-013).

Document dates (auditor report, Directors' statement, PDF creation) are NOT proof of
public disclosure. Exact IDX upload timestamps could not be obtained (IDX blocks scripted
access). For each disclosure this module records:
  * document dates (from the PDFs)
  * press evidence: the earliest dated news report found, an upper bound on public
    availability. The date is taken from the article URL path (YYYYMMDD or YYYY-MM-DD);
    month-only URLs are not used.
  * an ASSUMED statutory deadline (to be verified against POJK text):
      unaudited interim statements: end of the month after period-end;
      audited annual statements: end of the 3rd month after year-end;
      annual report (operational tables): end of the 4th month after year-end.
available_from = next weekday after the press date if press evidence exists, otherwise
the next weekday after the assumed deadline. Each row is labelled with its basis.
No row is claimed as verified point-in-time without an IDX timestamp.

Output: data/reference/TAPG_disclosure_dates.csv
Usage:  python -I quant/tapg_disclosure_dates.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"

D = [  # period, kind, period_end, doc date, doc-date basis, press date, press url
    ("FY2020", "audited FS", "2020-12-31", None, "not in hand (IPO in 2021; FY2020 is a comparative in AR2021)", None, None),
    ("FY2021", "audited FS", "2021-12-31", "2022-03-22", "Directors' authorisation (AR2021)", None, None),
    ("FY2022", "audited FS", "2022-12-31", "2023-02-24", "auditor report (AR2022)", None, None),
    ("FY2023", "audited FS", "2023-12-31", "2024-03-07", "auditor report (AR2023)", None, None),
    ("FY2024", "audited FS", "2024-12-31", "2025-02-26", "auditor report (AR2024)", "2025-02-28", "https://market.bisnis.com/read/20250228/7/1843371/laba-bersih-2024-melejit-94-saham-triputra-agro-tapg-tancap-gas"),
    ("FY2025", "audited FS", "2025-12-31", "2026-03-16", "auditor report (AR2025)", None, "https://www.receh.in/2026/03/laba-tapg-melejit-rp37-triliun-di-2025.html (month only - not used)"),
    ("Q1 2024", "interim FS", "2024-03-31", None, "document not in hand", "2024-05-02", "https://market.bisnis.com/read/20240502/192/1762315/emiten-cpo-grup-triputra-tapg-cetak-laba-bersih-rp3708-miliar-pada-kuartal-i2024"),
    ("H1 2024", "interim FS", "2024-06-30", None, "document not in hand", "2024-07-25", "https://market.bisnis.com/read/20240725/192/1785526/emiten-cpo-grup-triputra-tapg-cetak-laba-bersih-rp966-miliar-semester-i2024"),
    ("H1 2025", "interim FS", "2025-06-30", None, "comparative in H1 2026 filing", "2025-07-28", "https://market.bisnis.com/read/20250728/192/1896921/emiten-sawit-tp-rachmat-tapg-panen-laba-rp169-triliun-semester-i2025"),
    ("9M 2025", "interim FS", "2025-09-30", None, "comparative in 9M 2026 filing", "2025-10-28", "https://market.bisnis.com/read/20251028/192/1924054/laba-bersih-emiten-cpo-tp-rachmat-tapg-melonjak-6567-jadi-rp268-triliun"),
    ("Q1 2025", "interim FS", "2025-03-31", None, "comparative in Q1 2026 filing", None, None),
    ("Q1 2026", "interim FS", "2026-03-31", "2026-04-27", "Directors' statement date (IDX XBRL filing)", "2026-04-28", "https://www.bareksa.com/berita/saham/2026-04-28/tapg-q1-2026-kinerja-melambat-cpo-jadi-penopang-prospek-ke-depan"),
    ("H1 2026", "interim FS", "2026-06-30", "2026-07-29", "Directors' statement date (IDX XBRL filing)", None, None),
    ("9M 2026", "interim FS", "2026-09-30", "2026-10-28", "Directors' statement date (IDX XBRL filing)", None, "https://www.romisaputra.com/2026/10/... (month only - not used)"),
]
AR = [("FY2021", "2022-04-26"), ("FY2022", "2023-03-31"), ("FY2023", "2024-03-28"), ("FY2024", "2025-04-09"), ("FY2025", "2026-04-21")]


def next_weekday(d: pd.Timestamp) -> pd.Timestamp:
    d = d + pd.Timedelta(days=1)
    while d.weekday() >= 5:
        d += pd.Timedelta(days=1)
    return d


def deadline(period_end: str, kind: str) -> pd.Timestamp:
    pe = pd.Timestamp(period_end)
    months = {"interim FS": 1, "audited FS": 3, "annual report": 4}[kind]
    return (pe + pd.offsets.MonthEnd(months)).normalize()


def main() -> int:
    rows = []
    for period, kind, pe, doc, docb, press, url in D:
        dl = deadline(pe, kind)
        if press:
            avail, basis = next_weekday(pd.Timestamp(press)), "EVIDENCE: next weekday after dated press report (upper bound)"
        else:
            avail, basis = next_weekday(dl), "ASSUMPTION: next weekday after assumed statutory deadline"
        rows.append({"period": period, "disclosure": kind, "period_end": pe, "document_date": doc,
                     "document_date_basis": docb, "press_date": press, "press_url": url,
                     "assumed_deadline": dl.date(), "available_from": avail.date(), "basis": basis,
                     "pit_status": "not verified (no IDX timestamp)"})
    for period, pdf_date in AR:
        pe = f"{period[2:]}-12-31"
        dl = deadline(pe, "annual report")
        avail = max(next_weekday(dl), next_weekday(pd.Timestamp(pdf_date)))
        rows.append({"period": period, "disclosure": "annual report (operational tables)", "period_end": pe,
                     "document_date": pdf_date, "document_date_basis": "PDF creation date", "press_date": None,
                     "press_url": None, "assumed_deadline": dl.date(), "available_from": avail.date(),
                     "basis": "ASSUMPTION: later of assumed AR deadline and PDF creation, +1 weekday",
                     "pit_status": "not verified (no IDX timestamp)"})
    out = pd.DataFrame(rows)
    out.to_csv(REF / "TAPG_disclosure_dates.csv", index=False)
    print(out[["period", "disclosure", "document_date", "press_date", "assumed_deadline", "available_from", "basis"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
