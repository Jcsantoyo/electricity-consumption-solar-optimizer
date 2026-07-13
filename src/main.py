import os

import config

from data_loader import load_consumption_data
from optimization import (
    run_economic_grid_search,
    get_best_scenario_by_payback,
    get_best_scenario_by_self_sufficiency,
    print_scenario_summary,
    print_scenario_comparison,
    build_scenario_summary_text,
    build_best_scenarios_dataframe,
    build_outputs_index_text,
)
from visualization import (
    plot_payback_by_solar_and_battery,
    plot_self_sufficiency_by_solar_and_battery,
    plot_best_scenarios_comparison,
    plot_best_scenario_timeseries,
    plot_battery_state_over_time,
    plot_cumulative_energy_flows,
)

from solar import generate_solar_profile_for_timestamps
from battery import simulate_battery

from solar_data_loader import load_pvgis_solar_data, get_pvgis_generation_for_timestamps

from price_loader import (
    load_hourly_prices_if_enabled,
    validate_hourly_price_coverage
)

def ensure_output_directories() -> None:
    os.makedirs("reports", exist_ok=True)
    os.makedirs("images", exist_ok=True)


def main() -> None:
    ensure_output_directories()

    file_path = config.CONSUMPTION_DATA_PATH

    try:
        df_consumption = load_consumption_data(file_path)
    except FileNotFoundError:
        print(f"\nInput data file not found: {file_path}")
        print("Please generate the synthetic dataset first by running:")
        print("python scripts/generate_synthetic_consumption.py")
        return
    except ValueError as error:
        print(f"\nInvalid input data file: {file_path}")
        print(error)
        return

    simulation_days = (
        df_consumption["datetime"].max() - df_consumption["datetime"].min()
    ).days + 1

    tariff_profile = config.get_active_tariff_profile()

    consumption_kwh = df_consumption["consumption_kwh"].tolist()
    timestamps = df_consumption["datetime"]

    pvgis_df = None

    if config.USE_PVGIS_SOLAR_DATA:
        try:
            pvgis_df = load_pvgis_solar_data(config.PVGIS_SOLAR_DATA_PATH)
        except FileNotFoundError:
            print(f"\nPVGIS solar data file not found: {config.PVGIS_SOLAR_DATA_PATH}")
            print("Please download it first by running:")
            print("python scripts/download_pvgis_data.py")
            return
        except ValueError as error:
            print(f"\nInvalid PVGIS solar data file: {config.PVGIS_SOLAR_DATA_PATH}")
            print(error)
            return
        

    hourly_price_df = load_hourly_prices_if_enabled(
        use_hourly_price_data=config.USE_HOURLY_PRICE_DATA,
        file_path=config.HOURLY_PRICE_DATA_PATH,
        allow_negative_prices=config.HOURLY_PRICE_DATA_PATH
    )

    if hourly_price_df is None:
        print("Hourly electricity price data: disabled")
    else:
        validate_hourly_price_coverage(
            consumption_df=df_consumption,
            price_df=hourly_price_df,
        )

        print(
            "Hourly electricity price data loaded: "
            f"{len(hourly_price_df)} rows"
        )

    battery_capacities_kwh = config.BATTERY_CAPACITIES_KWH

    battery_efficiency = config.BATTERY_EFFICIENCY
    max_charge_power_kw = config.MAX_CHARGE_POWER_KW
    max_discharge_power_kw = config.MAX_DISCHARGE_POWER_KW
    initial_battery_state_kwh = config.INITIAL_BATTERY_STATE_KWH

    results_df = run_economic_grid_search(
        consumption_df=df_consumption,
        solar_peak_powers_kw=config.SOLAR_PEAK_POWERS_KW,
        battery_capacities_kwh=config.BATTERY_CAPACITIES_KWH,
        battery_efficiency=config.BATTERY_EFFICIENCY,
        max_charge_power_kw=config.MAX_CHARGE_POWER_KW,
        max_discharge_power_kw=config.MAX_DISCHARGE_POWER_KW,
        initial_battery_state_kwh=config.INITIAL_BATTERY_STATE_KWH,
        fixed_installation_cost=config.FIXED_INSTALLATION_COST_EUR,
        solar_cost_per_kw=config.SOLAR_COST_EUR_PER_KW,
        battery_cost_per_kwh=config.BATTERY_COST_EUR_PER_KWH,
        peak_price=tariff_profile["peak_price_eur_per_kwh"],
        flat_price=tariff_profile["flat_price_eur_per_kwh"],
        off_peak_price=tariff_profile["off_peak_price_eur_per_kwh"],
        surplus_compensation_price=tariff_profile["surplus_compensation_eur_per_kwh"],
        contracted_power_kw=tariff_profile["contracted_power_kw"],
        power_price_eur_per_kw_year=tariff_profile["power_price_eur_per_kw_year"],
        simulation_days=simulation_days,
        pvgis_df=pvgis_df,
        hourly_price_df=hourly_price_df,
        allow_negative_hourly_prices=config.ALLOW_NEGATIVE_HOURLY_PRICES
    )

    results_output_path = config.GRID_SEARCH_RESULTS_PATH
    results_df.to_csv(results_output_path, index=False)

    best_payback_scenario = get_best_scenario_by_payback(results_df)
    best_self_sufficiency_scenario = get_best_scenario_by_self_sufficiency(results_df)

    if pvgis_df is None:
        solar_data_source = "Synthetic solar profile"
    else:
        solar_data_source = f"PVGIS solar data ({config.PVGIS_SOLAR_DATA_PATH})"

    summary_text = build_scenario_summary_text(
        best_payback_scenario, best_self_sufficiency_scenario, solar_data_source
    )

    summary_output_path = config.SUMMARY_REPORT_PATH

    with open(summary_output_path, "w", encoding="utf-8") as file:
        file.write(summary_text)

    best_scenarios_df = build_best_scenarios_dataframe(
        best_payback_scenario, best_self_sufficiency_scenario
    )

    best_peak_power_kw = best_payback_scenario["solar_peak_power_kw"]
    best_battery_capacity_kwh = best_payback_scenario["battery_capacity_kwh"]

    if pvgis_df is None:
        best_solar_generation_kwh = generate_solar_profile_for_timestamps(
            timestamps, best_peak_power_kw
        )
    else:
        best_solar_generation_kwh = get_pvgis_generation_for_timestamps(
            pvgis_df, timestamps, best_peak_power_kw
        )

    best_battery_results = simulate_battery(
        consumption_kwh,
        best_solar_generation_kwh,
        best_battery_capacity_kwh,
        battery_efficiency=battery_efficiency,
        max_charge_power_kw=max_charge_power_kw,
        max_discharge_power_kw=max_discharge_power_kw,
        initial_battery_state_kwh=initial_battery_state_kwh,
    )

    best_timeseries_df = df_consumption.copy()

    best_timeseries_df["solar_generation_kwh"] = best_solar_generation_kwh
    best_timeseries_df["self_consumed_kwh"] = best_battery_results["self_consumed_kwh"]
    best_timeseries_df["battery_charge_kwh"] = best_battery_results[
        "battery_charge_kwh"
    ]
    best_timeseries_df["battery_discharge_kwh"] = best_battery_results[
        "battery_discharge_kwh"
    ]
    best_timeseries_df["grid_import_kwh"] = best_battery_results["grid_import_kwh"]
    best_timeseries_df["solar_surplus_kwh"] = best_battery_results["solar_surplus_kwh"]
    best_timeseries_df["battery_state_kwh"] = best_battery_results["battery_state_kwh"]

    best_timeseries_output_path = config.BEST_SCENARIO_TIMESERIES_PATH
    best_timeseries_df.to_csv(best_timeseries_output_path, index=False)

    outputs_index_text = build_outputs_index_text(solar_data_source)

    outputs_index_path = config.OUTPUTS_INDEX_PATH

    with open(outputs_index_path, "w", encoding="utf-8") as file:
        file.write(outputs_index_text)

    best_scenarios_output_path = config.BEST_SCENARIOS_PATH
    best_scenarios_df.to_csv(best_scenarios_output_path, index=False)

    print("\nElectricity Consumption Solar Optimizer")
    print(f"Input file: {file_path}")
    if pvgis_df is None:
        print("Solar data source: synthetic profile")
    else:
        print(f"Solar data source: PVGIS ({config.PVGIS_SOLAR_DATA_PATH})")
    print(f"Tariff profile: {config.ACTIVE_TARIFF_PROFILE}")
    print(f"Number of hours: {len(df_consumption)}")
    print(f"Results saved to: {results_output_path}")
    print(f"Summary saved to: {summary_output_path}")
    print(f"Best scenarios saved to: {best_scenarios_output_path}")
    print(f"Payback plot saved to: {config.PAYBACK_PLOT_PATH}")
    print(f"Self-sufficiency plot saved to: {config.SELF_SUFFICIENCY_PLOT_PATH}")
    print(
        "Best scenarios comparison plot saved to: "
        f"{config.BEST_SCENARIOS_COMPARISON_PLOT_PATH}"
    )
    print(
        "Best scenario timeseries plot saved to: "
        f"{config.BEST_SCENARIO_TIMESERIES_PLOT_PATH}"
    )
    print(f"Best scenario timeseries saved to: {best_timeseries_output_path}")

    print(
        "Best scenario battery state plot saved to: "
        f"{config.BEST_SCENARIO_BATTERY_STATE_PLOT_PATH}"
    )

    print(
        "Best scenario cumulative energy plot saved to: "
        f"{config.BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH}"
    )
    print(f"Outputs index saved to: {outputs_index_path}")

    print_scenario_summary("Best scenario by payback", best_payback_scenario)

    print_scenario_summary(
        "Best scenario by self-sufficiency", best_self_sufficiency_scenario
    )

    print_scenario_comparison(best_payback_scenario, best_self_sufficiency_scenario)

    plot_payback_by_solar_and_battery(
        results_df, battery_capacities_kwh, config.PAYBACK_PLOT_PATH
    )

    plot_self_sufficiency_by_solar_and_battery(
        results_df, battery_capacities_kwh, config.SELF_SUFFICIENCY_PLOT_PATH
    )

    plot_best_scenarios_comparison(
        best_scenarios_df, config.BEST_SCENARIOS_COMPARISON_PLOT_PATH
    )

    plot_best_scenario_timeseries(
        best_timeseries_df, config.BEST_SCENARIO_TIMESERIES_PLOT_PATH
    )

    plot_battery_state_over_time(
        best_timeseries_df, config.BEST_SCENARIO_BATTERY_STATE_PLOT_PATH
    )

    plot_cumulative_energy_flows(
        best_timeseries_df, config.BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH
    )


if __name__ == "__main__":
    main()
