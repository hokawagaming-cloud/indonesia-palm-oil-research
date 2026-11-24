# Decision Log

Record material decisions on scope, methodology, data and process. Add newest entries at the top. Do not delete entries; mark superseded ones instead.

| ID | Date | Decision | Rationale | Alternatives considered | Status |
|---|---|---|---|---|---|
| D-006 | 2026-11-24 | Use Yahoo (S-020) TAPG statements only as an interim, secondary, non-PIT source. Do not start TAPG operational modelling until the official annual reports are obtained. Do not create accounts on data sites (financialfilings, IPOSS) without the user's explicit approval. | Primary filings are blocked from this environment. Estimating operational metrics would mean fabricating data. | Proxy operational metrics from financials (rejected); sign up for APIs automatically (rejected). | Active |
| D-005 | 2026-11-24 | Deprecate S-001 (saham MCP prices). Use S-002 Yahoo daily data for liquidity and prices, pending a cross-check against IDX. | S-001 prices disagree materially with S-002 (e.g. AALI 5,900 vs 9,500 latest close), and S-001 is sampled only about weekly. | Keep S-001; reconcile the two sources. | Active |
| D-004 | 2026-11-24 | PROPOSED, not yet decided: re-tier on verified liquidity. BWPT and SIMP → core; GZCO → extended; ANJT, PSGO and CSRA → watch. | S-002 daily data shows tiers that differ from the D-002 screen (see the Phase I audit). Tiers are kept unchanged until the user decides. | Keep D-002 tiers (the current state). | Pending user decision |
| D-003 | 2026-11-24 | Adopt the methodology in `context/METHODOLOGY.md`: long-only, catalyst-driven quantamental; 3–12 month horizon; benchmarks IHSG and equal-weight core PIT universe; daily data, weekly screen, monthly rebalance; fundamentals on disclosure; backtest from 2016 subject to data; monthly PIT universe to avoid survivorship bias. | User mandate. PIT controls prevent look-ahead and survivorship bias. | — | Active |
| D-002 | 2026-11-24 | Universe = 9 core names (DSNG, SSMS, TAPG, STAA, LSIP, MGRO, NSSS, GZCO, AALI) for quant and fundamental work, plus 6 extended names (ANJT, TBLA, SIMP, BWPT, CSRA, PSGO) for fundamental work only. | The liquidity tiers keep the backtests realistic while still covering smaller names the market may overlook. See `research/industry/2026-11-24_universe_screen.md`. | Core only; the original 10-name list; all 22 names with no liquidity filter. | Active (pending free float / palm-revenue checks) |
| D-001 | 2026-11-24 | Use this repository as the single shared workspace for Claude Chat and Claude Code, with `context/` as the source of truth for project state. | Keeps research continuous across tools and sessions. | Separate notes per tool. | Active |

## Template

```
| D-XXX | YYYY-MM-DD | <decision> | <why> | <what else was considered> | Active / Superseded by D-YYY |
```
