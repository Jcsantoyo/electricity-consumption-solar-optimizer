import pytest

from price_mode import build_electricity_price_mode_description


def test_price_mode_description_for_hourly_prices() -> None:
    description = build_electricity_price_mode_description(
        price_mode="wholesale_hourly",
        hourly_price_data_path="data/processed/omie_hourly_prices.csv",
        tariff_profile_name="spanish_2_0td_example",
    )

    assert "Hourly wholesale electricity prices" in description
    assert "data/processed/omie_hourly_prices.csv" in description
    assert "fixed power cost" in description
    assert "surplus compensation" in description
    assert "spanish_2_0td_example" in description


def test_price_mode_description_for_fixed_tariff() -> None:
    description = build_electricity_price_mode_description(
        price_mode="fixed",
        hourly_price_data_path=None,
        tariff_profile_name="flat_price",
    )

    assert description == (
        "Fixed electricity price from tariff profile 'flat_price'"
    )


def test_price_mode_description_for_time_of_use_tariff() -> None:
    description = build_electricity_price_mode_description(
        price_mode="time_of_use",
        hourly_price_data_path=None,
        tariff_profile_name="spanish_2_0td_example",
    )

    assert description == (
        "Time-of-use electricity prices from tariff profile "
        "'spanish_2_0td_example'"
    )


def test_hourly_price_mode_requires_a_data_path() -> None:
    with pytest.raises(ValueError, match="requires an hourly price data path"):
        build_electricity_price_mode_description(
            price_mode="wholesale_hourly",
            hourly_price_data_path=None,
            tariff_profile_name="spanish_2_0td_example",
        )


def test_invalid_price_mode_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid electricity price mode"):
        build_electricity_price_mode_description(
            price_mode="invalid",
            hourly_price_data_path=None,
            tariff_profile_name="flat_price",
        )
