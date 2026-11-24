# CLAUDE.md — Indonesian Palm Oil Quantamental Research

This file is the operating manual for any Claude instance (Claude Chat or Claude Code) working in this repository. Read it first, then read the files in `context/` before doing any work.

## Objective

Identify underappreciated investment opportunities in Indonesian palm oil equities **before fundamental catalysts are fully priced in**, by combining fundamental research (macro, industry, company) with quantitative research (signals, factor models, backtests).

## Session start checklist

1. Read `context/RESEARCH_CONTEXT.md` — scope, universe, research questions.
2. Read `context/METHODOLOGY.md` — mandate, PIT rules, pipeline.
3. Read `context/PROJECT_STATUS.md` — what is done, in progress, and next.
4. Skim `context/DECISION_LOG.md` and `context/ASSUMPTIONS.md` — do not silently re-litigate recorded decisions or change assumptions.
5. Check `data/SOURCE_REGISTER.csv` before adding or using any dataset.

## Session end checklist

1. Update `context/PROJECT_STATUS.md` (done / in progress / next / blockers).
2. Log any material methodological or scope decision in `context/DECISION_LOG.md`.
3. Record any new or changed assumption in `context/ASSUMPTIONS.md` with its source and date.
4. Register every new data source in `data/SOURCE_REGISTER.csv`.

## Repository layout

| Path | Purpose |
|---|---|
| `context/` | Shared memory between Claude Chat and Claude Code: context, status, decisions, assumptions |
| `research/macro/` | Macro drivers: CPO prices, FX (IDR/USD), biodiesel mandates (B35/B40/B50), export levies, weather (El Niño/La Niña), demand from India/China/EU |
| `research/industry/` | Industry structure: supply, yields, tree age profiles, costs, regulation (EUDR, ISPO), peer landscape |
| `research/company/` | One subfolder per ticker (e.g. `research/company/AALI/`) with notes, thesis, catalysts |
| `data/raw/` | Untouched source data. Never edit in place. Large or licensed files are git-ignored |
| `data/processed/` | Cleaned, analysis-ready data produced by scripts |
| `data/reference/` | Small tracked reference tables: listings and PIT universe membership (no raw prices) |
| `data/SOURCE_REGISTER.csv` | Register of every data source (origin, licence, frequency, last pulled) |
| `quant/` | Signal construction, factor models, feature engineering |
| `valuation/` | DCF, SOTP, comps, NAV-per-hectare models |
| `backtests/` | Backtest code, configurations and result summaries |
| `outputs/` | Finished deliverables: reports, charts, memos |
| `tests/` | Tests for data pipelines and quant code |

## Working rules

- **Sources and traceability.** Every number in a deliverable must trace back to a source in `data/SOURCE_REGISTER.csv` or a documented assumption in `context/ASSUMPTIONS.md`. Cite filings, data vendors and dates.
- **Raw data is immutable.** Transform `data/raw/` into `data/processed/` with code, never by hand.
- **No look-ahead bias.** Quant signals and backtests must use only information available at each point in time (point-in-time fundamentals, publication lags for reports and filings).
- **Reproducibility.** Analysis is code (Python preferred), with pinned dependencies once added. Notebooks are fine for exploration; logic that is reused moves into modules under `quant/` or `valuation/` with tests in `tests/`.
- **Separate fact from view.** Mark clearly what is reported data, what is estimate, and what is opinion or thesis.
- **Currency and units.** State currency (IDR / USD) and units (tonnes, ha, MT FFB) explicitly; record FX rates used.
- **Secrets.** Never commit API keys, credentials, or licensed vendor data. Use `.env` (git-ignored).
- **Not investment advice.** This is a research workspace; outputs are analysis, not personalised recommendations.

## Claude Chat vs Claude Code

- **Claude Chat** — discussion, reading, thesis drafting. Paste the relevant `context/` files at the start of a chat, and bring decisions back into `context/DECISION_LOG.md`.
- **Claude Code** — data pulls, code, models, backtests, file updates, commits.
- Both treat the `context/` folder as the single source of truth for project state.

## Conventions

- Tickers use IDX codes (e.g. `AALI`, `LSIP`, `SIMP`, `SSMS`, `TAPG`, `DSNG`, `SGRO`, `BWPT`). Confirm the final universe in `context/RESEARCH_CONTEXT.md`.
- File names: `YYYY-MM-DD_topic.md` for dated notes; `snake_case` for code.
- Commit messages: imperative mood, short subject, describe the *why*.
