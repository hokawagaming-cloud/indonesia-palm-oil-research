"""Audit finding B: inventory release must not scale other products or production costs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
import tapg_q4_2026_nowcast as n  # noqa: E402

BASE = dict(harvest=1.0, inv_release=0.0, asp_vs_q3=0.0, pk_asp_vs_q3=0.0, fert_q4=75, ffb_price_pass=0.5, jv_assoc=300)


def test_release_adds_only_released_value_to_cogs_and_own_product_volume():
    a = n.run(BASE)
    b = n.run({**BASE, "inv_release": 1.0})
    released_cost = n.I["fg_inventory_build_bn"]
    assert abs((b["cogs"] - a["cogs"]) - released_cost) < 1e-6
    assert abs((b["revenue"] - a["revenue"]) - b["revenue_from_inventory"]) < 1e-6
    # CPO from production unchanged; PK increase equals only the PK share of the release
    assert abs((b["cpo_sales_kt"] - b["cpo_from_inventory_kt"]) - a["cpo_sales_kt"]) < 1e-9
    pk_release_kt = released_cost * n.FG_SHARE["pk"] * 1e3 / (n.I["q3_pk_asp"] * n.COST_TO_ASP)
    assert abs((b["pk_sales_kt"] - a["pk_sales_kt"]) - pk_release_kt) < 1e-9


def test_q3_replay_reproduces_q3_gross_profit():
    r = n.run(BASE)
    assert abs(r["gross_profit"] - n.Q3["gross_profit"]) < 1.0  # identity check of the cost structure
