from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from hourly_price_calculator import calculate_total_hourly_grid_import_cost
from tariff import (
    calculate_fixed_power_cost,
    calculate_net_electricity_cost_with_tariff,
    calculate_surplus_compensation,
    calculate_variable_grid_cost_with_tariff,
)


class ElectricityPriceModel(Protocol):
    def calculate_net_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
        surplus_column: str,
        simulation_days: int,
    ) -> float: ...

    def calculate_variable_grid_cost(
        self, energy_df: pd.DataFrame, grid_import_column: str
    ) -> float: ...


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
        simulation_days: int,
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
            simulation_days,
        )

    def calculate_variable_grid_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
    ) -> float:
        if grid_import_column not in energy_df.columns:
            raise ValueError(f"Missing required energy column: {grid_import_column}")

        grid_import = pd.to_numeric(
            energy_df[grid_import_column],
            errors="coerce",
        )

        if grid_import.isna().any():
            raise ValueError("Energy data contains invalid grid import values")

        if (grid_import < 0).any():
            raise ValueError("Energy data contains negative grid import values")

        return float(grid_import.sum() * self.fixed_price_eur_per_kwh)


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
            "Annual power price": self.power_price_eur_per_kw_year,
        }

        for field_name, value in prices.items():
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")

    def calculate_net_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
        surplus_column: str,
        simulation_days: int,
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
            simulation_days,
        )

    def calculate_variable_grid_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
    ) -> float:
        if "datetime" not in energy_df.columns:
            raise ValueError("Missing required energy column: datetime")

        if grid_import_column not in energy_df.columns:
            raise ValueError(f"Missing required energy column: {grid_import_column}")

        prepared_energy_df = energy_df.copy()

        prepared_energy_df["datetime"] = pd.to_datetime(
            prepared_energy_df["datetime"],
            errors="coerce",
        )

        if prepared_energy_df["datetime"].isna().any():
            raise ValueError("Energy data contains invalid datetime values")

        return float(
            calculate_variable_grid_cost_with_tariff(
                df=prepared_energy_df,
                grid_import_column=grid_import_column,
                peak_price=(self.peak_price_eur_per_kwh),
                flat_price=(self.flat_price_eur_per_kwh),
                off_peak_price=(self.off_peak_price_eur_per_kwh),
            )
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

        required_columns = {"datetime", "price_eur_per_kwh"}

        missing_columns = required_columns - set(self.price_df.columns)

        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))

            raise ValueError(
                f"Hourly price data is missing required columns: {missing_text}"
            )

        if self.surplus_compensation_price < 0:
            raise ValueError("Surplus compensation price cannot be negative")

        if self.contracted_power_kw < 0:
            raise ValueError("Contracted power cannot be negative")

        if self.power_price_eur_per_kw_year < 0:
            raise ValueError("Annual power price cannot be negative")

        prepared_price_df = self.price_df.copy()

        prepared_price_df["datetime"] = pd.to_datetime(
            prepared_price_df["datetime"], errors="coerce"
        )

        prepared_price_df["price_eur_per_kwh"] = pd.to_numeric(
            prepared_price_df["price_eur_per_kwh"], errors="coerce"
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

        prepared_price_df = prepared_price_df.sort_values("datetime").reset_index(
            drop=True
        )

        object.__setattr__(self, "price_df", prepared_price_df)

    def calculate_net_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
        surplus_column: str,
        simulation_days: int,
    ) -> float:
        if simulation_days <= 0:
            raise ValueError("Simulation days must be greater than zero")

        variable_grid_cost = self.calculate_variable_grid_cost(
            energy_df=energy_df,
            grid_import_column=(grid_import_column),
        )

        surplus_compensation = calculate_surplus_compensation(
            df=energy_df,
            surplus_column=surplus_column,
            surplus_compensation_price=(self.surplus_compensation_price),
        )

        fixed_power_cost = calculate_fixed_power_cost(
            contracted_power_kw=(self.contracted_power_kw),
            power_price_eur_per_kw_year=(self.power_price_eur_per_kw_year),
            simulation_days=simulation_days,
        )

        net_cost = variable_grid_cost + fixed_power_cost - surplus_compensation

        return max(
            float(net_cost),
            0.0,
        )

    def calculate_variable_grid_cost(
        self,
        energy_df: pd.DataFrame,
        grid_import_column: str,
    ) -> float:
        required_columns = {
            "datetime",
            grid_import_column,
        }

        missing_columns = required_columns - set(energy_df.columns)

        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Energy data is missing required columns: {missing_text}")

        hourly_energy_df = energy_df.loc[
            :,
            [
                "datetime",
                grid_import_column,
            ],
        ].copy()

        hourly_energy_df = hourly_energy_df.rename(
            columns={grid_import_column: ("grid_import_kwh")}
        )

        return calculate_total_hourly_grid_import_cost(
            energy_df=hourly_energy_df,
            price_df=self.price_df,
            allow_negative_prices=(self.allow_negative_prices),
        )
