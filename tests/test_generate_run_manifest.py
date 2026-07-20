from pathlib import Path

import config
from scripts.generate_run_manifest import collect_generated_output_paths


def test_collect_generated_output_paths_includes_existing_files(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    report_path = Path(config.OUTPUT_PATHS.historical_vs_forecast_comparison)
    plot_path = Path(config.OUTPUT_PATHS.historical_vs_forecast_payback_plot)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    plot_path.parent.mkdir(parents=True, exist_ok=True)

    report_path.write_text("example", encoding="utf-8")
    plot_path.write_bytes(b"example")

    output_paths = collect_generated_output_paths()

    assert str(report_path) in output_paths
    assert str(plot_path) in output_paths
    assert config.RUN_MANIFEST_PATH not in output_paths
