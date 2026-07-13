from price_mode import build_electricity_price_mode_description


def test_price_mode_description_for_hourly_prices() -> None:
    description = build_electricity_price_mode_description(
        use_hourly_price_data=True,
        hourly_price_data_path=(
            "data/processed/omie_hourly_prices.csv"
        ),
        tariff_profile_name="spanish_2_0td_example",
    )

    assert "Hourly electricity prices" in description
    assert "data/processed/omie_hourly_prices.csv" in description
    assert "fixed power cost" in description
    assert "surplus compensation" in description
    assert "spanish_2_0td_example" in description


def test_price_mode_description_for_tariff_profile() -> None:
    description = build_electricity_price_mode_description(
        use_hourly_price_data=False,
        hourly_price_data_path=(
            "data/processed/omie_hourly_prices.csv"
        ),
        tariff_profile_name="spanish_2_0td_example",
    )

    assert description == (
        "Time-of-use electricity prices from tariff profile "
        "'spanish_2_0td_example'"
    )