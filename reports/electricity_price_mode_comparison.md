# Electricity Price Mode Comparison

This report compares different electricity price models using the same hourly grid-import profile.

## Input data

- Energy data: `reports/best_scenario_timeseries.csv`
- Hourly electricity prices: `data/processed/omie_hourly_prices.csv`
- Fixed electricity price: `0.2000 EUR/kWh`

## Results

| Price mode | Variable grid cost | Difference vs fixed | Difference vs 2.0TD |
|---|---:|---:|---:|
| flat_fixed | 184.86 EUR | 0.00 EUR | 45.98 EUR |
| spanish_2_0td | 138.88 EUR | -45.98 EUR | 0.00 EUR |
| hourly | 82.41 EUR | -102.46 EUR | -56.48 EUR |

## Cheapest price mode

The lowest variable grid-import cost is obtained with `hourly`:

**82.41 EUR**

## Interpretation

Only the variable cost of imported electricity is compared here.
Fixed power charges, taxes, meter rental and surplus compensation are not included in this comparison.
OMIE values represent wholesale market prices and are not equivalent to a complete household retail electricity tariff.
