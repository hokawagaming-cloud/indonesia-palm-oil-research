"""Data-quality checks on the daily OHLCV files from quant/fetch_ohlcv.py (S-002).

Flags per ticker:
  * missing sessions versus the IHSG trading calendar (after the first bar),
  * zero-volume sessions (suspensions or no trades),
  * stale closes (same close on 5 or more consecutive sessions with zero volume),
  * extreme daily moves beyond IDX auto-rejection-style bounds (|r| > 35%), which
    usually mean an unadjusted corporate action or a bad print,
  * OHLC consistency (low <= open, close <= high).

Output: data/reference/ohlcv_quality.csv (tracked, no prices)
Usage:  python -I quant/ohlcv_quality.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ohlcv"
EXTREME = 0.35


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df.apply(pd.to_numeric, errors="coerce").dropna(subset=["Close"])


def check(df: pd.DataFrame, calendar: pd.DatetimeIndex) -> dict:
    cal = calendar[(calendar >= df.index.min()) & (calendar <= df.index.max())]
    missing = cal.difference(df.index)
    zero = df["Volume"].fillna(0) == 0
    same = df["Close"].diff().fillna(1) == 0
    run = (same & zero).astype(int)
    stale_runs = (run.groupby((run == 0).cumsum()).cumsum() >= 5).sum()
    r = df["Close"].pct_change()
    bad_ohlc = ((df["Low"] > df[["Open", "Close"]].min(axis=1) + 1e-9) |
                (df["High"] < df[["Open", "Close"]].max(axis=1) - 1e-9)).sum()
    ext = r[abs(r) > EXTREME]
    return {
        "first_date": df.index.min().date(), "last_date": df.index.max().date(),
        "sessions": len(df), "missing_vs_ihsg": len(missing),
        "zero_volume_sessions": int(zero.sum()),
        "stale_close_sessions": int(stale_runs),
        "extreme_moves": len(ext),
        "extreme_move_dates": ";".join(f"{d.date()}:{v:+.0%}" for d, v in ext.head(8).items()),
        "ohlc_inconsistent": int(bad_ohlc),
    }


def main() -> int:
    calendar = load(RAW / "IHSG.csv").index
    rows = []
    for p in sorted(RAW.glob("*.csv")):
        if p.stem in {"USDIDR", "BRENT"}:
            continue
        rows.append({"ticker": p.stem, **check(load(p), calendar)})
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "data" / "reference" / "ohlcv_quality.csv", index=False)
    print(out.drop(columns="extreme_move_dates").to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
