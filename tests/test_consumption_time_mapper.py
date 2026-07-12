import pandas as pd
import pytest

from consumption_time_mapper import (
    build_recent_consumption_scenario,
    remap_consumption_timestamps,
    select_consumption_period,
)


def build_consumption_dataframe(
    number_of_hours: int,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2006-12-16 17:00:00",
                periods=number_of_hours,
                freq="h",
            ),
            "consumption_kwh": [
                float(index + 1)
                for index in range(number_of_hours)
            ],
        }
    )


def test_select_consumption_period_returns_requested_number_of_days() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=1000,
    )

    selected_df = select_consumption_period(
        consumption_df=consumption_df,
        number_of_days=30,
    )

    assert len(selected_df) == 720


def test_select_consumption_period_keeps_consumption_values() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=48,
    )

    selected_df = select_consumption_period(
        consumption_df=consumption_df,
        number_of_days=1,
    )

    assert list(selected_df["consumption_kwh"]) == list(
        consumption_df.iloc[:24]["consumption_kwh"]
    )


def test_select_consumption_period_rejects_invalid_number_of_days() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=24,
    )

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        select_consumption_period(
            consumption_df=consumption_df,
            number_of_days=0,
        )


def test_select_consumption_period_rejects_insufficient_data() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=24,
    )

    with pytest.raises(
        ValueError,
        match="does not contain enough rows",
    ):
        select_consumption_period(
            consumption_df=consumption_df,
            number_of_days=2,
        )


def test_remap_consumption_timestamps_builds_hourly_sequence() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=3,
    )

    remapped_df = remap_consumption_timestamps(
        consumption_df=consumption_df,
        target_start_datetime="2026-06-01 17:00:00",
    )

    assert list(remapped_df["datetime"]) == list(
        pd.date_range(
            start="2026-06-01 17:00:00",
            periods=3,
            freq="h",
        )
    )


def test_remap_consumption_timestamps_keeps_original_dates() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=3,
    )

    remapped_df = remap_consumption_timestamps(
        consumption_df=consumption_df,
        target_start_datetime="2026-06-01 17:00:00",
    )

    assert list(remapped_df["original_datetime"]) == list(
        consumption_df["datetime"]
    )


def test_remap_consumption_timestamps_keeps_consumption_values() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=3,
    )

    remapped_df = remap_consumption_timestamps(
        consumption_df=consumption_df,
        target_start_datetime="2026-06-01 17:00:00",
    )

    assert list(remapped_df["consumption_kwh"]) == list(
        consumption_df["consumption_kwh"]
    )


def test_build_recent_consumption_scenario_combines_selection_and_remap() -> None:
    consumption_df = build_consumption_dataframe(
        number_of_hours=1000,
    )

    scenario_df = build_recent_consumption_scenario(
        consumption_df=consumption_df,
        number_of_days=30,
        target_start_datetime="2026-06-01 17:00:00",
    )

    assert len(scenario_df) == 720
    assert scenario_df.iloc[0]["datetime"] == pd.Timestamp(
        "2026-06-01 17:00:00"
    )
    assert scenario_df.iloc[-1]["datetime"] == pd.Timestamp(
        "2026-07-01 16:00:00"
    )