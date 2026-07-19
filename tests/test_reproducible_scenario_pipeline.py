from dataclasses import replace

import pandas as pd
from pandas.testing import assert_frame_equal

from forecasting import run_consumption_forecast
from optimization import run_economic_grid_search
from scenario_registry import get_project_scenario
from scenario_validation import (
    validate_project_scenario_data,
)
from price_model_factory import HourlyPriceModel

def build_reproducible_consumption_data() -> pd.DataFrame:
    datetimes = pd.date_range(
        start="2026-06-01 00:00:00",
        periods=72,
        freq="h",
    )

    consumption = []

    for timestamp in datetimes:
        hour = timestamp.hour

        if 0 <= hour < 7:
            value = 0.4
        elif 7 <= hour < 10:
            value = 1.4
        elif 10 <= hour < 18:
            value = 0.8
        elif 18 <= hour < 23:
            value = 1.8
        else:
            value = 0.7

        consumption.append(value)

    return pd.DataFrame(
        {
            "datetime": datetimes,
            "consumption_kwh": consumption,
        }
    )


def build_reproducible_price_data() -> pd.DataFrame:
    datetimes = pd.date_range(
        start="2026-06-01 00:00:00",
        periods=72,
        freq="h",
    )

    prices = []

    for timestamp in datetimes:
        hour = timestamp.hour

        if 0 <= hour < 8:
            price = 0.08
        elif 8 <= hour < 18:
            price = 0.04
        else:
            price = 0.16

        prices.append(price)

    return pd.DataFrame(
        {
            "datetime": datetimes,
            "price_eur_per_kwh": prices,
        }
    )


def build_test_scenario(
    tmp_path,
    consumption_df: pd.DataFrame,
    price_df: pd.DataFrame,
):
    consumption_path = (
        tmp_path / "consumption.csv"
    )
    price_path = (
        tmp_path / "prices.csv"
    )
    solar_path = (
        tmp_path / "solar.csv"
    )

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

    return replace(
        get_project_scenario(
            "uci_omie_june_2026"
        ),
        name="reproducibility_test",
        consumption_data_path=str(
            consumption_path
        ),
        hourly_price_data_path=str(
            price_path
        ),
        pvgis_solar_data_path=str(
            solar_path
        ),
        random_seed=42,
    )


def run_small_forecast(
    consumption_df: pd.DataFrame,
    random_seed: int,
) -> dict:
    return run_consumption_forecast(
        df=consumption_df,
        test_size_ratio=0.20,
        random_state=random_seed,
    )


def run_small_optimization(
    consumption_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> pd.DataFrame:
    price_model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.07,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
        allow_negative_prices=True,
    )

    return run_economic_grid_search(
        consumption_df=consumption_df,
        solar_peak_powers_kw=[
            0.0,
            1.0,
        ],
        battery_capacities_kwh=[
            0.0,
            1.0,
        ],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=800.0,
        solar_cost_per_kw=900.0,
        battery_cost_per_kwh=500.0,
        price_model=price_model,
        simulation_days=3,
        pvgis_df=None,
    )


def test_same_forecast_seed_produces_same_results() -> None:
    consumption_df = (
        build_reproducible_consumption_data()
    )

    first_run = run_small_forecast(
        consumption_df=consumption_df,
        random_seed=42,
    )

    second_run = run_small_forecast(
        consumption_df=consumption_df,
        random_seed=42,
    )

    assert_frame_equal(
        first_run["results_df"],
        second_run["results_df"],
    )

    assert first_run["metrics"] == (
        second_run["metrics"]
    )


def test_same_optimization_inputs_produce_same_results() -> None:
    consumption_df = (
        build_reproducible_consumption_data()
    )
    price_df = (
        build_reproducible_price_data()
    )

    first_results = run_small_optimization(
        consumption_df=consumption_df,
        price_df=price_df,
    )

    second_results = run_small_optimization(
        consumption_df=consumption_df,
        price_df=price_df,
    )

    assert_frame_equal(
        first_results,
        second_results,
    )


def test_small_project_scenario_is_valid_and_reproducible(
    tmp_path,
) -> None:
    consumption_df = (
        build_reproducible_consumption_data()
    )
    price_df = (
        build_reproducible_price_data()
    )

    scenario = build_test_scenario(
        tmp_path=tmp_path,
        consumption_df=consumption_df,
        price_df=price_df,
    )

    validation_report = (
        validate_project_scenario_data(
            scenario=scenario,
            consumption_df=consumption_df,
            price_df=price_df,
        )
    )

    forecast_results = run_small_forecast(
        consumption_df=consumption_df,
        random_seed=scenario.random_seed,
    )

    optimization_results = (
        run_small_optimization(
            consumption_df=consumption_df,
            price_df=price_df,
        )
    )

    assert validation_report.is_valid is True
    assert validation_report.consumption.rows == 72
    assert validation_report.prices is not None

    assert (
        forecast_results["results_df"]
        ["datetime"]
        .between(
            consumption_df["datetime"].min(),
            consumption_df["datetime"].max(),
        )
        .all()
    )

    assert len(optimization_results) == 4