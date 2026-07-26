from collections.abc import Sequence
from dataclasses import dataclass, asdict

from financial_assumptions import FinancialAssumptions
from financial_cash_flow import ReplacementCost, build_projected_annual_cash_flows
from financial_metrics import FinancialMetricsResult, calculate_financial_metrics

import pandas as pd


@dataclass(frozen=True)
class FinancialSensitivityCase:
    name: str
    assumptions: FinancialAssumptions

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Sensitivity case name cannot be empty")


@dataclass(frozen=True)
class FinancialSensitivityResult:
    case_name: str
    project_lifetime_years: int
    discount_rate: float
    annual_operating_cost_eur: float
    annual_solar_degradation_rate: float
    annual_electricity_price_growth_rate: float
    annual_operating_cost_growth_rate: float
    battery_replacement_year: int | None
    battery_replacement_cost_fraction: float
    battery_replacement_cost_eur: float
    net_present_value_eur: float
    discounted_payback_years: float | None
    internal_rate_of_return: float | None


def calculate_battery_replacement_cost(
    battery_capacity_kwh: float,
    battery_cost_per_kwh: float,
    replacement_cost_fraction: float,
) -> float:
    if battery_capacity_kwh < 0:
        raise ValueError("Battery capacity cannot be negative")

    if battery_cost_per_kwh < 0:
        raise ValueError("Battery cost per kwh cannot be negative")

    if replacement_cost_fraction < 0:
        raise ValueError("Battery replacement cost fraction cannot be negative")

    return battery_capacity_kwh * battery_cost_per_kwh * replacement_cost_fraction


def build_sensitivity_replacement_costs(
    battery_capacity_kwh: float,
    battery_cost_per_kwh: float,
    assumptions: FinancialAssumptions,
) -> tuple[list[ReplacementCost], float]:
    if battery_capacity_kwh < 0:
        raise ValueError("Battery capacity cannot be negative")

    if battery_cost_per_kwh < 0:
        raise ValueError("Battery cost per kWh cannot be negative")

    replacement_year = assumptions.battery_replacement_year

    if replacement_year is None or battery_capacity_kwh == 0:
        return [], 0.0

    replacement_cost_eur = calculate_battery_replacement_cost(
        battery_capacity_kwh=battery_capacity_kwh,
        battery_cost_per_kwh=battery_cost_per_kwh,
        replacement_cost_fraction=(assumptions.battery_replacement_cost_fraction),
    )

    return (
        [
            ReplacementCost(
                year=replacement_year,
                cost_eur=replacement_cost_eur,
            )
        ],
        replacement_cost_eur,
    )


def evaluate_financial_sensitivity_case(
    initial_investment_cost_eur: float,
    first_year_energy_savings_eur: float,
    battery_capacity_kwh: float,
    battery_cost_per_kwh: float,
    case: FinancialSensitivityCase,
) -> FinancialSensitivityResult:
    if initial_investment_cost_eur < 0:
        raise ValueError("Initial investment cost cannot be negative")

    assumptions = case.assumptions

    replacement_costs, replacement_cost_eur = build_sensitivity_replacement_costs(
        battery_capacity_kwh, battery_cost_per_kwh, assumptions
    )

    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur,
        first_year_energy_savings_eur,
        assumptions.project_lifetime_years,
        assumptions.annual_operating_cost_eur,
        assumptions.annual_solar_degradation_rate,
        assumptions.annual_electricity_price_growth_rate,
        assumptions.annual_operating_cost_growth_rate,
        replacement_costs,
    )

    metrics: FinancialMetricsResult = calculate_financial_metrics(
        cash_flows, assumptions.discount_rate
    )

    return FinancialSensitivityResult(
        case.name,
        assumptions.project_lifetime_years,
        assumptions.discount_rate,
        assumptions.annual_operating_cost_eur,
        assumptions.annual_solar_degradation_rate,
        assumptions.annual_electricity_price_growth_rate,
        assumptions.annual_operating_cost_growth_rate,
        assumptions.battery_replacement_year,
        assumptions.battery_replacement_cost_fraction,
        replacement_cost_eur,
        metrics.net_present_value_eur,
        metrics.discounted_payback_years,
        metrics.internal_rate_of_return,
    )


def run_financial_sensitivity_analysis(
    initial_investment_cost_eur: float,
    first_year_energy_savings_eur: float,
    battery_capacity_kwh: float,
    battery_cost_per_kwh: float,
    cases: Sequence[FinancialSensitivityCase],
) -> list[FinancialSensitivityResult]:
    if not cases:
        raise ValueError("Financial sensitivity analysis requires at least one case")

    case_names = [case.name for case in cases]

    if len(case_names) != len(set(case_names)):
        raise ValueError("Sensitivity case names must be unique")

    return [
        evaluate_financial_sensitivity_case(
            initial_investment_cost_eur=initial_investment_cost_eur,
            first_year_energy_savings_eur=first_year_energy_savings_eur,
            battery_capacity_kwh=battery_capacity_kwh,
            battery_cost_per_kwh=battery_cost_per_kwh,
            case=case,
        )
        for case in cases
    ]


FINANCIAL_SENSITIVITY_COLUMNS = [
    "case_name",
    "project_lifetime_years",
    "discount_rate",
    "annual_operating_cost_eur",
    "annual_solar_degradation_rate",
    "annual_electricity_price_growth_rate",
    "annual_operating_cost_growth_rate",
    "battery_replacement_year",
    "battery_replacement_cost_fraction",
    "battery_replacement_cost_eur",
    "net_present_value_eur",
    "discounted_payback_years",
    "internal_rate_of_return",
]


def financial_sensitivity_results_to_dataframe(
    results: Sequence[FinancialSensitivityResult],
) -> pd.DataFrame:
    rows = [asdict(result) for result in results]

    return pd.DataFrame(
        rows,
        columns=FINANCIAL_SENSITIVITY_COLUMNS,
    )
