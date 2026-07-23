import pytest

from financial_assumptions import (
    FinancialAssumptions,
)


def test_financial_assumptions_stores_values() -> None:
    assumptions = FinancialAssumptions(
        project_lifetime_years=25,
        discount_rate=0.05,
        annual_operating_cost_eur=100.0,
        annual_solar_degradation_rate=0.005,
        annual_electricity_price_growth_rate=0.02,
        annual_operating_cost_growth_rate=0.02,
    )

    assert assumptions.project_lifetime_years == 25
    assert assumptions.discount_rate == pytest.approx(0.05)
    assert assumptions.annual_operating_cost_eur == (pytest.approx(100.0))
    assert assumptions.annual_solar_degradation_rate == pytest.approx(0.005)


@pytest.mark.parametrize(
    (
        "project_lifetime_years",
        "discount_rate",
        "annual_operating_cost_eur",
        "solar_degradation_rate",
        "electricity_price_growth_rate",
        "operating_cost_growth_rate",
    ),
    [
        (0, 0.05, 100.0, 0.005, 0.02, 0.02),
        (-1, 0.05, 100.0, 0.005, 0.02, 0.02),
        (25, -0.01, 100.0, 0.005, 0.02, 0.02),
        (25, 0.05, -1.0, 0.005, 0.02, 0.02),
        (25, 0.05, 100.0, -1.0, 0.02, 0.02),
        (25, 0.05, 100.0, 0.005, -1.0, 0.02),
        (25, 0.05, 100.0, 0.005, 0.02, -1.0),
    ],
)
def test_financial_assumptions_rejects_invalid_values(
    project_lifetime_years: int,
    discount_rate: float,
    annual_operating_cost_eur: float,
    solar_degradation_rate: float,
    electricity_price_growth_rate: float,
    operating_cost_growth_rate: float,
) -> None:
    with pytest.raises(ValueError):
        FinancialAssumptions(
            project_lifetime_years=(project_lifetime_years),
            discount_rate=discount_rate,
            annual_operating_cost_eur=(annual_operating_cost_eur),
            annual_solar_degradation_rate=(solar_degradation_rate),
            annual_electricity_price_growth_rate=(electricity_price_growth_rate),
            annual_operating_cost_growth_rate=(operating_cost_growth_rate),
        )
