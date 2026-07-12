import pandas as pd
import pytest
import config

from price_loader import (
    load_hourly_prices,
    prepare_hourly_price_data,
    validate_hourly_price_columns,
    load_hourly_prices_if_enabled,
    validate_hourly_price_coverage
)


def test_validate_hourly_price_columns_accepts_valid_columns() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "price_eur_per_kwh": [0.12],
        }
    )

    validate_hourly_price_columns(price_df)


def test_validate_hourly_price_columns_raises_error_for_missing_columns() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "price": [0.12],
        }
    )

    with pytest.raises(ValueError, match="Missing required hourly price columns"):
        validate_hourly_price_columns(price_df)


def test_prepare_hourly_price_data_converts_and_sorts_data() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 02:00:00",
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "price_eur_per_kwh": [
                "0.10",
                "0.12",
                "0.11",
            ],
        }
    )

    prepared_df = prepare_hourly_price_data(price_df)

    assert list(prepared_df["price_eur_per_kwh"]) == [0.12, 0.11, 0.10]
    assert prepared_df["datetime"].is_monotonic_increasing


def test_prepare_hourly_price_data_raises_error_for_invalid_datetime() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": ["not-a-date"],
            "price_eur_per_kwh": [0.12],
        }
    )

    with pytest.raises(ValueError, match="invalid datetime"):
        prepare_hourly_price_data(price_df)


def test_prepare_hourly_price_data_raises_error_for_invalid_price() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "price_eur_per_kwh": ["not-a-price"],
        }
    )

    with pytest.raises(ValueError, match="invalid price"):
        prepare_hourly_price_data(price_df)


def test_prepare_hourly_price_data_raises_error_for_negative_price() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": ["2025-01-01 00:00:00"],
            "price_eur_per_kwh": [-0.01],
        }
    )

    with pytest.raises(ValueError, match="negative prices"):
        prepare_hourly_price_data(price_df)


def test_load_hourly_prices_loads_valid_csv(tmp_path) -> None:
    price_file = tmp_path / "hourly_prices.csv"

    price_file.write_text(
        "datetime,price_eur_per_kwh\n"
        "2025-01-01 01:00:00,0.11\n"
        "2025-01-01 00:00:00,0.12\n",
        encoding="utf-8",
    )

    price_df = load_hourly_prices(str(price_file))

    assert len(price_df) == 2
    assert list(price_df["price_eur_per_kwh"]) == [0.12, 0.11]
    assert price_df["datetime"].is_monotonic_increasing


def test_load_hourly_prices_raises_error_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError, match="Hourly price file not found"):
        load_hourly_prices("missing_hourly_prices.csv")

def test_hourly_price_configuration_exists() -> None:
    assert isinstance(config.USE_HOURLY_PRICE_DATA, bool)
    assert isinstance(config.HOURLY_PRICE_DATA_PATH, str)


def test_hourly_price_data_is_disabled_by_default() -> None:
    assert config.USE_HOURLY_PRICE_DATA is False


def test_hourly_price_data_path_points_to_raw_data_folder() -> None:
    assert config.HOURLY_PRICE_DATA_PATH.startswith("data/raw/")
    assert config.HOURLY_PRICE_DATA_PATH.endswith(".csv")

def test_load_hourly_prices_if_enabled_returns_none_when_disabled() -> None:
    price_df = load_hourly_prices_if_enabled(
        use_hourly_price_data=False,
        file_path="missing_hourly_prices.csv",
    )

    assert price_df is None


def test_load_hourly_prices_if_enabled_loads_file_when_enabled(tmp_path) -> None:
    price_file = tmp_path / "hourly_prices.csv"

    price_file.write_text(
        "datetime,price_eur_per_kwh\n"
        "2025-01-01 01:00:00,0.11\n"
        "2025-01-01 00:00:00,0.12\n",
        encoding="utf-8",
    )

    price_df = load_hourly_prices_if_enabled(
        use_hourly_price_data=True,
        file_path=str(price_file),
    )

    assert price_df is not None
    assert len(price_df) == 2
    assert list(price_df["price_eur_per_kwh"]) == [0.12, 0.11]

def test_validate_hourly_price_coverage_accepts_complete_coverage() -> None:
    consumption_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "consumption_kwh": [
                1.0,
                2.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "price_eur_per_kwh": [
                0.10,
                0.20,
            ],
        }
    )

    validate_hourly_price_coverage(
        consumption_df=consumption_df,
        price_df=price_df,
    )


def test_validate_hourly_price_coverage_raises_error_for_missing_timestamp() -> None:
    consumption_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "consumption_kwh": [
                1.0,
                2.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
            ],
            "price_eur_per_kwh": [
                0.10,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="does not cover 1 consumption timestamps",
    ):
        validate_hourly_price_coverage(
            consumption_df=consumption_df,
            price_df=price_df,
        )


def test_validate_hourly_price_coverage_ignores_extra_price_timestamps() -> None:
    consumption_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
            ],
            "consumption_kwh": [
                1.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": [
                "2025-01-01 00:00:00",
                "2025-01-01 01:00:00",
            ],
            "price_eur_per_kwh": [
                0.10,
                0.20,
            ],
        }
    )

    validate_hourly_price_coverage(
        consumption_df=consumption_df,
        price_df=price_df,
    )

def test_prepare_hourly_price_data_allows_negative_prices_when_enabled() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": [
                "2026-07-05 10:00:00",
                "2026-07-05 11:00:00",
            ],
            "price_eur_per_kwh": [
                -0.0000475,
                -0.0001025,
            ],
        }
    )

    prepared_df = prepare_hourly_price_data(
        price_df,
        allow_negative_prices=True,
    )

    assert list(prepared_df["price_eur_per_kwh"]) == pytest.approx(
        [
            -0.0000475,
            -0.0001025,
        ]
    )

def test_load_hourly_prices_allows_negative_prices_when_enabled(
    tmp_path,
) -> None:
    price_file = tmp_path / "omie_hourly_prices.csv"

    price_file.write_text(
        "datetime,price_eur_per_kwh\n"
        "2026-07-05 10:00:00,-0.0000475\n"
        "2026-07-05 11:00:00,-0.0001025\n",
        encoding="utf-8",
    )

    price_df = load_hourly_prices(
        file_path=str(price_file),
        allow_negative_prices=True,
    )

    assert len(price_df) == 2
    assert price_df["price_eur_per_kwh"].min() < 0

def test_negative_hourly_price_configuration_exists() -> None:
    assert isinstance(
        config.ALLOW_NEGATIVE_HOURLY_PRICES,
        bool,
    )