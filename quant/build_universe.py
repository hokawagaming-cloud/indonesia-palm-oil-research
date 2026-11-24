"""Build the monthly point-in-time (PIT) palm oil universe.

At each month-end date t, a ticker is eligible only if, using data available on or
before t:
  1. it had at least SEASONING_DAYS trading days since its first trade (an IPO filter),
  2. it traded in the last 20 sessions (filters out suspended or delisted names),
  3. its median daily traded value (close x volume) over the last ADV_WINDOW sessions
     meets the liquidity band (core >= A-001; extended within A-002).

The candidate list is data/reference/listings.csv, which includes excluded and
historical-only names so that stocks later dropped stay in the history (no
survivorship bias). Tickers with no price history (e.g. GOLL, MAGP) are reported as
data gaps rather than silently dropped.

Inputs:  data/raw/ohlcv/*.csv            (from quant/fetch_ohlcv.py, source S-002)
Outputs: data/reference/pit_universe_monthly.csv   (membership flags, no prices)
         data/reference/pit_universe_summary.csv

Usage:  python -I quant/build_universe.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ohlcv"
REF = ROOT / "data" / "reference"

START = "2016-01-31"
SEASONING_DAYS = 60          # A-004
ADV_WINDOW = 63              # A-003, about 3 months
CORE_MIN_IDR = 1.5e9         # A-001
EXT_MIN_IDR = 0.25e9         # A-002
STALE_WINDOW = 20


def load(ticker: str) -> pd.DataFrame | None:
    path = RAW / f"{ticker}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df = df[pd.to_numeric(df["Volume"], errors="coerce").notna()]
    df = df.astype(float)
    return df if not df.empty else None


def main() -> int:
    listings = pd.read_csv(REF / "listings.csv")
    ihsg = load("IHSG")
    calendar = ihsg.index if ihsg is not None else None
    month_ends = (pd.Series(calendar, index=calendar).loc[START:]
                  .groupby(calendar[calendar >= START].to_period("M")).max().tolist())

    rows, gaps = [], []
    for _, rec in listings.iterrows():
        t = rec["ticker"]
        df = load(t)
        if df is None:
            gaps.append(t)
            continue
        traded = df["Close"] * df["Volume"]
        first = df.index.min()
        for d in month_ends:
            hist = df.loc[:d]
            if hist.empty:
                continue
            sessions = len(hist)
            recent = hist.tail(STALE_WINDOW)
            active = bool((recent["Volume"] > 0).any())
            adv = float(traded.loc[:d].tail(ADV_WINDOW).median())
            seasoned = sessions >= SEASONING_DAYS
            if not (seasoned and active):
                band = "ineligible"
            elif adv >= CORE_MIN_IDR:
                band = "core_liquidity"
            elif adv >= EXT_MIN_IDR:
                band = "extended_liquidity"
            else:
                band = "below_threshold"
            rows.append({
                "date": d.date(), "ticker": t,
                "coverage_tier_d002": rec["coverage_tier_d002"],
                "seasoned": seasoned, "active": active,
                "median_adv_idr_bn": round(adv / 1e9, 3),
                "liquidity_band": band,
                "first_trade_in_data": first.date(),
            })

    out = pd.DataFrame(rows)
    out.to_csv(REF / "pit_universe_monthly.csv", index=False)

    summary = (out.assign(year=pd.to_datetime(out["date"]).dt.year)
               .pivot_table(index="year", columns="liquidity_band", values="ticker",
                            aggfunc="count", fill_value=0))
    # average names per month in each band, per year
    months = out.assign(year=pd.to_datetime(out["date"]).dt.year).groupby("year")["date"].nunique()
    summary = (summary.div(months, axis=0)).round(1)
    summary.to_csv(REF / "pit_universe_summary.csv")
    print(summary.to_string())
    print("No price history (survivorship gap):", ", ".join(gaps) or "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
