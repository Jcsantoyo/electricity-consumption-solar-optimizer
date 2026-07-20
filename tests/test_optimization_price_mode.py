import pandas as pd
import pytest

from electricity_price_models import (
    FixedPriceModel,
    HourlyPriceModel,
    TimeOfUsePriceModel,
    ElectricityPriceModel,
)
from optimization import (
    run_economic_grid_search,
)


def build_consumption_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 02:00:00",
                    "2026-06-01 11:00:00",
                    "2026-06-01 15:00:00",
                ]
            ),
            "consumption_kwh": [
                1.0,
                2.0,
                3.0,
            ],
        }
    )


def run_test_grid_search(
    price_model: ElectricityPriceModel,
) -> pd.DataFrame:
    return run_economic_grid_search(
        consumption_df=(build_consumption_dataframe()),
        solar_peak_powers_kw=[
            0.0,
        ],
        battery_capacities_kwh=[
            0.0,
        ],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=0.0,
        solar_cost_per_kw=0.0,
        battery_cost_per_kwh=0.0,
        price_model=price_model,
        simulation_days=1,
        pvgis_df=None,
    )


def test_grid_search_uses_fixed_price_model() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    assert len(results_df) == 1

    expected_cost = 6.0 * 0.20

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_cost)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_cost)


def test_grid_search_uses_time_of_use_model() -> None:
    price_model = TimeOfUsePriceModel(
        peak_price_eur_per_kwh=0.25,
        flat_price_eur_per_kwh=0.18,
        off_peak_price_eur_per_kwh=0.12,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_cost = 1.0 * 0.12 + 2.0 * 0.25 + 3.0 * 0.18

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_cost)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_cost)


def test_grid_search_uses_hourly_price_model() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 02:00:00",
                    "2026-06-01 11:00:00",
                    "2026-06-01 15:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.10,
                0.20,
                0.15,
            ],
        }
    )

    price_model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_cost = 1.0 * 0.10 + 2.0 * 0.20 + 3.0 * 0.15

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_cost)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_cost)


def test_grid_search_allows_negative_hourly_prices() -> None:
    consumption_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 14:00:00",
                ]
            ),
            "consumption_kwh": [
                1.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 14:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                -0.01,
            ],
        }
    )

    price_model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
        allow_negative_prices=True,
    )

    results_df = run_economic_grid_search(
        consumption_df=consumption_df,
        solar_peak_powers_kw=[
            0.0,
        ],
        battery_capacities_kwh=[
            0.0,
        ],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=800.0,
        solar_cost_per_kw=900.0,
        battery_cost_per_kwh=500.0,
        price_model=price_model,
        simulation_days=1,
        pvgis_df=None,
    )

    assert len(results_df) == 1

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(0.0)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(0.0)


def test_grid_search_stores_fixed_price_cost_breakdown() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.05,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_variable_cost = 6.0 * 0.20
    expected_fixed_power_cost = 4.6 * 35.0 / 365

    assert results_df.loc[
        0,
        "base_variable_energy_cost_eur",
    ] == pytest.approx(expected_variable_cost)

    assert results_df.loc[
        0,
        "base_fixed_power_cost_eur",
    ] == pytest.approx(expected_fixed_power_cost)

    assert results_df.loc[
        0,
        "base_surplus_compensation_eur",
    ] == pytest.approx(0.0)

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_variable_cost + expected_fixed_power_cost)

    assert results_df.loc[
        0,
        "scenario_variable_energy_cost_eur",
    ] == pytest.approx(expected_variable_cost)

    assert results_df.loc[
        0,
        "scenario_fixed_power_cost_eur",
    ] == pytest.approx(expected_fixed_power_cost)

    assert results_df.loc[
        0,
        "scenario_surplus_compensation_eur",
    ] == pytest.approx(0.0)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_variable_cost + expected_fixed_power_cost)


def test_grid_search_includes_cost_breakdown_columns() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_columns = {
        "base_variable_energy_cost_eur",
        "base_fixed_power_cost_eur",
        "base_surplus_compensation_eur",
        "base_net_cost_eur",
        "scenario_variable_energy_cost_eur",
        "scenario_fixed_power_cost_eur",
        "scenario_surplus_compensation_eur",
        "scenario_net_cost_eur",
    }

    assert expected_columns.issubset(results_df.columns)
