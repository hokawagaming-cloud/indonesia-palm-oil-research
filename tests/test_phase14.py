"""Phase XIV: prospective scripts and direct-return pre-registration (engineering tests, no network)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "quant"))
import itmg_prospective_run as pr  # noqa: E402
import itmg_c1 as c1  # noqa: E402

RES = ROOT / "data" / "reference" / "research"


def test_interval_brackets_point():
    lo, hi = pr.interval("ITMG_C1_forecasts.csv", "M2_distributed_lag", 100.0)
    assert lo < 100.0 < hi


def test_c1_forecast_primary_and_fallback_use_only_past_asp():
    N = c1.newcastle()
    q = pd.Period("2026Q3", "Q")
    a = pr.c1_forecast(q, N, two_month=False)
    b = pr.c1_forecast(q, N, two_month=True)
    for f in (a, b):
        assert np.isfinite(f["M2_distributed_lag"]) and 30 < f["M2_distributed_lag"] < 400
    assert c1.newcastle is not None  # monkeypatch restored
    assert a["M2_distributed_lag"] != b["M2_distributed_lag"]


def test_dr_preregistration_is_small_and_design_only():
    d = json.loads((RES / "DR_preregistration.json").read_text(encoding="utf-8"))
    assert len(d["hypotheses"]) <= 4
    assert "No return backtest" in d["status"]
    assert "Holm" in d["common_rules"]["inference"]
    for h in d["hypotheses"].values():
        assert "primary_benchmark" in h and "mechanism" in h


def test_journal_is_append_only_for_itmg_pending_rows():
    J = pd.read_csv(ROOT / "data" / "reference" / "forecast_journal.csv")
    pend = J[J.target.str.contains("ITMG 2026Q4", na=False) & J.status.str.startswith("pending", na=False)]
    assert len(pend) == 4
