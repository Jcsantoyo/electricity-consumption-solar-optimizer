from solar import simulate_self_consumption
from battery import simulate_battery


def compare_battery_scenario(
    consumption_kwh: list[float],
    solar_generation_kwh: list[float],
    battery_capacity_kwh: float,
    battery_efficiency: float = 0.90,
    max_charge_power_kw: float | None = None,
    max_discharge_power_kw: float | None = None,
    initial_battery_state_kwh: float = 0.0,
) -> dict[str, float]:

    self_consumed_no_battery, grid_import_no_battery, solar_surplus_no_battery = (
        simulate_self_consumption(consumption_kwh, solar_generation_kwh)
    )

    battery_results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh,
        battery_efficiency=battery_efficiency,
        max_charge_power_kw=max_charge_power_kw,
        max_discharge_power_kw=max_discharge_power_kw,
        initial_battery_state_kwh=initial_battery_state_kwh,
    )

    total_consumption = sum(consumption_kwh)
    total_solar_generation = sum(solar_generation_kwh)

    total_grid_import_no_battery = sum(grid_import_no_battery)
    total_grid_import_with_battery = sum(battery_results["grid_import_kwh"])

    total_solar_surplus_no_battery = sum(solar_surplus_no_battery)
    total_solar_surplus_with_battery = sum(battery_results["solar_surplus_kwh"])

    grid_import_reduction = (
        total_grid_import_no_battery - total_grid_import_with_battery
    )

    solar_surplus_reduction = (
        total_solar_surplus_no_battery - total_solar_surplus_with_battery
    )

    if total_consumption > 0:
        self_sufficiency_no_battery = 1 - (
            total_grid_import_no_battery / total_consumption
        )
        self_sufficiency_with_battery = 1 - (
            total_grid_import_with_battery / total_consumption
        )
    else:
        self_sufficiency_no_battery = 0
        self_sufficiency_with_battery = 0

    return {
        "total_consumption_kwh": total_consumption,
        "total_solar_generation_kwh": total_solar_generation,
        "grid_import_no_battery_kwh": total_grid_import_no_battery,
        "grid_import_with_battery_kwh": total_grid_import_with_battery,
        "solar_surplus_no_battery_kwh": total_solar_surplus_no_battery,
        "solar_surplus_with_battery_kwh": total_solar_surplus_with_battery,
        "grid_import_reduction_kwh": grid_import_reduction,
        "solar_surplus_reduction_kwh": solar_surplus_reduction,
        "self_sufficiency_no_battery": self_sufficiency_no_battery,
        "self_sufficiency_with_battery": self_sufficiency_with_battery,
        "self_sufficiency_improvement": (
            self_sufficiency_with_battery - self_sufficiency_no_battery
        ),
    }
