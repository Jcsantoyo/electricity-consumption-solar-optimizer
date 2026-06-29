from data_loader import load_consumption_data

file_path = "data/raw/consumption_sample.csv"

df = load_consumption_data(file_path)

print("\nLoaded consumption data:")
print(df.to_string(index=False))

total_consumption = df["consumption_kwh"].sum()
average_consumption = df["consumption_kwh"].mean()
peak_consumption = df["consumption_kwh"].max()
peak_consumption_hour = df.loc[df["consumption_kwh"].idxmax(), "hour"]

print("\nConsumption summary:")
print(f"Total consumption: {total_consumption:.2f} kWh")
print(f"Average hourly consumption: {average_consumption:.3f} kWh")
print(f"Peak consumption: {peak_consumption:.2f} kWh")
print(f"Peak consumption hour: {peak_consumption_hour}")