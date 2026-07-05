import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from uci_household_loader import (
    load_uci_household_power_data,
    convert_uci_minute_power_to_hourly_consumption,
    save_hourly_consumption_data
)


def main() -> None:
    input_path = "data/raw/household_power_consumption.txt"
    output_path = "data/processed/uci_household_power_hourly.csv"

    os.makedirs("data/processed", exist_ok=True)

    print("\nLoading UCI household power dataset...")
    df = load_uci_household_power_data(input_path)

    print(f"Raw rows loaded: {len(df)}")
    print(f"Start datetime: {df['datetime'].min()}")
    print(f"End datetime: {df['datetime'].max()}")

    print("\nConverting minute-level power data to hourly consumption...")
    hourly_df = convert_uci_minute_power_to_hourly_consumption(df)

    save_hourly_consumption_data(
        hourly_df,
        output_path
    )

    print("\nHourly consumption dataset generated:")
    print(f"Output file: {output_path}")
    print(f"Number of hourly rows: {len(hourly_df)}")
    print(f"Start datetime: {hourly_df['datetime'].min()}")
    print(f"End datetime: {hourly_df['datetime'].max()}")
    print(f"Total consumption: {hourly_df['consumption_kwh'].sum():.2f} kWh")
    print(f"Average hourly consumption: {hourly_df['consumption_kwh'].mean():.3f} kWh")


if __name__ == "__main__":
    main()