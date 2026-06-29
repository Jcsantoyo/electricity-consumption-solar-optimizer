import pandas as pd

def load_consumption_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    require_columns = ["datetime", "consumption_kwh"]

    for column in require_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")
        
    df["datetime"] = pd.to_datetime(df["datetime"])

    df = df.sort_values("datetime").reset_index(drop=True)

    df["hour"] = df["datetime"].dt.hour
    df["day"] = df["datetime"].dt.day
    df["month"] = df["datetime"].dt.month
    df["weekday"] = df["datetime"].dt.weekday

    return df