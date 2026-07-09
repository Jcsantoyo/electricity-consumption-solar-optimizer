# Roadmap

This file describes possible future improvements for the project.

The project already includes a complete end-to-end pipeline for historical solar and battery optimization, Machine Learning forecasting, forecast-based optimization, reports, plots, tests and continuous integration.

Future work could improve realism, usability and deployment.

---

## 1. Electricity price improvements

### Hourly electricity price CSV support

Add support for importing hourly electricity prices from a CSV file.

This would allow the optimization to use real or custom electricity prices instead of fixed tariff assumptions.

Possible input format:

```csv
datetime,price_eur_per_kwh
2024-01-01 00:00:00,0.12
2024-01-01 01:00:00,0.10
```

### PVPC or ESIOS integration

Add an optional downloader for Spanish PVPC hourly electricity prices.

This would make the economic model more realistic for Spanish users.

---

## 2. Forecasting improvements

### Weather-based forecasting

Include weather variables such as:

- Temperature
- Solar radiation
- Cloud cover
- Humidity

This could improve consumption forecasting and solar generation analysis.

### More forecasting models

Add and compare additional forecasting models, such as:

- Gradient Boosting
- XGBoost
- LightGBM
- SARIMA
- Prophet
- Neural networks

### Recursive multi-step forecasting

Improve the forecast-based optimization pipeline by implementing recursive or direct multi-step forecasting.

This would make future consumption forecasting more realistic.

---

## 3. Configuration improvements

### YAML configuration file

Move project parameters from `src/config.py` to an external YAML file.

This would make the project easier to configure without editing Python code.

Possible file:

```text
config.yaml
```

### Command-line interface

Add a CLI so users can run specific project stages with arguments.

Example:

```bash
python -m solar_optimizer --run pipeline
python -m solar_optimizer --solar 3.0 --battery 5.0
```

---

## 4. Dashboard and visualization

### Streamlit dashboard

Create an interactive dashboard to explore:

- Consumption data
- Solar generation
- Battery behavior
- Payback results
- Self-sufficiency results
- Forecasting results
- Historical vs forecast-based comparison

Possible command:

```bash
streamlit run app.py
```

---

## 5. Real household adaptation

### Smart meter data

Adapt the project to work with real household smart meter exports.

Possible data sources:

- Electricity distributor CSV exports
- Datadis
- Smart meter data
- Home Assistant energy data

### Household-specific analysis

Allow users to analyze their own consumption profile and compare it against the public UCI dataset.

---

## 6. Testing and quality improvements

### Stricter Ruff rules

The project currently uses basic Ruff checks.

Future work could enable more checks gradually:

- Import sorting
- Style checks
- Bugbear warnings
- Line length cleanup

### More integration tests

Add tests for:

- Full report generation
- Plot generation
- Pipeline failure handling
- Configuration edge cases

---

## 7. Packaging

### Python package structure

Convert the project into an installable Python package.

Possible command:

```bash
pip install -e .
```

### Versioning

Add simple versioning for project milestones.

---

## Priority order

A possible next development order:

1. YAML configuration file
2. Hourly electricity price CSV support
3. Streamlit dashboard
4. Weather-based forecasting
5. Real household data adaptation
6. Stricter code quality rules