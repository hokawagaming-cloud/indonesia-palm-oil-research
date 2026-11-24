"""Monthly CHIRPS v3.0 rainfall averaged over the main oil palm provinces (source S-007).

Reads one Cloud-Optimised GeoTIFF window per month over HTTP (no full global download)
and averages land pixels inside each province's bounding box.

Regions are APPROXIMATE rectangles (assumption A-009), not province polygons and not
estate locations. They are a regional proxy until estate coordinates are available
from company annual reports.

Output: data/processed/chirps_monthly_regions.csv (git-ignored; reproducible)
        data/reference/chirps_monthly_regions.csv (tracked copy; CHIRPS is public)
Usage:  python -I quant/fetch_chirps.py [start YYYY-MM] [end YYYY-MM]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[1]
URL = "/vsicurl/https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs/chirps-v3.0.{y}.{m:02d}.cog"

# (lon_min, lat_min, lon_max, lat_max) - approximate bounding boxes (A-009)
REGIONS = {
    "north_sumatra": (97.0, 1.0, 100.5, 4.3),
    "riau": (100.0, -1.2, 104.0, 2.5),
    "jambi": (101.2, -2.8, 104.5, -0.7),
    "south_sumatra": (102.0, -4.9, 106.2, -1.6),
    "west_kalimantan": (108.8, -3.1, 114.2, 2.1),
    "central_kalimantan": (110.7, -3.6, 115.8, 0.8),
    "east_kalimantan": (113.8, -2.4, 119.0, 2.0),
    "south_kalimantan": (114.3, -4.2, 116.6, -1.3),
}
OUTER = (96.5, -5.0, 119.5, 4.5)


def read_month(y: int, m: int) -> dict:
    with rasterio.open(URL.format(y=y, m=m)) as src:
        win = from_bounds(*OUTER, transform=src.transform)
        arr = src.read(1, window=win).astype("float64")
        tr = src.window_transform(win)
    arr[arr < 0] = np.nan  # ocean / no-data are negative
    rows, cols = arr.shape
    lons = tr.c + tr.a * (np.arange(cols) + 0.5)
    lats = tr.f + tr.e * (np.arange(rows) + 0.5)
    out = {}
    for name, (x0, y0, x1, y1) in REGIONS.items():
        cmask = (lons >= x0) & (lons <= x1)
        rmask = (lats >= y0) & (lats <= y1)
        sub = arr[np.ix_(rmask, cmask)]
        out[name] = float(np.nanmean(sub)) if np.isfinite(sub).any() else np.nan
        out[f"{name}_valid_px"] = int(np.isfinite(sub).sum())
    return out


def main(start: str = "2015-01", end: str | None = None) -> int:
    months = pd.period_range(start, end or pd.Timestamp.today().strftime("%Y-%m"), freq="M")
    rows = []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MAX_RETRY="3",
                      GDAL_HTTP_RETRY_DELAY="2"):
        for p in months:
            try:
                r = read_month(p.year, p.month)
                r["month"] = str(p)
                rows.append(r)
            except Exception as exc:  # month not yet published, or network error
                rows.append({"month": str(p), "error": str(exc)[:120]})
                print(f"{p}: {exc}", file=sys.stderr)
    df = pd.DataFrame(rows).set_index("month")
    for d in (ROOT / "data" / "processed", ROOT / "data" / "reference"):
        d.mkdir(parents=True, exist_ok=True)
        df.to_csv(d / "chirps_monthly_regions.csv")
    print(df[list(REGIONS)].describe().round(1).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
