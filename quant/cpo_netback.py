"""CPO export-parity netback after Indonesian export levy and duty (priority E).

netback_ref  = HRef - levy - duty                (USD/t; regulatory reference basis)
netback_wb   = World Bank palm oil price - levy - duty   (USD/t; market-price basis; WB is
               a CIF Malaysia/Rotterdam-type monthly average, so this is an INDEX of export
               parity, not a mill-gate price: freight and basis are ignored)
charge_relief_at_constant_price = change in (levy + duty) month on month
Domestic tender prices (KPBN via S-023, secondary, Aug-Nov 2026 only) are summarised for
comparison.

Output: data/reference/research/cpo_netback_monthly.csv
Usage:  python -I -X utf8 quant/cpo_netback.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"


def main() -> int:
    ld = pd.read_csv(REF / "cpo_levy_duty_monthly.csv").set_index("month")
    mac = pd.read_csv(REF / "macro_monthly.csv", index_col=0)
    d = ld[["hrf_usd_t", "levy_usd_t", "duty_usd_t", "total_usd_t"]].join(
        mac[["palm_oil_usd_t", "usdidr_month_avg"]], how="left")
    d["netback_ref_usd_t"] = d.hrf_usd_t - d.total_usd_t
    d["netback_wb_usd_t"] = d.palm_oil_usd_t - d.total_usd_t
    d["netback_wb_idr_kg"] = d.netback_wb_usd_t * d.usdidr_month_avg / 1000
    d["charge_change_usd_t"] = d.total_usd_t.diff()
    d["hrf_change_usd_t"] = d.hrf_usd_t.diff()
    d["netback_ref_change_usd_t"] = d.netback_ref_usd_t.diff()
    # KPBN tenders (secondary, S-023 snapshot)
    snap = ROOT / "data" / "raw" / "macro" / "infokomoditas_prices_snapshot_2026-11-24.json"
    if snap.exists():
        obs = [o for o in json.load(open(snap, encoding="utf-8"))["observations"]
               if o["commodity"] == "cpo" and "KPBN" in (o.get("source_name") or "") and o.get("currency") == "IDR"]
        k = pd.DataFrame(obs)[["observed_at", "price"]].drop_duplicates("observed_at")
        k["month"] = k.observed_at.str[:7]
        km = k.groupby("month").price.agg(["mean", "count"]).rename(columns={"mean": "kpbn_tender_idr_kg_avg", "count": "kpbn_obs"})
        d = d.join(km, how="left")
    d.to_csv(REF / "research" / "cpo_netback_monthly.csv", float_format="%.2f")
    print(d.loc["2026-05":].round(1).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
