"""LSIP oil-palm age-cohort model (Phase XVII).

    python -I -X utf8 valuation/lsip_cohort.py

1. Reconstruct a planting-year distribution H(y) (ha planted in year y, nucleus oil palm) consistent with the
   reported age bands FY2017-FY2023 (immature = ages 0-3, 4-6, 7-20, >20) and the reported immature area FY2024-25,
   by non-negative least squares with a smoothness penalty. Cohorts planted <= 1996 ("old stock") are only
   observed as an aggregate; their age spread is set so that the reported average age (18 or 19 years, end-2023)
   holds. Several feasible distributions (smoothing x average age x old-stock shape) form an ENSEMBLE whose spread
   is propagated into production and value. Detailed cohorts are NOT disclosed: this is a reconstruction.
2. Yield curve: a literature-shaped standard curve (t FFB/ha by age) -- an ANALYST ASSUMPTION broadly consistent
   with published oil-palm age-yield profiles (e.g. Corley & Tinker, The Oil Palm, 5th ed.) -- scaled to LSIP by a
   productivity factor k fitted to reported nucleus FFB FY2017-FY2025. It is not an empirically validated
   LSIP-specific age-yield relationship (LSIP does not disclose yield by age).
3. Roll the cohorts forward 2026-2050 under four replanting scenarios (A historical pace, B accelerated toward the
   sustainable replacement rate, C deferred, D intensive oldest-first), tracking A(a+1,t+1) = A(a,t) - R(a,t),
   A(0,t+1) = planted in t, FFB(t) = sum_a A(a,t) y(a) k(cohort).

Outputs: data/reference/research/LSIP_cohort_reconstruction.csv, LSIP_cohort_scenarios.csv,
         LSIP_cohort_ensemble.csv, LSIP_cohort_calibration.csv, LSIP_cohort_summary.json
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
AGE = pd.read_csv(RES / "LSIP_age_profile.csv")
OPS = pd.read_csv(RES / "LSIP_operational_annual.csv", index_col=0)

Y0, Y1 = 1997, 2025                     # planting years solved explicitly
OLD_LAST = Y0 - 1                       # 1996: last planting year of the aggregate "old stock"
MAXAGE = 45

# ---- standard yield curve (t FFB / ha / yr) by age at mid-year; ANALYST ASSUMPTION (see module docstring) ----
_pts = {0: 0, 1: 0, 2: 0, 3: 7, 4: 13, 5: 17, 6: 20, 7: 22, 8: 24, 9: 25, 14: 25, 18: 24, 20: 22, 25: 17, 30: 12, 35: 9, 45: 7}
YIELD = np.interp(np.arange(MAXAGE + 1), list(_pts), list(_pts.values()))


def yield_curve(decline_mult: float = 1.0) -> np.ndarray:
    """Standard curve; decline_mult scales the post-age-18 decline (sensitivity)."""
    y = YIELD.copy()
    a = np.arange(MAXAGE + 1)
    old = a > 18
    y[old] = np.maximum(YIELD[18] - (YIELD[18] - YIELD[old]) * decline_mult, 3.0)
    return y


def reconstruct(lam: float) -> tuple[pd.Series, pd.DataFrame]:
    Y = np.arange(Y0, Y1 + 1); n = len(Y); ix = {y: i for i, y in enumerate(Y)}
    rows, b, lab = [], [], []

    def eq(lo, hi, val, name):
        r = np.zeros(n)
        for y in range(lo, hi + 1):
            r[ix[y]] = 1
        rows.append(r); b.append(val); lab.append(name)
    for _, a in AGE.dropna(subset=["total"]).iterrows():
        t = int(a.date[:4])
        eq(t - 3, t, a.immature, f"{t} immature"); eq(t - 6, t - 4, a.a4_6, f"{t} 4-6"); eq(t - 20, t - 7, a.a7_20, f"{t} 7-20")
    for t in (2024, 2025):
        eq(t - 3, t, OPS.loc[f"FY{t}", "op_immature"], f"{t} immature")
    M, b = np.array(rows), np.array(b)
    D = np.diff(np.eye(n), 2, axis=0) * np.sqrt(lam)
    s = lsq_linear(np.vstack([M, D]), np.concatenate([b, np.zeros(len(D))]), bounds=(0, np.inf))
    H = pd.Series(s.x, index=Y)
    fit = pd.DataFrame({"equation": lab, "reported": b, "fitted": M @ s.x})
    return H, fit


def old_stock(H: pd.Series, avg_age: float, shape: str) -> pd.Series:
    """Old-stock (planted <= 1996) area by planting year at end-2023 such that the end-2023 average age equals
    avg_age. shape: 'front' (mass near 1994-96, the mid-1990s expansion) or 'spread' (uniform back to the
    earliest year needed). Returns ha by planting year."""
    a23 = AGE[AGE.date == "2023-12-31"].dropna(subset=["total"]).iloc[0]
    young = H[H.index <= 2023]
    young_ages = 2023 - young.index.values
    area_old = a23.gt20 - young[young.index <= 2002].sum()
    target_sum = avg_age * a23.total - (young.values * (young_ages + 0.5)).sum()
    m = target_sum / area_old - 0.5                       # mean age (end-year) of old stock
    m = max(m, 2023 - OLD_LAST + 0.5)                     # feasibility floor: old stock is >= 27 years old
    # choose span so that mean matches: 'front' = triangular declining from 1996 backwards, 'spread' = uniform
    for span in range(1, 30):
        yrs = np.arange(OLD_LAST - span + 1, OLD_LAST + 1)
        w = np.linspace(1, 0.25, span)[::-1] if shape == "front" else np.ones(span)
        w = w / w.sum()
        if ((2023 - yrs) * w).sum() >= m:
            break
    return pd.Series(area_old * w, index=yrs)


def state_2023(H, old) -> pd.Series:
    """Area by age at end-2023 (age = 2023 - planting year)."""
    s = pd.Series(0.0, index=np.arange(MAXAGE + 1))
    for y, v in pd.concat([old, H[H.index <= 2023]]).items():
        s[min(2023 - y, MAXAGE)] += v
    return s


def roll(state: pd.Series, plant: float, remove_total: float, kmult_state: pd.Series, k_new: float):
    """One year: remove `remove_total` ha oldest-first (replanting + disposals), age by one year, add plantings.
    kmult_state carries each cohort's productivity factor (new plantings get k_new)."""
    s, km = state.copy(), kmult_state.copy()
    r = remove_total
    for a in range(MAXAGE, -1, -1):
        if r <= 0:
            break
        take = min(s[a], r); s[a] -= take; r -= take
    s2 = pd.Series(0.0, index=s.index); k2 = pd.Series(km.mean(), index=s.index)
    s2[1:] = s.values[:-1]; s2[MAXAGE] += s[MAXAGE]
    k2[1:] = km.values[:-1]
    s2[0] = plant; k2[0] = k_new
    return s2, k2


