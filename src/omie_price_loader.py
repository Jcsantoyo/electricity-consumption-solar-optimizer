from pathlib import Path

import pandas as pd

def load_omie_quarter_hour_prices(file_path: str) -> pd.DataFrame:
    omie_path = Path(file_path)

    if not omie_path.exists():
        raise FileNotFoundError(f"OMIE price file not found: {file_path}")
    
    raw_df = pd.read_csv(
        omie_path,
        sep=";",
        skiprows=1,
        header=None,
        names=[
            "year",
            "month",
            "day",
            "period",
            "spain_price_eur_per_mwh",
            "portugal_price_eur_per_mwh",
            "empty_column"
        ]
    )

    raw_df = raw_df[raw_df["year"] != "*"].copy()

    raw_df["year"] = pd.to_numeric(
        raw_df["year"],
        errors="coerce",
    )

    raw_df["month"] = pd.to_numeric(
        raw_df["month"],
        errors="coerce",
    )

    raw_df["day"] = pd.to_numeric(
        raw_df["day"],
        errors="coerce",
    )

    raw_df["period"] = pd.to_numeric(
        raw_df["period"],
        errors="coerce",
    )

    raw_df["spain_price_eur_per_mwh"] = pd.to_numeric(
        raw_df["spain_price_eur_per_mwh"],
        errors="coerce",
    )

    validate_omie_quarter_hour_data(raw_df)

    base_datetime = pd.to_datetime(
        {
            "year": raw_df["year"],
            "month": raw_df["month"],
            "day": raw_df["day"]
        }
    )

    raw_df["datetime"] = base_datetime + pd.to_timedelta(
        (raw_df["period"] - 1) * 15,
        unit="minutes"
    )

    raw_df["price_eur_per_kwh"] = raw_df["spain_price_eur_per_mwh"] / 1000

    results_df = raw_df[["datetime", "price_eur_per_kwh"]].copy()

    results_df = results_df.sort_values("datetime")
    results_df = results_df.reset_index(drop=True)

    return results_df

def validate_omie_quarter_hour_data(omie_df: pd.DataFrame) -> None:
    required_columns = {
        "year",
        "month",
        "day",
        "period",
        "spain_price_eur_per_mwh",
    }

    missing_columns = required_columns - set(omie_df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required OMIE columns: "
            f"{sorted(missing_columns)}"
        )

    if omie_df[
        [
            "year",
            "month",
            "day",
            "period",
            "spain_price_eur_per_mwh",
        ]
    ].isna().any().any():
        raise ValueError("OMIE price data contains invalid values")

    if not omie_df["period"].between(1, 96).all():
        raise ValueError("OMIE period values must be between 1 and 96")

    if omie_df["period"].nunique() != 96:
        raise ValueError("OMIE price data must contain 96 quarter-hour periods")
    
def aggregate_omie_prices_to_hourly(
    quarter_hour_df: pd.DataFrame,
) -> pd.DataFrame:
    hourly_df = quarter_hour_df.copy()

    hourly_df["datetime"] = hourly_df["datetime"].dt.floor("h")

    hourly_df = (
        hourly_df.groupby(
            "datetime",
            as_index=False,
        )["price_eur_per_kwh"]
        .mean()
    )

    return hourly_df