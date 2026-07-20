from datetime import date

import pytest

from scripts.download_omie_prices import (
    build_omie_download_url,
    build_omie_filename,
    generate_date_range,
    parse_date,
    validate_downloaded_omie_content,
)


def test_parse_date_returns_expected_date() -> None:
    parsed_date = parse_date("2026-06-01")

    assert parsed_date == date(2026, 6, 1)


def test_parse_date_rejects_invalid_format() -> None:
    with pytest.raises(
        ValueError,
        match="Expected format",
    ):
        parse_date("01-06-2026")


def test_build_omie_filename_returns_expected_name() -> None:
    filename = build_omie_filename(date(2026, 6, 1))

    assert filename == "marginalpdbc_20260601.1"


def test_build_omie_download_url_contains_filename() -> None:
    url = build_omie_download_url(date(2026, 6, 1))

    assert "filename=marginalpdbc_20260601.1" in url
    assert "parents=marginalpdbc" in url


def test_generate_date_range_includes_both_limits() -> None:
    dates = generate_date_range(
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
    )

    assert dates == [
        date(2026, 6, 1),
        date(2026, 6, 2),
        date(2026, 6, 3),
    ]


def test_generate_date_range_rejects_reversed_dates() -> None:
    with pytest.raises(
        ValueError,
        match="End date cannot be earlier",
    ):
        generate_date_range(
            start_date=date(2026, 6, 3),
            end_date=date(2026, 6, 1),
        )


def test_validate_downloaded_omie_content_accepts_valid_content() -> None:
    content = b"MARGINALPDBC;\n2026;06;01;1;100;100;\n*"

    validate_downloaded_omie_content(
        content=content,
        filename="marginalpdbc_20260601.1",
    )


def test_validate_downloaded_omie_content_rejects_invalid_header() -> None:
    content = b"<html>Error</html>"

    with pytest.raises(
        ValueError,
        match="not a valid OMIE price file",
    ):
        validate_downloaded_omie_content(
            content=content,
            filename="marginalpdbc_20260601.1",
        )


def test_validate_downloaded_omie_content_rejects_missing_closing_marker() -> None:
    content = b"MARGINALPDBC;\n2026;06;01;1;100;100;\n"

    with pytest.raises(
        ValueError,
        match="no closing marker",
    ):
        validate_downloaded_omie_content(
            content=content,
            filename="marginalpdbc_20260601.1",
        )
