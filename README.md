# Electricity Consumption Solar Optimizer

A data science project for analyzing household electricity consumption,
simulating solar self-consumption, modeling battery storage, and
comparing economic and energy optimization scenarios.

The goal of this project is to estimate how different photovoltaic and
battery configurations affect:

-   Grid electricity imports
-   Solar surplus
-   Self-sufficiency
-   Annual savings
-   Investment payback period

The project uses Python, pandas, NumPy and matplotlib.

------------------------------------------------------------------------

## Project overview

This project models a residential electricity system with:

-   Hourly electricity consumption data
-   Synthetic solar generation profiles
-   Self-consumption without battery
-   Battery storage simulation
-   Economic analysis
-   Grid search over solar power and battery capacity
-   Visualization of payback and energy performance

The current version uses a synthetic 30-day consumption dataset and
extrapolates the results to estimate annual savings.

------------------------------------------------------------------------

## Main result

For the current synthetic 30-day dataset, the optimizer compares
multiple combinations of solar peak power and battery capacity.

Example output:

``` text
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

The photovoltaic-only configuration has a shorter payback period, while
the battery configuration provides much higher self-sufficiency.

------------------------------------------------------------------------

## Project structure

``` text
electricity-consumption-solar-optimizer/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── simulated/
│
├── images/
├── reports/
├── notebooks/
├── scripts/
│   └── generate_synthetic_consumption.py
│
├── archive/
│   └── practices/
│
├── src/
│   ├── battery.py
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

------------------------------------------------------------------------

## Main modules

### `data_loader.py`

Loads electricity consumption data from CSV files and prepares useful
time-based columns such as hour, day, month and weekday.

### `solar.py`

Generates simplified hourly solar production profiles and simulates
direct solar self-consumption.

### `battery.py`

Simulates battery charging and discharging hour by hour, including
battery capacity limits, charging efficiency, maximum charge/discharge
power and battery state of charge.

### `scenarios.py`

Compares energy scenarios with and without battery storage.

### `economics.py`

Calculates installation costs, electricity costs, savings and simple
payback period.

### `optimization.py`

Runs an economic grid search over different solar panel sizes and
battery capacities.

### `visualization.py`

Generates reusable plots for scenario comparison.

### `main.py`

Main project entry point.

------------------------------------------------------------------------

## Installation

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

------------------------------------------------------------------------

## How to run

``` bash
python scripts/generate_synthetic_consumption.py
python src/main.py
```

------------------------------------------------------------------------

## Input data format

``` csv
datetime,consumption_kwh
2025-01-01 00:00:00,0.20
2025-01-01 01:00:00,0.15
2025-01-01 02:00:00,0.10
```

------------------------------------------------------------------------

## Current assumptions

-   Synthetic hourly household consumption
-   Repeated daily solar generation pattern
-   Constant electricity price
-   Constant surplus compensation price
-   No fixed electricity bill terms
-   No taxes
-   No panel degradation
-   No battery degradation
-   No maintenance costs
-   Simple payback calculation

------------------------------------------------------------------------

## Future improvements

-   Use real household electricity consumption data
-   Use PVGIS solar generation data
-   Add seasonal and weather variation
-   Add Spanish electricity tariff structures
-   Add battery degradation
-   Add maintenance costs
-   Add net present value analysis
-   Add machine learning consumption forecasting
-   Build Jupyter notebooks for exploration and reporting

------------------------------------------------------------------------

## Technologies used

-   Python
-   pandas
-   NumPy
-   matplotlib
-   scikit-learn
-   Jupyter
