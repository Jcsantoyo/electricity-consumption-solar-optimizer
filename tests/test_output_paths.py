from pathlib import Path

import pytest

from output_paths import build_scenario_output_paths


def test_build_scenario_output_paths_uses_scenario_directories() -> None:
    paths = build_scenario_output_paths("example_scenario")

    assert paths.reports_directory == "reports/example_scenario"
    assert paths.images_directory == "images/example_scenario"
    assert paths.grid_search_results == str(
        Path("reports/example_scenario/grid_search_results.csv")
    )
    assert paths.payback_plot == str(
        Path("images/example_scenario/main_payback_grid_search.png")
    )


def test_different_scenarios_have_different_output_paths() -> None:
    first_paths = build_scenario_output_paths("first_scenario")
    second_paths = build_scenario_output_paths("second_scenario")

    assert first_paths.grid_search_results != second_paths.grid_search_results
    assert first_paths.payback_plot != second_paths.payback_plot


def test_output_paths_reject_empty_scenario_name() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        build_scenario_output_paths("")


def test_all_output_paths_contains_expected_files() -> None:
    paths = build_scenario_output_paths("example_scenario")
    all_paths = paths.all_output_paths()

    assert paths.grid_search_results in all_paths
    assert paths.forecast_results in all_paths
    assert paths.historical_vs_forecast_comparison in all_paths
    assert paths.run_manifest in all_paths
