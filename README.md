# FX Options Portfolio Risk Aggregator

A Python application that reads a portfolio of FX options, prices each trade using the Garman-Kohlhagen model, and produces trade-level and portfolio-level risk reports.

## Getting Started

```bash
pip install -r requirements.txt
python src/app.py --input data/fx_trades.xlsx --output data/output.xlsx
```

## Tests

```bash
pytest tests/
```

---

## Design

### Architecture

The application follows a layered architecture with a central `FXPortfolio` object that holds state and coordinates the pipeline from loading initial data through to writing the output report.

### Pricing Model

Uses the Garman-Kohlhagen model, which extends Black-Scholes for FX options by treating the foreign currency as a continuous dividend yield. Vanilla Black-Scholes does not account for the foreign risk-free rate and would misprice FX options.

```
PV (Call) = N * [S * e^(-r_f*T) * N(d1) - K * e^(-r_d*T) * N(d2)]
PV (Put)  = N * [K * e^(-r_d*T) * N(-d2) - S * e^(-r_f*T) * N(-d1)]

d1 = [ln(S/K) + (r_d - r_f + 0.5*σ²)*T] / (σ*√T)
d2 = d1 - σ*√T
```

Where `S` = spot, `K` = strike, `σ` = implied vol, `T` = expiry in years, `r_d` = domestic rate (quote ccy), `r_f` = foreign rate (base ccy), `N()` = cumulative normal distribution.

### Greeks Conventions

| Greek | Convention |
|-------|-----------|
| Delta | Unscaled spot delta — between 0 and 1 for calls, -1 and 0 for puts |
| Vega | Unscaled, per 1% move in implied vol per unit of spot |
| PV | Scaled by notional in the notional currency |

### Portfolio Aggregation

Aggregated by `notional_ccy` — USD trades (EUR/USD, GBP/USD) and JPY trades (USD/JPY) are reported separately. Cross-currency aggregation is intentionally avoided since summing USD and JPY PVs without FX conversion is meaningless.

---

## Assumptions

- Volatility, rates, and expiry are in decimal form — e.g. `0.11` for 11%, `0.25` for 3 months
- `RateDomestic` is the rate of the quote currency — e.g. USD for EUR/USD, JPY for USD/JPY
- `RateForeign` is the rate of the base currency — e.g. EUR for EUR/USD, USD for USD/JPY
- Notional is always positive — short positions should be represented separately
- Constant volatility assumed (flat vol surface)
- `NotionalCurrency` must be one of the two currencies in the underlying pair

---

## Input Format

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| TradeID | str | Unique trade identifier | T000001 |
| Underlying | str | Currency pair | EUR/USD |
| Notional | float | Trade notional | 1000000 |
| NotionalCurrency | str | 3-letter currency code | USD |
| Spot | float | Current FX spot rate | 1.10 |
| Strike | float | Option strike price | 1.12 |
| Vol | float | Implied volatility (decimal) | 0.11 |
| RateDomestic | float | Domestic risk-free rate (decimal) | 0.02 |
| RateForeign | float | Foreign risk-free rate (decimal) | 0.01 |
| Expiry | float | Time to expiry in years | 0.25 |
| OptionType | str | Call or Put (case insensitive) | Call |

## Output Format

Two-sheet xlsx file:

**Summary** — portfolio-level totals by notional currency: `notional_ccy`, `total_pv`, `total_delta`, `total_vega`

**Trades** — trade-level results sorted by notional currency: `trade_id`, `notional_ccy`, `pv`, `delta`, `vega`, `itm`