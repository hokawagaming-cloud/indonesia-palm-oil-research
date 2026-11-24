# CPO Export Levy and Duty Reconstruction (2015 – Nov 2026)

_Files: `data/reference/levy_regimes.csv` (209 band rows, 25 regimes), `duty_regimes.csv` (152 band rows, 11 regimes), `cpo_reference_prices.csv` (116 HRef periods), `cpo_levy_duty_monthly.csv`; code `quant/levy_duty.py`; tests `tests/test_levy_duty.py` (7 tests)._

## Sources

- **Regimes:** primary PMK texts from peraturan.bpk.go.id and jdih.kemenkeu.go.id (S-034). 8 levy and 5 duty regimes were read from image annexes by OCR (`source_class = primary (OCR)`).
- **Reference prices (HRef):** primary Kemendag decree PDFs (S-035), parsed automatically. **Coverage: 99 of 143 months (69%), from Oct 2017.**
  - Missing: all of 2015 to Sep 2017, plus 2017-11, 2018-02, 2018-08, 2019-03, 2019-05, 2020-08, 2023-01, 2023-05, 2024-10, 2025-09, 2025-10.
  - Missing months are left empty, never interpolated. Levy and duty are computed only where HRef exists or the regime is flat.
- **Products:** duty covers CPO only. Levy covers CPO, crude palm olein, RBD palm olein, and packaged RBD olein ≤ 25 kg. PK/PKO tables are not reconstructed.

## Formula

- **Duty** (USD/t) = the band amount for the HRef in force, from PMK annex bands. A band applies when lower < HRef ≤ upper.
- **Levy:** fixed USD/t or bands up to Sep 2024. From PMK 62/2024 it is a % of HRef (7.5% → 10% → 12.5% from 1 Mar 2026 under PMK 9/2026).
- **Monthly evaluation:** on the 15th. 2022–2023 semi-monthly HRef periods take the period covering the 15th.
- **Special episodes:** export ban 28 Apr–23 May 2022 (secondary, flagged, not modelled); levy suspension 15 Jul–31 Oct 2022 (PMK 115/2022, 130/2022); PMK 154/2022 zero levy below HRef 800 until end-2022.

## Validation

- Tests against values read from the PMK annexes: band edges, every levy episode.
- **Independent cross-checks against press reports (S-010), all PASS:** Nov 2026 duty 124 and levy 122.36; Oct duty 178 (HRef 1,042.15); Sep duty 148 and levy 125.94; Aug duty 148 (HRef 996.52); May duty 178; Mar HRef 938.87.

## Regimes

### Levy

| regime_id   | regulation                                     | effective_from   | effective_to   | basis   | source_class   |
|:------------|:-----------------------------------------------|:-----------------|:---------------|:--------|:---------------|
| L01         | PMK 114/PMK.05/2015                            | 2015-06-16       | 2015-07-15     | usd     | primary (OCR)  |
| L02         | PMK 133/PMK.05/2015                            | 2015-07-16       | 2016-02-22     | usd     | primary (OCR)  |
| L03         | PMK 30/PMK.05/2016 (amends 133/2015)           | 2016-02-23       | 2018-07-29     | usd     | primary (OCR)  |
| L04         | PMK 81/PMK.05/2018                             | 2018-07-30       | 2018-12-03     | usd     | primary        |
| L05         | PMK 152/PMK.05/2018 (amends 81/2018)           | 2018-12-04       | 2019-03-10     | usd     | primary (OCR)  |
| L06a        | PMK 23/PMK.05/2019 (amends 81/2018)            | 2019-03-11       | 2019-05-31     | usd     | primary (OCR)  |
| L06b        | PMK 23/PMK.05/2019                             | 2019-06-01       | 2019-09-30     | usd     | primary (OCR)  |
| L07a        | PMK 136/PMK.05/2019 (amends 81/2018)           | 2019-10-01       | 2019-12-31     | usd     | primary (OCR)  |
| L07b        | PMK 136/PMK.05/2019                            | 2020-01-01       | 2020-05-31     | usd     | primary (OCR)  |
| L08         | PMK 57/PMK.05/2020                             | 2020-06-01       | 2020-12-09     | usd     | primary        |
| L09         | PMK 191/PMK.05/2020 (amends 57/2020)           | 2020-12-10       | 2021-07-01     | usd     | primary        |
| L10         | PMK 76/PMK.05/2021 (amends 57/2020)            | 2021-07-02       | 2022-03-17     | usd     | primary        |
| L11         | PMK 23/PMK.05/2022 (amends 57/2020)            | 2022-03-18       | 2022-06-13     | usd     | primary        |
| L12a        | PMK 103/PMK.05/2022                            | 2022-06-14       | 2022-07-14     | usd     | primary        |
| L12b        | PMK 103/PMK.05/2022 (scheduled, never applied) | 2022-08-01       | 2022-08-01     | usd     | primary        |
| L13         | PMK 115/PMK.05/2022 (amends 103/2022)          | 2022-07-15       | 2022-08-31     | usd     | primary        |
| L13s        | PMK 115/PMK.05/2022 (scheduled, never applied) | 2022-09-01       | 2022-09-01     | usd     | primary        |
| L14         | PMK 130/PMK.05/2022 (amends 103/2022)          | 2022-09-01       | 2022-10-31     | usd     | primary        |
| L14s        | PMK 130/PMK.05/2022 (scheduled, never applied) | 2022-11-01       | 2022-11-01     | usd     | primary        |
| L15a        | PMK 154/PMK.05/2022 (amends 103/2022)          | 2022-11-01       | 2022-12-31     | usd     | primary        |
| L15b        | PMK 154/PMK.05/2022                            | 2023-01-01       | 2024-09-21     | usd     | primary        |
| L16         | PMK 62 Tahun 2024                              | 2024-09-22       | 2025-05-16     | pct     | primary        |
| L17         | PMK 30 Tahun 2025                              | 2025-05-17       | 2025-10-20     | pct     | primary        |
| L18         | PMK 69 Tahun 2025                              | 2025-10-21       | 2026-02-28     | pct     | primary        |
| L19         | PMK 9 Tahun 2026 (amends 69/2025)              | 2026-03-01       | nan            | pct     | primary        |

