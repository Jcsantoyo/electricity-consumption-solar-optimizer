import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

import config
from visualization import (
    plot_historical_vs_forecast_grid_import,
    plot_historical_vs_forecast_investment_cost,
    plot_historical_vs_forecast_payback,
    plot_historical_vs_forecast_savings,
    plot_historical_vs_forecast_self_sufficiency,
)


def load_best_scenarios(file_path: str, optimization_type: str) -> pd.DataFrame:
    df = pd.read_csv(file_path).copy()
    df["optimization_type"] = optimization_type

    if "scenario" not in df.columns:
        if "criterion" in df.columns:
            df = df.rename(columns={"criterion": "scenario"})
        elif "selection_criterion" in df.columns:
            df = df.rename(columns={"selection_criterion": "scenario"})
        else:
            df["scenario"] = ["best_payback", "best_self_sufficiency"][: len(df)]

    return df


def build_optimization_comparison(
    historical_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    comparison_df = pd.concat([historical_df, forecast_df], ignore_index=True)

    columns = [
        "optimization_type",
        "scenario",
        "solar_peak_power_kw",
        "battery_capacity_kwh",
        "investment_cost_eur",
        "annual_savings_eur",
        "payback_years",
        "self_sufficiency",
        "annual_grid_import_kwh",
    ]

    return comparison_df[columns]


def main() -> None:
    paths = config.OUTPUT_PATHS
    paths.create_directories()

    historical_path = paths.best_scenarios
    forecast_path = paths.forecast_optimization_best_scenarios
    output_path = paths.historical_vs_forecast_comparison

    historical_df = load_best_scenarios(
        historical_path,
        optimization_type="historical",
    )
    forecast_df = load_best_scenarios(
        forecast_path,
        optimization_type="forecast_based",
    )

    comparison_df = build_optimization_comparison(
        historical_df,
        forecast_df,
    )
    comparison_df.to_csv(output_path, index=False)

    plot_historical_vs_forecast_payback(
        comparison_df,
        paths.historical_vs_forecast_payback_plot,
    )
    plot_historical_vs_forecast_savings(
        comparison_df,
        paths.historical_vs_forecast_savings_plot,
    )
    plot_historical_vs_forecast_self_sufficiency(
        comparison_df,
        paths.historical_vs_forecast_self_sufficiency_plot,
    )
    plot_historical_vs_forecast_investment_cost(
        comparison_df,
        paths.historical_vs_forecast_investment_cost_plot,
    )
    plot_historical_vs_forecast_grid_import(
        comparison_df,
        paths.historical_vs_forecast_grid_import_plot,
    )

    print("\nHistorical vs forecast-based optimization comparison")
    print(f"Historical results: {historical_path}")
    print(f"Forecast-based results: {forecast_path}")
    print(f"Comparison saved to: {output_path}")
    print(f"Payback plot saved to: {paths.historical_vs_forecast_payback_plot}")
    print(f"Savings plot saved to: {paths.historical_vs_forecast_savings_plot}")
    print(
        "Self-sufficiency plot saved to: "
        f"{paths.historical_vs_forecast_self_sufficiency_plot}"
    )
    print(
        "Investment cost plot saved to: "
        f"{paths.historical_vs_forecast_investment_cost_plot}"
    )
    print(f"Grid import plot saved to: {paths.historical_vs_forecast_grid_import_plot}")

    print("\nComparison:")
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()
