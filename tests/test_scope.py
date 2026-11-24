import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
import tapg_scope  # noqa: E402


def test_mixed_scope_ratio_is_refused():
    with pytest.raises(tapg_scope.ScopeError):
        tapg_scope.ratio(("consolidated", "revenue"), ("groupwide", "cpo_production"), "FY2025")


def test_same_scope_ratio_works():
    r = tapg_scope.ratio(("consolidated", "gross_profit"), ("consolidated", "revenue"), "FY2025")
    assert abs(r - 4497617 / 11402198) < 1e-9
