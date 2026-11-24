"""Small, dependency-free statistics helpers (numpy only): OLS with Newey-West (HAC)
standard errors, max drawdown, and lagged cross-correlation."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ols_nw(y: pd.Series, X: pd.DataFrame, lags: int | None = None) -> pd.DataFrame:
    """OLS of y on [const, X] with Newey-West (Bartlett) standard errors.
    Returns a table of coef, se, t and adds attributes r2 and nobs."""
    d = pd.concat([y.rename("y"), X], axis=1).dropna()
    yv = d["y"].to_numpy()
    Xv = np.column_stack([np.ones(len(d)), d.drop(columns="y").to_numpy()])
    n, k = Xv.shape
    if lags is None:
        lags = int(np.floor(4 * (n / 100) ** (2 / 9)))
    XtX_inv = np.linalg.inv(Xv.T @ Xv)
    b = XtX_inv @ Xv.T @ yv
    e = yv - Xv @ b
    u = Xv * e[:, None]
    S = u.T @ u
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        G = u[L:].T @ u[:-L]
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V))
    out = pd.DataFrame({"coef": b, "se_nw": se, "t_nw": b / se}, index=["const"] + list(X.columns))
    ss_tot = ((yv - yv.mean()) ** 2).sum()
    out.attrs.update(r2=1 - (e ** 2).sum() / ss_tot, nobs=n, nw_lags=lags)
    return out


def drawdowns(level: pd.Series) -> pd.DataFrame:
    """Drawdown episodes (peak, trough, recovery) from a price/total-return level series."""
    level = level.dropna()
    peak = level.cummax()
    dd = level / peak - 1
    eps, in_dd, start = [], False, None
    for t, v in dd.items():
        if v < 0 and not in_dd:
            in_dd, start = True, t
        if in_dd and v == 0:
            seg = dd[start:t]
            eps.append({"peak": start, "trough": seg.idxmin(), "recovery": t, "depth": seg.min()})
            in_dd = False
    if in_dd:
        seg = dd[start:]
        eps.append({"peak": start, "trough": seg.idxmin(), "recovery": pd.NaT, "depth": seg.min()})
    out = pd.DataFrame(eps)
    if not out.empty:
        out["peak"] = [level.index[max(level.index.get_loc(p) - 1, 0)] for p in out["peak"]]
    return out.sort_values("depth").reset_index(drop=True)


def lagged_corr(x: pd.Series, y: pd.Series, lags=range(-3, 4)) -> pd.DataFrame:
    """corr(x_{t-k}, y_t) for each k. Positive k means x LEADS y by k periods."""
    rows = []
    for k in lags:
        d = pd.concat([x.shift(k), y], axis=1).dropna()
        n = len(d)
        r = d.iloc[:, 0].corr(d.iloc[:, 1])
        rows.append({"lag_k": k, "corr": r, "n": n, "approx_se": 1 / np.sqrt(n) if n else np.nan})
    return pd.DataFrame(rows)
