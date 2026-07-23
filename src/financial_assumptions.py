from dataclasses import dataclass


@dataclass(frozen=True)
class FinancialAssumptions:
    project_lifetime_years: int
    discount_rate: float
    annual_operating_cost_eur: float
    annual_solar_degradation_rate: float
    annual_electricity_price_growth_rate: float
    annual_operating_cost_growth_rate: float

    def __post_init__(self) -> None:
        if self.project_lifetime_years <= 0:
            raise ValueError("Project lifetime must be greater than zero")

        if self.discount_rate < 0:
            raise ValueError("Discount rate cannot be negative")

        if self.annual_operating_cost_eur < 0:
            raise ValueError("Annual operating cost cannot be negative")

        rates = {
            "Solar degradation rate": self.annual_solar_degradation_rate,
            "Electricity price growth rate": self.annual_electricity_price_growth_rate,
            "Operating cost growth rate": self.annual_operating_cost_growth_rate,
        }

        for rate_name, rate_value in rates.items():
            if rate_value <= -1:
                raise ValueError(f"{rate_name} must be greater than -1")
