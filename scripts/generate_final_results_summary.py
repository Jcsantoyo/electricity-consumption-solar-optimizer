import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

import config


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


def format_optional_years(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "Not achieved"

    return f"{value:.2f} years"


def format_optional_percent(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "Not available"

    return f"{value * 100:.2f}%"


def get_scenario(
    comparison_df: pd.DataFrame,
    optimization_type: str,
    scenario: str,
) -> pd.Series:
    filtered_df = comparison_df[
        (comparison_df["optimization_type"] == optimization_type)
        & (comparison_df["scenario"] == scenario)
    ]

    if filtered_df.empty:
        raise ValueError(f"Scenario not found: {optimization_type} / {scenario}")

    return filtered_df.iloc[0]


SCENARIO_DISPLAY_NAMES = {
    ("historical", "best_payback"): "Historical · Best payback",
    (
        "historical",
        "best_net_present_value",
    ): "Historical · Best NPV",
    (
        "historical",
        "best_self_sufficiency",
    ): "Historical · Best self-sufficiency",
    (
        "forecast_based",
        "best_payback",
    ): "Forecast · Best payback",
    (
        "forecast_based",
        "best_net_present_value",
    ): "Forecast · Best NPV",
    (
        "forecast_based",
        "best_self_sufficiency",
    ): "Forecast · Best self-sufficiency",
}


def get_scenario_display_name(
    optimization_type: str,
    scenario: str,
) -> str:
    key = (
        optimization_type,
        scenario,
    )

    if key not in SCENARIO_DISPLAY_NAMES:
        raise ValueError(
            f"Unknown scenario display name: {optimization_type} / {scenario}"
        )

    return SCENARIO_DISPLAY_NAMES[key]


SCENARIO_COMPARISON_TABLE_COLUMNS = {
    "optimization_type",
    "scenario",
    "solar_peak_power_kw",
    "battery_capacity_kwh",
    "investment_cost_eur",
    "annual_savings_eur",
    "payback_years",
    "net_present_value_eur",
    "discounted_payback_years",
    "internal_rate_of_return",
    "self_sufficiency",
}


def validate_scenario_comparison_dataframe(
    comparison_df: pd.DataFrame,
) -> None:
    missing_columns = SCENARIO_COMPARISON_TABLE_COLUMNS - set(comparison_df.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"Scenario comparison data is missing required columns: {missing_text}"
        )


def scenarios_use_same_configuration(
    first_scenario: pd.DataFrame, second_scenario: pd.Series
) -> bool:
    return float(first_scenario["solar_peak_power_kw"]) == float(
        second_scenario["solar_peak_power_kw"]
    ) and float(first_scenario["battery_capacity_kwh"]) == float(
        second_scenario["battery_capacity_kwh"]
    )


def build_scenario_comparison_table(
    comparison_df: pd.DataFrame,
) -> str:
    validate_scenario_comparison_dataframe(comparison_df)

    scenario_order = [
        (
            "historical",
            "best_payback",
        ),
        (
            "historical",
            "best_net_present_value",
        ),
        (
            "historical",
            "best_self_sufficiency",
        ),
        (
            "forecast_based",
            "best_payback",
        ),
        (
            "forecast_based",
            "best_net_present_value",
        ),
        (
            "forecast_based",
            "best_self_sufficiency",
        ),
    ]

    lines = [
        "| Scenario | Solar | Battery | Investment | "
        "Annual savings | Simple payback | NPV | "
        "Discounted payback | IRR | Self-sufficiency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for optimization_type, scenario_name in scenario_order:
        scenario = get_scenario(
            comparison_df,
            optimization_type,
            scenario_name,
        )

        display_name = get_scenario_display_name(
            optimization_type,
            scenario_name,
        )

        lines.append(
            "| "
            f"{display_name} | "
            f"{scenario['solar_peak_power_kw']:.2f} kW | "
            f"{scenario['battery_capacity_kwh']:.2f} kWh | "
            f"{format_eur(scenario['investment_cost_eur'])} | "
            f"{format_eur_per_year(scenario['annual_savings_eur'])} | "
            f"{format_years(scenario['payback_years'])} | "
            f"{format_eur(scenario['net_present_value_eur'])} | "
            f"{format_optional_years(scenario['discounted_payback_years'])} | "
            f"{format_optional_percent(scenario['internal_rate_of_return'])} | "
            f"{format_percent(scenario['self_sufficiency'])} |"
        )

    return "\n".join(lines)


def build_scenario_comparison_section(
    comparison_df: pd.DataFrame,
) -> str:
    table = build_scenario_comparison_table(comparison_df)

    lines = [
        "## Scenario comparison",
        "",
        (
            "The following table compares the main technical and "
            "financial metrics of the six selected scenarios."
        ),
        "",
        table,
        "",
    ]

    return "\n".join(lines)


def build_optimization_conclusion(
    historical_payback: pd.Series,
    historical_npv: pd.Series,
    historical_self_sufficiency: pd.Series,
    forecast_payback: pd.Series,
    forecast_npv: pd.Series,
    forecast_self_sufficiency: pd.Series,
) -> str:
    historical_payback_matches_npv = scenarios_use_same_configuration(
        historical_payback,
        historical_npv,
    )
    forecast_payback_matches_npv = scenarios_use_same_configuration(
        forecast_payback,
        forecast_npv,
    )

    historical_npv_matches_self_sufficiency = scenarios_use_same_configuration(
        historical_npv,
        historical_self_sufficiency,
    )
    forecast_npv_matches_self_sufficiency = scenarios_use_same_configuration(
        forecast_npv,
        forecast_self_sufficiency,
    )

    lines = [
        "## Main conclusion",
        "",
    ]

    if historical_payback_matches_npv:
        lines.append(
            "For the historical optimization, the configuration with the "
            "shortest payback also provides the highest net present value."
        )
    else:
        lines.append(
            "For the historical optimization, the configuration with the "
            "shortest payback differs from the configuration with the "
            "highest net present value."
        )

    lines.append("")

    if forecast_payback_matches_npv:
        lines.append(
            "For the forecast-based optimization, the configuration with "
            "the shortest payback also provides the highest net present "
            "value."
        )
    else:
        lines.append(
            "For the forecast-based optimization, the configuration with "
            "the shortest payback differs from the configuration with the "
            "highest net present value."
        )

    lines.append("")

    if (
        historical_npv_matches_self_sufficiency
        and forecast_npv_matches_self_sufficiency
    ):
        lines.append(
            "In both optimization approaches, the financially preferred "
            "configuration also maximizes self-sufficiency."
        )
    elif (
        not historical_npv_matches_self_sufficiency
        and not forecast_npv_matches_self_sufficiency
    ):
        lines.append(
            "In both optimization approaches, the configuration with the "
            "highest net present value differs from the configuration with "
            "the highest self-sufficiency. This reflects a clear trade-off "
            "between financial performance and energy independence."
        )
    else:
        lines.append(
            "The relationship between financial performance and "
            "self-sufficiency changes between the historical and "
            "forecast-based optimizations."
        )

    lines.extend(
        [
            "",
            (
                "Forecasted consumption can therefore change not only the "
                "expected savings, but also the preferred solar and battery "
                "configuration."
            ),
            "",
        ]
    )

    return "\n".join(lines)


COST_BREAKDOWN_COLUMNS = {
    "base_variable_energy_cost_eur",
    "base_fixed_power_cost_eur",
    "base_surplus_compensation_eur",
    "base_net_cost_eur",
    "scenario_variable_energy_cost_eur",
    "scenario_fixed_power_cost_eur",
    "scenario_surplus_compensation_eur",
    "scenario_net_cost_eur",
}


def has_cost_breakdown(
    scenario_row: pd.Series,
) -> bool:
    return COST_BREAKDOWN_COLUMNS.issubset(scenario_row.index)


def format_cost_breakdown_lines(
    scenario_row: pd.Series,
) -> list[str]:
    if not has_cost_breakdown(scenario_row):
        return []

    return [
        "- Simulation-period electricity cost breakdown:",
        (
            "  - Baseline variable energy cost: "
            f"`{format_eur(scenario_row['base_variable_energy_cost_eur'])}`"
        ),
        (
            "  - Baseline fixed power cost: "
            f"`{format_eur(scenario_row['base_fixed_power_cost_eur'])}`"
        ),
        (
            "  - Baseline surplus compensation: "
            f"`{format_eur(scenario_row['base_surplus_compensation_eur'])}`"
        ),
        (
            "  - Baseline net electricity cost: "
            f"`{format_eur(scenario_row['base_net_cost_eur'])}`"
        ),
        (
            "  - Optimized variable energy cost: "
            f"`{format_eur(scenario_row['scenario_variable_energy_cost_eur'])}`"
        ),
        (
            "  - Optimized fixed power cost: "
            f"`{format_eur(scenario_row['scenario_fixed_power_cost_eur'])}`"
        ),
        (
            "  - Optimized surplus compensation: "
            f"`{format_eur(scenario_row['scenario_surplus_compensation_eur'])}`"
        ),
        (
            "  - Optimized net electricity cost: "
            f"`{format_eur(scenario_row['scenario_net_cost_eur'])}`"
        ),
    ]


SCENARIO_FINANCIAL_COLUMNS = {
    "battery_replacement_cost_eur",
    "net_present_value_eur",
    "discounted_payback_years",
    "internal_rate_of_return",
}


def has_extended_financial_metrics(scenario_row: pd.Series) -> bool:
    return SCENARIO_FINANCIAL_COLUMNS.issubset(scenario_row.index)


def format_extended_financial_lines(
    scenario_row: pd.Series,
) -> list[str]:
    if not has_extended_financial_metrics(scenario_row):
        return []

    return [
        (
            "- Battery replacement cost: "
            f"`{format_eur(scenario_row['battery_replacement_cost_eur'])}`"
        ),
        (f"- Net present value: `{format_eur(scenario_row['net_present_value_eur'])}`"),
        (
            "- Discounted payback: "
            f"`{format_optional_years(scenario_row['discounted_payback_years'])}`"
        ),
        (
            "- Internal rate of return: "
            f"`{format_optional_percent(scenario_row['internal_rate_of_return'])}`"
        ),
    ]


def format_scenario_section(
    title: str,
    scenario_row: pd.Series,
) -> str:
    lines = [
        f"## {title}",
        "",
        (f"- Solar peak power: `{scenario_row['solar_peak_power_kw']:.2f} kW`"),
        (f"- Battery capacity: `{scenario_row['battery_capacity_kwh']:.2f} kWh`"),
        (f"- Investment cost: `{format_eur(scenario_row['investment_cost_eur'])}`"),
        (
            "- Annual savings: "
            f"`{format_eur_per_year(scenario_row['annual_savings_eur'])}`"
        ),
        (f"- Simple payback: `{format_years(scenario_row['payback_years'])}`"),
    ]

    extended_financial_lines = format_extended_financial_lines(scenario_row)

    if extended_financial_lines:
        lines.extend(extended_financial_lines)

    lines.extend(
        [
            (
                "- Self-sufficiency: "
                f"`{format_percent(scenario_row['self_sufficiency'])}`"
            ),
            (
                "- Annual grid import: "
                f"`{format_kwh_per_year(scenario_row['annual_grid_import_kwh'])}`"
            ),
        ]
    )

    cost_breakdown_lines = format_cost_breakdown_lines(scenario_row)

    if cost_breakdown_lines:
        lines.extend(
            [
                "",
                *cost_breakdown_lines,
            ]
        )

    lines.append("")

    return "\n".join(lines)


FINANCIAL_SENSITIVITY_REQUIRED_COLUMNS = {
    "case_name",
    "discount_rate",
    "annual_operating_cost_eur",
    "annual_electricity_price_growth_rate",
    "battery_replacement_cost_eur",
    "net_present_value_eur",
    "discounted_payback_years",
    "internal_rate_of_return",
}


def validate_financial_sensitivity_dataframe(
    sensitivity_df: pd.DataFrame,
) -> None:
    missing_columns = FINANCIAL_SENSITIVITY_REQUIRED_COLUMNS - set(
        sensitivity_df.columns
    )

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"Financial sensitivity data is missing required columns: {missing_text}"
        )


def build_financial_sensitivity_table(
    sensitivity_df: pd.DataFrame,
) -> str:
    validate_financial_sensitivity_dataframe(sensitivity_df)

    lines = [
        "| Case | Discount rate | Electricity price growth | "
        "Annual operating cost | Battery replacement cost | "
        "NPV | Discounted payback | IRR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for _, row in sensitivity_df.iterrows():
        lines.append(
            "| "
            f"{row['case_name']} | "
            f"{format_percent(row['discount_rate'])} | "
            f"{format_percent(row['annual_electricity_price_growth_rate'])} | "
            f"{format_eur(row['annual_operating_cost_eur'])} | "
            f"{format_eur(row['battery_replacement_cost_eur'])} | "
            f"{format_eur(row['net_present_value_eur'])} | "
            f"{format_optional_years(row['discounted_payback_years'])} | "
            f"{format_optional_percent(row['internal_rate_of_return'])} |"
        )

    return "\n".join(lines)


def get_sensitivity_case(
    sensitivity_df: pd.DataFrame,
    case_name: str,
) -> pd.Series:
    filtered_df = sensitivity_df[sensitivity_df["case_name"] == case_name]

    if filtered_df.empty:
        raise ValueError(f"Financial sensitivity case not found: {case_name}")

    return filtered_df.iloc[0]


def build_financial_sensitivity_interpretation(
    sensitivity_df: pd.DataFrame,
) -> str:
    validate_financial_sensitivity_dataframe(sensitivity_df)

    pessimistic = get_sensitivity_case(
        sensitivity_df,
        "pessimistic",
    )
    base = get_sensitivity_case(
        sensitivity_df,
        "base",
    )
    optimistic = get_sensitivity_case(
        sensitivity_df,
        "optimistic",
    )

    pessimistic_npv = float(pessimistic["net_present_value_eur"])
    base_npv = float(base["net_present_value_eur"])
    optimistic_npv = float(optimistic["net_present_value_eur"])

    if pessimistic_npv > 0:
        return (
            "The selected configuration remains profitable even under "
            "pessimistic assumptions. Its positive NPV across all three "
            "cases indicates comparatively robust financial performance."
        )

    if base_npv > 0:
        return (
            "The selected configuration is profitable under the base and "
            "optimistic assumptions, but not under the pessimistic case. "
            "Its financial attractiveness is therefore positive but not "
            "fully robust to adverse assumptions."
        )

    if optimistic_npv > 0:
        return (
            "The selected configuration is not profitable under the "
            "pessimistic or base assumptions. It only achieves a positive "
            "NPV under the optimistic case, so its financial viability "
            "depends strongly on favourable long-term assumptions."
        )

    return (
        "The selected configuration has a negative NPV under all tested "
        "financial assumptions. It is therefore not financially attractive "
        "within the current sensitivity range."
    )


def build_financial_sensitivity_section(
    sensitivity_df: pd.DataFrame,
    npv_plot_path: str,
    payback_plot_path: str,
    irr_plot_path: str,
) -> str:
    table = build_financial_sensitivity_table(sensitivity_df)

    interpretation = build_financial_sensitivity_interpretation(sensitivity_df)

    lines = [
        "## Financial sensitivity analysis",
        "",
        (
            "The historical configuration selected by maximum net present "
            "value is evaluated under pessimistic, base and optimistic "
            "financial assumptions."
        ),
        "",
        table,
        "",
        "### Interpretation",
        "",
        interpretation,
        "",
        "### Sensitivity charts",
        "",
        f"![Financial sensitivity NPV]({npv_plot_path})",
        "",
        (f"![Financial sensitivity discounted payback]({payback_plot_path})"),
        "",
        f"![Financial sensitivity IRR]({irr_plot_path})",
        "",
    ]

    return "\n".join(lines)


def build_final_results_summary(
    comparison_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame | None = None,
    npv_plot_path: str = "",
    payback_plot_path: str = "",
    irr_plot_path: str = "",
) -> str:
    historical_payback = get_scenario(
        comparison_df,
        "historical",
        "best_payback",
    )
    historical_npv = get_scenario(
        comparison_df,
        "historical",
        "best_net_present_value",
    )
    historical_self_sufficiency = get_scenario(
        comparison_df,
        "historical",
        "best_self_sufficiency",
    )

    forecast_payback = get_scenario(
        comparison_df,
        "forecast_based",
        "best_payback",
    )
    forecast_npv = get_scenario(
        comparison_df,
        "forecast_based",
        "best_net_present_value",
    )
    forecast_self_sufficiency = get_scenario(
        comparison_df,
        "forecast_based",
        "best_self_sufficiency",
    )

    sensitivity_section = ""

    if sensitivity_df is not None:
        sensitivity_section = build_financial_sensitivity_section(
            sensitivity_df=sensitivity_df,
            npv_plot_path=npv_plot_path,
            payback_plot_path=payback_plot_path,
            irr_plot_path=irr_plot_path,
        )

    conclusion = build_optimization_conclusion(
        historical_payback=historical_payback,
        historical_npv=historical_npv,
        historical_self_sufficiency=historical_self_sufficiency,
        forecast_payback=forecast_payback,
        forecast_npv=forecast_npv,
        forecast_self_sufficiency=forecast_self_sufficiency,
    )

    comparison_section = build_scenario_comparison_section(comparison_df)

    lines = [
        "# Final Results Summary",
        "",
        (
            "This report summarizes the main results produced by the full "
            "project pipeline."
        ),
        "",
        ("It compares historical optimization with forecast-based optimization."),
        "",
        comparison_section,
        format_scenario_section(
            "Best historical payback scenario",
            historical_payback,
        ),
        format_scenario_section(
            "Best historical net present value scenario",
            historical_npv,
        ),
        format_scenario_section(
            "Best historical self-sufficiency scenario",
            historical_self_sufficiency,
        ),
        format_scenario_section(
            "Best forecast-based payback scenario",
            forecast_payback,
        ),
        format_scenario_section(
            "Best forecast-based net present value scenario",
            forecast_npv,
        ),
        format_scenario_section(
            "Best forecast-based self-sufficiency scenario",
            forecast_self_sufficiency,
        ),
        sensitivity_section,
        conclusion,
    ]

    return "\n".join(lines)


def main() -> None:
    paths = config.OUTPUT_PATHS
    paths.create_directories()

    input_path = paths.historical_vs_forecast_comparison
    output_path = paths.final_results_summary
    sensitivity_input_path = paths.financial_sensitivity_results

    comparison_df = pd.read_csv(input_path)
    sensitivity_df = pd.read_csv(sensitivity_input_path)

    relative_images_directory = Path("../../images") / paths.scenario_name

    summary = build_final_results_summary(
        comparison_df=comparison_df,
        sensitivity_df=sensitivity_df,
        npv_plot_path=str(relative_images_directory / "financial_sensitivity_npv.png"),
        payback_plot_path=str(
            relative_images_directory / "financial_sensitivity_payback.png"
        ),
        irr_plot_path=str(relative_images_directory / "financial_sensitivity_irr.png"),
    )
    Path(output_path).write_text(summary, encoding="utf-8")

    print("\nFinal results summary generated")
    print(f"Sensitivity input file: {sensitivity_input_path}")
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
