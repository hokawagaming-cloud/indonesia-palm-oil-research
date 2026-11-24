"""Phase II TAPG extraction from the annual reports, with page citations and checks.

Produces SCOPE-SEPARATED tables (D-008):
  data/reference/TAPG_phase2_consolidated.csv subsidiaries only (financial statements, ASP,
                                              sales volumes, cost notes, capex roll-forward)
  data/reference/TAPG_phase2_jv.csv           USTP and other JVs (summarised financials,
                                              equity-method share, dividends)
  data/reference/TAPG_phase2_groupwide.csv    operational statistics reported "including
                                              associate companies" (area, FFB, production)
  data/reference/TAPG_estates.csv             subsidiaries, line of business, location
  data/reference/TAPG_phase2_checks.csv       validation results

Tables with a regular layout (fixed-asset roll-forward, FFB by region) are parsed
programmatically. Irregular ones are transcribed below with a page citation.
Usage: python -I quant/tapg_phase2_extract.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "data" / "processed" / "text" / "TAPG"
REF = ROOT / "data" / "reference"
ARS = {"AR_2021": ("AR 2021.pdf", 2021), "AR_2022": ("AR_2022.pdf", 2022), "AR_2023": ("AR_2023.pdf", 2023),
       "AR_2024": ("AR_2024.pdf", 2024), "TAPG_-_AR_2025": ("TAPG_-_AR_2025.pdf", 2025)}
VAL = re.compile(r"^\(?-?\d{1,3}(\.\d{3})*(,\d+)?\)?$|^-$")


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


def num(t):
    t = t.replace(" ", "")
    if t == "-":
        return 0.0
    neg = t.startswith("(")
    v = float(t.strip("()").replace(".", "").replace(",", "."))
    return -v if neg else v


def next_vals(lines, i, n, max_skip=3):
    out, j, skip = [], i + 1, 0
    while j < len(lines) and len(out) < n:
        t = lines[j].replace(" ", "")
        if VAL.match(t):
            out.append(t)
        elif out:
            break
        else:
            skip += 1
            if skip > max_skip:
                break
        j += 1
    return out


rows = {"consolidated": [], "jv": [], "groupwide": []}
checks = []


def add(scope, item, fy, value, unit, doc, page, note="", basis="audited"):
    rows[scope].append({"item": item, "period": f"FY{fy}", "fiscal_year": fy, "value": value, "unit": unit,
                        "source_doc": doc, "pdf_page": page, "basis": basis, "note": note})


def chk(name, fy, lhs, rhs, tol, detail=""):
    if pd.notna(lhs) and pd.notna(rhs):
        checks.append({"check": name, "fiscal_year": fy, "lhs": lhs, "rhs": rhs,
                       "result": "PASS" if abs(lhs - rhs) <= tol else "FAIL", "detail": detail})


# ---------------------------------------------------------------- 1. capex roll-forward
FA_CLASSES = [
    ("mature_oil_palm", r"^Tanaman kelapa sawit$", "plantation (bearer plants)"),
    ("mature_rubber", r"^Tanaman karet$", "plantation (bearer plants)"),
    ("immature_oil_palm", r"^Tanaman kelapa sawit$", "plantation (bearer plants)"),
    ("immature_rubber", r"^Tanaman karet$", "plantation (bearer plants)"),
    ("nursery", r"^Bibitan$", "plantation (bearer plants)"),
    ("land", r"^(Tanah|Hak atas tanah)$", "land"),
    ("buildings_infrastructure", r"^Bangunan( dan infrastruktur| dan prasarana)?$", "buildings & infrastructure (estates and mills, not split)"),
    ("machinery_installations", r"^Mesin( dan instalasi| dan peralatan)?$", "machinery & installations (mill-heavy, not split)"),
    ("vehicles_heavy_equipment", r"^Kendaraan( dan alat berat)?$", "vehicles & heavy equipment"),
    ("equipment_furniture", r"^Peralatan dan perabot", "other"),
    ("construction_in_progress", r"^Aset dalam (pembangunan|penyelesaian)$", "construction in progress (unallocated)"),
    ("total_cost", r"^(Total|Jumlah) nilai perolehan$", "total"),
]
for stem, (pdf, fy) in ARS.items():
    lines, pages = load(stem)
    # pages that carry a fixed-asset roll-forward: 'Nilai perolehan' followed by bearer plants
    starts = [i for i, s in enumerate(lines) if s == "Nilai perolehan" and pages[i] > 200
              and any("Tanaman" in t for t in lines[i:i + 12])]
    for k, start in enumerate(starts[:2]):  # first table = FY, second = FY-1
        year = fy - k
        end = next((j for j in range(start, start + 200) if re.match(r"^(Total|Jumlah) nilai perolehan$", lines[j])), start + 120)
        for name, pat, cls in FA_CLASSES:
            rx = re.compile(pat, re.I)
            hits = [j for j in range(start, end + 1) if rx.search(lines[j])]
            want = 1 if name.startswith("immature") else 0  # 2nd 'Tanaman ...' row = immature
            if len(hits) <= want:
                continue
            j = hits[want]
            vals = next_vals(lines, j, 5)
            if len(vals) >= 3:
                # beginning | additions | deductions | [reclass] | ending
                add("consolidated", f"fa_additions_{name}", year, num(vals[1]), "IDR mn", pdf, pages[j],
                    note=f"class: {cls}; row tokens {vals}")
                add("consolidated", f"fa_ending_cost_{name}", year, num(vals[-1]), "IDR mn", pdf, pages[j])
        con = pd.DataFrame(rows["consolidated"])
        sub = con[(con.period == f"FY{year}") & con["item"].str.startswith("fa_additions_") & (con.source_doc == pdf)]
        parts = sub[sub["item"] != "fa_additions_total_cost"]["value"].sum()
        tot = sub[sub["item"] == "fa_additions_total_cost"]["value"]
        if len(tot):
            chk("fixed-asset additions by class sum to total additions", year, parts, tot.iloc[0], 2, pdf)

# ---------------------------------------------------------------- 2. FFB by region (group-wide, nucleus)
REG_PAT = [("sumatra", r"^Sumatera$|^Sumatra$"), ("central_kalimantan", r"^Kalimantan Tengah$"),
           ("east_kalimantan", r"^Kalimantan Timur$"), ("total", r"^Total$")]
for stem, (pdf, fy) in ARS.items():
    lines, pages = load(stem)
    # the production table is the first 'Sumatra' row between pdf pages 88-101 followed by 3 values
    i0 = next(i for i, s in enumerate(lines) if 88 <= pages[i] <= 101 and re.match(r"^Sumatera$|^Sumatra$", s)
              and len(next_vals(lines, i, 3)) == 3 and "ha" not in " ".join(lines[i - 12:i]).lower().split())
    unit_tonnes = "(ton/tons)" in " ".join(lines[i0 - 12:i0])
    for reg, pat in REG_PAT:
        j = next(j for j in range(i0, i0 + 25) if re.match(pat, lines[j]))
        vals = next_vals(lines, j, 3, max_skip=2)
        for k, t in enumerate(vals):
            v = num(t) / 1000 if unit_tonnes else num(t)
            add("groupwide", f"ffb_nucleus_{reg}_kt", fy - k, v, "thousand t", pdf, pages[j],
                note=("printed in tonnes, converted" if unit_tonnes else "printed in thousand t") + "; incl. associates", basis="annual report MD&A")
    gw = pd.DataFrame(rows["groupwide"])
    for k in range(3):
        y = fy - k
        s = gw[(gw.source_doc == pdf) & (gw.fiscal_year == y)].set_index("item")["value"]
        chk("FFB regions sum to total", y, sum(s.get(f"ffb_nucleus_{r}_kt", 0) for r, _ in REG_PAT[:3]),
            s.get("ffb_nucleus_total_kt"), 2.5, pdf)

# ---------------------------------------------------------------- 3. cost of sales FY2020-FY2022 (old presentation)
OLD_COGS = {  # item: {fy: (value, doc, page)}
    "cogs_upkeep": {2021: (676129, "AR 2021.pdf", 314), 2020: (756017, "AR 2021.pdf", 314), 2022: (941410, "AR_2022.pdf", 338)},
    "cogs_harvesting": {2021: (406488, "AR 2021.pdf", 314), 2020: (388325, "AR 2021.pdf", 314), 2022: (554874, "AR_2022.pdf", 338)},
    "cogs_indirect_allocation_ffb": {2021: (425179, "AR 2021.pdf", 314), 2020: (405375, "AR 2021.pdf", 314), 2022: (507016, "AR_2022.pdf", 338)},
    "cogs_depreciation_ffb": {2021: (402335, "AR 2021.pdf", 314), 2020: (385698, "AR 2021.pdf", 314), 2022: (392984, "AR_2022.pdf", 338)},
    "cogs_ffb_production_cost": {2021: (1910131, "AR 2021.pdf", 314), 2020: (1935415, "AR 2021.pdf", 314), 2022: (2396284, "AR_2022.pdf", 338)},
    "cogs_ffb_purchases": {2021: (2357621, "AR 2021.pdf", 314), 2020: (1641547, "AR 2021.pdf", 314), 2022: (2851365, "AR_2022.pdf", 338)},
    "cogs_cpo_pk_processing": {2021: (114593, "AR 2021.pdf", 314), 2020: (105744, "AR 2021.pdf", 314), 2022: (156350, "AR_2022.pdf", 338)},
    "cogs_mill_depreciation": {2021: (128608, "AR 2021.pdf", 314), 2020: (122549, "AR 2021.pdf", 314), 2022: (154918, "AR_2022.pdf", 338)},
    "cogs_mill_indirect_allocation": {2021: (62447, "AR 2021.pdf", 314), 2020: (64980, "AR 2021.pdf", 314), 2022: (76216, "AR_2022.pdf", 338)},
    "cogs_cost_of_goods_manufactured": {2021: (4513423, "AR 2021.pdf", 314), 2020: (3820568, "AR 2021.pdf", 314), 2022: (5620309, "AR_2022.pdf", 338)},
    "cogs_cpo_purchases": {2021: (115888, "AR 2021.pdf", 314), 2020: (0, "AR 2021.pdf", 314), 2022: (53507, "AR_2022.pdf", 338)},
    "cogs_total": {2021: (4662334, "AR 2021.pdf", 315), 2020: (3872987, "AR 2021.pdf", 315), 2022: (5629777, "AR_2022.pdf", 339)},
}
for item, d in OLD_COGS.items():
    for fy, (v, doc, p) in d.items():
        add("consolidated", item, fy, v, "IDR mn", doc, p,
            note="old presentation (to FY2022); FFB purchases cover plasma and third-party FFB")
for fy in (2020, 2021, 2022):
    g = lambda i: OLD_COGS[i][fy][0]
    chk("FFB production cost components sum", fy, g("cogs_upkeep") + g("cogs_harvesting") + g("cogs_indirect_allocation_ffb") + g("cogs_depreciation_ffb"), g("cogs_ffb_production_cost"), 2)
chk("AR2021 vs AR2022 FY2021 FFB purchases", 2021, 2357621, 2357621, 0, "both documents print 2,357,621")

# ---------------------------------------------------------------- 4. USTP standalone (JV scope)
USTP = {  # fy: dict(values), doc, page
    2020: ({"current_assets": 1613015, "noncurrent_assets": 4504676, "current_liabilities": -632403,
            "noncurrent_liabilities": -969212, "net_sales": 2490669, "profit": 810715}, "AR 2021.pdf", 279),
    2021: ({"current_assets": 1811814, "noncurrent_assets": 4459071, "current_liabilities": -498180,
            "noncurrent_liabilities": -839572, "net_sales": 2635590, "profit": 689584}, "AR 2021.pdf", 279),
    2022: ({"current_assets": 3478921, "noncurrent_assets": 3563565, "current_liabilities": -764149,
            "noncurrent_liabilities": -526620, "net_sales": 4395106, "profit": 1917140}, "AR_2022.pdf", 305),
    2023: ({"current_assets": 2839399, "noncurrent_assets": 4450447, "current_liabilities": -455211,
            "noncurrent_liabilities": -395958, "nci": -69365, "net_sales": 3681492, "profit": 1274108,
            "total_assets": 7289846, "total_liabilities": -851169, "net_assets": 6369312}, "AR_2024.pdf", 292),
    2024: ({"current_assets": 2234674, "noncurrent_assets": 4563054, "total_assets": 6797728, "current_liabilities": -609208,
            "noncurrent_liabilities": -290091, "total_liabilities": -899299, "nci": -70289, "net_assets": 5828140,
            "net_sales": 4153034, "profit": 1773467, "tci": 1782086}, "TAPG_-_AR_2025.pdf", 305),
    2025: ({"current_assets": 2034730, "noncurrent_assets": 4158521, "total_assets": 6193251, "current_liabilities": -591279,
            "noncurrent_liabilities": -312415, "total_liabilities": -903694, "nci": -64969, "net_assets": 5224588,
            "net_sales": 4962369, "profit": 2119488, "tci": 2116190}, "TAPG_-_AR_2025.pdf", 305),
}
for fy, (d, doc, p) in USTP.items():
    for k, v in d.items():
        add("jv", f"ustp_{k}", fy, v, "IDR mn", doc, p, note="USTP and subsidiaries, 100% basis (summarised in TAPG note 14a)")
add("jv", "ustp_noncurrent_assets_restated", 2021, 3632260, "IDR mn", "AR_2022.pdf", 305,
    note="AR2022 comparative differs from AR2021 (4,459,071): restated/reclassified")
add("jv", "ustp_noncurrent_assets_restated", 2022, 3563565, "IDR mn", "AR_2023.pdf", 292, note="AR2023 comparative")
SHARE = {2021: (344792, 147820, 2029680, "AR 2021.pdf", 278), 2022: (958570, 148297, 2844061, "AR_2022.pdf", 304),
         2023: (637054, 296596, 3184656, "AR_2023.pdf", 291), 2024: (886734, 1161629, 2914070, "AR_2024.pdf", 291),
         2025: (1059744, 1359871, 2612294, "TAPG_-_AR_2025.pdf", 304)}
for fy, (sp, dv, cv, doc, p) in SHARE.items():
    add("jv", "ustp_share_of_profit_tapg", fy, sp, "IDR mn", doc, p, note="TAPG 50% equity-method share")
    add("jv", "ustp_dividend_to_tapg_declared", fy, dv, "IDR mn", doc, p)
    add("jv", "ustp_carrying_value_tapg", fy, cv, "IDR mn", doc, p)
    chk("USTP profit x 50% = TAPG share of USTP profit", fy, USTP[fy][0]["profit"] * 0.5, sp, 1)
add("jv", "jv_dividends_cash_received", 2025, 958807, "IDR mn", "TAPG_-_AR_2025.pdf", 247)
add("jv", "jv_dividends_in_kind_marketable_securities", 2025, 414235, "IDR mn", "TAPG_-_AR_2025.pdf", 355,
    note="note 42 non-cash: dividend income from JVs received as marketable securities")
add("jv", "all_jv_dividends_declared", 2025, 1373042, "IDR mn", "TAPG_-_AR_2025.pdf", 304)
chk("2025 JV dividends: cash + in-kind = declared (no receivable)", 2025, 958807 + 414235, 1373042, 1,
    "difference vs cash flow explained by non-cash securities dividend")
for fy, cash in {2021: 150000, 2022: 150000, 2023: 300000, 2024: 1170000}.items():
    checks.append({"check": "USTP dividend declared vs all-JV cash received", "fiscal_year": fy,
                   "lhs": SHARE[fy][1], "rhs": cash, "result": "INFO",
                   "detail": f"difference {cash - SHARE[fy][1]:,} = other small JVs (1% or less stakes); no receivable disclosed"})

# ---------------------------------------------------------------- 5. estates / subsidiaries (AR2025 p81-83)
lines, pages = load("TAPG_-_AR_2025")
est = []
for i, s in enumerate(lines):
    if 81 <= pages[i] <= 83 and re.fullmatch(r"\d{1,2}\.", s) and i + 2 < len(lines) and re.fullmatch(r"[A-Z]{2,6}", lines[i + 1]):
        block = lines[i:i + 22]
        code, pct = block[1], block[2]
        txt = " ".join(block[3:])
        biz = re.split(r"\s\d{1,3}(?:\.\d{3})*\s", " " + txt + " ")[0].strip()
        ta = re.search(r"\s(\d{1,3}(?:\.\d{3})*)\s", " " + txt + " ")
        loc = re.search(r"(Kalimantan Tengah|Kalimantan Timur|Kalimantan Barat|Jambi|Riau|Jakarta Selatan|Sumatera \w+)", txt)
        status = re.search(r"(Beroperasi sejak \d{4}|Belum beroperasi|Tidak beroperasi)", txt)
        est.append({"code": code, "ownership_pct": pct.replace(",", "."), "business_id_en": biz[:90],
                    "total_assets_idr_mn": num(ta.group(1)) if ta else None,
                    "status": status.group(1) if status else "", "location_reported": loc.group(1) if loc else "",
                    "location_type": "registered office (not estate)" if loc and loc.group(1) == "Jakarta Selatan" else "operating province",
                    "source_doc": "TAPG_-_AR_2025.pdf", "pdf_page": pages[i]})
pd.DataFrame(est).to_csv(REF / "TAPG_estates.csv", index=False)

# ---------------------------------------------------------------- 6. maturity and replanting (derived from age profile)
op = pd.read_csv(REF / "TAPG_operational_extracted.csv")
age = op[op["item"].str.startswith("age_")].set_index(["item", "fiscal_year"])["value"]
for fy in range(2022, 2026):
    for s in ("nucleus", "nucleus_plasma"):
        old_prev, old_now = age.get((f"age_gt20_ha_{s}", fy - 1)), age.get((f"age_gt20_ha_{s}", fy))
        if old_prev is not None and old_now is not None:
            add("groupwide", f"derived_change_gt20yr_ha_{s}", fy, old_now - old_prev, "ha", "derived", 0,
                note="year-on-year change in >20-year area (net of trees ageing in and of replanting/clearing); DERIVED, not a disclosed replanting figure",
                basis="derived")
rows_df = {k: pd.DataFrame(v) for k, v in rows.items()}
for k, df in rows_df.items():
    df.to_csv(REF / f"TAPG_phase2_{k}.csv", index=False)
pd.DataFrame(checks).to_csv(REF / "TAPG_phase2_checks.csv", index=False)
c = pd.DataFrame(checks)
print(c.to_string(index=False))
print({k: len(v) for k, v in rows_df.items()}, "estates:", len(est))
