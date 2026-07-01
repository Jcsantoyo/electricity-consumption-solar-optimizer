import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_consumption_data
from solar import(
    generate_solar_profile_for_timestamps,
    simulate_self_consumption
) 

from battery import simulate_battery

file_path = "data/simulated/synthetic_consumption_30_days.csv"

df = load_consumption_data(file_path)

consumption_kwh = df["consumption_kwh"].tolist()

peak_power_kw = 1.0
battery_capacity_kwh = 2.0

battery_efficiency = 0.90
max_charge_power_kw = 1.0
max_discharge_power_kw = 1.0
initial_battery_state_kwh = 0.0

solar_generation_kwh = generate_solar_profile_for_timestamps(df["datetime"], peak_power_kw)

self_consumed_no_battery, grid_import_no_battery, solar_surplus_no_battery = simulate_self_consumption(
    consumption_kwh,
    solar_generation_kwh
)

battery_results = simulate_battery(
    consumption_kwh,
    solar_generation_kwh,
    battery_capacity_kwh,
    battery_efficiency=battery_efficiency,
    max_charge_power_kw=max_charge_power_kw,
    max_discharge_power_kw=max_discharge_power_kw,
    initial_battery_state_kwh=initial_battery_state_kwh
)

df["solar_generation_kwh"] = solar_generation_kwh

df["grid_import_no_battery_kwh"] = grid_import_no_battery
df["solar_surplus_no_battery_kwh"] = solar_surplus_no_battery

df["self_consumed_with_battery_kwh"] = battery_results["self_consumed_kwh"]
df["battery_charge_kwh"] = battery_results["battery_charge_kwh"]
df["battery_discharge_kwh"] = battery_results["battery_discharge_kwh"]
df["grid_import_with_battery_kwh"] = battery_results["grid_import_kwh"]
df["solar_surplus_with_battery_kwh"] = battery_results["solar_surplus_kwh"]
df["battery_state_kwh"] = battery_results["battery_state_kwh"]

total_consumption = df["consumption_kwh"].sum()
total_solar_generation = df["solar_generation_kwh"].sum()

total_grid_import_no_battery = df["grid_import_no_battery_kwh"].sum()
total_grid_import_with_battery = df["grid_import_with_battery_kwh"].sum()

total_solar_surplus_no_battery = df["solar_surplus_no_battery_kwh"].sum()
total_solar_surplus_with_battery = df["solar_surplus_with_battery_kwh"].sum()

self_sufficiency_no_battery = 1 - (
    total_grid_import_no_battery / total_consumption
)

self_sufficiency_with_battery = 1 - (
    total_grid_import_with_battery / total_consumption
)

print("\n30-day simulation with time series:")
print(f"Input file: {file_path}")
print(f"Number of hours: {len(df)}")
print(f"Solar peak power: {peak_power_kw:.2f} kW")
print(f"Battery capacity: {battery_capacity_kwh:.2f} kWh")

print("\nEnergy summary:")
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

plt.figure(figsize=(12, 5))

plt.plot(
    df["datetime"],
    df["consumption_kwh"],
    label="Consumption"
)

plt.plot(
    df["datetime"],
    df["solar_generation_kwh"],
    label="Solar generation"
)

plt.title("Consumption vs Solar Generation Over 30 Days")
plt.xlabel("Datetime")
plt.ylabel("Energy (kWh)")
plt.grid(True)
plt.legend()

plt.savefig("images/consumption_vs_solar_30_days.png", dpi=300, bbox_inches="tight")

plt.figure(figsize=(12, 5))

plt.plot(
    df["datetime"],
    df["grid_import_no_battery_kwh"],
    label="Grid import without battery"
)

plt.plot(
    df["datetime"],
    df["grid_import_with_battery_kwh"],
    label="Grid import with battery"
)

plt.title("Grid Import Over 30 Days")
plt.xlabel("Datetime")
plt.ylabel("Grid Import (kWh)")
plt.grid(True)
plt.legend()

plt.savefig("images/grid_import_30_days.png", dpi=300, bbox_inches="tight")

plt.figure(figsize=(12, 5))

plt.plot(
    df["datetime"],
    df["battery_state_kwh"],
    label="Battery state"
)

plt.title("Battery State of Charge Over 30 Days")
plt.xlabel("Datetime")
plt.ylabel("Battery State (kWh)")
plt.grid(True)
plt.legend()

plt.savefig("images/battery_state_30_days.png", dpi=300, bbox_inches="tight")

plt.figure(figsize=(12, 5))

plt.plot(
    df["datetime"],
    df["solar_surplus_no_battery_kwh"],
    label="Solar surplus without battery"
)

plt.plot(
    df["datetime"],
    df["solar_surplus_with_battery_kwh"],
    label="Solar surplus with battery"
)

plt.title("Solar Surplus Over 30 Days")
plt.xlabel("Datetime")
plt.ylabel("Solar Surplus (kWh)")
plt.grid(True)
plt.legend()

plt.savefig("images/solar_surplus_30_days.png", dpi=300, bbox_inches="tight")

plt.show()