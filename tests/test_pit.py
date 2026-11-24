"""Regression tests against point-in-time leakage (audit finding A, D-014)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
sys.path.insert(0, str(ROOT / "quant"))
import pit_panel  # noqa: E402


def _v():
    return pd.read_csv(REF / "TAPG_pit_vintages.csv")


def test_value_never_available_before_its_own_document():
    v = _v()
    assert (pd.to_datetime(v.earliest_verified_availability) <= pd.to_datetime(v.vintage_available_from)).all()
    first = v.sort_values("vintage_available_from").groupby(["item", "reporting_period"]).head(1)
    assert (first.earliest_verified_availability == first.vintage_available_from).all()


def test_comparatives_not_dated_to_original_filing():
    v = _v()
    comp_only = v.groupby(["item", "reporting_period"]).filter(lambda g: not g.original_filing_in_hand.any())
    assert len(comp_only) > 0
    ok = pd.to_datetime(comp_only.earliest_verified_availability) >= pd.to_datetime(comp_only.vintage_available_from).groupby(
        [comp_only["item"], comp_only.reporting_period]).transform("min")
    assert ok.all()


def test_asof_returns_vintage_known_at_the_time():
    v = _v()
    assert np.isnan(pit_panel.asof(v, "finance_costs", "FY2022", "2023-01-01"))
    assert pit_panel.asof(v, "finance_costs", "FY2022", "2023-12-31") == -380151      # original AR2022
    assert pit_panel.asof(v, "finance_costs", "FY2022", "2024-03-13") == -380151      # strict: AR2023 PDF not yet public
    assert pit_panel.asof(v, "finance_costs", "FY2022", "2024-04-01") == -347594      # restated in AR2023 (AR filed 28 Mar 13:27)


def test_strict_never_earlier_than_lenient():
    v = _v()
    assert (pd.to_datetime(v.vintage_available_from) >= pd.to_datetime(v.vintage_available_from_lenient)).all()


def test_derived_quarters_not_available_before_inputs():
    q = pd.read_csv(REF / "TAPG_quarterly_derived.csv")
    pit = pd.read_csv(REF / "TAPG_pit_quarterly.csv").set_index(["item", "quarter"])["available_from"]
    for _, r in q.iterrows():
        assert pd.Timestamp(r.available_from) >= pd.Timestamp(pit[(r["item"], r.quarter)])
    r25 = q[(q["item"] == "revenue") & (q.quarter == "2025Q1")].iloc[0]
    assert pd.Timestamp(r25.available_from) >= pd.Timestamp("2026-04-28")  # value comes from the Q1 2026 filing


def test_quarterly_ops_not_before_first_seen_and_revision_flagged():
    o = pd.read_csv(REF / "TAPG_quarterly_ops.csv")
    assert (o.earliest_verified_availability == o.first_seen).all()
    imp = o[o["item"].str.endswith("_implied_by_9M")]
    assert len(imp) and (imp.revision_date == "2026-10-29").all()
    assert o.original_publication_date.isna().all()  # newsletters not in hand: never assumed


def test_available_from_after_period_end():
    q = pd.read_csv(REF / "TAPG_pit_quarterly.csv")
    end = pd.PeriodIndex(q.quarter.str[:4] + "Q" + q.quarter.str[-1], freq="Q").end_time.normalize()
    assert (pd.to_datetime(q.available_from) > end).all()
