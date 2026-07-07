import pandas as pd
import matplotlib.pyplot as plt

from solar import generate_daily_solar_profile
from battery import simulate_battery

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
battery_capacity_kwh = 2.0
battery_efficiency = 0.90
max_charge_power_kw = 1.0
max_discharge_power_kw = 1.0
initial_battery_state_kwh = 0.0

daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

battery_results = simulate_battery(
    daily_hourly_consumption_kwh,
    daily_solar_generation_kwh,
    battery_capacity_kwh,
    battery_efficiency=battery_efficiency,
    max_charge_power_kw=max_charge_power_kw,
    max_discharge_power_kw=max_discharge_power_kw,
    initial_battery_state_kwh=initial_battery_state_kwh,
)

df = pd.DataFrame(
    {
        "hour": range(24),
        "consumption_kwh": daily_hourly_consumption_kwh,
        "solar_generation_kwh": daily_solar_generation_kwh,
        "self_consumed_kwh": battery_results["self_consumed_kwh"],
        "battery_charge_kwh": battery_results["battery_charge_kwh"],
        "battery_discharge_kwh": battery_results["battery_discharge_kwh"],
        "grid_import_kwh": battery_results["grid_import_kwh"],
        "solar_surplus_kwh": battery_results["solar_surplus_kwh"],
        "battery_state_kwh": battery_results["battery_state_kwh"],
    }
)

print("Max battery state:", df["battery_state_kwh"].max())
print("Min battery state:", df["battery_state_kwh"].min())

total_consumption = df["consumption_kwh"].sum()
total_solar_generation = df["solar_generation_kwh"].sum()
total_self_consumed = df["self_consumed_kwh"].sum()
total_battery_charge = df["battery_charge_kwh"].sum()
total_battery_discharge = df["battery_discharge_kwh"].sum()
total_grid_import = df["grid_import_kwh"].sum()
total_solar_surplus = df["solar_surplus_kwh"].sum()

if total_solar_generation > 0:
    self_consumption_ratio = (
        total_self_consumed + total_battery_charge
    ) / total_solar_generation
else:
    self_consumption_ratio = 0

if total_consumption > 0:
    self_sufficiency_ratio = (
        total_self_consumed + total_battery_discharge
    ) / total_consumption
else:
    self_sufficiency_ratio = 0

print(df.to_string(index=False))

print("\nDaily battery simulation summary:")
print(f"Installed solar peak power: {peak_power_kw:.2f} kW")
print(f"Battery capacity: {battery_capacity_kwh:.2f} kWh")
print(f"Total consumption: {total_consumption:.2f} kWh")
print(f"Total solar generation: {total_solar_generation:.2f} kWh")
print(f"Total direct self-consumption: {total_self_consumed:.2f} kWh")
print(f"Total battery charge: {total_battery_charge:.2f} kWh")
print(f"Total battery discharge: {total_battery_discharge:.2f} kWh")
print(f"Total grid import: {total_grid_import:.2f} kWh")
print(f"Total solar surplus: {total_solar_surplus:.2f} kWh")
print(f"Self-consumption ratio: {self_consumption_ratio:.2%}")
print(f"Self-sufficiency ratio: {self_sufficiency_ratio:.2%}")
print(f"Battery efficiency: {battery_efficiency:.2%}")
print(f"Max charge power: {max_charge_power_kw:.2f} kW")
print(f"Max discharge power: {max_discharge_power_kw:.2f} kW")
print(f"Initial battery state: {initial_battery_state_kwh:.2f} kWh")

plt.figure(figsize=(10, 5))

plt.plot(df["hour"], df["battery_state_kwh"], marker="o", label="Battery state")

plt.title("Battery State of Charge")
plt.xlabel("Hour of Day")
plt.ylabel("Energy Stored (kWh)")
plt.xticks(range(24))
plt.grid(True)
plt.legend()

plt.savefig("images/battery_state_of_charge.png", dpi=300, bbox_inches="tight")
