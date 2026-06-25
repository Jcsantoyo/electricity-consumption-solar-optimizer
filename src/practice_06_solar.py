from solar import( 
    generate_daily_solar_profile,
    simulate_self_consumption
)

daily_hourly_consumption_kwh = [
    0.2, 0.15, 0.1, 0.1, 0.1, 0.13,
    0.2, 0.23, 0.25, 0.24, 0.25, 0.27,
    0.3, 0.35, 0.4, 0.3, 0.3, 0.28,
    0.25, 0.25, 0.3, 0.23, 0.2, 0.2
]

peak_power_kw = 3.0

daily_solar_generation_kwh = generate_daily_solar_profile(peak_power_kw)

for hour, solar_generation in enumerate(daily_solar_generation_kwh):
    print(f"Hour {hour:02d}: {solar_generation:.2f} kWh")

total_solar_generation = sum(daily_solar_generation_kwh)

print(f"\nTotal daily solar generation: {total_solar_generation:.2f} kWh")

self_consumed_kwh, grid_import_kwh, solar_surplus_kwh = simulate_self_consumption(daily_hourly_consumption_kwh, daily_solar_generation_kwh)


print("\nHour | Consumption | Solar | Self-consumed | Grid import | Surplus")

for hour in range(24):
    print(
        f"{hour:02d} | "
        f"{daily_hourly_consumption_kwh[hour]:.2f} kWh | "
        f"{daily_solar_generation_kwh[hour]:.2f} kWh | "
        f"{self_consumed_kwh[hour]:.2f} kWh | "
        f"{grid_import_kwh[hour]:.2f} kWh | "
        f"{solar_surplus_kwh[hour]:.2f} kWh"
    )

total_consumption = sum(daily_hourly_consumption_kwh)
total_self_consumed = sum(self_consumed_kwh)
total_grid_import = sum(grid_import_kwh)
total_solar_surplus = sum(solar_surplus_kwh)

print("\nDaily energy balance:")
print(f"Total consumption: {total_consumption:.2f} kWh")
print(f"Total solar generation: {total_solar_generation:.2f} kWh")
print(f"Total self-consumed energy: {total_self_consumed:.2f} kWh")
print(f"Total grid import: {total_grid_import:.2f} kWh")
print(f"Total solar surplus: {total_solar_surplus:.2f} kWh")

if total_solar_generation > 0:
    self_consumption_ratio = total_self_consumed / total_solar_generation
else:
    self_consumption_ratio = 0

if total_consumption > 0:
    self_sufficiency_ratio = total_self_consumed / total_consumption
else:
    self_sufficiency_ratio = 0

print(f"Self-consumption ratio: {self_consumption_ratio:.2%}")
print(f"Self-sufficiency ratio: {self_sufficiency_ratio:.2%}")