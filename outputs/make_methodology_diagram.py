"""Quantitative methodology diagram (Phase VIII). Every formula and status below is taken from the
implemented repository code; module names are cited. Nothing is shown as validated unless an
out-of-sample test exists (none does as of 2026-11-25).

Usage: python -I -X utf8 outputs/make_methodology_diagram.py  -> outputs/quant_methodology_2026-11-25.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "quant_methodology_2026-11-25.png"

# status colours (border + fill): implemented / exploratory / validated / planned
ST = {
    "IMPLEMENTED": ("#1f5f8b", "#e8f1f8"),
    "EXPLORATORY": ("#b26a00", "#fff4e0"),
    "VALIDATED": ("#2e7d32", "#e8f5e9"),
    "PLANNED": ("#757575", "#f4f4f4"),
}

STAGES = [
    ("1. Data sources", "IMPLEMENTED",
     ["IDX filings (user-supplied PDFs) + jejaksaham timestamps",
      "Yahoo OHLCV (unofficial) · World Bank CMO · KPBN snapshot",
      "PMK/Kepmendag levy & duty decrees · S&P consensus (Yahoo)",
      "Source register S-001..S-059; raw data immutable",
      "PIHPS chicken/egg prices 2017+ (poultry pilot, S-054)"],
     "data/SOURCE_REGISTER.csv"),
    ("2. Point-in-time processing", "IMPLEMENTED",
     ["available_from = filing day if filed < 09:00 WIB, else next",
      "  trading day (A-018); strict vintage: comparatives dated",
      "  to the document that re-publishes them",
      "Scope separation: consolidated / JV / group (ScopeError)"],
     "quant/pit_panel.py · tapg_scope.py"),
    ("3. Feature engineering", "IMPLEMENTED",
     ["netback = HRef - levy(HRef) - duty(HRef)   [USD/t]",
      "levy, duty = regime lookup on reference price band",
      "Standalone quarter: Q_n = cum_n - cum_(n-1)",
      "EW core PIT sector index (liquidity band, monthly rebalance)"],
     "levy_duty.py · cpo_netback.py · benchmarks.py"),
    ("4. Predictive earnings models", "EXPLORATORY",
     ["Product-level nowcast: Rev = sum_p vol_p x ASP_p;",
      "  COGS = Q3 COGS(ex-fert) x vol x FFB-price adj + fert_Q4;",
      "  inventory release modelled per product (fix D-015)",
      "Benchmarks: price_last y_q = y_(q-1) P_q/P_(q-1); price_seas (lag 4)",
      "Scenarios bear/base/bull, inputs tagged OBS/BRK/GUID/DER/EST"],
     "tapg_q4_2026_nowcast.py · lsip_stage1.py"),
    ("5. Statistical validation", "EXPLORATORY",
     ["PIT walk-forward vs benchmarks: n = 2 (TAPG); MAE, RMSE, bias, MAPE",
      "Factor OLS, Newey-West t: r_i = a + b_m r_IHSG + b_s (r_sect - r_IHSG)",
      "  + b_cpo r_CPO + b_fx r_USDIDR + e",
      "Event study CAR[0,k] = sum (r_i - r_peers); rank corr vs surprise n = 8",
      "Residual-momentum rank IC: mean +0.04, t 0.93 (not significant)"],
     "forecast_validation.py · final_decision.py · stats_utils.py"),
    ("6. Consensus comparison", "IMPLEMENTED",
     ["Implied Q4 = consensus FY EPS x shares - reported 9M profit",
      "Surprise = (A - E)/|E|;  SUE-like = (A - E)/dispersion",
      "Append-only consensus history from 2026-11-24 (no earlier history)"],
     "surprise_study.py · tapg_monitor.py"),
    ("7. Reverse valuation", "IMPLEMENTED",
     ["Mcap = E x c x (1+g)/(ke - g)  ->  implied sustainable E",
      "  ke 12.5%, g 2%, c 0.85 (A-024)",
      "Cash-adjusted: V = cash_12m x credit + m x (NP - after-tax interest)",
      "Joint adverse grid (buyback x cash credit x profit) instead of 1-D tests"],
     "reverse_valuation.py · final_decision.py"),
    ("8. Risk-adjusted decision", "IMPLEMENTED",
     ["E[R] = sum_s p_s (V_s + D_s)/P - 1, weights 30/50/20 (EST)",
      "Weight uncertainty: w ~ Dirichlet(10 x [0.3,0.5,0.2]); P(E[R] > 17.5%)",
      "Hurdle 17.5% = ke 12.5% + 5pp; net of 0.55% costs and taxes",
      "Scorecard 1-5 against stated rules (judgement, not probabilities)"],
     "tapg_entry_and_tactical.py · final_decision.py"),
    ("9. Monitoring & feedback", "IMPLEMENTED",
     ["Append-only forecast journal (42 rows) and catalyst register (C-001..C-021)",
      "Price triggers (TAPG <= 1,525); consensus snapshots each run",
      "First out-of-sample resolutions: FY2026 results, Feb-Mar 2027",
      "Feedback (dashed arrow): resolved errors re-fit models in box 4"],
     "forecast_validation.py · tapg_monitor.py"),
]

VALIDATION_FACTS = [
    "Empirically validated signals: NONE yet (no indicator has an out-of-sample record).",
    "Engineering tests: 43 unit tests (identities, PIT ordering, idempotent journal, bounds); they test code, not forecasting skill.",
    "CPIN H1 (pre-registered, PIT walk-forward, n = 20): broiler-margin MAE 7.06pp vs mean 5.80pp, DM t -0.76 -> FAILED (D-031).",
    "Measured so far (PIT, TAPG profit, n = 2): MAPE 23.5% (price_last), 27.2% (last_q); bias negative (under-forecast).",
]
PLANNED = [
    "Resolve journal vs FY2026 actuals (C-020; Feb-Mar 2027): first real out-of-sample errors for TAPG/LSIP nowcasts",
    "Extend PIT history (2021-25 interim vintages) to n >= 12 quarters before any signal is called validated",
    "Forecast-error decomposition (volume / price / cost / inventory) on resolved quarters",
    "Poultry H2 (levels, post-hoc): forward test on CPIN (2026Q4 logged) and replication on JPFA before any use",
]


def box(ax, x, y, w, h, title, status, lines, src):
    edge, fill = ST[status]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012",
                                linewidth=2.2, edgecolor=edge, facecolor=fill))
    ax.text(x + 0.012, y + h - 0.022, title, fontsize=12.5, weight="bold", color="#1a1a1a", va="top")
    ax.text(x + w - 0.012, y + h - 0.022, status, fontsize=8.5, weight="bold", color=edge, va="top", ha="right")
    for i, ln in enumerate(lines):
        ax.text(x + 0.014, y + h - 0.058 - i * 0.0265, ln, fontsize=8.6, family="DejaVu Sans Mono", color="#222", va="top")
    ax.text(x + 0.014, y + 0.012, src, fontsize=7.6, style="italic", color="#555", va="bottom")


def main() -> None:
    fig = plt.figure(figsize=(20, 13.5), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(0.02, 0.975, "Indonesian Palm Oil Quantamental Research — Implemented Quantitative Methodology",
            fontsize=19, weight="bold", va="top")
    ax.text(0.02, 0.945, "As of 2026-11-25 (commit after Phase VII). Formulas as coded in the repository modules cited in each box. "
            "Current decision: NO TRADE (TAPG / LSIP / DSNG WATCH, STAA AVOID).", fontsize=10.5, color="#444", va="top")
    # 3 x 3 snake layout
    W, H = 0.300, 0.215
    xs = [0.015, 0.335, 0.655]
    ys = [0.705, 0.455, 0.205]
    order = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (2, 2)]
    pos = []
    for (r, c), st in zip(order, STAGES):
        box(ax, xs[c], ys[r], W, H, *st)
        pos.append((xs[c], ys[r]))
    arrow = dict(arrowstyle="-|>", lw=2.0, color="#333", mutation_scale=18)
    for i in range(len(pos) - 1):
        (x0, y0), (x1, y1) = pos[i], pos[i + 1]
        if y0 == y1:
            if x1 > x0:
                ax.annotate("", xy=(x1, y1 + H / 2), xytext=(x0 + W, y0 + H / 2), arrowprops=arrow)
            else:
                ax.annotate("", xy=(x1 + W, y1 + H / 2), xytext=(x0, y0 + H / 2), arrowprops=arrow)
        else:
            ax.annotate("", xy=(x1 + W / 2, y1 + H), xytext=(x0 + W / 2, y0), arrowprops=arrow)
    # feedback loop: monitoring -> models
    ax.annotate("", xy=(xs[2] + W + 0.004, ys[1] + H * 0.5), xytext=(xs[2] + W + 0.004, ys[2] + H * 0.5),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#2e7d32", ls="--", connectionstyle="arc3,rad=0.28", mutation_scale=16))
    # legend
    lx, ly = 0.02, 0.175
    for i, (k, (e, f)) in enumerate(ST.items()):
        ax.add_patch(FancyBboxPatch((lx + i * 0.16, ly - 0.012), 0.02, 0.016, boxstyle="round,pad=0.002", edgecolor=e, facecolor=f, lw=2))
        desc = {"IMPLEMENTED": "implemented (code + tests)", "EXPLORATORY": "exploratory (n too small)",
                "VALIDATED": "empirically validated (none yet)", "PLANNED": "planned improvement"}[k]
        ax.text(lx + i * 0.16 + 0.026, ly - 0.004, desc, fontsize=9.5, va="center")
    # validation facts and planned
    edge, fill = ST["VALIDATED"]
    ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.47, 0.125, boxstyle="round,pad=0.008", edgecolor=edge, facecolor=fill, lw=1.8))
    ax.text(0.03, 0.135, "Evidence status", fontsize=11.5, weight="bold", va="top")
    for i, t in enumerate(VALIDATION_FACTS):
        ax.text(0.03, 0.11 - i * 0.024, "• " + t, fontsize=8.7, va="top", wrap=True)
    edge, fill = ST["PLANNED"]
    ax.add_patch(FancyBboxPatch((0.51, 0.02), 0.47, 0.125, boxstyle="round,pad=0.008", edgecolor=edge, facecolor=fill, lw=1.8, ls="--"))
    ax.text(0.52, 0.135, "Planned research improvements (not implemented)", fontsize=11.5, weight="bold", va="top")
    for i, t in enumerate(PLANNED):
        ax.text(0.52, 0.108 - i * 0.024, "• " + t, fontsize=8.7, va="top")
    fig.savefig(OUT, dpi=200, facecolor="white")
    print(OUT)


if __name__ == "__main__":
    main()
