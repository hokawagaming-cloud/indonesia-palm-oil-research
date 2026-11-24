# TAPG — Official Document Extraction and Reconciliation

_Date: 2026-11-24 · Documents supplied manually by the user into `data/raw/company/TAPG/` (git-ignored) · No estimates; no investment rating_

## 1. Document inventory (S-021 annual reports, S-025 interim statements)

| Document | Pages | Period | Publication-date anchor | Anchor basis |
|---|---|---|---|---|
| AR 2021.pdf | 342 | FY2021 (+FY2020 comparative) | 2022-03-22 | Statements authorised for issue by the Directors (AR PDF created 2022-04-26) |
| AR_2022.pdf | 364 | FY2022 (+FY2021) | 2023-02-24 | Auditor's report date (AR PDF 2023-03-31) |
| AR_2023.pdf | 350 | FY2023 (+FY2022) | 2024-03-07 | Auditor's report date (AR PDF 2024-03-28) |
| AR_2024.pdf | 346 | FY2024 (+FY2023) | 2025-02-26 | Auditor's report date (AR PDF 2025-04-09) |
| TAPG_-_AR_2025.pdf | 360 | FY2025 (+FY2024) | 2026-03-16 | Auditor's report date (AR PDF 2026-04-21) |
| FinancialStatement-2026-I-TAPG.pdf | 119 | Q1 2026 (+Q1 2025) | 2026-04-27 | Board of Directors' statement date, IDX XBRL filing |
| FinancialStatement-2026-II-TAPG.pdf | 119 | H1 2026 (+H1 2025) | 2026-07-29 | as above |
| FinancialStatement-2026-III-TAPG.pdf | 119 | 9M 2026 (+9M 2025) | 2026-10-28 | as above |

**Point-in-time rule:** audited figures are usable from the auditor's report date. Operational tables that appear only in the annual report are usable from the AR PDF creation date, which is later. Exact IDX upload timestamps are not in the documents (see gaps). The Sustainability Report 2025 was **not** among the supplied files.

Text is extracted per page by `quant/pdf_to_text.py`. **Every data point cites the PDF page index**, which is the page number shown in a PDF viewer. The operational dataset also records the printed folio.

## 2. Datasets produced

| Dataset | File (tracked) | Points | Coverage | Frequency | Source class | Validation |
|---|---|---|---|---|---|---|
| Financial statements, audited | `data/reference/TAPG_statements_extracted.csv` | 372 (incl. interim) | FY2020–FY2025, 26 line items (IS, BS, CF) | Annual | Primary | Rev + COGS = GP, PBT build-up and PBT + tax = profit: **30/30 PASS**. 100 cross-document overlaps match. 2 restatements (below). **36/36 overlapping values match Yahoo exactly** (`TAPG_yahoo_vs_official.csv`). |
| Financial statements, interim | same file | — | Q1, H1, 9M for 2025 and 2026 | Quarterly (cumulative) | Primary (unaudited) | Same identities pass. JV and associate shares are reported separately. |
| Discrete quarters | `data/reference/TAPG_quarterly_derived.csv` | — | 2025Q1–2026Q3 (Q4 2025 = FY − 9M) | Quarterly | Derived by subtraction from primary | Q3 2025, which Yahoo lacked, is now filled: revenue IDR 2,699.4bn |
| Highlight tables (financial and operational) | `data/reference/TAPG_extracted_highlights.csv` and `_reconciliation.csv` | — | FY2019–FY2025 | Annual | Primary (AR summary) | Nucleus + plasma = total area and FFB; CPO ÷ processed FFB = OER (±0.15pp): all PASS |
| Operational detail, cost, JV | `data/reference/TAPG_operational_extracted.csv` | 208 | Age profile FY2021–25; mature/immature by region FY2021–25; processed FFB by source FY2022–25; ASP FY2020–25; sales volume FY2020–25; segment revenue FY2024–25; COGS breakdown FY2022–25; USTP JV FY2021–25 | Annual | Primary | **All 41 checks PASS** (`TAPG_operational_checks.csv`): age bands sum to totals; regions sum to totals; immature = 0–3 yr band; mature + immature = nucleus total; volume × ASP = segment revenue within 0.01% (CPO, PK, PKO, FY24–25); COGS components = production cost |

### Key extracted series (IDR bn unless stated)

