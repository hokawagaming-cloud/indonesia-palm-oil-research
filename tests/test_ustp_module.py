import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "valuation"))
import ustp_module as u  # noqa: E402


def test_unset_inputs_return_none():
    assert u.look_through_values(u.UstpValuationInputs(), 1000.0) == {"pe": None, "pb": None, "ddm": None}


def test_methods_arithmetic():
    x = u.UstpValuationInputs(pe_multiple=10, pb_multiple=1.0, cost_of_equity=0.12, dividend_growth=0.02,
                              forward_profit=100.0, forward_dividend_to_tapg=10.0)
    v = u.look_through_values(x, 400.0)
    assert v["pe"] == 500 and v["pb"] == 200 and abs(v["ddm"] - 100) < 1e-9
    with pytest.raises(ValueError):
        u.look_through_values(u.UstpValuationInputs(cost_of_equity=0.02, dividend_growth=0.05, forward_dividend_to_tapg=1), 1)


def test_history_ties_to_tapg_share():
    h = u.history()
    r = h.loc["FY2025"]
    assert abs(r.profit * 0.5 - r.share_of_profit_tapg) <= 1
