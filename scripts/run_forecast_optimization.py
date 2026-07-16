import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

import config

from data_loader import load_consumption_data
from forecasting import run_consumption_forecast, build_forecasted_consumption_dataframe
from optimization import (
    run_economic_grid_search,
    get_best_scenario_by_payback,
    get_best_scenario_by_self_sufficiency,
    build_best_scenarios_dataframe,
)
from solar_data_loader import load_pvgis_solar_data
from price_loader import(
    load_hourly_prices_if_enabled,
    validate_hourly_price_coverage
) 

from price_mode import build_electricity_price_mode_description

def main() -> None:
    os.makedirs("reports", exist_ok=True)

    consumption_df = load_consumption_data(config.CONSUMPTION_DATA_PATH)

    forecast_results = run_consumption_forecast(consumption_df)

    forecasted_consumption_df = build_forecasted_consumption_dataframe(
        original_df=consumption_df, forecast_results_df=forecast_results["results_df"], forecast_mode=config.FORECAST_MODE
    )

    forecasted_consumption_path = "reports/forecasted_consumption_for_optimization.csv"

    forecasted_consumption_df.to_csv(forecasted_consumption_path, index=False)

    if config.USE_PVGIS_SOLAR_DATA:
        pvgis_df = load_pvgis_solar_data(config.PVGIS_SOLAR_DATA_PATH)
    else:
        pvgis_df = None
   
    hourly_price_df = load_hourly_prices_if_enabled(
        use_hourly_price_data=config.USE_HOURLY_PRICE_DATA,
        file_path=config.HOURLY_PRICE_DATA_PATH,
        allow_negative_prices=config.ALLOW_NEGATIVE_HOURLY_PRICES
    )

    if hourly_price_df is None:
        print("Hourly electricity price data: disabled")
    else:
        validate_hourly_price_coverage(
            consumption_df=forecasted_consumption_df,
            price_df=hourly_price_df,
        )

        print(
            "Hourly electricity price data loaded: "
            f"{len(hourly_price_df)} rows"
        )
        
    

    simulation_days = (
        forecasted_consumption_df["datetime"].max()
        - forecasted_consumption_df["datetime"].min()
    ).days + 1

    tariff_profile = config.get_active_tariff_profile()

    electricity_price_mode = (
        build_electricity_price_mode_description(
            use_hourly_price_data=config.ACTIVE_PROJECT_SCENARIO.price_mode,
            hourly_price_data_path=config.HOURLY_PRICE_DATA_PATH,
            tariff_profile_name=config.ACTIVE_TARIFF_PROFILE,
        )
    )

    print(
        "Electricity price mode: "
        f"{electricity_price_mode}"
    )

    results_df = run_economic_grid_search(
        consumption_df=forecasted_consumption_df,
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

    optimization_results_path = "reports/forecast_optimization_results.csv"

    results_df.to_csv(optimization_results_path, index=False)

    best_payback_scenario = get_best_scenario_by_payback(results_df)

    best_self_sufficiency_scenario = get_best_scenario_by_self_sufficiency(results_df)

    best_scenarios_df = build_best_scenarios_dataframe(
        best_payback_scenario, best_self_sufficiency_scenario
    )

    best_scenarios_path = "reports/forecast_optimization_best_scenarios.csv"

    best_scenarios_df.to_csv(best_scenarios_path, index=False)

    print("\nForecast-based optimization")
    print(f"Input file: {config.CONSUMPTION_DATA_PATH}")
    print(f"Electricity price mode: {electricity_price_mode}")
    print(f"Forecasted consumption saved to: {forecasted_consumption_path}")
    print(f"Optimization results saved to: {optimization_results_path}")
    print(f"Best scenarios saved to: {best_scenarios_path}")

    print("\nBest forecast-based scenario by payback:")
    print(f"Solar peak power: {best_payback_scenario['solar_peak_power_kw']:.2f} kW")
    print(f"Battery capacity: {best_payback_scenario['battery_capacity_kwh']:.2f} kWh")
    print(f"Annual savings: {best_payback_scenario['annual_savings_eur']:.2f} EUR/year")
    print(f"Payback: {best_payback_scenario['payback_years']:.2f} years")
    print(f"Self-sufficiency: {best_payback_scenario['self_sufficiency'] * 100:.2f}%")

    print("\nBest forecast-based scenario by self-sufficiency:")
    print(
        f"Solar peak power: "
        f"{best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW"
    )
    print(
        f"Battery capacity: "
        f"{best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh"
    )
    print(
        f"Annual savings: "
        f"{best_self_sufficiency_scenario['annual_savings_eur']:.2f} EUR/year"
    )
    print(f"Payback: {best_self_sufficiency_scenario['payback_years']:.2f} years")
    print(
        f"Self-sufficiency: "
        f"{best_self_sufficiency_scenario['self_sufficiency'] * 100:.2f}%"
    )


if __name__ == "__main__":
    main()
