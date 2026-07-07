import os
import requests
import pandas as pd


PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"


def download_pvgis_hourly_data(
    latitude: float,
    longitude: float,
    peak_power_kw: float,
    loss_percent: float,
    start_year: int,
    end_year: int,
    output_path: str,
) -> None:
    params = {
        "lat": latitude,
        "lon": longitude,
        "startyear": start_year,
        "endyear": end_year,
        "pvcalculation": 1,
        "peakpower": peak_power_kw,
        "loss": loss_percent,
        "angle": 30,
        "aspect": 0,
        "outputformat": "json",
    }

    response = requests.get(PVGIS_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    hourly_data = data["outputs"]["hourly"]

    df = pd.DataFrame(hourly_data)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df.to_csv(output_path, index=False)

    print("\nPVGIS hourly data downloaded")
    print(f"Output file: {output_path}")
    print(f"Number of rows: {len(df)}")
    print("Columns:")
    print(df.columns.tolist())


def main() -> None:
    latitude = 38.0952
    longitude = -3.6360

    peak_power_kw = 1.0
    loss_percent = 14.0

    start_year = 2020
    end_year = 2020

    output_path = "data/raw/pvgis_hourly_linares_1kw_2020.csv"

    download_pvgis_hourly_data(
        latitude,
        longitude,
        peak_power_kw,
        loss_percent,
        start_year,
        end_year,
        output_path,
    )


if __name__ == "__main__":
    main()
