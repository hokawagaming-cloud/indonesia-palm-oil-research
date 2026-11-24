# Project Status

_Last updated: 2026-11-24_

## Current phase

**Phase I — Data Availability Audit** (first pass complete). No investment analysis or rankings have been produced.

## Done

- [x] Repository created and initialised as a shared Claude Chat / Claude Code workspace (2026-11-24).
- [x] Folder structure, `CLAUDE.md`, context documents, source register and `.gitignore` created.
- [x] Stock universe confirmed: 9 core + 6 extended (D-002, 2026-11-24).
- [x] Methodology finalised: `context/METHODOLOGY.md` (D-003).
- [x] Daily OHLCV downloaded for 25 palm tickers plus IHSG, USD/IDR and Brent (`quant/fetch_ohlcv.py`, S-002).
- [x] Listing dates and current liquidity checked for all 15 coverage names.
- [x] First point-in-time universe built (`quant/build_universe.py` → `data/reference/pit_universe_monthly.csv`).
- [x] Source register filled with 19 tested sources and their verification status.
- [x] Audit write-up: `research/2026-11-24_phase1_data_availability_audit.md`.

## In progress

- Phase I gaps (see Blockers and Next).

## Next

- [ ] **Decide on re-tiering** (proposed D-004): BWPT and SIMP meet the core liquidity threshold; GZCO is now in the extended band; ANJT, PSGO and CSRA are below the extended threshold.
- [ ] Obtain IDX filings manually: quarterly financials, annual reports (production, age profile, segments) and the monthly shareholder registry (free float) for the 15 coverage names.
- [ ] Find a daily CPO price: test KPBN tender history, or authorise a vendor connector.
- [ ] Cross-check Yahoo (S-002) prices against IDX closes for a sample.
- [ ] Get price history for delisted or suspended GOLL and MAGP.
- [ ] Compile dated tables for the levy and duty schedule (PMK and Kepmendag) and the biodiesel allocations (Kepmen ESDM).
- [ ] Download CHIRPS rainfall and aggregate it to plantation provinces.
- [ ] Install `requirements.txt` in a virtual environment (xlrd is not yet installed).

## Blockers

- **IDX website blocks scripted access** (HTTP 403), and browser automation was not permitted in this session. Free float, palm-revenue exposure, financials and age profiles are therefore **unverified**.
- **No verified free daily CPO series**; only the monthly World Bank series is verified.
- Vendor connectors (LSEG, FactSet, S&P Global, Morningstar and others) are installed but not authorised. They need `/mcp` authorisation if we use them.
