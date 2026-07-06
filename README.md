# Electricity Consumption Solar Optimizer

![Python tests](https://github.com/Jcsantoyo/electricity-consumption-solar-optimizer/actions/workflows/tests.yml/badge.svg)

A data science project that analyzes residential electricity consumption, photovoltaic solar generation, battery storage, electricity tariffs, economic optimization and Machine Learning forecasting.

The project combines:

- Real household electricity consumption data
- PVGIS solar generation data
- Battery simulation
- Configurable electricity tariff profiles
- Economic analysis
- Grid search optimization
- Machine Learning consumption forecasting
- Forecast-based solar and battery optimization
- Historical vs forecast-based optimization comparison
- Model comparison
- Feature importance analysis
- Automated reports and plots
- Unit tests and GitHub Actions CI

The goal is to estimate which solar and battery configuration provides the best trade-off between investment cost, payback period and energy self-sufficiency.

---

## Project overview

This project simulates how a household could reduce grid electricity consumption by installing photovoltaic solar panels and, optionally, a battery.

The main pipeline:

1. Loads household electricity consumption data.
2. Loads realistic solar generation data from PVGIS.
3. Simulates solar self-consumption.
4. Simulates battery charging and discharging.
5. Computes grid import and solar surplus.
6. Applies a configurable electricity tariff model.
7. Estimates investment cost, yearly savings and payback.
8. Performs a grid search over solar and battery sizes.
9. Selects the best economic and energy scenarios.
10. Generates reports and plots automatically.

The forecasting pipeline:

1. Trains Machine Learning models using historical consumption.
2. Evaluates forecast accuracy.
3. Compares forecasting models.
4. Computes feature importance.
5. Uses predicted consumption as input for a forecast-based optimization pipeline.
6. Compares historical and forecast-based optimization results.

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

## Electricity tariff model

The project includes a simplified configurable electricity tariff model.

The current active tariff profile is:

```text
spanish_2_0td_example
```

This profile approximates the Spanish 2.0TD structure using three energy periods:

```text
off_peak
flat
peak
```

The tariff model includes:

- Different energy prices for peak, flat and off-peak periods.
- Weekend off-peak behavior.
- Surplus compensation.
- Contracted power fixed cost.

The prices are not intended to represent a specific electricity company contract. They are configurable assumptions defined in:

```text
src/config.py
```

This allows the project to compare different tariff scenarios without changing the optimization code.

---

## Main historical optimization results

Using the public real household consumption dataset, PVGIS solar generation and the configurable Spanish 2.0TD example tariff, the current best historical scenarios are:

### Best historical economic scenario

```text
Solar peak power: 3.00 kW
Battery capacity: 0.00 kWh
Investment cost: 3500.00 EUR
Annual savings: 684.83 EUR/year
Payback: 5.11 years
Self-sufficiency: 31.58%
Grid import: 25510.35 kWh
Annual grid import: 6464.45 kWh/year
Solar surplus: 7925.40 kWh
```

### Best historical self-sufficiency scenario

```text
Solar peak power: 3.00 kW
Battery capacity: 5.00 kWh
Investment cost: 6000.00 EUR
Annual savings: 819.44 EUR/year
Payback: 7.32 years
Self-sufficiency: 43.98%
Grid import: 20885.34 kWh
Annual grid import: 5292.28 kWh/year
Solar surplus: 2786.51 kWh
```

### Main conclusion

The economically optimal scenario is not necessarily the scenario with the highest energy self-sufficiency.

In the current historical simulation:

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

## Forecast-based optimization

The project can also use Machine Learning predictions as input for the solar and battery optimization pipeline.

Instead of optimizing only on historical consumption, the project can:

1. Train a forecasting model using historical household consumption.
2. Generate predicted future consumption.
3. Convert the predictions into the standard project format.
4. Run the solar and battery optimization pipeline on the forecasted consumption.

This connects the forecasting module with the economic optimization module.

Run:

```bash
python scripts/run_forecast_optimization.py
```

This generates:

```text
reports/forecasted_consumption_for_optimization.csv
reports/forecast_optimization_results.csv
reports/forecast_optimization_best_scenarios.csv
```

Current forecast-based optimization results:

### Best forecast-based economic scenario

```text
Solar peak power: 2.00 kW
Battery capacity: 0.00 kWh
Investment cost: 2600.00 EUR
Annual savings: 551.64 EUR/year
Payback: 4.71 years
Self-sufficiency: 30.46%
Annual grid import: 6151.91 kWh/year
```

### Best forecast-based self-sufficiency scenario

```text
Solar peak power: 3.00 kW
Battery capacity: 5.00 kWh
Investment cost: 6000.00 EUR
Annual savings: 865.36 EUR/year
Payback: 6.93 years
Self-sufficiency: 49.96%
Annual grid import: 4438.78 kWh/year
```

The forecast-based optimization can produce a different best economic scenario than the historical optimization. In the current results, the historical optimization selects 3 kW solar for the best payback, while the forecast-based optimization selects 2 kW solar.

This shows that the optimal solar and battery configuration may depend on whether the decision is based on past consumption or predicted future consumption.

---

## Historical vs forecast-based comparison

The project can compare the best scenarios obtained from historical optimization and forecast-based optimization.

Run:

```bash
python scripts/compare_optimization_results.py
```

This script reads:

```text
reports/best_scenarios.csv
reports/forecast_optimization_best_scenarios.csv
```

and generates:

```text
reports/historical_vs_forecast_optimization.csv
images/historical_vs_forecast_payback.png
images/historical_vs_forecast_savings.png
images/historical_vs_forecast_self_sufficiency.png
images/historical_vs_forecast_investment_cost.png
images/historical_vs_forecast_grid_import.png
```

This report allows direct comparison between:

- Historical optimization results
- Forecast-based optimization results

The comparison includes:

- Payback period
- Annual savings
- Self-sufficiency
- Investment cost
- Annual grid import

Example insight:

```text
Historical best payback:
3.00 kW solar, 0.00 kWh battery

Forecast-based best payback:
2.00 kW solar, 0.00 kWh battery
```

This shows that the optimal solar and battery configuration may change depending on whether the decision is based on historical consumption or predicted future consumption.

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
│   ├── forecast_model_comparison.png
│   ├── historical_vs_forecast_payback.png
│   ├── historical_vs_forecast_savings.png
│   ├── historical_vs_forecast_self_sufficiency.png
│   ├── historical_vs_forecast_investment_cost.png
│   └── historical_vs_forecast_grid_import.png
│
├── reports/
│   ├── grid_search_results.csv
│   ├── best_scenarios.csv
│   ├── best_scenario_timeseries.csv
│   ├── forecast_results.csv
│   ├── forecast_feature_importance.csv
│   ├── forecast_model_comparison.csv
│   ├── forecasted_consumption_for_optimization.csv
│   ├── forecast_optimization_results.csv
│   ├── forecast_optimization_best_scenarios.csv
│   ├── historical_vs_forecast_optimization.csv
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
│   ├── compare_optimization_results.py
│   ├── download_pvgis_data.py
│   ├── generate_synthetic_consumption.py
│   ├── prepare_uci_household_power.py
│   ├── run_forecasting.py
│   ├── run_forecast_optimization.py
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
│   ├── test_solar_data_loader.py
│   └── test_tariff.py
│
├── requirements.txt
├── .gitattributes
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

## Running the forecast-based optimization pipeline

Run:

```bash
python scripts/run_forecast_optimization.py
```

This generates:

```text
reports/forecasted_consumption_for_optimization.csv
reports/forecast_optimization_results.csv
reports/forecast_optimization_best_scenarios.csv
```

This script connects the Machine Learning forecasting module with the solar and battery optimization pipeline.

---

## Running the historical vs forecast comparison

Run:

```bash
python scripts/compare_optimization_results.py
```

This generates:

```text
reports/historical_vs_forecast_optimization.csv
images/historical_vs_forecast_payback.png
images/historical_vs_forecast_savings.png
images/historical_vs_forecast_self_sufficiency.png
images/historical_vs_forecast_investment_cost.png
images/historical_vs_forecast_grid_import.png
```

This report compares the best scenarios from historical optimization and forecast-based optimization.

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
- Tariff calculations

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

Computes basic economic metrics:

- Solar installation cost
- Battery installation cost
- Total investment cost
- Simple payback period

Earlier flat-price cost utilities are kept as simple reusable economic helpers.

---

### `src/tariff.py`

Contains the electricity tariff logic used by the optimization pipeline.

It supports:

- Spanish 2.0TD period classification
- Peak, flat and off-peak energy prices
- Weekend off-peak behavior
- Surplus compensation
- Contracted power fixed cost
- Net electricity cost calculation

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
- Annual grid import
- Solar surplus

The optimization uses the active tariff profile from the configuration.

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

It also computes feature importance for the Random Forest model and can convert predicted consumption into a dataset compatible with the optimization pipeline.

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
- Historical vs forecast-based payback comparison
- Historical vs forecast-based annual savings comparison
- Historical vs forecast-based self-sufficiency comparison
- Historical vs forecast-based investment cost comparison
- Historical vs forecast-based annual grid import comparison

---

## Generated reports

### `reports/grid_search_results.csv`

Contains all tested solar and battery scenarios for the historical optimization.

### `reports/best_scenarios.csv`

Contains the best historical economic scenario and the best historical self-sufficiency scenario.

### `reports/best_scenario_timeseries.csv`

Contains the hourly simulation results for the selected best historical scenario.

### `reports/forecast_results.csv`

Contains actual and predicted consumption values for the forecasting test set.

### `reports/forecast_feature_importance.csv`

Contains Random Forest feature importance values.

### `reports/forecast_model_comparison.csv`

Compares the forecasting models using MAE and RMSE.

### `reports/forecasted_consumption_for_optimization.csv`

Contains forecasted consumption converted into the standard optimization input format.

### `reports/forecast_optimization_results.csv`

Contains all tested solar and battery scenarios for the forecast-based optimization.

### `reports/forecast_optimization_best_scenarios.csv`

Contains the best economic and self-sufficiency scenarios from the forecast-based optimization.

### `reports/historical_vs_forecast_optimization.csv`

Compares the best historical optimization scenarios with the best forecast-based optimization scenarios.

### `reports/summary.txt`

Text summary of the main historical optimization results.

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

### Historical vs forecast-based payback comparison

```text
images/historical_vs_forecast_payback.png
```

Compares the payback period of the best historical optimization scenarios against the best forecast-based optimization scenarios.

### Historical vs forecast-based annual savings comparison

```text
images/historical_vs_forecast_savings.png
```

Compares the estimated annual savings of the best historical optimization scenarios against the best forecast-based optimization scenarios.

### Historical vs forecast-based self-sufficiency comparison

```text
images/historical_vs_forecast_self_sufficiency.png
```

Compares the self-sufficiency percentage of the best historical optimization scenarios against the best forecast-based optimization scenarios.

### Historical vs forecast-based investment cost comparison

```text
images/historical_vs_forecast_investment_cost.png
```

Compares the investment cost of the best historical optimization scenarios against the best forecast-based optimization scenarios.

### Historical vs forecast-based annual grid import comparison

```text
images/historical_vs_forecast_grid_import.png
```

Compares annualized grid import of the best historical optimization scenarios against the best forecast-based optimization scenarios.

These comparison plots help visualize how the recommended solar and battery configuration can change when the optimization uses predicted future consumption instead of historical consumption.

---

## Example output

Example output from the main historical optimization pipeline:

```text
Best scenario by payback:
Solar peak power: 3.00 kW
Battery capacity: 0.00 kWh
Investment cost: 3500.00 EUR
Annual savings: 684.83 EUR/year
Payback: 5.11 years
Self-sufficiency: 31.58%

Best scenario by self-sufficiency:
Solar peak power: 3.00 kW
Battery capacity: 5.00 kWh
Investment cost: 6000.00 EUR
Annual savings: 819.44 EUR/year
Payback: 7.32 years
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

Example output from the forecast-based optimization pipeline:

```text
Best forecast-based scenario by payback:
Solar peak power: 2.00 kW
Battery capacity: 0.00 kWh
Annual savings: 551.64 EUR/year
Payback: 4.71 years
Self-sufficiency: 30.46%

Best forecast-based scenario by self-sufficiency:
Solar peak power: 3.00 kW
Battery capacity: 5.00 kWh
Annual savings: 865.36 EUR/year
Payback: 6.93 years
Self-sufficiency: 49.96%
```

Example insight from the historical vs forecast-based comparison:

```text
Historical best payback:
3.00 kW solar, 0.00 kWh battery

Forecast-based best payback:
2.00 kW solar, 0.00 kWh battery
```

---

## Why this project is useful

This project shows how data science can be applied to a real energy optimization problem.

It combines:

- Time series data processing
- Real-world energy data
- Solar generation modeling
- Battery simulation
- Configurable electricity tariffs
- Economic optimization
- Machine Learning forecasting
- Forecast-based decision making
- Historical vs forecast-based scenario comparison
- Model evaluation
- Automated reporting
- Software testing
- Continuous integration

The project can be adapted to a real household by replacing the public dataset with consumption data downloaded from a smart meter, Datadis or an electricity distributor.

---

## Future improvements

Possible next steps:

- Add support for hourly electricity price CSV files.
- Add optional PVPC/ESIOS hourly price downloader.
- Include fixed taxes and additional regulated charges.
- Use weather variables for forecasting.
- Add more forecasting models.
- Implement recursive multi-step forecasting.
- Add a YAML configuration file.
- Add a command-line interface.
- Add a Streamlit dashboard.
- Compare public dataset results with real household smart meter data.