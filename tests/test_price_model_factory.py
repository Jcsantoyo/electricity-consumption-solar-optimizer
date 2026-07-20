import pytest
import pandas as pd

from electricity_price_models import (
    FixedPriceModel,
    TimeOfUsePriceModel,
    HourlyPriceModel,
)
from price_model_factory import (
    build_electricity_price_model,
)
from project_scenario import ProjectScenario


def build_test_scenario(
    price_mode: str,
    hourly_price_data_path: str | None = None,
    allow_negative_hourly_prices: bool = False,
) -> ProjectScenario:
    return ProjectScenario(
        name="test_scenario",
        consumption_data_path=("data/consumption.csv"),
        use_pvgis_solar_data=False,
        pvgis_solar_data_path=("data/solar.csv"),
        price_mode=price_mode,
        tariff_profile_name="test_tariff",
        hourly_price_data_path=(hourly_price_data_path),
        allow_negative_hourly_prices=(allow_negative_hourly_prices),
        forecast_mode="backtest",
        forecast_test_size_ratio=0.20,
        random_seed=42,
    )


def build_test_tariff_profile() -> dict[str, float]:
    return {
        "peak_price_eur_per_kwh": 0.25,
        "flat_price_eur_per_kwh": 0.20,
        "off_peak_price_eur_per_kwh": 0.12,
        "surplus_compensation_eur_per_kwh": 0.07,
        "contracted_power_kw": 4.6,
        "power_price_eur_per_kw_year": 35.0,
    }


def test_factory_builds_fixed_price_model() -> None:
    scenario = build_test_scenario(price_mode="fixed")

    model = build_electricity_price_model(
        scenario=scenario,
        tariff_profile=(build_test_tariff_profile()),
    )

    assert isinstance(
        model,
        FixedPriceModel,
    )

    assert model.fixed_price_eur_per_kwh == (pytest.approx(0.20))

    assert model.surplus_compensation_price == (pytest.approx(0.07))

    assert model.contracted_power_kw == (pytest.approx(4.6))

    assert model.power_price_eur_per_kw_year == (pytest.approx(35.0))


def test_factory_rejects_unsupported_price_mode() -> None:
    scenario = build_test_scenario(price_mode="unknown")

    with pytest.raises(
        ValueError,
        match=("Unsupported electricity price mode: unknown"),
    ):
        build_electricity_price_model(
            scenario=scenario,
            tariff_profile=(build_test_tariff_profile()),
        )


def test_factory_builds_time_of_use_price_model() -> None:
    scenario = build_test_scenario(price_mode="time_of_use")

    model = build_electricity_price_model(
        scenario=scenario,
        tariff_profile=(build_test_tariff_profile()),
    )

    assert isinstance(
        model,
        TimeOfUsePriceModel,
    )

    assert model.peak_price_eur_per_kwh == (pytest.approx(0.25))

    assert model.flat_price_eur_per_kwh == (pytest.approx(0.20))

    assert model.off_peak_price_eur_per_kwh == (pytest.approx(0.12))

    assert model.surplus_compensation_price == (pytest.approx(0.07))

    assert model.contracted_power_kw == (pytest.approx(4.6))

    assert model.power_price_eur_per_kw_year == (pytest.approx(35.0))


def test_factory_builds_hourly_price_model() -> None:
    hourly_price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 00:00:00",
                    "2026-06-01 01:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                -0.05,
                0.20,
            ],
        }
    )

    scenario = build_test_scenario(
        price_mode="wholesale_hourly",
        hourly_price_data_path=("data/hourly_prices.csv"),
        allow_negative_hourly_prices=True,
    )

    model = build_electricity_price_model(
        scenario=scenario,
        tariff_profile=(build_test_tariff_profile()),
        hourly_price_df=hourly_price_df,
    )

    assert isinstance(
        model,
        HourlyPriceModel,
    )

    assert model.price_df.equals(hourly_price_df)

    assert model.surplus_compensation_price == (pytest.approx(0.07))

    assert model.contracted_power_kw == (pytest.approx(4.6))

    assert model.power_price_eur_per_kw_year == (pytest.approx(35.0))

    assert model.allow_negative_prices is True


def test_factory_requires_hourly_price_data() -> None:
    scenario = build_test_scenario(
        price_mode="wholesale_hourly",
        hourly_price_data_path=("data/hourly_prices.csv"),
    )

    with pytest.raises(
        ValueError,
        match=("Wholesale hourly price mode requires hourly price data"),
    ):
        build_electricity_price_model(
            scenario=scenario,
            tariff_profile=(build_test_tariff_profile()),
            hourly_price_df=None,
        )
