import pytest

from financial_cash_flow import (
    AnnualCashFlow,
    build_annual_cash_flows,
)
from financial_metrics import (
    FinancialMetricsResult,
    calculate_discounted_cash_flow,
    calculate_discounted_payback_years,
    calculate_financial_metrics,
    calculate_internal_rate_of_return,
    calculate_net_present_value,
    validate_cash_flows,
    validate_discount_rate,
)


def test_calculate_discounted_cash_flow_for_year_zero() -> None:
    cash_flow = AnnualCashFlow(
        year=0,
        energy_savings_eur=0.0,
        operating_cost_eur=0.0,
        replacement_cost_eur=0.0,
        investment_cost_eur=1000.0,
        net_cash_flow_eur=-1000.0,
    )

    result = calculate_discounted_cash_flow(
        cash_flow=cash_flow,
        discount_rate=0.10,
    )

    assert result == pytest.approx(-1000.0)


def test_calculate_discounted_cash_flow_for_future_year() -> None:
    cash_flow = AnnualCashFlow(
        year=2,
        energy_savings_eur=400.0,
        operating_cost_eur=0.0,
        replacement_cost_eur=0.0,
        investment_cost_eur=0.0,
        net_cash_flow_eur=400.0,
    )

    result = calculate_discounted_cash_flow(
        cash_flow=cash_flow,
        discount_rate=0.10,
    )

    assert result == pytest.approx(400.0 / (1.10**2))


def test_calculate_net_present_value() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=400.0,
        project_lifetime_years=3,
    )

    result = calculate_net_present_value(
        cash_flows=cash_flows,
        discount_rate=0.10,
    )

    expected_result = -1000.0 + 400.0 / 1.10 + 400.0 / (1.10**2) + 400.0 / (1.10**3)

    assert result == pytest.approx(expected_result)


def test_net_present_value_with_zero_discount_rate() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=400.0,
        project_lifetime_years=3,
    )

    result = calculate_net_present_value(
        cash_flows=cash_flows,
        discount_rate=0.0,
    )

    assert result == pytest.approx(200.0)


def test_discounted_payback_with_zero_discount_rate() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=400.0,
        project_lifetime_years=3,
    )

    payback = calculate_discounted_payback_years(
        cash_flows=cash_flows,
        discount_rate=0.0,
    )

    assert payback == pytest.approx(2.5)


def test_discounted_payback_accounts_for_discounting() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=400.0,
        project_lifetime_years=4,
    )

    payback = calculate_discounted_payback_years(
        cash_flows=cash_flows,
        discount_rate=0.10,
    )

    discounted_year_1 = 400.0 / 1.10
    discounted_year_2 = 400.0 / (1.10**2)
    discounted_year_3 = 400.0 / (1.10**3)
    discounted_year_4 = 400.0 / (1.10**4)

    unrecovered_after_year_3 = (
        1000.0 - discounted_year_1 - discounted_year_2 - discounted_year_3
    )

    expected_payback = 3 + unrecovered_after_year_3 / discounted_year_4

    assert payback == pytest.approx(expected_payback)

    assert payback > 2.5


def test_discounted_payback_returns_none_when_not_recovered() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        annual_energy_savings_eur=100.0,
        project_lifetime_years=10,
    )

    payback = calculate_discounted_payback_years(
        cash_flows=cash_flows,
        discount_rate=0.05,
    )

    assert payback is None


def test_discounted_payback_returns_zero_for_zero_investment() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=0.0,
        annual_energy_savings_eur=100.0,
        project_lifetime_years=1,
    )

    payback = calculate_discounted_payback_years(
        cash_flows=cash_flows,
        discount_rate=0.05,
    )

    assert payback == pytest.approx(0.0)


