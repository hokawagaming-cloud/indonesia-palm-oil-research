"""TAPG monitoring run (Phase V, workstream 1). Append-only, dated, reuses existing data.

Run after refreshing inputs:
    python -I -X utf8 quant/fetch_ohlcv.py        # prices (S-002)
    python -I -X utf8 quant/fetch_macro.py        # WB CPO, Brent, fertilisers, ONI (S-003/S-006)
    python -I -X utf8 quant/levy_duty.py          # levy/duty (add new HRef decrees first, S-035)
    python -I -X utf8 quant/cpo_netback.py
    python -I -X utf8 quant/tapg_monitor.py
Each run:
  * appends a consensus snapshot for TAPG, DSNG, STAA and the screen universe to
    data/reference/consensus_history.csv. This builds the consensus HISTORY needed for
    expectation-adjusted surprise studies; Yahoo shows only current and 7/30/60/90-day values.
  * appends one row to data/reference/tapg_monitor_log.csv with the triggers and indicators
  * recomputes TAPG expected return at the latest price (valuation/tapg_entry_and_tactical.py)
Nothing already in either log is ever modified.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
sys.path.insert(0, str(ROOT / "valuation"))
TRIGGER_PRICE = 1525.0  # D-024 (was 1,530 before forward-dividend update)
SHARES = 19852.54
UNIVERSE = ["TAPG", "DSNG", "STAA", "AALI", "LSIP", "SSMS", "SIMP", "BWPT", "TBLA", "NSSS", "MGRO", "GZCO", "ANJT", "SGRO", "SMAR", "CSRA", "PSGO",
            "BBCA", "BBRI", "BMRI", "BBNI"]  # Phase IX (D-033): forward consensus history for banking hypothesis B6


def consensus_snapshot(run_date: str) -> pd.DataFrame:
    import yfinance as yf
    rows = []
    for t in UNIVERSE:
        try:
            tk = yf.Ticker(f"{t}.JK")
            e, tr = tk.earnings_estimate, tk.eps_trend
            for per, lab in (("0y", "FY26"), ("+1y", "FY27")):
                if per in e.index and pd.notna(e.loc[per, "avg"]):
                    rows.append({"retrieved": run_date, "ticker": t, "fy": lab, "eps_avg": e.loc[per, "avg"],
                                 "eps_low": e.loc[per, "low"], "eps_high": e.loc[per, "high"],
                                 "n_analysts": e.loc[per, "numberOfAnalysts"], "year_ago_eps": e.loc[per, "yearAgoEps"],
                                 "eps_7d_ago": tr.loc[per, "7daysAgo"], "eps_30d_ago": tr.loc[per, "30daysAgo"],
                                 "eps_90d_ago": tr.loc[per, "90daysAgo"], "source": "S&P via Yahoo (S-036)"})
        except Exception as exc:  # no coverage or network
            rows.append({"retrieved": run_date, "ticker": t, "fy": None, "source": f"unavailable: {str(exc)[:40]}"})
    return pd.DataFrame(rows)


def append(path: Path, df: pd.DataFrame, key: list[str]) -> int:
    if path.exists():
        old = pd.read_csv(path)
        new = df.merge(old[key].drop_duplicates(), on=key, how="left", indicator=True)
        new = new[new["_merge"] == "left_only"].drop(columns="_merge")
        pd.concat([old, new], ignore_index=True).to_csv(path, index=False)
        return len(new)
    df.to_csv(path, index=False)
    return len(df)


def main() -> int:
    run_date = date.today().isoformat()
    cs = consensus_snapshot(run_date)
    n_cons = append(REF / "consensus_history.csv", cs, ["retrieved", "ticker", "fy"])

    px = pd.read_csv(ROOT / "data" / "raw" / "ohlcv" / "TAPG.csv", index_col=0, parse_dates=True)
    close = pd.to_numeric(px["Close"], errors="coerce").dropna()
    last_px, last_dt = float(close.iloc[-1]), close.index[-1].date().isoformat()
    nb = pd.read_csv(REF / "research" / "cpo_netback_monthly.csv", index_col=0)
    nb_last = nb.dropna(subset=["netback_ref_usd_t"]).iloc[-1]
    mac = pd.read_csv(REF / "macro_monthly.csv", index_col=0)
    fert = mac[["urea_usd_t", "dap_usd_t", "mop_usd_t"]].dropna().iloc[-1]
    fert_yoy = (mac[["urea_usd_t", "dap_usd_t", "mop_usd_t"]].dropna().pct_change(12).iloc[-1]).round(3)
    brent = pd.to_numeric(pd.read_csv(ROOT / "data" / "raw" / "ohlcv" / "BRENT.csv", index_col=0)["Close"], errors="coerce").dropna().iloc[-1]
    kpbn = None
    snap = ROOT / "data" / "raw" / "macro" / "infokomoditas_prices_snapshot_2026-11-24.json"
    if snap.exists():
        obs = [o for o in json.load(open(snap, encoding="utf-8"))["observations"] if o["commodity"] == "cpo" and "KPBN" in (o.get("source_name") or "")]
        if obs:
            o = max(obs, key=lambda x: x["observed_at"])
            kpbn = (o["observed_at"], o["price"])
    tc = cs[(cs.ticker == "TAPG") & cs.fy.notna()].set_index("fy")
    import tapg_entry_and_tactical as ent
    ent.PRICE = last_px
    s = ent.SCEN
    ev = sum(p * (ent.value_per_share(e) + d) for _, e, p, d in s)
    row = {"run_date": run_date, "price_date": last_dt, "tapg_price": last_px, "trigger_hit": last_px <= TRIGGER_PRICE,
           "cons_fy26_eps": tc.eps_avg.get("FY26"), "cons_fy26_30d_chg": (tc.eps_avg.get("FY26") / tc.eps_30d_ago.get("FY26") - 1) if "FY26" in tc.index else None,
           "cons_fy27_eps": tc.eps_avg.get("FY27"), "cons_fy27_30d_chg": (tc.eps_avg.get("FY27") / tc.eps_30d_ago.get("FY27") - 1) if "FY27" in tc.index else None,
           "implied_q4_np_bn": tc.eps_avg.get("FY26") * SHARES / 1000 - 3505.62 if "FY26" in tc.index else None,
           "netback_month": nb_last.name, "netback_ref_usd_t": nb_last.netback_ref_usd_t, "levy_plus_duty_usd_t": nb_last.total_usd_t,
           "kpbn_latest": f"{kpbn[0]} {kpbn[1]:,.0f}" if kpbn else None, "brent_usd": float(brent),
           "urea_usd_t": fert.urea_usd_t, "dap_usd_t": fert.dap_usd_t, "mop_usd_t": fert.mop_usd_t, "fert_yoy": json.dumps(fert_yoy.to_dict()),
           "expected_12m_value": ev, "expected_return": ev / last_px - 1,
           "pending_data": "Q4 ops/inventory (newsletter S-033); fertiliser application (FY26 FS); B50 review outcome; Dec HRef decree"}
    n_mon = append(REF / "tapg_monitor_log.csv", pd.DataFrame([row]), ["run_date", "price_date"])
    print(pd.Series(row).to_string())
    print(f"appended consensus rows: {n_cons}; monitor rows: {n_mon}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
