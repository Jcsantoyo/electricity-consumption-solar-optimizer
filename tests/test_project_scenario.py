from dataclasses import replace

import pytest

from project_scenario import ProjectScenario


def build_valid_project_scenario() -> ProjectScenario:
    return ProjectScenario(
        name="test_scenario",
        consumption_data_path=("data/processed/consumption.csv"),
        use_pvgis_solar_data=True,
        pvgis_solar_data_path=("data/raw/solar.csv"),
        price_mode="wholesale_hourly",
        tariff_profile_name="test_tariff",
        hourly_price_data_path=("data/processed/prices.csv"),
        allow_negative_hourly_prices=True,
        forecast_mode="backtest",
        forecast_test_size_ratio=0.20,
        random_seed=42,
    )


def test_valid_project_scenario() -> None:
    scenario = build_valid_project_scenario()

    scenario.validate()


def test_project_scenario_detects_hourly_prices() -> None:
    scenario = build_valid_project_scenario()

    assert scenario.uses_hourly_prices is True


def test_project_scenario_rejects_invalid_price_mode() -> None:
    scenario = replace(
        build_valid_project_scenario(),
        price_mode="unknown",
    )

    with pytest.raises(
        ValueError,
        match="Invalid price mode",
    ):
        scenario.validate()


def test_project_scenario_rejects_invalid_forecast_mode() -> None:
    scenario = replace(
        build_valid_project_scenario(),
        forecast_mode="unknown",
    )

    with pytest.raises(
        ValueError,
        match="Invalid forecast mode",
    ):
        scenario.validate()


def test_project_scenario_rejects_invalid_test_ratio() -> None:
    scenario = replace(
        build_valid_project_scenario(),
        forecast_test_size_ratio=1.0,
    )

    with pytest.raises(
        ValueError,
        match="test size ratio",
    ):
        scenario.validate()


def test_hourly_mode_requires_price_path() -> None:
    scenario = replace(
        build_valid_project_scenario(),
        hourly_price_data_path=None,
    )

    with pytest.raises(
        ValueError,
        match="requires an hourly price data path",
    ):
        scenario.validate()


def test_fixed_mode_rejects_hourly_price_path() -> None:
    scenario = replace(
        build_valid_project_scenario(),
        price_mode="fixed",
    )

    with pytest.raises(
        ValueError,
        match="must be None",
    ):
        scenario.validate()
