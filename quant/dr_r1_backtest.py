"""DR-R1 palm CPO-impulse timing backtest (Phase XV). Executes DR_preregistration.json R1 exactly, with the
interpretations fixed in DR_R1_implementation.json (committed e56ed1a before any return was computed).

    python -I -X utf8 quant/dr_r1_backtest.py

Outputs (data/reference/research/):
  DR_R1_monthly.csv      signal, membership, gross/net returns, costs, turnover, cash, benchmark per month
  DR_R1_results.json     registered decision statistics, supplementary comparisons, attribution, robustness
  outputs/DR_R1_equity_drawdown.png
Robustness runs are report-only and never replace the primary result.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmarks import adj_close  # noqa: E402
from stats_utils import ols_nw  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
RES = REF / "research"
FIRST, LAST = pd.Period("2016-03", "M"), pd.Period("2026-10", "M")
SEED, BLOCK, REPS = 20261125, 6, 5000


# ---------------------------------------------------------------- inputs
def inputs():
    mm = pd.read_csv(REF / "macro_monthly.csv", index_col=0)
    mm.index = pd.PeriodIndex(mm.index, freq="M")
    cpo = mm["palm_oil_usd_t"] * mm["usdidr_month_avg"]
    pit = pd.read_csv(REF / "pit_universe_monthly.csv", parse_dates=["date"])
    ihsg = adj_close("IHSG")
    cal = ihsg.index
    me = cal.to_series().groupby(cal.to_period("M")).max()
    fm = cal.to_series().groupby(cal.to_period("M")).min()
    names = sorted(pit[pit.liquidity_band == "core_liquidity"].ticker.unique())
    px = pd.concat({t: adj_close(t) for t in names}, axis=1).sort_index().reindex(cal)
    rets = px.pct_change(fill_method=None)
    bi = pd.read_csv(REF / "bi_rate_history.csv", parse_dates=["decision_date"]).sort_values("decision_date")
    call = pd.read_csv(REF / "idr_call_money_monthly.csv", parse_dates=["month"])
    call.index = call.month.dt.to_period("M")
    return dict(cpo=cpo, pit=pit, ihsg=ihsg, cal=cal, me=me, fm=fm, rets=rets, bi=bi, call=call["call_money_pct"])


def cash_rate(D, d: pd.Timestamp, m: pd.Period, mode: str) -> float:
    if mode == "zero":
        return 0.0
    if mode == "call":
        return float(D["call"].get(m, np.nan)) / 100 / 12
    b = D["bi"][D["bi"].decision_date <= d]
    rate = float(b.bi_rate_pct.iloc[-1] if len(b) else D["bi"].bi_rate_pct.iloc[0])
    return (rate - (0.5 if mode == "bi_minus_50bp" else 0.0)) / 100 / 12


# ---------------------------------------------------------------- engine
def run(D, delay: int = 0, cost_mult: float = 1.0, exclude: set | None = None, cash_mode: str = "bi_minus_50bp",
        stale_excl: bool = False) -> pd.DataFrame:
    exclude = exclude or set()
    cal, me, rets, pit = D["cal"], D["me"], D["rets"], D["pit"]
    rows = []
    s_prev_inv, s_prev_w, b_prev_w = False, {}, {}
    for m in pd.period_range(FIRST, LAST, freq="M"):
        d = me[m - 1]                                   # formation date (last trading day of t)
        sig = float(np.log(D["cpo"][m - 2] / D["cpo"][m - 3]))   # CPO(t-1)/CPO(t-2), t = m-1
        mem = pit[(pit.date == d) & (pit.liquidity_band == "core_liquidity") & (~pit.ticker.isin(exclude))]
        adv = dict(zip(mem.ticker, mem.median_adv_idr_bn))
        i0 = cal.get_loc(d) + delay
        i1 = cal.get_loc(me[m]) + delay
        win = rets.iloc[i0 + 1:i1 + 1]
        names = [t for t in mem.ticker if t in rets.columns]
        if stale_excl:
            vol_ok = []
            for t in names:
                v = pd.read_csv(ROOT / "data" / "raw" / "ohlcv" / f"{t}.csv", index_col=0, parse_dates=True)["Volume"]
                z = (pd.to_numeric(v, errors="coerce").reindex(win.index).fillna(0) <= 0).sum()
                if z < 3:
                    vol_ok.append(t)
            names = vol_ok
        g = (1 + win[names].fillna(0.0)).cumprod().iloc[-1]
        R = float(g.mean() - 1)
        w_t = {t: 1 / len(names) for t in names}
        w_end = (g / g.sum()).to_dict()
        buy = {t: (0.0020 if adv.get(t, 0) >= 10 else 0.0045) * cost_mult for t in names}

        def sell_cost(w):
            out = 0.0
            for t, x in w.items():
                a = pit[(pit.date == d) & (pit.ticker == t)].median_adv_idr_bn
                big = (float(a.iloc[0]) if len(a) else 0) >= 10
                out += x * (0.0025 if big else 0.0055) * cost_mult
            return out

        def rebal(prev):
            ks = set(prev) | set(w_t)
            return sum(abs(w_t.get(k, 0) - prev.get(k, 0)) for k in ks)

        rc = cash_rate(D, d, m, cash_mode)
        # benchmark (always invested)
        if b_prev_w:
            b_turn = rebal(b_prev_w); b_cost = 0.003 * cost_mult * b_turn
        else:
            b_turn = 1.0; b_cost = sum(w_t[t] * buy[t] for t in names)
        b_net = (1 - b_cost) * (1 + R) - 1
        b_prev_w = w_end
        # strategy
        inv = sig > 0
        if inv and s_prev_inv:
            s_turn = rebal(s_prev_w); s_cost = 0.003 * cost_mult * s_turn; s_net = (1 - s_cost) * (1 + R) - 1
        elif inv:
            s_turn = 1.0; s_cost = sum(w_t[t] * buy[t] for t in names); s_net = (1 - s_cost) * (1 + R) - 1
        elif s_prev_inv:
            s_turn = 1.0; s_cost = sell_cost(s_prev_w); s_net = (1 - s_cost) * (1 + rc) - 1
        else:
            s_turn = 0.0; s_cost = 0.0; s_net = rc
        s_prev_inv, s_prev_w = inv, (w_end if inv else {})
        ih = D["ihsg"]
        rows.append(dict(month=str(m), formation_date=str(d.date()), signal_dlog_cpo_idr=sig, invested=inv,
                         n_members=len(names), members=" ".join(names), basket_gross=R, cash=rc,
                         strategy_cost=s_cost, strategy_turnover=s_turn, strategy_net=s_net,
                         benchmark_cost=b_cost, benchmark_turnover=b_turn, benchmark_net=b_net,
                         ihsg_price=float(ih.iloc[i1] / ih.iloc[i0] - 1),
                         cpo_idr_dlog_contemporaneous=float(np.log(D["cpo"][m] / D["cpo"][m - 1]))))
    return pd.DataFrame(rows).set_index("month")


# ---------------------------------------------------------------- statistics
def perf(r: pd.Series, rc: pd.Series) -> dict:
    w = (1 + r).cumprod()
    dd = w / w.cummax() - 1
    yrs = len(r) / 12
    cagr = float(w.iloc[-1] ** (1 / yrs) - 1)
    ex = r - rc
    down = ex[ex < 0]
    mdd = float(dd.min())
    return dict(final_wealth=float(w.iloc[-1]), cagr=cagr, ann_vol=float(r.std() * np.sqrt(12)),
                sharpe=float(ex.mean() / ex.std() * np.sqrt(12)),
                sortino=float(ex.mean() * 12 / (np.sqrt((down ** 2).sum() / len(ex)) * np.sqrt(12))),
                max_drawdown=mdd, calmar=float(cagr / abs(mdd)) if mdd < 0 else np.nan,
                monthly={"mean": float(r.mean()), "median": float(r.median()), "p05": float(r.quantile(.05)),
                         "p95": float(r.quantile(.95)), "min": float(r.min()), "max": float(r.max()),
                         "skew": float(r.skew()), "hit_rate": float((r > 0).mean())})


def hac_mean(x: pd.Series, lags: int = 3) -> dict:
    t = ols_nw(x.reset_index(drop=True), pd.DataFrame(index=range(len(x))), lags=lags).loc["const"]
    from scipy.stats import norm
    return dict(mean=float(t.coef), t=float(t.t_nw), p_one_sided=float(1 - norm.cdf(t.t_nw)),
                p_two_sided=float(2 * (1 - norm.cdf(abs(t.t_nw)))))


def block_boot_mean(x: np.ndarray) -> dict:
    rng = np.random.default_rng(SEED); n = len(x); nb = int(np.ceil(n / BLOCK)); out = np.empty(REPS)
    for k in range(REPS):
        st = rng.integers(0, n - BLOCK + 1, nb)
        out[k] = np.concatenate([x[s:s + BLOCK] for s in st])[:n].mean()
    return {"ci90_ann": [float(np.quantile(out, .05) * 12), float(np.quantile(out, .95) * 12)],
            "ci95_ann": [float(np.quantile(out, .025) * 12), float(np.quantile(out, .975) * 12)],
            "p_boot_le_0": float((out <= 0).mean())}


def decision_stats(M: pd.DataFrame) -> dict:
    s, b, rc = M.strategy_net, M.benchmark_net, M.cash
    ex = s - b
    h = hac_mean(ex)
    holm = min(1.0, 3 * h["p_one_sided"])
    half = len(ex) // 2
    ps, pb = perf(s, rc), perf(b, rc)
    crit = {"ann_excess_ge_3pct": bool(12 * ex.mean() >= 0.03),
            "holm_p_le_0_05": bool(holm <= 0.05),
            "positive_both_halves": bool(ex.iloc[:half].mean() > 0 and ex.iloc[half:].mean() > 0),
            "mdd_not_worse": bool(ps["max_drawdown"] >= pb["max_drawdown"])}
    return dict(n_months=len(ex), ann_excess_arith=float(12 * ex.mean()), cagr_diff=ps["cagr"] - pb["cagr"],
                hac=h, holm_adjusted_p=holm, holm_note="family R1-R3; R2, R3 untested -> p=1; adjusted = min(1, 3p)",
                halves={"first": [M.index[0], M.index[half - 1], float(12 * ex.iloc[:half].mean())],
                        "second": [M.index[half], M.index[-1], float(12 * ex.iloc[half:].mean())]},
                bootstrap=block_boot_mean(ex.to_numpy()), strategy=ps, benchmark=pb, criteria=crit,
                passes_registered_rule=bool(all(crit.values())))


def attribution(M: pd.DataFrame) -> dict:
    s, b, rc, ih = M.strategy_net, M.benchmark_net, M.cash, M.ihsg_price
    y = s - rc
    X = pd.DataFrame({"mkt_ihsg": ih - rc, "sector_basket_minus_ihsg": b - ih, "cpo_idr_dlog": M.cpo_idr_dlog_contemporaneous})
    def tab(o):
        return {k: {"coef": float(o.loc[k, "coef"]), "t_nw": float(o.loc[k, "t_nw"])} for k in o.index} | {"r2": float(o.attrs["r2"])}
    full = ols_nw(y, X, lags=3)
    mkt = ols_nw(y, X[["mkt_ihsg"]], lags=3)
    bas = ols_nw(y, pd.DataFrame({"basket_ex_cash": b - rc}), lags=3)
    xb = b - rc
    tm = ols_nw(y, pd.DataFrame({"basket_ex_cash": xb, "basket_ex_cash_sq": xb ** 2}), lags=3)
    hm = ols_nw(y, pd.DataFrame({"basket_ex_cash": xb, "up_market": xb.clip(lower=0)}), lags=3)
    inv = M.invested.mean()
    # constant-mix (basket weight = time invested), monthly rebalanced: cost 0.3% on the drift traded back (both legs)
    drift = inv * (1 + b) / (inv * (1 + b) + (1 - inv) * (1 + rc))
    mix = (inv * b + (1 - inv) * rc) - 0.003 * 2 * np.abs(drift - inv).shift(1).fillna(0)
    return dict(alpha_ann_full=float(full.loc["const", "coef"] * 12), full=tab(full),
                capm_ihsg=tab(mkt) | {"alpha_ann": float(mkt.loc["const", "coef"] * 12)},
                basket_beta=tab(bas) | {"alpha_ann": float(bas.loc["const", "coef"] * 12)},
                treynor_mazuy=tab(tm), henriksson_merton=tab(hm), time_invested=float(inv),
                constant_mix_same_exposure={"perf": perf(mix, rc), "excess_vs_mix": hac_mean(s - mix),
                                            "ann_excess_vs_mix": float(12 * (s - mix).mean())},
                signal_hit_rate={"invested_months_basket_beats_cash": float(((b - rc)[M.invested] > 0).mean()),
                                 "cash_months_basket_beats_cash": float(((b - rc)[~M.invested] > 0).mean()),
                                 "mean_basket_ex_cash_when_invested": float((b - rc)[M.invested].mean()),
                                 "mean_basket_ex_cash_when_cash": float((b - rc)[~M.invested].mean())})


def plot(M: pd.DataFrame, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    idx = pd.PeriodIndex(M.index, freq="M").to_timestamp(how="end")
    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    for c, lab, col in [("strategy_net", "R1 strategy (net)", "#1f5aa6"), ("benchmark_net", "Palm basket buy-and-hold (net, registered benchmark)", "#c0504d"),
                        ("ihsg_price", "IHSG (price only)", "#7f7f7f"), ("cash", "Cash (BI-Rate - 0.5pp)", "#2e8b57")]:
        w = (1 + M[c]).cumprod()
        ax[0].plot(idx, w, label=lab, color=col, lw=1.6 if c == "strategy_net" else 1.1)
        if c in ("strategy_net", "benchmark_net"):
            ax[1].plot(idx, w / w.cummax() - 1, color=col, lw=1.2)
    ax[0].set_ylabel("Wealth (start = 1)"); ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=.3)
    ax[0].set_title("DR-R1 palm CPO-impulse timing, 2016-03 to 2026-10 (historical backtest, not alpha proof)")
    ax[1].set_ylabel("Drawdown"); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def main() -> dict:
    D = inputs()
    M = run(D)
    M.to_csv(RES / "DR_R1_monthly.csv", float_format="%.6f")
    res = {"spec": "DR_preregistration.json R1 + DR_R1_implementation.json", "primary": decision_stats(M)}
    rc = M.cash
    res["supplementary_not_decision"] = {
        "passive_palm_basket_gross_no_costs": perf(M.basket_gross, rc),
        "ihsg_price_only": perf(M.ihsg_price, rc),
        "money_market": perf(rc, rc) | {"note": "Sharpe/Sortino undefined vs itself"},
        "costs": {"strategy_total_cost_sum": float(M.strategy_cost.sum()), "strategy_cost_ann": float(M.strategy_cost.mean() * 12),
                  "benchmark_cost_ann": float(M.benchmark_cost.mean() * 12),
                  "strategy_turnover_ann": float(M.strategy_turnover.mean() * 12), "benchmark_turnover_ann": float(M.benchmark_turnover.mean() * 12),
                  "switches": int((M.invested != M.invested.shift(1)).iloc[1:].sum())},
        "time_invested": float(M.invested.mean())}
    res["attribution"] = attribution(M)
    rob = {}
    for name, kw in {"delay_1_trading_day": dict(delay=1), "costs_x2": dict(cost_mult=2.0),
                     "exclude_BTEK_PALM": dict(exclude={"BTEK", "PALM"}), "exclude_stale_member_months": dict(stale_excl=True),
                     "cash_BI_rate": dict(cash_mode="bi"), "cash_call_money": dict(cash_mode="call"), "cash_zero": dict(cash_mode="zero")}.items():
        R = run(D, **kw); ds = decision_stats(R)
        rob[name] = {k: ds[k] for k in ("ann_excess_arith", "holm_adjusted_p", "criteria", "passes_registered_rule")} | \
                    {"strategy_cagr": ds["strategy"]["cagr"], "benchmark_cagr": ds["benchmark"]["cagr"],
                     "strategy_mdd": ds["strategy"]["max_drawdown"], "benchmark_mdd": ds["benchmark"]["max_drawdown"]}
    res["robustness_report_only"] = rob
    (RES / "DR_R1_results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    plot(M, ROOT / "outputs" / "DR_R1_equity_drawdown.png")
    return res


if __name__ == "__main__":
    r = main()
    p = r["primary"]
    print(json.dumps({k: p[k] for k in ("n_months", "ann_excess_arith", "cagr_diff", "hac", "holm_adjusted_p", "halves", "bootstrap", "criteria", "passes_registered_rule")}, indent=1, default=float))
    print("strategy", {k: round(v, 4) for k, v in p["strategy"].items() if k != "monthly"})
    print("benchmark", {k: round(v, 4) for k, v in p["benchmark"].items() if k != "monthly"})
