"""Engineering tests for ITMG-C1 (code correctness and PIT discipline; not evidence of forecasting skill)."""
import json
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parents[1] / "data" / "reference" / "research"


def test_manifest_hashes_and_coverage():
    m = pd.read_csv(R / "ITMG_document_manifest.csv")
    pres = m[(m.kind == "presentation") & m.file.notna()]
    assert len(pres) == 35 and pres.sha256.str.fullmatch(r"[0-9a-f]{64}").all()


def test_asp_series_complete_and_plausible():
    e = pd.read_csv(R / "ITMG_quarterly_raw_extract.csv")
    assert e.asp_usd_t.notna().sum() == 35
    assert e.asp_usd_t.between(40, 260).all()
    # first-reported text value preferred over rounded chart label
    assert abs(e.set_index("period").loc["2020Q3", "asp_usd_t"] - 48.8) < 1e-9


def test_origin_precedes_release_and_forecasts_use_prior_quarter_only():
    f = pd.read_csv(R / "ITMG_filing_dates.csv")
    assert (f.days_after_qend > 10).all()
    fc = pd.read_csv(R / "ITMG_C1_forecasts.csv")
    e = pd.read_csv(R / "ITMG_quarterly_raw_extract.csv").set_index("period")
    for r in fc.itertuples():
        prev = str(pd.Period(r.q, "Q") - 1)
        assert abs(r.B1_last - e.loc[prev, "asp_usd_t"]) < 1e-6


def test_results_follow_preregistered_rule():
    spec = json.loads((R / "ITMG_C1_preregistration.json").read_text(encoding="utf-8"))
    res = json.loads((R / "ITMG_C1_results.json").read_text(encoding="utf-8"))
    assert "0.85" in spec["pass_rule"] and res["n"] >= 16
    for m, v in res["models"].items():
        assert v["pass"] == (res["n"] >= 16 and v["MAE"] <= 0.85 * res["strongest_MAE"] and v["p_holm"] <= 0.05)
    assert res["classification"] in {"GO", "CONDITIONAL GO", "NO-GO"}
