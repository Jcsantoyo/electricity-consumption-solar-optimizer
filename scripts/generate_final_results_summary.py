import os
from pathlib import Path

import pandas as pd

def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"

def format_years(value: float) -> str:
    return f"{value:.2f} years"

def format_eur(value: float) -> str:
    return f"{value:.2f} EUR"

def format_eur_per_year(value: float) -> str:
    return f"{value:.2f} EUR/year"

def format_kwh_per_year(value: float) -> str:
    return f"{value:.2f} kWh/year"

def get_scenario(
        comparison_df: pd.DataFrame,
        optimization_type: str,
        scenario: str
) -> pd.Series:
    
    filtered_df = comparison_df[
        (comparison_df["optimization_type"] == optimization_type)
        & (comparison_df["scenario"] == scenario)
    ]

    if filtered_df.empty:
        raise ValueError(f"Scenario not found: {optimization_type} / {scenario}")
    
    return filtered_df.iloc[0]

def format_scenario_section(title: str, scenario_row: pd.Series) -> str:
    lines = [
        f"## {title}",
        "",
        f"- Solar peak power: `{scenario_row['solar_peak_power_kw']:.2f} kW`",
        f"- Battery capacity: `{scenario_row['battery_capacity_kwh']:.2f} kWh`",
        f"- Investment cost: `{format_eur(scenario_row['investment_cost_eur'])}`",
        f"- Annual savings: `{format_eur_per_year(scenario_row['annual_savings_eur'])}`",
        f"- Payback period: `{format_years(scenario_row['payback_years'])}`",
        f"- Self-sufficiency: `{format_percent(scenario_row['self_sufficiency'])}`",
        f"- Annual grid import: `{format_kwh_per_year(scenario_row['annual_grid_import_kwh'])}`",
        ""
    ]

    return "\n".join(lines)


def build_final_results_summary(comparison_df: pd.DataFrame) -> str:

    historical_payback = get_scenario(comparison_df, "historical", "best_payback")

    historical_self_sufficiency = get_scenario(comparison_df, "historical", "best_self_sufficiency")

    forecast_payback = get_scenario(comparison_df, "forecast_based", "best_payback")

    forecast_self_sufficiency = get_scenario(comparison_df, "forecast_based", "best_self_sufficiency")

    lines = [
        "# Final Results Summary",
        "",
        "This report summarizes the main results produced by the full project pipeline.",
        "",
        "It compares historical optimization with forecast-based optimization.",
        "",
        format_scenario_section(
            "Best historical economic scenario",
            historical_payback
        ),
        format_scenario_section(
            "Best historical self-sufficiency scenario",
            historical_self_sufficiency
        ),
        format_scenario_section(
            "Best forecast-based economic scenario",
            forecast_payback
        ),
        format_scenario_section(
            "Best forecast-based self-sufficiency scenario",
            forecast_self_sufficiency
        ),
        "## Main conclusion",
        "",
        "The best economic scenario and the best self-sufficiency scenario are not necessarily the same.",
        "",
        "In the current results, the forecast-based economic optimum can differ from the historical economic optimum.",
        "This means that using predicted future consumption may change the recommended solar and battery configuration.",
        ""
    ]

    return "\n".join(lines)


def main() -> None:

    input_path = "reports/historical_vs_forecast_optimization.csv"
    output_path = "reports/final_results_summary.md"

    comparison_df = pd.read_csv(input_path)


    summary = build_final_results_summary(comparison_df)

    os.makedirs("reports", exist_ok=True)

    Path(output_path).write_text(
        summary,
        encoding="utf-8"
    )

    print("\nFinal results summary generated")
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()