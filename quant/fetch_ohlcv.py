"""Download daily OHLCV for the palm oil candidate list and benchmarks from Yahoo Finance.

Writes one CSV per ticker to data/raw/ohlcv/ (git-ignored) and a coverage summary to
data/processed/ohlcv_coverage.csv. Source: S-002 in data/SOURCE_REGISTER.csv.

Usage:  python -I quant/fetch_ohlcv.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ohlcv"
PROCESSED = ROOT / "data" / "processed"

START = "2015-01-01"  # one year of history before the 2016 backtest start, for lookbacks

# Every IDX ticker with palm oil exposure that we know of, including excluded names, so
# the point-in-time universe can include stocks that later became illiquid or delisted.
PALM_TICKERS = [
    "AALI", "LSIP", "SIMP", "SSMS", "TAPG", "DSNG", "STAA", "NSSS", "MGRO", "GZCO",
    "ANJT", "TBLA", "BWPT", "CSRA", "PSGO",
    "SGRO", "SMAR", "TLDN", "FAPA", "CBUT", "JAWA", "UNSP", "PGUN",
    "PALM", "GOLL", "BTEK", "MAGP",
]
BENCHMARKS = {"^JKSE": "IHSG", "IDR=X": "USDIDR", "BZ=F": "BRENT"}


def fetch(symbol: str) -> pd.DataFrame:
    df = yf.download(symbol, start=START, interval="1d", auto_adjust=False,
                     progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna(how="all")


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    rows = []
    symbols = {f"{t}.JK": t for t in PALM_TICKERS} | BENCHMARKS
    for symbol, name in symbols.items():
        try:
            df = fetch(symbol)
        except Exception as exc:  # network / delisted symbol
            print(f"{symbol}: error {exc}", file=sys.stderr)
            df = pd.DataFrame()
        if df.empty:
            rows.append({"ticker": name, "symbol": symbol, "rows": 0})
            continue
        df.to_csv(RAW / f"{name}.csv")
        last_252 = df.tail(252)
        traded = (last_252["Close"] * last_252["Volume"])
        zero_vol = (last_252["Volume"] == 0).mean()
        rows.append({
            "ticker": name,
            "symbol": symbol,
            "rows": len(df),
            "first_date": df.index.min().date(),
            "last_date": df.index.max().date(),
            "median_adv_idr_bn_252d": round(traded.median() / 1e9, 3),
            "mean_adv_idr_bn_252d": round(traded.mean() / 1e9, 3),
            "zero_volume_share_252d": round(zero_vol, 3),
            "last_close": float(df["Close"].iloc[-1]),
        })
        print(f"{symbol}: {len(df)} rows {df.index.min().date()} -> {df.index.max().date()}")
    pd.DataFrame(rows).to_csv(PROCESSED / "ohlcv_coverage.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
