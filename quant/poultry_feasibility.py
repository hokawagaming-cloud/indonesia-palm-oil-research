"""Poultry pilot data-feasibility test (Phase VIII). Tests what is ACTUALLY retrievable, not what
is listed. Writes:
  data/raw/macro/pihps_poultry/*.json            raw PIHPS responses (git-ignored raw store)
  data/reference/poultry_prices_monthly.csv      national monthly series + feed-cost proxy
  data/reference/research/poultry_feasibility.csv   dataset-by-dataset verdict with evidence
Sources: S-054 PIHPS (Bank Indonesia), S-003 World Bank CMO (maize, soybean meal), USD/IDR (S-002),
Yahoo for CPIN/JPFA/MAIN (S-002/S-036). Probe results for sites that could not be scripted
(Bapanas, PINSAR, IDX, BPS) were obtained in this session and are recorded as evidence text.

Usage: python -I -X utf8 quant/poultry_feasibility.py
"""
from __future__ import annotations

import json
import time
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
RAW = ROOT / "data" / "raw" / "macro" / "pihps_poultry"
BASE = "https://www.bi.go.id/hargapangan/"
UA = "Mozilla/5.0 (research client)"
SERIES = {  # (price_type_id, comcat_id): name. PIHPS price types: 1 traditional retail, 3 wholesale, 4 producer
    (1, "cat_2"): "chicken_retail", (3, "cat_2"): "chicken_wholesale", (4, "cat_2"): "chicken_producer",
    (1, "cat_4"): "egg_retail", (3, "cat_4"): "egg_wholesale", (4, "cat_4"): "egg_producer"}
FEED_W = {"maize": 0.55, "soybean_meal": 0.25}   # EST broiler-feed inclusion shares; proxy only, not a cost model


def _opener():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    op.addheaders = [("User-Agent", UA), ("X-Requested-With", "XMLHttpRequest"),
                     ("Referer", BASE + "TabelHarga/ProdusenKomoditas")]
    op.open(BASE + "TabelHarga/ProdusenKomoditas", timeout=30).read()   # session cookie
    return op


def fetch_pihps(end: str = "2026-11-25") -> pd.DataFrame:
    RAW.mkdir(parents=True, exist_ok=True)
    op = _opener()
    out = {}
    for (pt, cat), name in SERIES.items():
        vals = {}
        for y in range(2017, int(end[:4]) + 1):
            s, e = f"{y}-01-01", (end if y == int(end[:4]) else f"{y}-12-31")
            url = (f"{BASE}WebSite/TabelHarga/GetGridDataKomoditas?price_type_id={pt}&comcat_id={cat}&province_id=&regency_id="
                   f"&showKota=false&showPasar=false&tipe_laporan=3&start_date={s}&end_date={e}")
            txt = op.open(url, timeout=120).read().decode("utf-8")
            (RAW / f"{name}_{y}.json").write_text(txt, encoding="utf-8")
            rows = json.loads(txt)["data"]
            nat = next((r for r in rows if r.get("level") == 0), None)
            if nat:
                for k, v in nat.items():
                    if k not in ("no", "name", "level") and v not in ("-", "", None):
                        vals[pd.Period(pd.to_datetime(k, format="%b %Y"), "M")] = float(str(v).replace(",", ""))
            time.sleep(0.5)
        out[name] = pd.Series(vals)
    return pd.DataFrame(out).sort_index()


def cmo_feed() -> pd.DataFrame:
    df = pd.read_excel(ROOT / "data" / "raw" / "macro" / "CMO-Historical-Data-Monthly.xlsx", "Monthly Prices", header=None)
    hdr, d = df.iloc[4], df.iloc[6:]
    col = {hdr[i]: i for i in range(len(hdr))}
    idx = pd.PeriodIndex([pd.Period(str(x).replace("M", "-"), "M") for x in d[0]], freq="M")
    f = pd.DataFrame({"maize_usd_t": pd.to_numeric(d[col["Maize"]], errors="coerce").to_numpy(),
                      "soybean_meal_usd_t": pd.to_numeric(d[col["Soybean meal"]], errors="coerce").to_numpy()}, index=idx)
    mac = pd.read_csv(REF / "macro_monthly.csv", index_col=0)
    mac.index = pd.PeriodIndex(mac.index, freq="M")
    f["usdidr"] = mac.usdidr_month_avg
    f["feed_proxy_idr_kg"] = (FEED_W["maize"] * f.maize_usd_t + FEED_W["soybean_meal"] * f.soybean_meal_usd_t) * f.usdidr / 1000
    return f


def equities() -> pd.DataFrame:
    import yfinance as yf
    rows = []
    for t in ("CPIN", "JPFA", "MAIN"):
        tk = yf.Ticker(f"{t}.JK")
        h = tk.history(period="max", auto_adjust=False)
        q = tk.quarterly_income_stmt
        e = tk.earnings_estimate
        rows.append({"ticker": t, "price_history_from": h.index.min().date().isoformat(), "n_days": len(h),
                     "median_traded_value_60d_bn": float((h.Close * h.Volume).iloc[-60:].median() / 1e9),
                     "yahoo_quarterly_is_n": q.shape[1],
                     "consensus_fy26_n_analysts": float(e.loc["0y", "numberOfAnalysts"]) if "0y" in e.index else np.nan,
                     "consensus_fy27_n_analysts": float(e.loc["+1y", "numberOfAnalysts"]) if "+1y" in e.index else np.nan})
    return pd.DataFrame(rows).set_index("ticker")


