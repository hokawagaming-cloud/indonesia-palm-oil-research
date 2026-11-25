"""Engineering tests for the bank monthly-report inventory (code correctness, not forecasting skill)."""
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parents[1] / "data" / "reference" / "research"


def test_inventory_coverage_and_regime():
    d = pd.read_csv(R / "bank_monthly_inventory.csv")
    d["y"] = d.month.str[:4].astype(int)
    assert set(d.bank) == {"BBCA", "BBRI", "BMRI", "BBNI"}
    assert not d.duplicated(["bank", "month"]).any()
    for b in ("BBCA", "BBRI", "BBNI"):
        n2018 = len(d[(d.bank == b) & (d.y == 2018)])
        assert n2018 >= 11                                       # all months published pre-POJK 37/2019
        recent = d[(d.bank == b) & (d.y.between(2022, 2025))]
        assert not recent.quarter_end_month.any()                # quarter-end months only via quarterly reports
    assert (d[d.bank == "BMRI"].groupby("y").size().loc[2018:2025] == 12).all()


def test_lags_are_positive_and_plausible():
    d = pd.read_csv(R / "bank_monthly_inventory.csv").dropna(subset=["lag_days"])
    assert (d.lag_days >= -1).all() and (d.lag_days <= 90).all()
    assert d[d.bank == "BBNI"].empty                             # BBNI undated: must not be given dates
