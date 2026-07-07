import pandas as pd


from scripts.compare_optimization_results import (
    load_best_scenarios,
    build_optimization_comparison,
)

from visualization import build_comparison_plot_labels


def test_load_best_scenarios_adds_optimization_type_and_renames_criterion(tmp_path):
    input_path = tmp_path / "best_scenarios.csv"

    input_df = pd.DataFrame(
        {
            "criterion": ["best_payback", "best_self_sufficiency"],
            "solar_peak_power_kw": [3.0, 3.0],
            "battery_capacity_kwh": [0.0, 5.0],
            "investment_cost_eur": [3500.0, 6000.0],
            "annual_savings_eur": [684.83, 819.44],
            "payback_years": [5.11, 7.32],
            "self_sufficiency": [0.3158, 0.4398],
            "annual_grid_import_kwh": [6464.45, 5292.28],
        }
    )

    input_df.to_csv(input_path, index=False)

    result_df = load_best_scenarios(str(input_path), optimization_type="historical")

    assert "optimization_type" in result_df.columns
    assert "scenario" in result_df.columns
    assert "criterion" not in result_df.columns

    assert result_df["optimization_type"].tolist() == ["historical", "historical"]

    assert result_df["scenario"].tolist() == ["best_payback", "best_self_sufficiency"]


def test_build_optimization_comparison_combines_historical_and_forecast_data():
    historical_df = pd.DataFrame(
        {
            "optimization_type": ["historical", "historical"],
            "scenario": ["best_payback", "best_self_sufficiency"],
            "solar_peak_power_kw": [3.0, 3.0],
            "battery_capacity_kwh": [0.0, 5.0],
            "investment_cost_eur": [3500.0, 6000.0],
            "annual_savings_eur": [684.83, 819.44],
            "payback_years": [5.11, 7.32],
            "self_sufficiency": [0.3158, 0.4398],
            "annual_grid_import_kwh": [6464.45, 5292.28],
        }
    )

    forecast_df = pd.DataFrame(
        {
            "optimization_type": ["forecast_based", "forecast_based"],
            "scenario": ["best_payback", "best_self_sufficiency"],
            "solar_peak_power_kw": [2.0, 3.0],
            "battery_capacity_kwh": [0.0, 5.0],
            "investment_cost_eur": [2600.0, 6000.0],
            "annual_savings_eur": [551.64, 865.36],
            "payback_years": [4.71, 6.93],
            "self_sufficiency": [0.3046, 0.4996],
            "annual_grid_import_kwh": [6151.91, 4438.78],
        }
    )

    comparison_df = build_optimization_comparison(historical_df, forecast_df)

    assert len(comparison_df) == 4

    assert comparison_df["optimization_type"].tolist() == [
        "historical",
        "historical",
        "forecast_based",
        "forecast_based",
    ]

    assert comparison_df["scenario"].tolist() == [
        "best_payback",
        "best_self_sufficiency",
        "best_payback",
        "best_self_sufficiency",
    ]

    assert "annual_grid_import_kwh" in comparison_df.columns

    assert comparison_df.loc[
        comparison_df["optimization_type"] == "forecast_based", "solar_peak_power_kw"
    ].tolist() == [2.0, 3.0]


def test_build_comparison_plot_labels_creates_readable_labels():
    comparison_df = pd.DataFrame(
        {
            "optimization_type": [
                "historical",
                "historical",
                "forecast_based",
                "forecast_based",
            ],
            "scenario": [
                "best_payback",
                "best_self_sufficiency",
                "best_payback",
                "best_self_sufficiency",
            ],
        }
    )

    labels = build_comparison_plot_labels(comparison_df)

    assert labels.tolist() == [
        "Hist. Payback",
        "Hist. Self-suff.",
        "Forecast Payback",
        "Forecast Self-suff.",
    ]
