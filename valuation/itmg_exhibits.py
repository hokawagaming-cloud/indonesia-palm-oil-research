"""Exhibits for the ITMG equity research report (Phase XVI).

    python -I -X utf8 valuation/itmg_exhibits.py   (after valuation/itmg_model.py)
Writes outputs/itmg/*.png. Every exhibit is drawn from committed data files (FS extract, C1 forecasts, valuation results).
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
OUT = ROOT / "outputs" / "itmg"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "quant"))
from itmg_prospective_run import read_series  # noqa: E402

C = {"ink": "#1f2933", "blue": "#1f5aa6", "red": "#c0504d", "grey": "#7f8c8d", "green": "#2e8b57", "amber": "#d49a2a"}
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=150); plt.close(fig)


def main():
    A = pd.read_csv(RES / "ITMG_financials_annual.csv", index_col=0) / 1000
    fy = A.loc[[f"FY{y}" for y in range(2018, 2026)]]
    R = json.loads((RES / "ITMG_valuation_results.json").read_text(encoding="utf-8"))
    base = R["scenarios"]["Base"]

    # 1 history: revenue, profit, dividends paid
    fig, ax = plt.subplots(figsize=(8, 3.6))
    x = np.arange(len(fy)); w = 0.27
    ax.bar(x - w, fy.revenue, w, label="Revenue", color=C["blue"])
    ax.bar(x, fy.profit_owners, w, label="Profit to owners", color=C["green"])
    ax.bar(x + w, -fy.dividends_paid, w, label="Dividends paid (cash)", color=C["amber"])
    ax.set_xticks(x, [i[2:] for i in fy.index]); ax.set_ylabel("USD m"); ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.set_title("Exhibit 1. ITMG revenue, profit and dividends paid, FY2018-FY2025 (audited FS)", loc="left")
    save(fig, "ex1_history.png")

    # 2 ASP vs Newcastle and unit cost
    fs = pd.read_csv(RES / "ITMG_fs_costs.csv", index_col=0); fs.index = pd.PeriodIndex(fs.index, freq="Q")
    fs["uc"] = (fs.cost_of_revenue_q - fs.royalty_q) / fs.implied_sales_mt / 1000
    N = read_series(sorted(glob.glob(str(ROOT / "data/raw/macro/cmo_vintages/CMO_origin_*.xlsx")))[-1], "Coal, Australian")
    Nq = N.groupby(N.index.asfreq("Q")).mean().reindex(fs.index)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    t = fs.index.to_timestamp()
    ax.plot(t, Nq, color=C["grey"], label="Newcastle (World Bank CMO, quarterly avg)")
    ax.plot(t, fs.asp_first, color=C["blue"], lw=2, label="ITMG ASP (first reported)")
    ax.plot(t, fs.uc, color=C["red"], label="ITMG unit cost ex-royalty (FS)")
    ax.set_ylabel("USD/t"); ax.legend(frameon=False); ax.set_title("Exhibit 2. Price realisation and unit cost, 2018Q1-2026Q3", loc="left")
    save(fig, "ex2_asp_cost.png")

    # 3 C1 forecasting record
    F = pd.read_csv(RES / "ITMG_C1_forecasts.csv").dropna(subset=["M2_distributed_lag"])
    fig, ax = plt.subplots(figsize=(8, 3.4))
    q = pd.PeriodIndex(F.q, freq="Q").to_timestamp()
    ax.plot(q, F.actual, "o-", color=C["ink"], ms=3, label="Actual ASP (first reported)")
    ax.plot(q, F.M2_distributed_lag, "s--", color=C["blue"], ms=3, label="C1-M2 forecast (walk-forward, origin q-end + 10d)")
    ax.plot(q, F.B4_price_scaled, ":", color=C["grey"], label="Strongest benchmark B4")
    mae_m, mae_b = (F.M2_distributed_lag - F.actual).abs().mean(), (F.B4_price_scaled - F.actual).abs().mean()
    ax.set_title(f"Exhibit 3. ITMG-C1 historical walk-forward record (MAE {mae_m:.1f} vs {mae_b:.1f} USD/t) - forecasting evidence, not alpha", loc="left")
    ax.set_ylabel("USD/t"); ax.legend(frameon=False)
    save(fig, "ex3_c1_record.png")

    # 4 production schedule (base)
    import openpyxl
    sys.path.insert(0, str(ROOT / "valuation"))
    from xlsx_eval import Evaluator
    wb = openpyxl.load_workbook(ROOT / "outputs" / "ITMG_model_valuation.xlsx")
    E = Evaluator(wb); E.set("Inputs", "B3", 2)
    ws = wb["Mines"]
    rows = {ws[f"A{r}"].value.split()[0]: r for r in range(1, 60) if isinstance(ws[f"A{r}"].value, str) and ws[f"A{r}"].value.endswith("production (Mt)")}
    cols = [openpyxl.utils.get_column_letter(3 + i) for i in range(25)]
    yrs = list(range(2026, 2051))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bottom = np.zeros(len(yrs))
    pal = ["#1f5aa6", "#4f81bd", "#9bbb59", "#d49a2a", "#c0504d", "#8064a2"]
    for (k, r), col in zip(rows.items(), pal):
        v = np.array([float(E.get("Mines", f"{c}{r}")) for c in cols])
        ax.bar(yrs, v, bottom=bottom, color=col, label=k); bottom += v
    ax.set_ylabel("Mt"); ax.legend(frameon=False, ncol=6, fontsize=8)
    ax.set_title("Exhibit 4. Base-case own production by mine (Mt; reserves at end-2025, IMM extended)", loc="left")
    save(fig, "ex4_production.png")

    # 5 valuation football field
    S = R["scenarios"]; price = R["price_idr"]
    snap = json.loads((RES / "ITMG_market_snapshot.json").read_text(encoding="utf-8"))
    pt = snap["itmg_price_targets"]
    bars = [("DCF bear / base / bull", S["Bear"]["valuation"]["fv"], S["Bull"]["valuation"]["fv"], S["Base"]["valuation"]["fv"]),
            ("Finite DDM (60% payout) bear-bull", S["Bear"]["valuation"]["ddm"], S["Bull"]["valuation"]["ddm"], S["Base"]["valuation"]["ddm"]),
            ("Peer P/E x FY27E EPS bear-bull", S["Bear"]["valuation"]["rel_pe"], S["Bull"]["valuation"]["rel_pe"], S["Base"]["valuation"]["rel_pe"]),
            ("Peer EV/EBITDA x FY27E bear-bull", S["Bear"]["valuation"]["rel_ev"], S["Bull"]["valuation"]["rel_ev"], S["Base"]["valuation"]["rel_ev"]),
            ("Analyst targets low-high (consensus)", pt["low"], pt["high"], pt["mean"]),
            ("52-week trading range", snap["itmg_info"]["fiftyTwoWeekLow"], snap["itmg_info"]["fiftyTwoWeekHigh"], np.nan)]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, (lab, lo, hi, mid) in enumerate(bars):
        lo2, hi2 = max(min(lo, hi), 0), max(lo, hi)
        ax.barh(i, hi2 - lo2, left=lo2, color=C["blue"] if i < 4 else C["grey"], alpha=0.55)
        if not np.isnan(mid):
            ax.plot(mid, i, "k|", ms=14)
    ax.axvline(price, color=C["red"], lw=1.5, label=f"Price IDR {price:,.0f}")
    ax.set_yticks(range(len(bars)), [b[0] for b in bars]); ax.invert_yaxis(); ax.set_xlabel("IDR per share (tick = base / mean)")
    ax.set_xlim(0, 70000); ax.legend(frameon=False, loc="lower right")
    ax.set_title("Exhibit 5. Valuation summary (bear-bull ranges; values below zero truncated)", loc="left")
    save(fig, "ex5_football.png")

    # 6 sensitivity heat map
    g = R["sensitivity_lr_ke"]
    lrs, kes = (85, 95, 105, 115, 125), (0.10, 0.11, 0.12, 0.13, 0.14)
    M = np.array([[g[f"{lr}|{ke}"] for ke in kes] for lr in lrs])
    fig, ax = plt.subplots(figsize=(6, 3.4))
    im = ax.imshow(M / price - 1, cmap="RdBu", vmin=-1, vmax=1)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{M[i, j] / 1000:,.1f}k", ha="center", va="center", fontsize=8)
    ax.set_xticks(range(5), [f"{k:.0%}" for k in kes]); ax.set_yticks(range(5), [f"${l}" for l in lrs])
    ax.set_xlabel("Cost of equity"); ax.set_ylabel("Long-run Newcastle 2029 (USD/t, +2%/yr)")
    ax.set_title("Exhibit 6. Base DCF (IDR/share); colour = vs price", loc="left", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.04, format=matplotlib.ticker.PercentFormatter(1.0))
    save(fig, "ex6_sensitivity.png")

    # 7 base projections FY2026-2030
    yrs5 = ["2026", "2027", "2028", "2029", "2030"]
    P = base["projection"]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    x = np.arange(5)
    ax.bar(x - 0.2, [P[y]["ebitda"] for y in yrs5], 0.4, color=C["blue"], label="EBITDA")
    ax.bar(x + 0.2, [P[y]["nio"] for y in yrs5], 0.4, color=C["green"], label="Profit to owners")
    ax2 = ax.twinx(); ax2.plot(x, [P[y]["asp"] for y in yrs5], "o-", color=C["red"], label="ASP (rhs)")
    ax.set_xticks(x, ["FY26E", "FY27E", "FY28E", "FY29E", "FY30E"]); ax.set_ylabel("USD m"); ax2.set_ylabel("USD/t")
    ax.legend(frameon=False, loc="upper right"); ax2.legend(frameon=False, loc="upper center")
    ax.set_title("Exhibit 7. Base-case forecasts (FY26E: 9M actual + C1/benchmark Q4; FY27E+: analyst assumptions)", loc="left")
    save(fig, "ex7_forecast.png")


if __name__ == "__main__":
    main(); print(sorted(p.name for p in OUT.glob("*.png")))
