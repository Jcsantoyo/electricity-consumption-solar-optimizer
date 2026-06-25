def get_solar_generation_for_hour(hour: int, peak_power_kw: float) -> float:
    if hour < 7:
        return 0.0
    elif hour < 10:
        return peak_power_kw * 0.25
    elif hour < 13:
        return peak_power_kw * 0.70
    elif hour < 16:
        return peak_power_kw * 0.90
    elif hour < 19:
        return peak_power_kw * 0.35
    else:
        return 0.0
    
def generate_daily_solar_profile(peak_power: int) -> list[float]:
    daily_solar_generation_kwh = []

    for hour in range(24):
        solar_generation = get_solar_generation_for_hour(hour, peak_power)
        daily_solar_generation_kwh.append(solar_generation)
    
    return daily_solar_generation_kwh

def simulate_self_consumption(consumption_kwh: list[float], solar_generation_kwh: list[float]) -> tuple[list[float], list[float], list[float]]:
    self_consumed_kwh = []
    grid_import_kwh = []
    solar_surplus_kwh = []


    for hour, solar_generation in enumerate(solar_generation_kwh):
        consumption = consumption_kwh[hour]

        self_consumed = min(consumption, solar_generation)
        grid_import = consumption - self_consumed
        solar_surplus = solar_generation - self_consumed

        self_consumed_kwh.append(self_consumed)
        grid_import_kwh.append(grid_import)
        solar_surplus_kwh.append(solar_surplus)

    return self_consumed_kwh, grid_import_kwh, solar_surplus_kwh