# Project Status

_Last updated: 2026-11-24_

## Current phase

**Phase 1 — Data verification** (Master Research Mandate, 24 Nov 2026). Phase 0 (consolidation) is complete. No rankings or ratings are produced in this phase (D-006).

Priority questions:
- **Q-A:** TAPG premium.
- **Q-B:** DSNG discount.
- **Q-C:** LSIP cash.

## Done

- [x] Repository and context files set up (2026-11-24).
- [x] Universe confirmed: 9 core + 6 extended (D-002).
- [x] Phase I TAPG stress-test, Phase II TAPG vs LSIP, Phase III sector alpha discovery (Claude Docs; consolidated in `RESEARCH_CONTEXT.md`).
- [x] Consolidated research context (`RESEARCH_CONTEXT.md`, 2026-11-24).
- [x] Phase 0–1 reconciliation and verification audit: `research/2026-11-24_phase1_verification_audit.md`.
- [x] Research backlog (`RESEARCH_BACKLOG.md`) and Claude Code task spec (`CLAUDE_CODE_TASKS.md`).
- [x] Quant scaffold committed: `quant/config/`, `quant/palmquant/` (point-in-time DuckDB store), `data/seed/`, `tests/test_store.py` (8 passing), `requirements.txt`.

## In progress

- Phase 1 verification of company figures. See backlog P1 items B-01 to B-09.

## Next

- [ ] B-01 DSNG 9M26 FS (resolves C-11, C-12).
- [ ] B-02 / B-03 LSIP 9M26 FS and buyback execution.
- [ ] B-04 / B-05 TAPG quarterly operations and JV accounts.
- [ ] B-07 Estate location database.
- [ ] Claude Code T-01 (seed loader and audit) and T-09 / T-10 / T-15 (need no networked data).
- [ ] Claude Code T-02 price ingestion on a networked machine.

## Blockers

- **No bulk data access from the cloud workspace.** IDX, KSEI, Yahoo, FRED, NASA POWER, CHIRPS, BMKG, MPOB and GAPKI are unreachable from the shell. Ingestion needs a networked machine or vendor data (backlog decision point 1).
- **No consensus or revision data.** Expectations use labelled proxies until a vendor is available.
- **DSNG reference figures in the mandate are internally inconsistent** (C-11 to C-13) until the 9M26 FS are read.
