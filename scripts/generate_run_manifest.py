import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

import config
from data_loader import load_consumption_data
from price_loader import load_hourly_prices_if_enabled
from run_manifest import build_run_manifest, write_run_manifest


def collect_generated_output_paths() -> list[str]:
    return [
        path
        for path in config.OUTPUT_PATHS.all_output_paths()
        if Path(path).is_file() and path != config.RUN_MANIFEST_PATH
    ]


def main() -> None:
    config.OUTPUT_PATHS.create_directories()

    scenario = config.ACTIVE_PROJECT_SCENARIO
    consumption_df = load_consumption_data(scenario.consumption_data_path)

    price_df = load_hourly_prices_if_enabled(
        use_hourly_price_data=scenario.uses_hourly_prices,
        file_path=scenario.hourly_price_data_path,
        allow_negative_prices=scenario.allow_negative_hourly_prices,
    )

    manifest = build_run_manifest(
        scenario=scenario,
        consumption_df=consumption_df,
        price_df=price_df,
        output_paths=collect_generated_output_paths(),
        solar_peak_powers_kw=config.SOLAR_PEAK_POWERS_KW,
        battery_capacities_kwh=config.BATTERY_CAPACITIES_KWH,
        battery_efficiency=config.BATTERY_EFFICIENCY,
        max_charge_power_kw=config.MAX_CHARGE_POWER_KW,
        max_discharge_power_kw=config.MAX_DISCHARGE_POWER_KW,
        initial_battery_state_kwh=config.INITIAL_BATTERY_STATE_KWH,
        days_per_year=config.DAYS_PER_YEAR,
    )

    write_run_manifest(
        manifest=manifest,
        output_path=config.RUN_MANIFEST_PATH,
    )

    print("\nRun manifest generated")
    print(f"Output file: {config.RUN_MANIFEST_PATH}")


if __name__ == "__main__":
    main()
