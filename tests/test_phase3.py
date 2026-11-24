"""Phase III guards: reverse valuation arithmetic, real-time PIT validation, netback calibration."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "valuation"))
sys.path.insert(0, str(ROOT / "quant"))
import reverse_valuation as rv  # noqa: E402
import tapg_fy2027_model as fy27  # noqa: E402


def test_reverse_valuation_round_trip():
    e = rv.implied_e(0.12, 0.02, 0.9, mcap=1000.0)
    assert abs(e * 0.9 * 1.02 / (0.12 - 0.02) - 1000.0) < 1e-9


def test_validation_uses_original_publication_cutoff():
    e = pd.read_csv(ROOT / "data" / "reference" / "research" / "TAPG_validation_errors.csv")
    pit = e[e.pit_valid]
    # 2025 quarters were first public in 2025 but are held only from 2026 filings: never PIT-valid targets
    assert not pit.quarter.str.startswith("2025").any()
    assert set(pit.quarter) <= {"2026Q2", "2026Q3"}


def test_fy27_netback_reproduces_q3_2026_asp():
    asp, lv, dt = fy27.realised_asp(1148.33, 17846.3, date="2026-08-15")
    assert abs(asp - 15565) < 60  # calibration basis -53 IDR/kg on Q3 2026 inputs


def test_forecast_journal_is_append_only():
    j = pd.read_csv(ROOT / "data" / "reference" / "forecast_journal.csv")
    # Phase III entries (26) and both superseded Q4 bases must still be present
    assert len(j) >= 31  # 25 Phase III rows + restored superseded row + 5 Phase IV rows
    sup = j[j.status.fillna("").str.startswith("superseded")]
    assert set(sup.value_idr_bn.round(1)) >= {1341.2, 1267.8}
