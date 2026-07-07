import pandas as pd


def get_spanish_2_0td_period(timestamp: pd.Timestamp) -> str:
    hour = timestamp.hour
    weekday = timestamp.weekday()

    if weekday >= 5:
        return "off_peak"

    if 0 <= hour < 8:
        return "off_peak"

    if 8 <= hour < 10:
        return "flat"

    if 10 <= hour < 14:
        return "peak"

    if 14 <= hour < 18:
        return "flat"

    if 18 <= hour < 22:
        return "peak"

    return "flat"


def add_tariff_period_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["tariff_period"] = df["datetime"].apply(get_spanish_2_0td_period)

    return df


def get_energy_price_for_period(
    period: str, peak_price: float, flat_price: float, off_peak_price: float
) -> float:
    if period == "peak":
        return peak_price

    if period == "flat":
        return flat_price

    if period == "off_peak":
        return off_peak_price

    raise ValueError(f"Unknown tariff period: {period}")


def calculate_variable_grid_cost_with_tariff(
    df: pd.DataFrame,
    grid_import_column: str,
    peak_price: float,
    flat_price: float,
    off_peak_price: float,
) -> float:
    df = add_tariff_period_column(df)

    df["energy_price_eur_per_kwh"] = df["tariff_period"].apply(
        lambda period: get_energy_price_for_period(
            period,
            peak_price=peak_price,
            flat_price=flat_price,
            off_peak_price=off_peak_price,
        )
    )

    df["grid_cost_eur"] = df[grid_import_column] * df["energy_price_eur_per_kwh"]

    return df["grid_cost_eur"].sum()


def calculate_surplus_compensation(
    df: pd.DataFrame, surplus_column: str, surplus_compensation_price: float
) -> float:
    return (df[surplus_column] * surplus_compensation_price).sum()


def calculate_fixed_power_cost(
    contracted_power_kw: float, power_price_eur_per_kw_year: float, simulation_days: int
) -> float:
    return contracted_power_kw * power_price_eur_per_kw_year * simulation_days / 365


def calculate_net_electricity_cost_with_tariff(
    df: pd.DataFrame,
    grid_import_column: str,
    surplus_column: str,
    peak_price: float,
    flat_price: float,
    off_peak_price: float,
    surplus_compensation_price: float,
    contracted_power_kw: float,
    power_price_eur_per_kw_year: float,
    simulation_days: int,
) -> float:
    variable_grid_cost = calculate_variable_grid_cost_with_tariff(
        df,
        grid_import_column=grid_import_column,
        peak_price=peak_price,
        flat_price=flat_price,
        off_peak_price=off_peak_price,
    )

    surplus_compensation = calculate_surplus_compensation(
        df,
        surplus_column=surplus_column,
        surplus_compensation_price=surplus_compensation_price,
    )

    fixed_power_cost = calculate_fixed_power_cost(
        contracted_power_kw=contracted_power_kw,
        power_price_eur_per_kw_year=power_price_eur_per_kw_year,
        simulation_days=simulation_days,
    )

    net_cost = variable_grid_cost + fixed_power_cost - surplus_compensation

    return max(net_cost, 0.0)
