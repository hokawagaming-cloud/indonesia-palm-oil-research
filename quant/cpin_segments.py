"""CPIN segment extraction (Phase VIII, M-VIII-1). Reads the segment note ('INFORMASI SEGMEN /
SEGMENT INFORMATION') of each interim/annual FS in data/raw/company/CPIN/ (S-055) and extracts
CURRENT-period cumulative (YTD) segment sales and segment results for: feed, broiler, DOC,
processed chicken, others, elimination, consolidated. Values in IDR million.

Checks (per file): sum of segments + elimination == consolidated (sales and results).
FY2023 has no own file on cp.co.id: taken from the comparative column of the FY2024 FS and
flagged vintage='comparative' (strict PIT: available only from the FY2024 filing).

Usage: python -I -X utf8 quant/cpin_segments.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "company" / "CPIN"
OUT = ROOT / "data" / "reference" / "research"
SEGS = ["feed", "broiler", "doc", "processed", "others", "elim", "consolidated"]
NUM = re.compile(r"^\(?-?[\d.]+\)?$|^-$")


def _num(t: str) -> float:
    if t == "-":
        return 0.0
    neg = t.startswith("(")
    v = float(t.strip("()").replace(".", ""))
    return -v if neg else v


def _tokens_after(text: str, label: str, n: int = 7, start: int = 0) -> tuple[list[float] | None, int]:
    i = text.find(label, start)
    if i < 0:
        return None, -1
    out = []
    for line in text[i + len(label):].splitlines():
        for tok in line.split():
            if NUM.match(tok):
                out.append(_num(tok))
                if len(out) == n:
                    return out, i
            elif out:  # a word after numbers started -> keep scanning only numeric tokens
                pass
    return None, i


def segment_text(path: Path) -> str:
    """Upper-cased text of the segment note: the first page mentioning the note whose next pages
    contain the segment-sales table (skips the accounting-policy reference and 'continued' pages)."""
    d = pymupdf.open(path)
    txt = [d[i].get_text().upper() for i in range(d.page_count)]
    for i, t in enumerate(txt):
        if "INFORMASI SEGMEN" in t or "SEGMENT INFORMATION" in t:
            block = "\n".join(txt[i:i + 5])
            if "PENJUALAN SEGMEN" in block:
                return block
    raise ValueError(f"no segment table in {path.name}")


def _find_first(t: str, labels: list[str], start: int) -> tuple[list[float] | None, int]:
    best = (None, -1)
    for lab in labels:
        v, i = _tokens_after(t, lab, 7, start)
        if v is not None and (best[1] < 0 or i < best[1]):
            best = (v, i)
    return best


def extract(path: Path, occurrence: int = 0) -> dict:
    """occurrence 0 = current-period table; 1 = comparative table (next occurrence of the labels).
    Two layouts: newer 'Hasil penjualan segmen' + 'Hasil segmen'; older 'Total penjualan segmen' +
    'Laba bruto' + allocated 'Beban penjualan' + allocated 'Beban umum dan administrasi'.
    Segment result = gross profit - allocated selling - allocated G&A in both (reconciles to operating
    profit after unallocated items)."""
    t = segment_text(path)
    pos, fmt = 0, None
    for _ in range(occurrence + 1):
        sales, i = _find_first(t, ["HASIL PENJUALAN SEGMEN", "TOTAL PENJUALAN SEGMEN", "JUMLAH PENJUALAN SEGMEN"], pos)
        if sales is None:
            raise ValueError(f"sales parse failed {path.name}")
        nxt_sales, k = _find_first(t, ["HASIL PENJUALAN SEGMEN", "TOTAL PENJUALAN SEGMEN", "JUMLAH PENJUALAN SEGMEN"], i + 10)
        res, j = _tokens_after(t, "HASIL SEGMEN", 7, i + 10)
        if res is not None and (k < 0 or j < k):
            fmt, pos = "new", j + 10
            gp = None
        else:
            gp, a = _tokens_after(t, "LABA BRUTO", 7, i + 10)
            sell, b = _tokens_after(t, "BEBAN PENJUALAN", 7, a + 5)
            ga, c = _tokens_after(t, "BEBAN UMUM DAN ADMINISTRASI", 7, b + 5)
            if None in (gp, sell, ga) or (k >= 0 and c > k):
                raise ValueError(f"result parse failed {path.name}")
            res = [x + y + z for x, y, z in zip(gp, sell, ga)]
            fmt, pos = "old", c + 10
    row = {f"sales_{k}": v for k, v in zip(SEGS, sales)}
    row.update({f"result_{k}": v for k, v in zip(SEGS, res)})
    if gp is not None:
        row.update({f"gp_{k}": v for k, v in zip(SEGS, gp)})
    row["layout"] = fmt
    return row


def period_of(name: str) -> pd.Period:
    yy, mm = int(name[5:7]), int(name[7:9])
    return pd.Period(f"20{yy:02d}-{mm:02d}", "M").asfreq("Q")


# Basis break: the FY2020 FS restated segment presentation (FY2019 consolidated sales 58.6tn -> 42.5tn,
# results reallocated between segments). Old basis = original 2018Q1-2020Q3 files (+FY2018, FY2019);
# new basis = FY2020 onward, with 2020Q1-Q3 taken from the comparative columns of the 2021 interims.
NEW_BASIS_FROM = pd.Period("2020Q4", "Q")
DEADLINE_LAG = {1: 1, 2: 1, 3: 1, 4: 3}   # months after period end: OJK deadlines Q1/H1/9M +1m, FY audited +3m


def deadline(p: pd.Period) -> pd.Timestamp:
    """Regulatory filing deadline of the report for period p (A-038: used as availability date)."""
    return (p.asfreq("M", "end") + DEADLINE_LAG[p.quarter]).to_timestamp(how="end").normalize()


def build() -> pd.DataFrame:
    rows = []
    for f in sorted(RAW.glob("CPIN-*IE.pdf")):
        p = period_of(f.name)
        r = extract(f)
        r.update(period=p, basis="new" if p >= NEW_BASIS_FROM else "old", source=f.name, vintage="current",
                 available_from=deadline(p))
        rows.append(r)
    comps = [("CPIN-210331IE.pdf", "2020Q1"), ("CPIN-210630IE.pdf", "2020Q2"), ("CPIN-210930IE.pdf", "2020Q3"),
             ("CPIN-241231IE.pdf", "2023Q4")]
    for f, per in comps:
        r = extract(RAW / f, occurrence=1)
        host = period_of(f)
        # FY2023: no own file on cp.co.id; the original FY2023 FS was filed on IDX by its deadline (A-038),
        # so its availability is the FY2023 deadline. 2020 restated values exist only from the 2021 filings.
        avail = deadline(pd.Period(per, "Q")) if per == "2023Q4" else deadline(host)
        r.update(period=pd.Period(per, "Q"), basis="new", source=f + " (comparative)", vintage="comparative", available_from=avail)
        rows.append(r)
    df = pd.DataFrame(rows).sort_values(["basis", "period"]).reset_index(drop=True)
    for kind in ("sales", "result"):
        df[f"chk_{kind}"] = df[[f"{kind}_{s}" for s in SEGS[:-1]]].sum(axis=1) - df[f"{kind}_consolidated"]
    return df


def standalone(cum: pd.DataFrame) -> pd.DataFrame:
    """YTD -> standalone quarter within each basis: Q1 = YTD; Qn = YTD_n - YTD_(n-1) (same year, same basis)."""
    cols = [c for c in cum.columns if c.startswith(("sales_", "result_"))]
    out = []
    for basis, g in cum.groupby("basis"):
        g = g.set_index("period").sort_index()
        for p in g.index:
            if p.quarter == 1:
                v = g.loc[p, cols]
            elif (p - 1) in g.index:
                v = g.loc[p, cols] - g.loc[p - 1, cols]
            else:
                continue
            row = v.to_dict()
            row.update(period=p, basis=basis, available_from=g.loc[p, "available_from"], source=g.loc[p, "source"])
            out.append(row)
    q = pd.DataFrame(out)
    for seg in SEGS[:-2] + ["consolidated"]:
        q[f"margin_{seg}"] = q[f"result_{seg}"] / q[f"sales_{seg}"]
    # one series per quarter: new basis wherever it exists
    q = q.sort_values(["period", "basis"]).drop_duplicates("period", keep="first").set_index("period").sort_index()
    return q


def main() -> int:
    cum = build()
    OUT.mkdir(parents=True, exist_ok=True)
    cum.to_csv(OUT / "CPIN_segments_ytd.csv", index=False)
    q = standalone(cum)
    q.to_csv(OUT / "CPIN_segments_quarterly.csv", float_format="%.4f")
    pd.set_option("display.width", 250)
    print(cum[["period", "basis", "sales_consolidated", "result_consolidated", "chk_sales", "chk_result", "vintage"]].to_string())
    print(q[["basis", "sales_broiler", "result_broiler", "margin_broiler", "margin_feed", "margin_doc", "margin_consolidated"]].round(3).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
