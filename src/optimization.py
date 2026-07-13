import pandas as pd

from solar import generate_solar_profile_for_timestamps
from economics import (
    calculate_total_installation_cost,
    calculate_simple_payback_years,
)

from solar_data_loader import get_pvgis_generation_for_timestamps
from battery import simulate_battery
from hourly_price_calculator import calculate_total_hourly_grid_import_cost
from tariff import(
    calculate_fixed_power_cost,
    calculate_net_electricity_cost_with_tariff,
    calculate_surplus_compensation
)

def calculate_net_electricity_cost_for_price_mode(
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
    hourly_price_df: pd.DataFrame | None = None,
    allow_negative_hourly_prices: bool = False
) -> float:
    
    if hourly_price_df is None:
        return calculate_net_electricity_cost_with_tariff(
            df,
            grid_import_column,
            surplus_column,
            peak_price,
            flat_price,
            off_peak_price,
            surplus_compensation_price,
            contracted_power_kw,
            power_price_eur_per_kw_year,
            simulation_days
        )
    
    hourly_energy_df = df[["datetime", grid_import_column]].copy()

    hourly_energy_df = hourly_energy_df.rename(
        columns={
            grid_import_column: "grid_import_kwh"
        }
    )

    variable_grid_cost = calculate_total_hourly_grid_import_cost(
        hourly_energy_df,
        hourly_price_df,
        allow_negative_hourly_prices
    )

    surplus_compensation = calculate_surplus_compensation(
        df,
        surplus_column,
        surplus_compensation_price
    )

    fixed_power_cost = calculate_fixed_power_cost(
        contracted_power_kw,
        power_price_eur_per_kw_year,
        simulation_days
    )

    net_cost = variable_grid_cost + fixed_power_cost - surplus_compensation

    return max(net_cost, 0.0)

