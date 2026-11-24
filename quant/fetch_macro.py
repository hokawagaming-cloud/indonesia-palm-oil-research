"""Download World Bank Pink Sheet monthly prices (S-003, incl. fertilisers urea / DAP / potassium
chloride as leading indicators of plantation cost) and NOAA ONI (S-006).

Raw files: data/raw/macro/ (git-ignored). Tracked derived monthly table:
data/reference/macro_monthly.csv with palm oil, soybean oil, palm kernel oil and Brent
(USD), USD/IDR month-end and month-average (from S-002 IDR=X), and the ONI index.

World Bank prices are MONTHLY AVERAGES. ONI is a 3-month running mean labelled by its
centre month. Lead-lag tests must allow for this averaging (it mechanically smooths and
shifts timing).
Usage: python -I quant/fetch_macro.py
"""
from pathlib import Path
import io
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "macro"
WB = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
UA = {"User-Agent": "Mozilla/5.0 (research script)"}


def get(url: str, dest: Path) -> Path:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        dest.write_bytes(r.read())
    return dest


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    wb = pd.read_excel(get(WB, RAW / "CMO-Historical-Data-Monthly.xlsx"), sheet_name="Monthly Prices", header=None)
    hdr = wb.iloc[4].tolist()
    want = {"Palm oil": "palm_oil_usd_t", "Soybean oil": "soybean_oil_usd_t",
            "Palm kernel oil": "palm_kernel_oil_usd_t", "Crude oil, Brent": "brent_usd_bbl",
            "Urea": "urea_usd_t", "DAP": "dap_usd_t", "Potassium chloride": "mop_usd_t"}
    norm = lambda h: h.replace("*", "").strip() if isinstance(h, str) else h
    cols = {i: want[norm(h)] for i, h in enumerate(hdr) if norm(h) in want}
    body = wb.iloc[6:, [0] + list(cols)].rename(columns={0: "month", **cols})
    body = body[body["month"].astype(str).str.match(r"^\d{4}M\d{2}$")]
    body["month"] = pd.PeriodIndex(body["month"].str.replace("M", "-"), freq="M").astype(str)
    body = body.set_index("month").apply(pd.to_numeric, errors="coerce")

    oni_txt = get(ONI, RAW / "oni.ascii.txt").read_text()
    oni = pd.read_csv(io.StringIO(oni_txt), sep=r"\s+")
    seas = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
    oni["month"] = [f"{y}-{seas[s]:02d}" for s, y in zip(oni.SEAS, oni.YR)]
    body = body.join(oni.set_index("month")["ANOM"].rename("oni"), how="left")

    fx = pd.read_csv(ROOT / "data" / "raw" / "ohlcv" / "USDIDR.csv", index_col=0, parse_dates=True)
    fx = pd.to_numeric(fx["Close"], errors="coerce").dropna()
    fx = fx[(fx > 5000) & (fx < 50000)]  # drop obviously bad prints
    m = fx.groupby(fx.index.to_period("M"))
    body = body.join(pd.DataFrame({"usdidr_month_end": m.last(), "usdidr_month_avg": m.mean()}).set_index(
        m.last().index.astype(str)), how="left")
    body["palm_oil_idr_kg"] = body["palm_oil_usd_t"] * body["usdidr_month_avg"] / 1000
    out = body.loc["2014-01":]
    out.to_csv(ROOT / "data" / "reference" / "macro_monthly.csv")
    print(out.tail(4).round(2).to_string())
    print("rows", len(out), "palm oil last", out["palm_oil_usd_t"].last_valid_index())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
