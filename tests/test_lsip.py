import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
import lsip_stage1 as l  # noqa: E402


def test_q3_reconstruction_identities():
    df = l.quarters()
    q3 = df.loc["Q3 2026"]
    assert abs(q3.revenue - q3.cogs - q3.gross_profit) < 1.0          # Q3 GP = revenue - COGS (from 9M - H1)
    assert abs(df.loc["Q1 2026"].revenue + df.loc["Q2 2026"].revenue + q3.revenue - l.CUM["9M 2026"]["revenue"]) < 1.0


def test_bridge_sums_to_gross_profit_change():
    df = l.quarters()
    br = l.q3_bridge(df).set_index("component")["idr_bn"]
    parts = br.drop(["  of which purchased FFB", "  of which upkeep & fertiliser", "= Gross profit change"]).sum()
    assert abs(parts - br["= Gross profit change"]) < 1e-6


def test_buyback_accretion_positive_and_bounded():
    cb = l.cash_and_buyback()
    assert 0.0 < cb["eps_accretion"] < cb["buyback_pct_shares"] / (1 - cb["buyback_pct_shares"])
