"""Indonesian CPO export levy (pungutan ekspor, BPDP) and export duty (bea keluar).

Regimes come from primary regulation texts (PMK) transcribed into
  data/reference/levy_regimes.csv  and  data/reference/duty_regimes.csv
and reference prices (HRef, Kemendag) from data/reference/cpo_reference_prices.csv.
Method and caveats: research/macro/2026-11-24_levy_duty_reconstruction.md

Band convention: band k applies when ref_price_gt_usd < price <= ref_price_le_usd (an
empty bound means unbounded). Regulations phrase bands as 'lebih dari X s.d. Y'
(upper-inclusive), with two near-boundary exceptions documented in the CSV notes.
Rows marked SCHEDULED_ONLY (tables superseded before taking effect) are ignored.

Functions
  levy_usd_t(date, ref_price, product="CPO") -> (value USD/t, regime_id)
  duty_usd_t(date, ref_price, product="CPO") -> (value USD/t, regime_id)
Builder
  python -I quant/levy_duty.py  -> data/reference/cpo_levy_duty_monthly.csv
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"


@lru_cache(maxsize=None)
def _table(kind: str) -> pd.DataFrame:
    df = pd.read_csv(REF / f"{kind}_regimes.csv", dtype={"effective_to": str})
    df = df[~df["verification_note"].fillna("").str.contains("SCHEDULED_ONLY")].copy()
    df["eff_from"] = pd.to_datetime(df["effective_from"])
    df["eff_to"] = pd.to_datetime(df["effective_to"].replace("", np.nan)).fillna(pd.Timestamp("2100-01-01"))
    df["lo"] = df["ref_price_gt_usd"].astype(float).fillna(-np.inf)
    df["hi"] = df["ref_price_le_usd"].astype(float).fillna(np.inf)
    return df


def _lookup(kind: str, date, ref_price: float | None, product: str):
    d = pd.Timestamp(date)
    t = _table(kind)
    t = t[(t["product"] == product) & (t.eff_from <= d) & (t.eff_to >= d)]
    if t.empty:
        return np.nan, None, "no regime"
    rid = t["regime_id"].iloc[0]
    t = t[t.regime_id == rid]
    if len(t) == 1 and np.isinf(t.lo.iloc[0]) and np.isinf(t.hi.iloc[0]):
        row = t.iloc[0]
    else:
        if ref_price is None or pd.isna(ref_price):
            return np.nan, rid, "reference price missing"
        m = t[(t.lo < ref_price) & (ref_price <= t.hi)]
        if m.empty:
            return np.nan, rid, "price outside bands"
        row = m.iloc[0]
    rate = float(row["rate"] if kind == "levy" else row["duty_usd_t"])
    if kind == "levy" and row["basis"] == "pct":
        if ref_price is None or pd.isna(ref_price):
            return np.nan, rid, "reference price missing"
        return round(rate / 100 * ref_price, 2), rid, f"{rate}% of HRef"
    return rate, rid, "USD/t"


def levy_usd_t(date, ref_price: float | None, product: str = "CPO"):
    v, rid, _ = _lookup("levy", date, ref_price, product)
    return v, rid


def duty_usd_t(date, ref_price: float | None, product: str = "CPO"):
    v, rid, _ = _lookup("duty", date, ref_price, product)
    return v, rid


def build_monthly(start: str = "2015-01", end: str = "2026-11") -> pd.DataFrame:
    """Monthly table evaluated on the 15th of each month, using the reference price
    period that covers that day. Months with two reference-price periods (2022-2023
    semi-monthly HRef) take the period covering the 15th; all periods are kept in
    cpo_reference_prices.csv."""
    rp = pd.read_csv(REF / "cpo_reference_prices.csv", parse_dates=["period_start", "period_end"])
    rows = []
    for m in pd.period_range(start, end, freq="M"):
        day = pd.Timestamp(m.year, m.month, 15)
        r = rp[(rp.period_start <= day) & (rp.period_end >= day)]
        price = float(r["hrf_usd_t"].iloc[0]) if len(r) else np.nan
        pcls = r["source_class"].iloc[0] if len(r) else "MISSING"
        lv, lrid, lnote = _lookup("levy", day, price, "CPO")
        dv, drid, dnote = _lookup("duty", day, price, "CPO")
        rows.append({"month": str(m), "eval_date": day.date(), "hrf_usd_t": price, "hrf_source_class": pcls,
                     "hrf_regulation": r["regulation"].iloc[0] if len(r) else "",
                     "levy_usd_t": lv, "levy_regime": lrid, "levy_basis": lnote,
                     "duty_usd_t": dv, "duty_regime": drid, "duty_basis": dnote,
                     "total_usd_t": lv + dv if pd.notna(lv) and pd.notna(dv) else np.nan,
                     "special_episode": _episode(day)})
    out = pd.DataFrame(rows)
    out.to_csv(REF / "cpo_levy_duty_monthly.csv", index=False)
    return out


def _episode(day: pd.Timestamp) -> str:
    # Export ban on CPO and derivatives (Permendag 22/2022, revoked by Permendag 30/2022):
    # 28 Apr - 23 May 2022. Dates from secondary reporting; not used in calculations.
    if pd.Timestamp("2022-04-28") <= day <= pd.Timestamp("2022-05-23"):
        return "export ban 28 Apr-23 May 2022 (secondary, unverified)"
    if pd.Timestamp("2022-07-15") <= day <= pd.Timestamp("2022-10-31"):
        return "levy suspended (PMK 115/2022, 130/2022)"
    return ""


if __name__ == "__main__":
    m = build_monthly()
    cov = m["hrf_usd_t"].notna().mean()
    print(m.tail(14).to_string(index=False))
    print(f"months {len(m)}, with reference price {m.hrf_usd_t.notna().sum()} ({cov:.0%}), "
          f"levy computed {m.levy_usd_t.notna().sum()}, duty computed {m.duty_usd_t.notna().sum()}")
