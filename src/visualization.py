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

def plot_self_sufficiency_by_solar_and_battery(
    df: pd.DataFrame,
    battery_capacities_kwh: list[float],
    output_path: str
) -> None:
    plt.figure(figsize=(10, 5))

    for battery_capacity_kwh in battery_capacities_kwh:
        battery_df = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

        plt.plot(
            battery_df["solar_peak_power_kw"],
            battery_df["self_sufficiency"] * 100,
            marker="o",
            label=f"{battery_capacity_kwh} kWh battery"
        )

    plt.title("Self-Sufficiency by Solar Power and Battery Capacity")
    plt.xlabel("Solar Peak Power (kW)")
    plt.ylabel("Self-Sufficiency (%)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")

def plot_best_scenarios_comparison(
    best_scenarios_df: pd.DataFrame,
    output_path: str
) -> None:
    labels = best_scenarios_df["criterion"]

    payback_years = best_scenarios_df["payback_years"]
    self_sufficiency_percent = best_scenarios_df["self_sufficiency"] * 100
    investment_cost = best_scenarios_df["investment_cost_eur"]

    x = range(len(labels))

    plt.figure(figsize=(8, 5))

    plt.bar(x, payback_years)

    plt.title("Best Scenarios Comparison: Payback")
    plt.xlabel("Scenario")
    plt.ylabel("Payback Period (years)")
    plt.xticks(x, labels, rotation=15)
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()

    print("\nBest scenarios comparison data:")
    for index, row in best_scenarios_df.iterrows():
        print(f"\nScenario: {row['criterion']}")
        print(f"Investment cost: {row['investment_cost_eur']:.2f} EUR")
        print(f"Annual savings: {row['annual_savings_eur']:.2f} EUR/year")
        print(f"Payback: {row['payback_years']:.2f} years")
        print(f"Self-sufficiency: {row['self_sufficiency']:.2%}")

def plot_best_scenario_timeseries(
    df: pd.DataFrame,
    output_path: str
) -> None:
    plt.figure(figsize=(12, 5))

    plt.plot(
        df["datetime"],
        df["consumption_kwh"],
        label="Consumption"
    )

    plt.plot(
        df["datetime"],
        df["solar_generation_kwh"],
        label="Solar generation"
    )

    plt.plot(
        df["datetime"],
        df["grid_import_kwh"],
        label="Grid import"
    )

    plt.title("Best Scenario Energy Flows Over Time")
    plt.xlabel("Datetime")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