def ffb(state, kstate, yc) -> float:
    """t FFB from a year-end state applied to the following year (ages +0.5 handled by using age+1 yields)."""
    ages = np.minimum(state.index.values + 1, MAXAGE)
    return float((state.values * yc[ages] * kstate.values).sum())


def back_states(H, old, yc):
    """States at end of 2016-2024 for calibration (old stock: the area later replanted was the oldest)."""
    out = {}
    a = AGE.dropna(subset=["total"]).set_index(AGE.dropna(subset=["total"]).date.str[:4].astype(int))
    for t in range(2016, 2025):
        s = pd.Series(0.0, index=np.arange(MAXAGE + 1))
        for y, v in H[H.index <= t].items():
            s[t - y] += v
        # old-stock area at t: reported >20 minus young cohorts aged > 20 (identity); 2024 from total oil palm
        if t in a.index:
            old_area = a.loc[t, "gt20"] - H[H.index <= t - 21].sum()
        elif t == 2016:
            old_area = a.loc[2017, "gt20"] - H[H.index <= 2016 - 21].sum()
        else:
            old_area = OPS.loc[f"FY{t}", "oil_palm"] - s.sum()
        ages = (t - old.index.values)
        w = old.values / old.values.sum()
        extra = max(old_area - old.sum(), 0)          # area replanted later: assume the oldest, add at max age+1..
        for ag, ww in zip(ages, w):
            s[min(ag, MAXAGE)] += ww * min(old_area, old.sum())
        if extra > 0:
            s[min(ages.max() + 1, MAXAGE)] += extra
        out[t] = s
    return out


SCEN = {
    "A_historical": "Continue the reconstructed 2017-2025 planting pace",
    "B_accelerated": "Ramp to the sustainable replacement rate (oil-palm area / 25-year cycle) by 2028",
    "C_deferred": "800 ha/yr 2026-2030 to preserve near-term output and cash, then historical pace",
    "D_intensive": "5,000 ha/yr oldest-first until no palms older than 25, then the sustainable rate",
}


def scenario_plan(name: str, t: int, hist: float, sustain: float, state: pd.Series) -> float:
    if name == "A_historical":
        return hist
    if name == "B_accelerated":
        return {2026: hist + (sustain - hist) / 3, 2027: hist + 2 * (sustain - hist) / 3}.get(t, sustain)
    if name == "C_deferred":
        return 800.0 if t <= 2030 else hist
    if name == "D_intensive":
        return 5000.0 if state[26:].sum() > 1 else sustain
    raise KeyError(name)


