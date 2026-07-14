import pytest

from scenario_registry import (
    DEFAULT_PROJECT_SCENARIO_NAME,
    get_project_scenario,
)


def test_default_project_scenario_can_be_loaded() -> None:
    scenario = get_project_scenario()

    assert (
        scenario.name
        == DEFAULT_PROJECT_SCENARIO_NAME
    )


def test_omie_project_scenario_uses_hourly_prices() -> None:
    scenario = get_project_scenario(
        "uci_omie_june_2026"
    )

    assert scenario.uses_hourly_prices is True
    assert scenario.forecast_mode == "backtest"
    assert scenario.random_seed == 42


def test_fixed_project_scenario_has_no_hourly_file() -> None:
    scenario = get_project_scenario(
        "uci_fixed_tariff"
    )

    assert scenario.uses_hourly_prices is False
    assert scenario.hourly_price_data_path is None
    assert (
        scenario.tariff_profile_name
        == "flat_price"
    )


def test_unknown_project_scenario_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="Unknown project scenario",
    ):
        get_project_scenario(
            "does_not_exist"
        )