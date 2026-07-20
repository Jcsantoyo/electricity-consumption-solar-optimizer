import pandas as pd

REQUIRED_ENERGY_COLUMNS = {"datetime", "grid_import_kwh"}

REQUIRED_PRICE_COLUMNS = {"datetime", "price_eur_per_kwh"}


def calculate_hourly_grid_import_cost(
    energy_df: pd.DataFrame, price_df: pd.DataFrame, allow_negative_prices: bool = False
) -> pd.DataFrame:

    validate_hourly_cost_inputs(energy_df, price_df)

    prepared_energy_df = prepare_energy_data(energy_df)
    prepared_price_df = prepare_price_data(price_df, allow_negative_prices)

    merged_df = prepared_energy_df.merge(prepared_price_df, on="datetime", how="left")

    if merged_df["price_eur_per_kwh"].isna().any():
        raise ValueError("Missing hourly electricity prices for some energy timestamps")

    merged_df["grid_import_cost_eur"] = (
        merged_df["grid_import_kwh"] * merged_df["price_eur_per_kwh"]
    )

    return merged_df


def calculate_total_hourly_grid_import_cost(
    energy_df: pd.DataFrame, price_df: pd.DataFrame, allow_negative_prices: bool = False
) -> float:

    cost_df = calculate_hourly_grid_import_cost(
        energy_df, price_df, allow_negative_prices
    )

    return float(cost_df["grid_import_cost_eur"].sum())


def validate_hourly_cost_inputs(
    energy_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> None:
    missing_energy_columns = REQUIRED_ENERGY_COLUMNS - set(energy_df.columns)

    if missing_energy_columns:
        raise ValueError(
            f"Missing required energy columns: {sorted(missing_energy_columns)}"
        )

    missing_price_columns = REQUIRED_PRICE_COLUMNS - set(price_df.columns)

    if missing_price_columns:
        raise ValueError(
            f"Missing required price columns: {sorted(missing_price_columns)}"
        )


def prepare_energy_data(energy_df: pd.DataFrame) -> pd.DataFrame:
    prepared_df = energy_df.copy()

    prepared_df["datetime"] = pd.to_datetime(
        prepared_df["datetime"],
        errors="coerce",
    )

    prepared_df["grid_import_kwh"] = pd.to_numeric(
        prepared_df["grid_import_kwh"],
        errors="coerce",
    )

    if prepared_df["datetime"].isna().any():
        raise ValueError("Energy data contains invalid datetime values")

    if prepared_df["grid_import_kwh"].isna().any():
        raise ValueError("Energy data contains invalid grid import values")

    if (prepared_df["grid_import_kwh"] < 0).any():
        raise ValueError("Energy data contains negative grid import values")

    prepared_df = prepared_df.sort_values("datetime")
    prepared_df = prepared_df.reset_index(drop=True)

    return prepared_df


def prepare_price_data(
    price_df: pd.DataFrame,
    allow_negative_prices: bool = False,
) -> pd.DataFrame:
    prepared_df = price_df.copy()

    prepared_df["datetime"] = pd.to_datetime(
        prepared_df["datetime"],
        errors="coerce",
    )

    prepared_df["price_eur_per_kwh"] = pd.to_numeric(
        prepared_df["price_eur_per_kwh"],
        errors="coerce",
    )

    if prepared_df["datetime"].isna().any():
        raise ValueError("Price data contains invalid datetime values")

    if prepared_df["price_eur_per_kwh"].isna().any():
        raise ValueError("Price data contains invalid price values")

    if not allow_negative_prices and (prepared_df["price_eur_per_kwh"] < 0).any():
        raise ValueError("Price data contains negative price values")

    prepared_df = prepared_df.sort_values("datetime")
    prepared_df = prepared_df.reset_index(drop=True)

    return prepared_df