def run_economic_grid_search(
    consumption_df: pd.DataFrame,
    solar_peak_powers_kw: list[float],
    battery_capacities_kwh: list[float],
    battery_efficiency: float,
    max_charge_power_kw: float,
    max_discharge_power_kw: float,
    initial_battery_state_kwh: float,
    fixed_installation_cost: float,
    solar_cost_per_kw: float,
    battery_cost_per_kwh: float,
    peak_price: float,
    flat_price: float,
    off_peak_price: float,
    surplus_compensation_price: float,
    contracted_power_kw: float,
    power_price_eur_per_kw_year: float,
    simulation_days: int,
    pvgis_df: pd.DataFrame | None = None,
    hourly_price_df: pd.DataFrame | None = None,
    allow_negative_hourly_prices: bool = False
) -> pd.DataFrame:
    results = []

    base_cost_df = consumption_df[["datetime", "consumption_kwh"]].copy()
    base_cost_df["grid_import_kwh"] = base_cost_df["consumption_kwh"]
    base_cost_df["solar_surplus_kwh"] = 0.0

    base_net_cost = calculate_net_electricity_cost_for_price_mode(
        base_cost_df,
        grid_import_column="grid_import_kwh",
        surplus_column="solar_surplus_kwh",
        peak_price=peak_price,
        flat_price=flat_price,
        off_peak_price=off_peak_price,
        surplus_compensation_price=surplus_compensation_price,
        contracted_power_kw=contracted_power_kw,
        power_price_eur_per_kw_year=power_price_eur_per_kw_year,
        simulation_days=simulation_days,
        hourly_price_df=hourly_price_df,
        allow_negative_hourly_prices=allow_negative_hourly_prices
    )

    for solar_peak_power_kw in solar_peak_powers_kw:
        if pvgis_df is None:
            solar_generation_kwh = generate_solar_profile_for_timestamps(
                consumption_df["datetime"], solar_peak_power_kw
            )
        else:
            solar_generation_kwh = get_pvgis_generation_for_timestamps(
                pvgis_df, consumption_df["datetime"], solar_peak_power_kw
            )

        for battery_capacity_kwh in battery_capacities_kwh:
            simulation_results = simulate_battery(
                consumption_kwh=consumption_df["consumption_kwh"].tolist(),
                solar_generation_kwh=solar_generation_kwh,
                battery_capacity_kwh=battery_capacity_kwh,
                battery_efficiency=battery_efficiency,
                max_charge_power_kw=max_charge_power_kw,
                max_discharge_power_kw=max_discharge_power_kw,
                initial_battery_state_kwh=initial_battery_state_kwh,
            )

            simulation_df = pd.DataFrame(simulation_results)

            simulation_df["datetime"] = consumption_df["datetime"].reset_index(
                drop=True
            )

            simulation_df["consumption_kwh"] = consumption_df[
                "consumption_kwh"
            ].reset_index(drop=True)

            simulation_df["solar_generation_kwh"] = solar_generation_kwh

            scenario_net_cost = calculate_net_electricity_cost_for_price_mode(
                simulation_df,
                grid_import_column="grid_import_kwh",
                surplus_column="solar_surplus_kwh",
                peak_price=peak_price,
                flat_price=flat_price,
                off_peak_price=off_peak_price,
                surplus_compensation_price=surplus_compensation_price,
                contracted_power_kw=contracted_power_kw,
                power_price_eur_per_kw_year=power_price_eur_per_kw_year,
                simulation_days=simulation_days,
                hourly_price_df=hourly_price_df,
                allow_negative_hourly_prices=allow_negative_hourly_prices
            )

            period_savings = base_net_cost - scenario_net_cost

            annual_savings = period_savings * 365 / simulation_days

            investment_cost = calculate_total_installation_cost(
                solar_peak_power_kw=solar_peak_power_kw,
                battery_capacity_kwh=battery_capacity_kwh,
                fixed_installation_cost=fixed_installation_cost,
                solar_cost_per_kw=solar_cost_per_kw,
                battery_cost_per_kwh=battery_cost_per_kwh,
            )

            payback_years = calculate_simple_payback_years(
                investment_cost, annual_savings
            )

            total_consumption_kwh = simulation_df["consumption_kwh"].sum()

            total_grid_import_kwh = simulation_df["grid_import_kwh"].sum()

            annual_grid_import_kwh = total_grid_import_kwh * 365 / simulation_days

            total_solar_surplus_kwh = simulation_df["solar_surplus_kwh"].sum()

            self_sufficiency = 1 - total_grid_import_kwh / total_consumption_kwh

            results.append(
                {
                    "solar_peak_power_kw": solar_peak_power_kw,
                    "battery_capacity_kwh": battery_capacity_kwh,
                    "investment_cost_eur": investment_cost,
                    "base_net_cost_eur": base_net_cost,
                    "scenario_net_cost_eur": scenario_net_cost,
                    "annual_savings_eur": annual_savings,
                    "payback_years": payback_years,
                    "self_sufficiency": self_sufficiency,
                    "grid_import_kwh": total_grid_import_kwh,
                    "solar_surplus_kwh": total_solar_surplus_kwh,
                    "annual_grid_import_kwh": annual_grid_import_kwh,
                }
            )

    results_df = pd.DataFrame(results)

    return results_df


def get_best_scenario_by_payback(df: pd.DataFrame) -> pd.Series:
    valid_payback_df = df.dropna(subset=["payback_years"])

    if valid_payback_df.empty:
        raise ValueError("No valid payback values found.")

    best_index = valid_payback_df["payback_years"].idxmin()

    return valid_payback_df.loc[best_index]


def get_best_scenario_by_self_sufficiency(df: pd.DataFrame) -> pd.Series:
    best_index = df["self_sufficiency"].idxmax()

    return df.loc[best_index]


