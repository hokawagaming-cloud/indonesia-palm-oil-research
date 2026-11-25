"""Engineering tests for MVP-B1 (code correctness and PIT discipline; not evidence of forecasting skill)."""
import json
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parents[1] / "data" / "reference" / "research"


def test_extraction_identities():
    c = pd.read_csv(R / "bank_extract_checks.csv")
    core = c[c.scope.isin(["monthly_bo", "quarterly"])]
    assert (core.nii_identity_ok == 1.0).all() and (core.np_lt_pbt_ok == 1.0).all()
    assert (core.missing_np == 0).all() and (core.missing_cons_owner == 0).all()


def test_scopes_kept_separate():
    q = pd.read_csv(R / "bank_quarterly_extract.csv")
    assert {"bo_net_profit", "cons_net_profit", "cons_np_owners"} <= set(q.columns)
    # consolidated NII must be >= bank-only NII in the same document for BBRI (large subsidiaries)
    b = q[q.bank == "BBRI"]
    assert (b.cons_nii >= b.bo_nii * 0.99).all()


def test_forecasts_point_in_time():
    f = pd.read_csv(R / "MVP_B1_forecasts_primary.csv", parse_dates=["origin"])
    m = pd.read_csv(R / "bank_monthly_extract.csv", parse_dates=["avail_verified"])
    ok = f[f.excluded.isna()]
    assert len(ok) >= 30
    for r in ok.itertuples():
        q = pd.Period(r.q, "Q"); m2 = (q.asfreq("M", "end") - 1).strftime("%Y-%m")
        av = m[(m.bank == r.bank) & (m.period == m2)].avail_verified.iloc[0]
        assert pd.Timestamp(r.origin) == av                      # origin = verified month-2 date


def test_spec_frozen_and_rules_applied():
    spec = json.loads((R / "MVP_B1_preregistration.json").read_text(encoding="utf-8"))
    assert spec["pooling"].startswith("none") and "0.85" in spec["pass_rule_T1"]
    res = json.loads((R / "MVP_B1_results.json").read_text(encoding="utf-8"))
    for r in res["results"]:
        if r["primary_T1_pass_rule"]:
            assert r["primary_T1_n"] >= 16 and r["primary_T1_model_value_improvement"] >= 0.15
    assert {r["classification"] for r in res["results"]} <= {"GO", "CONDITIONAL GO", "NO-GO"}
