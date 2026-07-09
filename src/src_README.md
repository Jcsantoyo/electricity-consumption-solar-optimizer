# Source code documentation

This folder contains the main Python source code used by the project.

The code is organized into small modules for data loading, solar simulation, battery simulation, tariffs, optimization, forecasting and visualization.

---

## Main entry point

### `main.py`

Runs the main historical optimization pipeline.

It loads consumption data, loads solar data, runs the grid search optimization, selects the best scenarios, saves reports and generates plots.

Equivalent command:

```bash
python src/main.py
```

---

## Configuration

### `config.py`

Central configuration file for the project.

It defines:

- Input data paths
- PVGIS settings
- Output paths
- Simulation settings
- Solar powers tested
- Battery capacities tested
- Battery model parameters
- Economic assumptions
- Active tariff profile
- Tariff profiles

Most project parameters can be changed here.

---

## Data loading

### `data_loader.py`

Loads consumption data in the standard project format:

```csv
datetime,consumption_kwh
```

It also adds useful time-based columns.

### `uci_household_loader.py`

Loads and processes the UCI Individual Household Electric Power Consumption dataset.

It converts minute-level power measurements into hourly energy consumption.

### `solar_data_loader.py`

Loads PVGIS solar generation data.

It parses timestamps, converts power to hourly energy and matches solar generation to consumption timestamps using month, day and hour.

---

## Energy simulation

### `solar.py`

Contains functions for synthetic solar generation and solar self-consumption simulation.

### `battery.py`

Simulates battery behavior hour by hour.

It models:

- Battery capacity
- Charging
- Discharging
- Charge efficiency
- Power limits
- Grid import
- Solar surplus
- Battery state of charge

### `scenarios.py`

Contains scenario comparison utilities used during early simulation development.

---

## Economics and tariffs

### `economics.py`

Computes economic metrics such as:

- Solar installation cost
- Battery installation cost
- Total investment cost
- Simple payback period

### `tariff.py`

Implements the configurable electricity tariff model.

It supports:

- Peak, flat and off-peak prices
- Spanish 2.0TD-style period classification
- Weekend off-peak behavior
- Surplus compensation
- Contracted power fixed cost
- Net electricity cost calculation

---

## Optimization

### `optimization.py`

Runs the solar and battery grid search optimization.

It evaluates combinations of:

- Solar peak power
- Battery capacity

For each scenario, it computes:

- Investment cost
- Annual savings
- Payback period
- Self-sufficiency
- Grid import
- Annual grid import
- Solar surplus

It also builds summary reports and the outputs index.

---

## Forecasting

### `forecasting.py`

Contains the Machine Learning forecasting pipeline.

It creates time series features such as:

- Hour
- Day
- Month
- Weekday
- Weekend flag
- Consumption lag 1 hour
- Consumption lag 24 hours

It trains and evaluates:

- Linear Regression
- Random Forest Regressor

It also builds forecasted consumption data compatible with the optimization pipeline.

---

## Visualization

### `visualization.py`

Generates all project plots.

It includes plots for:

- Payback grid search
- Self-sufficiency grid search
- Best scenario comparison
- Best scenario time series
- Battery state of charge
- Cumulative energy flows
- Forecast actual vs predicted
- Forecast feature importance
- Forecasting model comparison
- Historical vs forecast-based comparison plots

---

## Notes

The main project execution should normally be done from the root folder using:

```bash
make pipeline
```

or:

```bash
python scripts/run_full_pipeline.py
```
