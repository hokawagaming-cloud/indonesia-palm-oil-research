"""DuckDB point-in-time store.

Every table keeps two clocks:
  obs_date      the date the value refers to (trading day, quarter end, month);
  published_at  the timestamp from which the value was publicly available.

Rows are append-only. A revision or restatement is a new row with a later
published_at (a new vintage); point-in-time queries select the latest vintage
published at or before the decision time (see pit.py).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

from .config import Config, load_config

SCHEMA = {
    "prices": """
        ticker VARCHAR, obs_date DATE, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE,
        volume DOUBLE, value_traded DOUBLE, is_suspended BOOLEAN,
        published_at TIMESTAMP, published_at_estimated BOOLEAN,
        source_id VARCHAR, ingest_run VARCHAR""",
    "corporate_actions": """
        ticker VARCHAR, action_type VARCHAR, ex_date DATE, cash_amount DOUBLE, ratio DOUBLE,
        published_at TIMESTAMP, published_at_estimated BOOLEAN,
        source_id VARCHAR, url VARCHAR, ingest_run VARCHAR""",
    "fundamentals": """
        ticker VARCHAR, period_end DATE, period_type VARCHAR, item VARCHAR, value DOUBLE, unit VARCHAR,
        audit_status VARCHAR, published_at TIMESTAMP, published_at_estimated BOOLEAN,
        source_id VARCHAR, url VARCHAR, ingest_run VARCHAR""",
    "series": """
        series_id VARCHAR, obs_date DATE, value DOUBLE, unit VARCHAR,
        published_at TIMESTAMP, published_at_estimated BOOLEAN,
        source_id VARCHAR, url VARCHAR, ingest_run VARCHAR""",
    "events": """
        event_id VARCHAR, event_type VARCHAR, entity VARCHAR, announced_at TIMESTAMP, date_basis VARCHAR,
        effective_date DATE, status VARCHAR, description VARCHAR,
        source_id VARCHAR, url VARCHAR, ingest_run VARCHAR""",
    "universe_status": """
        ticker VARCHAR, status VARCHAR, start_date DATE, end_date DATE, value DOUBLE,
        announced_at TIMESTAMP, date_basis VARCHAR, source_id VARCHAR, url VARCHAR, ingest_run VARCHAR""",
    "ingest_log": """
        ingest_run VARCHAR, dataset VARCHAR, source_id VARCHAR, rows_in BIGINT, rows_written BIGINT,
        started_at TIMESTAMP, finished_at TIMESTAMP, status VARCHAR, message VARCHAR""",
}

REQUIRED = {
    "prices": ["ticker", "obs_date", "close", "published_at", "source_id"],
    "corporate_actions": ["ticker", "action_type", "ex_date", "published_at", "source_id"],
    "fundamentals": ["ticker", "period_end", "item", "value", "published_at", "source_id"],
    "series": ["series_id", "obs_date", "value", "published_at", "source_id"],
    "events": ["event_id", "event_type", "entity", "announced_at", "source_id"],
    "universe_status": ["ticker", "status", "start_date", "announced_at", "source_id"],
}


class ValidationError(ValueError):
    """Raised when a frame would violate a point-in-time or provenance rule."""


def connect(cfg: Config | None = None, path: str | Path | None = None) -> duckdb.DuckDBPyConnection:
    cfg = cfg or load_config()
    db_path = Path(path) if path is not None else cfg.path("duckdb_path")
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    for table, cols in SCHEMA.items():
        con.execute(f"CREATE TABLE IF NOT EXISTS {table} ({cols})")
    return con


def validate_frame(df: pd.DataFrame, table: str, cfg: Config | None = None) -> pd.DataFrame:
    """Reject rows that break provenance or timing rules instead of silently fixing them."""
    cfg = cfg or load_config()
    missing = [c for c in REQUIRED[table] if c not in df.columns]
    if missing:
        raise ValidationError(f"{table}: missing required columns {missing}")
    out = df.copy()
    for c in REQUIRED[table]:
        if out[c].isna().any():
            raise ValidationError(f"{table}: null values in required column '{c}' ({int(out[c].isna().sum())} rows)")
    unknown = set(out["source_id"]) - cfg.source_ids
    if unknown:
        raise ValidationError(f"{table}: source_id not in source register: {sorted(unknown)}")

    ts_col = "announced_at" if table in ("events", "universe_status") else "published_at"
    out[ts_col] = pd.to_datetime(out[ts_col])
    study_end = pd.Timestamp(cfg.settings["project"]["study_end"]) + pd.Timedelta(days=1)
    if (out[ts_col] >= study_end).any():
        raise ValidationError(f"{table}: {int((out[ts_col] >= study_end).sum())} rows published after study_end")

    date_col = {"prices": "obs_date", "series": "obs_date", "fundamentals": "period_end"}.get(table)
    if date_col:
        out[date_col] = pd.to_datetime(out[date_col])
        early = out[ts_col] < out[date_col]
        if early.any():
            raise ValidationError(
                f"{table}: {int(early.sum())} rows published before the period they describe (look-ahead risk)"
            )
    if "published_at_estimated" in SCHEMA[table] and "published_at_estimated" not in out.columns:
        out["published_at_estimated"] = False
    return out


def ingest(con: duckdb.DuckDBPyConnection, df: pd.DataFrame, table: str, dataset: str,
           cfg: Config | None = None) -> str:
    """Validate and append a frame; log the run. Returns the ingest run id."""
    cfg = cfg or load_config()
    run = uuid.uuid4().hex[:12]
    started = datetime.now()
    try:
        clean = validate_frame(df, table, cfg)
        cols = [c.split()[0] for c in SCHEMA[table].replace("\n", " ").split(",")]
        cols = [c.strip() for c in cols if c.strip()]
        clean = clean.assign(ingest_run=run)
        for c in cols:
            if c not in clean.columns:
                clean[c] = None
        clean = clean[cols]
        con.register("_incoming", clean)
        con.execute(f"INSERT INTO {table} SELECT * FROM _incoming")
        con.unregister("_incoming")
        status, msg, written = "ok", "", len(clean)
    except ValidationError as exc:
        status, msg, written = "rejected", str(exc), 0
    con.execute(
        "INSERT INTO ingest_log VALUES (?,?,?,?,?,?,?,?,?)",
        [run, dataset, ",".join(sorted(set(df.get("source_id", pd.Series(dtype=str)).dropna()))),
         len(df), written, started, datetime.now(), status, msg],
    )
    if status != "ok":
        raise ValidationError(msg)
    return run


def table_counts(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in SCHEMA}
