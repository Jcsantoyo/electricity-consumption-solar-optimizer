import pandas as pd

from tariff import (
    get_spanish_2_0td_period,
    add_tariff_period_column,
    calculate_variable_grid_cost_with_tariff,
    calculate_surplus_compensation,
    calculate_fixed_power_cost,
    calculate_net_electricity_cost_with_tariff
)


def test_weekday_off_peak_period():
    timestamp = pd.Timestamp("2024-01-02 03:00:00")
    assert get_spanish_2_0td_period(timestamp) == "off_peak"


def test_weekday_flat_period():
    timestamp = pd.Timestamp("2024-01-02 09:00:00")
    assert get_spanish_2_0td_period(timestamp) == "flat"


def test_weekday_peak_period():
    timestamp = pd.Timestamp("2024-01-02 11:00:00")
    assert get_spanish_2_0td_period(timestamp) == "peak"


def test_weekend_is_off_peak():
    timestamp = pd.Timestamp("2024-01-06 12:00:00")
    assert get_spanish_2_0td_period(timestamp) == "off_peak"


def test_add_tariff_period_column():
    df = pd.DataFrame({
        "datetime": [
            pd.Timestamp("2024-01-02 03:00:00"),
            pd.Timestamp("2024-01-02 11:00:00")
        ]
    })

    result_df = add_tariff_period_column(df)

    assert "tariff_period" in result_df.columns
    assert result_df.loc[0, "tariff_period"] == "off_peak"
    assert result_df.loc[1, "tariff_period"] == "peak"


def test_variable_grid_cost_with_tariff():
    df = pd.DataFrame({
        "datetime": [
            pd.Timestamp("2024-01-02 03:00:00"),
            pd.Timestamp("2024-01-02 11:00:00")
        ],
        "grid_import_kwh": [10.0, 10.0]
    })

    cost = calculate_variable_grid_cost_with_tariff(
        df,
        grid_import_column="grid_import_kwh",
        peak_price=0.25,
        flat_price=0.18,
        off_peak_price=0.12
    )

    assert cost == 3.7


def test_surplus_compensation():
    df = pd.DataFrame({
        "solar_surplus_kwh": [10.0, 5.0]
    })

    compensation = calculate_surplus_compensation(
        df,
        surplus_column="solar_surplus_kwh",
        surplus_compensation_price=0.07
    )

    assert compensation == 1.05


def test_fixed_power_cost():
    cost = calculate_fixed_power_cost(
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
        simulation_days=365
    )

    assert cost == 161.0


def test_net_electricity_cost_with_tariff():
    df = pd.DataFrame({
        "datetime": [
            pd.Timestamp("2024-01-02 03:00:00"),
            pd.Timestamp("2024-01-02 11:00:00")
        ],
        "grid_import_kwh": [10.0, 10.0],
        "solar_surplus_kwh": [2.0, 2.0]
    })

    net_cost = calculate_net_electricity_cost_with_tariff(
        df,
        grid_import_column="grid_import_kwh",
        surplus_column="solar_surplus_kwh",
        peak_price=0.25,
        flat_price=0.18,
        off_peak_price=0.12,
        surplus_compensation_price=0.07,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
        simulation_days=365
    )

    expected = 3.7 + 161.0 - 0.28

    assert net_cost == expected