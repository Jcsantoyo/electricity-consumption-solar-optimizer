# Tests documentation

This folder contains the pytest test suite for the project.

Tests can be executed with:

```bash
make test
```

or:

```bash
python -m pytest
```

---

## Pytest configuration

Pytest is configured in:

```text
pyproject.toml
```

The configuration defines:

```toml
[tool.pytest.ini_options]
testpaths = [
    "tests"
]

pythonpath = [
    ".",
    "src"
]

addopts = "-ra"
```

This allows tests to import modules from both the project root and the `src/` folder.

---

## Test files

### `test_battery.py`

Tests battery simulation behavior.

It checks that the battery model handles charging, discharging, grid import and solar surplus correctly.

### `test_economics.py`

Tests economic calculations such as:

- Solar installation cost
- Battery installation cost
- Total installation cost
- Grid cost
- Net cost
- Payback period

### `test_solar_data_loader.py`

Tests PVGIS solar data loading and generation matching.

### `test_tariff.py`

Tests the configurable electricity tariff model.

It checks:

- Spanish 2.0TD-style tariff period classification
- Variable grid cost calculation
- Surplus compensation
- Fixed power cost
- Net electricity cost

### `test_forecasting.py`

Tests forecasting utilities.

It checks:

- Time feature creation
- Lag feature creation
- Dataset preparation
- Time-based train/test split
- Forecast evaluation
- Feature importance extraction
- Forecasted consumption DataFrame generation

### `test_compare_optimization_results.py`

Tests historical vs forecast-based comparison logic.

It checks:

- Scenario loading
- Criterion normalization
- Comparison DataFrame creation
- Clean comparison plot labels

### `test_generate_config_summary.py`

Tests configuration summary generation.

It checks that the generated summary includes:

- Main sections
- Current configuration values
- Active tariff values

### `test_generate_final_results_summary.py`

Tests final results summary generation.

It checks:

- Formatting helpers
- Scenario selection
- Missing scenario errors
- Main report sections
- Key result values

### `test_run_full_pipeline.py`

Smoke tests for the full pipeline script.

It checks that the expected pipeline steps are present and in the correct order.

### `test_makefile.py`

Smoke tests for the Makefile.

It checks that common project commands exist and point to the expected scripts.

---

## Running tests locally

Run:

```bash
make test
```

or:

```bash
python -m pytest
```

---

## Running tests in GitHub Actions

The test suite is automatically executed by GitHub Actions on pushes and pull requests.

The workflow also runs Ruff lint checks.
