"""Expectation-adjusted earnings surprise (Phase V, workstream 2). Replaces growth-based proxies.

For a results filing of period P (cumulative Q1/H1/9M/FY) at availability date t:
  expected_P  = consensus FY profit (EPS x shares) as last recorded BEFORE t in
                data/reference/consensus_history.csv, minus reported cumulative profit
                already public before t (for FY, the 9M figure), i.e. the implied remainder
  actual_P    = reported remainder (e.g. Q4 = FY - 9M)
  surprise    = (actual - expected) / |expected|
  SUE-like    = (actual - expected) / (dispersion of the implied remainder from the
                consensus low/high EPS)
Then CAR windows come from the event-study logic in quant/tapg_price_in.py.
STATUS: consensus history starts 2026-11-24 (tapg_monitor.py), so the first measurable
event is the FY2026 filing (~Mar 2027). Until n >= 8 events per name, results are
DESCRIPTIVE only.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"


def implied_remainder(cons: pd.DataFrame, ticker: str, fy: str, before: str, shares_mn: float, reported_cum_bn: float) -> dict | None:
    """Consensus-implied profit for the not-yet-reported part of fiscal year `fy`, using the
    last snapshot strictly before `before`."""
    c = cons[(cons.ticker == ticker) & (cons.fy == fy) & (pd.to_datetime(cons.retrieved) < pd.Timestamp(before))]
    if c.empty:
        return None
    r = c.sort_values("retrieved").iloc[-1]
    f = lambda eps: eps * shares_mn / 1000 - reported_cum_bn
    return {"snapshot": r.retrieved, "expected": f(r.eps_avg), "low": f(r.eps_low), "high": f(r.eps_high), "n": r.n_analysts}


def surprise(actual_bn: float, imp: dict) -> dict:
    spread = max(imp["high"] - imp["low"], 1e-9)
    return {"surprise_pct": (actual_bn - imp["expected"]) / abs(imp["expected"]),
            "sue_like": (actual_bn - imp["expected"]) / spread}
