def get_price_for_hour(hour: int) -> float:
    if hour < 7:
        return 0.10
    elif hour < 18:
        return 0.18
    else:
        return 0.28
    

def calculate_fixed_tariff_cost(consumption_kwh: list[float], price_per_kwh: float) -> float:
    total_consumption = sum(consumption_kwh)
    total_cost = total_consumption * price_per_kwh
    return total_cost


def calculate_variable_tariff_cost(consumption_kwh: list[float]) -> tuple[float, list[float], list[float]]:
    hourly_costs_eur = []
    hourly_prices_eur_per_kwh = []

    for hour, consumption in enumerate(consumption_kwh):
        hourly_price = get_price_for_hour(hour)
        hourly_cost = hourly_price * consumption

        hourly_prices_eur_per_kwh.append(hourly_price)
        hourly_costs_eur.append(hourly_cost)
        
    
    total_cost = sum(hourly_costs_eur)
    return total_cost, hourly_costs_eur, hourly_prices_eur_per_kwh
