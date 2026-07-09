# Notebooks documentation

This folder contains Jupyter notebooks used for exploration and analysis.

The notebooks are not required to run the main pipeline, but they are useful for understanding the project step by step.

The main reproducible pipeline is executed from scripts:

```bash
make pipeline
```

or:

```bash
python scripts/run_full_pipeline.py
```

---

## Notebook files

### `01_exploratory_analysis.ipynb`

Initial exploratory analysis of electricity consumption data.

Useful for inspecting:

- Consumption patterns
- Hourly behavior
- Daily behavior
- Basic statistics

### `02_solar_battery_simulation.ipynb`

Exploration of solar generation and battery simulation.

Useful for understanding:

- Solar self-consumption
- Grid import
- Solar surplus
- Battery charging and discharging

### `03_optimization_analysis.ipynb`

Exploration of optimization results.

Useful for analyzing:

- Grid search results
- Payback period
- Self-sufficiency
- Best economic scenario
- Best energy scenario

### `04_consumption_forecasting.ipynb`

Exploration of the Machine Learning forecasting workflow.

Useful for understanding:

- Time-based features
- Lag features
- Model training
- Forecast evaluation
- Feature importance
- Forecasting model comparison

---

## Notes

Notebooks are mainly used for learning, exploration and explanation.

For reproducible execution, use the scripts and Makefile commands instead of relying on notebook state.

Recommended full execution:

```bash
make pipeline
```
