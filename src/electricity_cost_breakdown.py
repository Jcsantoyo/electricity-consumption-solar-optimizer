from dataclasses import dataclass


@dataclass(frozen=True)
class ElectricityCostBreakdown:
    variable_energy_cost_eur: float
    fixed_power_cost_eur: float
    surplus_compensation_eur: float
    total_cost_eur: float

    def __post_init__(self) -> None:
        non_negative_fields = {
            "Fixed power cost": (self.fixed_power_cost_eur),
            "Surplus compensation": (self.surplus_compensation_eur),
            "Total electricity cost": (self.total_cost_eur),
        }

        for field_name, value in non_negative_fields.items():
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")

        expected_total = max(
            self.variable_energy_cost_eur
            + self.fixed_power_cost_eur
            - self.surplus_compensation_eur,
            0.0,
        )

        if abs(self.total_cost_eur - expected_total) > 1e-9:
            raise ValueError(
                "Total electricity cost does not match its component values"
            )
