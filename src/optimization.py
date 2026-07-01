import pandas as pd

from solar import generate_solar_profile_for_timestamps
from scenarios import compare_battery_scenario
from economics import (
    calculate_total_installation_cost,
    calculate_daily_grid_cost,
    calculate_daily_net_cost,
    calculate_simple_payback_years
)

def run_economic_grid_search(
    consumption_kwh: list[float],
    timestamps,
    solar_peak_powers_kw: list[float],
    battery_capacities_kwh: list[float],
    battery_efficiency: float,
    max_charge_power_kw: float | None,
    max_discharge_power_kw: float | None,
    initial_battery_state_kwh: float,
    electricity_price_eur_per_kwh: float,
    surplus_compensation_eur_per_kwh: float,
    fixed_installation_cost: float,
    solar_cost_per_kw: float,
    battery_cost_per_kwh: float,
    simulation_days: int,
    days_per_year: int = 365
) -> pd.DataFrame:

    total_consumption = sum(consumption_kwh)

    baseline_period_cost = calculate_daily_grid_cost(
        total_consumption,
        electricity_price_eur_per_kwh
    )

    baseline_annual_cost = baseline_period_cost * (
        days_per_year / simulation_days
    )

    results = []

    for peak_power_kw in solar_peak_powers_kw:
        solar_generation_kwh = generate_solar_profile_for_timestamps(
            timestamps,
            peak_power_kw
        )

        for battery_capacity_kwh in battery_capacities_kwh:
            summary = compare_battery_scenario(
                consumption_kwh,
                solar_generation_kwh,
                battery_capacity_kwh,
                battery_efficiency=battery_efficiency,
                max_charge_power_kw=max_charge_power_kw,
                max_discharge_power_kw=max_discharge_power_kw,
                initial_battery_state_kwh=initial_battery_state_kwh
            )

            scenario_period_cost = calculate_daily_net_cost(
                summary["grid_import_with_battery_kwh"],
                summary["solar_surplus_with_battery_kwh"],
                electricity_price_eur_per_kwh,
                surplus_compensation_eur_per_kwh
            )

            scenario_annual_cost = scenario_period_cost * (
                days_per_year / simulation_days
            )

            period_savings = baseline_period_cost - scenario_period_cost
            annual_savings = baseline_annual_cost - scenario_annual_cost

            investment_cost = calculate_total_installation_cost(
                peak_power_kw,
                battery_capacity_kwh,
                solar_cost_per_kw,
                battery_cost_per_kwh,
                fixed_installation_cost=fixed_installation_cost
            )

            payback_years = calculate_simple_payback_years(
                investment_cost,
                annual_savings
            )

            results.append({
                "solar_peak_power_kw": peak_power_kw,
                "battery_capacity_kwh": battery_capacity_kwh,
                "investment_cost_eur": investment_cost,
                "period_cost_eur": scenario_period_cost,
                "annual_cost_eur": scenario_annual_cost,
                "period_savings_eur": period_savings,
                "annual_savings_eur": annual_savings,
                "payback_years": payback_years,
                "grid_import_kwh": summary["grid_import_with_battery_kwh"],
                "solar_surplus_kwh": summary["solar_surplus_with_battery_kwh"],
                "potential_surplus_compensation_eur": (
                    summary["solar_surplus_with_battery_kwh"]
                    * surplus_compensation_eur_per_kwh
                ),
                "self_sufficiency": summary["self_sufficiency_with_battery"]
            })

    return pd.DataFrame(results)