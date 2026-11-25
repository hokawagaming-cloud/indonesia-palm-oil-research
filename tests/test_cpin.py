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


def test_v2_pit_corrections():
    q = pd.read_csv(R / "CPIN_segments_quarterly_v2.csv", parse_dates=["available_from", "deadline"]).set_index("period")
    # FY2023 (comparative vintage) only available from the FY2024 filing
    assert q.loc["2023Q4", "available_from"] >= pd.Timestamp("2025-03-18")
    # restated 2020 values only from the 2021 filings
    assert (q.loc[["2020Q1", "2020Q2", "2020Q3"], "available_from"] >= pd.Timestamp("2021-04-30")).all()
    # actual filings never later than 5 trading days after the deadline in this sample
    act = q[q.date_basis.str.startswith("actual")]
    assert ((act.available_from - act.deadline).dt.days <= 7).all() and len(act) >= 12


def test_predictor_timing_and_frozen_spec():
    import json
    pc = pd.read_csv(R / "CPIN_predictor_timing_check.csv")
    assert pc.ok.all()
    spec = json.loads((R / "CPIN_H2_frozen_spec.json").read_text(encoding="utf-8"))
    assert spec["parameters_frozen"] is True and len(spec["benchmarks"]) == 3
    assert abs(spec["a"] + 0.5593) < 1e-3 and spec["evaluation"]["final_n"] == 12


def test_v1_outputs_preserved():
    m = pd.read_csv(R / "CPIN_walkforward_metrics.csv")
    v = m[(m.target == "broiler") & (m.method == "VERDICT")].iloc[0]
    assert v.n == 20 and abs(v.mae_ratio - 1.216) < 0.001
