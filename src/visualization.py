import matplotlib.pyplot as plt
import pandas as pd


def plot_payback_by_solar_and_battery(
    df: pd.DataFrame, battery_capacities_kwh: list[float], output_path: str
) -> None:
    plt.figure(figsize=(10, 5))

    for battery_capacity_kwh in battery_capacities_kwh:
        battery_df = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

        plt.plot(
            battery_df["solar_peak_power_kw"],
            battery_df["payback_years"],
            marker="o",
            label=f"{battery_capacity_kwh} kWh battery",
        )

    plt.title("Payback Period by Solar Power and Battery Capacity")
    plt.xlabel("Solar Peak Power (kW)")
    plt.ylabel("Payback Period (years)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_self_sufficiency_by_solar_and_battery(
    df: pd.DataFrame, battery_capacities_kwh: list[float], output_path: str
) -> None:
    plt.figure(figsize=(10, 5))

    for battery_capacity_kwh in battery_capacities_kwh:
        battery_df = df[df["battery_capacity_kwh"] == battery_capacity_kwh]

        plt.plot(
            battery_df["solar_peak_power_kw"],
            battery_df["self_sufficiency"] * 100,
            marker="o",
            label=f"{battery_capacity_kwh} kWh battery",
        )

    plt.title("Self-Sufficiency by Solar Power and Battery Capacity")
    plt.xlabel("Solar Peak Power (kW)")
    plt.ylabel("Self-Sufficiency (%)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_best_scenarios_comparison(
    best_scenarios_df: pd.DataFrame, output_path: str
) -> None:
    labels = best_scenarios_df["criterion"]

    payback_years = best_scenarios_df["payback_years"]

    x = range(len(labels))

    plt.figure(figsize=(8, 5))

    plt.bar(x, payback_years)

    plt.title("Best Scenarios Comparison: Payback")
    plt.xlabel("Scenario")
    plt.ylabel("Payback Period (years)")
    plt.xticks(x, labels, rotation=15)
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    print("\nBest scenarios comparison data:")
    for index, row in best_scenarios_df.iterrows():
        print(f"\nScenario: {row['criterion']}")
        print(f"Investment cost: {row['investment_cost_eur']:.2f} EUR")
        print(f"Annual savings: {row['annual_savings_eur']:.2f} EUR/year")
        print(f"Payback: {row['payback_years']:.2f} years")
        print(f"Self-sufficiency: {row['self_sufficiency']:.2%}")