def print_scenario_summary(title: str, scenario: pd.Series) -> None:
    print(f"\n{title}:")
    print(f"Solar peak power: {scenario['solar_peak_power_kw']:.2f} kW")
    print(f"Battery capacity: {scenario['battery_capacity_kwh']:.2f} kWh")
    print(f"Investment cost: {scenario['investment_cost_eur']:.2f} EUR")
    print(f"Annual savings: {scenario['annual_savings_eur']:.2f} EUR/year")
    print(f"Payback: {scenario['payback_years']:.2f} years")
    print(f"Self-sufficiency: {scenario['self_sufficiency']:.2%}")
    print(f"Grid import: {scenario['grid_import_kwh']:.2f} kWh")
    print(f"Solar surplus: {scenario['solar_surplus_kwh']:.2f} kWh")


def print_scenario_comparison(
    best_payback_scenario: pd.Series, best_self_sufficiency_scenario: pd.Series
) -> None:
    print("\nComparison:")

    print(
        f"Best payback scenario: "
        f"{best_payback_scenario['solar_peak_power_kw']:.2f} kW solar, "
        f"{best_payback_scenario['battery_capacity_kwh']:.2f} kWh battery"
    )

    print(
        f"Best self-sufficiency scenario: "
        f"{best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW solar, "
        f"{best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh battery"
    )

    if (
        best_payback_scenario["solar_peak_power_kw"]
        == best_self_sufficiency_scenario["solar_peak_power_kw"]
        and best_payback_scenario["battery_capacity_kwh"]
        == best_self_sufficiency_scenario["battery_capacity_kwh"]
    ):
        print("Both criteria select the same scenario.")
    else:
        print(
            "The economically optimal scenario and the energy optimal scenario "
            "are different."
        )


def build_scenario_summary_text(
    best_payback_scenario: pd.Series,
    best_self_sufficiency_scenario: pd.Series,
    solar_data_source: str,
    electricity_price_mode: str
) -> str:
    text = ""

    text += "Electricity Consumption Solar Optimizer\n"
    text += "======================================\n\n"

    text += f"Solar data source: {solar_data_source}\n"
    text += f"Electricity price mode: {electricity_price_mode}\n\n"
    text += "Best scenario by payback:\n"
    text += f"Solar peak power: {best_payback_scenario['solar_peak_power_kw']:.2f} kW\n"
    text += (
        f"Battery capacity: {best_payback_scenario['battery_capacity_kwh']:.2f} kWh\n"
    )
    text += f"Investment cost: {best_payback_scenario['investment_cost_eur']:.2f} EUR\n"
    text += (
        f"Annual savings: {best_payback_scenario['annual_savings_eur']:.2f} EUR/year\n"
    )
    text += f"Payback: {best_payback_scenario['payback_years']:.2f} years\n"
    text += f"Self-sufficiency: {best_payback_scenario['self_sufficiency']:.2%}\n"
    text += f"Grid import: {best_payback_scenario['grid_import_kwh']:.2f} kWh\n"
    text += f"Solar surplus: {best_payback_scenario['solar_surplus_kwh']:.2f} kWh\n\n"

    text += "Best scenario by self-sufficiency:\n"
    text += f"Solar peak power: {best_self_sufficiency_scenario['solar_peak_power_kw']:.2f} kW\n"
    text += f"Battery capacity: {best_self_sufficiency_scenario['battery_capacity_kwh']:.2f} kWh\n"
    text += f"Investment cost: {best_self_sufficiency_scenario['investment_cost_eur']:.2f} EUR\n"
    text += f"Annual savings: {best_self_sufficiency_scenario['annual_savings_eur']:.2f} EUR/year\n"
    text += f"Payback: {best_self_sufficiency_scenario['payback_years']:.2f} years\n"
    text += (
        f"Self-sufficiency: {best_self_sufficiency_scenario['self_sufficiency']:.2%}\n"
    )
    text += (
        f"Grid import: {best_self_sufficiency_scenario['grid_import_kwh']:.2f} kWh\n"
    )
    text += f"Solar surplus: {best_self_sufficiency_scenario['solar_surplus_kwh']:.2f} kWh\n\n"

    if (
        best_payback_scenario["solar_peak_power_kw"]
        == best_self_sufficiency_scenario["solar_peak_power_kw"]
        and best_payback_scenario["battery_capacity_kwh"]
        == best_self_sufficiency_scenario["battery_capacity_kwh"]
    ):
        text += "Both criteria select the same scenario.\n"
    else:
        text += (
            "The economically optimal scenario and the energy optimal "
            "scenario are different.\n"
        )

    return text


