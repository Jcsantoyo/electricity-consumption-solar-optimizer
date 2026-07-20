from pathlib import Path


def test_main_passes_hourly_prices_to_grid_search() -> None:
    main_text = Path("src/main.py").read_text(encoding="utf-8")

    assert "load_hourly_prices_if_enabled" in main_text
    assert "hourly_price_df=hourly_price_df" in main_text


def test_forecast_optimization_passes_hourly_prices_to_grid_search() -> None:
    script_text = Path("scripts/run_forecast_optimization.py").read_text(
        encoding="utf-8"
    )

    assert "load_hourly_prices_if_enabled" in script_text
    assert "hourly_price_df=hourly_price_df" in script_text
