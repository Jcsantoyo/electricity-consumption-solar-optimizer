def simulate_battery(
    consumption_kwh: list[float],
    solar_generation_kwh: list[float],
    battery_capacity_kwh: float,
    battery_efficiency = 0.90,
    max_charge_power_kw: float | None = None,
    max_discharge_power_kw: float | None = None,
    initial_battery_state_kwh = 0.0

) -> dict[str, list[float]]:
    
    battery_state = min(initial_battery_state_kwh, battery_capacity_kwh)

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

        if max_charge_power_kw is None:
            charge_power_limit = initial_solar_surplus
        else:
            charge_power_limit = max_charge_power_kw

        raw_battery_charge = min(charge_power_limit, avalaible_capacity / battery_efficiency, initial_solar_surplus)

        effective_battery_charge = raw_battery_charge * battery_efficiency

        battery_state = battery_state + effective_battery_charge

        if max_discharge_power_kw is None:
            discharge_power_limit = remaining_consumption
        else:
            discharge_power_limit = max_discharge_power_kw

        battery_discharge = min(remaining_consumption, battery_state, discharge_power_limit)

        battery_state = battery_state - battery_discharge

        grid_import = remaining_consumption - battery_discharge
        final_solar_surplus = initial_solar_surplus - raw_battery_charge

        self_consumed_kwh.append(self_consumed)
        battery_charge_kwh.append(raw_battery_charge)
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