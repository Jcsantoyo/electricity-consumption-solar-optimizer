# Scripts documentation

This folder contains executable scripts used to prepare data, run the pipeline and generate reports.

Most scripts can be executed directly from the project root.

---

## Recommended command

The full pipeline can be executed with:

```bash
make pipeline
```

or:

```bash
python scripts/run_full_pipeline.py
```

This is the recommended way to regenerate all main outputs.

---

## Full pipeline

### `run_full_pipeline.py`

Runs the complete project pipeline in order.

It executes:

1. Configuration summary generation
2. Historical solar and battery optimization
3. Machine Learning consumption forecasting
4. Forecast-based solar and battery optimization
5. Historical vs forecast-based comparison
6. Final results summary generation

This script stops if any step fails.

---

## Data preparation scripts

### `prepare_uci_household_power.py`

Converts the original UCI household power consumption dataset from minute-level data into hourly electricity consumption.

Input:

```text
data/raw/household_power_consumption.txt
```

Output:

```text
data/processed/uci_household_power_hourly.csv
```

### `generate_synthetic_consumption.py`

Generates a synthetic electricity consumption dataset.

This was useful during early development and for quick experiments.

Output:

```text
data/simulated/synthetic_consumption_30_days.csv
```

### `download_pvgis_data.py`

Script related to obtaining PVGIS solar generation data.

The main pipeline currently uses the configured PVGIS file:

```text
data/raw/pvgis_hourly_linares_1kw_2020.csv
```

---

## Forecasting scripts

### `run_forecasting.py`

Runs the Machine Learning forecasting pipeline.

It generates:

```text
reports/forecast_results.csv
reports/forecast_feature_importance.csv
reports/forecast_model_comparison.csv
images/consumption_forecast_actual_vs_predicted.png
images/forecast_feature_importance.png
images/forecast_model_comparison.png
```

### `run_forecast_optimization.py`

Uses forecasted consumption as input for the solar and battery optimization pipeline.

It generates:

```text
reports/forecasted_consumption_for_optimization.csv
reports/forecast_optimization_results.csv
reports/forecast_optimization_best_scenarios.csv
```

---

## Comparison and summary scripts

### `compare_optimization_results.py`

Compares historical optimization results with forecast-based optimization results.

It generates:

```text
reports/historical_vs_forecast_optimization.csv
images/historical_vs_forecast_payback.png
images/historical_vs_forecast_savings.png
images/historical_vs_forecast_self_sufficiency.png
images/historical_vs_forecast_investment_cost.png
images/historical_vs_forecast_grid_import.png
```

### `generate_config_summary.py`

Generates:

```text
reports/configuration_summary.md
```

This report records the configuration used by the project pipeline.

### `generate_final_results_summary.py`

Generates:

```text
reports/final_results_summary.md
```

This report summarizes the final historical and forecast-based optimization results.

---

## PVGIS validation scripts

### `test_pvgis_generation_match.py`

Manual script used to inspect and validate PVGIS generation matching.

### `test_pvgis_loader.py`

Manual script used to inspect PVGIS loading behavior.

These are development/inspection scripts, not the main pytest test suite.

---

## Notes

Run scripts from the project root so relative paths work correctly.

Recommended:

```bash
python scripts/run_full_pipeline.py
```

or:

```bash
make pipeline
```
