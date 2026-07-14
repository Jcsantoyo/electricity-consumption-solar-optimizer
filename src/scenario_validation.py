from dataclasses import dataclass

import pandas as pd

from price_loader import validate_hourly_price_coverage
from project_scenario import ProjectScenario

@dataclass(frozen=True)
class TimeSeriesSummary:
    name: str
    rows: int
    unique_timestamps: int
    start: pd.Timestamp
    end: pd.Timestamp
    frequency: str

@dataclass(frozen=True)
class ScenarioValidationReport:
    scenario_name: str
    consumption: TimeSeriesSummary
    prices: TimeSeriesSummary | None
    forecast_mode: str
    forecast_test_rows: int
    is_valid: bool

def prepare_datetime_series(
    df: pd.DataFrame,
    dataset_name: str
) -> pd.Series:
    if "datetime" not in df.columns:
        raise ValueError(f"{dataset_name} data is missing required column: datetime")
    
    datetimes = pd.to_datetime(df["datetime"], errors="coerce")

    if datetimes.isna().any():
        raise ValueError(f"{dataset_name} data contains invalid datetime values")
    
    return datetimes

def validate_unique_timestamps(
    datetimes: pd.Series,
    dataset_name: str
) -> None:
    duplicated = datetimes.duplicated(keep=False)

    if duplicated.any():
        duplicated_count = int(duplicated.sum())

        raise ValueError(f"{dataset_name} data contains {duplicated_count} duplicated timestamps")
    
def validate_hourly_frequency(datetimes: pd.Series, dataset_name: str) -> None:
    sorted_datetimes = datetimes.sort_values().reset_index(drop=True)

    if len(sorted_datetimes) < 2:
        raise ValueError(f"{dataset_name} data must contain at least two timestamps")
    
    expected_datetimes = pd.date_range(
        start=sorted_datetimes.iloc[0],
        end=sorted_datetimes.iloc[-1], 
        freq="h"
    )

    actual_timestamps = set(sorted_datetimes)

    expected_datetimes = set(expected_datetimes)

    missing_timestamps = expected_datetimes - actual_timestamps

    if missing_timestamps:
        first_missing = min(missing_timestamps)
        last_missing = max(missing_timestamps)

        raise ValueError(
            f"{dataset_name} data is not continuous hourly data. "
            f"Missing {len(missing_timestamps)} timestamps "
            f"between {first_missing} and {last_missing}"
        )
    
def validate_consumption_values(
    consumption_df: pd.DataFrame,
) -> None:
    if "consumption_kwh" not in consumption_df.columns:
        raise ValueError(
            "Consumption data is missing required column: "
            "consumption_kwh"
        )

    consumption = pd.to_numeric(
        consumption_df["consumption_kwh"],
        errors="coerce",
    )

    if consumption.isna().any():
        raise ValueError(
            "Consumption data contains invalid consumption values"
        )

    if (consumption < 0).any():
        raise ValueError(
            "Consumption data contains negative consumption values"
        )
    
def summarize_time_series(
    df: pd.DataFrame,
    dataset_name: str
) -> TimeSeriesSummary:
    datetimes = prepare_datetime_series(df, dataset_name)

    return TimeSeriesSummary(
        name=dataset_name,
        rows=len(df),
        unique_timestamps=datetimes.nunique(),
        start=datetimes.min(),
        end=datetimes.max(),
        frequency="hourly"
    )


def calculate_backtest_rows(
    total_rows: int,
    test_size_ratio: float,
    maximum_lag_hours: int = 24
) -> int:
    usable_rows = total_rows - maximum_lag_hours

    if usable_rows <= 1:
        raise ValueError("Consumption data does not contain enough rows for "
                         "forecasting after lag generation")
    
    test_rows = usable_rows - int(usable_rows * (1 - test_size_ratio))

    if test_rows <= 0:
        raise ValueError("Forecast configuration produces an empty test partition")
    
    return test_rows

def validate_consumption_time_series(
    consumption_df: pd.DataFrame,
) -> TimeSeriesSummary:
    validate_consumption_values(
        consumption_df
    )

    datetimes = prepare_datetime_series(
        df=consumption_df,
        dataset_name="Consumption",
    )

    validate_unique_timestamps(
        datetimes=datetimes,
        dataset_name="Consumption",
    )

    validate_hourly_frequency(
        datetimes=datetimes,
        dataset_name="Consumption",
    )

    return summarize_time_series(
        df=consumption_df,
        dataset_name="Consumption",
    )


def validate_price_time_series(
    price_df: pd.DataFrame,
) -> TimeSeriesSummary:
    datetimes = prepare_datetime_series(
        df=price_df,
        dataset_name="Hourly price",
    )

    validate_unique_timestamps(
        datetimes=datetimes,
        dataset_name="Hourly price",
    )

    validate_hourly_frequency(
        datetimes=datetimes,
        dataset_name="Hourly price",
    )

    return summarize_time_series(
        df=price_df,
        dataset_name="Hourly price",
    )


def validate_project_scenario_data(
    scenario: ProjectScenario,
    consumption_df: pd.DataFrame,
    price_df: pd.DataFrame | None = None,
) -> ScenarioValidationReport:
    scenario.validate()
    scenario.validate_input_files_exist()

    consumption_summary = (
        validate_consumption_time_series(
            consumption_df
        )
    )

    forecast_test_rows = 0

    if scenario.forecast_mode == "backtest":
        forecast_test_rows = calculate_backtest_rows(
            total_rows=len(consumption_df),
            test_size_ratio=(
                scenario.forecast_test_size_ratio
            ),
        )

    price_summary = None

    if scenario.uses_hourly_prices:
        if price_df is None:
            raise ValueError(
                "Hourly price mode requires loaded price data"
            )

        price_summary = validate_price_time_series(
            price_df
        )

        validate_hourly_price_coverage(
            consumption_df=consumption_df,
            price_df=price_df,
        )

    return ScenarioValidationReport(
        scenario_name=scenario.name,
        consumption=consumption_summary,
        prices=price_summary,
        forecast_mode=scenario.forecast_mode,
        forecast_test_rows=forecast_test_rows,
        is_valid=True,
    )


def format_validation_report(
    report: ScenarioValidationReport,
) -> str:
    lines = [
        "Scenario validation",
        "===================",
        "",
        f"Scenario: {report.scenario_name}",
        f"Status: {'valid' if report.is_valid else 'invalid'}",
        "",
        "Consumption data:",
        f"- Rows: {report.consumption.rows}",
        (
            "- Unique timestamps: "
            f"{report.consumption.unique_timestamps}"
        ),
        f"- Start: {report.consumption.start}",
        f"- End: {report.consumption.end}",
        (
            "- Frequency: "
            f"{report.consumption.frequency}"
        ),
        "",
        f"Forecast mode: {report.forecast_mode}",
        (
            "Forecast test rows: "
            f"{report.forecast_test_rows}"
        ),
    ]

    if report.prices is not None:
        lines.extend(
            [
                "",
                "Hourly price data:",
                f"- Rows: {report.prices.rows}",
                (
                    "- Unique timestamps: "
                    f"{report.prices.unique_timestamps}"
                ),
                f"- Start: {report.prices.start}",
                f"- End: {report.prices.end}",
                (
                    "- Frequency: "
                    f"{report.prices.frequency}"
                ),
                "- Consumption coverage: complete",
            ]
        )

    return "\n".join(lines)