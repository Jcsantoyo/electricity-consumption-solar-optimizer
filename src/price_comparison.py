import pandas as pd

from hourly_price_calculator import(
    calculate_total_hourly_grid_import_cost,
    prepare_energy_data
) 

from tariff import calculate_variable_grid_cost_with_tariff

def calculate_flat_grid_import_cost(
    energy_df: pd.DataFrame,
    flat_price_eur_per_kwh: float
) -> float:
    
    validate_flat_price(flat_price_eur_per_kwh)

    if "grid_import_kwh" not in energy_df.columns:
        raise ValueError("Missing required energy column: grid_import_kwh")
    
    grid_import = pd.to_numeric(energy_df["grid_import_kwh"], errors="coerce")

    if grid_import.isna().any():
        raise ValueError("Energy data contains invalid grid import values")
    
    if (grid_import < 0).any():
        raise ValueError("Energy data contains negative grid import values")
    
    return float(grid_import.sum() * flat_price_eur_per_kwh)

def compare_flat_vs_hourly_price_cost(
        energy_df: pd.DataFrame,
        price_df: pd.DataFrame,
        flat_price_eur_per_kwh: float
) -> dict:
    
    flat_cost = calculate_flat_grid_import_cost(energy_df, flat_price_eur_per_kwh)

    hourly_cost = calculate_total_hourly_grid_import_cost(energy_df, price_df)

    difference = hourly_cost - flat_cost

    return {
        "flat_cost_eur": flat_cost,
        "hourly_cost_eur": hourly_cost,
        "difference_eur": difference
    }

def validate_flat_price(flat_price_eur_per_kwh) -> None:
    if flat_price_eur_per_kwh < 0:
        raise ValueError("Flat electricity price cannot be negative")
    
def compare_tariff_vs_hourly_price_cost(
        energy_df: pd.DataFrame,
        price_df: pd.DataFrame,
        peak_price_eur_per_kwh: float,
        flat_price_eur_per_kwh: float,
        off_peak_price_eur_per_kwh: float
) -> dict:
    
    prepared_energy_df = prepare_energy_data(energy_df)
    
    tariff_cost = calculate_variable_grid_cost_with_tariff(
        df=prepared_energy_df,
        grid_import_column="grid_import_kwh",
        peak_price=peak_price_eur_per_kwh,
        flat_price=flat_price_eur_per_kwh,
        off_peak_price=off_peak_price_eur_per_kwh
    )

    hourly_cost = calculate_total_hourly_grid_import_cost(prepared_energy_df, price_df)

    difference = hourly_cost - tariff_cost

    return{
        "tariff_cost_eur": float(tariff_cost),
        "hourly_cost_eur": float(hourly_cost),
        "difference_eur": float(difference)
    }