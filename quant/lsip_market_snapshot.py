"""LSIP / TAPG / palm-peer market data and consensus snapshot (Phase XVII). Dated forward snapshot only; no
historical consensus is reconstructed (none exists in this repository before 2026-11-24).

    python -I -X utf8 quant/lsip_market_snapshot.py -> data/reference/research/LSIP_market_snapshot.json
                                                       data/reference/research/palm_peers_snapshot.csv
                                                       appends rows to data/reference/consensus_history.csv
                                                       refreshes data/raw/ohlcv/{LSIP,TAPG}.csv (git-ignored)
Source: Yahoo Finance (S-002 prices; S-036 S&P consensus via Yahoo). Field definitions are vendor-defined.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from itmg_market_snapshot import FIELDS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
PEERS = ["LSIP", "TAPG", "AALI", "SSMS", "DSNG", "SIMP", "SGRO", "BWPT", "STAA", "TBLA"]
FOCUS = ("LSIP", "TAPG")


def main() -> dict:
    import yfinance as yf
    today = str(date.today())
    rows, cons = [], []
    snap = {"retrieved": today, "source": "Yahoo Finance quote/financial summary (S-002) and S&P consensus via Yahoo (S-036)"}
    for t in PEERS:
        tk = yf.Ticker(f"{t}.JK")
        try:
            info = tk.info
        except Exception as exc:  # noqa: BLE001
            rows.append({"ticker": t, "error": str(exc)[:60]}); continue
        r = {"ticker": t, "name": info.get("longName")} | {f: info.get(f) for f in FIELDS}
        rows.append(r)
        try:
            e = tk.earnings_estimate
            for per, lab in (("0y", "FY26"), ("+1y", "FY27")):
                if e is not None and per in e.index:
                    cons.append({"retrieved": today, "ticker": t, "fy": lab, "eps_avg": e.loc[per, "avg"], "eps_low": e.loc[per, "low"],
                                 "eps_high": e.loc[per, "high"], "n_analysts": e.loc[per, "numberOfAnalysts"],
                                 "year_ago_eps": e.loc[per, "yearAgoEps"]})
        except Exception:  # noqa: BLE001
            pass
        if t in FOCUS:
            k = t.lower()
            snap[f"{k}_info"] = r
            try:
                snap[f"{k}_price_targets"] = {a: (float(v) if v is not None else None) for a, v in tk.analyst_price_targets.items()}
            except Exception as exc:  # noqa: BLE001
                snap[f"{k}_price_targets"] = f"unavailable: {exc}"
            try:
                snap[f"{k}_recommendations"] = tk.recommendations.to_dict("records")
            except Exception:  # noqa: BLE001
                snap[f"{k}_recommendations"] = None
            h = tk.history(period="max", auto_adjust=False)
            h.index = h.index.tz_localize(None)
            h.to_csv(ROOT / "data" / "raw" / "ohlcv" / f"{t}_yf_full.csv")
            snap[f"{k}_last_close"] = {"date": str(h.index[-1].date()), "close": float(h.Close.iloc[-1])}
            snap[f"{k}_dividends_idr"] = {str(d.date()): float(v) for d, v in tk.dividends.items()}
    pd.DataFrame(rows).to_csv(REF / "research" / "palm_peers_snapshot.csv", index=False)
    C = pd.DataFrame(cons)
    snap["consensus"] = C.to_dict("records")
    (REF / "research" / "LSIP_market_snapshot.json").write_text(json.dumps(snap, indent=1, default=str), encoding="utf-8")
    if len(C):
        from tapg_monitor import append
        append(REF / "consensus_history.csv", C.assign(source="S&P via Yahoo (S-036)"), ["retrieved", "ticker", "fy"])
    return snap


if __name__ == "__main__":
    s = main()
    print(json.dumps({k: v for k, v in s.items() if not k.endswith("dividends_idr")}, indent=1, default=str)[:6000])
    print(pd.read_csv(REF / "research" / "palm_peers_snapshot.csv")[["ticker", "currentPrice", "marketCap", "trailingPE", "forwardPE",
                                                                       "enterpriseToEbitda", "dividendYield", "priceToBook", "totalCash"]].to_string())
