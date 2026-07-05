# Electricity Consumption Solar Optimizer

![Python tests](https://github.com/Jcsantoyo/electricity-consumption-solar-optimizer/actions/workflows/tests.yml/badge.svg)

A data science project that analyzes residential electricity consumption, photovoltaic solar generation, battery storage and economic optimization.

The project combines:

- Real household electricity consumption data
- PVGIS solar generation data
- Battery simulation
- Economic analysis
- Grid search optimization
- Machine Learning consumption forecasting
- Model comparison
- Feature importance analysis
- Automated reports and plots
- Unit tests and GitHub Actions CI

The goal is to estimate which solar and battery configuration provides the best trade-off between investment cost, payback period and self-sufficiency.

---

## Project overview

This project simulates how a household could reduce grid electricity consumption by installing photovoltaic solar panels and, optionally, a battery.

The pipeline:

1. Loads household electricity consumption data.
2. Loads realistic solar generation data from PVGIS.
3. Simulates solar self-consumption.
4. Simulates battery charging and discharging.
5. Computes grid import and solar surplus.
6. Estimates investment cost, yearly savings and payback.
7. Performs a grid search over solar and battery sizes.
8. Selects the best scenarios.
9. Forecasts future electricity consumption using Machine Learning.
10. Generates reports and plots automatically.

---

## Current dataset

The project currently uses a public real-world residential electricity dataset:

**UCI Individual Household Electric Power Consumption Dataset**

This dataset contains electricity measurements from a real household with minute-level resolution over almost four years.

The raw dataset is converted into hourly electricity consumption with the following format:

```csv
datetime,consumption_kwh
2006-12-16 17:00:00,2.533733
2006-12-16 18:00:00,3.632200
```

The processed dataset used by the project is:

```text
data/processed/uci_household_power_hourly.csv
```

The original synthetic dataset is still useful for testing and quick experiments, but the main pipeline now uses the public real household consumption dataset.

---

## Solar data

Solar generation data is obtained from PVGIS for Linares, Spain.

The PVGIS file used by the project is:

```text
data/raw/pvgis_hourly_linares_1kw_2020.csv
```

The PVGIS data represents hourly solar generation for a 1 kW photovoltaic system. The project scales this generation according to the tested solar peak power.

Example:

```text
1 kW PVGIS generation × 3.0 = 3 kW solar installation
```

Since the consumption dataset and PVGIS data correspond to different years, the matching is performed using:

```text
month + day + hour
```

This allows the project to combine real household consumption patterns with realistic solar generation profiles.

---

## Main results

Using the public real household consumption dataset and PVGIS solar generation, the current best scenarios are:

### Best economic scenario

```text
Solar peak power: 3.00 kW
Battery capacity: 0.00 kWh
Investment cost: 3500.00 EUR
Annual savings: 736.44 EUR/year
Payback: 4.75 years
Self-sufficiency: 31.58%
Grid import: 25510.35 kWh
Solar surplus: 7925.40 kWh
```

### Best self-sufficiency scenario

```text
Solar peak power: 3.00 kW
Battery capacity: 5.00 kWh
Investment cost: 6000.00 EUR
Annual savings: 879.53 EUR/year
Payback: 6.82 years
Self-sufficiency: 43.98%
Grid import: 20885.34 kWh
Solar surplus: 2786.51 kWh
```

### Main conclusion

The economically optimal scenario is not necessarily the scenario with the highest energy self-sufficiency.

In the current simulation:

- The best payback is achieved with solar panels only.
- Adding a battery improves self-sufficiency.
- However, the battery increases the investment cost and therefore increases the payback period.

---

## Forecasting results

The project also includes a Machine Learning module for electricity consumption forecasting.

The current forecasting models are:

- Linear Regression
- Random Forest Regressor

Current results using the public real household dataset:

```text
Random Forest MAE: 0.3368 kWh
Random Forest RMSE: 0.4886 kWh

Linear Regression MAE: 0.3755 kWh
Linear Regression RMSE: 0.5241 kWh
```

The Random Forest model performs better than the Linear Regression baseline.

### Feature importance

Current Random Forest feature importance:

```text
consumption_kwh_lag_1      0.622855
hour                       0.114752
consumption_kwh_lag_24     0.111544
day                        0.062347
month                      0.045991
weekday                    0.035974
is_weekend                 0.006538
```

The most important feature is the consumption in the previous hour. This makes sense because real electricity consumption has short-term continuity, but it is less perfectly repetitive than a synthetic daily pattern.

---

## Repository structure

```text
electricity-consumption-solar-optimizer/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── data/
│   ├── raw/
│   │   ├── household_power_consumption.txt
│   │   └── pvgis_hourly_linares_1kw_2020.csv
│   │
│   ├── processed/
│   │   └── uci_household_power_hourly.csv
│   │
│   └── simulated/
│       └── synthetic_consumption_30_days.csv
│
├── images/
│   ├── main_payback_grid_search.png
│   ├── main_self_sufficiency_grid_search.png
│   ├── best_scenarios_comparison.png
│   ├── best_scenario_timeseries.png
│   ├── best_scenario_battery_state.png
│   ├── best_scenario_cumulative_energy.png
│   ├── consumption_forecast_actual_vs_predicted.png
│   ├── forecast_feature_importance.png
│   └── forecast_model_comparison.png
│
├── reports/
│   ├── grid_search_results.csv
│   ├── best_scenarios.csv
│   ├── best_scenario_timeseries.csv
│   ├── forecast_results.csv
│   ├── forecast_feature_importance.csv
│   ├── forecast_model_comparison.csv
│   ├── summary.txt
│   └── outputs_index.md
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_solar_battery_simulation.ipynb
│   ├── 03_optimization_analysis.ipynb
│   └── 04_consumption_forecasting.ipynb
│
├── scripts/
│   ├── download_pvgis_data.py
│   ├── generate_synthetic_consumption.py
│   ├── prepare_uci_household_power.py
│   ├── run_forecasting.py
│   ├── test_pvgis_generation_match.py
│   └── test_pvgis_loader.py
│
├── src/
│   ├── battery.py
│   ├── config.py
│   ├── data_loader.py
│   ├── economics.py
│   ├── forecasting.py
│   ├── main.py
│   ├── optimization.py
│   ├── scenarios.py
│   ├── solar.py
│   ├── solar_data_loader.py
│   ├── tariff.py
│   ├── uci_household_loader.py
│   └── visualization.py
│
├── tests/
│   ├── test_battery.py
│   ├── test_economics.py
│   ├── test_forecasting.py
│   └── test_solar_data_loader.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Jcsantoyo/electricity-consumption-solar-optimizer.git
cd electricity-consumption-solar-optimizer
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Preparing the public consumption dataset

The project uses the UCI household power consumption dataset.

After downloading and extracting the original dataset, place the file here:

```text
data/raw/household_power_consumption.txt
```

Then run:

```bash
python scripts/prepare_uci_household_power.py
```

This generates:

```text
data/processed/uci_household_power_hourly.csv
```

The conversion process:

```text
minute-level power data
        ↓
convert kW to kWh per minute
        ↓
resample by hour
        ↓
generate hourly consumption dataset
```

The resulting file has the standard project format:

```csv
datetime,consumption_kwh
2006-12-16 17:00:00,2.533733
2006-12-16 18:00:00,3.632200
```

---

## Running the main optimization pipeline

Run:

```bash
python src/main.py
```

This generates:

```text
reports/grid_search_results.csv
reports/best_scenarios.csv
reports/best_scenario_timeseries.csv
reports/summary.txt
reports/outputs_index.md
```

and plots in:

```text
images/
```

---

## Running the forecasting pipeline

Run:

```bash
python scripts/run_forecasting.py
```

This generates:

```text
reports/forecast_results.csv
reports/forecast_feature_importance.csv
reports/forecast_model_comparison.csv
```

and plots:

```text
images/consumption_forecast_actual_vs_predicted.png
images/forecast_feature_importance.png
images/forecast_model_comparison.png
```

---

## Running tests

Run:

```bash
python -m pytest
```

The project includes tests for:

- Economic calculations
- Battery simulation
- PVGIS solar data loading
- Forecasting utilities

GitHub Actions automatically runs the test suite on pushes and pull requests.

---

## Main modules

### `src/data_loader.py`

Loads electricity consumption data in the standard project format:

```csv
datetime,consumption_kwh
```

It also adds useful time-based features such as hour, day, month and weekday.

---

### `src/uci_household_loader.py`

Loads and converts the UCI household power consumption dataset.

Main tasks:

- Read the original semicolon-separated file.
- Handle missing values.
- Parse date and time columns.
- Convert minute-level power values into energy.
- Aggregate data to hourly consumption.

---

### `src/solar_data_loader.py`

Loads PVGIS solar generation data.

Main tasks:

- Parse PVGIS timestamps.
- Convert power values to hourly energy.
- Match PVGIS generation to consumption timestamps using month, day and hour.
- Scale 1 kW generation to any tested solar peak power.

---

### `src/battery.py`

Simulates battery behavior hour by hour.

It considers:

- Battery capacity
- Charge efficiency
- Maximum charging power
- Maximum discharging power
- Battery state of charge
- Grid import
- Solar surplus

---

### `src/economics.py`

Computes economic metrics:

- Solar installation cost
- Battery installation cost
- Total investment cost
- Grid electricity cost
- Surplus compensation
- Net cost
- Annual savings
- Simple payback period

---

### `src/optimization.py`

Runs the grid search over solar and battery configurations.

It evaluates combinations of:

```text
solar peak power
battery capacity
```

For each scenario, it computes:

- Investment cost
- Annual savings
- Payback
- Self-sufficiency
- Grid import
- Solar surplus

---

### `src/forecasting.py`

Contains the Machine Learning forecasting pipeline.

It creates features such as:

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

It also computes feature importance for the Random Forest model.

---

### `src/visualization.py`

Generates plots for:

- Payback grid search
- Self-sufficiency grid search
- Best scenario comparison
- Best scenario time series
- Battery state of charge
- Cumulative energy balance
- Forecast actual vs predicted
- Forecast feature importance
- Forecasting model comparison

---

## Generated reports

### `reports/grid_search_results.csv`

Contains all tested solar and battery scenarios.

### `reports/best_scenarios.csv`

Contains the best economic scenario and the best self-sufficiency scenario.

### `reports/best_scenario_timeseries.csv`

Contains the hourly simulation results for the selected best scenario.

### `reports/forecast_results.csv`

Contains actual and predicted consumption values for the forecasting test set.

### `reports/forecast_feature_importance.csv`

Contains Random Forest feature importance values.

### `reports/forecast_model_comparison.csv`

Compares the forecasting models using MAE and RMSE.

### `reports/summary.txt`

Text summary of the main optimization results.

### `reports/outputs_index.md`

Index of generated reports and plots.

---

## Generated plots

### Payback grid search

```text
images/main_payback_grid_search.png
```

Shows how the payback period changes depending on solar size and battery capacity.

### Self-sufficiency grid search

```text
images/main_self_sufficiency_grid_search.png
```

Shows how energy self-sufficiency changes depending on solar size and battery capacity.

### Best scenarios comparison

```text
images/best_scenarios_comparison.png
```

Compares the best economic scenario and the best self-sufficiency scenario.

### Best scenario time series

```text
images/best_scenario_timeseries.png
```

Shows consumption, solar generation and grid import over time.

### Battery state of charge

```text
images/best_scenario_battery_state.png
```

Shows how the battery charges and discharges over time.

### Cumulative energy balance

```text
images/best_scenario_cumulative_energy.png
```

Shows accumulated consumption, solar generation and grid import.

### Forecast actual vs predicted

```text
images/consumption_forecast_actual_vs_predicted.png
```

Compares real consumption with Machine Learning predictions.

### Forecast feature importance

```text
images/forecast_feature_importance.png
```

Shows which features are most important for the Random Forest forecast.

### Forecasting model comparison

```text
images/forecast_model_comparison.png
```

Compares forecasting models using MAE.

---

## Example output

Example output from the main pipeline:

```text
Best scenario by payback:
Solar peak power: 3.00 kW
Battery capacity: 0.00 kWh
Investment cost: 3500.00 EUR
Annual savings: 736.44 EUR/year
Payback: 4.75 years
Self-sufficiency: 31.58%

Best scenario by self-sufficiency:
Solar peak power: 3.00 kW
Battery capacity: 5.00 kWh
Investment cost: 6000.00 EUR
Annual savings: 879.53 EUR/year
Payback: 6.82 years
Self-sufficiency: 43.98%
```

Example output from the forecasting pipeline:

```text
Consumption forecast results:
MAE: 0.3368 kWh
RMSE: 0.4886 kWh

Model comparison:
Random Forest       MAE: 0.3368    RMSE: 0.4886
Linear Regression   MAE: 0.3755    RMSE: 0.5241
```

---

## Why this project is useful

This project shows how data science can be applied to a real energy optimization problem.

It combines:

- Time series data processing
- Real-world energy data
- Solar generation modeling
- Battery simulation
- Economic optimization
- Machine Learning forecasting
- Model evaluation
- Automated reporting
- Software testing
- Continuous integration

The project can be adapted to a real household by replacing the public dataset with consumption data downloaded from a smart meter, Datadis or an electricity distributor.

---

## Future improvements

Possible next steps:

- Add Spanish electricity tariffs with peak, flat and off-peak periods.
- Include fixed power terms, taxes and surplus compensation limits.
- Use weather variables for forecasting.
- Add more forecasting models.
- Use forecasted consumption inside the optimization pipeline.
- Add a YAML configuration file.
- Add a command-line interface.
- Add a Streamlit dashboard.
- Compare public dataset results with real household smart meter data.