def project(H, old, yc, k_hist, uplift, name, disposal_2026=1467.0, cycle=25.0):
    # end-2025 state: roll 2023 -> 2025 using reconstructed plantings and the reported oil-palm area
    s = state_2023(H, old); km = pd.Series(k_hist, index=s.index)
    for t in (2024, 2025):
        rem = s.sum() + H[t] - OPS.loc[f"FY{t}", "oil_palm"]
        s, km = roll(s, H[t], rem, km, k_hist * (1 + uplift))
    hist = float(H.loc[2017:2025].mean())
    sustain = (OPS.loc["FY2025", "oil_palm"] - disposal_2026) / cycle
    rows = []
    for t in range(2026, 2051):
        plant = scenario_plan(name, t, hist, sustain, s)
        dispose = disposal_2026 if t == 2026 else 0.0
        out_ffb_state = s.copy()
        # replanted area is cleared at the start of the year: production uses the post-clearing state
        s_clear = s.copy(); r = plant + dispose
        for a in range(MAXAGE, -1, -1):
            if r <= 0:
                break
            take = min(s_clear[a], r); s_clear[a] -= take; r -= take
        prod = ffb(s_clear, km, yc)
        lost = ffb(out_ffb_state, km, yc) - prod
        s, km = roll(s, plant, plant + dispose, km, k_hist * (1 + uplift))
        ages = s.index.values
        rows.append({"scenario": name, "year": t, "replant_ha": plant, "disposal_ha": dispose, "area_ha": s.sum(),
                     "immature_ha": s[:4].sum(), "mature_ha": s[4:].sum(), "gt20_ha": s[21:].sum(), "gt25_ha": s[26:].sum(),
                     "avg_age": float((s.values * (ages + 0.5)).sum() / s.sum()), "ffb_nucleus_kt": prod / 1000,
                     "ffb_lost_to_replanting_kt": lost / 1000,
                     "yield_t_ha_mature": prod / max(s_clear[3:].sum(), 1)})
    return pd.DataFrame(rows)


def calibrate(H, old, yc):
    """k(t) = reported nucleus FFB / (sum_a A(a,t-1) y(a+1)) for 2017-2025; base k = FY2021-25 mean (ANALYST)."""
    st = back_states(H, old, yc)
    rows = []
    for t in range(2017, 2026):
        pot = ffb(st[t - 1], pd.Series(1.0, index=st[t - 1].index), yc)
        rows.append({"year": t, "reported_ffb_kt": OPS.loc[f"FY{t}", "ffb_nucleus"], "standard_curve_ffb_kt": pot / 1000,
                     "k": OPS.loc[f"FY{t}", "ffb_nucleus"] * 1000 / pot})
    return pd.DataFrame(rows)


def steady_state_yield(yc, cycle=25) -> float:
    """t FFB per planted ha (all ages) under a uniform replacement cycle, standard curve (k = 1)."""
    ages = np.arange(cycle)
    return float(yc[np.minimum(ages + 1, MAXAGE)].mean())


LR_RATE = {"A_historical": "hist", "B_accelerated": "sustain", "C_deferred": "hist", "D_intensive": "sustain"}


def steady_states(r, area=89331.0) -> dict:
    """Terminal steady state per scenario: the scenario's long-run planting rate held forever, i.e. a uniform age
    distribution over a replacement cycle = area / rate, all area on replanted material (k_new). This is what the
    terminal value capitalises -- productivity is NOT assumed to persist without reinvestment."""
    hist = float(r["H"].loc[2017:2025].mean()); sustain = area / 25.0
    k_new = r["k"] * 1.15
    out = {}
    for n in SCEN:
        rate = hist if LR_RATE[n] == "hist" else sustain
        cyc = area / rate; ages = np.arange(int(round(cyc)))
        yl = r["yc"][np.minimum(ages + 1, MAXAGE)]
        out[n] = {"replant_ha": rate, "cycle_years": cyc, "ffb_nucleus_kt": area * yl.mean() * k_new / 1000,
                  "mature_ha": area * (len(ages) - 4) / len(ages), "immature_ha": area * 4 / len(ages),
                  "avg_age": float(ages.mean() + 0.5), "gt20_ha": area * max(len(ages) - 21, 0) / len(ages)}
    return out


def run(lam=0.5, avg_age=19.0, shape="front", uplift=0.15, decline=1.0):
    yc = yield_curve(decline)
    H, fit = reconstruct(lam)
    old = old_stock(H, avg_age, shape)
    cal = calibrate(H, old, yc)
    k_hist = float(cal[cal.year >= 2021].k.mean())        # recent regime FY2021-25 (2017-25 mean reported too)
    sc = pd.concat([project(H, old, yc, k_hist, uplift, n) for n in SCEN], ignore_index=True)
    return dict(H=H, fit=fit, old=old, cal=cal, k=k_hist, sc=sc, yc=yc)