| | FY2020 | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|---|---|
| Revenue | 5,265.8 | 6,278.1 | 9,345.6 | 8,325.9 | 9,671.5 | 11,402.2 |
| Gross profit | 1,392.8 | 1,615.8 | 3,715.9 | 2,217.3 | 3,722.8 | 4,497.6 |
| Share of profit, JVs and associates | 405.1 | 348.7 | 968.4 | 643.3 | 893.8 | 1,066.9 |
| — of which USTP (50% JV) | — | 344.8 | 958.6 | 637.1 | 886.7 | 1,059.7 |
| Profit before tax | 1,070.9 | 1,421.3 | 3,689.3 | 1,941.1 | 3,926.9 | 4,661.3 |
| Profit to owners | 911.1 | 1,159.0 | 2,981.1 | 1,608.2 | 3,120.3 | 3,702.3 |
| Capex, acquisition of fixed assets (cash) | 427.2 | 455.2 | 738.2 | 802.4 | 587.6 | 622.7 |
| JV dividends received (cash) | 50.0 | 150.0 | 150.0 | 300.0 | 1,170.0 | 958.8 |
| CPO ASP (IDR/kg) | 8,298 | 9,274 | 12,211 | 11,115 | 13,156 | 14,220 |
| CPO sales volume (kt, consolidated) | 567 | 578 | 666 | 677.0 | 636.0 | 658.9 |
| CPO production (kt, incl. associates) | — | — | — | 978 | 916 | 953 |
| Nucleus mature area (ha, year-end) | — | 129,943 | 130,300 | 129,221 | 128,178 | 125,201 |
| Nucleus trees > 20 years (ha) | — | 8,551 | 8,200 | 7,155 | 6,796 | 4,544 |

USTP accounts for 98.9–99.3% of the JV and associate profit line every year, and the line equals about 23% of FY2025 pre-tax profit. JV earnings are therefore a first-order driver that needs its own model input.

## 3. Reconciliation findings

1. **FY2022 total equity:** the AR2023 and AR2024 highlight tables print 10,412,277. The audited balance sheets (AR2022 p234, AR2023 comparative p228) print **10,412,744**. The highlight figure fails A = L + E by 467. **The audited value is used**; the highlight figure is a typo in the summary table.
2. **FY2022 finance income and costs were reclassified:** AR2022 shows +69,469 / −380,151; the AR2023 comparative shows +36,912 / −347,594. Both moved by 32,557, a netting reclassification with no PBT effect. **The latest presentation (AR2023) is used**, with the original kept in the extraction file.
3. **Scope mismatch:** production, area, yield and OER are reported "including associate companies" (the company's term, which covers USTP). Sales volumes, ASP and the financial statements are consolidated. For example, FY2025 CPO production of 953 kt compares with consolidated CPO sales of 658.9 kt. **Ratios across the two scopes are invalid unless adjusted.**
4. **AR2024 sales table unit label:** the header says "thousand tons", but the values are tonnes (636,021). Treated as tonnes. Volume × ASP reconciles to segment revenue only on that basis.
5. **AR2022 rounding:** the age profile and region tables are printed rounded to 100 ha.
6. **JV dividends declared vs received:** in FY2021–FY2024 the declared and received amounts differ by IDR 2–8bn. In FY2025, IDR 1,359.9bn was declared but IDR 958.8bn received, leaving about IDR 401bn outstanding at year-end; IDR 900bn was received in 9M2026.
7. **PK sales FY2022:** AR2022 prints 141 kt and AR2023 prints 142 kt (rounding).

## 4. Remaining gaps before earnings nowcasting and modelling

| # | Gap | Impact | Possible source |
|---|---|---|---|
| G1 | **Quarterly or monthly operational data** (FFB, CPO production, sales volume, ASP) for 2025–2026. The interim filings contain financials only. | High: nowcasting needs within-year volume and price drivers | Company quarterly presentations / public expose materials; IDX monthly production disclosures if any |
| G2 | **Unit cash cost per tonne:** not disclosed. "Materials and processing" (IDR 4,439bn in FY2025) bundles purchased third-party FFB with fertiliser and chemicals. | High for margin modelling | Analyst presentations; AR notes on FFB purchases (not found yet) |
| G3 | **USTP standalone operations** (hectares, production, costs) and its summarised financials. Only the equity-method share, dividends and carrying value were extracted. | High: USTP is ~23% of PBT | JV summarised-financials note in each AR (not yet extracted) |
| G4 | Capex split (bearer plants and replanting vs mills and other) | Medium | Fixed-asset roll-forward note (note 12), not yet extracted |
| G5 | FFB production and yield by region; age profile before FY2021 | Medium | AR region tables (visible, not yet transcribed); IPO prospectus (2021) for earlier years |
| G6 | COGS breakdown FY2020–FY2021 (not found under the same label in AR2021/AR2022) | Low–medium | Re-check AR2021/AR2022 note wording |
| G7 | Exact IDX publication timestamps for each filing and for earnings announcements | Medium for PIT tests | IDX announcement archive (blocked to scripts, S-013) |
| G8 | Sustainability Report 2025 (water, fertiliser, emissions, estate-level data) | Low–medium | User download |
| G9 | Estate coordinates for estate-weighted rainfall (CHIRPS currently uses province boxes, A-009) | Medium | AR / SR maps |
| G10 | Long domestic CPO price history (KPBN) | High for nowcasting the ASP | Vendor or IPOSS access (unchanged) |

Gaps G3–G6 can be closed from the supplied documents with further extraction. G1, G2 and G10 need new sources.
