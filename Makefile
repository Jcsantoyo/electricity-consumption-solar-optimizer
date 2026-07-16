SCENARIO ?= uci_omie_june_2026

.PHONY: install test lint format validate-scenario pipeline optimize forecast forecast-optimize compare price-mode-comparison config-summary final-summary run-manifest clean-reports

install:
	pip install -r requirements.txt

test:
	python -m pytest

lint:
	ruff check .

format:
	ruff format .

validate-scenario:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/validate_scenario.py

pipeline:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/run_full_pipeline.py

optimize:
	PROJECT_SCENARIO=$(SCENARIO) python src/main.py

forecast:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/run_forecasting.py

forecast-optimize:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/run_forecast_optimization.py

compare:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/compare_optimization_results.py

price-mode-comparison:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/generate_price_mode_comparison.py

config-summary:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/generate_config_summary.py

final-summary:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/generate_final_results_summary.py

run-manifest:
	PROJECT_SCENARIO=$(SCENARIO) python scripts/generate_run_manifest.py

clean-reports:
	rm -f reports/*.csv reports/*.txt reports/*.md reports/*.json
	rm -f images/*.png