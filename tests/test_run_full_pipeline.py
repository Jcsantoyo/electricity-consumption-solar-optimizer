from pathlib import Path


def test_full_pipeline_contains_expected_steps():
    script_path = Path("scripts/run_full_pipeline.py")
    script_text = script_path.read_text(encoding="utf-8")

    expected_steps = [
        "scripts/generate_config_summary.py",
        "src/main.py",
        "scripts/run_forecasting.py",
        "scripts/run_forecast_optimization.py",
        "scripts/compare_optimization_results.py",
    ]

    for step in expected_steps:
        assert step in script_text


def test_full_pipeline_steps_are_in_expected_order():
    script_path = Path("scripts/run_full_pipeline.py")
    script_text = script_path.read_text(encoding="utf-8")

    expected_steps = [
        "scripts/generate_config_summary.py",
        "src/main.py",
        "scripts/run_forecasting.py",
        "scripts/run_forecast_optimization.py",
        "scripts/compare_optimization_results.py",
        "scripts/generate_final_results_summary.py"
    ]

    positions = [
        script_text.index(step)
        for step in expected_steps
    ]

    assert positions == sorted(positions)