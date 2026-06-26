import pandas as pd
import matplotlib.pyplot as plt

from solar import (
    generate_daily_solar_profile,
    simulate_self_consumption
)

from battery import simulate_battery


daily_hourly_consumption_kwh = [
    0.2, 0.15, 0.1, 0.1, 0.1, 0.13,
    0.2, 0.23, 0.25, 0.24, 0.25, 0.27,
    0.3, 0.35, 0.4, 0.3, 0.3, 0.28,
    0.25, 0.25, 0.3, 0.23, 0.2, 0.2
]

peak_power_kw = 1.0
battery_capacity_kwh = 2.0

daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

self_consumed_no_battery, grid_import_no_battery, solar_surplus_no_battery = simulate_self_consumption(
    daily_hourly_consumption_kwh,
    daily_solar_generation_kwh
)

battery_results = simulate_battery(daily_hourly_consumption_kwh, daily_solar_generation_kwh, battery_capacity_kwh)

grid_import_with_battery = battery_results["grid_import_kwh"]
solar_surplus_with_battery = battery_results["solar_surplus_kwh"]
battery_state_kwh = battery_results["battery_state_kwh"]

df = pd.DataFrame({
    "hour": range(24),
    "consumption_kwh": daily_hourly_consumption_kwh,
    "solar_generation_kwh": daily_solar_generation_kwh,

    "grid_import_no_battery_kwh": grid_import_no_battery,
    "solar_surplus_no_battery_kwh": solar_surplus_no_battery,

    "grid_import_with_battery_kwh": grid_import_with_battery,
    "solar_surplus_with_battery_kwh": solar_surplus_with_battery,
    "battery_state_kwh": battery_state_kwh
})

total_consumption = df["consumption_kwh"].sum()
total_solar_generation = df["solar_generation_kwh"].sum()

total_grid_import_no_battery = df["grid_import_no_battery_kwh"].sum()
total_grid_import_with_battery = df["grid_import_with_battery_kwh"].sum()

total_solar_surplus_no_battery = df["solar_surplus_no_battery_kwh"].sum()
total_solar_surplus_with_battery = df["solar_surplus_with_battery_kwh"].sum()

grid_import_reduction = total_grid_import_no_battery - total_grid_import_with_battery
solar_surplus_reduction = total_solar_surplus_no_battery - total_solar_surplus_with_battery

self_sufficiency_no_battery = 1 -(total_grid_import_no_battery / total_consumption)
self_sufficiency_with_battery = 1 -(total_grid_import_with_battery / total_consumption)

print(df.to_string(index=False))

print("\nBattery impact summary:")
print(f"Solar peak power: {peak_power_kw:.2f} kW")
print(f"Battery capacity: {battery_capacity_kwh:.2f} kWh")
print(f"Total consumption: {total_consumption:.2f} kWh")
print(f"Total solar generation: {total_solar_generation:.2f} kWh")

print("\nWithout battery:")
print(f"Grid import: {total_grid_import_no_battery:.2f} kWh")
print(f"Solar surplus: {total_solar_surplus_no_battery:.2f} kWh")
print(f"Self-sufficiency: {self_sufficiency_no_battery:.2%}")

print("\nWith battery:")
print(f"Grid import: {total_grid_import_with_battery:.2f} kWh")
print(f"Solar surplus: {total_solar_surplus_with_battery:.2f} kWh")
print(f"Self-sufficiency: {self_sufficiency_with_battery:.2%}")

print("\nImprovement:")
print(f"Grid import reduction: {grid_import_reduction:.2f} kWh")
print(f"Solar surplus reduction: {solar_surplus_reduction:.2f} kWh")
print(
    f"Self-sufficiency improvement: "
    f"{(self_sufficiency_with_battery - self_sufficiency_no_battery):.2%}"
)

plt.figure(figsize=(10, 5))

plt.plot(
    df["hour"],
    df["grid_import_no_battery_kwh"],
    marker="o",
    label="Grid import without battery"
)

plt.plot(
    df["hour"],
    df["grid_import_with_battery_kwh"],
    marker="o",
    label="Grid import with battery"
)

plt.title("Grid Import: Without Battery vs With Battery")
plt.xlabel("Hour of Day")
plt.ylabel("Energy Imported from Grid (kWh)")
plt.xticks(range(24))
plt.grid(True)
plt.legend()

plt.savefig("images/grid_import_battery_comparison.png", dpi=300, bbox_inches="tight")


plt.figure(figsize=(10, 5))

plt.plot(
    df["hour"],
    df["solar_surplus_no_battery_kwh"],
    marker="o",
    label="Solar surplus without battery"
)

plt.plot(
    df["hour"],
    df["solar_surplus_with_battery_kwh"],
    marker="o",
    label="Solar surplus with battery"
)

plt.title("Solar Surplus: Without Battery vs With Battery")
plt.xlabel("Hour of Day")
plt.ylabel("Solar Surplus (kWh)")
plt.xticks(range(24))
plt.grid(True)
plt.legend()

plt.savefig("images/solar_surplus_battery_comparison.png", dpi=300, bbox_inches="tight")

