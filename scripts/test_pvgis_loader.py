import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from solar_data_loader import load_pvgis_solar_data


def main() -> None:
    file_path = "data/raw/pvgis_hourly_linares_1kw_2020.csv"

    df = load_pvgis_solar_data(file_path)

    print("\nPVGIS solar data loaded:")
    print(f"Number of rows: {len(df)}")
    print(f"Start datetime: {df['datetime'].min()}")
    print(f"End datetime: {df['datetime'].max()}")

    print("\nFirst rows:")
    print(df[["datetime", "P", "solar_generation_1kw_kwh"]].head(24).to_string(index=False))

    print("\nTotal yearly generation for 1 kW system:")
    print(f"{df['solar_generation_1kw_kwh'].sum():.2f} kWh")


if __name__ == "__main__":
    main()