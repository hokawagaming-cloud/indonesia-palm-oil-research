"""Engineering tests for Phase XI artefacts (correctness/consistency, not forecasting skill)."""
import json
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parents[1] / "data" / "reference" / "research"


def test_audit_findings_recorded_and_originals_kept():
    a = json.loads((R / "MVP_B1_audit.json").read_text(encoding="utf-8"))
    assert a["pbt_substitution"]["documents_using_pbt"] == a["pbt_substitution"]["reconciled_within_0.1pct"]
    s = pd.read_csv(R / "MVP_B1_audit_impairment_signs.csv")
    assert set(s["class"]) <= {"sign convention", "possible genuine reversal"}
    orig = json.loads((R / "MVP_B1_results.json").read_text(encoding="utf-8"))
    assert {r["classification"] for r in orig["results"]} == {"NO-GO"}       # original preserved
    corr = json.loads((R / "MVP_B1_results_corrected.json").read_text(encoding="utf-8"))
    assert not any(v["pass_rule"] for v in corr.values())


def test_corrected_extract_only_flips_reversals():
    m1 = pd.read_csv(R / "bank_monthly_extract.csv"); m2 = pd.read_csv(R / "bank_monthly_extract_v2.csv")
    diff = m1.merge(m2, on=["bank", "period"], suffixes=("_a", "_b"))
    changed = diff[diff.bo_impairment_a != diff.bo_impairment_b]
    assert len(changed) == 3 and (changed.bank == "BBCA").all() and (changed.bo_impairment_b < 0).all()


def test_b2_frozen_spec():
    s = json.loads((R / "MVP_B2_preregistration.json").read_text(encoding="utf-8"))
    assert "1.5 x NII_BO2" in s["forecast_formula"] and s["pooling"].startswith("none")
    assert "n = 12" in s["final_test"] and "0.85" in s["final_test"] and "2026Q4" in s["evaluation_window"]


def test_coal_feasibility_verdicts():
    c = pd.read_csv(R / "coal_feasibility.csv")
    assert c.verdict.str.match(r"^(AVAILABLE|PARTIAL|NOT AVAILABLE|NOT VERIFIED)").all()
    assert (c[c.dataset.str.contains("Indonesian Coal Index")].verdict.str.startswith("NOT AVAILABLE")).all()
