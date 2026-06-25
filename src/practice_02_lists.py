hourly_consumption_kwh = [0.30, 0.20, 0.25, 0.27, 0.35]

print(hourly_consumption_kwh[0])
print(hourly_consumption_kwh[1])
print(hourly_consumption_kwh[4])

number_of_hours = len(hourly_consumption_kwh)

print("Number of hours:", number_of_hours)

total_consumption = sum(hourly_consumption_kwh)

print("Total consumption:", total_consumption)

average_consumption = total_consumption / number_of_hours

print("Average consumption:", average_consumption)

price_per_kwh = 0.18

total_cost = total_consumption * price_per_kwh

print("Total cost:", total_cost)

daily_hourly_consumption_kwh = [0.2, 0.15, 0.1, 0.1, 0.1, 0.13, 0.2, 0.23, 0.25, 0.24, 0.25, 0.27, 0.3, 0.35, 0.4, 0.3, 0.3, 0.28, 0.25, 0.25, 0.3, 0.23, 0.2, 0.2]

print("Number of daily records:", len(daily_hourly_consumption_kwh))

daily_total_consumption = sum(daily_hourly_consumption_kwh)

daily_average_consumption = daily_total_consumption / len(daily_hourly_consumption_kwh)

daily_total_cost = price_per_kwh * daily_total_consumption

print("Daily total consumption:", round(daily_total_consumption, 2), "kWh")

print("Daily average consumption:", round(daily_average_consumption, 3), "kWh")

print("Daily total cost:", round(daily_total_cost, 2), "EUR")

print("\nHourly consumption profile:")

for hour, consumption in enumerate(daily_hourly_consumption_kwh):
    print(f"Hour {hour}: {consumption:.2f} kWh")

hourly_costs_eur = []

for hour, consumption in enumerate(daily_hourly_consumption_kwh):
    hourly_cost = consumption * price_per_kwh
    hourly_costs_eur.append(hourly_cost,2)
    
print("\nHourly costs list:")

for hour, cost in enumerate(hourly_costs_eur):
    print(f"Hour {hour}: {cost:.2f} EUR")

max_consumption = max(daily_hourly_consumption_kwh)

peak_hour = daily_hourly_consumption_kwh.index(max_consumption)

print(f"\nPeak consumption occurs at hour {peak_hour} with {max_consumption:.2f} kWh")