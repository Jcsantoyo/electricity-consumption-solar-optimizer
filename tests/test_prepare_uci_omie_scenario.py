import pandas as pd

from scripts.prepare_uci_omie_scenario import (
    prepare_uci_omie_scenario,
)


def test_prepare_uci_omie_scenario_writes_output_csv(
    tmp_path,
) -> None:
    input_file = tmp_path / "consumption.csv"
    output_file = tmp_path / "scenario.csv"

    consumption_df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2006-12-16 17:00:00",
                periods=48,
                freq="h",
            ),
            "consumption_kwh": [float(index + 1) for index in range(48)],
        }
    )

    consumption_df.to_csv(
        input_file,
        index=False,
    )

    scenario_df = prepare_uci_omie_scenario(
        consumption_path=str(input_file),
        output_path=str(output_file),
        number_of_days=1,
        target_start_datetime="2026-06-01 00:00:00",
    )

    assert output_file.exists()
    assert len(scenario_df) == 24


def test_prepare_uci_omie_scenario_remaps_dates(
    tmp_path,
) -> None:
    input_file = tmp_path / "consumption.csv"
    output_file = tmp_path / "scenario.csv"

    consumption_df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2006-12-16 17:00:00",
                periods=24,
                freq="h",
            ),
            "consumption_kwh": [1.0 for _ in range(24)],
        }
    )

    consumption_df.to_csv(
        input_file,
        index=False,
    )

    scenario_df = prepare_uci_omie_scenario(
        consumption_path=str(input_file),
        output_path=str(output_file),
        number_of_days=1,
        target_start_datetime="2026-06-01 00:00:00",
    )

    assert scenario_df.iloc[0]["datetime"] == pd.Timestamp("2026-06-01 00:00:00")

    assert scenario_df.iloc[-1]["datetime"] == pd.Timestamp("2026-06-01 23:00:00")


def test_prepare_uci_omie_scenario_keeps_original_dates(
    tmp_path,
) -> None:
    input_file = tmp_path / "consumption.csv"
    output_file = tmp_path / "scenario.csv"

    original_dates = pd.date_range(
        start="2006-12-16 17:00:00",
        periods=24,
        freq="h",
    )

    consumption_df = pd.DataFrame(
        {
            "datetime": original_dates,
            "consumption_kwh": [1.0 for _ in range(24)],
        }
    )

    consumption_df.to_csv(
        input_file,
        index=False,
    )

    scenario_df = prepare_uci_omie_scenario(
        consumption_path=str(input_file),
        output_path=str(output_file),
        number_of_days=1,
        target_start_datetime="2026-06-01 00:00:00",
    )

    assert list(pd.to_datetime(scenario_df["original_datetime"])) == list(
        original_dates
    )
