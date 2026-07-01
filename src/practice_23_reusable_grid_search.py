import matplotlib.pyplot as plt

from data_loader import load_consumption_data
from optimization import run_economic_grid_search


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

df = run_economic_grid_search(
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

print("\nReusable economic grid search:")
print(f"Input file: {file_path}")
print(df.to_string(index=False))

valid_payback_df = df.dropna(subset=["payback_years"])

best_payback_index = valid_payback_df["payback_years"].idxmin()
best_payback_scenario = valid_payback_df.loc[best_payback_index]

best_self_sufficiency_index = df["self_sufficiency"].idxmax()
best_self_sufficiency_scenario = df.loc[best_self_sufficiency_index]

print("\nBest scenario by payback:")
print(f"Solar peak power: {best_payback_scenario['solar_peak_power_kw']:.2f} kW")
print(f"Battery capacity: {best_payback_scenario['battery_capacity_kwh']:.2f} kWh")
print(f"Payback: {best_payback_scenario['payback_years']:.2f} years")
print(f"Self-sufficiency: {best_payback_scenario['self_sufficiency']:.2%}")

print("\nBest scenario by self-sufficiency:")
print(f"Solar peak power: {best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW")
print(f"Battery capacity: {best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh")
print(f"Payback: {best_self_sufficiency_scenario['payback_years']:.2f} years")
print(f"Self-sufficiency: {best_self_sufficiency_scenario['self_sufficiency']:.2%}")

plt.figure(figsize=(10, 5))

for battery_capacity_kwh in battery_capacities_kwh:
    battery_df = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

    plt.plot(
        battery_df["solar_peak_power_kw"],
        battery_df["payback_years"],
        marker="o",
        label=f"{battery_capacity_kwh} kWh battery"
    )

plt.title("Reusable Grid Search: Payback by Solar Power and Battery Capacity")
plt.xlabel("Solar Peak Power (kW)")
plt.ylabel("Payback Period (years)")
plt.grid(True)
plt.legend()

plt.savefig("images/reusable_grid_search_payback.png", dpi=300, bbox_inches="tight")
