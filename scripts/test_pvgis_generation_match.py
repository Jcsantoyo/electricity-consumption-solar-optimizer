import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from data_loader import load_consumption_data
from solar_data_loader import load_pvgis_solar_data, get_pvgis_generation_for_timestamps


def main() -> None:
    consumption_path = "data/simulated/synthetic_consumption_30_days.csv"
    pvgis_path = "data/raw/pvgis_hourly_linares_1kw_2020.csv"

    df_consumption = load_consumption_data(consumption_path)
    df_pvgis = load_pvgis_solar_data(pvgis_path)

    peak_power_kw = 1.5

    solar_generation_kwh = get_pvgis_generation_for_timestamps(
        df_pvgis, df_consumption["datetime"], peak_power_kw
    )

    df_consumption["solar_generation_kwh"] = solar_generation_kwh

    print("\nPVGIS solar generation matched to consumption timestamps:")
    print(f"Number of consumption rows: {len(df_consumption)}")
    print(f"Number of solar generation values: {len(solar_generation_kwh)}")
    print(f"Solar peak power: {peak_power_kw:.2f} kW")

    print("\nFirst rows:")
    print(
        df_consumption[["datetime", "consumption_kwh", "solar_generation_kwh"]]
        .head(48)
        .to_string(index=False)
    )

    print("\nTotal solar generation:")
    print(f"{sum(solar_generation_kwh):.2f} kWh")


if __name__ == "__main__":
    main()
