from data_loader import load_consumption_data
from solar import generate_solar_profile_for_timestamps
from scenarios import compare_battery_scenario


file_path = "data/simulated/synthetic_consumption_30_days.csv"

df_consumption = load_consumption_data(file_path)

consumption_kwh = df_consumption["consumption_kwh"].tolist()

peak_power_kw = 1.0
battery_capacity_kwh = 2.0

battery_efficiency = 0.90
max_charge_power_kw = 1.0
max_discharge_power_kw = 1.0
initial_battery_state_kwh = 0.0

solar_generation_kwh = generate_solar_profile_for_timestamps(
    df_consumption["datetime"], peak_power_kw
)

summary = compare_battery_scenario(
    consumption_kwh,
    solar_generation_kwh,
    battery_capacity_kwh,
    battery_efficiency=battery_efficiency,
    max_charge_power_kw=max_charge_power_kw,
    max_discharge_power_kw=max_discharge_power_kw,
    initial_battery_state_kwh=initial_battery_state_kwh,
)

print("\nSynthetic 30-day simulation:")
print(f"Input file: {file_path}")
print(f"Number of hours: {len(consumption_kwh)}")
print(f"Solar peak power: {peak_power_kw:.2f} kW")
print(f"Battery capacity: {battery_capacity_kwh:.2f} kWh")

print("\nEnergy summary:")
print(f"Total consumption: {summary['total_consumption_kwh']:.2f} kWh")
print(f"Total solar generation: {summary['total_solar_generation_kwh']:.2f} kWh")

print("\nWithout battery:")
print(f"Grid import: {summary['grid_import_no_battery_kwh']:.2f} kWh")
print(f"Solar surplus: {summary['solar_surplus_no_battery_kwh']:.2f} kWh")
print(f"Self-sufficiency: {summary['self_sufficiency_no_battery']:.2%}")

print("\nWith battery:")
print(f"Grid import: {summary['grid_import_with_battery_kwh']:.2f} kWh")
print(f"Solar surplus: {summary['solar_surplus_with_battery_kwh']:.2f} kWh")
print(f"Self-sufficiency: {summary['self_sufficiency_with_battery']:.2%}")

print("\nImprovement:")
print(f"Grid import reduction: {summary['grid_import_reduction_kwh']:.2f} kWh")
print(f"Solar surplus reduction: {summary['solar_surplus_reduction_kwh']:.2f} kWh")
print(f"Self-sufficiency improvement: {summary['self_sufficiency_improvement']:.2%}")
