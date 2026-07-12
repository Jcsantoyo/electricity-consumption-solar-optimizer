import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

import config
from consumption_time_mapper import build_recent_consumption_scenario
from data_loader import load_consumption_data

DEFAULT_OUTUPUT_PATH = "data/processed/uci_consumption_omie_scenario.csv"

DEFAULT_NUMBER_OF_DAYS = 30
DEFAULT_TARGET_START_DATETIME = "2026-06-01 00:00:00"

def prepare_uci_omie_scenario(
    consumption_path: str,
    output_path: str,
    number_of_days: int,
    target_start_datetime: str
) -> pd.DataFrame:
    consumption_df = load_consumption_data(consumption_path)

    scenario_df = build_recent_consumption_scenario(
        consumption_df,
        number_of_days,
        target_start_datetime
    )

    output_file = Path(output_path)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    scenario_df.to_csv(output_file, index=False)

    return scenario_df

def main() -> None:
    scenario_df = prepare_uci_omie_scenario(
        config.CONSUMPTION_DATA_PATH,
        DEFAULT_OUTUPUT_PATH,
        DEFAULT_NUMBER_OF_DAYS,
        DEFAULT_TARGET_START_DATETIME
    )

    print("UCI OMIE consumption scenario prepared successfully.")
    print(f"Processed rows: {len(scenario_df)}")
    print(f"Scenario start: {scenario_df['datetime'].min()}")
    print(f"Scenario end: {scenario_df['datetime'].max()}")
    print(f"Output file: {DEFAULT_OUTUPUT_PATH}")

if __name__ == "__main__":
    main()