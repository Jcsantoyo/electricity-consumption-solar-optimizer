from pathlib import Path


def test_makefile_exists():
    makefile_path = Path("Makefile")

    assert makefile_path.exists()


def test_makefile_contains_expected_commands():
    makefile_text = Path("Makefile").read_text(
        encoding="utf-8"
    )

    expected_commands = [
        "install:",
        "test:",
        "pipeline:",
        "optimize:",
        "forecast:",
        "forecast-optimize:",
        "compare:",
        "config-summary:",
        "final-summary:",
        "clean-reports:",
    ]

    for command in expected_commands:
        assert command in makefile_text


def test_makefile_pipeline_runs_full_pipeline_script():
    makefile_text = Path("Makefile").read_text(
        encoding="utf-8"
    )

    assert "python scripts/run_full_pipeline.py" in makefile_text


def test_makefile_test_runs_pytest():
    makefile_text = Path("Makefile").read_text(
        encoding="utf-8"
    )

    assert "python -m pytest" in makefile_text