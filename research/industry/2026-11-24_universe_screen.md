# Universe Screen — Indonesian Palm Oil Equities

_Date: 2026-11-24 · Source: S-001 (local IDX price dataset, 1-year lookback, last updated 2026-11-07) · Status: liquidity screen done; free float and palm-revenue share still to verify_

## Method

1. Started from every IDX-listed ticker with palm oil plantation or palm-based processing exposure (22 names).
2. Approximate liquidity = average traded volume × midpoint of the 1-year price range, in IDR bn per trading day. This is **indicative only**: the dataset samples roughly weekly, so treat these figures as an order of magnitude.
3. Tiers:
   - **Core:** ≥ IDR 1.5bn per day and enough data history. Used for quant signals and backtests and for full fundamental coverage.
   - **Extended:** IDR 0.25–1.5bn per day. Fundamental coverage, flagged for liquidity, outside the main backtest.
   - **Excluded / watch:** < IDR 0.25bn per day, sparse data, or no data.

## Results

| Ticker | Company | Tier | Approx. value traded (IDR bn/day) | 1y return | Data points | Notes |
|---|---|---|---|---|---|---|
| DSNG | Dharma Satya Nusantara | Core | ~18 | -21% | 46 | |
| SSMS | Sawit Sumber Mas Sarana | Core | ~14 | +74% | 38 | Strong re-rating; check for corporate action |
| TAPG | Triputra Agro Persada | Core | ~9 | -8% | 48 | |
| STAA | Sumber Tani Agung Resources | Core | ~8 | +1% | 45 | |
| LSIP | PP London Sumatra Indonesia | Core | ~8 | -14% | 48 | |
| MGRO | Mahkota Group | Core | ~4 | -4% | 19 | Refinery-heavy; check palm-revenue split; sparse data |
| NSSS | Nusantara Sawit Sejahtera | Core | ~4 | +10% | 32 | |
| GZCO | Gozco Plantations | Core | ~4 | +1% | 47 | Low-priced stock; check free float |
| AALI | Astra Agro Lestari | Core | ~2 | -5% | 48 | Large cap; low share turnover |
| ANJT | Austindo Nusantara Jaya | Extended | ~1.0 | +11% | 36 | |
| TBLA | Tunas Baru Lampung | Extended | ~0.8 | -4% | 42 | Integrated, with a sugar segment |
| SIMP | Salim Ivomas Pratama | Extended | ~0.7 | -8% | 45 | Integrated (Indofood group) |
| BWPT | Eagle High Plantations | Extended | ~0.5 | -7% | 48 | Leveraged; low-priced stock |
| CSRA | Cisadane Sawit Raya | Extended | ~0.3 | -8% | 24 | |
| PSGO | Palma Serasih | Extended | ~0.3 | -10% | 34 | |
| JAWA | Jaya Agra Wattie | Excluded | ~0.3 | -10% | 33 | Mixed crops; distressed history |
| SGRO | Sampoerna Agro | Excluded | ~0.15 | +1% | 8 | Very thin trading |
| SMAR | SMART | Excluded | ~0.1 | -2% | 18 | Very low free float |
| TLDN | Teladan Prima Agro | Excluded | ~0.08 | -2% | 43 | |
| FAPA | FAP Agri | Excluded | ~0.05 | 0% | 5 | Very low free float |
| CBUT | Citra Borneo Utama | Excluded | ~0.01 | +31% | 5 | |
| UNSP, PGUN | Bakrie Sumatera, Pradiksi Gunatama | Excluded | n/a | n/a | 0 | No data in the dataset |

## Still to verify (per name, from annual reports and IDX data)

- Free float % and major shareholders
- Share of revenue from palm oil (CPO, PK, FFB) vs downstream or other businesses
- Planted and mature hectares, tree age profile
- Exact daily traded value from a full daily price series, replacing the estimates above
