# Electricity Consumption Solar Optimizer

A data science project for analyzing household electricity consumption, simulating solar self-consumption, modeling battery storage, and comparing economic and energy optimization scenarios.

The goal of this project is to estimate how different photovoltaic and battery configurations affect:

- Grid electricity imports
- Solar surplus
- Self-sufficiency
- Annual savings
- Investment payback period

The project uses Python, pandas, NumPy and matplotlib.

---

## Project overview

This project models a residential electricity system with:

- Hourly electricity consumption data
- Synthetic solar generation profiles
- Self-consumption without battery
- Battery storage simulation
- Economic analysis
- Grid search over solar power and battery capacity
- Visualization of payback and energy performance

The current version uses a synthetic 30-day consumption dataset and extrapolates the results to estimate annual savings.

---

## Main result

For the current synthetic 30-day dataset, the optimizer compares multiple combinations of solar peak power and battery capacity.

Example output:

```text
Best scenario by payback:
Solar peak power: 1.50 kW
Battery capacity: 0.00 kWh
Investment cost: 2150.00 EUR
Annual savings: 431.73 EUR/year
Payback: 4.98 years
Self-sufficiency: 48.83%

Best scenario by self-sufficiency:
Solar peak power: 1.50 kW
Battery capacity: 5.00 kWh
Investment cost: 4650.00 EUR
Annual savings: 563.25 EUR/year
Payback: 8.26 years
Self-sufficiency: 99.46%
```

The economic optimum and the energy optimum are different.

The photovoltaic-only configuration has a shorter payback period, while the battery configuration provides much higher self-sufficiency.

---

## Visual results

### Payback period by solar power and battery capacity

This plot shows how the payback period changes depending on the photovoltaic system size and battery capacity.

![Payback grid search](images/main_payback_grid_search.png)

### Self-sufficiency by solar power and battery capacity

This plot shows how increasing solar power and battery capacity affects the percentage of household electricity demand covered by the PV-battery system.

![Self-sufficiency grid search](images/main_self_sufficiency_grid_search.png)

### Best scenarios comparison

This plot highlights the trade-off between the most profitable configuration and the most energy-independent configuration.

![Best scenarios comparison](images/best_scenarios_comparison.png)

### Best scenario energy flows

This plot shows the hourly consumption, solar generation and grid imports for the best economic scenario.

![Best scenario timeseries](images/best_scenario_timeseries.png)

### Battery state of charge

This plot shows how the battery charges and discharges over the simulated period.

![Battery state](images/best_scenario_battery_state.png)

### Cumulative energy flows

This plot shows how total consumption, solar generation, grid imports and solar surplus evolve over the simulated period.

![Cumulative energy flows](images/best_scenario_cumulative_energy.png)

---

## Project structure

```text
electricity-consumption-solar-optimizer/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── simulated/
│
├── images/
│
├── reports/
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_solar_battery_simulation.ipynb
│   └── 03_optimization_analysis.ipynb
│
├── scripts/
│   └── generate_synthetic_consumption.py
│
├── archive/
│   └── practices/
│
├── src/
│   ├── battery.py
│   ├── config.py
│   ├── data_loader.py
│   ├── economics.py
│   ├── main.py
│   ├── optimization.py
│   ├── scenarios.py
│   ├── solar.py
│   ├── tariff.py
│   └── visualization.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Main modules

### `data_loader.py`

Loads electricity consumption data from CSV files and prepares useful time-based columns such as hour, day, month and weekday.

### `solar.py`

Generates simplified hourly solar production profiles and simulates direct solar self-consumption.

### `battery.py`

Simulates battery charging and discharging hour by hour, including:

- Battery capacity limits
- Charging efficiency
- Maximum charge power
- Maximum discharge power
- Battery state of charge

### `scenarios.py`

Compares energy scenarios with and without battery storage.

### `economics.py`

Calculates installation costs, electricity costs, savings and simple payback period.

### `optimization.py`

Runs an economic grid search over different solar panel sizes and battery capacities, selects the best scenarios and builds report outputs.

### `visualization.py`

Generates reusable plots for scenario comparison and time-series analysis.

### `config.py`

Stores input paths, output paths, simulation parameters, battery assumptions and economic assumptions.

### `main.py`

Main project entry point.

---

## Notebooks

The project includes exploratory and analytical notebooks:

```text
notebooks/01_exploratory_analysis.ipynb
notebooks/02_solar_battery_simulation.ipynb
notebooks/03_optimization_analysis.ipynb
```

The notebooks provide a more visual and narrative explanation of the project:

- `01_exploratory_analysis.ipynb`: explores the synthetic electricity consumption dataset.
- `02_solar_battery_simulation.ipynb`: analyzes solar generation and battery behavior.
- `03_optimization_analysis.ipynb`: studies the economic optimization results and the trade-off between payback and self-sufficiency.

---

## Installation

Clone the repository and create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## How to run

First, generate the synthetic 30-day consumption dataset:

```bash
python scripts/generate_synthetic_consumption.py
```

Then run the main optimizer:

```bash
python src/main.py
```

The program prints the best scenarios, generates output plots in the `images/` folder and saves report files in the `reports/` folder.

---

## Outputs

Running the main optimizer generates:

```text
images/main_payback_grid_search.png
images/main_self_sufficiency_grid_search.png
images/best_scenarios_comparison.png
images/best_scenario_timeseries.png
images/best_scenario_battery_state.png
images/best_scenario_cumulative_energy.png

reports/grid_search_results.csv
reports/best_scenarios.csv
reports/best_scenario_timeseries.csv
reports/summary.txt
reports/outputs_index.md
```

The CSV files contain the full optimization results, the selected optimal scenarios and the hourly energy flows for the best economic scenario.

The summary file contains the two best scenarios selected by economic payback and by energy self-sufficiency.

The `outputs_index.md` file describes all generated reports and plots.

The plots provide a visual summary of the economic, energetic and temporal behavior of the simulated PV-battery system.

---

## Input data format

Consumption data is expected as a CSV file with the following columns:

```csv
datetime,consumption_kwh
2025-01-01 00:00:00,0.20
2025-01-01 01:00:00,0.15
2025-01-01 02:00:00,0.10
```

The `datetime` column is parsed as a timestamp, and `consumption_kwh` represents the electricity consumed during each hour.

---

## Current assumptions

The current model is intentionally simplified. It assumes:

- Synthetic hourly household consumption
- Repeated daily solar generation pattern
- Constant electricity price
- Constant surplus compensation price
- No fixed electricity bill terms
- No taxes
- No panel degradation
- No battery degradation
- No maintenance costs
- Simple payback calculation

These assumptions make the model easy to understand and extend.

---

## Future improvements

Planned improvements include:

- Use real household electricity consumption data
- Use PVGIS solar generation data for a real location
- Add seasonal and weather variation
- Add Spanish electricity tariff structures
- Add battery degradation
- Add maintenance costs
- Add net present value analysis
- Add machine learning consumption forecasting
- Add configuration through external YAML files
- Add a command-line interface
- Build a Streamlit dashboard for interactive scenario exploration

---

## Technologies used

- Python
- pandas
- NumPy
- matplotlib
- scikit-learn
- Jupyter