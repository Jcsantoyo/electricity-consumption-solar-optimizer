import pandas as pd
import pytest

from optimization import(
    calculate_net_electricity_cost_for_price_mode,
    run_economic_grid_search
) 




def build_energy_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2025-01-06 01:00:00",
                    "2025-01-06 11:00:00",
                    "2025-01-06 15:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
                2.0,
                3.0,
            ],
            "solar_surplus_kwh": [
                0.0,
                0.0,
                0.0,
            ],
        }
    )


def build_hourly_price_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2025-01-06 01:00:00",
                    "2025-01-06 11:00:00",
                    "2025-01-06 15:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.10,
                0.20,
                0.15,
            ],
        }
    )


def test_price_mode_uses_tariff_when_hourly_prices_are_none() -> None:
    energy_df = build_energy_dataframe()

    net_cost = calculate_net_electricity_cost_for_price_mode(
        df=energy_df,
        grid_import_column="grid_import_kwh",
        surplus_column="solar_surplus_kwh",
        peak_price=0.25,
        flat_price=0.18,
        off_peak_price=0.12,
        surplus_compensation_price=0.07,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
        simulation_days=1,
        hourly_price_df=None,
    )

    assert net_cost == pytest.approx(1.16)


def test_price_mode_uses_hourly_prices_when_dataframe_is_provided() -> None:
    energy_df = build_energy_dataframe()
    hourly_price_df = build_hourly_price_dataframe()

    net_cost = calculate_net_electricity_cost_for_price_mode(
        df=energy_df,
        grid_import_column="grid_import_kwh",
        surplus_column="solar_surplus_kwh",
        peak_price=0.25,
        flat_price=0.18,
        off_peak_price=0.12,
        surplus_compensation_price=0.07,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
        simulation_days=1,
        hourly_price_df=hourly_price_df,
    )

    assert net_cost == pytest.approx(0.95)


def test_hourly_price_mode_keeps_fixed_cost_and_surplus_compensation() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2025-01-06 12:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
            ],
            "solar_surplus_kwh": [
                0.5,
            ],
        }
    )

    hourly_price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2025-01-06 12:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.20,
            ],
        }
    )

    net_cost = calculate_net_electricity_cost_for_price_mode(
        df=energy_df,
        grid_import_column="grid_import_kwh",
        surplus_column="solar_surplus_kwh",
        peak_price=0.25,
        flat_price=0.18,
        off_peak_price=0.12,
        surplus_compensation_price=0.07,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
        simulation_days=1,
        hourly_price_df=hourly_price_df,
    )

    expected_variable_cost = 1.0 * 0.20
    expected_fixed_cost = 4.6 * 35.0 / 365
    expected_surplus_compensation = 0.5 * 0.07

    expected_net_cost = (
        expected_variable_cost
        + expected_fixed_cost
        - expected_surplus_compensation
    )

    assert net_cost == pytest.approx(expected_net_cost)

def test_grid_search_allows_negative_hourly_prices() -> None:
    consumption_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                ["2026-06-01 14:00:00"]
            ),
            "consumption_kwh": [1.0],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                ["2026-06-01 14:00:00"]
            ),
            "price_eur_per_kwh": [-0.01],
        }
    )

    results_df = run_economic_grid_search(
        consumption_df=consumption_df,
        solar_peak_powers_kw=[0.0],
        battery_capacities_kwh=[0.0],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=800.0,
        solar_cost_per_kw=900.0,
        battery_cost_per_kwh=500.0,
        peak_price=0.25,
        flat_price=0.18,
        off_peak_price=0.12,
        surplus_compensation_price=0.07,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
        simulation_days=1,
        pvgis_df=None,
        hourly_price_df=price_df,
        allow_negative_hourly_prices=True,
    )

    assert len(results_df) == 1