def plot_best_scenario_timeseries(df: pd.DataFrame, output_path: str) -> None:
    plt.figure(figsize=(12, 5))

    plt.plot(df["datetime"], df["consumption_kwh"], label="Consumption")

    plt.plot(df["datetime"], df["solar_generation_kwh"], label="Solar generation")

    plt.plot(df["datetime"], df["grid_import_kwh"], label="Grid import")

    plt.title("Best Scenario Energy Flows Over Time")
    plt.xlabel("Datetime")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_battery_state_over_time(df: pd.DataFrame, output_path: str) -> None:
    plt.figure(figsize=(12, 5))

    plt.plot(df["datetime"], df["battery_state_kwh"], label="Battery state")

    plt.title("Battery State of Charge Over Time")
    plt.xlabel("Datetime")
    plt.ylabel("Battery State (kWh)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_cumulative_energy_flows(df: pd.DataFrame, output_path: str) -> None:
    cumulative_grid_import = df["grid_import_kwh"].cumsum()
    cumulative_solar_surplus = df["solar_surplus_kwh"].cumsum()
    cumulative_consumption = df["consumption_kwh"].cumsum()
    cumulative_solar_generation = df["solar_generation_kwh"].cumsum()

    plt.figure(figsize=(12, 5))

    plt.plot(df["datetime"], cumulative_consumption, label="Cumulative consumption")

    plt.plot(
        df["datetime"], cumulative_solar_generation, label="Cumulative solar generation"
    )

    plt.plot(df["datetime"], cumulative_grid_import, label="Cumulative grid import")

    plt.plot(df["datetime"], cumulative_solar_surplus, label="Cumulative solar surplus")

    plt.title("Cumulative Energy Flows Over Time")
    plt.xlabel("Datetime")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_forecast_actual_vs_predicted(
    results_df: pd.DataFrame, output_path: str
) -> None:
    plt.figure(figsize=(12, 5))

    plt.plot(
        results_df.index,
        results_df["actual_consumption_kwh"],
        label="Actual Consumption",
    )

    plt.plot(
        results_df.index,
        results_df["predicted_consumption_kwh"],
        label="Predicted Consumption",
    )

    plt.title("Consumption Forecast: Actual vs Predicted")
    plt.xlabel("Test sample")
    plt.ylabel("Consumption (kWh)")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_feature_importance(
    feature_importance_df: pd.DataFrame, output_path: str
) -> None:

    plt.figure(figsize=(10, 5))

    plt.barh(feature_importance_df["feature"], feature_importance_df["importance"])

    plt.title("Forecast Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.gca().invert_yaxis()
    plt.grid(axis="x")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_forecasting_model_comparison(
    comparison_df: pd.DataFrame, output_path: str
) -> None:
    plt.figure(figsize=(8, 5))

    plt.bar(comparison_df["model"], comparison_df["mae"])

    plt.title("Forecasting Model Comparison")
    plt.xlabel("Model")
    plt.ylabel("MAE (kWh)")
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def build_comparison_plot_labels(comparison_df: pd.DataFrame) -> pd.Series:
    labels = []

    for _, row in comparison_df.iterrows():
        optimization_type = row["optimization_type"]
        scenario = row["scenario"]

        if optimization_type == "historical":
            optimization_label = "Hist."
        elif optimization_type == "forecast_based":
            optimization_label = "Forecast"
        else:
            optimization_label = str(optimization_type)

        if scenario == "best_payback":
            scenario_label = "Payback"
        elif scenario == "best_self_sufficiency":
            scenario_label = "Self-suff."
        else:
            scenario_label = str(scenario)

        labels.append(f"{optimization_label} {scenario_label}")

    return pd.Series(labels, index=comparison_df.index)


def plot_historical_vs_forecast_payback(
    comparison_df: pd.DataFrame, output_path: str
) -> None:
    comparison_df = comparison_df.copy()

    label_values = build_comparison_plot_labels(comparison_df)

    plt.figure(figsize=(10, 5))

    plt.bar(label_values, comparison_df["payback_years"])

    plt.title("Historical vs Forecast-Based Optimization Payback")
    plt.xlabel("Scenario")
    plt.ylabel("Payback (years)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_historical_vs_forecast_savings(
    comparison_df: pd.DataFrame, output_path: str
) -> None:
    comparison_df = comparison_df.copy()

    label_values = build_comparison_plot_labels(comparison_df)

    plt.figure(figsize=(10, 5))

    plt.bar(label_values, comparison_df["annual_savings_eur"])

    plt.title("Historical vs Forecast-Based Annual Savings")
    plt.xlabel("Scenario")
    plt.ylabel("Annual savings (EUR/year)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_historical_vs_forecast_self_sufficiency(
    comparison_df: pd.DataFrame, output_path: str
) -> None:
    comparison_df = comparison_df.copy()

    label_values = build_comparison_plot_labels(comparison_df)

    self_sufficiency_percent = comparison_df["self_sufficiency"] * 100

    plt.figure(figsize=(10, 5))

    plt.bar(label_values, self_sufficiency_percent)

    plt.title("Historical vs Forecast-Based Self-Sufficiency")
    plt.xlabel("Scenario")
    plt.ylabel("Self-sufficiency (%)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_historical_vs_forecast_investment_cost(
    comparison_df: pd.DataFrame, output_path: str
) -> None:
    comparison_df = comparison_df.copy()

    label_values = build_comparison_plot_labels(comparison_df)

    plt.figure(figsize=(10, 5))

    plt.bar(label_values, comparison_df["investment_cost_eur"])

    plt.title("Historical vs Forecast-Based Investment Cost")
    plt.xlabel("Scenario")
    plt.ylabel("Investment cost (EUR)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_historical_vs_forecast_grid_import(
    comparison_df: pd.DataFrame, output_path: str
) -> None:
    comparison_df = comparison_df.copy()

    label_values = build_comparison_plot_labels(comparison_df)

    plt.figure(figsize=(10, 5))

    plt.bar(label_values, comparison_df["annual_grid_import_kwh"])

    plt.title("Historical vs Forecast-Based Annual Grid Import")
    plt.xlabel("Scenario")
    plt.ylabel("Annual grid import (kWh/year)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
