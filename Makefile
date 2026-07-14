.PHONY: install test lint format pipeline optimize forecast forecast-optimize compare price-mode-comparison config-summary final-summary clean-reports

install:
	pip install -r requirements.txt

test:
	python -m pytest

lint:
	ruff check .

format:
	ruff format .

pipeline:
	python scripts/run_full_pipeline.py

optimize:
	python src/main.py

forecast:
	python scripts/run_forecasting.py

forecast-optimize:
	python scripts/run_forecast_optimization.py

compare:
	python scripts/compare_optimization_results.py

price-mode-comparison:
	python scripts/generate_price_mode_comparison.py

config-summary:
	python scripts/generate_config_summary.py

final-summary:
	python scripts/generate_final_results_summary.py

clean-reports:
	rm -f reports/*.csv reports/*.txt reports/*.md
	rm -f images/*.png