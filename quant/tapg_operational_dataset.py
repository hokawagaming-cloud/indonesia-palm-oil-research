"""TAPG operational, cost and JV dataset, transcribed from the annual reports with
page citations, followed by internal consistency checks.

Values were read from the per-page text in data/processed/text/TAPG (quant/pdf_to_text.py)
and are entered exactly as printed: Indonesian format converted, no rounding, no
estimates. Each record carries the document and PDF page. The printed folio is looked up
automatically from the page text.

Scope warning: operational volumes and areas are reported "including associate
companies" (the company's wording, which covers the 50% JV PT Union Sampoerna Triputra
Persada and others). Sales volumes, ASP and the financial statements are consolidated
(subsidiaries only). Do not divide one by the other without adjusting for scope.

Outputs: data/reference/TAPG_operational_extracted.csv
         data/reference/TAPG_operational_checks.csv
Usage:   python -I quant/tapg_operational_dataset.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "data" / "processed" / "text" / "TAPG"
REF = ROOT / "data" / "reference"

DOC = {  # pdf -> (text stem, publication-date anchor, basis)
    "AR 2021.pdf": ("AR_2021", "2022-04-26", "PDF creation date (AR)"),
    "AR_2022.pdf": ("AR_2022", "2023-03-31", "PDF creation date (AR)"),
    "AR_2023.pdf": ("AR_2023", "2024-03-28", "PDF creation date (AR)"),
    "AR_2024.pdf": ("AR_2024", "2025-04-09", "PDF creation date (AR)"),
    "TAPG_-_AR_2025.pdf": ("TAPG_-_AR_2025", "2026-04-21", "PDF creation date (AR)"),
}
INC = "incl. associates (company definition)"
CONS = "consolidated"

R = []  # (item, period_end_year, value, unit, scope, doc, pdf_page, note)


def add(item, year, value, unit, scope, doc, page, note=""):
    R.append((item, year, value, unit, scope, doc, page, note))


# --- Palm tree age profile, year-end, hectares (nucleus only | nucleus + plasma) ------
AGE = {
    2021: ("AR 2021.pdf", 93, [(7791, 10950), (8171, 10652), (113221, 125341), (8551, 13200), (137734, 160143)], ""),
    2022: ("AR_2022.pdf", 100, [(8100, 11200), (4100, 6600), (118000, 131100), (8200, 12500), (138400, 161400)],
           "AR2022 prints this table rounded to the nearest 100 ha"),
    2023: ("AR_2023.pdf", 96, [(7164, 10263), (3880, 6590), (118186, 132063), (7155, 11628), (136385, 160544)], ""),
    2024: ("AR_2024.pdf", 96, [(7416, 10649), (4375, 6942), (117008, 131939), (6796, 11268), (135594, 160798)], ""),
    2025: ("TAPG_-_AR_2025.pdf", 100, [(7613, 11059), (4853, 7059), (115804, 132054), (4544, 9535), (132814, 159707)], ""),
}
BANDS = ["age_0_3", "age_4_6", "age_7_20", "age_gt20", "age_total"]
for y, (doc, p, vals, note) in AGE.items():
    for band, (nuc, tot) in zip(BANDS, vals):
        add(f"{band}_ha_nucleus", y, nuc, "ha", INC, doc, p, note)
        add(f"{band}_ha_nucleus_plasma", y, tot, "ha", INC, doc, p, note)

# --- Nucleus mature / immature area by region, year-end, ha --------------------------
REG = {
    2021: ("AR 2021.pdf", 93, {"sumatra": (3434, 2506), "central_kalimantan": (77916, 4139), "east_kalimantan": (48593, 1146), "total": (129943, 7791)}, ""),
    2022: ("AR_2022.pdf", 100, {"sumatra": (2300, 3500), "central_kalimantan": (78800, 4000), "east_kalimantan": (49200, 600), "total": (130300, 8100)}, "rounded to nearest 100 ha"),
    2023: ("AR_2023.pdf", 96, {"sumatra": (2123, 3392), "central_kalimantan": (77619, 3639), "east_kalimantan": (49479, 133), "total": (129221, 7164)}, ""),
    2024: ("AR_2024.pdf", 97, {"sumatra": (2506, 3072), "central_kalimantan": (76288, 4280), "east_kalimantan": (49384, 64), "total": (128178, 7416)}, ""),
    2025: ("TAPG_-_AR_2025.pdf", 100, {"sumatra": (3204, 2172), "central_kalimantan": (73927, 5128), "east_kalimantan": (48070, 313), "total": (125201, 7613)}, ""),
}
for y, (doc, p, d, note) in REG.items():
    for reg, (m, im) in d.items():
        add(f"mature_ha_nucleus_{reg}", y, m, "ha", INC, doc, p, note)
        add(f"immature_ha_nucleus_{reg}", y, im, "ha", INC, doc, p, note)

# --- FFB processed by source, thousand tonnes ----------------------------------------
for y, vals in {2025: (3031, 400, 659, 4089), 2024: (2957, 326, 679, 3962), 2023: (3058, 325, 820, 4203)}.items():
    for k, v in zip(["nucleus", "plasma", "third_party", "total"], vals):
        add(f"ffb_processed_{k}_kt", y, v, "thousand t", INC, "TAPG_-_AR_2025.pdf", 100)
for k, v in zip(["nucleus", "plasma", "third_party"], (3199, 325, 892)):
    add(f"ffb_processed_{k}_kt", 2022, v, "thousand t", INC, "AR_2024.pdf", 97)

# --- Average selling price (IDR/kg) and sales volume, consolidated -------------------
ASP = [
    # (year, product, asp, doc, page)
    (2021, "cpo", 9274, "AR 2021.pdf", 97), (2020, "cpo", 8298, "AR 2021.pdf", 97),
    (2021, "pk", 7236, "AR 2021.pdf", 97), (2020, "pk", 4424, "AR 2021.pdf", 97),
    (2021, "ffb", 2171, "AR 2021.pdf", 97), (2020, "ffb", 1618, "AR 2021.pdf", 97),
    (2021, "rubber_slab", 20466, "AR 2021.pdf", 97), (2020, "rubber_slab", 15690, "AR 2021.pdf", 97),
    (2021, "rubber_rss", 25259, "AR 2021.pdf", 97), (2020, "rubber_rss", 21948, "AR 2021.pdf", 97),
    (2022, "cpo", 12211, "AR_2022.pdf", 104), (2022, "pk", 8209, "AR_2022.pdf", 104),
    (2022, "ffb", 3202, "AR_2022.pdf", 104), (2022, "rubber_slab", 20969, "AR_2022.pdf", 104),
    (2022, "rubber_rss", 24037, "AR_2022.pdf", 104),
    (2023, "cpo", 11115, "AR_2023.pdf", 100), (2023, "pk", 5392, "AR_2023.pdf", 100),
    (2023, "rubber_slab", 19103, "AR_2023.pdf", 100), (2023, "rubber_rss", 22287, "AR_2023.pdf", 100),
    (2023, "pko", 10985, "AR_2024.pdf", 101),
    (2024, "cpo", 13156, "AR_2024.pdf", 101), (2024, "pk", 7891, "AR_2024.pdf", 101),
    (2024, "pko", 19101, "AR_2024.pdf", 101), (2024, "rubber_slab", 25111, "AR_2024.pdf", 101),
    (2024, "rubber_rss", 32528, "AR_2024.pdf", 101),
    (2025, "cpo", 14220, "TAPG_-_AR_2025.pdf", 104), (2025, "pk", 11967, "TAPG_-_AR_2025.pdf", 104),
    (2025, "pko", 26212, "TAPG_-_AR_2025.pdf", 104), (2025, "rubber_slab", 27713, "TAPG_-_AR_2025.pdf", 104),
    (2025, "rubber_rss", 33117, "TAPG_-_AR_2025.pdf", 104),
]
for y, prod, v, doc, p in ASP:
    add(f"asp_{prod}_idr_per_kg", y, v, "IDR/kg", CONS, doc, p)

VOL = [
    # (year, product, tonnes, doc, page, note)
    (2021, "cpo", 578000, "AR 2021.pdf", 97, "printed as 578 thousand t"),
    (2020, "cpo", 567000, "AR 2021.pdf", 97, "printed as 567 thousand t"),
    (2021, "pk", 113000, "AR 2021.pdf", 97, "printed as 113 thousand t"),
    (2020, "pk", 112000, "AR 2021.pdf", 97, "printed as 112 thousand t"),
    (2021, "ffb", 34700, "AR 2021.pdf", 97, "printed as 34.7 thousand t"),
    (2022, "cpo", 666000, "AR_2022.pdf", 104, "printed as 666 thousand t"),
    (2022, "pk", 141000, "AR_2022.pdf", 104, "printed as 141 thousand t; AR2023 p100 prints 142"),
    (2022, "ffb", 6500, "AR_2022.pdf", 104, "printed as 6.5 thousand t"),
    (2023, "cpo", 676987, "AR_2024.pdf", 101, "table header says 'thousand tons' but values are tonnes"),
    (2023, "pk", 129589, "AR_2024.pdf", 101, "as above"),
    (2023, "pko", 6300, "AR_2024.pdf", 101, "as above"),
    (2024, "cpo", 636021, "TAPG_-_AR_2025.pdf", 104, ""), (2024, "pk", 110558, "TAPG_-_AR_2025.pdf", 104, ""),
    (2024, "pko", 19500, "TAPG_-_AR_2025.pdf", 104, ""),
    (2025, "cpo", 658917, "TAPG_-_AR_2025.pdf", 104, ""), (2025, "pk", 113364, "TAPG_-_AR_2025.pdf", 104, ""),
    (2025, "pko", 22399, "TAPG_-_AR_2025.pdf", 104, ""),
]
for y, prod, v, doc, p, note in VOL:
    add(f"sales_volume_{prod}_t", y, v, "t", CONS, doc, p, note)

# --- Segment revenue, IDR mn (AR2025 p101) -------------------------------------------
for item, v25, v24 in [("seg_rev_palm_total", 11378649, 9640778), ("seg_rev_cpo", 9369969, 8367543),
                       ("seg_rev_pk", 1356630, 872463), ("seg_rev_pko", 587121, 372478),
                       ("seg_rev_pkm", 28777, 27508), ("seg_rev_ffb", 36151, 786),
                       ("seg_op_profit_palm", 3637063, 3036382), ("seg_rev_rubber", 23549, 30685)]:
    add(item, 2025, v25, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 101)
    add(item, 2024, v24, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 101)

# --- Cost of sales breakdown (palm products), IDR mn ---------------------------------
COGS = [
    (2025, 4439387, 731697, 870294, 683230, "TAPG_-_AR_2025.pdf", 337),
    (2024, 3842031, 689826, 742111, 650363, "TAPG_-_AR_2025.pdf", 337),
    (2023, 3946612, 693806, 710428, 619611, "AR_2023.pdf", 325),
    (2022, 3876917, 628117, 583232, 547902, "AR_2023.pdf", 325),
]
for y, mat, lab, ovh, dep, doc, p in COGS:
    add("cogs_palm_materials_processing", y, mat, "IDR mn", CONS, doc, p, "raw & supporting materials incl. purchased FFB and processing; not split further")
    add("cogs_palm_direct_labour", y, lab, "IDR mn", CONS, doc, p)
    add("cogs_palm_overhead", y, ovh, "IDR mn", CONS, doc, p)
    add("cogs_palm_depreciation", y, dep, "IDR mn", CONS, doc, p)
add("cogs_palm_production_cost", 2025, 6724608, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 337)
add("cogs_palm_production_cost", 2024, 5924331, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 337)
add("cogs_palm_total", 2025, 6876533, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 337)
add("cogs_palm_total", 2024, 5920116, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 337)
add("selling_transport_freight", 2025, 246372, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 337)
add("selling_transport_freight", 2024, 243100, "IDR mn", CONS, "TAPG_-_AR_2025.pdf", 337)

# --- JV: PT Union Sampoerna Triputra Persada (USTP), 50% -----------------------------
USTP = [  # year, share of profit, dividend declared, ending carrying value, doc, page
    (2021, 344792, 147820, 2029680, "AR 2021.pdf", 278),
    (2022, 958570, 148297, 2844061, "AR_2022.pdf", 304),
    (2023, 637054, 296596, 3184656, "AR_2023.pdf", 291),
    (2024, 886734, 1161629, 2914070, "AR_2024.pdf", 291),
    (2025, 1059744, 1359871, 2612294, "TAPG_-_AR_2025.pdf", 304),
]
for y, sp, dv, cv, doc, p in USTP:
    add("ustp_share_of_profit", y, sp, "IDR mn", "50% JV, equity method", doc, p)
    add("ustp_dividend_declared", y, dv, "IDR mn", "50% JV, equity method", doc, p, "dividend in the JV roll-forward (declared); cash received is in the cash flow statement")
    add("ustp_carrying_value", y, cv, "IDR mn", "50% JV, equity method", doc, p)
add("all_jv_share_of_profit", 2025, 1070205, "IDR mn", "JVs, equity method", "TAPG_-_AR_2025.pdf", 304)
add("all_jv_dividend_declared", 2025, 1373042, "IDR mn", "JVs, equity method", "TAPG_-_AR_2025.pdf", 304)
add("all_jv_carrying_value", 2025, 2640217, "IDR mn", "JVs, equity method", "TAPG_-_AR_2025.pdf", 304)


def folio(stem: str, page: int) -> str:
    cur, lines = 0, []
    for ln in open(TXT / f"{stem}.txt", encoding="utf-8"):
        m = re.match(r"=== PAGE (\d+) ===", ln)
        if m:
            if cur == page:
                break
            cur, lines = int(m.group(1)), []
            continue
        if cur == page and ln.strip():
            lines.append(ln.strip())
    for s in lines[::-1]:
        if re.fullmatch(r"\d{1,3}", s):
            return s
    return ""


def main() -> int:
    df = pd.DataFrame(R, columns=["item", "fiscal_year", "value", "unit", "scope", "source_doc", "pdf_page", "note"])
    df["period"] = "FY" + df["fiscal_year"].astype(str)
    df["printed_page"] = [folio(DOC[d][0], p) for d, p in zip(df.source_doc, df.pdf_page)]
    df["publication_date_proxy"] = df.source_doc.map(lambda d: DOC[d][1])
    df["publication_date_basis"] = df.source_doc.map(lambda d: DOC[d][2])
    df.to_csv(REF / "TAPG_operational_extracted.csv", index=False)

    v = df.set_index(["item", "fiscal_year"])["value"]
    g = lambda i, y: v.get((i, y), float("nan"))
    checks = []

    def chk(name, y, lhs, rhs, tol):
        if pd.notna(lhs) and pd.notna(rhs):
            checks.append({"check": name, "fiscal_year": y, "lhs": lhs, "rhs": rhs,
                           "result": "PASS" if abs(lhs - rhs) <= tol else "FAIL"})

    for y in range(2020, 2026):
        for s in ("nucleus", "nucleus_plasma"):
            tol = 300 if y == 2022 else 2
            chk(f"age bands sum to total ({s})", y, sum(g(f"{b}_ha_{s}", y) for b in BANDS[:4]), g(f"age_total_ha_{s}", y), tol)
        chk("regions sum to total (mature)", y, sum(g(f"mature_ha_nucleus_{r}", y) for r in ("sumatra", "central_kalimantan", "east_kalimantan")), g("mature_ha_nucleus_total", y), 2)
        chk("regions sum to total (immature)", y, sum(g(f"immature_ha_nucleus_{r}", y) for r in ("sumatra", "central_kalimantan", "east_kalimantan")), g("immature_ha_nucleus_total", y), 2)
        chk("immature nucleus = age 0-3 nucleus", y, g("immature_ha_nucleus_total", y), g("age_0_3_ha_nucleus", y), 2)
        chk("mature + immature = nucleus age total", y, g("mature_ha_nucleus_total", y) + g("immature_ha_nucleus_total", y), g("age_total_ha_nucleus", y), 300 if y == 2022 else 2)
        chk("processed FFB sources sum to total", y, g("ffb_processed_nucleus_kt", y) + g("ffb_processed_plasma_kt", y) + g("ffb_processed_third_party_kt", y), g("ffb_processed_total_kt", y), 2)
        chk("CPO segment revenue = volume x ASP (IDR mn)", y, g("sales_volume_cpo_t", y) * g("asp_cpo_idr_per_kg", y) / 1e3, g("seg_rev_cpo", y), 0.005 * max(1, g("seg_rev_cpo", y)))
        chk("PK segment revenue = volume x ASP (IDR mn)", y, g("sales_volume_pk_t", y) * g("asp_pk_idr_per_kg", y) / 1e3, g("seg_rev_pk", y), 0.005 * max(1, g("seg_rev_pk", y)))
        chk("PKO segment revenue = volume x ASP (IDR mn)", y, g("sales_volume_pko_t", y) * g("asp_pko_idr_per_kg", y) / 1e3, g("seg_rev_pko", y), 0.005 * max(1, g("seg_rev_pko", y)))
        chk("COGS components = production cost", y, sum(g(i, y) for i in ("cogs_palm_materials_processing", "cogs_palm_direct_labour", "cogs_palm_overhead", "cogs_palm_depreciation")), g("cogs_palm_production_cost", y), 2)
    # JV roll-forward continuity is checked against the statements file
    st = pd.read_csv(REF / "TAPG_statements_extracted.csv")
    st = st[st.status == "extracted"].drop_duplicates(["item", "period"], keep="last").set_index(["item", "period"])["value"]
    for y in range(2021, 2026):
        tot = st.get(("share_of_profit_jv_associates", f"FY{y}"))
        if tot is not None:
            chk("USTP share <= total JV & associate share", y, g("ustp_share_of_profit", y), tot, 10**12)
            checks[-1]["result"] = "PASS" if g("ustp_share_of_profit", y) <= tot + 1 else "FAIL"
            checks[-1]["detail"] = f"USTP {g('ustp_share_of_profit', y)/tot:.1%} of reported total"
        rec = st.get(("dividends_received_jv", f"FY{y}"))
        if rec is not None:
            checks.append({"check": "USTP dividend declared vs JV dividends received in cash", "fiscal_year": y,
                           "lhs": g("ustp_dividend_declared", y), "rhs": rec,
                           "result": "INFO", "detail": f"declared minus received = {g('ustp_dividend_declared', y) - rec:,.0f} (timing / receivable)"})
    c = pd.DataFrame(checks)
    c.to_csv(REF / "TAPG_operational_checks.csv", index=False)
    print(c.to_string(index=False))
    print(f"\n{len(df)} data points; {df.printed_page.eq('').sum()} without printed folio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
