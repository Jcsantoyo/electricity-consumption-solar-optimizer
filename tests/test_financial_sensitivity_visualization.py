from pathlib import Path

import pandas as pd
import pytest

from visualization import (
    plot_financial_sensitivity_irr,
    plot_financial_sensitivity_metric,
    plot_financial_sensitivity_npv,
    plot_financial_sensitivity_payback,
)


def build_sensitivity_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "case_name": [
                "pessimistic",
                "base",
                "optimistic",
            ],
            "net_present_value_eur": [
                -2500.0,
                -850.0,
                2100.0,
            ],
            "discounted_payback_years": [
                None,
                None,
                16.5,
            ],
            "internal_rate_of_return": [
                None,
                0.025,
                0.069,
            ],
        }
    )


@pytest.mark.parametrize(
    (
        "plot_function",
        "filename",
    ),
    [
        (
            plot_financial_sensitivity_npv,
            "npv.png",
        ),
        (
            plot_financial_sensitivity_payback,
            "payback.png",
        ),
        (
            plot_financial_sensitivity_irr,
            "irr.png",
        ),
    ],
)
def test_financial_sensitivity_plot_creates_file(
    tmp_path: Path,
    plot_function,
    filename: str,
) -> None:
    output_path = tmp_path / "nested" / filename

    created = plot_function(
        sensitivity_df=build_sensitivity_dataframe(),
        output_path=str(output_path),
    )

    assert created is True
    assert output_path.is_file()
    assert output_path.stat().st_size > 0


def test_payback_plot_ignores_missing_values(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "payback.png"

    created = plot_financial_sensitivity_payback(
        sensitivity_df=build_sensitivity_dataframe(),
        output_path=str(output_path),
    )

    assert created is True
    assert output_path.is_file()


def test_plot_returns_false_when_all_metric_values_are_missing(
    tmp_path: Path,
) -> None:
    dataframe = pd.DataFrame(
        {
            "case_name": [
                "pessimistic",
                "base",
                "optimistic",
            ],
            "discounted_payback_years": [
                None,
                None,
                None,
            ],
        }
    )

    output_path = tmp_path / "payback.png"

    created = plot_financial_sensitivity_payback(
        sensitivity_df=dataframe,
        output_path=str(output_path),
    )

    assert created is False
    assert not output_path.exists()


def test_plot_rejects_missing_required_columns(
    tmp_path: Path,
) -> None:
    dataframe = pd.DataFrame(
        {
            "case_name": ["base"],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing required financial sensitivity columns",
    ):
        plot_financial_sensitivity_metric(
            sensitivity_df=dataframe,
            metric_column="net_present_value_eur",
            title="NPV",
            axis_label="EUR",
            output_path=str(tmp_path / "npv.png"),
        )
