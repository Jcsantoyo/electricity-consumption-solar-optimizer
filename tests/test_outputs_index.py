from optimization import build_outputs_index_text


def test_outputs_index_includes_main_historical_outputs() -> None:
    text = build_outputs_index_text(
        solar_data_source="PVGIS",
        electricity_price_mode="Fixed tariff",
    )

    assert "grid_search_results.csv" in text
    assert "best_scenarios.csv" in text
    assert "best_scenario_timeseries.csv" in text


def test_outputs_index_documents_financial_sensitivity_results() -> None:
    text = build_outputs_index_text(
        solar_data_source="PVGIS",
        electricity_price_mode="Fixed tariff",
    )

    assert "financial_sensitivity_results.csv" in text
    assert "pessimistic, base and optimistic" in text
    assert "maximum net present value" in text


def test_outputs_index_includes_run_context() -> None:
    text = build_outputs_index_text(
        solar_data_source="PVGIS",
        electricity_price_mode="Fixed tariff",
    )

    assert "Solar data source: PVGIS" in text
    assert "Electricity price mode: Fixed tariff" in text
