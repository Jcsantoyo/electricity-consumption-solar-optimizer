import matplotlib.pyplot as plt
import pandas as pd


def plot_payback_by_solar_and_battery(
    df: pd.DataFrame,
    battery_capacities_kwh: list[float],
    output_path: str
) -> None:
    plt.figure(figsize=(10, 5))

    for battery_capacity_kwh in battery_capacities_kwh:
        battery_df = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

        plt.plot(
            battery_df["solar_peak_power_kw"],
            battery_df["payback_years"],
            marker="o",
            label=f"{battery_capacity_kwh} kWh battery"
        )

    plt.title("Payback Period by Solar Power and Battery Capacity")
    plt.xlabel("Solar Peak Power (kW)")
    plt.ylabel("Payback Period (years)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
