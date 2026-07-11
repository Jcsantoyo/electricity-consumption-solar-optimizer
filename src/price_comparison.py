import pandas as pd

from hourly_price_calculator import calculate_total_hourly_grid_import_cost

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