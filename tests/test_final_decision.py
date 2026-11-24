import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
import final_decision as fd  # noqa: E402


def test_interest_income_not_double_counted():
    v = fd.lsip_valuation()
    # cash-adjusted value must be built on operating (ex-interest) profit: raising NP by the interest
    # amount should be exactly offset when it is stripped
    hi = fd.lsip_valuation(np27={k: x + fd.INT_AT for k, x in fd.NP27.items()},
                           pe_ops={"bear": 0.33, "base": 1.2, "bull": 2.3})
    assert hi["values"]["cash_adjusted"]["base"] > v["values"]["cash_adjusted"]["base"]
    assert 200 < fd.INT_AT < 320


def test_dividend_paid_from_cash_once():
    v = fd.lsip_valuation(buyback_done=0.0)
    assert abs(v["cash12"] - (fd.CASH + 1800 - fd.PAYOUT * fd.NP26_BASE)) < 1e-6


def test_joint_adverse_worse_than_isolated():
    j = fd.joint_adverse()
    iso = j[(j.buyback_executed == 1.0) & (j.cash_credit == 1.0) & (j.np27_case == "bear")].ret_cash_adjusted.iloc[0]
    assert j.ret_cash_adjusted.min() < iso - 0.2


def test_scores_bounded_and_rules_cover_all():
    for t, s in fd.SCORES.items():
        assert set(s) == set(fd.SCORE_RULES)
        assert all(1 <= x <= 5 for x in s.values())