# Evidence recorded from this session's probes (2026-11-25); 'verdict' uses: AVAILABLE / PARTIAL / NOT AVAILABLE / NOT VERIFIED
PROBES = [
    ("Livebird price (farm gate)", "PINSAR pinsar.id/harga", "NOT AVAILABLE",
     "Page shows only month-to-date provincial averages (all blank on 2026-11-25); history only via 'Minta Data Lainnya' (request)."),
    ("Livebird price (farm gate)", "Bapanas Panel Harga (Ayam Ras Pedaging Hidup, producer)", "NOT VERIFIED",
     "Commodity listed; API api-panelhargav2.badanpangan.go.id returns 401 'Invalid or missing API key'; front-end showed 'Harga Belum Tersedia'; no export found."),
    ("DOC price", "PINSAR / Bapanas / PIHPS", "NOT AVAILABLE",
     "No DOC series on any free source tested; PIHPS has no DOC; company presentations (JPFA, 2024-26 only) are the only candidate."),
    ("Domestic corn price", "Bapanas (Jagung Pipilan Kering, producer)", "NOT VERIFIED",
     "Same API-key barrier; PIHPS does not cover corn. Indonesia restricts feed-corn imports, so world maize is a weak proxy (untested)."),
    ("World maize, soybean meal", "World Bank CMO (local file)", "AVAILABLE", "Monthly 1960-01 to 2026-10, USD/t."),
    ("USD/IDR", "Yahoo / macro_monthly.csv", "AVAILABLE", "Monthly average since 2014 in repository."),
    ("Chicken meat / egg prices", "PIHPS Bank Indonesia (retail, wholesale, producer)", "AVAILABLE",
     "Scripted with session cookie; national monthly from 2017-03 (retail), 2017-06 (wholesale), 2018-03 (producer). Producer 'daging ayam' is carcass-level, NOT livebird."),
    ("Poultry production volume", "BPS WebAPI", "PARTIAL", "Annual provincial statistics only; API requires a registered key (not created)."),
    ("Supply-control policy (DOC/HE culling)", "Kementan circulars", "PARTIAL", "Unstructured documents; would require manual event coding."),
    ("Quarterly segment financials", "CPIN website (cp.co.id)", "AVAILABLE (HEAD-checked)",
     "Interim FS PDFs at predictable URLs, HTTP 200 for Sep-2018..Sep-2026 tested; segment note content not yet verified (no download)."),
    ("Quarterly segment financials", "JPFA website / IDX", "PARTIAL",
     "JPFA site lists 2025-26 only; IDX API behind Cloudflare challenge (not bypassed) -> manual download needed for history."),
    ("Filing timestamps (PIT)", "jejaksaham.id mirror", "AVAILABLE", "Listings for CPIN/JPFA/MAIN reachable (first page 2024-26; older pages to test)."),
    ("Historical analyst expectations", "Yahoo/S&P", "NOT AVAILABLE", "Current snapshot only (no history); forward logging possible from 2026-11-25."),
    ("Alternative: monthly bank-only statements", "OJK CFS / bank websites", "PARTIAL",
     "OJK publishes with a 3-month lag (POJK 37/2019) and omits quarter-end months; banks publish their own monthly reports ~1 month after; per-bank collection required."),
]


def main() -> int:
    px = fetch_pihps()
    feed = cmo_feed()
    m = px.join(feed, how="left")
    m["chicken_producer_to_feed"] = m.chicken_producer / m.feed_proxy_idr_kg
    m.index.name = "month"
    m.to_csv(REF / "poultry_prices_monthly.csv", float_format="%.2f")
    eq = equities()
    cov = pd.DataFrame({"first": px.apply(lambda s: s.first_valid_index()), "last": px.apply(lambda s: s.last_valid_index()),
                        "n_months": px.notna().sum()})
    # first look only (not a predictive test): co-movement of producer chicken price with the feed proxy
    q = m[["chicken_producer", "feed_proxy_idr_kg"]].dropna()
    q.index = q.index.to_timestamp()
    qq = q.resample("QE").mean().pct_change().dropna()
    corr = qq.corr().iloc[0, 1]
    probes = pd.DataFrame(PROBES, columns=["dataset", "source_tested", "verdict", "evidence"])
    probes.to_csv(REF / "research" / "poultry_feasibility.csv", index=False)
    pd.concat([cov.astype(str), eq.astype(str)], axis=0).to_csv(REF / "research" / "poultry_coverage.csv")
    print(cov.to_string()); print(eq.to_string())
    print(f"quarterly co-movement chicken_producer vs feed proxy (pct chg): r = {corr:.2f}, n = {len(qq)}")
    print(probes[["dataset", "verdict"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
