import pandas as pd
import pytest

from scripts.generate_price_mode_comparison import (
    build_price_mode_comparison_markdown,
    load_energy_data,
)


def test_load_energy_data_reads_required_columns(
    tmp_path,
) -> None:
    input_path = tmp_path / "energy.csv"

    pd.DataFrame(
        {
            "datetime": [
                "2026-06-01 00:00:00",
            ],
            "grid_import_kwh": [
                1.5,
            ],
            "solar_generation_kwh": [
                0.0,
            ],
        }
    ).to_csv(
        input_path,
        index=False,
    )

    energy_df = load_energy_data(str(input_path))

    assert energy_df.columns.tolist() == [
        "datetime",
        "grid_import_kwh",
    ]

    assert energy_df.iloc[0]["grid_import_kwh"] == pytest.approx(1.5)


def test_load_energy_data_raises_error_for_missing_column(
    tmp_path,
) -> None:
    input_path = tmp_path / "energy.csv"

    pd.DataFrame(
        {
            "datetime": [
                "2026-06-01 00:00:00",
            ],
        }
    ).to_csv(
        input_path,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="Missing required energy columns",
    ):
        load_energy_data(str(input_path))


def test_build_price_mode_comparison_markdown() -> None:
    comparison_df = pd.DataFrame(
        {
            "price_mode": [
                "flat_fixed",
                "spanish_2_0td",
                "hourly",
            ],
            "variable_grid_cost_eur": [
                100.0,
                90.0,
                70.0,
            ],
            "difference_vs_flat_eur": [
                0.0,
                -10.0,
                -30.0,
            ],
            "difference_vs_2_0td_eur": [
                10.0,
                0.0,
                -20.0,
            ],
        }
    )

    markdown = build_price_mode_comparison_markdown(
        comparison_df=comparison_df,
        fixed_price_eur_per_kwh=0.20,
        energy_data_path=("reports/best_scenario_timeseries.csv"),
        hourly_price_data_path=("data/processed/omie_hourly_prices.csv"),
    )

    assert "# Electricity Price Mode Comparison" in markdown
    assert "| flat_fixed | 100.00 EUR" in markdown
    assert "| spanish_2_0td | 90.00 EUR" in markdown
    assert "| hourly | 70.00 EUR" in markdown
    assert "The lowest variable grid-import cost" in markdown
    assert "`hourly`" in markdown
    assert "wholesale market prices" in markdown
