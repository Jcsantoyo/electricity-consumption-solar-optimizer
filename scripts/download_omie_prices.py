from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


DEFAULT_START_DATE = "2026-06-01"
DEFAULT_END_DATE = "2026-06-30"
DEFAULT_OUTPUT_DIRECTORY = "data/raw"

OMIE_DOWNLOAD_URL_TEMPLATE = (
    "https://www.omie.es/en/file-download"
    "?filename={filename}&parents=marginalpdbc"
)


def parse_date(date_text: str) -> date:
    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()
    except ValueError as error:
        raise ValueError(
            f"Invalid date: {date_text}. Expected format: YYYY-MM-DD"
        ) from error


def build_omie_filename(target_date: date) -> str:
    return (
        "marginalpdbc_"
        f"{target_date.strftime('%Y%m%d')}"
        ".1"
    )


def build_omie_download_url(target_date: date) -> str:
    filename = build_omie_filename(target_date)

    return OMIE_DOWNLOAD_URL_TEMPLATE.format(
        filename=filename,
    )


def generate_date_range(
    start_date: date,
    end_date: date,
) -> list[date]:
    if end_date < start_date:
        raise ValueError(
            "End date cannot be earlier than start date"
        )

    number_of_days = (end_date - start_date).days + 1

    return [
        start_date + timedelta(days=day_offset)
        for day_offset in range(number_of_days)
    ]


def validate_downloaded_omie_content(
    content: bytes,
    filename: str,
) -> None:
    decoded_content = content.decode(
        "utf-8",
        errors="replace",
    )

    if not decoded_content.startswith("MARGINALPDBC;"):
        raise ValueError(
            f"Downloaded file is not a valid OMIE price file: {filename}"
        )

    if not decoded_content.rstrip().endswith("*"):
        raise ValueError(
            f"Downloaded OMIE file has no closing marker: {filename}"
        )


def download_omie_file(
    target_date: date,
    output_directory: str,
    overwrite: bool = False,
) -> Path:
    output_path = Path(output_directory)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = build_omie_filename(target_date)
    destination = output_path / filename

    if destination.exists() and not overwrite:
        print(f"Skipping existing file: {filename}")
        return destination

    url = build_omie_download_url(target_date)

    try:
        with urlopen(url, timeout=30) as response:
            content = response.read()
    except HTTPError as error:
        raise RuntimeError(
            f"OMIE returned HTTP {error.code} for {filename}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Could not download {filename}: {error.reason}"
        ) from error

    validate_downloaded_omie_content(
        content=content,
        filename=filename,
    )

    destination.write_bytes(content)

    print(f"Downloaded: {filename}")

    return destination


def download_omie_date_range(
    start_date: str,
    end_date: str,
    output_directory: str = DEFAULT_OUTPUT_DIRECTORY,
    overwrite: bool = False,
) -> list[Path]:
    parsed_start_date = parse_date(start_date)
    parsed_end_date = parse_date(end_date)

    dates = generate_date_range(
        start_date=parsed_start_date,
        end_date=parsed_end_date,
    )

    downloaded_files = []

    for target_date in dates:
        downloaded_file = download_omie_file(
            target_date=target_date,
            output_directory=output_directory,
            overwrite=overwrite,
        )

        downloaded_files.append(downloaded_file)

    return downloaded_files


def main() -> None:
    downloaded_files = download_omie_date_range(
        start_date=DEFAULT_START_DATE,
        end_date=DEFAULT_END_DATE,
    )

    print()
    print("OMIE download completed successfully.")
    print(f"Files available: {len(downloaded_files)}")
    print(f"Output directory: {DEFAULT_OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()