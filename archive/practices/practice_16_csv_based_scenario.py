from data_loader import load_consumption_data
from solar import generate_daily_solar_profile
from scenarios import compare_battery_scenario


file_path = "data/raw/consumption_sample.csv"

df_consumption = load_consumption_data(file_path)

daily_hourly_consumption_kwh = df_consumption["consumption_kwh"].tolist()

peak_power_kw = 1.0
battery_capacity_kwh = 1.0

battery_efficiency = 0.90
max_charge_power_kw = 1.0
max_discharge_power_kw = 1.0
initial_battery_state_kwh = 0.0

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

print("\nCSV-based scenario simulation:")
print(f"Input file: {file_path}")
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
