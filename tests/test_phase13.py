"""Engineering tests for Phase XIII artefacts (correctness and PIT discipline; not forecasting skill)."""
import json
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parents[1] / "data" / "reference" / "research"


def test_cmo_vintages_small_revisions():
    v = pd.read_csv(R / "CMO_newcastle_vintages.csv", index_col=0)
    cur = v["current_20261124"]
    assert (v.drop(columns="current_20261124").sub(cur, axis=0).abs().max() <= 0.1).all()


def test_implied_volume_reconciles_and_costs_complete():
    cov = json.loads((R / "ITMG_c2c3_coverage.json").read_text(encoding="utf-8"))
    assert cov["implied_volume_reconciliation"]["max_abs_pct_gap"] <= 0.02
    assert cov["fs_quarters_standalone"]["cost_of_revenue"] == 35
    o = pd.read_csv(R / "ITMG_ops_extract.csv")
    assert o.guid_value_mt.notna().all()


def test_preregistration_order_and_rules():
    s = json.loads((R / "ITMG_C2_C3_preregistration.json").read_text(encoding="utf-8"))
    assert "0.85" in s["common"]["pass_rule"] and "mine_rainfall" in s["common"]["data_scope_exclusions"]
    r = json.loads((R / "ITMG_C2_C3_results.json").read_text(encoding="utf-8"))
    for k in ("C2", "C3"):
        for m, v in r[k]["models"].items():
            assert v["pass"] == (r[k]["n"] >= 16 and v["improvement"] >= 0.15 - 1e-12 and v["p_holm"] <= 0.05)


def test_integrated_uses_benchmarks_for_failed_components():
    f = pd.read_csv(R / "ITMG_I1_forecasts.csv")
    res = json.loads((R / "ITMG_I1_results.json").read_text(encoding="utf-8"))
    assert res["n"] == len(f) >= 16
    pm = pd.read_csv(R / "programme_multiplicity_v2.csv", index_col=0)
    assert pm.loc["I1_integrated_GP", "p_holm_programme"] > 0.05      # => CONDITIONAL, not GO
