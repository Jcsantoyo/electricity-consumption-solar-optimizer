import pandas as pd
import matplotlib.pyplot as plt

def get_price_for_hour(hour: int) -> float:
    if hour < 7:
        return 0.10
    elif hour < 18:
        return 0.18
    else:
        return 0.28
    
daily_hourly_consumption_kwh = [
    0.2, 0.15, 0.1, 0.1, 0.1, 0.13,
    0.2, 0.23, 0.25, 0.24, 0.25, 0.27,
    0.3, 0.35, 0.4, 0.3, 0.3, 0.28,
    0.25, 0.25, 0.3, 0.23, 0.2, 0.2
]

df = pd.DataFrame({
    "hour": range(24),
    "consumption_kwh": daily_hourly_consumption_kwh
})

df["price_eur_per_kwh"] = df["hour"].apply(get_price_for_hour)

df["cost_eur"] = df["consumption_kwh"] * df["price_eur_per_kwh"]

total_consumption = df["consumption_kwh"].sum()
average_consumption = df["consumption_kwh"].mean()
total_cost = df["cost_eur"].sum()


print(f"\nTotal consumption: {total_consumption:.2f} kWh")
print(f"Average hourly consumption: {average_consumption:.3f} kWh")
print(f"Variable tariff total cost: {total_cost:.2f} EUR")


plt.figure(figsize=(10, 5))

plt.plot(df["hour"], df["consumption_kwh"], marker="o")

plt.title("Hourly Electricity Consumption")
plt.xlabel("Hour of Day")
plt.ylabel("Consumption (kWh)")

plt.grid(True)
plt.savefig("images/hourly_consumption.png", dpi=300, bbox_inches="tight")

max_consumption = df["consumption_kwh"].max()

peak_consumption_hour = df.loc[df["consumption_kwh"].idxmax(), "hour"]

print(f"Peak consumption: {max_consumption:.2f} kWh at hour {peak_consumption_hour}")

min_consumption = df["consumption_kwh"].min()

min_consumption_hour = df.loc[df["consumption_kwh"].idxmin(), "hour"]

print(f"Minimum consumption: {min_consumption:.2f} kWh at hour {min_consumption_hour}")

max_hourly_cost = df["cost_eur"].max()

max_cost_hour = df.loc[df["cost_eur"].idxmax(), "hour"]

print(f"Highest hourly cost: {max_hourly_cost:.2f} EUR at hour {max_cost_hour}")

fixed_price_per_hour = 0.18

df["fixed_price_eur_per_kwh"] = fixed_price_per_hour

df["fixed_cost_eur"] = df["fixed_price_eur_per_kwh"] * df["consumption_kwh"]

print(df.to_string(index=False))

fixed_total_cost = df["fixed_cost_eur"].sum()
variable_total_cost = df["cost_eur"].sum()
difference = variable_total_cost - fixed_total_cost

print(f"\nFixed tariff total cost: {fixed_total_cost:.2f} EUR")
print(f"Variable tariff total cost: {variable_total_cost:.2f} EUR")
print(f"Difference: {difference:.2f} EUR")

if variable_total_cost < fixed_total_cost:
    print("Variable tariff is cheaper")
elif variable_total_cost > fixed_total_cost:
    print("Fixed tariff is cheaper")
else:
    print("Both tariffs have the same cost")

plt.figure(figsize=(10, 5))

plt.plot(df["hour"], df["cost_eur"], marker="o", label="Variable tariff")
plt.plot(df["hour"], df["fixed_cost_eur"], marker="o", label="Fixed tariff")

plt.title("Hourly Electricity Cost: Fixed vs Variable Tariff")
plt.xlabel("Hour of Day")
plt.ylabel("Cost (EUR)")

plt.grid(True)
plt.legend()

plt.savefig("images/hourly_cost_comparison.png", dpi=300, bbox_inches="tight")
