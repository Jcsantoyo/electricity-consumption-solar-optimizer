def calculate_solar_installation_cost(
    solar_peak_power_kw: float, cost_per_kw: float
) -> float:
    return solar_peak_power_kw * cost_per_kw


def calculate_battery_installation_cost(
    battery_capacity_kwh: float, cost_per_kwh: float
) -> float:
    return battery_capacity_kwh * cost_per_kwh


def calculate_total_installation_cost(
    solar_peak_power_kw: float,
    battery_capacity_kwh: float,
    solar_cost_per_kw: float,
    battery_cost_per_kwh: float,
    fixed_installation_cost: float = 0.0,
) -> float:
    battery_cost = calculate_battery_installation_cost(
        battery_capacity_kwh, battery_cost_per_kwh
    )

    solar_cost = calculate_solar_installation_cost(
        solar_peak_power_kw, solar_cost_per_kw
    )

    return solar_cost + battery_cost + fixed_installation_cost


def calculate_grid_cost(
    grid_import_kwh: float, electricity_price_eur_per_kwh: float
) -> float:
    return grid_import_kwh * electricity_price_eur_per_kwh


def calculate_simple_payback_years(
    investment_cost_eur: float, annual_savings_eur: float
) -> float | None:
    if annual_savings_eur <= 0:
        return None

    return investment_cost_eur / annual_savings_eur


def calculate_net_cost(
    grid_import_kwh: float,
    solar_surplus_kwh: float,
    electricity_price_eur_per_kwh: float,
    surplus_compensation_eur_per_kwh: float,
) -> float:
    grid_cost = grid_import_kwh * electricity_price_eur_per_kwh
    surplus_compensation = solar_surplus_kwh * surplus_compensation_eur_per_kwh

    net_cost = grid_cost - surplus_compensation

    return max(net_cost, 0.0)
