import pandas as pd
import pytest

from omie_price_loader import (
    aggregate_omie_prices_to_hourly,
    load_omie_quarter_hour_prices,
)


def build_omie_test_file_text() -> str:
    lines = ["MARGINALPDBC;"]

    for period in range(1, 97):
        price = 100 + period

        lines.append(f"2026;07;05;{period};{price};{price};")

    lines.append("*")

    return "\n".join(lines)


def test_load_omie_quarter_hour_prices_returns_96_rows(tmp_path) -> None:
    omie_file = tmp_path / "marginalpdbc_test.1"

    omie_file.write_text(
        build_omie_test_file_text(),
        encoding="utf-8",
    )

    price_df = load_omie_quarter_hour_prices(str(omie_file))

    assert len(price_df) == 96


def test_load_omie_quarter_hour_prices_builds_expected_datetimes(
    tmp_path,
) -> None:
    omie_file = tmp_path / "marginalpdbc_test.1"

    omie_file.write_text(
        build_omie_test_file_text(),
        encoding="utf-8",
    )

    price_df = load_omie_quarter_hour_prices(str(omie_file))

    assert price_df.iloc[0]["datetime"] == pd.Timestamp("2026-07-05 00:00:00")

    assert price_df.iloc[-1]["datetime"] == pd.Timestamp("2026-07-05 23:45:00")


def test_load_omie_quarter_hour_prices_converts_price_units(
    tmp_path,
) -> None:
    omie_file = tmp_path / "marginalpdbc_test.1"

    omie_file.write_text(
        build_omie_test_file_text(),
        encoding="utf-8",
    )

    price_df = load_omie_quarter_hour_prices(str(omie_file))

    assert price_df.iloc[0]["price_eur_per_kwh"] == pytest.approx(0.101)


def test_aggregate_omie_prices_to_hourly_returns_24_rows(
    tmp_path,
) -> None:
    omie_file = tmp_path / "marginalpdbc_test.1"

    omie_file.write_text(
        build_omie_test_file_text(),
        encoding="utf-8",
    )

    quarter_hour_df = load_omie_quarter_hour_prices(str(omie_file))

    hourly_df = aggregate_omie_prices_to_hourly(quarter_hour_df)

    assert len(hourly_df) == 24


def test_aggregate_omie_prices_to_hourly_calculates_mean_price(
    tmp_path,
) -> None:
    omie_file = tmp_path / "marginalpdbc_test.1"

    omie_file.write_text(
        build_omie_test_file_text(),
        encoding="utf-8",
    )

    quarter_hour_df = load_omie_quarter_hour_prices(str(omie_file))

    hourly_df = aggregate_omie_prices_to_hourly(quarter_hour_df)

    expected_first_hour_price = (0.101 + 0.102 + 0.103 + 0.104) / 4

    assert hourly_df.iloc[0]["price_eur_per_kwh"] == pytest.approx(
        expected_first_hour_price
    )
