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
from run_manifest import (
    build_run_manifest,
    write_run_manifest,
)


def collect_generated_output_paths() -> list[str]:
    candidate_paths = [
        config.GRID_SEARCH_RESULTS_PATH,
        config.BEST_SCENARIOS_PATH,
        config.SUMMARY_REPORT_PATH,
        config.PAYBACK_PLOT_PATH,
        config.SELF_SUFFICIENCY_PLOT_PATH,
        config.BEST_SCENARIOS_COMPARISON_PLOT_PATH,
        config.BEST_SCENARIO_TIMESERIES_PLOT_PATH,
        config.BEST_SCENARIO_TIMESERIES_PATH,
        config.BEST_SCENARIO_BATTERY_STATE_PLOT_PATH,
        config.BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH,
        config.OUTPUTS_INDEX_PATH,
        "reports/configuration_summary.md",
        "reports/forecast_results.csv",
        "reports/forecast_feature_importance.csv",
        "reports/forecast_model_comparison.csv",
        "reports/forecasted_consumption_for_optimization.csv",
        "reports/forecast_optimization_results.csv",
        "reports/forecast_optimization_best_scenarios.csv",
        "reports/electricity_price_mode_comparison.csv",
        "reports/electricity_price_mode_comparison.md",
        "reports/final_results_summary.md",
        "images/forecast_model_comparison.png",
        "images/consumption_forecast_actual_vs_predicted.png",
        "images/forecast_feature_importance.png",
        "images/electricity_price_mode_comparison.png",
        "reports/historical_vs_forecast_optimization.csv",
        "images/historical_vs_forecast_payback.png",
        "images/historical_vs_forecast_savings.png",
        (
            "images/"
            "historical_vs_forecast_self_sufficiency.png"
        ),
        (
            "images/"
            "historical_vs_forecast_investment_cost.png"
        ),
        (
            "images/"
            "historical_vs_forecast_grid_import.png"
        ),
    ]

    return [
        path
        for path in candidate_paths
        if Path(path).is_file()
    ]


def main() -> None:
    scenario = config.ACTIVE_PROJECT_SCENARIO

    consumption_df = load_consumption_data(
        scenario.consumption_data_path
    )

    price_df = load_hourly_prices_if_enabled(
        use_hourly_price_data=(
            scenario.uses_hourly_prices
        ),
        file_path=(
            scenario.hourly_price_data_path
            or ""
        ),
        allow_negative_prices=(
            scenario.allow_negative_hourly_prices
        ),
    )

    manifest = build_run_manifest(
        scenario=scenario,
        consumption_df=consumption_df,
        price_df=price_df,
        output_paths=collect_generated_output_paths(),
        solar_peak_powers_kw=(
            config.SOLAR_PEAK_POWERS_KW
        ),
        battery_capacities_kwh=(
            config.BATTERY_CAPACITIES_KWH
        ),
        battery_efficiency=(
            config.BATTERY_EFFICIENCY
        ),
        max_charge_power_kw=(
            config.MAX_CHARGE_POWER_KW
        ),
        max_discharge_power_kw=(
            config.MAX_DISCHARGE_POWER_KW
        ),
        initial_battery_state_kwh=(
            config.INITIAL_BATTERY_STATE_KWH
        ),
        days_per_year=config.DAYS_PER_YEAR,
    )

    write_run_manifest(
        manifest=manifest,
        output_path=config.RUN_MANIFEST_PATH,
    )

    print()
    print("Run manifest generated")
    print(
        f"Output file: {config.RUN_MANIFEST_PATH}"
    )


if __name__ == "__main__":
    main()