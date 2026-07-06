import os
import pandas as pd


def load_best_scenarios(
    file_path: str,
    optimization_type: str
) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    df = df.copy()
    df["optimization_type"] = optimization_type

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

    available_columns = [
        column for column in columns
        if column in comparison_df.columns
    ]

    comparison_df = comparison_df[available_columns]

    return comparison_df


def main() -> None:
    historical_path = "reports/best_scenarios.csv"
    forecast_path = "reports/forecast_optimization_best_scenarios.csv"
    output_path = "reports/historical_vs_forecast_optimization.csv"

    os.makedirs("reports", exist_ok=True)

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

    print("\nHistorical vs forecast-based optimization comparison")
    print(f"Historical results: {historical_path}")
    print(f"Forecast-based results: {forecast_path}")
    print(f"Comparison saved to: {output_path}")

    print("\nComparison:")
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()