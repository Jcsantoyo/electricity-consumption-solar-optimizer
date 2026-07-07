def get_price_for_hour(hour: int) -> float:
    if hour < 7:
        return 0.10
    elif hour < 18:
        return 0.18
    else:
        return 0.28


def calculate_fixed_tariff_cost(
    consumption_kwh: list[float], price_per_kwh: float
) -> float:
    total_consumption = sum(consumption_kwh)
    total_cost = total_consumption * price_per_kwh
    return total_cost


def calculate_variable_tariff_cost(
    consumption_kwh: list[float],
) -> tuple[float, list[float], list[float]]:
    variable_hourly_costs_eur = []
    hourly_prices_eur_per_kwh = []
    for hour, consumption in enumerate(consumption_kwh):
        hourly_price = get_price_for_hour(hour)
        hourly_cost = hourly_price * consumption
        variable_hourly_costs_eur.append(hourly_cost)
        hourly_prices_eur_per_kwh.append(hourly_price)

    variable_total_cost = sum(variable_hourly_costs_eur)
    return variable_total_cost, variable_hourly_costs_eur, hourly_prices_eur_per_kwh


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


variable_total_cost, variable_hourly_costs_eur, hourly_prices_eur_per_kwh = (
    calculate_variable_tariff_cost(daily_hourly_consumption_kwh)
)

print(f"\nVariable total cost: {variable_total_cost:.2f} EUR")

fixed_price_per_kwh = 0.18

fixed_total_cost = calculate_fixed_tariff_cost(
    daily_hourly_consumption_kwh, fixed_price_per_kwh
)

print(f"Fixed tariff total cost: {fixed_total_cost:.2f} EUR")

if variable_total_cost < fixed_total_cost:
    print("Variable tariff is cheaper")
elif variable_total_cost > fixed_total_cost:
    print("Fixed tariff is cheaper")
else:
    print("Both tariffs have the same cost")

print("\nHourly tariff table:")
print("Hour | Consumption | Price | Cost")

for hour, consumption in enumerate(daily_hourly_consumption_kwh):
    price = hourly_prices_eur_per_kwh[hour]
    cost = variable_hourly_costs_eur[hour]

    print(f"{hour:02d} | {consumption:.2f} kWh | {price:.2f} EUR/kWh | {cost:.2f} EUR")
