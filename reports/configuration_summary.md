# Project Configuration Summary

This file summarizes the configuration used by the project pipeline.

## Input data

- Consumption data path: `data/processed/uci_consumption_omie_scenario.csv`
- Use PVGIS solar data: `True`
- PVGIS solar data path: `data/raw/pvgis_hourly_linares_1kw_2020.csv`

## Electricity price data

- Use hourly electricity prices: `True`
- Hourly price data path: `data/processed/omie_hourly_prices.csv`
- Allow negative hourly prices: `True`
- Electricity price mode: Hourly electricity prices (data/processed/omie_hourly_prices.csv); fixed power cost and surplus compensation from tariff profile 'spanish_2_0td_example'

## Simulation settings

- Days per year: `365`

## Grid search parameters

- Solar peak powers tested:

```text
0.5, 1.0, 1.5, 2.0, 3.0 kW
```

- Battery capacities tested:

```text
0, 0.5, 1.0, 2.0, 3.0, 5.0 kWh
```

## Battery model

- Battery efficiency: `0.9`
- Maximum charge power: `1.0` kW
- Maximum discharge power: `1.0` kW
- Initial battery state: `0.0` kWh

## Economic assumptions

- Fixed installation cost: `800.0` EUR
- Solar cost: `900.0` EUR/kW
- Battery cost: `500.0` EUR/kWh

## Active tariff profile

- Active tariff profile: `spanish_2_0td_example`

### Active tariff values

- Peak price: `0.25` EUR/kWh
- Flat price: `0.18` EUR/kWh
- Off-peak price: `0.12` EUR/kWh
- Surplus compensation: `0.07` EUR/kWh
- Contracted power: `4.6` kW
- Power price: `35.0` EUR/kW/year

## Available tariff profiles

- `flat_price`
- `spanish_2_0td_example`

## Notes

The tariff profile values are illustrative assumptions.
When hourly prices are enabled, they replace the tariff profile prices
for the variable cost of imported electricity.
The tariff profile still provides fixed power costs and surplus compensation.
OMIE prices represent wholesale market prices, not a complete household
retail electricity tariff.
