from collections.abc import Mapping

import pandas as pd

from electricity_price_models import (
    ElectricityPriceModel,
    FixedPriceModel,
    TimeOfUsePriceModel,
    HourlyPriceModel
)

from project_scenario import ProjectScenario

def build_electricity_price_model(
    scenario: ProjectScenario,
    tariff_profile: Mapping[str, float],
    hourly_price_df: pd.DataFrame | None = None
) -> ElectricityPriceModel:
    if scenario.price_mode == "fixed":
        return FixedPriceModel(
            tariff_profile["flat_price_eur_per_kwh"],
            tariff_profile["surplus_compensation_eur_per_kwh"],
            tariff_profile["contracted_power_kw"],
            tariff_profile["power_price_eur_per_kw_year"]
        )
    
    if scenario.price_mode == "time_of_use":
        return TimeOfUsePriceModel(
            tariff_profile["peak_price_eur_per_kwh"],
            tariff_profile["flat_price_eur_per_kwh"],
            tariff_profile["off_peak_price_eur_per_kwh"],
            tariff_profile["surplus_compensation_eur_per_kwh"],
            tariff_profile["contracted_power_kw"],
            tariff_profile["power_price_eur_per_kw_year"]
        )
    
    if scenario.price_mode == "wholesale_hourly":
        if hourly_price_df is None:
            raise ValueError("Wholesale hourly price mode requires hourly price data")
        
        return HourlyPriceModel(
            hourly_price_df,
            tariff_profile["surplus_compensation_eur_per_kwh"],
            tariff_profile["contracted_power_kw"],
            tariff_profile["power_price_eur_per_kw_year"],
            scenario.allow_negative_hourly_prices
        )
    
    raise ValueError(f"Unsupported electricity price mode: {scenario.price_mode}")