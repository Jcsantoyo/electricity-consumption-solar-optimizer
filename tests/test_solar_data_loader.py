import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from solar_data_loader import (
    load_pvgis_solar_data,
    get_pvgis_generation_for_timestamps
)


def test_load_pvgis_solar_data_converts_time_and_power(tmp_path) -> None:
    csv_path = tmp_path / "pvgis_test.csv"

    csv_path.write_text(
        "time,P,G(i),H_sun,T2m,WS10m,Int\n"
        "20200101:0010,0.0,0.0,0.0,6.0,1.0,0.0\n"
        "20200101:1210,704.33,900.0,28.0,14.0,1.0,0.0\n",
        encoding="utf-8"
    )

    df = load_pvgis_solar_data(str(csv_path))

    assert "datetime" in df.columns
    assert "solar_generation_1kw_kwh" in df.columns

    assert df.loc[0, "datetime"] == pd.Timestamp("2020-01-01 00:10:00")
    assert df.loc[1, "datetime"] == pd.Timestamp("2020-01-01 12:10:00")

    assert df.loc[0, "solar_generation_1kw_kwh"] == 0.0
    assert df.loc[1, "solar_generation_1kw_kwh"] == 0.70433


def test_load_pvgis_solar_data_missing_time_column(tmp_path) -> None:
    csv_path = tmp_path / "pvgis_missing_time.csv"

    csv_path.write_text(
        "P,G(i),H_sun,T2m,WS10m,Int\n"
        "704.33,900.0,28.0,14.0,1.0,0.0\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Missing required column: time"):
        load_pvgis_solar_data(str(csv_path))


def test_load_pvgis_solar_data_missing_power_column(tmp_path) -> None:
    csv_path = tmp_path / "pvgis_missing_power.csv"

    csv_path.write_text(
        "time,G(i),H_sun,T2m,WS10m,Int\n"
        "20200101:1210,900.0,28.0,14.0,1.0,0.0\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Missing required column: P"):
        load_pvgis_solar_data(str(csv_path))


def test_get_pvgis_generation_for_timestamps_scales_peak_power() -> None:
    pvgis_df = pd.DataFrame({
        "datetime": [
            pd.Timestamp("2020-01-01 10:10:00"),
            pd.Timestamp("2020-01-01 11:10:00")
        ],
        "solar_generation_1kw_kwh": [0.5, 0.8]
    })

    timestamps = pd.Series([
        pd.Timestamp("2025-01-01 10:00:00"),
        pd.Timestamp("2025-01-01 11:00:00")
    ])

    solar_generation = get_pvgis_generation_for_timestamps(
        pvgis_df,
        timestamps,
        peak_power_kw=2.0
    )

    assert solar_generation == [1.0, 1.6]


def test_get_pvgis_generation_for_timestamps_matches_by_month_day_hour() -> None:
    pvgis_df = pd.DataFrame({
        "datetime": [
            pd.Timestamp("2020-01-01 12:10:00"),
            pd.Timestamp("2020-01-02 12:10:00")
        ],
        "solar_generation_1kw_kwh": [0.7, 0.8]
    })

    timestamps = pd.Series([
        pd.Timestamp("2025-01-01 12:00:00"),
        pd.Timestamp("2025-01-02 12:00:00")
    ])

    solar_generation = get_pvgis_generation_for_timestamps(
        pvgis_df,
        timestamps,
        peak_power_kw=1.5
    )

    assert round(solar_generation[0], 2) == 1.05
    assert round(solar_generation[1], 2) == 1.20


def test_get_pvgis_generation_for_missing_timestamp_returns_zero() -> None:
    pvgis_df = pd.DataFrame({
        "datetime": [
            pd.Timestamp("2020-01-01 12:10:00")
        ],
        "solar_generation_1kw_kwh": [0.7]
    })

    timestamps = pd.Series([
        pd.Timestamp("2025-01-01 12:00:00"),
        pd.Timestamp("2025-01-01 13:00:00")
    ])

    solar_generation = get_pvgis_generation_for_timestamps(
        pvgis_df,
        timestamps,
        peak_power_kw=1.0
    )

    assert solar_generation == [0.7, 0.0]