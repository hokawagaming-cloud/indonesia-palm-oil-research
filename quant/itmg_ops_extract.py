"""Phase XIII: ITMG C2/C3 data layer.
(1) Deck operating fields per quarter (first-reported, page provenance): sales Mt, production Mt,
    next-quarter production target Mt (management guidance printed in the deck of quarter q for q+1),
    FY sales target (range midpoint).
(2) FS cost-of-revenue lines (USD thousands, YTD) -> standalone quarters: mining costs, royalty,
    coal purchases, coal transportation, fuel and oil, salaries, inventory change, total cost of revenue;
    plus net revenue. Q4 = FY (12M) - 9M.
Outputs: ITMG_ops_extract.csv, ITMG_fs_costs.csv, ITMG_c2c3_coverage.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "coal" / "ITMG"
OUT = ROOT / "data" / "reference" / "research"
QS = [f"{q}Q{yy}" for yy in range(18, 27) for q in (1, 2, 3, 4) if not (yy == 26 and q == 4)]
V = r"(\d{1,2}[.,]\d)"


def deck(q: str) -> list[str]:
    return [" ".join(p.get_text().split()) for p in pymupdf.open(RAW / f"ITM_Analyst_Presentation_{q}.pdf")]


def nxt(q: str) -> str:
    n, yy = int(q[0]), int(q[2:])
    return f"{n % 4 + 1}Q{yy + (n == 4):02d}"


def grab(P, pats):
    for pat in pats:
        for i, t in enumerate(P):
            m = re.search(pat, t, re.I)
            if m:
                return float(m.group(1).replace(",", ".")), i + 1, pat[:40]
    return np.nan, None, None


def ops(q: str) -> dict:
    P = deck(q); nq = nxt(q)
    r = {"quarter": q}
    r["sales_mt"], r["sales_pg"], r["sales_pat"] = grab(P, [
        rf"Total {q} sales {V} ?Mt", rf"{V} ?Mt Sales\b", rf"Sales volume \(Mt\)\s+[\d.]+\s+[\d.]+\s+{V}",
        rf"{q} (?:coal )?sales (?:volume )?(?:of|was|reached|at|recorded at) {V} ?Mt", rf"{V} ?Mt sales {q}",
        rf"{q} sales volume (?:of|was|at|reached) {V}"])
    r["prod_mt"], r["prod_pg"], r["prod_pat"] = grab(P, [
        rf"{V} ?Mt Production\b", rf"Production {V} ?Mt", rf"{q} (?:total )?(?:production|output)[^.]{{0,60}}? (?:at|of|reached|was) {V} ?Mt",
        rf"{q} production (?:was|is|reached|achieved)[^.]{{0,40}}? {V} ?Mt"])
    r["next_target_mt"], r["tgt_pg"], r["tgt_pat"] = grab(P, [
        rf"{nq} Target: {V} ?Mt", rf"{nq}:? {V} ?Mt", rf"{nq} production target (?:is |will be )?(?:expected |set )?(?:at|to be|of) {V}",
        rf"{nq}e? (?:total )?(?:production|output) target (?:is |will be )?(?:expected )?(?:at|of) {V}"])
    # Sales guidance printed in this deck (used for the NEXT quarter's forecast; PIT: deck q is public before q+1 ends).
    # Types: FY (year), H1 (6M of year), Q (a specific quarter). Range -> midpoint.
    R = r"(\d{1,2}[.,]\d)(?: ?[–-] ?(\d{1,2}[.,]\d))? ?Mt"
    pats = [("FY", rf"(?:TARGET SALES|Target sales) (20\d{{2}}): {R}", lambda g: int(g[0])),
            ("FY", rf"FY(\d{{2}}) (?:coal )?sales target:? ?{R}", lambda g: 2000 + int(g[0])),
            ("Q", rf"([1-4])Q(\d{{2}}) sales target:? ?{R}", None),
            ("H1", rf"6M(\d{{2}}) sales target:? ?{R}", lambda g: 2000 + int(g[0]))]
    for i, t in enumerate(P):
        for typ, pat, yr in pats:
            m = re.search(pat, t, re.I)
            if m:
                g = m.groups()
                if typ == "Q":
                    r["guid_type"], r["guid_year"], r["guid_quarter"] = "Q", 2000 + int(g[1]), int(g[0]); vals = g[2:]
                else:
                    r["guid_type"], r["guid_year"] = typ, yr(g); vals = g[1:]
                v = [float(x.replace(",", ".")) for x in vals if x]
                r["guid_value_mt"] = float(np.mean(v)); r["guid_pg"] = i + 1
                break
        if "guid_type" in r:
            break
    r["fy_sales_target_mt"] = r.get("guid_value_mt") if r.get("guid_type") == "FY" else np.nan
    return r


LINES = {"mining": r"Biaya penambangan", "royalty": r"Royalti(?:/iuran eksploitasi)?", "coal_purchase": r"Pembelian batubara",
         "transport": r"Transportasi batubara", "fuel": r"Bahan bakar(?: dan minyak)?", "salaries": r"Gaji dan tunjangan",
         "cost_of_revenue": r"Beban pokok pendapatan"}


def fs_costs(path: Path) -> dict:
    d = pymupdf.open(path)
    for p in d:
        t = " ".join(p.get_text().split())
        if re.search(r"BEBAN POKOK PENDAPATAN \d*\.?\s*COST OF REVENUE|24\. BEBAN POKOK PENDAPATAN|25\. BEBAN POKOK PENDAPATAN|26\. BEBAN POKOK PENDAPATAN", t):
            i = re.search(r"\d{2}\. BEBAN POKOK PENDAPATAN", t).start()
            s = t[i:i + 3000]
            out = {}
            for k, pat in LINES.items():
                m = re.search(pat + r"\s+(\(?[\d,]+\)?)", s)
                if k == "cost_of_revenue":
                    m = re.search(r"Beban pokok pendapatan\s+(\(?[\d,]+\)?)\s+\(?[\d,]+\)?\s+Cost of revenue", s)
                out[k] = float(m.group(1).strip("()").replace(",", "")) if m else np.nan
            out["coal_revenue"] = np.nan
            for p2 in d:
                t2 = " ".join(p2.get_text().split())
                m2 = re.search(r"\d{2}\. PENDAPATAN BERSIH \d{2}\. NET REVENUE.{0,80}?Batubara Coal - Pihak ketiga ([\d,]+) [\d,]+ Third parties - - Pihak berelasi ([\d,]+)", t2)
                if m2:
                    out["coal_revenue"] = float(m2.group(1).replace(",", "")) + float(m2.group(2).replace(",", "")); break
            return out
    return {}


def main() -> int:
    O = pd.DataFrame([ops(q) for q in QS]); O["period"] = [f"20{q[-2:]}Q{q[0]}" for q in O.quarter]
    man = pd.read_csv(OUT / "ITMG_document_manifest.csv")
    fs = man[(man.kind == "fs") & man.file.notna()]
    rows = []
    for r in fs.itertuples():
        rows.append({"period": r.period, **fs_costs(Path(r.file))})
    C = pd.DataFrame(rows).sort_values("period").set_index("period")
    # YTD -> standalone
    S = C.copy()
    for p in C.index:
        q = pd.Period(p, "Q")
        if q.quarter > 1:
            prev = str(q - 1)
            S.loc[p] = C.loc[p] - C.loc[prev] if prev in C.index else np.nan
    S = S.add_suffix("_q")
    F = C.add_suffix("_ytd").join(S)
    # implied sales volume = coal revenue (USD k, standalone) / first-reported ASP (USD/t) -> Mt
    E = pd.read_csv(OUT / "ITMG_quarterly_raw_extract.csv").set_index("period")
    F["asp_first"] = E.asp_usd_t.reindex(F.index)
    F["implied_sales_mt"] = F["coal_revenue_q"] / F["asp_first"] / 1000
    rec = O.set_index("period")[["sales_mt"]].join(F[["implied_sales_mt"]]).dropna()
    cov_rec = {"n": len(rec), "median_abs_pct_gap": float(((rec.implied_sales_mt / rec.sales_mt) - 1).abs().median()),
               "max_abs_pct_gap": float(((rec.implied_sales_mt / rec.sales_mt) - 1).abs().max())}
    print("reconciliation deck sales vs implied:", rec.round(2).to_dict("index"), cov_rec)
    O.to_csv(OUT / "ITMG_ops_extract.csv", index=False)
    F.to_csv(OUT / "ITMG_fs_costs.csv")
    cov = {"implied_volume_reconciliation": cov_rec, "implied_sales_mt_quarters": int(F.implied_sales_mt.notna().sum()), "quarters": len(QS), "sales_mt": int(O.sales_mt.notna().sum()), "prod_mt": int(O.prod_mt.notna().sum()),
           "next_target_mt": int(O.next_target_mt.notna().sum()), "fy_sales_target_mt": int(O.fy_sales_target_mt.notna().sum()),
           "fs_quarters_standalone": {k: int(S[k + "_q"].notna().sum()) for k in LINES}}
    (OUT / "ITMG_c2c3_coverage.json").write_text(json.dumps(cov, indent=1), encoding="utf-8")
    pd.set_option("display.width", 250)
    print(O[["period", "sales_mt", "sales_pg", "prod_mt", "prod_pg", "next_target_mt", "tgt_pg", "fy_sales_target_mt"]].to_string())
    print(F[[c for c in F.columns if c.endswith("_q")]].round(0).to_string()); print(json.dumps(cov, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
