from dataclasses import replace

import pandas as pd
import pytest

from scenario_registry import get_project_scenario
from scenario_validation import (
    calculate_backtest_rows,
    format_validation_report,
    validate_consumption_time_series,
    validate_project_scenario_data,
)


def build_consumption_df(
    periods: int = 48,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2026-06-01 00:00:00",
                periods=periods,
                freq="h",
            ),
            "consumption_kwh": [1.0] * periods,
        }
    )


def build_price_df(
    periods: int = 48,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2026-06-01 00:00:00",
                periods=periods,
                freq="h",
            ),
            "price_eur_per_kwh": [0.10] * periods,
        }
    )


def test_consumption_validation_accepts_hourly_data() -> None:
    summary = validate_consumption_time_series(build_consumption_df())

    assert summary.rows == 48
    assert summary.unique_timestamps == 48
    assert summary.frequency == "hourly"


def test_consumption_validation_rejects_duplicates() -> None:
    consumption_df = build_consumption_df()

    consumption_df.loc[
        1,
        "datetime",
    ] = consumption_df.loc[
        0,
        "datetime",
    ]

    with pytest.raises(
        ValueError,
        match="duplicated timestamps",
    ):
        validate_consumption_time_series(consumption_df)


def test_consumption_validation_rejects_hourly_gap() -> None:
    consumption_df = build_consumption_df().drop(index=10).reset_index(drop=True)

    with pytest.raises(
        ValueError,
        match="not continuous hourly data",
    ):
        validate_consumption_time_series(consumption_df)


def test_consumption_validation_rejects_negative_values() -> None:
    consumption_df = build_consumption_df()

    consumption_df.loc[
        5,
        "consumption_kwh",
    ] = -1.0

    with pytest.raises(
        ValueError,
        match="negative consumption",
    ):
        validate_consumption_time_series(consumption_df)


def test_calculate_backtest_rows_matches_forecast_split() -> None:
    test_rows = calculate_backtest_rows(
        total_rows=720,
        test_size_ratio=0.20,
        maximum_lag_hours=24,
    )

    assert test_rows == 140


def test_project_scenario_validation_accepts_complete_data(
    tmp_path,
) -> None:
    consumption_path = tmp_path / "consumption.csv"
    price_path = tmp_path / "prices.csv"
    solar_path = tmp_path / "solar.csv"

    consumption_df = build_consumption_df()
    price_df = build_price_df()

    consumption_df.to_csv(
        consumption_path,
        index=False,
    )
    price_df.to_csv(
        price_path,
        index=False,
    )
    solar_path.write_text(
        "placeholder",
        encoding="utf-8",
    )

    scenario = replace(
        get_project_scenario("uci_omie_june_2026"),
        consumption_data_path=str(consumption_path),
        hourly_price_data_path=str(price_path),
        pvgis_solar_data_path=str(solar_path),
    )

    report = validate_project_scenario_data(
        scenario=scenario,
        consumption_df=consumption_df,
        price_df=price_df,
    )

    assert report.is_valid is True
    assert report.prices is not None
    assert report.forecast_mode == "backtest"


def test_project_scenario_validation_rejects_missing_prices(
    tmp_path,
) -> None:
    consumption_path = tmp_path / "consumption.csv"
    price_path = tmp_path / "prices.csv"
    solar_path = tmp_path / "solar.csv"

    consumption_df = build_consumption_df()
    price_df = build_price_df(periods=47)

    consumption_df.to_csv(
        consumption_path,
        index=False,
    )
    price_df.to_csv(
        price_path,
        index=False,
    )
    solar_path.write_text(
        "placeholder",
        encoding="utf-8",
    )

    scenario = replace(
        get_project_scenario("uci_omie_june_2026"),
        consumption_data_path=str(consumption_path),
        hourly_price_data_path=str(price_path),
        pvgis_solar_data_path=str(solar_path),
    )

    with pytest.raises(
        ValueError,
        match="does not cover 1 consumption timestamps",
    ):
        validate_project_scenario_data(
            scenario=scenario,
            consumption_df=consumption_df,
            price_df=price_df,
        )


def test_validation_report_contains_main_information(
    tmp_path,
) -> None:
    consumption_path = tmp_path / "consumption.csv"
    price_path = tmp_path / "prices.csv"
    solar_path = tmp_path / "solar.csv"

    consumption_df = build_consumption_df()
    price_df = build_price_df()

    consumption_df.to_csv(
        consumption_path,
        index=False,
    )
    price_df.to_csv(
        price_path,
        index=False,
    )
    solar_path.write_text(
        "placeholder",
        encoding="utf-8",
    )

    scenario = replace(
        get_project_scenario("uci_omie_june_2026"),
        consumption_data_path=str(consumption_path),
        hourly_price_data_path=str(price_path),
        pvgis_solar_data_path=str(solar_path),
    )

    report = validate_project_scenario_data(
        scenario=scenario,
        consumption_df=consumption_df,
        price_df=price_df,
    )

    text = format_validation_report(report)

    assert "Scenario validation" in text
    assert "Status: valid" in text
    assert "Consumption coverage: complete" in text
