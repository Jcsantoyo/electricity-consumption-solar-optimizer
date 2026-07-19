import pandas as pd

from electricity_price_models import (
    ElectricityPriceModel,
    FixedPriceModel,
    HourlyPriceModel,
    TimeOfUsePriceModel,
)


def calculate_variable_cost_with_model(
    energy_df: pd.DataFrame,
    price_model: ElectricityPriceModel,
) -> float:
    return float(
        price_model.calculate_variable_grid_cost(
            energy_df=energy_df,
            grid_import_column="grid_import_kwh",
        )
    )


def calculate_flat_grid_import_cost(
    energy_df: pd.DataFrame,
    flat_price_eur_per_kwh: float,
) -> float:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=(
            flat_price_eur_per_kwh
        ),
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    return calculate_variable_cost_with_model(
        energy_df=energy_df,
        price_model=price_model,
    )


def compare_flat_vs_hourly_price_cost(
    energy_df: pd.DataFrame,
    price_df: pd.DataFrame,
    flat_price_eur_per_kwh: float,
    allow_negative_hourly_prices: bool = False,
) -> dict:
    fixed_model = FixedPriceModel(
        fixed_price_eur_per_kwh=(
            flat_price_eur_per_kwh
        ),
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    hourly_model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
        allow_negative_prices=(
            allow_negative_hourly_prices
        ),
    )

    flat_cost = calculate_variable_cost_with_model(
        energy_df=energy_df,
        price_model=fixed_model,
    )

    hourly_cost = calculate_variable_cost_with_model(
        energy_df=energy_df,
        price_model=hourly_model,
    )

    difference = hourly_cost - flat_cost

    return {
        "flat_cost_eur": flat_cost,
        "hourly_cost_eur": hourly_cost,
        "difference_eur": difference,
    }


def compare_tariff_vs_hourly_price_cost(
    energy_df: pd.DataFrame,
    price_df: pd.DataFrame,
    peak_price_eur_per_kwh: float,
    flat_price_eur_per_kwh: float,
    off_peak_price_eur_per_kwh: float,
    allow_negative_hourly_prices: bool = False,
) -> dict:
    tariff_model = TimeOfUsePriceModel(
        peak_price_eur_per_kwh=(
            peak_price_eur_per_kwh
        ),
        flat_price_eur_per_kwh=(
            flat_price_eur_per_kwh
        ),
        off_peak_price_eur_per_kwh=(
            off_peak_price_eur_per_kwh
        ),
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    hourly_model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
        allow_negative_prices=(
            allow_negative_hourly_prices
        ),
    )

    tariff_cost = calculate_variable_cost_with_model(
        energy_df=energy_df,
        price_model=tariff_model,
    )

    hourly_cost = calculate_variable_cost_with_model(
        energy_df=energy_df,
        price_model=hourly_model,
    )

    difference = hourly_cost - tariff_cost

    return {
        "tariff_cost_eur": tariff_cost,
        "hourly_cost_eur": hourly_cost,
        "difference_eur": difference,
    }


def compare_all_price_modes(
    energy_df: pd.DataFrame,
    price_df: pd.DataFrame,
    fixed_price_eur_per_kwh: float,
    peak_price_eur_per_kwh: float,
    flat_price_eur_per_kwh: float,
    off_peak_price_eur_per_kwh: float,
    allow_negative_hourly_prices: bool = False,
) -> pd.DataFrame:
    models = {
        "flat_fixed": FixedPriceModel(
            fixed_price_eur_per_kwh=(
                fixed_price_eur_per_kwh
            ),
            surplus_compensation_price=0.0,
            contracted_power_kw=0.0,
            power_price_eur_per_kw_year=0.0,
        ),
        "spanish_2_0td": TimeOfUsePriceModel(
            peak_price_eur_per_kwh=(
                peak_price_eur_per_kwh
            ),
            flat_price_eur_per_kwh=(
                flat_price_eur_per_kwh
            ),
            off_peak_price_eur_per_kwh=(
                off_peak_price_eur_per_kwh
            ),
            surplus_compensation_price=0.0,
            contracted_power_kw=0.0,
            power_price_eur_per_kw_year=0.0,
        ),
        "hourly": HourlyPriceModel(
            price_df=price_df,
            surplus_compensation_price=0.0,
            contracted_power_kw=0.0,
            power_price_eur_per_kw_year=0.0,
            allow_negative_prices=(
                allow_negative_hourly_prices
            ),
        ),
    }

    rows = []

    for price_mode, price_model in models.items():
        variable_grid_cost = (
            calculate_variable_cost_with_model(
                energy_df=energy_df,
                price_model=price_model,
            )
        )

        rows.append(
            {
                "price_mode": price_mode,
                "variable_grid_cost_eur": (
                    variable_grid_cost
                ),
            }
        )

    comparison_df = pd.DataFrame(
        rows
    )

    fixed_cost = comparison_df.loc[
        comparison_df["price_mode"]
        == "flat_fixed",
        "variable_grid_cost_eur",
    ].iloc[0]

    tariff_cost = comparison_df.loc[
        comparison_df["price_mode"]
        == "spanish_2_0td",
        "variable_grid_cost_eur",
    ].iloc[0]

    comparison_df[
        "difference_vs_flat_eur"
    ] = (
        comparison_df[
            "variable_grid_cost_eur"
        ]
        - fixed_cost
    )

    comparison_df[
        "difference_vs_2_0td_eur"
    ] = (
        comparison_df[
            "variable_grid_cost_eur"
        ]
        - tariff_cost
    )

    return comparison_df