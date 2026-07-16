from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "criterion",
    "solar_peak_power_kw",
    "battery_capacity_kwh"
}

NON_METRIC_COLUMNS = {
    "scenario_name",
    "criterion"
}

def validate_best_scenarios_dataframe(
    dataframe: pd.DataFrame,
    scenario_name: str
) -> None:
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        formatted_columns = ", ".join(sorted(missing_columns))

        raise ValueError(f"Scenario '{scenario_name}' is missing required columns: {formatted_columns}")
    
    if dataframe.empty:
        raise ValueError(f"Scenario '{scenario_name}' contains no best-scenario rows")
    
    if dataframe["criterion"].isna().any():
        raise ValueError(f"Scenario '{scenario_name}' contains no best-scenario rows")

    duplicated_criteria = dataframe["criterion"].duplicated(keep=False)

    if duplicated_criteria.any():
        duplicated_values = sorted(
            dataframe.loc[duplicated_criteria, "criterion"]
            .astype(str)
            .unique()
            .tolist()
        )
        raise ValueError(f"Scenario '{scenario_name}' contains duplicated criteria: " + ", ".join(duplicated_values))
    

def discover_available_scenarios(reports_root: str = "reports") -> list[str]:
    root_path = Path(reports_root)

    if not root_path.is_dir():
        return []
    
    scenario_names = []

    for directory in root_path.iterdir():
        if not directory.is_dir():
            continue
        best_scenarios_path = directory / "best_scenarios.csv"

        if best_scenarios_path.is_file():
            scenario_names.append(directory.name)

    return sorted(scenario_names)

def load_best_scenarios(scenario_name: str, reports_root: str = "reports") -> pd.DataFrame:
    cleaned_scenario_name = scenario_name.strip()

    if not cleaned_scenario_name:
        raise ValueError("Scenario name cannot be empty")
    
    input_path = Path(reports_root) / cleaned_scenario_name / "best_scenarios.csv"

    if not input_path.is_file():
        raise FileNotFoundError(
            "Best-scenarios file not found for "
            f"scenario '{cleaned_scenario_name}': "
            f"{input_path}"
        )
    
    dataframe = pd.read_csv(input_path)

    validate_best_scenarios_dataframe(dataframe, cleaned_scenario_name)

    dataframe = dataframe.copy()

    dataframe.insert(0, "scenario_name", cleaned_scenario_name)

    return dataframe

def clean_scenario_names(scenario_names: list[str]) -> list[str]:
    cleaned_names = [
        scenario_name.strip()
        for scenario_name in scenario_names
        if scenario_name.strip()
    ]

    if len(cleaned_names) < 2:
        raise ValueError("At least two different scenarios are required for comparison")
    
    if len(set(cleaned_names)) != len(cleaned_names):
        raise ValueError("Scenario names must be unique")
    
    return cleaned_names

def combine_scenario_results(
    scenario_names: list[str],
    reports_root: str = "reports"
) -> pd.DataFrame:
    cleaned_names = clean_scenario_names(scenario_names)

    dataframes = []

    for scenario_name in cleaned_names:
        dataframes.append(load_best_scenarios(scenario_name, reports_root))

    comparison_df = pd.concat(dataframes, ignore_index=True, sort=False)

    return comparison_df

def discover_numeric_metric_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    metric_columns = []

    for column in dataframe.columns:
        if column in NON_METRIC_COLUMNS:
            continue

        if column.endswith(
            "_difference_vs_reference"
        ):
            continue

        if pd.api.types.is_numeric_dtype(
            dataframe[column]
        ):
            metric_columns.append(column)

    return metric_columns

def discover_criteria(dataframe: pd.DataFrame) -> list[str]:
    return (dataframe["criterion"].dropna().astype(str).drop_duplicates().tolist())

