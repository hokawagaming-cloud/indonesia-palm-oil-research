"""Unit tests for benchmark construction. Run: python -I -m pytest tests -q"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
from benchmarks import ew_buy_and_hold  # noqa: E402


def test_equal_weight_two_assets_one_period():
    idx = pd.to_datetime(["2020-01-31", "2020-02-03", "2020-02-04"])
    r = pd.DataFrame({"A": [0.0, 0.10, 0.0], "B": [0.0, -0.10, 0.10]}, index=idx)
    out = ew_buy_and_hold(r, {pd.Timestamp("2020-01-31"): ["A", "B"]})
    # day 1: (1.1 + 0.9)/2 = 1.0 -> 0%; day 2: (1.1 + 0.99)/2 = 1.045 -> +4.5%
    assert np.isnan(out.iloc[0])
    assert abs(out.iloc[1] - 0.0) < 1e-12
    assert abs(out.iloc[2] - 0.045) < 1e-12


def test_no_lookahead_returns_start_after_rebalance_date():
    idx = pd.to_datetime(["2020-01-30", "2020-01-31", "2020-02-03"])
    r = pd.DataFrame({"A": [0.5, 0.5, 0.01]}, index=idx)
    out = ew_buy_and_hold(r, {pd.Timestamp("2020-01-31"): ["A"]})
    assert out.loc["2020-01-31":"2020-01-31"].isna().all()
    assert abs(out.loc["2020-02-03"] - 0.01) < 1e-12


def test_membership_change_resets_weights():
    idx = pd.to_datetime(["2020-01-31", "2020-02-28", "2020-03-02"])
    r = pd.DataFrame({"A": [0, 0.2, 0.0], "B": [0, 0.0, 0.3]}, index=idx)
    m = {pd.Timestamp("2020-01-31"): ["A"], pd.Timestamp("2020-02-28"): ["B"]}
    out = ew_buy_and_hold(r, m)
    assert abs(out.loc["2020-02-28"] - 0.2) < 1e-12
    assert abs(out.loc["2020-03-02"] - 0.3) < 1e-12
