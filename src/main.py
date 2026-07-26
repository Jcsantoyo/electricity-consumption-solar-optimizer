import config

from battery import simulate_battery
from data_loader import load_consumption_data
from optimization import (
    build_best_scenarios_dataframe,
    build_outputs_index_text,
    build_scenario_summary_text,
    get_best_scenario_by_net_present_value,
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
    plot_financial_sensitivity_irr,
    plot_financial_sensitivity_npv,
    plot_financial_sensitivity_payback,
)
from financial_sensitivity import (
    financial_sensitivity_results_to_dataframe,
    run_financial_sensitivity_analysis,
)


def main() -> None:
    config.OUTPUT_PATHS.create_directories()

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

    try:
        hourly_price_df = load_hourly_prices_if_enabled(
            use_hourly_price_data=(config.USE_HOURLY_PRICE_DATA),
            file_path=(config.HOURLY_PRICE_DATA_PATH),
            allow_negative_prices=(config.ALLOW_NEGATIVE_HOURLY_PRICES),
        )

        if hourly_price_df is None:
            print("Hourly electricity price data: disabled")
        else:
            validate_hourly_price_coverage(
                consumption_df=df_consumption,
                price_df=hourly_price_df,
            )

            print(f"Hourly electricity price data loaded: {len(hourly_price_df)} rows")

        price_model = build_electricity_price_model(
            scenario=(config.ACTIVE_PROJECT_SCENARIO),
            tariff_profile=tariff_profile,
            hourly_price_df=hourly_price_df,
        )

    except FileNotFoundError:
        print("\nHourly electricity price data file not found")
        print(f"Expected file: {config.HOURLY_PRICE_DATA_PATH}")
        return
    except ValueError as error:
        print("\nInvalid electricity price configuration or data")
        print(error)
        return

    electricity_price_mode = build_electricity_price_mode_description(
        price_mode=(config.ACTIVE_PROJECT_SCENARIO.price_mode),
        hourly_price_data_path=(config.HOURLY_PRICE_DATA_PATH),
        tariff_profile_name=(config.ACTIVE_TARIFF_PROFILE),
    )

    battery_capacities_kwh = config.BATTERY_CAPACITIES_KWH

    battery_efficiency = config.BATTERY_EFFICIENCY

    max_charge_power_kw = config.MAX_CHARGE_POWER_KW

    max_discharge_power_kw = config.MAX_DISCHARGE_POWER_KW

    initial_battery_state_kwh = config.INITIAL_BATTERY_STATE_KWH

    financial_assumptions = config.get_active_financial_assumptions()

    results_df = run_economic_grid_search(
        consumption_df=df_consumption,
        solar_peak_powers_kw=(config.SOLAR_PEAK_POWERS_KW),
        battery_capacities_kwh=(config.BATTERY_CAPACITIES_KWH),
        battery_efficiency=(config.BATTERY_EFFICIENCY),
        max_charge_power_kw=(config.MAX_CHARGE_POWER_KW),
        max_discharge_power_kw=(config.MAX_DISCHARGE_POWER_KW),
        initial_battery_state_kwh=(config.INITIAL_BATTERY_STATE_KWH),
        fixed_installation_cost=(config.FIXED_INSTALLATION_COST_EUR),
        solar_cost_per_kw=(config.SOLAR_COST_EUR_PER_KW),
        battery_cost_per_kwh=(config.BATTERY_COST_EUR_PER_KWH),
        price_model=price_model,
        simulation_days=simulation_days,
        pvgis_df=pvgis_df,
        financial_assumptions=financial_assumptions,
    )

    results_output_path = config.GRID_SEARCH_RESULTS_PATH

    results_df.to_csv(
        results_output_path,
        index=False,
    )

    best_payback_scenario = get_best_scenario_by_payback(results_df)

    best_self_sufficiency_scenario = get_best_scenario_by_self_sufficiency(results_df)

    best_net_present_value_scenario = get_best_scenario_by_net_present_value(results_df)

    financial_sensitivity_results = run_financial_sensitivity_analysis(
        initial_investment_cost_eur=float(
            best_net_present_value_scenario["investment_cost_eur"]
        ),
        first_year_energy_savings_eur=float(
            best_net_present_value_scenario["annual_savings_eur"]
        ),
        battery_capacity_kwh=float(
            best_net_present_value_scenario["battery_capacity_kwh"]
        ),
        battery_cost_per_kwh=config.BATTERY_COST_EUR_PER_KWH,
        cases=config.get_financial_sensitivity_cases(),
    )

    financial_sensitivity_df = financial_sensitivity_results_to_dataframe(
        financial_sensitivity_results
    )

    financial_sensitivity_df.insert(
        0,
        "solar_peak_power_kw",
        float(best_net_present_value_scenario["solar_peak_power_kw"]),
    )

    financial_sensitivity_df.insert(
        1,
        "battery_capacity_kwh",
        float(best_net_present_value_scenario["battery_capacity_kwh"]),
    )

    financial_sensitivity_df.insert(
        2,
        "initial_investment_cost_eur",
        float(best_net_present_value_scenario["investment_cost_eur"]),
    )

    financial_sensitivity_df.insert(
        3,
        "first_year_energy_savings_eur",
        float(best_net_present_value_scenario["annual_savings_eur"]),
    )

    financial_sensitivity_df.to_csv(
        config.FINANCIAL_SENSITIVITY_RESULTS_PATH,
        index=False,
    )

    financial_sensitivity_npv_created = plot_financial_sensitivity_npv(
        sensitivity_df=financial_sensitivity_df,
        output_path=config.FINANCIAL_SENSITIVITY_NPV_PLOT_PATH,
    )

    financial_sensitivity_payback_created = plot_financial_sensitivity_payback(
        sensitivity_df=financial_sensitivity_df,
        output_path=(config.FINANCIAL_SENSITIVITY_PAYBACK_PLOT_PATH),
    )

    financial_sensitivity_irr_created = plot_financial_sensitivity_irr(
        sensitivity_df=financial_sensitivity_df,
        output_path=config.FINANCIAL_SENSITIVITY_IRR_PLOT_PATH,
    )

    if pvgis_df is None:
        solar_data_source = "Synthetic solar profile"
    else:
        solar_data_source = f"PVGIS solar data ({config.PVGIS_SOLAR_DATA_PATH})"

    summary_text = build_scenario_summary_text(
        best_payback_scenario,
        best_self_sufficiency_scenario,
        solar_data_source,
        electricity_price_mode,
        best_net_present_value_scenario,
    )

    summary_output_path = config.SUMMARY_REPORT_PATH

    with open(
        summary_output_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(summary_text)

    best_scenarios_df = build_best_scenarios_dataframe(
        best_payback_scenario,
        best_self_sufficiency_scenario,
        best_net_present_value_scenario,
    )

    best_peak_power_kw = best_payback_scenario["solar_peak_power_kw"]

    best_battery_capacity_kwh = best_payback_scenario["battery_capacity_kwh"]

    if pvgis_df is None:
        best_solar_generation_kwh = generate_solar_profile_for_timestamps(
            timestamps,
            best_peak_power_kw,
        )
    else:
        best_solar_generation_kwh = get_pvgis_generation_for_timestamps(
            pvgis_df,
            timestamps,
            best_peak_power_kw,
        )

    best_battery_results = simulate_battery(
        consumption_kwh,
        best_solar_generation_kwh,
        best_battery_capacity_kwh,
        battery_efficiency=(battery_efficiency),
        max_charge_power_kw=(max_charge_power_kw),
        max_discharge_power_kw=(max_discharge_power_kw),
        initial_battery_state_kwh=(initial_battery_state_kwh),
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

    best_timeseries_df.to_csv(
        best_timeseries_output_path,
        index=False,
    )

    outputs_index_text = build_outputs_index_text(
        solar_data_source,
        electricity_price_mode,
    )

    outputs_index_path = config.OUTPUTS_INDEX_PATH

    with open(
        outputs_index_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(outputs_index_text)

    best_scenarios_output_path = config.BEST_SCENARIOS_PATH

    best_scenarios_df.to_csv(
        best_scenarios_output_path,
        index=False,
    )

    print("\nElectricity Consumption Solar Optimizer")

    print(f"Input file: {file_path}")

    if pvgis_df is None:
        print("Solar data source: synthetic profile")
    else:
        print(f"Solar data source: PVGIS ({config.PVGIS_SOLAR_DATA_PATH})")

    print(f"Electricity price mode: {electricity_price_mode}")

    print(f"Number of hours: {len(df_consumption)}")

    print(f"Results saved to: {results_output_path}")

    print(f"Summary saved to: {summary_output_path}")

    print(f"Best scenarios saved to: {best_scenarios_output_path}")

    print(f"Payback plot saved to: {config.PAYBACK_PLOT_PATH}")

    print(f"Self-sufficiency plot saved to: {config.SELF_SUFFICIENCY_PLOT_PATH}")

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

    print(f"Best scenario timeseries saved to: {best_timeseries_output_path}")

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
        f"Financial sensitivity results saved to: {config.FINANCIAL_SENSITIVITY_RESULTS_PATH}"
    )

    if financial_sensitivity_npv_created:
        print(
            "Financial sensitivity NPV plot saved to: "
            f"{config.FINANCIAL_SENSITIVITY_NPV_PLOT_PATH}"
        )

    if financial_sensitivity_payback_created:
        print(
            "Financial sensitivity payback plot saved to: "
            f"{config.FINANCIAL_SENSITIVITY_PAYBACK_PLOT_PATH}"
        )
    else:
        print(
            "Financial sensitivity payback plot not generated: "
            "no discounted payback values available"
        )

    if financial_sensitivity_irr_created:
        print(
            "Financial sensitivity IRR plot saved to: "
            f"{config.FINANCIAL_SENSITIVITY_IRR_PLOT_PATH}"
        )
    else:
        print(
            "Financial sensitivity IRR plot not generated: "
            "no internal rate of return values available"
        )

    print(f"Outputs index saved to: {outputs_index_path}")

    print_scenario_summary(
        "Best scenario by payback",
        best_payback_scenario,
    )

    print_scenario_summary(
        "Best scenario by self-sufficiency",
        best_self_sufficiency_scenario,
    )

    print_scenario_summary(
        "Best scenario by net present value",
        best_net_present_value_scenario,
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
