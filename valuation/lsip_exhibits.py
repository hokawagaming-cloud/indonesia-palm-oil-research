"""Exhibits 1-13 for the LSIP equity research report (Phase XVII).

    python -I -X utf8 valuation/lsip_exhibits.py   (after the cohort, model, analysis and TAPG scripts)
Writes outputs/lsip/ex01_*.png ... ex13_*.png from committed data files only.
"""
from __future__ import annotations

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
OUT = ROOT / "outputs" / "lsip"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "valuation"))
import lsip_cohort as LC  # noqa: E402

C = {"ink": "#1f2933", "blue": "#1f5aa6", "red": "#c0504d", "grey": "#7f8c8d", "green": "#2e8b57", "amber": "#d49a2a", "purple": "#8064a2",
     "lblue": "#9cb8dd"}
SC = {"A_historical": C["grey"], "B_accelerated": C["blue"], "C_deferred": C["red"], "D_intensive": C["green"]}
SCL = {"A_historical": "A historical pace", "B_accelerated": "B accelerated", "C_deferred": "C deferred", "D_intensive": "D intensive"}
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=150); plt.close(fig)


def main():
    A = pd.read_csv(RES / "LSIP_age_profile.csv")
    O = pd.read_csv(RES / "LSIP_operational_annual.csv", index_col=0)
    S = pd.read_csv(RES / "LSIP_cohort_scenarios.csv")
    E = pd.read_csv(RES / "LSIP_cohort_ensemble.csv")
    R = json.loads((RES / "LSIP_valuation_results.json").read_text())
    CS = json.loads((RES / "LSIP_cohort_summary.json").read_text())
    T = json.loads((RES / "LSIP_TAPG_valuation.json").read_text())
    TC = pd.read_csv(RES / "LSIP_TAPG_comparison.csv")
    px = R["price"]

    # 1 historical age profile
    a = A.dropna(subset=["total"]).copy(); a["yr"] = a.date.str[:4].astype(int)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    bot = np.zeros(len(a))
    for col, lab, cc in (("immature", "Immature (0-3)", C["green"]), ("a4_6", "4-6 yrs", C["lblue"]), ("a7_20", "7-20 yrs", C["blue"]), ("gt20", ">20 yrs", C["red"])):
        ax.bar(a.yr, a[col] / 1000, bottom=bot, color=cc, label=lab); bot += a[col].values / 1000
    for x, v in zip(a.yr, a.gt20_share):
        ax.text(x, bot[list(a.yr).index(x)] + 1, f"{v:.0%}", ha="center", fontsize=8, color=C["red"])
    ax2 = ax.twinx()
    aa = A.dropna(subset=["reported_avg_age"]).copy(); aa["t"] = pd.to_datetime(aa.date).dt.year + pd.to_datetime(aa.date).dt.month / 12 - 0.5
    ax2.plot(aa.t, aa.reported_avg_age, "ko--", ms=3, label="Reported average age (rhs)")
    ax2.set_ylim(10, 22); ax2.set_ylabel("years")
    ax.set_ylabel("'000 ha"); ax.set_ylim(0, 115); ax.legend(frameon=False, ncol=4, loc="upper left", fontsize=8); ax2.legend(frameon=False, loc="upper right", fontsize=8)
    ax.set_title("Exhibit 1. Nucleus oil-palm age profile FY2017-23 (% = >20 yrs); no disclosure after FY2023", loc="left")
    save(fig, "ex01_age_profile.png")

    # 2 cohort evolution (A vs B)
    base = LC.run()
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, n in zip(axs, ("A_historical", "B_accelerated")):
        g = S[S.scenario == n].set_index("year")
        imm = g.immature_ha / 1000; gt20 = g.gt20_ha / 1000; mid = (g.area_ha - g.immature_ha - g.gt20_ha) / 1000
        ax.stackplot(g.index, imm, mid, gt20, colors=[C["green"], C["blue"], C["red"]], labels=["Immature", "4-20 yrs", ">20 yrs"])
        ax.set_title(SCL[n], fontsize=9); ax.set_xlim(2026, 2050)
    axs[0].set_ylabel("'000 ha"); axs[0].legend(frameon=False, fontsize=8, loc="lower left")
    fig.suptitle("Exhibit 2. Reconstructed age-cohort evolution to 2050 (base ensemble member)", x=0.01, ha="left", fontsize=9)
    save(fig, "ex02_cohort_evolution.png")

    # 3 yield curve
    yc = LC.yield_curve(); k = CS["k_hist_2021_2025_base"]
    ages = np.arange(0, 41)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(ages, yc[ages], color=C["grey"], lw=2, label="Standard curve (analyst assumption, literature-shaped)")
    ax.plot(ages, yc[ages] * k, color=C["red"], lw=2, label=f"LSIP-scaled, k = {k:.2f} (FY21-25 fit)")
    ax.plot(ages, yc[ages] * k * 1.15, color=C["blue"], ls="--", label="Replanted material (k x 1.15, assumption)")
    for d in (0.75, 1.25):
        ax.plot(ages, LC.yield_curve(d)[ages] * k, color=C["red"], lw=0.6, ls=":")
    ax.axhline(O.loc["FY2025", "yield_nucleus_t_ha"], color=C["red"], lw=0.8); ax.text(30, O.loc["FY2025", "yield_nucleus_t_ha"] + 0.4, "LSIP FY25 13.4 t/ha (mature)", fontsize=8, color=C["red"])
    ax.axhline(24.3, color=C["green"], lw=0.8); ax.text(30, 24.7, "TAPG FY25 24.3 t/ha (group-wide)", fontsize=8, color=C["green"])
    ax.set_xlabel("palm age (years)"); ax.set_ylabel("t FFB / ha / yr"); ax.legend(frameon=False, fontsize=8, loc="center right")
    ax.set_title("Exhibit 3. Age-yield curve: assumption scaled to LSIP (dotted: decline 0.75x / 1.25x); NOT an LSIP-disclosed relationship", loc="left")
    save(fig, "ex03_yield_curve.png")

    # 4 replanting rate
    H = pd.read_csv(RES / "LSIP_cohort_reconstruction.csv"); H = H[H.kind.str.startswith("planting")]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    h = H[H.planting_year >= 2005]
    ax.bar(h.planting_year, h.ha, color=C["lblue"], label="Planted (reconstructed from age bands, NNLS)")
    ax.axhline(CS["hist_planting_rate_2017_2025_ha"], color=C["grey"], ls="--", label=f"Historical 2017-25 avg {CS['hist_planting_rate_2017_2025_ha']:,.0f} ha/yr (~{CS['implied_cycle_years_at_hist_rate']:.0f}-yr cycle)")
    ax.axhline(CS["sustainable_rate_ha_25y"], color=C["blue"], label=f"Sustainable, 25-yr cycle {CS['sustainable_rate_ha_25y']:,.0f} ha/yr")
    ax.axhline(CS["sustainable_rate_ha_22y"], color=C["blue"], ls=":", label=f"Sustainable, 22-yr cycle {CS['sustainable_rate_ha_22y']:,.0f} ha/yr")
    ax.axhline(5000, color=C["green"], ls="-.", label="Scenario D intensive 5,000 ha/yr")
    ax.set_ylabel("ha / yr"); ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.set_title("Exhibit 4. Historical (reconstructed) vs sustainable replanting rate", loc="left")
    save(fig, "ex04_replanting_rate.png")

    # 5 production by scenario with ensemble range
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for n, g in S.groupby("scenario"):
        ax.plot(g.year, g.ffb_nucleus_kt, color=SC[n], lw=2, label=SCL[n])
        e = E[E.scenario == n]
        for yy, col in ((2035, "ffb_2035"), (2050, "ffb_2050")):
            ax.plot([yy, yy], [e[col].min(), e[col].max()], color=SC[n], lw=4, alpha=0.35)
    ax.scatter(O.index[O.index.str.startswith("FY")].str[2:].astype(int), O.loc[O.index.str.startswith("FY"), "ffb_nucleus"], color=C["ink"], s=12, label="Reported")
    ax.scatter([2026], [1180], color=C["amber"], s=18, label="FY26E (9M + Q4E)")
    ax.set_ylabel("nucleus FFB, kt"); ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower left")
    ax.set_title("Exhibit 5. Nucleus FFB by replanting scenario (bars at 2035/2050: 36-member ensemble range)", loc="left")
    save(fig, "ex05_production_scenarios.png")

    # 6 replant capex and FCF
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    yrs = list(range(2026, 2051))
    for n in SC:
        d = R["detail"][f"{n}|base"]
        axs[0].plot(yrs, [d["cx_rep"][str(y)] for y in yrs], color=SC[n], label=SCL[n])
        axs[1].plot(yrs, [d["fcff"][str(y)] for y in yrs], color=SC[n], label=SCL[n])
    axs[0].set_title("Replanting capex (IDR bn, nominal)", fontsize=9); axs[1].set_title("Operating FCFF ex interest (IDR bn)", fontsize=9)
    axs[0].legend(frameon=False, fontsize=7.5)
    fig.suptitle("Exhibit 6. Replanting capex and free cash flow, base price case", x=0.01, ha="left", fontsize=9)
    save(fig, "ex06_capex_fcf.png")

    # 7 cash waterfall
    W = pd.read_csv(RES / "LSIP_cash_decomposition.csv")
    steps = W[~W.item.str.startswith("  ") & ~W.item.str.contains("Restricted|Replanting|Buyback|Distributable")]
    labels = ["Cash\n30 Sep 26", "Operating\ncash", "Seasonal\nWC", "CIP\ncommitments", "Employee\nbenefits", "Taxes\npayable"]
    vals = steps.idr_bn.values
    fig, ax = plt.subplots(figsize=(8, 3.6))
    cum = 0
    for i, (lab, v) in enumerate(zip(labels, vals)):
        ax.bar(i, v if i == 0 else v, bottom=0 if i == 0 else cum, color=C["blue"] if i == 0 else C["red"])
        cum = v if i == 0 else cum + v
        ax.text(i, (cum if i else v) + 80, f"{v:,.0f}", ha="center", fontsize=8)
    surplus = cum
    ax.bar(len(labels), surplus, color=C["green"]); ax.text(len(labels), surplus + 80, f"{surplus:,.0f}\n(IDR {surplus * 1000 / 6819.96:,.0f}/sh)", ha="center", fontsize=8)
    rp = float(W.loc[W.item.str.contains("related-party"), "idr_bn"].iloc[0])
    ax.bar(len(labels) + 1, rp, color=C["amber"]); ax.text(len(labels) + 1, rp + 80, f"{rp:,.0f}\nmemo", ha="center", fontsize=8)
    ax.bar(len(labels) + 2, 750, color=C["grey"]); ax.text(len(labels) + 2, 830, "750\nunverified", ha="center", fontsize=8)
    ax.set_xticks(range(len(labels) + 3), labels + ["Distributable\nsurplus", "of which at\nBank Ina", "Buyback\nauthorised"], fontsize=7.5)
    ax.set_ylim(0, 9600); ax.set_ylabel("IDR bn"); ax.set_title("Exhibit 7. Cash allocation at 30 Sep 2026: genuinely surplus cash (replanting is funded inside the DCF)", loc="left")
    save(fig, "ex07_cash_waterfall.png")

    # 8 dividend policy
    D = pd.read_csv(RES / "LSIP_capital_return_history.csv")
    fig, ax = plt.subplots(figsize=(8, 3.6))
    x = D.fy.values
    ax.bar(x - 0.2, D.profit_bn, 0.4, color=C["blue"], label="Profit")
    ax.bar(x + 0.2, D.dividend_bn, 0.4, color=C["amber"], label="Dividend declared")
    ax.plot(x, D.cash_end_bn, "s-", color=C["green"], label="Year-end cash")
    ax2 = ax.twinx(); ax2.plot(x, D.payout, "o--", color=C["red"], label="Payout (rhs)"); ax2.set_ylim(0, 0.6)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_ylabel("IDR bn"); ax.legend(frameon=False, loc="upper left", fontsize=8); ax2.legend(frameon=False, loc="upper center", fontsize=8)
    ax.set_title("Exhibit 8. Profit, dividends and the cash pile, FY2020-FY2025 (payout 20-35%)", loc="left")
    save(fig, "ex08_dividends.png")

    # 9 earnings vs consensus
    Q = pd.read_csv(RES / "LSIP_q4_2026_nowcast_v2.csv", index_col=0)
    cons = pd.read_csv(ROOT / "data" / "reference" / "consensus_history.csv")
    cl = cons[cons.ticker == "LSIP"].sort_values("retrieved").groupby("fy").last()
    fy26 = {c: Q.loc[c, "fy26_np_owners"] for c in ("bear", "base", "bull")}
    fy27 = {c: R["detail"][f"A_historical|{c}"]["ni"]["2027"] for c in ("bear", "base", "bull")}
    fig, ax = plt.subplots(figsize=(8, 3.4))
    for i, (lab, d, cv) in enumerate((("FY2026E", fy26, cl.loc["FY26", "eps_avg"] * 6.81996), ("FY2027E", fy27, cl.loc["FY27", "eps_avg"] * 6.81996))):
        ax.bar(i - 0.27, d["bear"], 0.18, color=C["red"], label="Ours bear" if i == 0 else None)
        ax.bar(i - 0.09, d["base"], 0.18, color=C["blue"], label="Ours base" if i == 0 else None)
        ax.bar(i + 0.09, d["bull"], 0.18, color=C["green"], label="Ours bull" if i == 0 else None)
        ax.bar(i + 0.27, cv, 0.18, color=C["grey"], label="Consensus (S&P via Yahoo, 25 Nov 2026)" if i == 0 else None)
        for dx, v in ((-0.27, d["bear"]), (-0.09, d["base"]), (0.09, d["bull"]), (0.27, cv)):
            ax.text(i + dx, v + 30, f"{v:,.0f}", ha="center", fontsize=7.5)
    ax.set_xticks([0, 1], ["FY2026E (9M actual + Q4E)", "FY2027E (scenario A)"]); ax.set_ylabel("profit to owners, IDR bn")
    ax.legend(frameon=False, fontsize=8, ncol=2); ax.set_title("Exhibit 9. Earnings forecasts vs consensus (no historical consensus exists before 24 Nov 2026)", loc="left")
    save(fig, "ex09_earnings_vs_consensus.png")

    # 10 football field
    J = R["joint"]
    snap = json.loads((RES / "LSIP_market_snapshot.json").read_text(encoding="utf-8"))
    pt = snap["lsip_price_targets"]
    bars = [("DCF + surplus cash, 80% credit (A, bear-bull)", J["A_historical|bear|0.8"]["ps"], J["A_historical|bull|0.8"]["ps"], J["A_historical|base|0.8"]["ps"]),
            ("DCF + surplus cash, 100% credit (A)", J["A_historical|bear|1.0"]["ps"], J["A_historical|bull|1.0"]["ps"], J["A_historical|base|1.0"]["ps"]),
            ("DCF + surplus cash, 60% credit (A)", J["A_historical|bear|0.6"]["ps"], J["A_historical|bull|0.6"]["ps"], J["A_historical|base|0.6"]["ps"]),
            ("All replanting scenarios, base price, 80%", min(J[f"{n}|base|0.8"]["ps"] for n in SC), max(J[f"{n}|base|0.8"]["ps"] for n in SC), np.nan),
            ("DDM, 30% payout (minority cash receipts)", J["A_historical|bear|0.8"]["ddm_ps"], J["A_historical|bull|0.8"]["ddm_ps"], J["A_historical|base|0.8"]["ddm_ps"]),
            ("Surplus cash only (80-100%)", J["A_historical|base|0.8"]["cash_ps"], J["A_historical|base|1.0"]["cash_ps"], np.nan),
            ("Analyst targets low-high", pt["low"], pt["high"], pt["mean"]),
            ("52-week range", snap["lsip_info"]["fiftyTwoWeekLow"], snap["lsip_info"]["fiftyTwoWeekHigh"], np.nan)]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    for i, (lab, lo, hi, mid) in enumerate(bars):
        ax.barh(i, hi - lo, left=lo, color=C["blue"] if i < 6 else C["grey"], alpha=0.55)
        if not np.isnan(mid):
            ax.plot(mid, i, "k|", ms=14)
    ax.axvline(px, color=C["red"], lw=1.5, label=f"Price IDR {px:,.0f}")
    ax.set_yticks(range(len(bars)), [b[0] for b in bars], fontsize=8); ax.invert_yaxis(); ax.set_xlabel("IDR per share (tick = base / mean)")
    ax.legend(frameon=False, loc="lower right"); ax.set_title("Exhibit 10. Valuation summary (value at 31 Dec 2026)", loc="left")
    save(fig, "ex10_football_field.png")

    # 11 reverse DCF heat map
    gl = R["grid_lr_beta"]; lrs = (11000, 12500, 14000, 15500, 17000); bs = (0.6, 0.75, 0.9, 1.05, 1.2)
    M = np.array([[gl[f"{lr}|{b}"] for b in bs] for lr in lrs])
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    im = ax.imshow(M / px - 1, cmap="RdBu", vmin=-0.6, vmax=0.6)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{M[i, j]:,.0f}", ha="center", va="center", fontsize=8)
    ax.set_xticks(range(5), [f"{0.0774 + b * 0.06:.1%}" for b in bs]); ax.set_yticks(range(5), [f"{lr:,}" for lr in lrs])
    ax.set_xlabel("cost of equity"); ax.set_ylabel("long-run realised CPO (IDR/kg, FY2029)")
    rv = R["reverse"]
    ax.set_title(f"Exhibit 11. Value/share (A, 80% cash credit). Price implies LR CPO ~{rv['implied_long_run_cpo_idr_kg']:,.0f}\n(80% credit) / {rv['implied_long_run_cpo_full_cash_credit']:,.0f} (100%); cash credit {rv['implied_cash_credit_at_base_ops']:.0%} at base ops", loc="left", fontsize=8.5)
    fig.colorbar(im, ax=ax, fraction=0.04, format=matplotlib.ticker.PercentFormatter(1.0))
    save(fig, "ex11_reverse_dcf.png")

    # 12 LSIP vs TAPG
    fig, axs = plt.subplots(1, 4, figsize=(10, 3.2))
    for ax, col, ttl, fmt in ((axs[0], "yield_t_ha", "FFB yield (t/ha)", "{:.1f}"), (axs[1], "op_margin", "Operating margin", "{:.0%}"),
                              (axs[2], "roic", "ROIC (NOPAT / equity ex cash)", "{:.0%}"), (axs[3], "fcf_payout", "Dividends / FCF", "{:.0%}")):
        for co, cc in (("LSIP", C["red"]), ("TAPG", C["green"])):
            d = TC[TC.company == co]
            ax.plot(d.fy, d[col], "o-", color=cc, label=co)
        ax.set_title(ttl, fontsize=9); ax.set_xticks(range(2021, 2026), [str(y)[2:] for y in range(2021, 2026)])
        if fmt.endswith("%}"):
            ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    axs[0].legend(frameon=False)
    fig.suptitle("Exhibit 12. LSIP vs TAPG operating economics, FY2021-FY2025 (TAPG operating data group-wide incl. associates; >20-yr share: LSIP 41% vs TAPG 3-6%)", x=0.01, ha="left", fontsize=8.5)
    save(fig, "ex12_lsip_vs_tapg.png")

    # 13 catalyst timeline
    ev = [("2026-12-31", "Buyback window closes\n(up to IDR 750bn)"), ("2027-01-10", "IDX buyback report\n(C-019)"),
          ("2027-02-26", "FY2026 results\nQ4 vs 360 cons. (C-020)"), ("2027-04-30", "AR/SR 2026: age\nprofile disclosure?"),
          ("2027-06-25", "AGM: FY26 payout\n(C-021)"), ("2027-07-31", "H1 2027 results\n(El Nino lag?)"), ("2027-10-30", "9M 2027 results")]
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ts = pd.to_datetime([e[0] for e in ev])
    ax.plot(ts, np.zeros(len(ts)), "-", color=C["grey"])
    for i, (t, (d, lab)) in enumerate(zip(ts, ev)):
        yy = 0.6 if i % 2 == 0 else -0.6
        ax.plot([t, t], [0, yy * 0.8], color=C["blue"]); ax.plot(t, 0, "o", color=C["blue"])
        ax.text(t, yy, f"{t:%d %b %Y}\n{lab}", ha="center", va="center", fontsize=7.5)
    ax.set_ylim(-1.2, 1.2); ax.axis("off")
    ax.set_title("Exhibit 13. Catalyst timeline (dates after 2026 are expected, not confirmed)", loc="left")
    save(fig, "ex13_catalysts.png")


if __name__ == "__main__":
    main(); print(sorted(p.name for p in OUT.glob("*.png")))
