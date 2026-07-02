# Project outputs

Solar data source: PVGIS solar data (data/raw/pvgis_hourly_linares_1kw_2020.csv)

This folder contains the generated reports from the electricity consumption solar optimizer.

## CSV reports

### `grid_search_results.csv`

Full grid search results. Each row represents one combination of solar peak power and battery capacity, including investment cost, annual savings, payback period, grid import, solar surplus and self-sufficiency.

### `best_scenarios.csv`

Summary table with the two selected optimal scenarios: one by minimum payback period and one by maximum self-sufficiency.

### `best_scenario_timeseries.csv`

Hourly energy flow table for the best economic scenario. It includes consumption, solar generation, self-consumption, battery charge, battery discharge, grid import, solar surplus and battery state.

## Text reports

### `summary.txt`

Readable summary of the best economic scenario and the best self-sufficiency scenario.

## Generated plots

The main plots are saved in the `images/` folder:

- `main_payback_grid_search.png`: payback period by solar power and battery capacity.
- `main_self_sufficiency_grid_search.png`: self-sufficiency by solar power and battery capacity.
- `best_scenarios_comparison.png`: comparison between the economic optimum and the energy optimum.
- `best_scenario_timeseries.png`: hourly consumption, solar generation and grid import for the best economic scenario.
- `best_scenario_battery_state.png`: battery state of charge over time.
- `best_scenario_cumulative_energy.png`: cumulative consumption, solar generation, grid import and solar surplus.
