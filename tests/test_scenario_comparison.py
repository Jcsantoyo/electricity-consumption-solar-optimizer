from pathlib import Path

import pandas as pd
import pytest

from scenario_comparison import (
    add_reference_differences,
    build_scenario_comparison_markdown,
    combine_scenario_results,
    discover_available_scenarios,
    discover_criteria,
    discover_numeric_metric_columns,
    load_best_scenarios,
    validate_best_scenarios_dataframe,
)


def build_best_scenarios_dataframe(
    savings_multiplier: float = 1.0,
    include_extra_criterion: bool = False,
) -> pd.DataFrame:
    dataframe = pd.DataFrame(
        {
            "criterion": [
                "best_payback",
                "best_self_sufficiency",
            ],
            "solar_peak_power_kw": [
                3.0,
                3.0,
            ],
            "battery_capacity_kwh": [
                0.0,
                5.0,
            ],
            "investment_cost_eur": [
                3500.0,
                6000.0,
            ],
            "annual_savings_eur": [
                250.0 * savings_multiplier,
                220.0 * savings_multiplier,
            ],
            "payback_years": [
                14.0 / savings_multiplier,
                27.0 / savings_multiplier,
            ],
            "self_sufficiency": [
                0.25,
                0.34,
            ],
            "annual_grid_import_kwh": [
                11000.0,
                9800.0,
            ],
        }
    )

    if include_extra_criterion:
        extra_row = pd.DataFrame(
            {
                "criterion": [
                    "best_annual_savings",
                ],
                "solar_peak_power_kw": [
                    4.0,
                ],
                "battery_capacity_kwh": [
                    2.0,
                ],
                "investment_cost_eur": [
                    5000.0,
                ],
                "annual_savings_eur": [
                    300.0
                    * savings_multiplier,
                ],
                "payback_years": [
                    16.67
                    / savings_multiplier,
                ],
                "self_sufficiency": [
                    0.30,
                ],
                "annual_grid_import_kwh": [
                    10400.0,
                ],
            }
        )

        dataframe = pd.concat(
            [
                dataframe,
                extra_row,
            ],
            ignore_index=True,
        )

    return dataframe


def write_scenario_results(
    reports_root: Path,
    scenario_name: str,
    dataframe: pd.DataFrame,
) -> None:
    scenario_directory = (
        reports_root / scenario_name
    )

    scenario_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        scenario_directory
        / "best_scenarios.csv",
        index=False,
    )


def test_validate_accepts_dynamic_criteria() -> None:
    dataframe = (
        build_best_scenarios_dataframe(
            include_extra_criterion=True
        )
    )

    validate_best_scenarios_dataframe(
        dataframe=dataframe,
        scenario_name="example",
    )


