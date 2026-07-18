from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from hourly_price_calculator import calculate_total_hourly_grid_import_cost
from tariff import (
    calculate_net_electricity_cost_with_tariff,
    calculate_fixed_power_cost,
    calculate_surplus_compensation
)


class ElectricityPriceModel(Protocol):
    def calculate_net_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
        surplus_column: str,
        simulation_days: int,
    ) -> float:
        ...


@dataclass(frozen=True)
class FixedPriceModel:
    fixed_price_eur_per_kwh: float
    surplus_compensation_price: float
    contracted_power_kw: float
    power_price_eur_per_kw_year: float

    def __post_init__(self) -> None:
        if self.fixed_price_eur_per_kwh < 0:
            raise ValueError("Fixed electricity price cannot be negative")
        
        if self.surplus_compensation_price < 0:
            raise ValueError("Surplus compensation price cannot be negative")
        
        if self.contracted_power_kw < 0:
            raise ValueError("Contracted power cannot be negative")
        
        if self.power_price_eur_per_kw_year < 0:
            raise ValueError("Annual power price cannot be negative")

    def calculate_net_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
        surplus_column: str,
        simulation_days: int
    ) -> float:
        if simulation_days <= 0:
            raise ValueError("Simulation days must be greater than zero")
        
        return calculate_net_electricity_cost_with_tariff(
            energy_df,
            grid_import_column,
            surplus_column,
            self.fixed_price_eur_per_kwh,
            self.fixed_price_eur_per_kwh,
            self.fixed_price_eur_per_kwh,
            self.surplus_compensation_price,
            self.contracted_power_kw,
            self.power_price_eur_per_kw_year,
            simulation_days
        )
    


@dataclass(frozen=True)
class TimeOfUsePriceModel:
    peak_price_eur_per_kwh: float
    flat_price_eur_per_kwh: float
    off_peak_price_eur_per_kwh: float
    surplus_compensation_price: float
    contracted_power_kw: float
    power_price_eur_per_kw_year: float

    def __post_init__(self) -> None:
        prices = {
            "Peak_power_price": self.peak_price_eur_per_kwh,
            "Flat electricity price": self.flat_price_eur_per_kwh,
            "Off-peak electricity price": self.off_peak_price_eur_per_kwh,
            "Surplus compensation price": self.surplus_compensation_price,
            "Contracted power": self.contracted_power_kw,
            "Annual power price": self.power_price_eur_per_kw_year
        }

        for field_name, value in prices.items():
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")
            
    def calculate_net_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
        surplus_column: str,
        simulation_days: str
    ) -> float:
        if simulation_days <= 0:
            raise ValueError("Simulation days must be greater than zero")
        
        return calculate_net_electricity_cost_with_tariff(
            energy_df,
            grid_import_column,
            surplus_column,
            self.peak_price_eur_per_kwh,
            self.flat_price_eur_per_kwh,
            self.off_peak_price_eur_per_kwh,
            self.surplus_compensation_price,
            self.contracted_power_kw,
            self.power_price_eur_per_kw_year,
            simulation_days
        )
        
@dataclass(frozen=True)
class HourlyPriceModel:
    price_df: pd.DataFrame
    surplus_compensation_price: float
    contracted_power_kw: float
    power_price_eur_per_kw_year: float
    allow_negative_prices: bool = False

    def __post_init__(self) -> None:
        if self.price_df.empty:
            raise ValueError("Hourly price data cannot be empty")
        
        required_columns = {
            "datetime",
            "price_eur_per_kwh"
        }

        missing_columns = required_columns - set(self.price_df.columns)

        if missing_columns: 
            missing_text = ", ".join(sorted(missing_columns))
            
            raise ValueError(f"Hourly price data is missing required columns: {missing_text}")
        
        if self.surplus_compensation_price < 0:
            raise ValueError("Surplus compensation price cannot be negative")
        
        if self.contracted_power_kw < 0:
            raise ValueError("Contracted power cannot be negative")
        
        if self.power_price_eur_per_kw_year < 0:
            raise ValueError("Annual power price cannot be negative")
        
        prepared_price_df = self.price_df.copy()

        prepared_price_df["datetime"] = pd.to_datetime(
            prepared_price_df["datetime"],
            errors="coerce"
        )

        prepared_price_df["price_eur_per_kwh"] = pd.to_numeric(
            prepared_price_df["price_eur_per_kwh"],
            errors="coerce"
        )

        if prepared_price_df["datetime"].isna().any():
            raise ValueError("Hourly price data contains invalid datetime values")
        
        if prepared_price_df["price_eur_per_kwh"].isna().any():
            raise ValueError("Hourly price data contains invalid price values")
        
        if (
            not self.allow_negative_prices 
            and (prepared_price_df["price_eur_per_kwh"] < 0).any()
        ):
            raise ValueError("Hourly price data contains negative prices")
        
        prepared_price_df = prepared_price_df.sort_values("datetime").reset_index(drop=True)

        object.__setattr__(self, "price_df", prepared_price_df)

    def calculate_net_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
        surplus_column: str,
        simulation_days: int
    ) -> float:
        if simulation_days <= 0:
            raise ValueError("Simulation days must be greater than zero")
        
        hourly_energy_df = energy_df[
            [
                "datetime",
                grid_import_column,
            ]
        ].copy()
        
        hourly_energy_df = (
            hourly_energy_df.rename(
                columns={
                    grid_import_column: "grid_import_kwh"
                }
            )
        )
        
        variable_grid_cost = calculate_total_hourly_grid_import_cost(
            hourly_energy_df,
            self.price_df,
            self.allow_negative_prices
        )

        surplus_compensation = calculate_surplus_compensation(
            energy_df,
            surplus_column,
            self.surplus_compensation_price
        )

        fixed_power_cost = calculate_fixed_power_cost(
            self.contracted_power_kw,
            self.power_price_eur_per_kw_year,
            simulation_days
        )

        net_cost = variable_grid_cost + fixed_power_cost - surplus_compensation

        return max(float(net_cost), 0.0)