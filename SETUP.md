# Setup guide

This guide explains how to set up the project from a fresh clone.

---

## 1. Clone the repository

```bash
git clone https://github.com/Jcsantoyo/electricity-consumption-solar-optimizer.git
cd electricity-consumption-solar-optimizer
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or using the Makefile:

```bash
make install
```

---

## 4. Prepare input data

The project expects the main raw consumption dataset at:

```text
data/raw/household_power_consumption.txt
```

This file comes from the UCI Individual Household Electric Power Consumption dataset.

After placing the raw file in `data/raw/`, run:

```bash
python scripts/prepare_uci_household_power.py
```

This generates:

```text
data/processed/uci_household_power_hourly.csv
```

The processed file is the main consumption input used by the historical optimization, forecasting and forecast-based optimization pipelines.

---

## 5. Add PVGIS solar data

The project expects PVGIS solar generation data at:

```text
data/raw/pvgis_hourly_linares_1kw_2020.csv
```

This file contains hourly solar generation for a 1 kW photovoltaic installation.

The path is configured in:

```text
src/config.py
```

The project scales this 1 kW PVGIS generation profile depending on the solar peak power tested by the optimizer.

---

## 6. Check the configuration

The main configurable parameters are defined in:

```text
src/config.py
```

This includes:

- Input data paths
- PVGIS usage
- Solar powers tested
- Battery capacities tested
- Battery model assumptions
- Economic assumptions
- Active electricity tariff profile

The current configuration can be summarized by running:

```bash
python scripts/generate_config_summary.py
```

This generates:

```text
reports/configuration_summary.md
```

---

## 7. Run tests

```bash
make test
```

or:

```bash
python -m pytest
```

---

## 8. Run lint checks

```bash
make lint
```

or:

```bash
ruff check .
```

---

## 9. Run the full pipeline

```bash
make pipeline
```

or:

```bash
python scripts/run_full_pipeline.py
```

The full pipeline runs:

1. Configuration summary generation
2. Historical solar and battery optimization
3. Machine Learning consumption forecasting
4. Forecast-based solar and battery optimization
5. Historical vs forecast-based comparison
6. Final results summary generation

The full pipeline generates reports in:

```text
reports/
```

and plots in:

```text
images/
```

---

## Main outputs

Recommended files to inspect first:

```text
reports/final_results_summary.md
reports/configuration_summary.md
reports/historical_vs_forecast_optimization.csv
reports/outputs_index.md
```

Recommended plots:

```text
images/historical_vs_forecast_payback.png
images/historical_vs_forecast_self_sufficiency.png
images/historical_vs_forecast_grid_import.png
```

---

## Notes

Large data files are ignored by Git and must be added locally.

The data folders are kept in the repository using `.gitkeep` files.

The main project execution should normally be done from the repository root folder.

Recommended command:

```bash
make pipeline
```