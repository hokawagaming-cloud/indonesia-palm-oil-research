# Phase I — Data Availability Audit

_Date: 2026-11-24 · Status: first pass complete; gaps listed below · Source IDs refer to `data/SOURCE_REGISTER.csv`_

"Verified" means the data was downloaded and parsed on 2026-11-24. "Reachable" means the source responded, but its data has not been downloaded or parsed yet. Nothing has been filled in or estimated.

## 1. Coverage by data need

| Data need | Best verified source | Status | Frequency | History | Gap / action |
|---|---|---|---|---|---|
| Stock OHLCV | S-002 Yahoo Finance | **Verified** | Daily | 2015 onward (or from IPO) for 25 tickers | Unofficial; cross-check against IDX. No data for delisted GOLL and MAGP. |
| IHSG benchmark | S-002 (`^JKSE`) | **Verified** | Daily | 2015 onward | Official IDX index history would be preferable. |
| CPO price | S-003 World Bank | **Verified (monthly)** | Monthly | 1960M01–2026M10 | **No verified free daily CPO series.** S-009 KPBN (daily domestic tender) is reachable but untested; S-018 Bursa FCPO needs a vendor. |
| USD/IDR | S-002 (`IDR=X`) | **Verified** | Daily | 2015 onward | Official BI JISDOR (S-008) reachable; export untested. |
| Brent | S-002 (`BZ=F` futures) | **Verified** | Daily | 2015 onward | EIA spot (S-005) downloaded but not parsed. |
| Rainfall | S-007 CHIRPS v3.0 | Reachable | Daily / monthly | 1981 onward | Download and aggregate to plantation regions. BMKG (S-019) needs registration. |
| ENSO | S-006 NOAA ONI | **Verified** | Monthly | 1950–ASO 2026 | — |
| Industry production | S-004 USDA PSD | **Verified (annual)** | Annual | 1960–2026 | Not point-in-time (revisions overwrite). Monthly GAPKI (S-016) archive location to confirm; BPS (S-015) reachable. |
| Company production volumes | S-013 IDX annual and quarterly reports | **Blocked** | Quarterly / annual | — | IDX returns 403 to scripted access; needs manual download. |
| Plantation age profiles | S-013 annual reports | **Blocked** | Annual | — | Same as above. |
| Biodiesel allocations | S-012 ESDM JDIH | Reachable | On change | — | Compile the decree history into a dated table. |
| Export levy and duty | S-010 (press-verified for Nov 2026), S-011 Kemenkeu JDIH | Partially verified | Monthly / on change | — | Compile the full PMK and Kepmendag history with effective dates. |
| Quarterly financial statements | S-013 IDX | **Blocked** | Quarterly | — | Manual download, or a vendor (e.g. LSEG, FactSet, S&P; their connectors are installed but not authorised). |
| Free float | S-013 IDX monthly registry | **Blocked** | Monthly | — | Press coverage confirms IDX publishes it; the per-ticker figures were not obtainable. |

## 2. Universe verification (from S-002 daily data)

| Check | Result |
|---|---|
| Listing dates | Listed before 2015: AALI, LSIP, SIMP, SSMS, DSNG, GZCO, ANJT, TBLA, BWPT. First trade after 2015: PSGO 2019-11-25, CSRA 2020-01-09, MGRO 2018-07-12, TAPG 2021-04-12, STAA 2022-03-10, NSSS 2023-03-10. These are Yahoo first-bar dates; confirm against IDX listing dates. |
| Liquidity (median 63-day traded value, as of 2026-11-24) | TAPG 21.5bn, AALI 20.6, LSIP 13.6, SSMS 9.7, **BWPT 6.9**, **SIMP 5.1**, DSNG 5.1, STAA 4.1, MGRO 2.6, NSSS 2.5, **GZCO 1.1**, TBLA 0.7, **CSRA 0.23**, **ANJT 0.06**, **PSGO 0.03** (IDR bn) |
| Mismatch with D-002 tiers | BWPT and SIMP (extended) meet the core threshold. GZCO (core) falls to the extended band. ANJT, PSGO and CSRA (extended) are below the extended threshold. Tiers are unchanged pending a decision. |
| Free float | **Not verified** (S-013 blocked) |
| Palm oil revenue exposure | **Not verified** (S-013 blocked) |
| Survivorship | GOLL (delisted 2026-11-10 per S-014) and MAGP (suspended since 2022-07-18) have no Yahoo data. The PIT history is incomplete for those names until IDX data is obtained. |

**S-001 deprecated.** The saham MCP prices behind the D-002 screen disagree materially with S-002 (e.g. AALI 5,900 vs 9,500 latest close). The D-002 liquidity figures should be treated as superseded by the S-002 figures above.

## 3. PIT universe — first build

`quant/build_universe.py` → `data/reference/pit_universe_monthly.csv`. Average number of names per month in the core liquidity band: 6.3 (2016), 6.1 (2019), 10.1 (2022), 11.9 (2026). The equal-weight core benchmark therefore holds only about 6 names in 2016–2020, which limits how much the early-period backtest can show.

## 4. Priority actions for Phase II

1. **Manual IDX downloads (user):** quarterly financials, annual reports, and the latest monthly shareholder registry for the 15 coverage names, plus listing and delisting announcements for GOLL and MAGP.
2. **Daily CPO:** test KPBN tender history depth, or authorise a vendor (LSEG, FactSet, S&P connectors are installed but need `/mcp` authorisation).
3. Cross-check S-002 against IDX closes for a sample of dates and tickers.
4. Compile the levy, duty and biodiesel regulation history into dated tables.
5. Download and aggregate CHIRPS rainfall to the main plantation provinces.
6. Decide whether to re-tier BWPT, SIMP, GZCO, ANJT, PSGO and CSRA (proposed D-004).

## 5. Update — TAPG official documents (2026-11-24)

The user supplied TAPG AR2021–AR2025 and the 2026 interim statements. Company financials, the age profile, area, processed FFB, ASP, sales volumes, COGS breakdown and JV contribution are now **verified from primary sources**, with page citations (S-021, S-025). Details and remaining gaps: `research/company/TAPG/2026-11-24_official_document_extraction.md`. The other 14 coverage names still need the same treatment, and free float is still unverified.
