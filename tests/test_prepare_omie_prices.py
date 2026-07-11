import pandas as pd
import pytest

from scripts.prepare_omie_prices import (
    build_hourly_omie_price_dataframe,
    find_omie_files,
    prepare_omie_prices,
)


def build_omie_file_text(
    year: int,
    month: int,
    day: int,
    base_price: float,
) -> str:
    lines = ["MARGINALPDBC;"]

    for period in range(1, 97):
        price = base_price + period

        lines.append(
            f"{year};{month:02d};{day:02d};"
            f"{period};{price};{price};"
        )

    lines.append("*")

    return "\n".join(lines)


def test_find_omie_files_returns_sorted_matching_files(
    tmp_path,
) -> None:
    first_file = tmp_path / "marginalpdbc_20260705.1"
    second_file = tmp_path / "marginalpdbc_20260706.1"
    ignored_file = tmp_path / "other_file.txt"

    second_file.write_text("", encoding="utf-8")
    first_file.write_text("", encoding="utf-8")
    ignored_file.write_text("", encoding="utf-8")

    omie_files = find_omie_files(str(tmp_path))

    assert omie_files == [
        first_file,
        second_file,
    ]


def test_find_omie_files_raises_error_when_none_exist(
    tmp_path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="No OMIE files found",
    ):
        find_omie_files(str(tmp_path))


def test_build_hourly_omie_price_dataframe_combines_days(
    tmp_path,
) -> None:
    first_file = tmp_path / "marginalpdbc_20260705.1"
    second_file = tmp_path / "marginalpdbc_20260706.1"

    first_file.write_text(
        build_omie_file_text(
            year=2026,
            month=7,
            day=5,
            base_price=100,
        ),
        encoding="utf-8",
    )

    second_file.write_text(
        build_omie_file_text(
            year=2026,
            month=7,
            day=6,
            base_price=200,
        ),
        encoding="utf-8",
    )

    hourly_df = build_hourly_omie_price_dataframe(
        [
            first_file,
            second_file,
        ]
    )

    assert len(hourly_df) == 48
    assert hourly_df["datetime"].is_monotonic_increasing
    assert hourly_df["datetime"].nunique() == 48


def test_prepare_omie_prices_writes_output_csv(
    tmp_path,
) -> None:
    input_directory = tmp_path / "raw"
    output_file = (
        tmp_path
        / "processed"
        / "omie_hourly_prices.csv"
    )

    input_directory.mkdir()

    omie_file = (
        input_directory
        / "marginalpdbc_20260705.1"
    )

    omie_file.write_text(
        build_omie_file_text(
            year=2026,
            month=7,
            day=5,
            base_price=100,
        ),
        encoding="utf-8",
    )

    hourly_df = prepare_omie_prices(
        input_directory=str(input_directory),
        output_path=str(output_file),
    )

    assert output_file.exists()
    assert len(hourly_df) == 24

    saved_df = pd.read_csv(output_file)

    assert list(saved_df.columns) == [
        "datetime",
        "price_eur_per_kwh",
    ]

    assert len(saved_df) == 24


def test_build_hourly_omie_price_dataframe_removes_duplicates(
    tmp_path,
) -> None:
    first_file = tmp_path / "marginalpdbc_first.1"
    second_file = tmp_path / "marginalpdbc_second.1"

    first_file.write_text(
        build_omie_file_text(
            year=2026,
            month=7,
            day=5,
            base_price=100,
        ),
        encoding="utf-8",
    )

    second_file.write_text(
        build_omie_file_text(
            year=2026,
            month=7,
            day=5,
            base_price=200,
        ),
        encoding="utf-8",
    )

    hourly_df = build_hourly_omie_price_dataframe(
        [
            first_file,
            second_file,
        ]
    )

    assert len(hourly_df) == 24
    assert hourly_df["datetime"].nunique() == 24