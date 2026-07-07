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

peak_power_kw = 1.0
battery_efficiency = 0.90
max_charge_power_kw = 1.0
max_discharge_power_kw = 1.0
initial_battery_state_kwh = 0.0

daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

battery_capacities_kwh = [0, 0.5, 1.0, 2.0, 3.0, 5.0]

results = []

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
            "battery_capacity_kwh": battery_capacity_kwh,
            "grid_import_with_battery_kwh": summary["grid_import_with_battery_kwh"],
            "solar_surplus_with_battery_kwh": summary["solar_surplus_with_battery_kwh"],
            "grid_import_reduction_kwh": summary["grid_import_reduction_kwh"],
            "solar_surplus_reduction_kwh": summary["solar_surplus_reduction_kwh"],
            "self_sufficiency_with_battery": summary["self_sufficiency_with_battery"],
            "self_sufficiency_improvement": summary["self_sufficiency_improvement"],
        }
    )

df = pd.DataFrame(results)

print("\nBattery capacity sweep:")
print(df.to_string(index=False))

plt.figure(figsize=(10, 5))

plt.plot(df["battery_capacity_kwh"], df["self_sufficiency_with_battery"], marker="o")

plt.title("Self-Sufficiency vs Battery Capacity")
plt.xlabel("Battery Capacity (kWh)")
plt.ylabel("Self-Sufficiency")
plt.grid(True)

plt.savefig(
    "images/self_sufficiency_vs_battery_capacity.png", dpi=300, bbox_inches="tight"
)

plt.figure(figsize=(10, 5))

plt.plot(df["battery_capacity_kwh"], df["grid_import_with_battery_kwh"], marker="o")

plt.title("Grid Import vs Battery Capacity")
plt.xlabel("Battery Capacity (kWh)")
plt.ylabel("Grid Import (kWh)")
plt.grid(True)

plt.savefig("images/grid_import_vs_battery_capacity.png", dpi=300, bbox_inches="tight")
