import pandas as pd
import pytest

from electricity_price_models import (
    ElectricityPriceModel,
    FixedPriceModel,
    TimeOfUsePriceModel,
    HourlyPriceModel
)


def build_energy_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2026-06-01 00:00:00",
                periods=2,
                freq="h",
            ),
            "grid_import_kwh": [
                1.0,
                2.0,
            ],
            "solar_surplus_kwh": [
                0.0,
                0.0,
            ],
        }
    )


def test_fixed_price_model_calculates_import_cost() -> None:
    energy_df = build_energy_dataframe()

    model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.07,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    result = model.calculate_net_cost(
        energy_df=energy_df,
        grid_import_column=(
            "grid_import_kwh"
        ),
        surplus_column=(
            "solar_surplus_kwh"
        ),
        simulation_days=1,
    )

    assert result == pytest.approx(
        0.60
    )


def test_fixed_price_model_compensates_surplus() -> None:
    energy_df = build_energy_dataframe()

    energy_df[
        "solar_surplus_kwh"
    ] = [
        1.0,
        1.0,
    ]

    model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.05,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    result = model.calculate_net_cost(
        energy_df=energy_df,
        grid_import_column=(
            "grid_import_kwh"
        ),
        surplus_column=(
            "solar_surplus_kwh"
        ),
        simulation_days=1,
    )

    expected_import_cost = (
        3.0 * 0.20
    )

    expected_surplus_income = (
        2.0 * 0.05
    )

    expected_net_cost = (
        expected_import_cost
        - expected_surplus_income
    )

    assert result == pytest.approx(
        expected_net_cost
    )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "expected_message",
    ),
    [
        (
            "fixed_price_eur_per_kwh",
            -0.01,
            (
                "Fixed electricity price "
                "cannot be negative"
            ),
        ),
        (
            "surplus_compensation_price",
            -0.01,
            (
                "Surplus compensation price "
                "cannot be negative"
            ),
        ),
        (
            "contracted_power_kw",
            -1.0,
            (
                "Contracted power "
                "cannot be negative"
            ),
        ),
        (
            "power_price_eur_per_kw_year",
            -1.0,
            (
                "Annual power price "
                "cannot be negative"
            ),
        ),
    ],
)
def test_fixed_price_model_rejects_negative_parameters(
    field_name: str,
    invalid_value: float,
    expected_message: str,
) -> None:
    parameters = {
        "fixed_price_eur_per_kwh": 0.20,
        "surplus_compensation_price": 0.05,
        "contracted_power_kw": 4.6,
        "power_price_eur_per_kw_year": 35.0,
    }

    parameters[field_name] = invalid_value

    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        FixedPriceModel(
            **parameters
        )


def test_fixed_price_model_rejects_invalid_simulation_days() -> None:
    model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.05,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Simulation days must be "
            "greater than zero"
        ),
    ):
        model.calculate_net_cost(
            energy_df=(
                build_energy_dataframe()
            ),
            grid_import_column=(
                "grid_import_kwh"
            ),
            surplus_column=(
                "solar_surplus_kwh"
            ),
            simulation_days=0,
        )


def accepts_electricity_price_model(
    model: ElectricityPriceModel,
) -> ElectricityPriceModel:
    return model


def test_fixed_price_model_matches_protocol() -> None:
    model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.05,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    accepted_model = (
        accepts_electricity_price_model(
            model
        )
    )

    assert accepted_model is model

def test_time_of_use_price_model_calculates_net_cost() -> None:
    energy_df = pd.DataFrame(
    {
        "datetime": pd.to_datetime(
            [
                "2026-06-01 11:00:00",
                "2026-06-01 15:00:00",
                "2026-06-01 02:00:00",
            ]
        ),
        "grid_import_kwh": [
            1.0,
            1.0,
            1.0,
        ],
        "solar_surplus_kwh": [
            0.0,
            0.0,
            0.0,
        ],
    }
)

    model = TimeOfUsePriceModel(
        peak_price_eur_per_kwh=0.25,
        flat_price_eur_per_kwh=0.18,
        off_peak_price_eur_per_kwh=0.12,
        surplus_compensation_price=0.07,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    result = model.calculate_net_cost(
        energy_df=energy_df,
        grid_import_column="grid_import_kwh",
        surplus_column="solar_surplus_kwh",
        simulation_days=1,
    )

    assert result == pytest.approx(
        0.25 + 0.18 + 0.12
    )

def test_hourly_price_model_calculates_net_cost() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
                2.0,
            ],
            "solar_surplus_kwh": [
                0.0,
                0.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.10,
                0.20,
            ],
        }
    )

    model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.05,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    result = model.calculate_net_cost(
        energy_df=energy_df,
        grid_import_column=(
            "grid_import_kwh"
        ),
        surplus_column=(
            "solar_surplus_kwh"
        ),
        simulation_days=1,
    )

    expected_cost = (
        1.0 * 0.10
        + 2.0 * 0.20
    )

    assert result == pytest.approx(
        expected_cost
    )

