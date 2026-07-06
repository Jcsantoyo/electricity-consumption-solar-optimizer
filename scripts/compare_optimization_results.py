import os
import pandas as pd

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from visualization import (
    plot_historical_vs_forecast_payback,
    plot_historical_vs_forecast_savings,
    plot_historical_vs_forecast_self_sufficiency
)

def load_best_scenarios(
    file_path: str,
    optimization_type: str
) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    df = df.copy()
    df["optimization_type"] = optimization_type

    if "scenario" not in df.columns:
        if "criterion" in df.columns:
            df = df.rename(
                columns={
                    "criterion": "scenario"
                }
            )
        elif "selection_criterion" in df.columns:
            df = df.rename(
                columns={
                    "selection_criterion": "scenario"
                }
            )
        else:
            df["scenario"] = [
                "best_payback",
                "best_self_sufficiency"
            ][:len(df)]

    return df


def build_optimization_comparison(
    historical_df: pd.DataFrame,
    forecast_df: pd.DataFrame
) -> pd.DataFrame:
    comparison_df = pd.concat(
        [
            historical_df,
            forecast_df
        ],
        ignore_index=True
    )

    columns = [
        "optimization_type",
        "scenario",
        "solar_peak_power_kw",
        "battery_capacity_kwh",
        "investment_cost_eur",
        "annual_savings_eur",
        "payback_years",
        "self_sufficiency"
    ]

    comparison_df = comparison_df[columns]

    return comparison_df


def main() -> None:
    historical_path = "reports/best_scenarios.csv"
    forecast_path = "reports/forecast_optimization_best_scenarios.csv"
    output_path = "reports/historical_vs_forecast_optimization.csv"
    plot_output_path = "images/historical_vs_forecast_payback.png"

    payback_plot_path = "images/historical_vs_forecast_payback.png"
    savings_plot_path = "images/historical_vs_forecast_savings.png"
    self_sufficiency_plot_path = "images/historical_vs_forecast_self_sufficiency.png"

    os.makedirs("reports", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    historical_df = load_best_scenarios(
        historical_path,
        optimization_type="historical"
    )

    forecast_df = load_best_scenarios(
        forecast_path,
        optimization_type="forecast_based"
    )

    comparison_df = build_optimization_comparison(
        historical_df,
        forecast_df
    )

    comparison_df.to_csv(
        output_path,
        index=False
    )

    plot_historical_vs_forecast_payback(comparison_df, plot_output_path)

    plot_historical_vs_forecast_payback(comparison_df, payback_plot_path)

    plot_historical_vs_forecast_savings(comparison_df, savings_plot_path)

    plot_historical_vs_forecast_self_sufficiency(comparison_df, self_sufficiency_plot_path)

    print("\nHistorical vs forecast-based optimization comparison")
    print(f"Historical results: {historical_path}")
    print(f"Forecast-based results: {forecast_path}")
    print(f"Comparison saved to: {output_path}")
    print(f"Comparison plot saved to: {plot_output_path}")
    print(f"Payback plot saved to: {payback_plot_path}")
    print(f"Savings plot saved to: {savings_plot_path}")
    print(f"Self-sufficiency plot saved to: {self_sufficiency_plot_path}")

    print("\nComparison:")
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()