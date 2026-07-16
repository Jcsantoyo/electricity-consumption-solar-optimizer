import json
from dataclasses import replace

import pandas as pd
import pytest

from run_manifest import (
    build_dataset_metadata,
    build_run_manifest,
    write_run_manifest,
)
from scenario_registry import get_project_scenario


def build_consumption_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2026-06-01 00:00:00",
                periods=48,
                freq="h",
            ),
            "consumption_kwh": [1.0] * 48,
        }
    )


def build_price_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2026-06-01 00:00:00",
                periods=48,
                freq="h",
            ),
            "price_eur_per_kwh": [0.10] * 48,
        }
    )


def test_build_dataset_metadata() -> None:
    metadata = build_dataset_metadata(
        df=build_consumption_df(),
        file_path="consumption.csv",
    )

    assert metadata["path"] == "consumption.csv"
    assert metadata["rows"] == 48
    assert metadata["unique_timestamps"] == 48
    assert metadata["start"] == (
        "2026-06-01T00:00:00"
    )
    assert metadata["end"] == (
        "2026-06-02T23:00:00"
    )


def test_build_dataset_metadata_rejects_missing_datetime() -> None:
    df = pd.DataFrame(
        {
            "consumption_kwh": [1.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing required column",
    ):
        build_dataset_metadata(
            df=df,
            file_path="consumption.csv",
        )


def test_build_run_manifest_contains_scenario_data(
    tmp_path,
) -> None:
    consumption_path = (
        tmp_path / "consumption.csv"
    )
    price_path = tmp_path / "prices.csv"
    solar_path = tmp_path / "solar.csv"

    build_consumption_df().to_csv(
        consumption_path,
        index=False,
    )
    build_price_df().to_csv(
        price_path,
        index=False,
    )
    solar_path.write_text(
        "placeholder",
        encoding="utf-8",
    )

    scenario = replace(
        get_project_scenario(
            "uci_omie_june_2026"
        ),
        consumption_data_path=str(
            consumption_path
        ),
        hourly_price_data_path=str(
            price_path
        ),
        pvgis_solar_data_path=str(
            solar_path
        ),
    )

    manifest = build_run_manifest(
        scenario=scenario,
        consumption_df=build_consumption_df(),
        price_df=build_price_df(),
        output_paths=[
            "reports/example.csv",
            "reports/example.csv",
            "images/example.png",
        ],
        solar_peak_powers_kw=[
            1.0,
            2.0,
        ],
        battery_capacities_kwh=[
            0.0,
            2.0,
        ],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        days_per_year=365,
    )

    assert manifest["manifest_version"] == 1
    assert manifest["scenario"]["name"] == (
        "uci_omie_june_2026"
    )
    assert manifest["scenario"]["random_seed"] == 42
    assert manifest["datasets"]["consumption"]["rows"] == 48
    assert manifest["datasets"]["hourly_prices"]["rows"] == 48

    assert manifest["outputs"] == [
        "images/example.png",
        "reports/example.csv",
    ]


def test_write_run_manifest_creates_json_file(
    tmp_path,
) -> None:
    output_path = (
        tmp_path / "run_manifest.json"
    )

    manifest = {
        "manifest_version": 1,
        "scenario": {
            "name": "test",
        },
    }

    write_run_manifest(
        manifest=manifest,
        output_path=str(output_path),
    )

    loaded_manifest = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert loaded_manifest == manifest