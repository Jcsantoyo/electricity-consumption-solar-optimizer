import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )

import config
from data_loader import load_consumption_data
from price_loader import load_hourly_prices_if_enabled
from scenario_validation import (
    format_validation_report,
    validate_project_scenario_data,
)


def main() -> None:
    scenario = config.ACTIVE_PROJECT_SCENARIO

    consumption_df = load_consumption_data(scenario.consumption_data_path)

    price_df = load_hourly_prices_if_enabled(
        use_hourly_price_data=(scenario.uses_hourly_prices),
        file_path=(scenario.hourly_price_data_path or ""),
        allow_negative_prices=(scenario.allow_negative_hourly_prices),
    )

    report = validate_project_scenario_data(
        scenario=scenario,
        consumption_df=consumption_df,
        price_df=price_df,
    )

    print()
    print(format_validation_report(report))


if __name__ == "__main__":
    main()
