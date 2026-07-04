import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from data_loader import load_consumption_data
from forecasting import run_consumption_forecast
from visualization import(
    plot_forecast_actual_vs_predicted,
    plot_feature_importance
)


def main() -> None:
    data_path = "data/simulated/synthetic_consumption_30_days.csv"

    df = load_consumption_data(data_path)

    forecast_results = run_consumption_forecast(df)

    metrics = forecast_results["metrics"]
    results_df = forecast_results["results_df"]
    feature_importance_df = forecast_results["feature_importance_df"]

    print("\nConsumption forecast results:")
    print(f"MAE: {metrics['mae']:.4f} kWh")
    print(f"RMSE: {metrics['rmse']:.4f} kWh")

    print("\nFirst predictions:")
    print(
        results_df[
            [
                "actual_consumption_kwh",
                "predicted_consumption_kwh"
            ]
        ].head(20).to_string(index=False)
    )

    print("\nFeature importance:")
    print(feature_importance_df.to_string(index=False))

    output_path = "images/consumption_forecast_actual_vs_predicted.png"

    plot_forecast_actual_vs_predicted(
        results_df,
        output_path
    )

    print(f"\nForecast plot saved to: {output_path}")

    feature_importance_output_path = "images/forecast_feature_importance.png"

    plot_feature_importance(feature_importance_df, feature_importance_output_path)

    print(f"Feature importance plot saved to: {feature_importance_output_path}")


if __name__ == "__main__":
    main()