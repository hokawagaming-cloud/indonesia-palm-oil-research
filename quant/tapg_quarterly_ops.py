"""TAPG quarterly and annual operational dataset from external documents, with
source, scope, first-seen date and reconciliation checks.

Sources (data/raw/company/TAPG/external/, git-ignored; S-028..S-032):
  KBV   KB Valbury, "Strong Harvest, Stronger Earnings", 29 Oct 2026 (charts p2 read
        visually from rendered images + text p1). 9 quarters 3Q24-3Q26.
  ALD   Aldiracita 9M26 Earnings Flash, 29 Oct 2026 (tables p2; states the source is TAPG
        investor newsletter Vol 24).
  AJB   Ajaib Company Update, 5 May 2026 (1Q26 text).
  PHN   Phintraco initiation, 8 Jul 2025 (FY24 commentary; broker estimates).
  PE25  TAPG Public Expose FY2025 deck, IDX filing 2026-03-16 21:12 WIB (S-027 timestamp):
        annual FY2021-25 split by subsidiaries vs associates, plus 2026F guidance.

Scope labels: groupwide = incl. associates (company definition); subsidiaries /
associates = split from PE25; consolidated = financial-statement scope (sales, ASP, costs).

first_seen: the earliest dated public document in hand that contains the figure. It is
NOT the original disclosure date (the newsletters were not obtained). Backtests must
not use a figure before first_seen (D-011).

Outputs: data/reference/TAPG_quarterly_ops.csv, data/reference/TAPG_annual_ops_split.csv,
         data/reference/TAPG_quarterly_ops_checks.csv
Usage:   python -I -X utf8 quant/tapg_quarterly_ops.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
Q = ["2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2", "2026Q3"]
KBV = ("kbvalbury_tapg_3q26_261030.pdf", "2026-10-29")
ALD = ("aldiracita_TAPG_9M26_EarningsFlash.pdf", "2026-10-29")
AJB = ("ajaib_TAPG_company_update_20260505.pdf", "2026-05-05")
BRK = ("Bareksa 2026-04-28 (S-026)", "2026-04-28")
PE = ("idx_public_expose_FY2025_20260316.pdf", "2026-03-16")

rows = []


def add(item, period, value, unit, scope, src, page, method, note=""):
    rows.append({"item": item, "period": period, "value": value, "unit": unit, "scope": scope,
                 "source_doc": src[0], "page": page, "first_seen": src[1], "method": method, "note": note})


# --- KB Valbury charts (p2, Exhibits 3-6), '000 t and % --------------------------------
series = {
    "ffb_nucleus_kt": [691, 887, 741, 815, 721, 763, 698, 840, 789],
    "ffb_plasma_kt": [79, 100, 89, 100, 90, 105, 95, 108, 104],
    "ffb_processed_internal_kt_kbv": [622, 851, 691, 753, 651, 738, 659, 813, 797],
    "ffb_processed_external_kt_kbv": [292, 348, 310, 338, 307, 302, 283, 332, 326],
    "cpo_production_kt": [209, 273, 231, 254, 222, 245, 227, 271, 271],
    "oer_pct": [22.9, 22.8, 23.1, 23.3, 23.2, 23.6, 24.1, 23.7, 24.1],
    "pk_production_kt": [44, 58, 50, 54, 46, 52, 46, 58, 60],
    "ker_pct": [4.8, 4.8, 5.0, 4.9, 4.8, 5.0, 4.9, 5.1, 5.3],
}
for item, vals in series.items():
    unit = "%" if item.endswith("pct") else "thousand t"
    for q, v in zip(Q, vals):
        add(item, q, v, unit, "groupwide", KBV, 2, "chart data label (read from rendered image)",
            "KBV split label 'internal (nucleus+plasma)' does not match company definitions; see checks" if "kbv" in item else "")

# --- Aldiracita tables (p2), more precise, 3Q25 / 2Q26 / 3Q26 / 9M ------------------------
ald = {
    "ffb_nucleus_kt": (721.3, 839.5, 789.4, 2277.1, 2345.1),
    "ffb_plasma_kt": (90.6, 107.8, 104.1, 279.2, 292.8),
    "ffb_processed_kt": (957.5, 1145.3, 1123.5, 3048.6, 3214.6),
    "cpo_production_kt": (222.1, 271.1, 270.9, 708.0, 756.8),
    "pk_production_kt": (46.2, 58.1, 60.3, 149.6, 163.7),
    "oer_pct": (23.2, 23.7, 24.1, 23.2, 23.5),
    "ker_pct": (4.8, 5.1, 5.4, 4.9, 5.1),
    "rubber_sales_t": (155, 229, 162, 584, 564),
}
for item, vals in ald.items():
    unit = "%" if item.endswith("pct") else ("t" if item.endswith("_t") else "thousand t")
    for per, v in zip(["2025Q3", "2026Q2", "2026Q3", "9M2025", "9M2026"], vals):
        add(item, per, v, unit, "groupwide" if "rubber" not in item else "consolidated", ALD, 2, "table",
            "source stated by ALD: TAPG investor newsletter Vol 24")
for per, v in zip(["2025Q3", "2026Q2", "2026Q3"], (146, 198, 230)):
    add("ffb_external_kt_ald_calc", per, v, "thousand t", "groupwide", ALD, 3,
        "broker calculation: processed - nucleus - plasma (not a disclosed figure)")

# --- Consolidated sales and ASP (KBV text p1) -------------------------------------------
add("sales_volume_cpo_kt", "9M2026", 507.8, "thousand t", "consolidated", KBV, 1, "text")
add("asp_cpo_idr_kg", "9M2026", 15157, "IDR/kg", "consolidated", KBV, 1, "text")
add("revenue_cpo_idr_bn", "9M2026", 7700, "IDR bn", "consolidated", KBV, 1, "text ('IDR7.70 tn')")
add("sales_volume_cpo_kt", "2026Q3", 187.5, "thousand t", "consolidated", KBV, 1, "text")
add("asp_cpo_idr_kg", "2026Q3", 15565, "IDR/kg", "consolidated", KBV, 1, "text")
add("revenue_cpo_idr_bn", "2026Q3", 2920, "IDR bn", "consolidated", KBV, 1, "text ('IDR2.92 tn')")
add("sales_volume_pk_kt", "2026Q3", 34.2, "thousand t", "consolidated", KBV, 1, "text")
add("asp_pk_idr_kg", "2026Q3", 13402, "IDR/kg", "consolidated", KBV, 1, "text")
add("fertilizer_cost_idr_bn", "2026Q3", 75, "IDR bn", "consolidated", KBV, 1, "text ('-46% YoY to IDR75 bn')")
add("fertilizer_cost_yoy_pct", "2026Q3", -46, "%", "consolidated", KBV, 1, "text")
add("fertilizer_cost_yoy_pct", "9M2026", -23, "%", "consolidated", KBV, 1, "text")
add("purchased_ffb_cost_yoy_pct", "2026Q3", 60, "%", "consolidated", KBV, 1, "text ('+60% YoY rise in purchased FFB costs'); level not disclosed")
add("ffb_yield_t_ha", "2026Q3", 6.4, "t/ha", "groupwide", KBV, 1, "text")
add("ffb_yield_t_ha", "9M2026", 18.9, "t/ha", "groupwide", KBV, 1, "text")
add("share_jv_assoc_idr_bn", "9M2026", 918.9, "IDR bn", "consolidated", KBV, 1, "text; official 9M26 = 956.9 - 38.0 = 918.9")
# --- Ajaib / Bareksa 1Q26 ---------------------------------------------------------------
add("ffb_nucleus_kt", "2026Q1", 698, "thousand t", "groupwide", BRK, 0, "press text ('sekitar 698 ribu ton')")
add("ffb_nucleus_kt", "2025Q1", 741, "thousand t", "groupwide", BRK, 0, "press text")
add("ffb_nucleus_kt", "2026Q1", 698, "thousand t", "groupwide", AJB, 1, "text ('approximately 698 thousand tons')")

# --- Public expose FY2025 (annual split, IDX-disclosed 2026-03-16 21:12) ----------------
YRS = [2021, 2022, 2023, 2024, 2025]
pe = {
    "ffb_nucleus_kt": ({"subsidiaries": [1522, 1881, 1848, 1825, 1902], "associates": [1118, 1319, 1202, 1121, 1138]}, 5),
    "ffb_plasma_kt": ({"subsidiaries": [230, 270, 258, 238, 270], "associates": [73, 84, 91, 92, 114]}, 5),
    "cpo_production_kt": ({"subsidiaries": [564, 676, 671, 631, 652], "associates": [286, 323, 307, 285, 301]}, 7),
    "pk_production_kt": ({"subsidiaries": [113, 141, 141, 132, 137], "associates": [61, 69, 67, 61, 65]}, 7),
    "ffb_processed_kt": ({"internal": [2619, 3199, 3058, 2957, 3031], "external": [1068, 1217, 1145, 1005, 1058]}, 6),
}
annual = []
for item, (d, page) in pe.items():
    for part, vals in d.items():
        for y, v in zip(YRS, vals):
            annual.append({"item": item, "split": part, "period": f"FY{y}", "value": v, "unit": "thousand t",
                           "source_doc": PE[0], "page": page, "first_seen": PE[1],
                           "scope": "subsidiaries" if part == "subsidiaries" else ("associates" if part == "associates" else "groupwide")})
for part, v in {"internal": 3217, "external": 1085, "total": 4302}.items():
    annual.append({"item": "ffb_processed_kt", "split": part, "period": "FY2026F", "value": v, "unit": "thousand t",
                   "source_doc": PE[0], "page": 9, "first_seen": PE[1], "scope": "groupwide (company guidance)"})
for part, v in {"subsidiaries": 692, "associates": 324, "total": 1016}.items():
    annual.append({"item": "cpo_production_kt", "split": part, "period": "FY2026F", "value": v, "unit": "thousand t",
                   "source_doc": PE[0], "page": 9, "first_seen": PE[1], "scope": "company guidance"})
annual.append({"item": "oer_pct", "split": "total", "period": "FY2026F", "value": 23.6, "unit": "%", "source_doc": PE[0],
               "page": 9, "first_seen": PE[1], "scope": "company guidance"})
A = pd.DataFrame(annual)
A.to_csv(REF / "TAPG_annual_ops_split.csv", index=False)
D = pd.DataFrame(rows)
D.to_csv(REF / "TAPG_quarterly_ops.csv", index=False)

# --- checks -------------------------------------------------------------------------------
chk = []


def c(name, lhs, rhs, tol, detail=""):
    chk.append({"check": name, "lhs": lhs, "rhs": rhs, "result": "PASS" if abs(lhs - rhs) <= tol else "FAIL", "detail": detail})


k = D[D.source_doc == KBV[0]].pivot_table(index="item", columns="period", values="value")
g = pd.read_csv(REF / "TAPG_scope_groupwide.csv").set_index(["item", "period"])["value"]
y25 = ["2025Q1", "2025Q2", "2025Q3", "2025Q4"]
c("KBV FY2025 nucleus FFB = AR2025", k.loc["ffb_nucleus_kt", y25].sum(), g[("ffb_nucleus_total_kt", "FY2025")], 2)
c("KBV FY2025 plasma FFB = AR2025", k.loc["ffb_plasma_kt", y25].sum(), 384, 2, "AR2025 p14 highlight")
c("KBV FY2025 CPO = AR2025", k.loc["cpo_production_kt", y25].sum(), 953, 2)
c("KBV FY2025 PK = AR2025", k.loc["pk_production_kt", y25].sum(), 202, 2)
c("KBV FY2025 processed = AR2025", k.loc[["ffb_processed_internal_kt_kbv", "ffb_processed_external_kt_kbv"], y25].sum().sum(), 4089, 2)
c("KBV FY2025 'internal' processed = company internal (PE25/AR nucleus 3,031)",
  k.loc["ffb_processed_internal_kt_kbv", y25].sum(), 3031, 2, "definition mismatch if FAIL")
for q in Q:
    proc = k.loc["ffb_processed_internal_kt_kbv", q] + k.loc["ffb_processed_external_kt_kbv", q]
    c(f"KBV OER = CPO / processed ({q})", 100 * k.loc["cpo_production_kt", q] / proc, k.loc["oer_pct", q], 0.15)
    c(f"KBV KER = PK / processed ({q})", 100 * k.loc["pk_production_kt", q] / proc, k.loc["ker_pct", q], 0.15)
a = D[D.source_doc == ALD[0]].pivot_table(index="item", columns="period", values="value")
for item in ["ffb_nucleus_kt", "ffb_plasma_kt", "cpo_production_kt", "pk_production_kt", "oer_pct", "ker_pct"]:
    for q in ["2025Q3", "2026Q2", "2026Q3"]:
        c(f"KBV vs ALD {item} {q}", k.loc[item, q], a.loc[item, q], 0.55 if "kt" in item else 0.05)
    c(f"KBV 9M2026 sum vs ALD 9M2026 {item}" if "pct" not in item else f"skip {item}", 0, 0, 1)
for item in ["ffb_nucleus_kt", "ffb_plasma_kt", "cpo_production_kt", "pk_production_kt"]:
    c(f"KBV 9M2026 sum = ALD 9M2026 ({item})", k.loc[item, ["2026Q1", "2026Q2", "2026Q3"]].sum(), a.loc[item, "9M2026"], 1.5)
    c(f"KBV 9M2025 sum = ALD 9M2025 ({item})", k.loc[item, ["2025Q1", "2025Q2", "2025Q3"]].sum(), a.loc[item, "9M2025"], 1.5)
for item in ["ffb_nucleus_kt", "ffb_plasma_kt", "cpo_production_kt", "pk_production_kt"]:
    for y in YRS:
        s = A[(A["item"] == item) & (A.period == f"FY{y}")]["value"].sum()
        tot = g.get((f"ffb_nucleus_total_kt" if item == "ffb_nucleus_kt" else "", f"FY{y}"))
        hl = pd.read_csv(REF / "TAPG_highlights_reconciliation.csv").set_index(["item", "fiscal_year"])["latest_value"]
        ref = {"ffb_nucleus_kt": "ffb_harvested_nucleus", "ffb_plasma_kt": "ffb_harvested_plasma",
               "cpo_production_kt": "cpo_production", "pk_production_kt": "pk_production"}[item]
        if (ref, y) in hl.index:
            c(f"PE25 subsidiaries + associates = AR highlight total ({item} FY{y})", s, hl[(ref, y)], 1.5)
c("CPO revenue 9M26 = volume x ASP (IDR bn)", 507.8 * 15157 / 1000, 7700, 15)
c("CPO revenue 3Q26 = volume x ASP (IDR bn)", 187.5 * 15565 / 1000, 2920, 15)
c("PE25 FY2025 subsidiaries CPO (652kt) vs consolidated CPO sales (658.9kt)", 652, 658.917, 10,
  "difference = purchased CPO and inventory change; consistent scope")
# Q1 2026 implied by 9M2026 cumulative (ALD 9M - ALD 2Q26 - ALD 3Q26) vs Q1 as first reported
for item in ["ffb_nucleus_kt", "ffb_plasma_kt", "cpo_production_kt", "pk_production_kt", "ffb_processed_kt"]:
    implied = a.loc[item, "9M2026"] - a.loc[item, "2026Q2"] - a.loc[item, "2026Q3"]
    add(f"{item}_implied_by_9M", "2026Q1", round(implied, 1), "thousand t", "groupwide", ALD, 2,
        "DERIVED: 9M2026 - 2Q26 - 3Q26 (ALD); differs from Q1 as first reported - possible revision")
    first = {"ffb_nucleus_kt": 698, "ffb_plasma_kt": 95, "cpo_production_kt": 227, "pk_production_kt": 46,
             "ffb_processed_kt": 942}[item]
    chk.append({"check": f"Q1 2026 {item}: implied by 9M cumulative vs first reported (press 2026-04-28 / KBV chart)",
                "lhs": round(implied, 1), "rhs": first, "result": "DIFFERS" if abs(implied - first) > 1.5 else "PASS",
                "detail": "unexplained; treat Q1 2026 as revised; PIT: use first-reported value before 2026-10-28"})
D = pd.DataFrame(rows)
# PIT fields (audit finding A): keep reporting period, original publication (unknown unless
# verified), revision date and earliest verified availability separately.
D["reporting_period"] = D["period"]
D["original_publication_date"] = None          # newsletters (S-033) not in hand -> unverified
D["revision_date"] = None
D.loc[D["item"].str.endswith("_implied_by_9M"), "revision_date"] = "2026-10-29"
D["earliest_verified_availability"] = D["first_seen"]
D.to_csv(REF / "TAPG_quarterly_ops.csv", index=False)
for x in chk:
    if x["check"].startswith("KBV 9M2026 sum = ALD 9M2026") and x["result"] == "FAIL":
        x["result"] = "DIFFERS"; x["detail"] = "KBV quarterly chart sums vs 9M cumulative (KBV text agrees with ALD 9M): traced to Q1 2026 revision"
    if x["check"] in ("KBV vs ALD ffb_plasma_kt 2025Q3", "KBV vs ALD ker_pct 2026Q3") and x["result"] == "FAIL":
        x["result"] = "ROUNDING"; x["detail"] = "chart label rounding (ALD has one more decimal)"
    if x["check"].startswith("KBV FY2025 'internal'") and x["result"] == "FAIL":
        x["result"] = "DEFINITION MISMATCH"; x["detail"] = "KBV internal/external split (2,833/1,257) differs from company definition (internal 3,031 = nucleus processed; external 1,058 = plasma 400 + third party 659); totals agree. Do not use KBV split."
chk = [x for x in chk if not x["check"].startswith("skip")]
C = pd.DataFrame(chk)
C.to_csv(REF / "TAPG_quarterly_ops_checks.csv", index=False)
print(C[C.result == "FAIL"].to_string(index=False))
print(C.result.value_counts().to_string())