def test_validate_rejects_missing_required_column() -> None:
    dataframe = (
        build_best_scenarios_dataframe()
        .drop(
            columns=[
                "criterion",
            ]
        )
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        validate_best_scenarios_dataframe(
            dataframe=dataframe,
            scenario_name="example",
        )


def test_validate_rejects_duplicated_criteria() -> None:
    dataframe = (
        build_best_scenarios_dataframe()
    )

    dataframe = pd.concat(
        [
            dataframe,
            dataframe.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="duplicated criteria",
    ):
        validate_best_scenarios_dataframe(
            dataframe=dataframe,
            scenario_name="example",
        )


def test_discover_available_scenarios(
    tmp_path,
) -> None:
    reports_root = tmp_path / "reports"

    write_scenario_results(
        reports_root=reports_root,
        scenario_name="scenario_b",
        dataframe=(
            build_best_scenarios_dataframe()
        ),
    )

    write_scenario_results(
        reports_root=reports_root,
        scenario_name="scenario_a",
        dataframe=(
            build_best_scenarios_dataframe()
        ),
    )

    unrelated_directory = (
        reports_root / "other_output"
    )

    unrelated_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    discovered = (
        discover_available_scenarios(
            reports_root=str(reports_root)
        )
    )

    assert discovered == [
        "scenario_a",
        "scenario_b",
    ]


def test_load_best_scenarios_adds_name(
    tmp_path,
) -> None:
    reports_root = tmp_path / "reports"

    write_scenario_results(
        reports_root=reports_root,
        scenario_name="scenario_a",
        dataframe=(
            build_best_scenarios_dataframe()
        ),
    )

    loaded_df = load_best_scenarios(
        scenario_name="scenario_a",
        reports_root=str(reports_root),
    )

    assert (
        loaded_df["scenario_name"]
        .eq("scenario_a")
        .all()
    )


def test_combine_scenarios_supports_extra_criteria(
    tmp_path,
) -> None:
    reports_root = tmp_path / "reports"

    write_scenario_results(
        reports_root=reports_root,
        scenario_name="scenario_a",
        dataframe=(
            build_best_scenarios_dataframe(
                include_extra_criterion=True
            )
        ),
    )

    write_scenario_results(
        reports_root=reports_root,
        scenario_name="scenario_b",
        dataframe=(
            build_best_scenarios_dataframe(
                savings_multiplier=2.0,
                include_extra_criterion=True,
            )
        ),
    )

    comparison_df = combine_scenario_results(
        scenario_names=[
            "scenario_a",
            "scenario_b",
        ],
        reports_root=str(reports_root),
    )

    assert len(comparison_df) == 6

    assert set(
        discover_criteria(comparison_df)
    ) == {
        "best_payback",
        "best_self_sufficiency",
        "best_annual_savings",
    }


def test_discover_numeric_metrics_includes_new_metric() -> None:
    dataframe = (
        build_best_scenarios_dataframe()
        .assign(
            net_present_value_eur=[
                1000.0,
                1200.0,
            ]
        )
        .assign(
            scenario_name="example"
        )
    )

    metrics = (
        discover_numeric_metric_columns(
            dataframe
        )
    )

    assert "annual_savings_eur" in metrics
    assert "payback_years" in metrics
    assert "net_present_value_eur" in metrics


def test_reference_differences_are_dynamic() -> None:
    comparison_df = pd.concat(
        [
            (
                build_best_scenarios_dataframe()
                .assign(
                    scenario_name="reference",
                    net_present_value_eur=[
                        1000.0,
                        1200.0,
                    ],
                )
            ),
            (
                build_best_scenarios_dataframe(
                    savings_multiplier=2.0
                )
                .assign(
                    scenario_name="alternative",
                    net_present_value_eur=[
                        1700.0,
                        2000.0,
                    ],
                )
            ),
        ],
        ignore_index=True,
    )

    result_df = add_reference_differences(
        comparison_df=comparison_df,
        reference_scenario_name="reference",
    )

    alternative_payback = result_df[
        (
            result_df["scenario_name"]
            == "alternative"
        )
        & (
            result_df["criterion"]
            == "best_payback"
        )
    ].iloc[0]

    assert (
        alternative_payback[
            "annual_savings_eur_difference_vs_reference"
        ]
        == pytest.approx(250.0)
    )

    assert (
        alternative_payback[
            "net_present_value_eur_difference_vs_reference"
        ]
        == pytest.approx(700.0)
    )


def test_markdown_includes_dynamic_criterion() -> None:
    comparison_df = pd.concat(
        [
            (
                build_best_scenarios_dataframe(
                    include_extra_criterion=True
                )
                .assign(
                    scenario_name="reference"
                )
            ),
            (
                build_best_scenarios_dataframe(
                    savings_multiplier=2.0,
                    include_extra_criterion=True,
                )
                .assign(
                    scenario_name="alternative"
                )
            ),
        ],
        ignore_index=True,
    )

    comparison_df = add_reference_differences(
        comparison_df=comparison_df,
        reference_scenario_name="reference",
    )

    markdown = (
        build_scenario_comparison_markdown(
            comparison_df=comparison_df,
            reference_scenario_name=(
                "reference"
            ),
        )
    )

    assert "# Project scenario comparison" in markdown
    assert "Best Annual Savings" in markdown
    assert "alternative" in markdown