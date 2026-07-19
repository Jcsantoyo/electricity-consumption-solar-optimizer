import config

from battery import simulate_battery
from data_loader import load_consumption_data
from optimization import (
    build_best_scenarios_dataframe,
    build_outputs_index_text,
    build_scenario_summary_text,
    get_best_scenario_by_payback,
    get_best_scenario_by_self_sufficiency,
    print_scenario_comparison,
    print_scenario_summary,
    run_economic_grid_search,
)
from price_loader import (
    load_hourly_prices_if_enabled,
    validate_hourly_price_coverage,
)
from price_mode import (
    build_electricity_price_mode_description,
)
from price_model_factory import (
    build_electricity_price_model,
)
from solar import generate_solar_profile_for_timestamps
from solar_data_loader import (
    get_pvgis_generation_for_timestamps,
    load_pvgis_solar_data,
)
from visualization import (
    plot_battery_state_over_time,
    plot_best_scenario_timeseries,
    plot_best_scenarios_comparison,
    plot_cumulative_energy_flows,
    plot_payback_by_solar_and_battery,
    plot_self_sufficiency_by_solar_and_battery,
)


def main() -> None:
    config.OUTPUT_PATHS.create_directories()

    file_path = config.CONSUMPTION_DATA_PATH

    try:
        df_consumption = load_consumption_data(
            file_path
        )
    except FileNotFoundError:
        print(
            "\nInput data file not found: "
            f"{file_path}"
        )
        print(
            "Please generate the synthetic dataset "
            "first by running:"
        )
        print(
            "python "
            "scripts/generate_synthetic_consumption.py"
        )
        return
    except ValueError as error:
        print(
            "\nInvalid input data file: "
            f"{file_path}"
        )
        print(error)
        return

    simulation_days = (
        (
            df_consumption["datetime"].max()
            - df_consumption["datetime"].min()
        ).days
        + 1
    )

    tariff_profile = (
        config.get_active_tariff_profile()
    )

    consumption_kwh = (
        df_consumption[
            "consumption_kwh"
        ].tolist()
    )

    timestamps = df_consumption["datetime"]

    pvgis_df = None

    if config.USE_PVGIS_SOLAR_DATA:
        try:
            pvgis_df = load_pvgis_solar_data(
                config.PVGIS_SOLAR_DATA_PATH
            )
        except FileNotFoundError:
            print(
                "\nPVGIS solar data file not found: "
                f"{config.PVGIS_SOLAR_DATA_PATH}"
            )
            print(
                "Please download it first by running:"
            )
            print(
                "python scripts/download_pvgis_data.py"
            )
            return
        except ValueError as error:
            print(
                "\nInvalid PVGIS solar data file: "
                f"{config.PVGIS_SOLAR_DATA_PATH}"
            )
            print(error)
            return

    try:
        hourly_price_df = (
            load_hourly_prices_if_enabled(
                use_hourly_price_data=(
                    config.USE_HOURLY_PRICE_DATA
                ),
                file_path=(
                    config.HOURLY_PRICE_DATA_PATH
                ),
                allow_negative_prices=(
                    config.ALLOW_NEGATIVE_HOURLY_PRICES
                ),
            )
        )

        if hourly_price_df is None:
            print(
                "Hourly electricity price data: "
                "disabled"
            )
        else:
            validate_hourly_price_coverage(
                consumption_df=df_consumption,
                price_df=hourly_price_df,
            )

            print(
                "Hourly electricity price data "
                "loaded: "
                f"{len(hourly_price_df)} rows"
            )

        price_model = (
            build_electricity_price_model(
                scenario=(
                    config.ACTIVE_PROJECT_SCENARIO
                ),
                tariff_profile=tariff_profile,
                hourly_price_df=hourly_price_df,
            )
        )

    except FileNotFoundError:
        print(
            "\nHourly electricity price data "
            "file not found"
        )
        print(
            "Expected file: "
            f"{config.HOURLY_PRICE_DATA_PATH}"
        )
        return
    except ValueError as error:
        print(
            "\nInvalid electricity price "
            "configuration or data"
        )
        print(error)
        return

    electricity_price_mode = (
        build_electricity_price_mode_description(
            price_mode=(
                config.ACTIVE_PROJECT_SCENARIO
                .price_mode
            ),
            hourly_price_data_path=(
                config.HOURLY_PRICE_DATA_PATH
            ),
            tariff_profile_name=(
                config.ACTIVE_TARIFF_PROFILE
            ),
        )
    )

    battery_capacities_kwh = (
        config.BATTERY_CAPACITIES_KWH
    )

    battery_efficiency = (
        config.BATTERY_EFFICIENCY
    )

    max_charge_power_kw = (
        config.MAX_CHARGE_POWER_KW
    )

    max_discharge_power_kw = (
        config.MAX_DISCHARGE_POWER_KW
    )

    initial_battery_state_kwh = (
        config.INITIAL_BATTERY_STATE_KWH
    )

    results_df = run_economic_grid_search(
        consumption_df=df_consumption,
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
        fixed_installation_cost=(
            config.FIXED_INSTALLATION_COST_EUR
        ),
        solar_cost_per_kw=(
            config.SOLAR_COST_EUR_PER_KW
        ),
        battery_cost_per_kwh=(
            config.BATTERY_COST_EUR_PER_KWH
        ),
        price_model=price_model,
        simulation_days=simulation_days,
        pvgis_df=pvgis_df,
    )

    results_output_path = (
        config.GRID_SEARCH_RESULTS_PATH
    )

    results_df.to_csv(
        results_output_path,
        index=False,
    )

    best_payback_scenario = (
        get_best_scenario_by_payback(
            results_df
        )
    )

    best_self_sufficiency_scenario = (
        get_best_scenario_by_self_sufficiency(
            results_df
        )
    )

    if pvgis_df is None:
        solar_data_source = (
            "Synthetic solar profile"
        )
    else:
        solar_data_source = (
            "PVGIS solar data "
            f"({config.PVGIS_SOLAR_DATA_PATH})"
        )

    summary_text = (
        build_scenario_summary_text(
            best_payback_scenario,
            best_self_sufficiency_scenario,
            solar_data_source,
            electricity_price_mode,
        )
    )

    summary_output_path = (
        config.SUMMARY_REPORT_PATH
    )

    with open(
        summary_output_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            summary_text
        )

    best_scenarios_df = (
        build_best_scenarios_dataframe(
            best_payback_scenario,
            best_self_sufficiency_scenario,
        )
    )

    best_peak_power_kw = (
        best_payback_scenario[
            "solar_peak_power_kw"
        ]
    )

    best_battery_capacity_kwh = (
        best_payback_scenario[
            "battery_capacity_kwh"
        ]
    )

    if pvgis_df is None:
        best_solar_generation_kwh = (
            generate_solar_profile_for_timestamps(
                timestamps,
                best_peak_power_kw,
            )
        )
    else:
        best_solar_generation_kwh = (
            get_pvgis_generation_for_timestamps(
                pvgis_df,
                timestamps,
                best_peak_power_kw,
            )
        )

    best_battery_results = simulate_battery(
        consumption_kwh,
        best_solar_generation_kwh,
        best_battery_capacity_kwh,
        battery_efficiency=(
            battery_efficiency
        ),
        max_charge_power_kw=(
            max_charge_power_kw
        ),
        max_discharge_power_kw=(
            max_discharge_power_kw
        ),
        initial_battery_state_kwh=(
            initial_battery_state_kwh
        ),
    )

    best_timeseries_df = (
        df_consumption.copy()
    )

    best_timeseries_df[
        "solar_generation_kwh"
    ] = best_solar_generation_kwh

    best_timeseries_df[
        "self_consumed_kwh"
    ] = best_battery_results[
        "self_consumed_kwh"
    ]

    best_timeseries_df[
        "battery_charge_kwh"
    ] = best_battery_results[
        "battery_charge_kwh"
    ]

    best_timeseries_df[
        "battery_discharge_kwh"
    ] = best_battery_results[
        "battery_discharge_kwh"
    ]

    best_timeseries_df[
        "grid_import_kwh"
    ] = best_battery_results[
        "grid_import_kwh"
    ]

    best_timeseries_df[
        "solar_surplus_kwh"
    ] = best_battery_results[
        "solar_surplus_kwh"
    ]

    best_timeseries_df[
        "battery_state_kwh"
    ] = best_battery_results[
        "battery_state_kwh"
    ]

    best_timeseries_output_path = (
        config.BEST_SCENARIO_TIMESERIES_PATH
    )

    best_timeseries_df.to_csv(
        best_timeseries_output_path,
        index=False,
    )

    outputs_index_text = (
        build_outputs_index_text(
            solar_data_source,
            electricity_price_mode,
        )
    )

    outputs_index_path = (
        config.OUTPUTS_INDEX_PATH
    )

    with open(
        outputs_index_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            outputs_index_text
        )

    best_scenarios_output_path = (
        config.BEST_SCENARIOS_PATH
    )

    best_scenarios_df.to_csv(
        best_scenarios_output_path,
        index=False,
    )

    print(
        "\nElectricity Consumption Solar Optimizer"
    )

    print(
        f"Input file: {file_path}"
    )

    if pvgis_df is None:
        print(
            "Solar data source: synthetic profile"
        )
    else:
        print(
            "Solar data source: PVGIS "
            f"({config.PVGIS_SOLAR_DATA_PATH})"
        )

    print(
        "Electricity price mode: "
        f"{electricity_price_mode}"
    )

    print(
        "Number of hours: "
        f"{len(df_consumption)}"
    )

    print(
        "Results saved to: "
        f"{results_output_path}"
    )

    print(
        "Summary saved to: "
        f"{summary_output_path}"
    )

    print(
        "Best scenarios saved to: "
        f"{best_scenarios_output_path}"
    )

    print(
        "Payback plot saved to: "
        f"{config.PAYBACK_PLOT_PATH}"
    )

    print(
        "Self-sufficiency plot saved to: "
        f"{config.SELF_SUFFICIENCY_PLOT_PATH}"
    )

    print(
        "Best scenarios comparison plot "
        "saved to: "
        f"{config.BEST_SCENARIOS_COMPARISON_PLOT_PATH}"
    )

    print(
        "Best scenario timeseries plot "
        "saved to: "
        f"{config.BEST_SCENARIO_TIMESERIES_PLOT_PATH}"
    )

    print(
        "Best scenario timeseries saved to: "
        f"{best_timeseries_output_path}"
    )

    print(
        "Best scenario battery state plot "
        "saved to: "
        f"{config.BEST_SCENARIO_BATTERY_STATE_PLOT_PATH}"
    )

    print(
        "Best scenario cumulative energy "
        "plot saved to: "
        f"{config.BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH}"
    )

    print(
        "Outputs index saved to: "
        f"{outputs_index_path}"
    )

    print_scenario_summary(
        "Best scenario by payback",
        best_payback_scenario,
    )

    print_scenario_summary(
        "Best scenario by self-sufficiency",
        best_self_sufficiency_scenario,
    )

    print_scenario_comparison(
        best_payback_scenario,
        best_self_sufficiency_scenario,
    )

    plot_payback_by_solar_and_battery(
        results_df,
        battery_capacities_kwh,
        config.PAYBACK_PLOT_PATH,
    )

    plot_self_sufficiency_by_solar_and_battery(
        results_df,
        battery_capacities_kwh,
        config.SELF_SUFFICIENCY_PLOT_PATH,
    )

    plot_best_scenarios_comparison(
        best_scenarios_df,
        config.BEST_SCENARIOS_COMPARISON_PLOT_PATH,
    )

    plot_best_scenario_timeseries(
        best_timeseries_df,
        config.BEST_SCENARIO_TIMESERIES_PLOT_PATH,
    )

    plot_battery_state_over_time(
        best_timeseries_df,
        config.BEST_SCENARIO_BATTERY_STATE_PLOT_PATH,
    )

    plot_cumulative_energy_flows(
        best_timeseries_df,
        config.BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH,
    )


if __name__ == "__main__":
    main()