def main():
    base = run()
    H, fit, old, cal, sc = base["H"], base["fit"], base["old"], base["cal"], base["sc"]
    recon = pd.concat([old.rename("ha").to_frame().assign(kind="old stock (reconstructed spread)"),
                       H.rename("ha").to_frame().assign(kind="planting year (NNLS fit)")])
    recon.index.name = "planting_year"
    recon.to_csv(RES / "LSIP_cohort_reconstruction.csv", float_format="%.1f")
    fit.to_csv(RES / "LSIP_cohort_fit.csv", index=False, float_format="%.1f")
    cal.to_csv(RES / "LSIP_cohort_calibration.csv", index=False, float_format="%.4f")
    sc.to_csv(RES / "LSIP_cohort_scenarios.csv", index=False, float_format="%.3f")
    # ensemble: smoothing x reported average age (AR 19 / SR 18) x old-stock shape x yield decline
    ens = []
    for lam, aa, shp, dec in itertools.product((0.05, 0.5, 5.0), (18.0, 19.0), ("front", "spread"), (0.75, 1.0, 1.25)):
        r = run(lam, aa, shp, 0.15, dec)
        for n, g in r["sc"].groupby("scenario"):
            ens.append({"lam": lam, "avg_age_2023": aa, "old_shape": shp, "decline_mult": dec, "scenario": n, "k": r["k"],
                        "hist_rate": float(r["H"].loc[2017:2025].mean()),
                        "ffb_2030": g.set_index("year").loc[2030, "ffb_nucleus_kt"],
                        "ffb_2035": g.set_index("year").loc[2035, "ffb_nucleus_kt"],
                        "ffb_2050": g.set_index("year").loc[2050, "ffb_nucleus_kt"],
                        "ffb_cum_2026_2050": g.ffb_nucleus_kt.sum(), "avg_age_2030": g.set_index("year").loc[2030, "avg_age"],
                        "old_mean_age_2023": float(((2023 - r["old"].index) * r["old"]).sum() / r["old"].sum())})
    E = pd.DataFrame(ens); E.to_csv(RES / "LSIP_cohort_ensemble.csv", index=False, float_format="%.3f")
    a23 = AGE[AGE.date == "2023-12-31"].dropna(subset=["total"]).iloc[0]
    st25 = None
    summ = {
        "k_hist_2021_2025_base": base["k"], "k_mean_2017_2025": float(cal.k.mean()), "k_by_year": dict(zip(cal.year.astype(str), cal.k.round(4))),
        "hist_planting_rate_2017_2025_ha": float(H.loc[2017:2025].mean()),
        "hist_planting_rate_range_ensemble": [float(E.hist_rate.min()), float(E.hist_rate.max())],
        "sustainable_rate_ha_25y": float((OPS.loc["FY2025", "oil_palm"] - 1467) / 25),
        "sustainable_rate_ha_22y": float((OPS.loc["FY2025", "oil_palm"] - 1467) / 22),
        "implied_cycle_years_at_hist_rate": float(OPS.loc["FY2025", "oil_palm"] / H.loc[2017:2025].mean()),
        "fit_max_abs_residual_ha": float((fit.fitted - fit.reported).abs().max()),
        "fit_mean_abs_residual_ha": float((fit.fitted - fit.reported).abs().mean()),
        "old_stock_mean_age_2023": float(((2023 - old.index) * old).sum() / old.sum()),
        "gt20_share_2023_reported": float(a23.gt20_share),
        "steady_state_yield_per_planted_ha_k1": steady_state_yield(base["yc"]),
        "steady_state_yield_per_mature_ha_k1": float(base["yc"][np.arange(4, 26)].mean()),
        "scenarios": SCEN,
        "steady_state": steady_states(base),
        "ensemble_ffb_2035_range": {n: [float(g.ffb_2035.min()), float(g.ffb_2035.median()), float(g.ffb_2035.max())] for n, g in E.groupby("scenario")},
        "ensemble_ffb_2050_range": {n: [float(g.ffb_2050.min()), float(g.ffb_2050.median()), float(g.ffb_2050.max())] for n, g in E.groupby("scenario")},
    }
    (RES / "LSIP_cohort_summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(json.dumps(summ, indent=1))
    print(cal.to_string())
    print(sc[sc.year.isin([2026, 2027, 2030, 2035, 2040, 2050])].to_string())


if __name__ == "__main__":
    main()
