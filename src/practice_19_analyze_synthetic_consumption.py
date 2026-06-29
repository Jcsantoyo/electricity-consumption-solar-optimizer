import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_consumption_data


file_path = "data/simulated/synthetic_consumption_30_days.csv"

df = load_consumption_data(file_path)

print("\nSynthetic consumption data loaded:")
print(f"Input file: {file_path}")
print(f"Number of rows: {len(df)}")
print(f"Start datetime: {df['datetime'].min()}")
print(f"End datetime: {df['datetime'].max()}")

total_consumption = df["consumption_kwh"].sum()
average_consumption = df["consumption_kwh"].mean()
max_consumption = df["consumption_kwh"].max()
min_consumption = df["consumption_kwh"].min()

print("\nConsumption summary:")
print(f"Total consumption: {total_consumption:.2f} kWh")
print(f"Average hourly consumption: {average_consumption:.3f} kWh")
print(f"Maximum hourly consumption: {max_consumption:.2f} kWh")
print(f"Minimum hourly consumption: {min_consumption:.2f} kWh")

daily_consumption = (
    df.groupby(df["datetime"].dt.date)["consumption_kwh"]
    .sum()
    .reset_index()
)

daily_consumption.columns = ["date", "daily_consumption_kwh"]

print("\nDaily consumption:")
print(daily_consumption.to_string(index=False))

average_consumption_by_hour = (
    df.groupby("hour")["consumption_kwh"]
    .mean()
    .reset_index()
)

print("\nAverage consumption by hour:")
print(average_consumption_by_hour.to_string(index=False))

plt.figure(figsize=(12, 5))

plt.plot(
    df["datetime"],
    df["consumption_kwh"]
)

plt.title("Hourly Consumption Over 30 Days")
plt.xlabel("Datetime")
plt.ylabel("Consumption (kWh)")
plt.grid(True)

plt.savefig("images/hourly_consumption_30_days.png", dpi=300, bbox_inches="tight")

plt.figure(figsize=(10, 5))

plt.plot(
    daily_consumption["date"],
    daily_consumption["daily_consumption_kwh"],
    marker="o"
)

plt.title("Daily Consumption Over 30 Days")
plt.xlabel("Date")
plt.ylabel("Daily Consumption (kWh)")
plt.xticks(rotation=45)
plt.grid(True)

plt.savefig("images/daily_consumption_30_days.png", dpi=300, bbox_inches="tight")

plt.figure(figsize=(10, 5))

plt.plot(
    average_consumption_by_hour["hour"],
    average_consumption_by_hour["consumption_kwh"],
    marker="o"
)

plt.title("Average Consumption by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Average Consumption (kWh)")
plt.xticks(range(24))
plt.grid(True)

plt.savefig("images/average_consumption_by_hour.png", dpi=300, bbox_inches="tight")

