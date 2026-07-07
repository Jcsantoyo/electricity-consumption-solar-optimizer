import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from data_loader import load_consumption_data
from forecasting import run_consumption_forecast, compare_forecasting_models
from visualization import (
    plot_forecast_actual_vs_predicted,
    plot_feature_importance,
    plot_forecasting_model_comparison,
)


def main() -> None:
    data_path = "data/processed/uci_household_power_hourly.csv"

    df = load_consumption_data(data_path)

    os.makedirs("reports", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    forecast_results = run_consumption_forecast(df)

    metrics = forecast_results["metrics"]
    results_df = forecast_results["results_df"]
    feature_importance_df = forecast_results["feature_importance_df"]

    forecast_results_output_path = "reports/forecast_results.csv"

    results_df.to_csv(forecast_results_output_path, index=False)

    print(f"\nForecast results saved to: {forecast_results_output_path}")

    print("\nConsumption forecast results:")
    print(f"MAE: {metrics['mae']:.4f} kWh")
    print(f"RMSE: {metrics['rmse']:.4f} kWh")

    print("\nFirst predictions:")
    print(
        results_df[["actual_consumption_kwh", "predicted_consumption_kwh"]]
        .head(20)
        .to_string(index=False)
    )

    print("\nFeature importance:")
    print(feature_importance_df.to_string(index=False))

    feature_importance_report_path = "reports/forecast_feature_importance.csv"

    feature_importance_df.to_csv(feature_importance_report_path, index=False)

    print(f"Feature importance report saved to: {feature_importance_report_path}")

    comparison_df = compare_forecasting_models(df)

    print("\nModel comparison:")
    print(comparison_df.to_string(index=False))

    model_comparison_report_path = "reports/forecast_model_comparison.csv"

    comparison_df.to_csv(model_comparison_report_path, index=False)

    print(f"Model comparison report saved to: {model_comparison_report_path}")

    model_comparison_output_path = "images/forecast_model_comparison.png"

    plot_forecasting_model_comparison(comparison_df, model_comparison_output_path)

    print(f"Model comparison plot saved to: {model_comparison_output_path}")

    output_path = "images/consumption_forecast_actual_vs_predicted.png"

    plot_forecast_actual_vs_predicted(results_df, output_path)

    print(f"\nForecast plot saved to: {output_path}")

    feature_importance_output_path = "images/forecast_feature_importance.png"

    plot_feature_importance(feature_importance_df, feature_importance_output_path)

    print(f"Feature importance plot saved to: {feature_importance_output_path}")


if __name__ == "__main__":
    main()
