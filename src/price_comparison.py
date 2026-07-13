import pandas as pd

from hourly_price_calculator import (
    calculate_total_hourly_grid_import_cost,
    prepare_energy_data,
)
from tariff import calculate_variable_grid_cost_with_tariff


def calculate_flat_grid_import_cost(
    energy_df: pd.DataFrame,
    flat_price_eur_per_kwh: float,
) -> float:
    validate_flat_price(flat_price_eur_per_kwh)

    if "grid_import_kwh" not in energy_df.columns:
        raise ValueError(
            "Missing required energy column: grid_import_kwh"
        )

    grid_import = pd.to_numeric(
        energy_df["grid_import_kwh"],
        errors="coerce",
    )

    if grid_import.isna().any():
        raise ValueError(
            "Energy data contains invalid grid import values"
        )

    if (grid_import < 0).any():
        raise ValueError(
            "Energy data contains negative grid import values"
        )

    return float(
        grid_import.sum() * flat_price_eur_per_kwh
    )


def compare_flat_vs_hourly_price_cost(
    energy_df: pd.DataFrame,
    price_df: pd.DataFrame,
    flat_price_eur_per_kwh: float,
    allow_negative_hourly_prices: bool = False,
) -> dict:
    flat_cost = calculate_flat_grid_import_cost(
        energy_df=energy_df,
        flat_price_eur_per_kwh=flat_price_eur_per_kwh,
    )

    hourly_cost = calculate_total_hourly_grid_import_cost(
        energy_df=energy_df,
        price_df=price_df,
        allow_negative_prices=allow_negative_hourly_prices,
    )

    difference = hourly_cost - flat_cost

    return {
        "flat_cost_eur": flat_cost,
        "hourly_cost_eur": hourly_cost,
        "difference_eur": difference,
    }


def validate_flat_price(
    flat_price_eur_per_kwh: float,
) -> None:
    if flat_price_eur_per_kwh < 0:
        raise ValueError(
            "Flat electricity price cannot be negative"
        )


def compare_tariff_vs_hourly_price_cost(
    energy_df: pd.DataFrame,
    price_df: pd.DataFrame,
    peak_price_eur_per_kwh: float,
    flat_price_eur_per_kwh: float,
    off_peak_price_eur_per_kwh: float,
    allow_negative_hourly_prices: bool = False,
) -> dict:
    prepared_energy_df = prepare_energy_data(energy_df)

    tariff_cost = calculate_variable_grid_cost_with_tariff(
        df=prepared_energy_df,
        grid_import_column="grid_import_kwh",
        peak_price=peak_price_eur_per_kwh,
        flat_price=flat_price_eur_per_kwh,
        off_peak_price=off_peak_price_eur_per_kwh,
    )

    hourly_cost = calculate_total_hourly_grid_import_cost(
        energy_df=prepared_energy_df,
        price_df=price_df,
        allow_negative_prices=allow_negative_hourly_prices,
    )

    difference = hourly_cost - tariff_cost

    return {
        "tariff_cost_eur": float(tariff_cost),
        "hourly_cost_eur": float(hourly_cost),
        "difference_eur": float(difference),
    }


def compare_all_price_modes(
    energy_df: pd.DataFrame,
    price_df: pd.DataFrame,
    fixed_price_eur_per_kwh: float,
    peak_price_eur_per_kwh: float,
    flat_price_eur_per_kwh: float,
    off_peak_price_eur_per_kwh: float,
    allow_negative_hourly_prices: bool = False,
) -> pd.DataFrame:
    prepared_energy_df = prepare_energy_data(energy_df)

    fixed_cost = calculate_flat_grid_import_cost(
        energy_df=prepared_energy_df,
        flat_price_eur_per_kwh=fixed_price_eur_per_kwh,
    )

    tariff_cost = calculate_variable_grid_cost_with_tariff(
        df=prepared_energy_df,
        grid_import_column="grid_import_kwh",
        peak_price=peak_price_eur_per_kwh,
        flat_price=flat_price_eur_per_kwh,
        off_peak_price=off_peak_price_eur_per_kwh,
    )

    hourly_cost = calculate_total_hourly_grid_import_cost(
        energy_df=prepared_energy_df,
        price_df=price_df,
        allow_negative_prices=allow_negative_hourly_prices,
    )

    comparison_df = pd.DataFrame(
        {
            "price_mode": [
                "flat_fixed",
                "spanish_2_0td",
                "hourly",
            ],
            "variable_grid_cost_eur": [
                fixed_cost,
                float(tariff_cost),
                hourly_cost,
            ],
        }
    )

    comparison_df["difference_vs_flat_eur"] = (
        comparison_df["variable_grid_cost_eur"]
        - fixed_cost
    )

    comparison_df["difference_vs_2_0td_eur"] = (
        comparison_df["variable_grid_cost_eur"]
        - float(tariff_cost)
    )

    return comparison_df