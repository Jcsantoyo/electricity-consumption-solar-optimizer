import os

import config

from data_loader import load_consumption_data
from optimization import (
    run_economic_grid_search,
    get_best_scenario_by_payback,
    get_best_scenario_by_self_sufficiency,
    print_scenario_summary,
    print_scenario_comparison,
    build_scenario_summary_text
)
from visualization import plot_payback_by_solar_and_battery

def ensure_output_directories() -> None:
    os.makedirs("reports", exist_ok=True)
    os.makedirs("images", exist_ok=True)

def main() -> None:

    ensure_output_directories()
    
    file_path = config.CONSUMPTION_DATA_PATH

    df_consumption = load_consumption_data(file_path)

    consumption_kwh = df_consumption["consumption_kwh"].tolist()
    timestamps = df_consumption["datetime"]

    solar_peak_powers_kw = config.SOLAR_PEAK_POWERS_KW
    battery_capacities_kwh = config.BATTERY_CAPACITIES_KWH

    battery_efficiency = config.BATTERY_EFFICIENCY
    max_charge_power_kw = config.MAX_CHARGE_POWER_KW
    max_discharge_power_kw = config.MAX_DISCHARGE_POWER_KW
    initial_battery_state_kwh = config.INITIAL_BATTERY_STATE_KWH

    electricity_price_eur_per_kwh = config.ELECTRICITY_PRICE_EUR_PER_KWH
    surplus_compensation_eur_per_kwh = config.SURPLUS_COMPENSATION_EUR_PER_KWH

    fixed_installation_cost = config.FIXED_INSTALLATION_COST_EUR
    solar_cost_per_kw = config.SOLAR_COST_EUR_PER_KW
    battery_cost_per_kwh = config.BATTERY_COST_EUR_PER_KWH

    simulation_days = config.SIMULATION_DAYS
    days_per_year = config.DAYS_PER_YEAR

    results_df = run_economic_grid_search(
        consumption_kwh,
        timestamps,
        solar_peak_powers_kw,
        battery_capacities_kwh,
        battery_efficiency,
        max_charge_power_kw,
        max_discharge_power_kw,
        initial_battery_state_kwh,
        electricity_price_eur_per_kwh,
        surplus_compensation_eur_per_kwh,
        fixed_installation_cost,
        solar_cost_per_kw,
        battery_cost_per_kwh,
        simulation_days,
        days_per_year=days_per_year
    )

    results_output_path = config.GRID_SEARCH_RESULTS_PATH
    results_df.to_csv(results_output_path, index=False)


    best_payback_scenario = get_best_scenario_by_payback(results_df)
    best_self_sufficiency_scenario = get_best_scenario_by_self_sufficiency(results_df)

    summary_text = build_scenario_summary_text(
        best_payback_scenario,
        best_self_sufficiency_scenario
    )

    summary_output_path = config.SUMMARY_REPORT_PATH

    with open(summary_output_path, "w", encoding="utf-8") as file:
        file.write(summary_text)


    print("\nElectricity Consumption Solar Optimizer")
    print(f"Input file: {file_path}")
    print(f"Number of hours: {len(df_consumption)}")
    print(f"Results saved to: {results_output_path}")
    print(f"Results saved to: {results_output_path}")
    print(f"Summary saved to: {summary_output_path}")

    print_scenario_summary(
        "Best scenario by payback",
        best_payback_scenario
    )

    print_scenario_summary(
        "Best scenario by self-sufficiency",
        best_self_sufficiency_scenario
    )

    print_scenario_comparison(
        best_payback_scenario,
        best_self_sufficiency_scenario
    )

    plot_payback_by_solar_and_battery(
        results_df,
        battery_capacities_kwh,
        config.PAYBACK_PLOT_PATH    
    )


if __name__ == "__main__":
    main()