import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from scenario_comparison import (  # noqa: E402
    add_reference_differences,
    combine_scenario_results,
    discover_available_scenarios,
    discover_criteria,
    save_scenario_comparison_csv,
    save_scenario_comparison_markdown,
)
from visualization import (  # noqa: E402
    generate_scenario_metric_plots,
)


REPORTS_ROOT = "reports"

COMPARISON_REPORTS_DIRECTORY = "reports/scenario_comparison"

COMPARISON_IMAGES_DIRECTORY = "images/scenario_comparison"

COMPARISON_CSV_PATH = f"{COMPARISON_REPORTS_DIRECTORY}/scenario_comparison.csv"

COMPARISON_MARKDOWN_PATH = f"{COMPARISON_REPORTS_DIRECTORY}/scenario_comparison.md"

PLOTTABLE_METRICS = [
    "annual_savings_eur",
    "payback_years",
    "self_sufficiency",
    "annual_grid_import_kwh",
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Compare optimization results from multiple project scenarios.")
    )

    parser.add_argument(
        "scenarios",
        nargs="*",
        help=(
            "Scenario names to compare. When omitted, "
            "all scenarios containing a best_scenarios.csv "
            "file are discovered automatically."
        ),
    )

    parser.add_argument(
        "--reference",
        default=None,
        help=(
            "Scenario used as the reference for differences. "
            "Defaults to the first selected scenario."
        ),
    )

    parser.add_argument(
        "--reports-root",
        default=REPORTS_ROOT,
        help=("Root directory containing scenario reports."),
    )

    return parser.parse_args()


def resolve_scenario_names(
    requested_scenarios: list[str],
    reports_root: str,
) -> list[str]:
    if requested_scenarios:
        return requested_scenarios

    discovered_scenarios = discover_available_scenarios(reports_root=reports_root)

    if len(discovered_scenarios) < 2:
        raise ValueError(
            "At least two completed scenarios are "
            "required. Run the optimization pipeline "
            "for more scenarios first."
        )

    return discovered_scenarios


def create_output_directories() -> None:
    Path(COMPARISON_REPORTS_DIRECTORY).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(COMPARISON_IMAGES_DIRECTORY).mkdir(
        parents=True,
        exist_ok=True,
    )


def print_comparison_summary(
    comparison_df,
    scenario_names: list[str],
    reference_scenario_name: str,
) -> None:
    criteria = discover_criteria(comparison_df)

    print("\nProject scenario comparison")
    print("===========================")

    print("Scenarios: " + ", ".join(scenario_names))

    print(f"Reference scenario: {reference_scenario_name}")

    print("Criteria: " + ", ".join(criteria))

    preferred_columns = [
        "scenario_name",
        "criterion",
        "solar_peak_power_kw",
        "battery_capacity_kwh",
        "annual_savings_eur",
        "payback_years",
        "self_sufficiency",
    ]

    available_columns = [
        column for column in preferred_columns if column in comparison_df.columns
    ]

    print("\nComparison data:")

    print(comparison_df[available_columns].to_string(index=False))


def main() -> None:
    arguments = parse_arguments()

    scenario_names = resolve_scenario_names(
        requested_scenarios=(arguments.scenarios),
        reports_root=(arguments.reports_root),
    )

    reference_scenario_name = arguments.reference or scenario_names[0]

    create_output_directories()

    comparison_df = combine_scenario_results(
        scenario_names=scenario_names,
        reports_root=arguments.reports_root,
    )

    comparison_df = add_reference_differences(
        comparison_df=comparison_df,
        reference_scenario_name=(reference_scenario_name),
    )

    save_scenario_comparison_csv(
        comparison_df=comparison_df,
        output_path=COMPARISON_CSV_PATH,
    )

    save_scenario_comparison_markdown(
        comparison_df=comparison_df,
        reference_scenario_name=(reference_scenario_name),
        output_path=COMPARISON_MARKDOWN_PATH,
    )

    generated_plot_paths = generate_scenario_metric_plots(
        comparison_df=comparison_df,
        metric_columns=PLOTTABLE_METRICS,
        output_directory=(COMPARISON_IMAGES_DIRECTORY),
    )

    print_comparison_summary(
        comparison_df=comparison_df,
        scenario_names=scenario_names,
        reference_scenario_name=(reference_scenario_name),
    )

    print(f"\nCSV saved to: {COMPARISON_CSV_PATH}")

    print(f"Markdown report saved to: {COMPARISON_MARKDOWN_PATH}")

    print("\nGenerated plots:")

    for path in generated_plot_paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
