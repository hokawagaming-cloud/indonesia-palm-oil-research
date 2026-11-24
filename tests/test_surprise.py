import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
import surprise_study as s  # noqa: E402


def test_uses_only_snapshots_before_event():
    c = pd.DataFrame({"ticker": ["X", "X"], "fy": ["FY26", "FY26"], "retrieved": ["2026-11-24", "2027-03-20"],
                      "eps_avg": [200.0, 300.0], "eps_low": [190.0, 290.0], "eps_high": [210.0, 310.0], "n_analysts": [4, 4]})
    imp = s.implied_remainder(c, "X", "FY26", "2027-03-17", shares_mn=1000, reported_cum_bn=150)
    assert imp["snapshot"] == "2026-11-24" and imp["expected"] == 50.0
    out = s.surprise(60.0, imp)
    assert abs(out["surprise_pct"] - 0.2) < 1e-12 and abs(out["sue_like"] - 0.5) < 1e-12
    assert s.implied_remainder(c, "X", "FY26", "2026-11-24", 1000, 150) is None  # nothing strictly before
