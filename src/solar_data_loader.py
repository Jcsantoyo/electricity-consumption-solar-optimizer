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