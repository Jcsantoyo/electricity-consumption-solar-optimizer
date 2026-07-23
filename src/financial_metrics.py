from dataclasses import dataclass

from collections.abc import Sequence

from financial_cash_flow import AnnualCashFlow


@dataclass(frozen=True)
class FinancialMetricsResult:
    net_present_value_eur: float
    discounted_payback_years: float | None
    internal_rate_of_return: float | None


def validate_cash_flows(cash_flows: Sequence[AnnualCashFlow]) -> None:
    if not cash_flows:
        raise ValueError("Cash flow sequence cannot be empty")

    expected_years = list(range(len(cash_flows)))

    actual_years = [cash_flow.year for cash_flow in cash_flows]

    if actual_years != expected_years:
        raise ValueError("Cash flow years must start at zero and be consecutive")


def validate_discount_rate(discount_rate: float) -> None:
    if discount_rate < 0:
        raise ValueError("Discount rate cannot be negative")


def calculate_discounted_cash_flow(
    cash_flow: AnnualCashFlow, discount_rate: float
) -> float:
    validate_discount_rate(discount_rate)

    discount_factor = (1 + discount_rate) ** cash_flow.year

    return cash_flow.net_cash_flow_eur / discount_factor


def calculate_net_present_value(
    cash_flows: Sequence[AnnualCashFlow], discount_rate: float
) -> float:
    validate_cash_flows(cash_flows)
    validate_discount_rate(discount_rate)

    return sum(
        calculate_discounted_cash_flow(cash_flow=cash_flow, discount_rate=discount_rate)
        for cash_flow in cash_flows
    )


def calculate_discounted_payback_years(
    cash_flows: Sequence[AnnualCashFlow], discount_rate: float
) -> float | None:
    validate_cash_flows(cash_flows)
    validate_discount_rate(discount_rate)

    cumulative_cash_flow = 0.0

    for cash_flow in cash_flows:
        discounted_cash_flow = calculate_discounted_cash_flow(cash_flow, discount_rate)

        previous_cumulative_cash_flow = cumulative_cash_flow

        cumulative_cash_flow += discounted_cash_flow

        if cumulative_cash_flow >= 0:
            if cash_flow.year == 0:
                return 0.0

            if discounted_cash_flow <= 0:
                return float(cash_flow.year)

            unrecovered_amount = -previous_cumulative_cash_flow

            fraction_of_year = unrecovered_amount / discounted_cash_flow

            return cash_flow.year - 1 + fraction_of_year

    return None


def _calculate_net_present_value_for_rate(
    cash_flows: Sequence[AnnualCashFlow], rate: bool
) -> float:
    if rate <= -1:
        raise ValueError("Rate must be greater than -1")

    return sum(
        cash_flow.net_cash_flow_eur / ((1 + rate) ** cash_flow.year)
        for cash_flow in cash_flows
    )


def _count_cash_flow_sign_changes(cash_flows: Sequence[AnnualCashFlow]) -> int:
    non_zero_cash_flows = [
        cash_flow.net_cash_flow_eur
        for cash_flow in cash_flows
        if cash_flow.net_cash_flow_eur != 0
    ]

    return sum(
        current_value * next_value < 0
        for current_value, next_value in zip(
            non_zero_cash_flows, non_zero_cash_flows[1:], strict=False
        )
    )


def calculate_internal_rate_of_return(
    cash_flows: Sequence[AnnualCashFlow],
    tolerance: float = 1e-7,
    max_iterations: int = 200,
    minimum_rate: float = -0.9999,
    maximum_rate: float = 10.0,
) -> float | None:
    validate_cash_flows(cash_flows)

    if tolerance <= 0:
        raise ValueError("IRR tolerance must be greater than zero")

    if max_iterations <= 0:
        raise ValueError("Maximum IRR iteration must be greater than zero")

    if minimum_rate <= -1:
        raise ValueError("Minimum IRR rate must be greater than -1")

    if maximum_rate <= minimum_rate:
        raise ValueError("Maximum IRR rate must be greater than minimum IRR rate")

    sign_changes = _count_cash_flow_sign_changes(cash_flows)

    if sign_changes != 1:
        return None

    lower_rate = minimum_rate
    upper_rate = maximum_rate

    lower_npv = _calculate_net_present_value_for_rate(cash_flows, lower_rate)

    upper_npv = _calculate_net_present_value_for_rate(cash_flows, upper_rate)

    if abs(lower_npv) <= tolerance:
        return lower_rate

    if abs(upper_npv) <= tolerance:
        return upper_rate

    if lower_npv * upper_npv > 0:
        return None

    for _ in range(max_iterations):
        middle_rate = (lower_rate + upper_rate) / 2

        middle_npv = _calculate_net_present_value_for_rate(cash_flows, middle_rate)

        if abs(middle_npv) <= tolerance:
            return middle_rate

        if lower_npv * middle_npv < 0:
            upper_rate = middle_rate
        else:
            lower_rate = middle_rate
            lower_npv = middle_npv

    return (lower_rate + upper_rate) / 2


def calculate_financial_metrics(
    cash_flows: Sequence[AnnualCashFlow], discount_rate: float
) -> FinancialMetricsResult:
    return FinancialMetricsResult(
        calculate_net_present_value(cash_flows, discount_rate),
        calculate_discounted_payback_years(cash_flows, discount_rate),
        calculate_internal_rate_of_return(cash_flows),
    )
