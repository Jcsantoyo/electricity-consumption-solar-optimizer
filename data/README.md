# Data documentation

This folder contains the input and processed data used by the project.

---

## Folder structure

```text
data/
├── raw/
├── processed/
└── simulated/
```

---

## `data/raw/`

This folder contains external raw input files.

### `household_power_consumption.txt`

Original UCI Individual Household Electric Power Consumption dataset.

This file contains minute-level household electricity measurements.

It is used as the main real-world consumption dataset before preprocessing.

The project converts this minute-level dataset into hourly electricity consumption before using it in the optimization and forecasting pipelines.

### `pvgis_hourly_linares_1kw_2020.csv`

PVGIS hourly solar generation data for Linares, Spain.

The file represents hourly photovoltaic generation for a 1 kW solar installation.

The project scales this generation depending on the solar peak power tested by the optimizer.

For example:

```text
1 kW PVGIS generation × 3.0 = 3 kW solar installation
```

---

## `data/processed/`

This folder contains cleaned and processed datasets generated from raw data.

### `uci_household_power_hourly.csv`

Hourly electricity consumption dataset generated from the original UCI minute-level dataset.

It is created by running:

```bash
python scripts/prepare_uci_household_power.py
```

Expected format:

```csv
datetime,consumption_kwh
2006-12-16 17:00:00,2.533733
2006-12-16 18:00:00,3.632200
```

This is the main consumption input used by the historical optimization, forecasting and forecast-based optimization pipelines.

---

## `data/simulated/`

This folder contains synthetic datasets generated for testing and early development.

### `synthetic_consumption_30_days.csv`

Synthetic hourly electricity consumption dataset.

It can be regenerated with:

```bash
python scripts/generate_synthetic_consumption.py
```

This dataset is useful for quick experiments and development, but the main project pipeline currently uses the processed UCI household dataset.

---

## Main data flow

```text
data/raw/household_power_consumption.txt
        ↓
scripts/prepare_uci_household_power.py
        ↓
data/processed/uci_household_power_hourly.csv
        ↓
historical optimization
forecasting
forecast-based optimization
```

Solar generation data follows this flow:

```text
data/raw/pvgis_hourly_linares_1kw_2020.csv
        ↓
PVGIS timestamp parsing and scaling
        ↓
solar generation input for each tested solar size
```

---

## Notes

Large raw datasets may be excluded from version control depending on repository size.

Processed files can be regenerated from the raw input data using the scripts in the `scripts/` folder.

The main pipeline currently uses:

```text
data/processed/uci_household_power_hourly.csv
data/raw/pvgis_hourly_linares_1kw_2020.csv
```

These paths are configured in:

```text
src/config.py
```