### Duty

| regime_id   | regulation                                                  | effective_from   | effective_to   | source_class   |
|:------------|:------------------------------------------------------------|:-----------------|:---------------|:---------------|
| D01         | PMK 136/PMK.010/2015 (4th amendment of PMK 75/PMK.011/2012) | 2015-07-16       | 2016-09-29     | primary (OCR)  |
| D02         | PMK 140/PMK.010/2016                                        | 2016-09-30       | 2017-02-09     | primary (OCR)  |
| D03         | PMK 13/PMK.010/2017                                         | 2017-02-10       | 2019-01-16     | primary        |
| D04         | PMK 164/PMK.010/2018 (amends 13/2017)                       | 2019-01-17       | 2020-10-22     | primary (OCR)  |
| D05         | PMK 166/PMK.010/2020 (amends 13/2017)                       | 2020-10-23       | 2022-01-11     | primary (OCR)  |
| D06         | PMK 1/PMK.010/2022 (amends 13/2017)                         | 2022-01-12       | 2022-03-31     | primary (OCR)  |
| D07         | PMK 39/PMK.010/2022                                         | 2022-04-01       | 2022-06-09     | primary        |
| D08         | PMK 98/PMK.010/2022 (amends 39/2022)                        | 2022-06-10       | 2022-08-08     | primary        |
| D09         | PMK 123/PMK.010/2022 (amends 39/2022)                       | 2022-08-09       | 2024-06-02     | primary        |
| D10         | PMK 38 Tahun 2024                                           | 2024-06-03       | 2025-10-20     | primary        |
| D11         | PMK 68 Tahun 2025 (amends 38/2024)                          | 2025-10-21       | nan            | primary        |

## Netback (audit finding E) — `quant/cpo_netback.py`

| Month | HRef | Levy | Duty | Charges | Netback (HRef − charges) |
|---|---|---|---|---|---|
| Oct 2026 | 1,042.15 | 130.27 | 178 | 308.27 | 733.88 |
| Nov 2026 | 978.90 | 122.36 | 124 | 246.36 | 732.54 |

- **On the regulatory basis, the audit claim is verified:** the Nov charge cut (−61.9 USD/t) offsets 98% of the HRef fall (−63.3), so the reference netback moves only −1.3 USD/t.
- **It does not follow that domestic prices held up.** HRef is set from the prior month's prices, while domestic tenders follow current world prices. KPBN tenders (S-023, secondary, few observations) averaged IDR 14,806/kg in Oct and 14,239/kg in Nov-to-date (−3.8%).
- For a given world price, the November schedule raises export parity by about USD 62/t (≈ IDR 1,100/kg) versus October. That is a cushion, not an increase.
- The Q4 base scenario uses −5.5% vs Q3 for ASP: KPBN Q4-to-date vs Q3, partial and secondary.