def build_best_scenarios_dataframe(
    best_payback_scenario: pd.Series, best_self_sufficiency_scenario: pd.Series
) -> pd.DataFrame:
    rows = [
        {
            "criterion": "best_payback",
            "solar_peak_power_kw": best_payback_scenario["solar_peak_power_kw"],
            "battery_capacity_kwh": best_payback_scenario["battery_capacity_kwh"],
            "investment_cost_eur": best_payback_scenario["investment_cost_eur"],
            "annual_savings_eur": best_payback_scenario["annual_savings_eur"],
            "payback_years": best_payback_scenario["payback_years"],
            "self_sufficiency": best_payback_scenario["self_sufficiency"],
            "grid_import_kwh": best_payback_scenario["grid_import_kwh"],
            "annual_grid_import_kwh": best_payback_scenario["annual_grid_import_kwh"],
            "solar_surplus_kwh": best_payback_scenario["solar_surplus_kwh"],
        },
        {
            "criterion": "best_self_sufficiency",
            "solar_peak_power_kw": best_self_sufficiency_scenario[
                "solar_peak_power_kw"
            ],
            "battery_capacity_kwh": best_self_sufficiency_scenario[
                "battery_capacity_kwh"
            ],
            "investment_cost_eur": best_self_sufficiency_scenario[
                "investment_cost_eur"
            ],
            "annual_savings_eur": best_self_sufficiency_scenario["annual_savings_eur"],
            "payback_years": best_self_sufficiency_scenario["payback_years"],
            "self_sufficiency": best_self_sufficiency_scenario["self_sufficiency"],
            "grid_import_kwh": best_self_sufficiency_scenario["grid_import_kwh"],
            "annual_grid_import_kwh": best_self_sufficiency_scenario[
                "annual_grid_import_kwh"
            ],
            "solar_surplus_kwh": best_self_sufficiency_scenario["solar_surplus_kwh"],
        },
    ]

    return pd.DataFrame(rows)