@pytest.mark.parametrize(
    "discount_rate",
    [
        -0.01,
        -0.50,
    ],
)
def test_validate_discount_rate_rejects_negative_values(
    discount_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        validate_discount_rate(discount_rate)


def test_validate_cash_flows_rejects_empty_sequence() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        validate_cash_flows([])


def test_validate_cash_flows_rejects_non_consecutive_years() -> None:
    cash_flows = [
        AnnualCashFlow(
            year=0,
            energy_savings_eur=0.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=1000.0,
            net_cash_flow_eur=-1000.0,
        ),
        AnnualCashFlow(
            year=2,
            energy_savings_eur=400.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=0.0,
            net_cash_flow_eur=400.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="start at zero and be consecutive",
    ):
        validate_cash_flows(cash_flows)


def test_calculate_internal_rate_of_return() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=600.0,
        project_lifetime_years=2,
    )

    internal_rate_of_return = calculate_internal_rate_of_return(cash_flows)

    assert internal_rate_of_return == pytest.approx(
        0.130662386,
        abs=1e-6,
    )


def test_internal_rate_of_return_can_be_zero() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=500.0,
        project_lifetime_years=2,
    )

    internal_rate_of_return = calculate_internal_rate_of_return(cash_flows)

    assert internal_rate_of_return == pytest.approx(
        0.0,
        abs=1e-6,
    )


def test_internal_rate_of_return_returns_none_without_sign_change() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=0.0,
        annual_energy_savings_eur=500.0,
        project_lifetime_years=2,
    )

    internal_rate_of_return = calculate_internal_rate_of_return(cash_flows)

    assert internal_rate_of_return is None


def test_internal_rate_of_return_returns_none_for_multiple_sign_changes() -> None:
    cash_flows = [
        AnnualCashFlow(
            year=0,
            energy_savings_eur=0.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=1000.0,
            net_cash_flow_eur=-1000.0,
        ),
        AnnualCashFlow(
            year=1,
            energy_savings_eur=1500.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=0.0,
            net_cash_flow_eur=1500.0,
        ),
        AnnualCashFlow(
            year=2,
            energy_savings_eur=0.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=1000.0,
            investment_cost_eur=0.0,
            net_cash_flow_eur=-1000.0,
        ),
    ]

    internal_rate_of_return = calculate_internal_rate_of_return(cash_flows)

    assert internal_rate_of_return is None


@pytest.mark.parametrize(
    (
        "tolerance",
        "max_iterations",
        "minimum_rate",
        "maximum_rate",
    ),
    [
        (0.0, 200, -0.9999, 10.0),
        (-1e-7, 200, -0.9999, 10.0),
        (1e-7, 0, -0.9999, 10.0),
        (1e-7, -1, -0.9999, 10.0),
        (1e-7, 200, -1.0, 10.0),
        (1e-7, 200, 0.50, 0.50),
        (1e-7, 200, 1.0, 0.50),
    ],
)
def test_internal_rate_of_return_rejects_invalid_parameters(
    tolerance: float,
    max_iterations: int,
    minimum_rate: float,
    maximum_rate: float,
) -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=600.0,
        project_lifetime_years=2,
    )

    with pytest.raises(ValueError):
        calculate_internal_rate_of_return(
            cash_flows=cash_flows,
            tolerance=tolerance,
            max_iterations=max_iterations,
            minimum_rate=minimum_rate,
            maximum_rate=maximum_rate,
        )


def test_calculate_financial_metrics_returns_all_metrics() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=600.0,
        project_lifetime_years=2,
    )

    result = calculate_financial_metrics(
        cash_flows=cash_flows,
        discount_rate=0.05,
    )

    assert isinstance(
        result,
        FinancialMetricsResult,
    )

    assert result.net_present_value_eur == pytest.approx(
        calculate_net_present_value(
            cash_flows=cash_flows,
            discount_rate=0.05,
        )
    )

    assert result.discounted_payback_years == pytest.approx(
        calculate_discounted_payback_years(
            cash_flows=cash_flows,
            discount_rate=0.05,
        )
    )

    assert result.internal_rate_of_return == pytest.approx(
        0.130662386,
        abs=1e-6,
    )
