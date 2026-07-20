import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from project_scenario import ProjectScenario


def get_git_commit_hash() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    commit_hash = result.stdout.strip()

    if not commit_hash:
        return None

    return commit_hash


def build_dataset_metadata(df: pd.DataFrame, file_path: str) -> dict[str, Any]:
    if "datetime" not in df.columns:
        raise ValueError("Dataset is missing required column: datetime")

    datetimes = pd.to_datetime(df["datetime"], errors="coerce")

    if datetimes.isna().any():
        raise ValueError(f"Dataset contains invalid datetime values: {file_path}")

    return {
        "path": file_path,
        "rows": len(df),
        "unique_timestamps": int(datetimes.nunique()),
        "start": datetimes.min().isoformat(),
        "end": datetimes.max().isoformat(),
    }


def build_run_manifest(
    scenario: ProjectScenario,
    consumption_df: pd.DataFrame,
    price_df: pd.DataFrame | None,
    output_paths: list[str],
    solar_peak_powers_kw: list[float],
    battery_capacities_kwh: list[float],
    battery_efficiency: float,
    max_charge_power_kw: float,
    max_discharge_power_kw: float,
    initial_battery_state_kwh: float,
    days_per_year: int,
) -> dict[str, Any]:
    scenario.validate()

    consumption_metadata = build_dataset_metadata(
        consumption_df, scenario.consumption_data_path
    )

    price_metadata = None

    if price_df is not None:
        if scenario.hourly_price_data_path is None:
            raise ValueError("Loaded hourly prices require an hourly price path")

        price_metadata = build_dataset_metadata(
            price_df, scenario.hourly_price_data_path
        )

    return {
        "manifest_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit_hash(),
        "scenario": {
            "name": scenario.name,
            "price_mode": scenario.price_mode,
            "tariff_profile": (scenario.tariff_profile_name),
            "use_pvgis_solar_data": (scenario.use_pvgis_solar_data),
            "pvgis_solar_data_path": (scenario.pvgis_solar_data_path),
            "allow_negative_hourly_prices": (scenario.allow_negative_hourly_prices),
            "forecast_mode": scenario.forecast_mode,
            "forecast_test_size_ratio": (scenario.forecast_test_size_ratio),
            "random_seed": scenario.random_seed,
        },
        "datasets": {
            "consumption": consumption_metadata,
            "hourly_prices": price_metadata,
        },
        "simulation": {
            "days_per_year": days_per_year,
            "solar_peak_powers_kw": (solar_peak_powers_kw),
            "battery_capacities_kwh": (battery_capacities_kwh),
            "battery_efficiency": battery_efficiency,
            "max_charge_power_kw": (max_charge_power_kw),
            "max_discharge_power_kw": (max_discharge_power_kw),
            "initial_battery_state_kwh": (initial_battery_state_kwh),
        },
        "outputs": sorted(set(output_paths)),
    }


def write_run_manifest(manifest: dict[str, Any], output_path: str) -> None:
    destination = Path(output_path)

    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
