"""Extract LSIP note-level data (Phase XVII): cost of goods sold breakdown, bearer-plant movements,
related-party (Bank Ina Perdana) cash and declared dividends.

    python -I -X utf8 quant/lsip_notes_extract.py      (after quant/pdf_to_text.py)

Outputs (IDR million unless stated):
  data/reference/research/LSIP_cogs_breakdown.csv
  data/reference/research/LSIP_bearer_plants.csv
  data/reference/research/LSIP_related_party_cash.csv
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "quant"))
from lsip_fs_extract import DOCS, TXT, block_before, to_num  # noqa: E402

OUT = ROOT / "data" / "reference" / "research"

COGS = {
    "indirect": r"Allocation of indirect costs",
    "ffb_purchases": r"FFB purchases|Purchases of FFB",
    "harvesting": r"Harvesting costs",
    "upkeep_fertiliser": r"Upkeep and cultivation costs",
    "depreciation": r"Depreciation and amortization expenses",
    "manufacturing": r"Manufacturing costs",
    "total_production_cost": r"Total manufacturing costs",
    "cost_goods_manufactured": r"Cost of goods manufactured",
    "cogs": r"Cost of goods sold(?![\s\|]*(?:are|adalah))",
}


def joined(stem: str) -> str:
    return (TXT / f"{stem}.txt").read_text(encoding="utf-8").replace("\n", "|")


def cogs_note(stem: str) -> dict:
    s = joined(stem)
    m = re.search(r"\d{2}\.\s*COST OF GOODS SOLD(?!\s*\(continued)", s)
    if m is None:
        return {}
    w = s[m.start(): m.start() + 9000]
    out = {}
    for k, rx in COGS.items():
        mm = re.search(rx, w)
        if mm:
            v = block_before(w, mm.start())
            if v:
                out[k] = v
    # finished goods (opening/closing) are the second occurrence of the at-beginning/at-end labels
    fg = w[w.find("Finished goods"):] if "Finished goods" in w else ""
    for k, rx in {"fg_open": r"At the beginning of (?:the )?year|At the beginning of (?:the )?period",
                  "fg_close": r"At the end of (?:the )?year|At the end of (?:the )?period"}.items():
        mm = re.search(rx, fg)
        if mm:
            v = block_before(fg, mm.start())
            if v:
                out[k] = v
    return out


def bearer_movements(stem: str) -> dict:
    """First two numbers of the Additions / Reclassifications / Deductions rows of the cost roll-forward
    (columns: immature, mature bearer plants). Two roll-forwards per annual note (prior year, current year)."""
    s = joined(stem)
    a = s.find("Tanaman Produktif/|Bearer Plants")
    if a < 0:
        a = s.find("Bearer Plants|Aset Tetap Lainnya")
    if a < 0:
        return {}
    w = s[a: a + 6000]
    out = {}
    for k, rx in {"additions": r"Penambahan\s*/\s*Additions", "deductions": r"Pengurangan\s*/\s*Deductions",
                  "reclass": r"Reklasifikasi\s*/\s*Reclassifications"}.items():
        hits = list(re.finditer(rx, w[: w.find("Akumulasi") if "Akumulasi" in w else len(w)]))
        if hits:
            h = hits[-1]                                    # current-year roll-forward is the last one
            toks = [t.strip() for t in w[h.end():].split("|") if t.strip()][:2]
            try:
                out[k] = [to_num(t) if t != "-" else 0.0 for t in toks]
            except ValueError:
                pass
    return out


def main() -> None:
    rows, brows = [], []
    for stem, (cur, pri) in DOCS.items():
        if not (TXT / f"{stem}.txt").exists():
            continue
        c = cogs_note(stem)
        rows.append({"period": cur, "source": stem, **{k: v[0] for k, v in c.items()}})
        if pri.startswith("FY") and pri == "FY2020":
            rows.append({"period": pri, "source": stem, **{k: v[1] for k, v in c.items()}})
        if cur.startswith("FY"):
            b = bearer_movements(stem)
            brows.append({"period": cur, "source": stem,
                          **{f"{k}_immature": v[0] for k, v in b.items()},
                          **{f"{k}_mature": v[1] for k, v in b.items() if len(v) > 1}})
    C = pd.DataFrame(rows).set_index("period").sort_index()
    C.to_csv(OUT / "LSIP_cogs_breakdown.csv", float_format="%.0f")
    B = pd.DataFrame(brows).set_index("period").sort_index()
    B.to_csv(OUT / "LSIP_bearer_plants.csv", float_format="%.0f")
    # related-party bank: transcribed from the cash notes (current accounts + time deposits at PT Bank Ina
    # Perdana Tbk, Salim group); every value is asserted to appear in the cited document text.
    rp = [("FY2021", "AR2022", ["518.756"], 518756), ("FY2022", "AR2023", ["73.849", "600.000"], 673849),
          ("FY2023", "pp_london_sumatra_indonesia_bilingual_31_des_2024_released", ["246.645", "600.000"], 846645),
          ("FY2024", "LSIP_bilingual_31_des_2025_released", ["121.293", "15.379", "770.000"], 906672),
          ("FY2025", "LSIP_bilingual_31_des_2025_released", ["915.788", "23.768", "700.000"], 1639556),
          ("9M26", "LSIP_bilingual_30_Sep_2026_Released", ["82.306", "32.710", "550.000"], 665016)]
    R = []
    for p, stem, parts, tot in rp:
        s = joined(stem)
        assert all(x in s for x in parts), (p, parts)
        assert abs(sum(to_num(x) for x in parts) - tot) < 1, p
        R.append({"period": p, "source": stem, "bank_ina_perdana": tot})
    R = pd.DataFrame(R).set_index("period")
    fin = pd.read_csv(OUT / "LSIP_financials_annual.csv", index_col=0)
    R["cash_total"] = fin["cash_end"].reindex(R.index)
    R["share"] = R.bank_ina_perdana / R.cash_total
    R.to_csv(OUT / "LSIP_related_party_cash.csv", float_format="%.4f")
    print(C.to_string()); print(B.to_string()); print(R.to_string())


if __name__ == "__main__":
    main()
