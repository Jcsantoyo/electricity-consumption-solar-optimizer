from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioOutputPaths:
    scenario_name: str
    reports_directory: str
    images_directory: str
    grid_search_results: str
    best_scenarios: str
    summary_report: str
    outputs_index: str
    configuration_summary: str
    run_manifest: str
    payback_plot: str
    self_sufficiency_plot: str
    best_scenarios_comparison_plot: str
    best_scenario_timeseries_plot: str
    best_scenario_timeseries: str
    best_scenario_battery_state_plot: str
    best_scenario_cumulative_energy_plot: str
    forecast_results: str
    forecast_feature_importance: str
    forecast_model_comparison: str
    forecast_model_comparison_plot: str
    forecast_actual_vs_predicted_plot: str
    forecast_feature_importance_plot: str
    forecasted_consumption: str
    forecast_optimization_results: str
    forecast_optimization_best_scenarios: str
    price_mode_comparison_csv: str
    price_mode_comparison_markdown: str
    price_mode_comparison_plot: str
    historical_vs_forecast_comparison: str
    historical_vs_forecast_payback_plot: str
    historical_vs_forecast_savings_plot: str
    historical_vs_forecast_self_sufficiency_plot: str
    historical_vs_forecast_investment_cost_plot: str
    historical_vs_forecast_grid_import_plot: str
    final_results_summary: str

    def create_directories(self) -> None:
        Path(self.reports_directory).mkdir(parents=True, exist_ok=True)
        Path(self.images_directory).mkdir(parents=True, exist_ok=True)

    def all_output_paths(self) -> list[str]:
        return [
            self.grid_search_results,
            self.best_scenarios,
            self.summary_report,
            self.outputs_index,
            self.configuration_summary,
            self.run_manifest,
            self.payback_plot,
            self.self_sufficiency_plot,
            self.best_scenarios_comparison_plot,
            self.best_scenario_timeseries_plot,
            self.best_scenario_timeseries,
            self.best_scenario_battery_state_plot,
            self.best_scenario_cumulative_energy_plot,
            self.forecast_results,
            self.forecast_feature_importance,
            self.forecast_model_comparison,
            self.forecast_model_comparison_plot,
            self.forecast_actual_vs_predicted_plot,
            self.forecast_feature_importance_plot,
            self.forecasted_consumption,
            self.forecast_optimization_results,
            self.forecast_optimization_best_scenarios,
            self.price_mode_comparison_csv,
            self.price_mode_comparison_markdown,
            self.price_mode_comparison_plot,
            self.historical_vs_forecast_comparison,
            self.historical_vs_forecast_payback_plot,
            self.historical_vs_forecast_savings_plot,
            self.historical_vs_forecast_self_sufficiency_plot,
            self.historical_vs_forecast_investment_cost_plot,
            self.historical_vs_forecast_grid_import_plot,
            self.final_results_summary,
        ]


def build_scenario_output_paths(scenario_name: str) -> ScenarioOutputPaths:
    normalized_name = scenario_name.strip()

    if not normalized_name:
        raise ValueError("Scenario name cannot be empty")

    reports = Path("reports") / normalized_name
    images = Path("images") / normalized_name

    return ScenarioOutputPaths(
        scenario_name=normalized_name,
        reports_directory=str(reports),
        images_directory=str(images),
        grid_search_results=str(reports / "grid_search_results.csv"),
        best_scenarios=str(reports / "best_scenarios.csv"),
        summary_report=str(reports / "summary.txt"),
        outputs_index=str(reports / "outputs_index.md"),
        configuration_summary=str(reports / "configuration_summary.md"),
        run_manifest=str(reports / "run_manifest.json"),
        payback_plot=str(images / "main_payback_grid_search.png"),
        self_sufficiency_plot=str(
            images / "main_self_sufficiency_grid_search.png"
        ),
        best_scenarios_comparison_plot=str(
            images / "best_scenarios_comparison.png"
        ),
        best_scenario_timeseries_plot=str(
            images / "best_scenario_timeseries.png"
        ),
        best_scenario_timeseries=str(
            reports / "best_scenario_timeseries.csv"
        ),
        best_scenario_battery_state_plot=str(
            images / "best_scenario_battery_state.png"
        ),
        best_scenario_cumulative_energy_plot=str(
            images / "best_scenario_cumulative_energy.png"
        ),
        forecast_results=str(reports / "forecast_results.csv"),
        forecast_feature_importance=str(
            reports / "forecast_feature_importance.csv"
        ),
        forecast_model_comparison=str(
            reports / "forecast_model_comparison.csv"
        ),
        forecast_model_comparison_plot=str(
            images / "forecast_model_comparison.png"
        ),
        forecast_actual_vs_predicted_plot=str(
            images / "consumption_forecast_actual_vs_predicted.png"
        ),
        forecast_feature_importance_plot=str(
            images / "forecast_feature_importance.png"
        ),
        forecasted_consumption=str(
            reports / "forecasted_consumption_for_optimization.csv"
        ),
        forecast_optimization_results=str(
            reports / "forecast_optimization_results.csv"
        ),
        forecast_optimization_best_scenarios=str(
            reports / "forecast_optimization_best_scenarios.csv"
        ),
        price_mode_comparison_csv=str(
            reports / "electricity_price_mode_comparison.csv"
        ),
        price_mode_comparison_markdown=str(
            reports / "electricity_price_mode_comparison.md"
        ),
        price_mode_comparison_plot=str(
            images / "electricity_price_mode_comparison.png"
        ),
        historical_vs_forecast_comparison=str(
            reports / "historical_vs_forecast_optimization.csv"
        ),
        historical_vs_forecast_payback_plot=str(
            images / "historical_vs_forecast_payback.png"
        ),
        historical_vs_forecast_savings_plot=str(
            images / "historical_vs_forecast_savings.png"
        ),
        historical_vs_forecast_self_sufficiency_plot=str(
            images / "historical_vs_forecast_self_sufficiency.png"
        ),
        historical_vs_forecast_investment_cost_plot=str(
            images / "historical_vs_forecast_investment_cost.png"
        ),
        historical_vs_forecast_grid_import_plot=str(
            images / "historical_vs_forecast_grid_import.png"
        ),
        final_results_summary=str(reports / "final_results_summary.md"),
    )
