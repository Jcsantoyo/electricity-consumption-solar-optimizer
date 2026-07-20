import pytest

from electricity_cost_breakdown import (
    ElectricityCostBreakdown,
)


def test_electricity_cost_breakdown_stores_components() -> None:
    breakdown = ElectricityCostBreakdown(
        variable_energy_cost_eur=120.0,
        fixed_power_cost_eur=30.0,
        surplus_compensation_eur=20.0,
        total_cost_eur=130.0,
    )

    assert breakdown.variable_energy_cost_eur == 120.0
    assert breakdown.fixed_power_cost_eur == 30.0
    assert breakdown.surplus_compensation_eur == 20.0
    assert breakdown.total_cost_eur == 130.0


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("variable_energy_cost_eur", -1.0),
        ("fixed_power_cost_eur", -1.0),
        ("surplus_compensation_eur", -1.0),
        ("total_cost_eur", -1.0),
    ],
)
def test_electricity_cost_breakdown_rejects_negative_values(
    field_name: str,
    field_value: float,
) -> None:
    values = {
        "variable_energy_cost_eur": 10.0,
        "fixed_power_cost_eur": 5.0,
        "surplus_compensation_eur": 2.0,
        "total_cost_eur": 13.0,
    }

    values[field_name] = field_value

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        ElectricityCostBreakdown(**values)

def test_electricity_cost_breakdown_rejects_inconsistent_total() -> None:
    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        ElectricityCostBreakdown(
            variable_energy_cost_eur=100.0,
            fixed_power_cost_eur=20.0,
            surplus_compensation_eur=10.0,
            total_cost_eur=50.0,
        )