import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_consumption_data
from solar import generate_daily_solar_profile
from scenarios import compare_battery_scenario
from economics import (
    calculate_total_installation_cost,
    calculate_daily_grid_cost,
    calculate_daily_net_cost,
    calculate_simple_payback_years,
)

file_path = "data/raw/consumption_sample.csv"

df_consumptions = load_consumption_data(file_path)

daily_hourly_consumption_kwh = df_consumptions["consumption_kwh"].tolist()

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

total_consumption = sum(daily_hourly_consumption_kwh)

baseline_daily_cost = calculate_daily_grid_cost(
    total_consumption, electricity_price_eur_per_kwh
)

baseline_annual_cost = baseline_daily_cost * days_per_year

results = []

for peak_power_kw in solar_peak_powers_kw:
    daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

    for battery_capacity_kwh in battery_capacities_kwh:
        summary = compare_battery_scenario(
            daily_hourly_consumption_kwh,
            daily_solar_generation_kwh,
            battery_capacity_kwh,
            battery_efficiency=battery_efficiency,
            max_charge_power_kw=max_charge_power_kw,
            max_discharge_power_kw=max_discharge_power_kw,
            initial_battery_state_kwh=initial_battery_state_kwh,
        )

        scenario_daily_cost = calculate_daily_net_cost(
            summary["grid_import_with_battery_kwh"],
            summary["solar_surplus_with_battery_kwh"],
            electricity_price_eur_per_kwh,
            surplus_compensation_eur_per_kwh,
        )

        scenario_annual_cost = scenario_daily_cost * days_per_year

        daily_savings = baseline_daily_cost - scenario_daily_cost
        annual_savings = baseline_annual_cost - scenario_annual_cost

        investment_cost = calculate_total_installation_cost(
            peak_power_kw,
            battery_capacity_kwh,
            solar_cost_per_kw,
            battery_cost_per_kwh,
            fixed_installation_cost=fixed_installation_cost,
        )

        payback_years = calculate_simple_payback_years(investment_cost, annual_savings)

        results.append(
            {
                "solar_peak_power_kw": peak_power_kw,
                "battery_capacity_kwh": battery_capacity_kwh,
                "investment_cost_eur": investment_cost,
                "daily_cost_eur": scenario_daily_cost,
                "annual_cost_eur": scenario_annual_cost,
                "daily_savings_eur": daily_savings,
                "annual_savings_eur": annual_savings,
                "payback_years": payback_years,
                "grid_import_kwh": summary["grid_import_with_battery_kwh"],
                "solar_surplus_kwh": summary["solar_surplus_with_battery_kwh"],
                "potential_surplus_compensation_eur": (
                    summary["solar_surplus_with_battery_kwh"]
                    * surplus_compensation_eur_per_kwh
                ),
                "self_sufficiency": summary["self_sufficiency_with_battery"],
            }
        )

df = pd.DataFrame(results)

print("\nCSV-based economic grid search")
print(f"Input file: {file_path}")

print("\nEconomic assumptions:")
print(f"Electricity price: {electricity_price_eur_per_kwh:.2f} EUR/kWh")
print(f"Surplus compensation: {surplus_compensation_eur_per_kwh:.2f} EUR/kWh")
print(f"Fixed installation cost: {fixed_installation_cost:.2f} EUR")
print(f"Solar installation cost: {solar_cost_per_kw:.2f} EUR/kW")
print(f"Battery installation cost: {battery_cost_per_kwh:.2f} EUR/kWh")
print(f"Baseline daily cost: {baseline_daily_cost:.2f} EUR/day")
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

best_self_sufficiency_index = df["self_sufficiency"].idxmax()
best_self_sufficiency_scenario = df.loc[best_self_sufficiency_index]

print("\nBest scenario by self-sufficiency:")
print(
    f"Solar peak power: {best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW"
)
print(
    f"Battery capacity: {best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh"
)
print(
    f"Investment cost: {best_self_sufficiency_scenario['investment_cost_eur']:.2f} EUR"
)
print(
    f"Annual savings: {best_self_sufficiency_scenario['annual_savings_eur']:.2f} EUR/year"
)
print(f"Payback: {best_self_sufficiency_scenario['payback_years']:.2f} years")
print(f"Self-sufficiency: {best_self_sufficiency_scenario['self_sufficiency']:.2%}")

plt.figure(figsize=(10, 5))

for battery_capacity_kwh in battery_capacities_kwh:
    battery_df = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

    plt.plot(
        battery_df["solar_peak_power_kw"],
        battery_df["payback_years"],
        marker="o",
        label=f"{battery_capacity_kwh} kWh battery",
    )

plt.title("CSV-Based Payback Period by Solar Power and Battery Capacity")
plt.xlabel("Solar Peak Power (kW)")
plt.ylabel("Payback Period (years)")
plt.grid(True)
plt.legend()

plt.savefig("images/csv_payback_grid_search.png", dpi=300, bbox_inches="tight")
