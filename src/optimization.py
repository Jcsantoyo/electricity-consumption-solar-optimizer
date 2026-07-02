import pandas as pd

from solar import generate_solar_profile_for_timestamps
from scenarios import compare_battery_scenario
from economics import (
    calculate_total_installation_cost,
    calculate_grid_cost,
    calculate_net_cost,
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

    baseline_period_cost = calculate_grid_cost(
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

            scenario_period_cost = calculate_net_cost(
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

def get_best_scenario_by_payback(df: pd.DataFrame) -> pd.Series:
    valid_payback_df = df.dropna(subset=["payback_years"])

    if valid_payback_df.empty:
        raise ValueError("No valid payback values found.")

    best_index = valid_payback_df["payback_years"].idxmin()

    return valid_payback_df.loc[best_index]


def get_best_scenario_by_self_sufficiency(df: pd.DataFrame) -> pd.Series:
    best_index = df["self_sufficiency"].idxmax()

    return df.loc[best_index]

def print_scenario_summary(
    title: str,
    scenario: pd.Series
) -> None:
    print(f"\n{title}:")
    print(f"Solar peak power: {scenario['solar_peak_power_kw']:.2f} kW")
    print(f"Battery capacity: {scenario['battery_capacity_kwh']:.2f} kWh")
    print(f"Investment cost: {scenario['investment_cost_eur']:.2f} EUR")
    print(f"Annual savings: {scenario['annual_savings_eur']:.2f} EUR/year")
    print(f"Payback: {scenario['payback_years']:.2f} years")
    print(f"Self-sufficiency: {scenario['self_sufficiency']:.2%}")
    print(f"Grid import: {scenario['grid_import_kwh']:.2f} kWh")
    print(f"Solar surplus: {scenario['solar_surplus_kwh']:.2f} kWh")

def print_scenario_comparison(
    best_payback_scenario: pd.Series,
    best_self_sufficiency_scenario: pd.Series
) -> None:
    print("\nComparison:")

    print(
        f"Best payback scenario: "
        f"{best_payback_scenario['solar_peak_power_kw']:.2f} kW solar, "
        f"{best_payback_scenario['battery_capacity_kwh']:.2f} kWh battery"
    )

    print(
        f"Best self-sufficiency scenario: "
        f"{best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW solar, "
        f"{best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh battery"
    )

    if (
        best_payback_scenario["solar_peak_power_kw"]
        == best_self_sufficiency_scenario["solar_peak_power_kw"]
        and best_payback_scenario["battery_capacity_kwh"]
        == best_self_sufficiency_scenario["battery_capacity_kwh"]
    ):
        print("Both criteria select the same scenario.")
    else:
        print(
            "The economically optimal scenario and the energy optimal scenario "
            "are different."
        )

def build_scenario_summary_text(
    best_payback_scenario: pd.Series,
    best_self_sufficiency_scenario: pd.Series
) -> str:
    text = ""

    text += "Electricity Consumption Solar Optimizer\n"
    text += "======================================\n\n"

    text += "Best scenario by payback:\n"
    text += f"Solar peak power: {best_payback_scenario['solar_peak_power_kw']:.2f} kW\n"
    text += f"Battery capacity: {best_payback_scenario['battery_capacity_kwh']:.2f} kWh\n"
    text += f"Investment cost: {best_payback_scenario['investment_cost_eur']:.2f} EUR\n"
    text += f"Annual savings: {best_payback_scenario['annual_savings_eur']:.2f} EUR/year\n"
    text += f"Payback: {best_payback_scenario['payback_years']:.2f} years\n"
    text += f"Self-sufficiency: {best_payback_scenario['self_sufficiency']:.2%}\n"
    text += f"Grid import: {best_payback_scenario['grid_import_kwh']:.2f} kWh\n"
    text += f"Solar surplus: {best_payback_scenario['solar_surplus_kwh']:.2f} kWh\n\n"

    text += "Best scenario by self-sufficiency:\n"
    text += f"Solar peak power: {best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW\n"
    text += f"Battery capacity: {best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh\n"
    text += f"Investment cost: {best_self_sufficiency_scenario['investment_cost_eur']:.2f} EUR\n"
    text += f"Annual savings: {best_self_sufficiency_scenario['annual_savings_eur']:.2f} EUR/year\n"
    text += f"Payback: {best_self_sufficiency_scenario['payback_years']:.2f} years\n"
    text += f"Self-sufficiency: {best_self_sufficiency_scenario['self_sufficiency']:.2%}\n"
    text += f"Grid import: {best_self_sufficiency_scenario['grid_import_kwh']:.2f} kWh\n"
    text += f"Solar surplus: {best_self_sufficiency_scenario['solar_surplus_kwh']:.2f} kWh\n\n"

    if (
        best_payback_scenario["solar_peak_power_kw"]
        == best_self_sufficiency_scenario["solar_peak_power_kw"]
        and best_payback_scenario["battery_capacity_kwh"]
        == best_self_sufficiency_scenario["battery_capacity_kwh"]
    ):
        text += "Both criteria select the same scenario.\n"
    else:
        text += (
            "The economically optimal scenario and the energy optimal "
            "scenario are different.\n"
        )

    return text

def build_best_scenarios_dataframe(
    best_payback_scenario: pd.Series,
    best_self_sufficiency_scenario: pd.Series
) -> pd.DataFrame:
    rows = [
        {
            "criterion": "best_payback",
            "solar_peak_power_kw": best_payback_scenario["solar_peak_power_kw"],
            "battery_capacity_kwh": best_payback_scenario["battery_capacity_kwh"],
            "investment_cost_eur": best_payback_scenario["investment_cost_eur"],
            "annual_savings_eur": best_payback_scenario["annual_savings_eur"],
            "payback_years": best_payback_scenario["payback_years"],
            "self_sufficiency": best_payback_scenario["self_sufficiency"],
            "grid_import_kwh": best_payback_scenario["grid_import_kwh"],
            "solar_surplus_kwh": best_payback_scenario["solar_surplus_kwh"]
        },
        {
            "criterion": "best_self_sufficiency",
            "solar_peak_power_kw": best_self_sufficiency_scenario["solar_peak_power_kw"],
            "battery_capacity_kwh": best_self_sufficiency_scenario["battery_capacity_kwh"],
            "investment_cost_eur": best_self_sufficiency_scenario["investment_cost_eur"],
            "annual_savings_eur": best_self_sufficiency_scenario["annual_savings_eur"],
            "payback_years": best_self_sufficiency_scenario["payback_years"],
            "self_sufficiency": best_self_sufficiency_scenario["self_sufficiency"],
            "grid_import_kwh": best_self_sufficiency_scenario["grid_import_kwh"],
            "solar_surplus_kwh": best_self_sufficiency_scenario["solar_surplus_kwh"]
        }
    ]

    return pd.DataFrame(rows)