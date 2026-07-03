import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from data_loader import load_consumption_data
from forecasting import run_consumption_forecast


def main() -> None:
    data_path = "data/simulated/synthetic_consumption_30_days.csv"

    df = load_consumption_data(data_path)

    forecast_results = run_consumption_forecast(df)

    metrics = forecast_results["metrics"]
    results_df = forecast_results["results_df"]

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


if __name__ == "__main__":
    main()