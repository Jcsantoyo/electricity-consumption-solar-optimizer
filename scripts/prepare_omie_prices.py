import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


from omie_price_loader import (
    aggregate_omie_prices_to_hourly,
    load_omie_quarter_hour_prices,
)

DEFAULT_INPUT_DIRECTORY = "data/raw"
DEFAULT_OUTPUT_PATH = "data/processed/omie_hourly_prices.csv"
OMIE_FILE_PATTERN = "marginalpdbc_*.1"

def find_omie_files(input_directory: str) -> list[Path]:
    input_path = Path(input_directory)

    if not input_path.exists():
        raise FileNotFoundError(f"OMIE input directory not found: {input_directory}")
    
    omie_files = sorted(input_path.glob(OMIE_FILE_PATTERN))

    if not omie_files:
        raise FileNotFoundError(
            "No OMIE files found in "
            f"{input_directory} using pattern {OMIE_FILE_PATTERN}"
        )
    
    return omie_files

def build_hourly_omie_price_dataframe(omie_files: list[Path]) -> pd.DataFrame:
    hourly_dataframes = []

    for omie_file in omie_files:
        quarter_hour_df = load_omie_quarter_hour_prices(str(omie_file))

        hourly_df = aggregate_omie_prices_to_hourly(quarter_hour_df)

        hourly_dataframes.append(hourly_df)

    combined_df = pd.concat(hourly_dataframes, ignore_index=True)

    combined_df = combined_df.sort_values("datetime")

    combined_df = combined_df.drop_duplicates(
        subset=["datetime"],
        keep="last"
    )

    combined_df = combined_df.reset_index(drop=True)

    return combined_df


def prepare_omie_prices(
    input_directory: str = DEFAULT_INPUT_DIRECTORY,
    output_path: str = DEFAULT_OUTPUT_PATH
) -> pd.DataFrame:
    
    omie_files = find_omie_files(input_directory)

    hourly_price_df = build_hourly_omie_price_dataframe(omie_files)

    output_file = Path(output_path)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    hourly_price_df.to_csv(output_file, index=False)

    return hourly_price_df

def main() -> None:
    hourly_price_df = prepare_omie_prices()

    print("OMIE hourly price data prepared successfully")

    print(f"Processed rows: {len(hourly_price_df)}")

    print(f"Output file: {DEFAULT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()