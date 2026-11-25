"""R1 point-in-time audit (Phase XV). Runs BEFORE any R1 return is computed; it touches prices only to check
data integrity (corporate actions, stale/suspended days), never strategy performance.

    python -I -X utf8 quant/dr_r1_audit.py   -> data/reference/research/DR_R1_pit_audit.json

Checks
 1. CPO publication: for each archived CMO vintage, the latest palm-oil month present and the capture date
    (evidence that month t-1 is published well before the end of month t), plus revisions across vintages.
 2. Signal formation / execution dates: the last IHSG trading day of each month (signal date = execution close).
 3. Universe: PIT membership dates coincide with those month-ends and use only data up to that date.
 4. Corporate actions: Yahoo 'Adj Close' vs 'Close' factor changes (dividends) and daily moves beyond the IDX
    auto-rejection band (possible splits / data errors).
 5. Suspended / stale members: zero-volume days of basket members during each holding month.
 6. Survivorship: listings without price history.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from itmg_prospective_run import read_series  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
RAW = ROOT / "data" / "raw"


def ohlcv(t: str) -> pd.DataFrame:
    d = pd.read_csv(RAW / "ohlcv" / f"{t}.csv", index_col=0, parse_dates=True)
    return d.apply(pd.to_numeric, errors="coerce")


def main() -> dict:
    out: dict = {}
    # 1. CPO vintages
    vint = {}
    for f in sorted((RAW / "macro" / "cmo_vintages").glob("CMO_*.xlsx")):
        s = read_series(f, "Palm oil")
        stamp = f.stem.split("_")[-1].replace("origin", "").strip("_")
        vint[stamp] = s
    cap = []
    for k, s in vint.items():
        ts = pd.Timestamp(k.replace("T", "").replace("Z", "")[:14])
        last = s.index[-1]
        cap.append({"captured_utc": str(ts), "latest_month": str(last),
                    "days_after_month_end": int((ts - last.to_timestamp(how="end")).days)})
    base = list(vint.values())[-1]
    rev = []
    for k, s in vint.items():
        c = pd.concat([s, base], axis=1).dropna()
        c = c[c.index >= pd.Period("2015-12", "M")]
        rev.append(float((c.iloc[:, 0] - c.iloc[:, 1]).abs().max()))
    out["cpo_publication"] = {"vintages": cap, "max_abs_revision_usd_t_since_2015_12": max(rev),
                              "rule": "signal for holding month t+1 uses CPO(t-1)/CPO(t-2); month t-1 must be published before the last trading day of month t",
                              "evidence": "all archived vintages show month m-1 present 9-15 days after its end (2026 only); pre-2026 release dates not archived in repo"}
    # 2./3. dates
    ihsg = ohlcv("IHSG")
    me = ihsg.index.to_series().groupby(ihsg.index.to_period("M")).max()
    pit = pd.read_csv(REF / "pit_universe_monthly.csv", parse_dates=["date"])
    pdates = set(pit.date.unique())
    out["dates"] = {"signal_and_execution": "close of the last IHSG trading day of month t (signal inputs published >= ~2 weeks earlier)",
                    "pit_dates_equal_month_ends": bool(pdates <= set(me.values)),
                    "pit_rule": "membership at t uses seasoning >= 60 sessions, trading in last 20 sessions, 63-session median traded value up to t (build_universe.py)"}
    # 4./5. corporate actions and stale days
    core = pit[pit.liquidity_band == "core_liquidity"]
    names = sorted(core.ticker.unique())
    ca, stale = [], []
    for t in names:
        d = ohlcv(t)
        f = (d["Adj Close"] / d["Close"]).dropna()
        jumps = f.pct_change().abs()
        r = d["Adj Close"].pct_change()
        big = r[r.abs() > 0.35]
        ca.append({"ticker": t, "dividend_like_factor_changes": int((jumps > 0.002).sum()),
                   "moves_beyond_35pct": {str(k.date()): round(float(v), 3) for k, v in big.items()}})
        for dt, g in core[core.ticker == t].groupby("date"):
            nxt = me[me > dt]
            if nxt.empty:
                continue
            w = d.loc[(d.index > dt) & (d.index <= nxt.iloc[0])]
            z = int((w["Volume"].fillna(0) <= 0).sum())
            if z:
                stale.append({"ticker": t, "formation": str(dt.date()), "zero_volume_days_in_holding_month": z, "sessions": int(len(w))})
    out["corporate_actions"] = {"price_field": "Yahoo 'Adj Close' (split- and dividend-adjusted, gross of the 10% dividend tax)",
                                "per_ticker": ca}
    out["stale_members"] = {"count_member_months_with_zero_volume_days": len(stale),
                            "member_months_total": int(len(core)), "cases": stale,
                            "treatment": "a zero-volume day is a 0% return at the last price (benchmarks.py); exit at a stale price may be non-executable"}
    lst = pd.read_csv(REF / "listings.csv")
    nop = [t for t in lst.ticker if not (RAW / "ohlcv" / f"{t}.csv").exists()]
    out["survivorship"] = {"listings_without_prices": nop,
                           "notes": {r.ticker: r.status_note for r in lst.itertuples() if r.ticker in nop},
                           "unknown_unknowns": "the candidate list was compiled in 2026; palm names delisted before 2015 or absent from Yahoo would be missing entirely",
                           "palm_exposure_unverified_members": sorted(set(core.ticker) & set(lst[lst.palm_exposure_status.str.contains('unverified|changed', case=False, na=False) | lst.status_note.str.contains('unverified|changed', case=False, na=False)].ticker))}
    out["ihsg_total_return"] = "not available: ^JKSE is a price index (Adj Close = Close); IHSG comparisons are price-only"
    (REF / "research" / "DR_R1_pit_audit.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: (v if k != "corporate_actions" else "...") for k, v in o.items() if k != "stale_members"}, indent=1, default=str)[:4000])
    print("stale member-months:", o["stale_members"]["count_member_months_with_zero_volume_days"], "of", o["stale_members"]["member_months_total"])
    print([c for c in o["corporate_actions"]["per_ticker"] if c["moves_beyond_35pct"]])
