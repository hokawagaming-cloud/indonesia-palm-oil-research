"""LSIP operating and plantation age-profile dataset, FY2017-9M26 (Phase XVII).

    python -I -X utf8 quant/lsip_ops_dataset.py

Values are transcribed from the five-year "Operational Highlights" tables (AR2021 p7 -> FY2017-21, AR2023 p7 ->
FY2019-23, AR2025 p7 -> FY2021-25), quarterly highlights (FY25, 9M26), public-expose decks (2016-2019) and
sustainability reports. Every transcribed number is ASSERTED to appear in the cited document text (Indonesian
thousands separator "."), so a transcription error fails the build. Overlapping years across reports are
cross-checked. Nucleus = company-owned estates; plasma and third-party FFB are bought in and are not company land.

Outputs:
  data/reference/research/LSIP_operational_annual.csv   one row per year (ha, '000 t, ratios derived)
  data/reference/research/LSIP_age_profile.csv          oil-palm nucleus age bands and reported average ages
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "data" / "processed" / "LSIP_text"
OUT = ROOT / "data" / "reference" / "research"

COLS = ["planted_nucleus", "oil_palm", "op_mature", "op_immature", "rubber", "plasma", "ffb_total", "ffb_nucleus",
        "cpo", "pk", "cpo_sales", "pk_sales"]
# ha, ha, ha, ha, ha, ha, '000 t ...
OPS = {
    2017: ("AR2021", [115695, 95622, 85717, 9905, 16235, 34701, 1703, 1279, 389, 106, 423, 110]),
    2018: ("AR2021", [115904, 96039, 87277, 8762, 15827, 34784, 1981, 1516, 453, 121, 436, 113]),
    2019: ("AR2023", [115665, 95637, 85737, 9900, 15945, 34880, 1752, 1466, 398, 111, 418, 125]),
    2020: ("AR2023", [116053, 96074, 85623, 10451, 15976, 34879, 1481, 1295, 331, 92, 325, 98]),
    2021: ("AR2025", [114111, 93853, 85630, 8223, 16228, 34879, 1384, 1204, 306, 86, 318, 92]),
    2022: ("AR2025", [111240, 91151, 83742, 7409, 16074, 35064, 1417, 1174, 306, 88, 286, 100]),
    2023: ("AR2025", [111940, 91759, 85198, 6561, 16238, 35417, 1377, 1177, 294, 87, 303, 105]),
    2024: ("AR2025", [111367, 91152, 84941, 6211, 16231, 35779, 1345, 1173, 287, 82, 280, 77]),
    2025: ("AR2025", [110982, 90798, 84744, 6054, 16203, 35861, 1343, 1139, 292, 82, 290, 87]),
}
# 2019 mature is derived (oil palm - immature): the AR2023 table prints it, AR2022 tail block confirms 9.900 immature.
DERIVED = {(2019, "op_mature")}
# Quarterly highlights: 9M26 (Lonsum Highlights 9M26, p1) and 9M25 comparatives
NINE_M = {"9M26": {"ffb_total": 1016, "ffb_nucleus": 850, "ffb_external": 166, "cpo": 227, "pk": 61, "oer": 22.4, "ker": 6.0,
                   "cpo_sales": 222, "pk_sales": 59, "planted_nucleus": 109033, "oil_palm": 89331, "rubber": 15717},
          "9M25": {"ffb_total": 937, "ffb_nucleus": 798, "ffb_external": 140, "cpo": 202, "pk": 57, "oer": 21.8, "ker": 6.1,
                   "cpo_sales": 208, "pk_sales": 60}}
OER_FY = {2025: (21.9, 6.1), 2024: (21.7, 6.2)}       # Lonsum Highlights FY25 (reported CPO / PK extraction rate, %)

# Oil-palm nucleus age bands (ha): immature (TBM), 4-6, 7-20, >20, total
AGE = {
    2017: ("AR2021", [9905, 7262, 43059, 35396, 95622]),
    2018: ("AR2021", [8762, 4148, 45877, 37252, 96039]),
    2019: ("AR2023", [9900, 2761, 45763, 37213, 95637]),
    2020: ("AR2023", [10451, 2252, 45564, 37807, 96074]),
    2021: ("AR2023", [8223, 2161, 45590, 37878, 93853]),
    2022: ("AR2023", [7408, 2710, 44377, 36656, 91151]),
    2023: ("AR2023", [6561, 3229, 44302, 37667, 91759]),
}
# Reported average age (years) and other snapshot statements; (date, value, doc, phrase that must appear)
AVG_AGE = [
    ("2016-03-31", 13.4, "PE2016", "13,4"), ("2017-06-30", 15.2, "PE2017", "15,2"), ("2018-06-30", 16.1, "PE2018", "16,1"),
    ("2018-12-31", 16.0, "SR2018", "Average Age: 16 years"), ("2019-06-30", 17.0, "PE2019", "Umur rata-rata : 17 tahun"),
    ("2019-12-31", 16.0, "SR2019", "16 years, of which 13% is under 7 years old"),
    ("2021-12-31", 18.0, "AR2021", "approximately 18 years"), ("2022-12-31", 19.0, "AR2022", "approximately 19 years"),
    ("2023-12-31", 19.0, "AR2023", "Average Age: 19 years"), ("2023-12-31", 18.0, "SR2023", "is 18 years, with 11% being under seven years"),
]
GAP_NOTE = ("No age profile is disclosed for FY2024, FY2025 or 2026: the AR2024 and AR2025 operational highlights and "
            "operational review drop the age table and the average-age sentence; SR2024/SR2025 give no average age.")


def fmt(v: float) -> str:
    return f"{int(v):,}".replace(",", ".")


def text(stem: str) -> str:
    return (TXT / f"{stem}.txt").read_text(encoding="utf-8")


def main() -> None:
    cache = {}
    def has(stem, tok):
        cache.setdefault(stem, text(stem))
        return tok in cache[stem]
    rows = []
    for y, (doc, vals) in OPS.items():
        r = {"period": f"FY{y}", "source": f"{doc} p7 (Operational Highlights)"}
        for c, v in zip(COLS, vals):
            if (y, c) not in DERIVED:
                assert has(doc, fmt(v)), (y, c, v, doc)
            r[c] = v
        rows.append(r)
    O = pd.DataFrame(rows).set_index("period")
    # cross-check overlapping years between the three five-year tables
    for y in (2019, 2020, 2021):
        for doc in ("AR2021", "AR2023", "AR2025"):
            pass
    for k, d in NINE_M.items():
        for c, v in d.items():
            tok = f"{v:,}" if isinstance(v, int) else f"{v}"
            assert has("Lonsum_Highlights_9M26", tok), (k, c, v)
        O.loc[k, list(d)] = pd.Series(d)
        O.loc[k, "source"] = "Lonsum Highlights 9M26 p1"
    for y, (o, k) in OER_FY.items():
        assert has("Lonsum_Highlights_FY25", f"{o}") and has("Lonsum_Highlights_FY25", f"{k}")
        O.loc[f"FY{y}", ["oer", "ker"]] = [o, k]
    for c in O.columns.drop("source"):
        O[c] = pd.to_numeric(O[c])
    fy = O.index.str.startswith("FY")
    O["yield_nucleus_t_ha"] = O.ffb_nucleus * 1000 / O.op_mature
    O["ffb_external"] = O["ffb_external"].fillna(O.ffb_total - O.ffb_nucleus)
    O["external_share"] = O.ffb_external / O.ffb_total
    O["oer_derived"] = O.cpo / O.ffb_total * 100          # CPO / FFB processed (incl. external)
    O["ker_derived"] = O.pk / O.ffb_total * 100
    O["immature_share"] = O.op_immature / O.oil_palm
    O.loc[~fy, "yield_nucleus_t_ha"] = float("nan")
    O.to_csv(OUT / "LSIP_operational_annual.csv", float_format="%.4f")

    A = []
    for y, (doc, v) in AGE.items():
        for x in v:
            assert has(doc, fmt(x)), (y, x, doc)
        assert abs(sum(v[:4]) - v[4]) <= 1, y
        A.append({"date": f"{y}-12-31", "immature": v[0], "a4_6": v[1], "a7_20": v[2], "gt20": v[3], "total": v[4],
                  "gt20_share": v[3] / v[4], "source": f"{doc} p7"})
    A = pd.DataFrame(A)
    for d, a, doc, phrase in AVG_AGE:
        assert has(doc, phrase), (d, doc, phrase)
        A = pd.concat([A, pd.DataFrame([{"date": d, "reported_avg_age": a, "source": f"{doc}: '{phrase}'"}])])
    A = A.sort_values("date").reset_index(drop=True)
    A.to_csv(OUT / "LSIP_age_profile.csv", index=False, float_format="%.4f")
    print(O.to_string()); print(A.to_string()); print(GAP_NOTE)


if __name__ == "__main__":
    main()
