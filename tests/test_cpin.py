"""Engineering tests for the CPIN segment dataset and walk-forward (they test code, not skill)."""
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parents[1] / "data" / "reference" / "research"


def test_segments_reconcile_to_consolidated():
    c = pd.read_csv(R / "CPIN_segments_ytd.csv")
    assert c.chk_sales.abs().max() <= 2 and c.chk_result.abs().max() <= 2   # IDR million rounding


def test_standalone_quarters_sum_to_full_year():
    c = pd.read_csv(R / "CPIN_segments_ytd.csv")
    q = pd.read_csv(R / "CPIN_segments_quarterly.csv")
    for basis, y in (("old", 2019), ("new", 2022), ("new", 2024)):
        fy = c[(c.basis == basis) & (c.period == f"{y}Q4")].sales_consolidated.iloc[0]
        qs = q[q.period.str.startswith(str(y))]
        assert len(qs) == 4 and (qs.basis == basis).all()
        assert abs(qs.sales_consolidated.sum() - fy) < 5


def test_walkforward_is_point_in_time():
    wf = pd.read_csv(R / "CPIN_walkforward_forecasts.csv")
    q = pd.read_csv(R / "CPIN_segments_quarterly.csv", parse_dates=["available_from"]).set_index("period")
    for r in wf.itertuples():
        assert pd.Timestamp(r.forecast_date) < q.loc[r.period, "available_from"]
        assert r.n_train >= 12


def test_kill_rule_recorded():
    m = pd.read_csv(R / "CPIN_walkforward_metrics.csv")
    v = m[(m.target == "broiler") & (m.method == "VERDICT")].iloc[0]
    assert v["pass"] in (False, "False") and v.n >= 16
