import pandas as pd

def select_consumption_period(
    consumption_df: pd.DataFrame,
    number_of_days: int
) -> pd.DataFrame:
    validate_consumption_dataframe(consumption_df)

    if number_of_days <= 0:
        raise ValueError("Number of days must be greater than zero")
    
    number_of_hours = number_of_days * 24

    if len(consumption_df) < number_of_hours:
        raise ValueError(
            "Consumption data does not contain enough rows for "
            f"{number_of_days} days"
        )
    
    selected_df = consumption_df.iloc[:number_of_hours].copy()
    selected_df = selected_df.reset_index(drop=True)

    return selected_df

def remap_consumption_timestamps(
    consumption_df: pd.DataFrame,
    target_start_datetime: str
) -> pd.DataFrame:
    validate_consumption_dataframe(consumption_df)

    target_start = pd.to_datetime(target_start_datetime, errors="coerce")

    if pd.isna(target_start):
        raise ValueError("Target start datetime is invalid")
    
    remapped_df = consumption_df.copy()

    remapped_df["original_datetime"] = remapped_df["datetime"]

    remapped_df["datetime"] = pd.date_range(
        start=target_start,
        periods=len(remapped_df),
        freq="h"
    )

    return remapped_df

def build_recent_consumption_scenario(
    consumption_df: pd.DataFrame,
    number_of_days: int,
    target_start_datetime: str | pd.Timestamp
) -> pd.DataFrame:
    selected_df = select_consumption_period(
        consumption_df,
        number_of_days
    )

    remapped_df = remap_consumption_timestamps(
        selected_df,
        target_start_datetime
    )

    return remapped_df


def validate_consumption_dataframe(consumption_df: pd.DataFrame) -> None:
    required_columns = {
        "datetime",
        "consumption_kwh",
    }

    missing_columns = required_columns - set(consumption_df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required consumption columns: "
            f"{sorted(missing_columns)}"
        )

    datetime_values = pd.to_datetime(
        consumption_df["datetime"],
        errors="coerce",
    )

    consumption_values = pd.to_numeric(
        consumption_df["consumption_kwh"],
        errors="coerce",
    )

    if datetime_values.isna().any():
        raise ValueError(
            "Consumption data contains invalid datetime values"
        )

    if consumption_values.isna().any():
        raise ValueError(
            "Consumption data contains invalid consumption values"
        )

    if (consumption_values < 0).any():
        raise ValueError(
            "Consumption data contains negative consumption values"
        )