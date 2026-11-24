"""USTP (PT Union Sampoerna Triputra Persada, 50% JV) module for a future SOTP model.

This module only prepares inputs. It does NOT produce a valuation or rating: the
valuation functions need explicit, documented assumptions (multiples, cost of equity,
growth) that have not yet been set in context/ASSUMPTIONS.md.

History (JV scope, 100% basis, IDR mn) comes from data/reference/TAPG_scope_jv.csv
(TAPG note 14a, summarised financials).

Usage:  python -I valuation/ustp_module.py   -> writes data/reference/USTP_history.csv
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
STAKE = 0.50  # TAPG direct ownership of USTP (AR2025 p304)


def history() -> pd.DataFrame:
    jv = pd.read_csv(REF / "TAPG_scope_jv.csv")
    p = jv.pivot_table(index="period", columns="item", values="value", aggfunc="last")
    h = pd.DataFrame(index=p.index)
    h["net_sales"] = p.get("ustp_net_sales")
    h["profit"] = p.get("ustp_profit")
    h["net_margin"] = h["profit"] / h["net_sales"]
    h["net_assets"] = p.get("ustp_net_assets")
    h["share_of_profit_tapg"] = p.get("ustp_share_of_profit_tapg")
    h["dividend_to_tapg"] = p.get("ustp_dividend_to_tapg_declared")
    h["carrying_value_tapg"] = p.get("ustp_carrying_value_tapg")
    h["payout_ratio"] = h["dividend_to_tapg"] / h["share_of_profit_tapg"]
    h["roe_on_avg_net_assets"] = h["profit"] / h["net_assets"].rolling(2).mean()
    return h.sort_index()


@dataclass
class UstpValuationInputs:
    """All fields must be set from documented assumptions before use."""
    pe_multiple: float | None = None          # on forward USTP profit (100%)
    pb_multiple: float | None = None          # on USTP net assets (100%)
    cost_of_equity: float | None = None       # for dividend discount
    dividend_growth: float | None = None
    forward_profit: float | None = None       # IDR mn, 100% basis; from the nowcast/forecast, not history
    forward_dividend_to_tapg: float | None = None


def look_through_values(x: UstpValuationInputs, net_assets: float) -> dict[str, float | None]:
    """TAPG's 50% look-through value of USTP under each method (IDR mn)."""
    out: dict[str, float | None] = {}
    out["pe"] = STAKE * x.pe_multiple * x.forward_profit if None not in (x.pe_multiple, x.forward_profit) else None
    out["pb"] = STAKE * x.pb_multiple * net_assets if x.pb_multiple is not None else None
    if None not in (x.cost_of_equity, x.dividend_growth, x.forward_dividend_to_tapg):
        if x.cost_of_equity <= x.dividend_growth:
            raise ValueError("cost of equity must exceed dividend growth")
        out["ddm"] = x.forward_dividend_to_tapg / (x.cost_of_equity - x.dividend_growth)
    else:
        out["ddm"] = None
    return out


if __name__ == "__main__":
    h = history()
    h.to_csv(REF / "USTP_history.csv")
    print((h.drop(columns=["net_margin", "payout_ratio", "roe_on_avg_net_assets"]) / 1e3).round(1).to_string())
    print(h[["net_margin", "payout_ratio", "roe_on_avg_net_assets"]].round(3).to_string())
