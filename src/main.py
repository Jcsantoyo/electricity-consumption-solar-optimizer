from data_loader import load_consumption_data
from optimization import (
    run_economic_grid_search,
    get_best_scenario_by_payback,
    get_best_scenario_by_self_sufficiency,
    print_scenario_summary,
    print_scenario_comparison
)
from visualization import plot_payback_by_solar_and_battery


def main() -> None:
    file_path = "data/simulated/synthetic_consumption_30_days.csv"

    df_consumption = load_consumption_data(file_path)

    consumption_kwh = df_consumption["consumption_kwh"].tolist()
    timestamps = df_consumption["datetime"]

    solar_peak_powers_kw = [0.5, 1.0, 1.5, 2.0, 3.0]
    battery_capacities_kwh = [0, 0.5, 1.0, 2.0, 3.0, 5.0]

    battery_efficiency = 0.90
    max_charge_power_kw = 1.0
    max_discharge_power_kw = 1.0
    initial_battery_state_kwh = 0.0

    electricity_price_eur_per_kwh = 0.20
    surplus_compensation_eur_per_kwh = 0.07

    fixed_installation_cost = 800.0
    solar_cost_per_kw = 900.0
    battery_cost_per_kwh = 500.0

    simulation_days = 30
    days_per_year = 365

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

    best_payback_scenario = get_best_scenario_by_payback(results_df)
    best_self_sufficiency_scenario = get_best_scenario_by_self_sufficiency(
        results_df
    )

    print("\nElectricity Consumption Solar Optimizer")
    print(f"Input file: {file_path}")
    print(f"Number of hours: {len(df_consumption)}")

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
        "images/main_payback_grid_search.png"
    )


if __name__ == "__main__":
    main()