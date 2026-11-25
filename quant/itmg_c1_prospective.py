"""ITMG-C1 FROZEN prospective forecast (D-039). Run ON the origin date (quarter end + 10 days), e.g.
    python -I -X utf8 quant/itmg_c1_prospective.py 2026Q4 path/to/CMO-Historical-Data-Monthly.xlsx
Rules (frozen in ITMG_C1_frozen_spec.json; identical to the evaluated spec):
  * Inputs: the CMO file AS DOWNLOADED ON THE ORIGIN DATE (archive it with its SHA-256) and first-reported ITMG
    ASP for quarters published before the origin (ITMG_quarterly_raw_extract.csv, updated with the q-1 deck).
  * M2 is re-estimated on the expanding window exactly as in quant/itmg_c1.py (procedure frozen; parameters
    update mechanically with new data). B4 is computed alongside.
  * If the quarter's third Newcastle month is NOT in the file at the origin, the forecast is NOT made at the origin;
    it is made on the first day the month is available and flagged 'late_origin' (still before ITMG's release).
  * The forecast is appended to data/reference/forecast_journal.csv; it RESOLVES when ITMG publishes the quarter.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import itmg_c1 as c  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def run(q: str, cmo_path: str) -> dict:
    qq = pd.Period(q, "Q")
    orig_cmo = c.ROOT / "data" / "raw" / "macro" / "CMO-Historical-Data-Monthly.xlsx"
    c_newc = c.newcastle
    def newc_from_file():                                   # read the origin-date vintage, not the repo copy
        df = pd.read_excel(cmo_path, "Monthly Prices", header=None)
        hdr, d = df.iloc[4], df.iloc[6:]
        col = [i for i, h in enumerate(hdr) if isinstance(h, str) and h.startswith("Coal, Australian")][0]
        idx = pd.PeriodIndex([pd.Period(str(x).replace("M", "-"), "M") for x in d[0]], freq="M")
        return pd.Series(pd.to_numeric(d[col], errors="coerce").to_numpy(), index=idx).dropna()
    c.newcastle = newc_from_file
    try:
        N = newc_from_file()
        if qq.asfreq("M", "end") not in N.index:
            return {"status": "late_origin: third month not yet published", "quarter": q}
        P = c.panel()
        P = P.reindex(P.index.union(pd.PeriodIndex([qq], freq="Q")))
        P.loc[qq, "N"] = N.loc[qq.asfreq("M", "start"):qq.asfreq("M", "end")].mean()
        P.loc[qq, "N1"] = N.loc[qq.asfreq("M", "start") - 1:qq.asfreq("M", "end") - 1].mean()
        P.loc[qq, "asp"] = float("nan")
        f = c.forecast(P, qq)
    finally:
        c.newcastle = c_newc
    sha = hashlib.sha256(Path(cmo_path).read_bytes()).hexdigest()
    return {"quarter": q, "made_on": date.today().isoformat(), "cmo_sha256": sha, "M2": f["M2_distributed_lag"], "B4": f["B4_price_scaled"]}


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1], sys.argv[2]), indent=1, default=float))
