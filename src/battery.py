def simulate_battery(
        consumption_kwh: list[float],
        solar_generation_kwh: list[float],
        battery_capacity_kwh: float
) -> dict[str, list[float]]:
    
    battery_state = 0.0

    self_consumed_kwh = []
    battery_charge_kwh = []
    battery_discharge_kwh = []
    grid_import_kwh = []
    solar_surplus_kwh = []
    battery_state_kwh = []

    for hour, consumption in enumerate(consumption_kwh):
        solar_generation = solar_generation_kwh[hour]

        self_consumed = min(consumption, solar_generation)

        remaining_consumption = consumption - self_consumed
        initial_solar_surplus = solar_generation - self_consumed

        avalaible_capacity = battery_capacity_kwh - battery_state
        battery_charge = min(initial_solar_surplus, avalaible_capacity)

        battery_state = battery_state + battery_charge

        battery_discharge = min(remaining_consumption, battery_state)

        battery_state = battery_state - battery_discharge

        grid_import = remaining_consumption - battery_discharge
        final_solar_surplus = initial_solar_surplus - battery_charge

        self_consumed_kwh.append(self_consumed)
        battery_charge_kwh.append(battery_charge)
        battery_discharge_kwh.append(battery_discharge)
        grid_import_kwh.append(grid_import)
        solar_surplus_kwh.append(final_solar_surplus)
        battery_state_kwh.append(battery_state)

    return {
        "self_consumed_kwh": self_consumed_kwh,
        "battery_charge_kwh": battery_charge_kwh,
        "battery_discharge_kwh": battery_discharge_kwh,
        "grid_import_kwh": grid_import_kwh,
        "solar_surplus_kwh": solar_surplus_kwh,
        "battery_state_kwh": battery_state_kwh
    }