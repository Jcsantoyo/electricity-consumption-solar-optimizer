import pandas as pd


def load_uci_household_power_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=";", na_values=["?"], low_memory=False)

    required_columns = ["Date", "Time", "Global_active_power"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    df = df[required_columns].copy()

    df["datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    )

    df["Global_active_power"] = pd.to_numeric(
        df["Global_active_power"], errors="coerce"
    )

    df = df.dropna(subset=["datetime", "Global_active_power"]).reset_index(drop=True)

    return df


def convert_uci_minute_power_to_hourly_consumption(df: pd.DataFrame) -> pd.DataFrame:

    df["consumption_kwh"] = df["Global_active_power"] / 60.0

    hourly_df = (
        df.set_index("datetime").resample("h")["consumption_kwh"].sum().reset_index()
    )

    hourly_df = hourly_df.dropna().reset_index(drop=True)

    return hourly_df


def save_hourly_consumption_data(hourly_df: pd.DataFrame, output_path: str) -> None:

    hourly_df.to_csv(output_path, index=False)
