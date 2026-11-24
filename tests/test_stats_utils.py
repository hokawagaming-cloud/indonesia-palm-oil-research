import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
from stats_utils import drawdowns, lagged_corr, ols_nw  # noqa: E402


def test_ols_recovers_coefficients():
    rng = np.random.default_rng(0)
    x = pd.Series(rng.normal(size=500), name="x")
    y = 0.5 + 2.0 * x + rng.normal(scale=0.1, size=500)
    r = ols_nw(pd.Series(y), x.to_frame())
    assert abs(r.loc["x", "coef"] - 2.0) < 0.02 and abs(r.loc["const", "coef"] - 0.5) < 0.02
    assert r.attrs["r2"] > 0.99


def test_drawdown_depth_and_recovery():
    lvl = pd.Series([100, 120, 90, 60, 130, 125], index=pd.date_range("2020-01-01", periods=6))
    dd = drawdowns(lvl)
    assert abs(dd.loc[0, "depth"] - (60 / 120 - 1)) < 1e-12
    assert dd.loc[0, "recovery"] == lvl.index[4]


def test_lagged_corr_detects_lead():
    rng = np.random.default_rng(1)
    x = pd.Series(rng.normal(size=300))
    y = x.shift(1) + rng.normal(scale=0.01, size=300)
    t = lagged_corr(x, y, lags=[0, 1])
    assert t.set_index("lag_k").loc[1, "corr"] > 0.99
