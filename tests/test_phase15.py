"""Phase XV DR-R1: engineering tests (PIT timing, engine identity, decision bookkeeping). Not evidence of skill."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
sys.path.insert(0, str(ROOT / "quant"))


def monthly():
    return pd.read_csv(RES / "DR_R1_monthly.csv", index_col=0)


def test_signal_uses_only_t_minus_1_and_t_minus_2():
    mm = pd.read_csv(ROOT / "data" / "reference" / "macro_monthly.csv", index_col=0)
    mm.index = pd.PeriodIndex(mm.index, freq="M")
    cpo = mm.palm_oil_usd_t * mm.usdidr_month_avg
    M = monthly()
    for m in ["2016-03", "2020-04", "2026-10"]:
        p = pd.Period(m, "M")
        assert np.isclose(M.loc[m, "signal_dlog_cpo_idr"], np.log(cpo[p - 2] / cpo[p - 3]), atol=1e-6)  # CSV stores 6 decimals
    assert (M.invested == (M.signal_dlog_cpo_idr > 0)).all()


def test_formation_date_precedes_holding_month():
    M = monthly()
    f = pd.to_datetime(M.formation_date).dt.to_period("M")
    assert (f == pd.PeriodIndex(M.index, freq="M") - 1).all()


def test_basket_reproduces_existing_benchmark():
    M = monthly()
    b = pd.read_csv(ROOT / "data" / "reference" / "benchmarks_daily.csv", index_col=0, parse_dates=True)
    bm = (1 + b.ew_core_pit_ret.fillna(0)).groupby(b.index.to_period("M")).prod() - 1
    bm.index = bm.index.astype(str)
    c = pd.concat([M.basket_gross, bm], axis=1).dropna()
    assert len(c) == 128 and (c.iloc[:, 0] - c.iloc[:, 1]).abs().max() < 1e-4


def test_cash_months_earn_cash_less_exit_cost():
    M = monthly()
    stay = (~M.invested) & (~M.invested.shift(1, fill_value=True))
    assert np.allclose(M.strategy_net[stay], M.cash[stay])


def test_holm_family_not_reduced_and_decision_recorded():
    r = json.loads((RES / "DR_R1_results.json").read_text(encoding="utf-8"))
    p = r["primary"]
    assert p["holm_adjusted_p"] == min(1.0, 3 * p["hac"]["p_one_sided"])
    assert p["passes_registered_rule"] is False
    assert json.loads((RES / "DR_preregistration.json").read_text(encoding="utf-8"))["hypotheses"].keys() >= {"R1_palm_cpo_impulse_timing"}
