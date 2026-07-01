def calculate_cost(consumption_kwh: float, price_per_kwh: float) -> float:
    cost = consumption_kwh * price_per_kwh
    return cost


# Electricity consumption in kWh
consumption_kwh = 3.5

# Electricity price in euros per kWh
price_per_kwh = 0.18

# Total cost calculation
cost = calculate_cost(consumption_kwh, price_per_kwh)

print("Consumption:", consumption_kwh, "kWh")
print("Price:", price_per_kwh, "EUR/kWh")
print("Cost:", round(cost, 2), "EUR")

print(type(consumption_kwh))
print(type(price_per_kwh))
print(type("Consumption"))

# Daily example
daily_consumption_kwh = 12.4
daily_cost = calculate_cost(daily_consumption_kwh, price_per_kwh)

print("Daily consumption:", daily_consumption_kwh, "kWh")
print("Daily cost:", round(daily_cost, 2), "EUR")