def test_hourly_price_model_compensates_surplus() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
                1.0,
            ],
            "solar_surplus_kwh": [
                1.0,
                1.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.20,
                0.20,
            ],
        }
    )

    model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.05,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    result = model.calculate_net_cost(
        energy_df=energy_df,
        grid_import_column=(
            "grid_import_kwh"
        ),
        surplus_column=(
            "solar_surplus_kwh"
        ),
        simulation_days=1,
    )

    expected_import_cost = (
        2.0 * 0.20
    )

    expected_surplus_income = (
        2.0 * 0.05
    )

    assert result == pytest.approx(
        expected_import_cost
        - expected_surplus_income
    )

def test_hourly_price_model_allows_negative_prices() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
            ],
            "solar_surplus_kwh": [
                0.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                -0.05,
            ],
        }
    )

    model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
        allow_negative_prices=True,
    )

    result = model.calculate_net_cost(
        energy_df=energy_df,
        grid_import_column=(
            "grid_import_kwh"
        ),
        surplus_column=(
            "solar_surplus_kwh"
        ),
        simulation_days=1,
    )

    assert result == pytest.approx(
        0.0
    )

def test_hourly_price_model_rejects_negative_prices_by_default() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                -0.05,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match=(
            "Hourly price data contains "
            "negative prices"
        ),
    ):
        HourlyPriceModel(
            price_df=price_df,
            surplus_compensation_price=0.0,
            contracted_power_kw=0.0,
            power_price_eur_per_kw_year=0.0,
        )

def test_hourly_price_model_rejects_missing_price_timestamp() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
                1.0,
            ],
            "solar_surplus_kwh": [
                0.0,
                0.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.20,
            ],
        }
    )

    model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Missing hourly electricity prices"
        ),
    ):
        model.calculate_net_cost(
            energy_df=energy_df,
            grid_import_column=(
                "grid_import_kwh"
            ),
            surplus_column=(
                "solar_surplus_kwh"
            ),
            simulation_days=1,
        )

def test_hourly_price_model_matches_protocol() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.20,
            ],
        }
    )

    model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.05,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    accepted_model = (
        accepts_electricity_price_model(
            model
        )
    )

    assert accepted_model is model


def test_fixed_price_model_calculates_variable_grid_cost() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
                2.0,
            ],
        }
    )

    model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    result = model.calculate_variable_grid_cost(
        energy_df=energy_df,
        grid_import_column="grid_import_kwh",
    )

    assert result == pytest.approx(
        0.60
    )

def test_time_of_use_model_calculates_variable_grid_cost() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 02:00:00",
                    "2026-06-01 11:00:00",
                    "2026-06-01 15:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
                2.0,
                3.0,
            ],
        }
    )

    model = TimeOfUsePriceModel(
        peak_price_eur_per_kwh=0.25,
        flat_price_eur_per_kwh=0.18,
        off_peak_price_eur_per_kwh=0.12,
        surplus_compensation_price=0.0,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    result = model.calculate_variable_grid_cost(
        energy_df=energy_df,
        grid_import_column="grid_import_kwh",
    )

    assert result == pytest.approx(
        1.16
    )

def test_hourly_price_model_calculates_variable_grid_cost() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "grid_import_kwh": [
                1.0,
                2.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.10,
                0.20,
            ],
        }
    )

    model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    result = model.calculate_variable_grid_cost(
        energy_df=energy_df,
        grid_import_column="grid_import_kwh",
    )

    assert result == pytest.approx(
        0.50
    )