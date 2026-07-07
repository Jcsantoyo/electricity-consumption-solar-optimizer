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
battery_capacity_kwh = 2.0

daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

summary = compare_battery_scenario(
    daily_hourly_consumption_kwh,
    daily_solar_generation_kwh,
    battery_capacity_kwh,
    battery_efficiency=0.90,
    max_charge_power_kw=1.0,
    max_discharge_power_kw=1.0,
    initial_battery_state_kwh=0.0,
)

print("\nBattery scenario comparison:")
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
