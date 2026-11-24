# Assumptions

Every assumption used in models, valuations or backtests goes here with its source and date. Update the entry when it changes, and keep the history in the Changes column.

| ID | Area | Assumption | Value | Source / basis | Date set | Changes |
|---|---|---|---|---|---|---|
| A-001 | Quant | Liquidity threshold for the core universe (approx. average daily traded value) | ≥ IDR 1.5bn | Judgement; screen in `research/industry/2026-11-24_universe_screen.md` (S-001) | 2026-11-24 | — |
| A-002 | Quant | Liquidity band for the extended universe | IDR 0.25–1.5bn | Same as A-001 | 2026-11-24 | — |

## Areas to cover

- **Macro:** CPO price deck (MYR/t, USD/t), IDR/USD, export levy and duty schedule, biodiesel mandate path.
- **Industry:** FFB yields by tree age, oil extraction rate, cash cost per tonne, replanting rates.
- **Company:** planted and mature hectares, production growth, capex, dividend payout.
- **Valuation:** risk-free rate, equity risk premium, country risk premium, beta, terminal growth, EV per planted hectare.
- **Quant:** rebalancing frequency, transaction costs, publication lags, liquidity filters.
