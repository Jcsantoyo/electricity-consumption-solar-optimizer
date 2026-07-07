from tariff import (
    calculate_fixed_tariff_cost,
    calculate_variable_tariff_cost,
)

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

fixed_price_per_kwh = 0.18

fixed_total_cost = calculate_fixed_tariff_cost(
    daily_hourly_consumption_kwh, fixed_price_per_kwh
)

variable_total_cost, hourly_costs, hourly_prices = calculate_variable_tariff_cost(
    daily_hourly_consumption_kwh
)

print(f"Fixed tariff total cost: {fixed_total_cost:.2f} EUR")
print(f"Variable tariff total cost: {variable_total_cost:.2f} EUR")
