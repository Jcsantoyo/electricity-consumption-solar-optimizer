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

battery_capacity_kwh = 2.0
battery_efficiency = 0.90
max_charge_power_kw = 1.0
max_discharge_power_kw = 1.0
initial_battery_state_kwh = 0.0

results = []

for peak_power_kw in solar_peak_powers_kw:
    daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

    summary = compare_battery_scenario(
        daily_hourly_consumption_kwh,
        daily_solar_generation_kwh,
        battery_capacity_kwh,
        battery_efficiency=battery_efficiency,
        max_charge_power_kw=max_charge_power_kw,
        max_discharge_power_kw=max_discharge_power_kw,
        initial_battery_state_kwh=initial_battery_state_kwh,
    )

    results.append(
        {
            "solar_peak_power_kw": peak_power_kw,
            "total_solar_generation_kwh": summary["total_solar_generation_kwh"],
            "grid_import_with_battery_kwh": summary["grid_import_with_battery_kwh"],
            "solar_surplus_with_battery_kwh": summary["solar_surplus_with_battery_kwh"],
            "grid_import_reduction_kwh": summary["grid_import_reduction_kwh"],
            "solar_surplus_reduction_kwh": summary["solar_surplus_reduction_kwh"],
            "self_sufficiency_with_battery": summary["self_sufficiency_with_battery"],
            "self_sufficiency_improvement": summary["self_sufficiency_improvement"],
        }
    )

df = pd.DataFrame(results)

print("\nSolar peak power sweep:")
print(df.to_string(index=False))

plt.figure(figsize=(10, 5))

plt.plot(df["solar_peak_power_kw"], df["self_sufficiency_with_battery"], marker="o")

plt.title("Self-Sufficiency vs Solar Peak Power")
plt.xlabel("Solar Peak Power (kW)")
plt.ylabel("Self-Sufficiency")
plt.grid(True)

plt.savefig(
    "images/self_sufficiency_vs_solar_peak_power.png", dpi=300, bbox_inches="tight"
)

plt.figure(figsize=(10, 5))

plt.plot(df["solar_peak_power_kw"], df["solar_surplus_with_battery_kwh"], marker="o")

plt.title("Solar Surplus vs Solar Peak Power")
plt.xlabel("Solar Peak Power (kW)")
plt.ylabel("Solar Surplus (kWh)")
plt.grid(True)

plt.savefig(
    "images/solar_surplus_vs_solar_peak_power.png", dpi=300, bbox_inches="tight"
)
