from pathlib import Path

import pandas as pd

REQUIRED_HOURLY_PRICE_COLUMNS = {
    "datetime",
    "price_eur_per_kwh"
}

def load_hourly_prices(file_path: str, allow_negative_prices: bool = False) -> pd.DataFrame:
    price_path = Path(file_path)

    if not price_path.exists():
        raise FileNotFoundError(f"Hourly price file not found: {file_path}")
    
    price_df = pd.read_csv(price_path)

    validate_hourly_price_columns(price_df)

    price_df = prepare_hourly_price_data(price_df, allow_negative_prices)

    return price_df

def validate_hourly_price_columns(price_df: pd.DataFrame) -> None:
    missing_columns = REQUIRED_HOURLY_PRICE_COLUMNS - set(price_df.columns)

    if missing_columns:
        raise ValueError(f"Missing required hourly price columns: {sorted(missing_columns)}")
    

def prepare_hourly_price_data(
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
        raise ValueError(
            "Hourly price data contains invalid datetime values"
        )

    if prepared_df["price_eur_per_kwh"].isna().any():
        raise ValueError(
            "Hourly price data contains invalid price values"
        )

    if (
        not allow_negative_prices
        and (prepared_df["price_eur_per_kwh"] < 0).any()
    ):
        raise ValueError(
            "Hourly price data contains negative prices"
        )

    prepared_df = prepared_df.sort_values("datetime")
    prepared_df = prepared_df.reset_index(drop=True)

    return prepared_df

def load_hourly_prices_if_enabled(
    use_hourly_price_data: bool,
    file_path: str,
    allow_negative_prices: bool = False
) -> pd.DataFrame | None:
    if not use_hourly_price_data:
        return None
    
    return load_hourly_prices(file_path, allow_negative_prices)


def validate_hourly_price_coverage(
    consumption_df: pd.DataFrame,
    price_df: pd.DataFrame
) -> None:
    
    if "datetime" not in consumption_df.columns:
        raise ValueError("Consumtion data is missing required column: datetime")
    
    if "datetime" not in price_df.columns:
        raise ValueError("Hourly price data is missing required column: datetime")
    
    consumption_datetimes = set(
        pd.to_datetime(consumption_df["datetime"], errors="coerce")
    )

    price_datetimes = set(
        pd.to_datetime(price_df["datetime"], errors="coerce")
    )

    if pd.NaT in consumption_datetimes:
        raise ValueError("Consumption data contains invalid datetime values")
    
    if pd.NaT in price_datetimes:
        raise ValueError("Hourly price data contains invalid datetime values")
    
    missing_datetimes = consumption_datetimes - price_datetimes

    if missing_datetimes:
        raise ValueError(
            "Hourly price data does not cover "
            f"{len(missing_datetimes)} consumption timestamps"
        )