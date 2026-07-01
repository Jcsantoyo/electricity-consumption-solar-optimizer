import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_consumption_data
from solar import generate_solar_profile_for_timestamps
from scenarios import compare_battery_scenario
from economics import (
    calculate_total_installation_cost,
    calculate_daily_grid_cost,
    calculate_daily_net_cost,
    calculate_simple_payback_years
)

file_path = "data/simulated/synthetic_consumption_30_days.csv"

df_consumption = load_consumption_data(file_path)

consumption_kwh = df_consumption["consumption_kwh"].tolist()

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

days_per_year = 365
simulation_days = 30

total_consumption = sum(consumption_kwh)

baseline_period_cost = calculate_daily_grid_cost(
    total_consumption,
    electricity_price_eur_per_kwh
)

baseline_annual_cost = baseline_period_cost * (days_per_year / simulation_days)

results = []

for peak_power_kw in solar_peak_powers_kw:
    solar_generation_kwh = generate_solar_profile_for_timestamps(
        df_consumption["datetime"],
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

df = pd.DataFrame(results)

print("\n30-day economic grid search")
print(f"Input file: {file_path}")
print(f"Number of hours: {len(df_consumption)}")
print(f"Simulation days: {simulation_days}")

print("\nEconomic assumptions:")
print(f"Electricity price: {electricity_price_eur_per_kwh:.2f} EUR/kWh")
print(f"Surplus compensation: {surplus_compensation_eur_per_kwh:.2f} EUR/kWh")
print(f"Fixed installation cost: {fixed_installation_cost:.2f} EUR")
print(f"Solar installation cost: {solar_cost_per_kw:.2f} EUR/kW")
print(f"Battery installation cost: {battery_cost_per_kwh:.2f} EUR/kWh")
print(f"Baseline period cost: {baseline_period_cost:.2f} EUR")
print(f"Baseline annual cost: {baseline_annual_cost:.2f} EUR/year")

print("\nEconomic grid search results:")
print(df.to_string(index=False))

valid_payback_df = df.dropna(subset=["payback_years"])

best_payback_index = valid_payback_df["payback_years"].idxmin()
best_payback_scenario = valid_payback_df.loc[best_payback_index]

print("\nBest scenario by payback:")
print(f"Solar peak power: {best_payback_scenario['solar_peak_power_kw']:.2f} kW")
print(f"Battery capacity: {best_payback_scenario['battery_capacity_kwh']:.2f} kWh")
print(f"Investment cost: {best_payback_scenario['investment_cost_eur']:.2f} EUR")
print(f"Annual savings: {best_payback_scenario['annual_savings_eur']:.2f} EUR/year")
print(f"Payback: {best_payback_scenario['payback_years']:.2f} years")
print(f"Self-sufficiency: {best_payback_scenario['self_sufficiency']:.2%}")
print(f"Grid import: {best_payback_scenario['grid_import_kwh']:.2f} kWh")
print(f"Solar surplus: {best_payback_scenario['solar_surplus_kwh']:.2f} kWh")

best_self_sufficiency_index = df["self_sufficiency"].idxmax()
best_self_sufficiency_scenario = df.loc[best_self_sufficiency_index]

print("\nBest scenario by self-sufficiency:")
print(f"Solar peak power: {best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW")
print(f"Battery capacity: {best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh")
print(f"Investment cost: {best_self_sufficiency_scenario['investment_cost_eur']:.2f} EUR")
print(f"Annual savings: {best_self_sufficiency_scenario['annual_savings_eur']:.2f} EUR/year")
print(f"Payback: {best_self_sufficiency_scenario['payback_years']:.2f} years")
print(f"Self-sufficiency: {best_self_sufficiency_scenario['self_sufficiency']:.2%}")
print(f"Grid import: {best_self_sufficiency_scenario['grid_import_kwh']:.2f} kWh")
print(f"Solar surplus: {best_self_sufficiency_scenario['solar_surplus_kwh']:.2f} kWh")

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

plt.figure(figsize=(10, 5))

for battery_capacity_kwh in battery_capacities_kwh:
    battery_df = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

    plt.plot(
        battery_df["solar_peak_power_kw"],
        battery_df["payback_years"],
        marker="o",
        label=f"{battery_capacity_kwh} kWh battery"
    )

plt.title("30-Day Payback Period by Solar Power and Battery Capacity")
plt.xlabel("Solar Peak Power (kW)")
plt.ylabel("Payback Period (years)")
plt.grid(True)
plt.legend()

plt.savefig("images/payback_grid_search_30_days.png", dpi=300, bbox_inches="tight")
