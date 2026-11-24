# Decision Log

Record material decisions on scope, methodology, data and process. Add newest entries at the top. Do not delete entries; mark superseded ones instead.

| ID | Date | Decision | Rationale | Alternatives considered | Status |
|---|---|---|---|---|---|
| D-006 | 2026-11-24 | No stock rankings, ratings or price targets in Phase 1. The Phase III ranking (SIMP, AALI, SSMS, LSIP, BWPT…) is kept as a dated historical record, not the current view. Quant rankings stay locked until the quality gates pass. | Mandate §19 (Phase 1: "Do not generate final stock rankings yet"); the quant brief rule against ranking unverified data. | Refresh the Phase III ranking now. | Active |
| D-005 | 2026-11-24 | Quant code lives in `quant/palmquant/` (Python package) with configs in `quant/config/`. Hand-collected, press-sourced seed tables go in `data/seed/` (committed). The DuckDB store `data/palmquant.duckdb` is git-ignored. Tests live in `tests/`, and the `quant/` path is set in `pyproject.toml`. | Keeps the existing repo layout (CLAUDE.md) and the session scaffold, without rebuilding it. Seeds are small, sourced and not licensed vendor data. | A separate `palmquant/` repo; a top-level `src/`. | Active |
| D-004 | 2026-11-24 | Point-in-time universe. Membership on each date follows listing / delisting, suspension, HSC status, 20-day ADV ≥ Rp1bn and business exposure. History is **not** truncated to today's names. STAA, CSRA and PSGO stay in history but are not investable while on the IDX HSC list (from 11 Nov 2026). JARR, SMAR and SGRO join the fundamental watchlist only (HSC / suspended). | Mandate §10 (a dynamic point-in-time universe, no survivorship bias). Resolves the D-002 implication logged in `RESEARCH_CONTEXT.md` §2.2. | Drop HSC names entirely; ignore HSC status. | Active (amends D-002) |
| D-003 | 2026-11-24 | Adopt the **Master Research Mandate** (24 Nov 2026) as the governing brief. Primary coverage: **TAPG, DSNG, LSIP**. Phase III finalists SIMP, SSMS and AALI move to the comparison watchlist (not dropped). Priority questions Q-A / Q-B / Q-C. NO TRADE is a valid outcome. | The user's mandate. The Phase III work stays recorded and can be revived if evidence supports it. Note that Phase III ranked DSNG 6th and TAPG 8th; adopting them as primary coverage is a scope choice, not a re-rating. | Keep SIMP / SSMS / AALI as primary. | Active |
| D-002 | 2026-11-24 | Universe = 9 core names (DSNG, SSMS, TAPG, STAA, LSIP, MGRO, NSSS, GZCO, AALI) for quant and fundamental work, plus 6 extended names (ANJT, TBLA, SIMP, BWPT, CSRA, PSGO) for fundamental work only. | The liquidity tiers keep the backtests realistic while still covering smaller names the market may overlook. See `research/industry/2026-11-24_universe_screen.md`. | Core only; the original 10-name list; all 22 names with no liquidity filter. | Active (pending free float / palm-revenue checks) |
| D-001 | 2026-11-24 | Use this repository as the single shared workspace for Claude Chat and Claude Code, with `context/` as the source of truth for project state. | Keeps research continuous across tools and sessions. | Separate notes per tool. | Active |

## Template

```
| D-XXX | YYYY-MM-DD | <decision> | <why> | <what else was considered> | Active / Superseded by D-YYY |
```
