import pandas as pd
import pytest

from hourly_price_calculator import (
    calculate_hourly_grid_import_cost,
    calculate_total_hourly_grid_import_cost,
    prepare_energy_data,
    prepare_price_data,
)


def test_calculate_hourly_grid_import_cost_adds_cost_column() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "grid_import_kwh": [
                1.0,
                2.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "price_eur_per_kwh": [
                0.10,
                0.20,
            ],
        }
    )

    cost_df = calculate_hourly_grid_import_cost(
        energy_df=energy_df,
        price_df=price_df,
    )

    assert list(cost_df["grid_import_cost_eur"]) == [0.10, 0.40]


def test_calculate_total_hourly_grid_import_cost_returns_total_cost() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "grid_import_kwh": [
                1.0,
                2.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "price_eur_per_kwh": [
                0.10,
                0.20,
            ],
        }
    )

    total_cost = calculate_total_hourly_grid_import_cost(
        energy_df=energy_df,
        price_df=price_df,
    )

    assert total_cost == 0.50


def test_calculate_hourly_grid_import_cost_raises_error_for_missing_price() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "grid_import_kwh": [
                1.0,
                2.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
            ],
            "price_eur_per_kwh": [
                0.10,
            ],
        }
    )

    with pytest.raises(ValueError, match="Missing hourly electricity prices"):
        calculate_hourly_grid_import_cost(
            energy_df=energy_df,
            price_df=price_df,
        )


def test_prepare_energy_data_raises_error_for_negative_grid_import() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "grid_import_kwh": [-1.0],
        }
    )

    with pytest.raises(ValueError, match="negative grid import"):
        prepare_energy_data(energy_df)


def test_prepare_price_data_raises_error_for_negative_price() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "price_eur_per_kwh": [-0.10],
        }
    )

    with pytest.raises(ValueError, match="negative price"):
        prepare_price_data(price_df)


def test_calculate_hourly_grid_import_cost_raises_error_for_missing_energy_column() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "import_kwh": [1.0],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "price_eur_per_kwh": [0.10],
        }
    )

    with pytest.raises(ValueError, match="Missing required energy columns"):
        calculate_hourly_grid_import_cost(
            energy_df=energy_df,
            price_df=price_df,
        )


def test_calculate_hourly_grid_import_cost_raises_error_for_missing_price_column() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "grid_import_kwh": [1.0],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "price": [0.10],
        }
    )

    with pytest.raises(ValueError, match="Missing required price columns"):
        calculate_hourly_grid_import_cost(
            energy_df=energy_df,
            price_df=price_df,
        )
