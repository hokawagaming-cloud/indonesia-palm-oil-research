# Decision Log

Record material decisions on scope, methodology, data and process. Add newest entries at the top. Do not delete entries; mark superseded ones instead.

| ID | Date | Decision | Rationale | Alternatives considered | Status |
|---|---|---|---|---|---|
| D-002 | 2026-11-24 | Universe = 9 core names (DSNG, SSMS, TAPG, STAA, LSIP, MGRO, NSSS, GZCO, AALI) for quant and fundamental work, plus 6 extended names (ANJT, TBLA, SIMP, BWPT, CSRA, PSGO) for fundamental work only. | The liquidity tiers keep the backtests realistic while still covering smaller names the market may overlook. See `research/industry/2026-11-24_universe_screen.md`. | Core only; the original 10-name list; all 22 names with no liquidity filter. | Active (pending free float / palm-revenue checks) |
| D-001 | 2026-11-24 | Use this repository as the single shared workspace for Claude Chat and Claude Code, with `context/` as the source of truth for project state. | Keeps research continuous across tools and sessions. | Separate notes per tool. | Active |

## Template

```
| D-XXX | YYYY-MM-DD | <decision> | <why> | <what else was considered> | Active / Superseded by D-YYY |
```