def add_reference_differences(
    comparison_df: pd.DataFrame,
    reference_scenario_name: str,
    metric_columns: list[str] | None = None,
) -> pd.DataFrame:
    available_scenarios = set(
        comparison_df["scenario_name"]
        .astype(str)
        .tolist()
    )

    if reference_scenario_name not in available_scenarios:
        raise ValueError(
            "Reference scenario is not present "
            "in comparison data: "
            f"{reference_scenario_name}"
        )

    if metric_columns is None:
        metric_columns = (
            discover_numeric_metric_columns(
                comparison_df
            )
        )

    reference_mask = (
        comparison_df["scenario_name"]
        == reference_scenario_name
    )

    reference_columns = [
        "criterion",
        *metric_columns,
    ]

    reference_df = comparison_df.loc[
        reference_mask,
        reference_columns,
    ].copy()

    reference_column_names = {
        metric: f"reference_{metric}"
        for metric in metric_columns
    }

    reference_df = reference_df.rename(
        columns=reference_column_names
    )

    result_df = comparison_df.merge(
        reference_df,
        on="criterion",
        how="left",
        validate="many_to_one",
    )

    for metric in metric_columns:
        reference_column = (
            f"reference_{metric}"
        )

        difference_column = (
            f"{metric}"
            "_difference_vs_reference"
        )

        result_df[difference_column] = (
            result_df[metric]
            - result_df[reference_column]
        )

    result_df[
        "reference_scenario_name"
    ] = reference_scenario_name

    columns_to_remove = [
        f"reference_{metric}"
        for metric in metric_columns
    ]

    return result_df.drop(
        columns=columns_to_remove
    )

def format_column_name(column_name: str) -> str:
    return column_name.replace("_", " ").strip().title()

def format_criterion_name(criterion: str) -> str:
    return format_column_name(criterion)

def format_markdown_value(value: object, column_name: str) -> str:
    if pd.isna(value):
        return "N/A"
    
    if column_name == "self_sufficiency":
        return f"{float(value) * 100.0:.2f}%"
    
    if column_name == "self_sufficiency_difference_vs_reference":
        return f"{float(value) * 100.0:.2f} pp"
    
    if isinstance(value, float):
        return f"{value:.2f}"
    
    return str(value)


def build_markdown_table(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> list[str]:
    headers = [
        format_column_name(column)
        for column in columns
    ]

    lines = [
        "| " + " | ".join(headers) + " |",
        "|"
        + "|".join(
            "---" if index == 0 else "---:"
            for index in range(len(columns))
        )
        + "|",
    ]

    for _, row in dataframe.iterrows():
        values = [
            format_markdown_value(
                value=row[column],
                column_name=column,
            )
            for column in columns
        ]

        lines.append(
            "| " + " | ".join(values) + " |"
        )

    return lines


def build_scenario_comparison_markdown(
    comparison_df: pd.DataFrame,
    reference_scenario_name: str,
) -> str:
    metric_columns = (
        discover_numeric_metric_columns(
            comparison_df
        )
    )

    difference_columns = [
        (
            f"{metric}"
            "_difference_vs_reference"
        )
        for metric in metric_columns
        if (
            f"{metric}"
            "_difference_vs_reference"
        )
        in comparison_df.columns
    ]

    criteria = discover_criteria(
        comparison_df
    )

    lines = [
        "# Project scenario comparison",
        "",
        (
            f"Reference scenario: "
            f"`{reference_scenario_name}`"
        ),
        "",
        "## Interpretation",
        "",
        (
            "Each scenario is generated by the same "
            "optimization pipeline. Differences can come "
            "from consumption data, solar production, "
            "electricity prices, forecasting settings or "
            "optimization parameters."
        ),
        "",
        (
            "Energy metrics can remain identical when two "
            "scenarios use the same physical consumption and "
            "generation data but different electricity-price "
            "models."
        ),
        "",
    ]

    for criterion in criteria:
        criterion_df = comparison_df[
            comparison_df["criterion"]
            == criterion
        ].copy()

        lines.extend(
            [
                (
                    "## "
                    + format_criterion_name(
                        criterion
                    )
                ),
                "",
            ]
        )

        result_columns = [
            "scenario_name",
            *metric_columns,
        ]

        lines.extend(
            build_markdown_table(
                dataframe=criterion_df,
                columns=result_columns,
            )
        )

        lines.extend(
            [
                "",
                "### Differences from reference",
                "",
            ]
        )

        difference_table_columns = [
            "scenario_name",
            *difference_columns,
        ]

        lines.extend(
            build_markdown_table(
                dataframe=criterion_df,
                columns=difference_table_columns,
            )
        )

        lines.append("")

    return "\n".join(lines)


def save_scenario_comparison_csv(comparison_df: pd.DataFrame, output_path: str) -> None:
    resolved_output_path = Path(output_path)

    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)

    comparison_df.to_csv(resolved_output_path, index=False)

def save_scenario_comparison_markdown(
    comparison_df: pd.DataFrame,
    reference_scenario_name: str,
    output_path:str
) -> None:
    markdown = build_scenario_comparison_markdown(comparison_df, reference_scenario_name)

    resolved_output_path = Path(output_path)

    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)

    resolved_output_path.write_text(markdown, encoding="utf-8")