def build_outputs_index_text(solar_data_source: str, electricity_price_mode: str) -> str:
    text = ""

    text += "# Project outputs\n\n"

    text += f"Solar data source: {solar_data_source}\n\n"
    text += f"Electricity price mode: {electricity_price_mode}\n\n"
    text += (
        "This folder contains the generated reports from the electricity "
        "consumption solar optimizer.\n\n"
    )

    text += "## CSV reports\n\n"

    text += "### `grid_search_results.csv`\n\n"
    text += (
        "Full historical grid search results. Each row represents one "
        "combination of solar peak power and battery capacity, including "
        "investment cost, annual savings, payback period, grid import, "
        "annual grid import, solar surplus and self-sufficiency.\n\n"
    )

    text += "### `best_scenarios.csv`\n\n"
    text += (
        "Summary table with the two selected historical optimal scenarios: "
        "one by minimum payback period and one by maximum self-sufficiency.\n\n"
    )

    text += "### `best_scenario_timeseries.csv`\n\n"
    text += (
        "Hourly energy flow table for the best economic historical scenario. "
        "It includes consumption, solar generation, self-consumption, battery "
        "charge, battery discharge, grid import, solar surplus and battery "
        "state.\n\n"
    )

    text += "### `forecast_results.csv`\n\n"
    text += (
        "Forecasting results for the test period. It includes the actual "
        "consumption and the predicted consumption generated by the Machine "
        "Learning model.\n\n"
    )

    text += "### `forecast_feature_importance.csv`\n\n"
    text += (
        "Feature importance values from the Random Forest forecasting model. "
        "It shows which variables are most relevant for predicting household "
        "electricity consumption.\n\n"
    )

    text += "### `forecast_model_comparison.csv`\n\n"
    text += (
        "Comparison between forecasting models using error metrics such as "
        "MAE and RMSE.\n\n"
    )

    text += "### `forecasted_consumption_for_optimization.csv`\n\n"
    text += (
        "Forecasted consumption converted into the standard project input "
        "format so it can be used by the solar and battery optimization "
        "pipeline.\n\n"
    )

    text += "### `forecast_optimization_results.csv`\n\n"
    text += (
        "Full grid search results using forecasted consumption instead of "
        "historical consumption.\n\n"
    )

    text += "### `forecast_optimization_best_scenarios.csv`\n\n"
    text += (
        "Best economic and best self-sufficiency scenarios obtained from "
        "forecast-based optimization.\n\n"
    )

    text += "### `historical_vs_forecast_optimization.csv`\n\n"
    text += (
        "Comparison table between the best historical optimization scenarios "
        "and the best forecast-based optimization scenarios.\n\n"
    )

    text += "## Text reports\n\n"

    text += "### `configuration_summary.md`\n\n"
    text += (
        "Summary of the configuration used by the project pipeline, including "
        "input data paths, PVGIS settings, grid search parameters, battery "
        "model assumptions, economic assumptions and the active tariff profile.\n\n"
    )

    text += "### `final_results_summary.md`\n\n"
    text += (
        "Readable final summary of the main results produced by the full "
        "pipeline. It compares the best historical and forecast-based "
        "optimization scenarios.\n\n"
    )

    text += "### `summary.txt`\n\n"
    text += (
        "Readable summary of the best historical economic scenario and the "
        "best historical self-sufficiency scenario.\n\n"
    )

    text += "### `outputs_index.md`\n\n"
    text += "Index describing the generated reports and plots.\n\n"

    text += "## Generated plots\n\n"

    text += "The main plots are saved in the `images/` folder:\n\n"

    text += "- `main_payback_grid_search.png`: payback period by solar power and battery capacity.\n"
    text += "- `main_self_sufficiency_grid_search.png`: self-sufficiency by solar power and battery capacity.\n"
    text += "- `best_scenarios_comparison.png`: comparison between the economic optimum and the energy optimum.\n"
    text += "- `best_scenario_timeseries.png`: hourly consumption, solar generation and grid import for the best economic scenario.\n"
    text += "- `best_scenario_battery_state.png`: battery state of charge over time.\n"
    text += "- `best_scenario_cumulative_energy.png`: cumulative consumption, solar generation, grid import and solar surplus.\n"
    text += "- `consumption_forecast_actual_vs_predicted.png`: actual vs predicted electricity consumption.\n"
    text += "- `forecast_feature_importance.png`: feature importance for the Random Forest forecasting model.\n"
    text += (
        "- `forecast_model_comparison.png`: comparison between forecasting models.\n"
    )
    text += "- `historical_vs_forecast_payback.png`: payback comparison between historical and forecast-based optimization.\n"
    text += "- `historical_vs_forecast_savings.png`: annual savings comparison between historical and forecast-based optimization.\n"
    text += "- `historical_vs_forecast_self_sufficiency.png`: self-sufficiency comparison between historical and forecast-based optimization.\n"
    text += "- `historical_vs_forecast_investment_cost.png`: investment cost comparison between historical and forecast-based optimization.\n"
    text += "- `historical_vs_forecast_grid_import.png`: annual grid import comparison between historical and forecast-based optimization.\n"

    return text
