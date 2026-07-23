from dataclasses import dataclass


@dataclass(frozen=True)
class AnnualCashFlow:
    year: int
    energy_savings_eur: float
    operating_cost_eur: float
    replacement_cost_eur: float
    investment_cost_eur: float
    net_cash_flow_eur: float

    def __post_init__(self) -> None:
        if self.year < 0:
            raise ValueError("Cash flow year cannot be negative")

        non_negative_costs = {
            "Operating cost": self.operating_cost_eur,
            "Replacement cost": self.replacement_cost_eur,
            "Investment cost": self.investment_cost_eur,
        }

        for field_name, value in non_negative_costs.items():
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")

        expected_net_cash_flow = (
            self.energy_savings_eur
            - self.operating_cost_eur
            - self.replacement_cost_eur
            - self.investment_cost_eur
        )

        if abs(self.net_cash_flow_eur - expected_net_cash_flow) > 1e-9:
            raise ValueError("Net cash flow does not match its component values")


@dataclass(frozen=True)
class ReplacementCost:
    year: int
    cost_eur: float

    def __post_init__(self) -> None:
        if self.year <= 0:
            raise ValueError("Replacement year must be greater than zero")

        if self.cost_eur < 0:
            raise ValueError("Replacement cost cannot be negative")


def build_annual_cash_flows(
    initial_investment_cost_eur: float,
    annual_energy_savings_eur: float,
    project_lifetime_years: int,
    annual_operating_cost_eur: float = 0.0,
) -> list[AnnualCashFlow]:
    if initial_investment_cost_eur < 0:
        raise ValueError("Initial investment cost cannto be negative")

    if project_lifetime_years <= 0:
        raise ValueError("Project lifetime must be greater than zero")

    if annual_operating_cost_eur < 0:
        raise ValueError("Annual operating cost cannot be negative")

    cash_flows = [
        AnnualCashFlow(
            year=0,
            energy_savings_eur=0.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=initial_investment_cost_eur,
            net_cash_flow_eur=-initial_investment_cost_eur,
        )
    ]

    annual_net_cash_flow = annual_energy_savings_eur - annual_operating_cost_eur

    for year in range(1, project_lifetime_years + 1):
        cash_flows.append(
            AnnualCashFlow(
                year=year,
                energy_savings_eur=annual_energy_savings_eur,
                operating_cost_eur=annual_operating_cost_eur,
                replacement_cost_eur=0.0,
                investment_cost_eur=0.0,
                net_cash_flow_eur=annual_net_cash_flow,
            )
        )

    return cash_flows


def build_projected_annual_cash_flows(
    initial_investment_cost_eur: float,
    first_year_energy_savings_eur: float,
    project_lifetime_years: int,
    annual_operating_cost_eur: float = 0.0,
    annual_solar_degradation_rate: float = 0.0,
    annual_electricity_price_growth_rate: float = 0.0,
    annual_operating_cost_growth_rate: float = 0.0,
    replacement_costs: list[ReplacementCost] | None = None,
) -> list[AnnualCashFlow]:
    if initial_investment_cost_eur < 0:
        raise ValueError("Initial investment cost cannot be negative")

    if project_lifetime_years <= 0:
        raise ValueError("Project lifetime must be greater than zero")

    if annual_operating_cost_eur < 0:
        raise ValueError("Annual operating cost cannot be negative")

    rates = {
        "Solar degradation rate": annual_solar_degradation_rate,
        "Electricity price growth rate": annual_electricity_price_growth_rate,
        "Operating cost growth rate": annual_operating_cost_growth_rate,
    }

    for rate_name, rate_value in rates.items():
        if rate_value <= -1:
            raise ValueError(f"{rate_name} must be greater than -1")

    replacement_cost_by_year: dict[int, float] = {}

    for replacement in replacement_costs or []:
        if replacement.year > project_lifetime_years:
            raise ValueError("Replacement year cannot exceed project lifetime")

        replacement_cost_by_year[replacement.year] = (
            replacement_cost_by_year.get(replacement.year, 0.0) + replacement.cost_eur
        )

    cash_flows = [
        AnnualCashFlow(
            year=0,
            energy_savings_eur=0.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=initial_investment_cost_eur,
            net_cash_flow_eur=-initial_investment_cost_eur,
        )
    ]

    for year in range(1, project_lifetime_years + 1):
        elapsed_years = year - 1

        degradation_factor = (1 - annual_solar_degradation_rate) ** elapsed_years

        price_growth_factor = (
            1 + annual_electricity_price_growth_rate
        ) ** elapsed_years

        operating_cost_growth_factor = (
            1 + annual_operating_cost_growth_rate
        ) ** elapsed_years

        energy_savings = (
            first_year_energy_savings_eur * degradation_factor * price_growth_factor
        )

        operating_cost = annual_operating_cost_eur * operating_cost_growth_factor

        replacement_cost = replacement_cost_by_year.get(year, 0.0)

        net_cash_flow = energy_savings - operating_cost - replacement_cost

        cash_flows.append(
            AnnualCashFlow(
                year=year,
                energy_savings_eur=energy_savings,
                operating_cost_eur=operating_cost,
                replacement_cost_eur=replacement_cost,
                investment_cost_eur=0.0,
                net_cash_flow_eur=net_cash_flow,
            )
        )

    return cash_flows
