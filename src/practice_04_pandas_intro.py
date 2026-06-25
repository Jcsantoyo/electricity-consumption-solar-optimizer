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

print(df.to_string(index=False))

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