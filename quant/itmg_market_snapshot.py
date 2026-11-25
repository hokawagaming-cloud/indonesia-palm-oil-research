"""ITMG market data and consensus snapshot (Phase XVI). Dated forward snapshot only; no historical consensus is
reconstructed (none exists in this repository before 2026-11-24).

    python -I -X utf8 quant/itmg_market_snapshot.py  -> data/reference/research/ITMG_market_snapshot.json
                                                      data/reference/research/coal_peers_snapshot.csv
                                                      appends ITMG/peers rows to data/reference/consensus_history.csv
Source: Yahoo Finance (S-002 prices; S-036 S&P consensus via Yahoo). Yahoo field definitions are vendor-defined;
currency of each field is recorded as reported (financialCurrency vs currency).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
PEERS = ["ITMG", "PTBA", "AADI", "ADRO", "BSSR", "HRUM", "INDY", "BUMI", "ABMM", "GEMS"]
FIELDS = ["currentPrice", "previousClose", "marketCap", "sharesOutstanding", "impliedSharesOutstanding", "currency", "financialCurrency",
          "trailingPE", "forwardPE", "priceToBook", "enterpriseValue", "enterpriseToEbitda", "enterpriseToRevenue", "ebitda",
          "totalRevenue", "netIncomeToCommon", "trailingEps", "forwardEps", "dividendYield", "trailingAnnualDividendYield",
          "dividendRate", "payoutRatio", "totalCash", "totalDebt", "returnOnEquity", "beta", "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
          "targetMeanPrice", "targetMedianPrice", "targetHighPrice", "targetLowPrice", "numberOfAnalystOpinions", "recommendationKey"]


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
            e, rv = tk.earnings_estimate, tk.revenue_estimate
            for per, lab in (("0y", "FY26"), ("+1y", "FY27")):
                if e is not None and per in e.index:
                    cons.append({"retrieved": today, "ticker": t, "fy": lab, "eps_avg": e.loc[per, "avg"], "eps_low": e.loc[per, "low"],
                                 "eps_high": e.loc[per, "high"], "n_analysts": e.loc[per, "numberOfAnalysts"], "year_ago_eps": e.loc[per, "yearAgoEps"],
                                 "rev_avg": rv.loc[per, "avg"] if rv is not None and per in rv.index else None,
                                 "rev_n": rv.loc[per, "numberOfAnalysts"] if rv is not None and per in rv.index else None})
        except Exception:  # noqa: BLE001
            pass
        if t == "ITMG":
            snap["itmg_info"] = r
            try:
                snap["itmg_price_targets"] = {k: (float(v) if v is not None else None) for k, v in tk.analyst_price_targets.items()}
            except Exception as exc:  # noqa: BLE001
                snap["itmg_price_targets"] = f"unavailable: {exc}"
            try:
                snap["itmg_recommendations"] = tk.recommendations.to_dict("records")
            except Exception:  # noqa: BLE001
                snap["itmg_recommendations"] = None
            h = tk.history(period="max", auto_adjust=False)
            h.index = h.index.tz_localize(None)
            h.to_csv(ROOT / "data" / "raw" / "ohlcv" / "ITMG.csv")
            snap["itmg_last_close"] = {"date": str(h.index[-1].date()), "close": float(h.Close.iloc[-1])}
            snap["itmg_dividends_idr"] = {str(k.date()): float(v) for k, v in tk.dividends.items()}
    pd.DataFrame(rows).to_csv(REF / "research" / "coal_peers_snapshot.csv", index=False)
    C = pd.DataFrame(cons)
    snap["consensus"] = C.to_dict("records")
    (REF / "research" / "ITMG_market_snapshot.json").write_text(json.dumps(snap, indent=1, default=str), encoding="utf-8")
    if len(C):
        from tapg_monitor import append
        add = C.drop(columns=["rev_avg", "rev_n"]).assign(source="S&P via Yahoo (S-036)")
        append(REF / "consensus_history.csv", add, ["retrieved", "ticker", "fy"])
    return snap


if __name__ == "__main__":
    s = main()
    print(json.dumps({k: v for k, v in s.items() if k not in ("itmg_dividends_idr",)}, indent=1, default=str)[:5000])
    print(pd.read_csv(REF / "research" / "coal_peers_snapshot.csv")[["ticker", "currentPrice", "marketCap", "currency", "financialCurrency", "trailingPE", "forwardPE", "enterpriseToEbitda", "dividendYield", "priceToBook"]].to_string())
