import pandas as pd


def load_pvgis_solar_data(file_path: str) -> pd.DataFrame:

    df = pd.read_csv(file_path)

    required_columns = ["time", "P"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    df["datetime"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")

    df["solar_generation_1kw_kwh"] = df["P"] / 1000

    df = df.sort_values("datetime").reset_index(drop=True)

    return df


def get_pvgis_generation_for_timestamps(
    pvgis_df: pd.DataFrame, timestamps, peak_power_kw: float
) -> list[float]:

    solar_df = pvgis_df.copy()

    solar_df["month"] = solar_df["datetime"].dt.month
    solar_df["day"] = solar_df["datetime"].dt.day
    solar_df["hour"] = solar_df["datetime"].dt.hour

    timestamps_df = pd.DataFrame({"datetime": timestamps})

    timestamps_df["month"] = timestamps_df["datetime"].dt.month
    timestamps_df["day"] = timestamps_df["datetime"].dt.day
    timestamps_df["hour"] = timestamps_df["datetime"].dt.hour

    merged_df = timestamps_df.merge(
        solar_df[["month", "day", "hour", "solar_generation_1kw_kwh"]],
        on=["month", "day", "hour"],
        how="left",
    )

    merged_df["solar_generation_kwh"] = (
        merged_df["solar_generation_1kw_kwh"] * peak_power_kw
    )

    return merged_df["solar_generation_kwh"].fillna(0.0).tolist()
