import numpy as np
import pandas as pd
import os

start_date = "2025-01-01"
num_days = 30

date_range = pd.date_range(start=start_date, periods=num_days * 24, freq="h")

consumption_values = []

for timestamp in date_range:
    hour = timestamp.hour
    weekday = timestamp.weekday()

    if hour < 6:
        base_consumption = 0.15
    elif hour < 9:
        base_consumption = 0.35
    elif hour < 14:
        base_consumption = 0.25
    elif hour < 18:
        base_consumption = 0.30
    elif hour < 23:
        base_consumption = 0.55
    else:
        base_consumption = 0.25

    if weekday >= 5:
        base_consumption *= 1.15

    random_noise = np.random.normal(loc=0.0, scale=0.05)

    consumption = base_consumption + random_noise

    consumption = max(consumption, 0.05)

    consumption_values.append(consumption)

df = pd.DataFrame({"datetime": date_range, "consumption_kwh": consumption_values})

os.makedirs("data/simulated", exist_ok=True)

output_path = "data/simulated/synthetic_consumption_30_days.csv"

df.to_csv(output_path, index=False)

print("\nSynthetic consumption dataset generated:")
print(f"Output file: {output_path}")
print(f"Number of rows: {len(df)}")
print(f"Start datetime: {df['datetime'].min()}")
print(f"End datetime: {df['datetime'].max()}")
print(f"Total consumption: {df['consumption_kwh'].sum():.2f} kWh")
print(f"Average hourly consumption: {df['consumption_kwh'].mean():.3f} kWh")
