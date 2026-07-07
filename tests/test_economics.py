from economics import (
    calculate_grid_cost,
    calculate_net_cost,
    calculate_total_installation_cost,
    calculate_simple_payback_years,
)


def test_calculate_grid_cost() -> None:
    cost = calculate_grid_cost(grid_import_kwh=10.0, electricity_price_eur_per_kwh=0.20)

    assert cost == 2.0


def test_calculate_net_cost_with_surplus_compensation() -> None:
    cost = calculate_net_cost(
        grid_import_kwh=10.0,
        solar_surplus_kwh=5.0,
        electricity_price_eur_per_kwh=0.20,
        surplus_compensation_eur_per_kwh=0.07,
    )

    assert cost == 1.65


def test_calculate_net_cost_never_negative() -> None:
    cost = calculate_net_cost(
        grid_import_kwh=1.0,
        solar_surplus_kwh=100.0,
        electricity_price_eur_per_kwh=0.20,
        surplus_compensation_eur_per_kwh=0.07,
    )

    assert cost == 0.0


def test_calculate_total_installation_cost() -> None:
    cost = calculate_total_installation_cost(
        solar_peak_power_kw=2.0,
        battery_capacity_kwh=5.0,
        solar_cost_per_kw=900.0,
        battery_cost_per_kwh=500.0,
        fixed_installation_cost=800.0,
    )

    assert cost == 5100.0


def test_calculate_simple_payback_years() -> None:
    payback = calculate_simple_payback_years(
        investment_cost_eur=2000.0, annual_savings_eur=400.0
    )

    assert payback == 5.0


def test_calculate_simple_payback_years_with_zero_savings() -> None:
    payback = calculate_simple_payback_years(
        investment_cost_eur=2000.0, annual_savings_eur=0.0
    )

    assert payback is None
