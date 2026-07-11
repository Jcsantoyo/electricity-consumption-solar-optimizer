import pandas as pd
import pytest

from price_comparison import (
    calculate_flat_grid_import_cost,
    compare_flat_vs_hourly_price_cost,
    compare_tariff_vs_hourly_price_cost
)


def test_calculate_flat_grid_import_cost_returns_expected_cost() -> None:
    energy_df = pd.DataFrame(
        {
            "grid_import_kwh": [
                1.0,
                2.0,
                3.0,
            ],
        }
    )

    cost = calculate_flat_grid_import_cost(
        energy_df=energy_df,
        flat_price_eur_per_kwh=0.20,
    )

    assert cost == pytest.approx(1.20)


def test_compare_flat_vs_hourly_price_cost_returns_expected_values() -> None:
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
                0.30,
            ],
        }
    )

    comparison = compare_flat_vs_hourly_price_cost(
        energy_df=energy_df,
        price_df=price_df,
        flat_price_eur_per_kwh=0.20,
    )

    assert comparison["flat_cost_eur"] == pytest.approx(0.60)
    assert comparison["hourly_cost_eur"] == pytest.approx(0.70)
    assert comparison["difference_eur"] == pytest.approx(0.10)


def test_calculate_flat_grid_import_cost_raises_error_for_missing_column() -> None:
    energy_df = pd.DataFrame(
        {
            "import_kwh": [
                1.0,
            ],
        }
    )

    with pytest.raises(ValueError, match="Missing required energy column"):
        calculate_flat_grid_import_cost(
            energy_df=energy_df,
            flat_price_eur_per_kwh=0.20,
        )


def test_calculate_flat_grid_import_cost_raises_error_for_invalid_grid_import() -> None:
    energy_df = pd.DataFrame(
        {
            "grid_import_kwh": [
                "not-a-number",
            ],
        }
    )

    with pytest.raises(ValueError, match="invalid grid import"):
        calculate_flat_grid_import_cost(
            energy_df=energy_df,
            flat_price_eur_per_kwh=0.20,
        )


def test_calculate_flat_grid_import_cost_raises_error_for_negative_grid_import() -> None:
    energy_df = pd.DataFrame(
        {
            "grid_import_kwh": [
                -1.0,
            ],
        }
    )

    with pytest.raises(ValueError, match="negative grid import"):
        calculate_flat_grid_import_cost(
            energy_df=energy_df,
            flat_price_eur_per_kwh=0.20,
        )


def test_calculate_flat_grid_import_cost_raises_error_for_negative_flat_price() -> None:
    energy_df = pd.DataFrame(
        {
            "grid_import_kwh": [
                1.0,
            ],
        }
    )

    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_flat_grid_import_cost(
            energy_df=energy_df,
            flat_price_eur_per_kwh=-0.20,
        )


def test_compare_tariff_vs_hourly_price_cost_returns_expected_values() -> None:
    energy_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-06 01:00:00",
                "2025-01-06 11:00:00",
                "2025-01-06 15:00:00",
            ],
            "grid_import_kwh": [
                1.0,
                2.0,
                3.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-06 01:00:00",
                "2025-01-06 11:00:00",
                "2025-01-06 15:00:00",
            ],
            "price_eur_per_kwh": [
                0.10,
                0.20,
                0.15,
            ],
        }
    )

    comparison = compare_tariff_vs_hourly_price_cost(
        energy_df=energy_df,
        price_df=price_df,
        peak_price_eur_per_kwh=0.25,
        flat_price_eur_per_kwh=0.18,
        off_peak_price_eur_per_kwh=0.12,
    )

    assert comparison["tariff_cost_eur"] == pytest.approx(1.16)
    assert comparison["hourly_cost_eur"] == pytest.approx(0.95)
    assert comparison["difference_eur"] == pytest.approx(-0.21)