"""Benchmark series (A-007).

1. IHSG: daily price-index return of ^JKSE (S-002). This is a PRICE index, so it
   excludes dividends.
2. EW core PIT: an equal-weight portfolio of names in the core liquidity band at each
   month-end (data/reference/pit_universe_monthly.csv), held through the next month.
   Daily returns use Yahoo 'Adj Close' (dividend- and split-adjusted), so this is a
   TOTAL-return series. Weights drift within the month (buy-and-hold) and reset at
   each month-end.

Membership at month-end t uses only data up to t (see build_universe.py); returns
start on the first session after t, so there is no look-ahead.

Output: data/reference/benchmarks_daily.csv (index levels and returns, base 100)
Usage:  python -I quant/benchmarks.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ohlcv"
REF = ROOT / "data" / "reference"


def adj_close(ticker: str) -> pd.Series:
    df = pd.read_csv(RAW / f"{ticker}.csv", index_col=0, parse_dates=True)
    s = pd.to_numeric(df["Adj Close"], errors="coerce").dropna()
    return s[~s.index.duplicated()]


def ew_buy_and_hold(returns: pd.DataFrame, members_by_month: dict) -> pd.Series:
    """Daily returns of a portfolio rebalanced to equal weight at each month-end.

    returns:          daily simple returns, columns = tickers
    members_by_month: {rebalance_date (Timestamp): [tickers]}
    """
    out = pd.Series(np.nan, index=returns.index)
    dates = sorted(members_by_month)
    for i, d in enumerate(dates):
        end = dates[i + 1] if i + 1 < len(dates) else returns.index.max()
        period = returns.loc[(returns.index > d) & (returns.index <= end)]
        names = [n for n in members_by_month[d] if n in returns.columns]
        if period.empty or not names:
            continue
        r = period[names].fillna(0.0)  # untraded day = 0% (suspension handled at selection)
        growth = (1 + r).cumprod()
        value = growth.mean(axis=1)               # equal starting weights
        prev = value.shift(1).fillna(1.0)
        out.loc[period.index] = value / prev - 1
    return out


def main() -> int:
    pit = pd.read_csv(REF / "pit_universe_monthly.csv", parse_dates=["date"])
    core = pit[pit["liquidity_band"] == "core_liquidity"]
    members = {d: list(g["ticker"]) for d, g in core.groupby("date")}
    tickers = sorted(core["ticker"].unique())
    px = pd.concat({t: adj_close(t) for t in tickers}, axis=1).sort_index()
    rets = px.pct_change(fill_method=None)

    ihsg = adj_close("IHSG")
    ihsg_r = ihsg.pct_change()
    ew_r = ew_buy_and_hold(rets, members)

    start = min(members)
    df = pd.DataFrame({"ihsg_ret": ihsg_r, "ew_core_pit_ret": ew_r}).loc[lambda x: x.index > start]
    df = df.dropna(how="all")
    df["ihsg_level"] = 100 * (1 + df["ihsg_ret"].fillna(0)).cumprod()
    df["ew_core_pit_level"] = 100 * (1 + df["ew_core_pit_ret"].fillna(0)).cumprod()
    df["ew_core_pit_names"] = pd.Series(
        {d: len(v) for d, v in members.items()}).reindex(df.index, method="ffill")
    df.to_csv(REF / "benchmarks_daily.csv", float_format="%.6f")

    yearly = (1 + df[["ihsg_ret", "ew_core_pit_ret"]].fillna(0)).groupby(df.index.year).prod() - 1
    print((yearly * 100).round(1).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
