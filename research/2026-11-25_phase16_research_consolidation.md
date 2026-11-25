# Phase XVI — Research Consolidation

_Date: 2026-11-25._

_Companion to `research/company/ITMG/2026-11-25_ITMG_equity_research.md`. Decision: D-046._

**Accepted and preserved:**
- R1 NO-GO (D-045). The signal is not reversed and not optimised.
- All results are preserved.

**Paused:** cross-sector exploration. DR-R2 and DR-R3 remain registered and untested.

## 1. R1: CAGR difference vs annualised excess return

| Measure | Value | Definition | Role |
|---|---|---|---|
| **Annualised excess return (arithmetic)** | **−5.0% per year** | 12 × mean of monthly (strategy net − benchmark net) | **The registered decision statistic** (`DR_R1_implementation.json`) and the quantity tested with HAC and bootstrap |
| CAGR difference (geometric) | −3.7pp | CAGR(strategy) − CAGR(benchmark) = −1.4% − 2.3% | Descriptive only |

**Why they differ — volatility drag:**
- Geometric growth ≈ arithmetic mean − σ²/2.
- The benchmark is more volatile (27.5% vs 21.6% a year), so its drag (≈ 3.8% a year) exceeds the strategy's (≈ 2.3%). That narrows the geometric gap by about 1.4pp.
- **Both measures are negative, and every registered criterion fails under either measure.**
- The Phase XV memo's headline (−5.0%) is the registered statistic; "CAGR difference −3.7pp" appears alongside it as a descriptive figure. No change to the decision.

## 2. Programme-wide hypothesis register

`data/reference/research/hypothesis_register.csv` has 16 entries:

| Status | Experiments |
|---|---|
| **GO (historical; prospective pending)** | ITMG-C1 |
| **CONDITIONAL GO** | ITMG-I1 |
| **Frozen prospective** | CPIN-H2, MVP-B2 |
| **NO-GO** (preserved) | CPIN-H1, B1-BBCA, B1-BBRI, C1 alternatives (M1/M4), ITMG-C2, ITMG-C3, DR-R1 |
| **Designed / untested** | ITMG-ES1, DR-R2, DR-R3 |
| **Decisions** | Palm oil NO TRADE; ITMG HOLD/WATCH (equity research, not a statistical test) |

Programme-wide multiplicity covers 17 tests (`programme_multiplicity_v3.csv`); only C1 survives (Holm p 0.013).

## 3. Scheduled prospective forecasts (unchanged)

| Task | When | Status |
|---|---|---|
| `itmg-prospective-forecast-2026q4` | 10 Jan 2027, 10:00 WIB | Scheduled; verified by a scheduled dry run (Phase XIV) |
| `itmg-prospective-evaluation-2026q4` | 8 Mar 2027, 10:00 WIB | Scheduled |
| MVP-B2 origins | Dec 2026 | Pending |
| CPIN H2 | — | Awaiting resolutions |

The Phase XVI equity research used a **provisional** C1 run (25 Nov, October data only) for the report only. It did **not** write to the forecast journal and does not replace the frozen 10 Jan run.

## 4. Outstanding data-quality and point-in-time limitations

| Area | Limitation | Affects |
|---|---|---|
| World Bank CMO | D+10 availability proven for one quarter only (June 2026). Pre-2026 vintages not archived. 2026 revisions up to USD 58/t (palm oil). | C1 (fallback model), DR-R1 |
| ITMG decks | "First-reported" values taken from today's copies of historical decks | C1, C2, I1 targets |
| ITMG FS parsing | Text-anchor parser. Identities pass for all 10 periods; per-line spot checks only for FY2025 and 9M26. | ITMG model history |
| Consensus | Forward snapshots only (from 2026-11-24). Vendor share basis undisclosed. | ITMG expectations gap, ES1 |
| Prices | Yahoo Adj Close is gross of the 10% dividend tax. Zero-volume days are holiday rows. No IHSG total return. | DR-R1, relative valuation |
| Survivorship | Delisted palm names (GOLL, MAGP) lack prices; unknown pre-2015 delistings | DR-R1, any cross-section |
| Regulation | IUPK royalty (PP 15/2022), PP 19/2025 IUP royalty and the export levy are knowledge-only or unverified | ITMG valuation scenarios |
| Licences | Extensions assumed for TCM, BEK, NPR, GPK, TIS; IMM flexed | ITMG DCF |
| Peer multiples | Yahoo mixes IDR prices with USD fundamentals for USD reporters (corrected by USD/IDR); trailing periods differ | Relative valuation |
| Workbook | No Excel/LibreOffice recalculation in the build environment; verified by an independent evaluator (1,717 formulas, 0 errors) | ITMG workbook |
| Palm, CPIN, banking | Earlier registers (S-033 vintages, CPIN segment layouts, bank PIT timing) unchanged | Earlier phases |
