import pandas as pd
import matplotlib.pyplot as plt

from solar import generate_daily_solar_profile
from scenarios import compare_battery_scenario

daily_hourly_consumption_kwh = [
    0.2,
    0.15,
    0.1,
    0.1,
    0.1,
    0.13,
    0.2,
    0.23,
    0.25,
    0.24,
    0.25,
    0.27,
    0.3,
    0.35,
    0.4,
    0.3,
    0.3,
    0.28,
    0.25,
    0.25,
    0.3,
    0.23,
    0.2,
    0.2,
]

solar_peak_powers_kw = [0.5, 1.0, 1.5, 2.0, 3.0]
battery_capacities_kwh = [0, 0.5, 1.0, 2.0, 3.0, 5.0]

battery_efficiency = 0.90
max_charge_power_kw = 1.0
max_discharge_power_kw = 1.0
initial_battery_state_kwh = 0.0

results = []

for peak_power_kw in solar_peak_powers_kw:
    daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

    for battery_capacity_kwh in battery_capacities_kwh:
        summary = compare_battery_scenario(
            daily_hourly_consumption_kwh,
            daily_solar_generation_kwh,
            battery_capacity_kwh,
            battery_efficiency,
            max_charge_power_kw,
            max_discharge_power_kw,
            initial_battery_state_kwh,
        )

        results.append(
            {
                "solar_peak_power_kw": peak_power_kw,
                "battery_capacity_kwh": battery_capacity_kwh,
                "total_solar_generation_kwh": summary["total_solar_generation_kwh"],
                "grid_import_with_battery_kwh": summary["grid_import_with_battery_kwh"],
                "solar_surplus_with_battery_kwh": summary[
                    "solar_surplus_with_battery_kwh"
                ],
                "self_sufficiency_with_battery": summary[
                    "self_sufficiency_with_battery"
                ],
                "grid_import_reduction_kwh": summary["grid_import_reduction_kwh"],
                "solar_surplus_reduction_kwh": summary["solar_surplus_reduction_kwh"],
                "self_sufficiency_improvement": summary["self_sufficiency_improvement"],
            }
        )

df = pd.DataFrame(results)

best_index = df["self_sufficiency_improvement"].idxmax()
best_scenario = df.loc[best_index]

print("\nBest scenario by self-sufficiency:")
print(f"Solar peak power: {best_scenario['solar_peak_power_kw']:.2f} kW")
print(f"Battery capacity: {best_scenario['battery_capacity_kwh']:.2f} kWh")
print(f"Self-sufficiency: {best_scenario['self_sufficiency_with_battery']:.2%}")
print(f"Grid import: {best_scenario['grid_import_with_battery_kwh']:.2f} kWh")
print(f"Solar surplus: {best_scenario['solar_surplus_with_battery_kwh']:.2f} kWh")

plt.figure(figsize=(10, 5))

for battery_capacity_kwh in battery_capacities_kwh:
    subset = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

    plt.plot(
        subset["solar_peak_power_kw"],
        subset["self_sufficiency_with_battery"],
        marker="o",
        label=f"{battery_capacity_kwh} kWh battery",
    )

plt.title("Self-Sufficiency by Solar Power and Battery Capacity")
plt.xlabel("Solar Peak Power (kW)")
plt.ylabel("Self-Sufficiency")
plt.grid(True)
plt.legend()

plt.savefig("images/grid_search_self_sufficiency.png", dpi=300, bbox_inches="tight")
