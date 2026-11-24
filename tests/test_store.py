"""Tests for the point-in-time store: provenance and look-ahead rules."""
import pandas as pd
import pytest

from palmquant.config import load_config
from palmquant.store import ValidationError, connect, ingest, table_counts, validate_frame


@pytest.fixture()
def con():
    c = connect(path=":memory:")
    yield c
    c.close()


def _prices(**overrides):
    row = {
        "ticker": "TAPG",
        "obs_date": "2026-11-20",
        "close": 1715.0,
        "published_at": "2026-11-20 16:15",
        "source_id": "S_IDX_PRICES",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_config_loads_and_has_sources():
    cfg = load_config()
    assert "S_IDX_PRICES" in cfg.source_ids
    assert "S_NOAA_CPC" in cfg.source_ids
    assert cfg.settings["project"]["study_end"]


def test_valid_row_is_ingested_and_logged(con):
    ingest(con, _prices(), "prices", "unit_test")
    counts = table_counts(con)
    assert counts["prices"] == 1
    assert counts["ingest_log"] == 1


def test_unknown_source_rejected():
    with pytest.raises(ValidationError, match="source register"):
        validate_frame(_prices(source_id="S_MADE_UP"), "prices")


def test_null_required_field_rejected():
    with pytest.raises(ValidationError, match="null"):
        validate_frame(_prices(close=None), "prices")


def test_published_before_period_rejected():
    # A quarterly figure cannot be public before the quarter ends.
    df = pd.DataFrame([{
        "ticker": "DSNG", "period_end": "2026-09-30", "item": "net_profit_parent",
        "value": 1.46e12, "published_at": "2026-09-15", "source_id": "S_IDX_FILINGS",
    }])
    with pytest.raises(ValidationError, match="look-ahead"):
        validate_frame(df, "fundamentals")


def test_published_after_study_end_rejected():
    with pytest.raises(ValidationError, match="after study_end"):
        validate_frame(_prices(obs_date="2026-11-30", published_at="2026-11-30 16:15"), "prices")


def test_rejected_ingest_is_logged_and_writes_nothing(con):
    with pytest.raises(ValidationError):
        ingest(con, _prices(source_id="S_MADE_UP"), "prices", "unit_test")
    assert table_counts(con)["prices"] == 0
    status = con.execute("SELECT status FROM ingest_log").fetchone()[0]
    assert status == "rejected"


def test_seed_policy_events_pass_validation():
    cfg = load_config()
    seed = pd.read_csv(cfg.path("seed_dir") / "policy_events.csv")
    validate_frame(seed, "events", cfg)
