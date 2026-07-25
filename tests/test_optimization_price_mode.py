import pandas as pd
import pytest

from electricity_price_models import (
    FixedPriceModel,
    HourlyPriceModel,
    TimeOfUsePriceModel,
    ElectricityPriceModel,
)
from optimization import (
    build_best_scenarios_dataframe,
    build_scenario_financial_summary_text,
    format_optional_currency,
    format_optional_percentage,
    format_optional_years,
    get_best_scenario_by_net_present_value,
    run_economic_grid_search,
)
from financial_assumptions import FinancialAssumptions


def build_consumption_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 02:00:00",
                    "2026-06-01 11:00:00",
                    "2026-06-01 15:00:00",
                ]
            ),
            "consumption_kwh": [
                1.0,
                2.0,
                3.0,
            ],
        }
    )


def build_test_financial_assumptions(
    battery_replacement_year: int | None = None,
    battery_replacement_cost_fraction: float = 1.0,
) -> FinancialAssumptions:
    return FinancialAssumptions(
        project_lifetime_years=20,
        discount_rate=0.05,
        annual_operating_cost_eur=0.0,
        annual_solar_degradation_rate=0.0,
        annual_electricity_price_growth_rate=0.0,
        annual_operating_cost_growth_rate=0.0,
        battery_replacement_year=(battery_replacement_year),
        battery_replacement_cost_fraction=(battery_replacement_cost_fraction),
    )


def run_test_grid_search(
    price_model: ElectricityPriceModel,
) -> pd.DataFrame:
    return run_economic_grid_search(
        consumption_df=(build_consumption_dataframe()),
        solar_peak_powers_kw=[
            0.0,
        ],
        battery_capacities_kwh=[
            0.0,
        ],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=0.0,
        solar_cost_per_kw=0.0,
        battery_cost_per_kwh=0.0,
        price_model=price_model,
        simulation_days=1,
        pvgis_df=None,
    )


def test_grid_search_uses_fixed_price_model() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    assert len(results_df) == 1

    expected_cost = 6.0 * 0.20

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_cost)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_cost)


def test_grid_search_uses_time_of_use_model() -> None:
    price_model = TimeOfUsePriceModel(
        peak_price_eur_per_kwh=0.25,
        flat_price_eur_per_kwh=0.18,
        off_peak_price_eur_per_kwh=0.12,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_cost = 1.0 * 0.12 + 2.0 * 0.25 + 3.0 * 0.18

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_cost)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_cost)


def test_grid_search_uses_hourly_price_model() -> None:
    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 02:00:00",
                    "2026-06-01 11:00:00",
                    "2026-06-01 15:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                0.10,
                0.20,
                0.15,
            ],
        }
    )

    price_model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_cost = 1.0 * 0.10 + 2.0 * 0.20 + 3.0 * 0.15

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_cost)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_cost)


def test_grid_search_allows_negative_hourly_prices() -> None:
    consumption_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 14:00:00",
                ]
            ),
            "consumption_kwh": [
                1.0,
            ],
        }
    )

    price_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 14:00:00",
                ]
            ),
            "price_eur_per_kwh": [
                -0.01,
            ],
        }
    )

    price_model = HourlyPriceModel(
        price_df=price_df,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
        allow_negative_prices=True,
    )

    results_df = run_economic_grid_search(
        consumption_df=consumption_df,
        solar_peak_powers_kw=[
            0.0,
        ],
        battery_capacities_kwh=[
            0.0,
        ],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=800.0,
        solar_cost_per_kw=900.0,
        battery_cost_per_kwh=500.0,
        price_model=price_model,
        simulation_days=1,
        pvgis_df=None,
    )

    assert len(results_df) == 1

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(0.0)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(0.0)


def test_grid_search_stores_fixed_price_cost_breakdown() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.05,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_variable_cost = 6.0 * 0.20
    expected_fixed_power_cost = 4.6 * 35.0 / 365

    assert results_df.loc[
        0,
        "base_variable_energy_cost_eur",
    ] == pytest.approx(expected_variable_cost)

    assert results_df.loc[
        0,
        "base_fixed_power_cost_eur",
    ] == pytest.approx(expected_fixed_power_cost)

    assert results_df.loc[
        0,
        "base_surplus_compensation_eur",
    ] == pytest.approx(0.0)

    assert results_df.loc[
        0,
        "base_net_cost_eur",
    ] == pytest.approx(expected_variable_cost + expected_fixed_power_cost)

    assert results_df.loc[
        0,
        "scenario_variable_energy_cost_eur",
    ] == pytest.approx(expected_variable_cost)

    assert results_df.loc[
        0,
        "scenario_fixed_power_cost_eur",
    ] == pytest.approx(expected_fixed_power_cost)

    assert results_df.loc[
        0,
        "scenario_surplus_compensation_eur",
    ] == pytest.approx(0.0)

    assert results_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(expected_variable_cost + expected_fixed_power_cost)


def test_grid_search_includes_cost_breakdown_columns() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    expected_columns = {
        "base_variable_energy_cost_eur",
        "base_fixed_power_cost_eur",
        "base_surplus_compensation_eur",
        "base_net_cost_eur",
        "scenario_variable_energy_cost_eur",
        "scenario_fixed_power_cost_eur",
        "scenario_surplus_compensation_eur",
        "scenario_net_cost_eur",
    }

    assert expected_columns.issubset(results_df.columns)


def test_best_scenarios_dataframe_preserves_cost_breakdown() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.05,
        contracted_power_kw=4.6,
        power_price_eur_per_kw_year=35.0,
    )

    results_df = run_test_grid_search(price_model)

    scenario = results_df.iloc[0]

    best_scenarios_df = build_best_scenarios_dataframe(
        best_payback_scenario=scenario,
        best_self_sufficiency_scenario=scenario,
    )

    expected_columns = {
        "base_variable_energy_cost_eur",
        "base_fixed_power_cost_eur",
        "base_surplus_compensation_eur",
        "base_net_cost_eur",
        "scenario_variable_energy_cost_eur",
        "scenario_fixed_power_cost_eur",
        "scenario_surplus_compensation_eur",
        "scenario_net_cost_eur",
    }

    assert expected_columns.issubset(best_scenarios_df.columns)

    assert best_scenarios_df["criterion"].tolist() == [
        "best_payback",
        "best_self_sufficiency",
    ]

    assert best_scenarios_df.loc[
        0,
        "scenario_net_cost_eur",
    ] == pytest.approx(scenario["scenario_net_cost_eur"])

    assert best_scenarios_df.loc[
        1,
        "scenario_net_cost_eur",
    ] == pytest.approx(scenario["scenario_net_cost_eur"])


def test_best_scenarios_dataframe_preserves_extra_columns() -> None:
    scenario = pd.Series(
        {
            "solar_peak_power_kw": 3.0,
            "battery_capacity_kwh": 2.0,
            "annual_savings_eur": 500.0,
            "custom_future_metric": 42.0,
        }
    )

    result_df = build_best_scenarios_dataframe(
        best_payback_scenario=scenario,
        best_self_sufficiency_scenario=scenario,
    )

    assert "custom_future_metric" in result_df.columns

    assert result_df["custom_future_metric"].tolist() == pytest.approx(
        [
            42.0,
            42.0,
        ]
    )


def test_grid_search_leaves_financial_metrics_empty_without_assumptions() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_test_grid_search(price_model)

    assert pd.isna(
        results_df.loc[
            0,
            "net_present_value_eur",
        ]
    )

    assert pd.isna(
        results_df.loc[
            0,
            "discounted_payback_years",
        ]
    )

    assert pd.isna(
        results_df.loc[
            0,
            "internal_rate_of_return",
        ]
    )


def test_grid_search_calculates_financial_metrics() -> None:
    consumption_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2026-06-01 12:00:00",
                ]
            ),
            "consumption_kwh": [
                1.0,
            ],
        }
    )

    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=1.0,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_economic_grid_search(
        consumption_df=consumption_df,
        solar_peak_powers_kw=[1.0],
        battery_capacities_kwh=[0.0],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=0.0,
        solar_cost_per_kw=100.0,
        battery_cost_per_kwh=0.0,
        price_model=price_model,
        simulation_days=1,
        pvgis_df=None,
        financial_assumptions=(build_test_financial_assumptions()),
    )

    assert len(results_df) == 1

    assert (
        results_df.loc[
            0,
            "net_present_value_eur",
        ]
        > 0
    )

    assert pd.notna(
        results_df.loc[
            0,
            "discounted_payback_years",
        ]
    )

    assert pd.notna(
        results_df.loc[
            0,
            "internal_rate_of_return",
        ]
    )


def test_grid_search_has_no_replacement_cost_without_battery() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_economic_grid_search(
        consumption_df=build_consumption_dataframe(),
        solar_peak_powers_kw=[0.0],
        battery_capacities_kwh=[0.0],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=0.0,
        solar_cost_per_kw=0.0,
        battery_cost_per_kwh=500.0,
        price_model=price_model,
        simulation_days=1,
        pvgis_df=None,
        financial_assumptions=(
            build_test_financial_assumptions(
                battery_replacement_year=10,
                battery_replacement_cost_fraction=0.70,
            )
        ),
    )

    assert results_df.loc[
        0,
        "battery_replacement_cost_eur",
    ] == pytest.approx(0.0)


def test_grid_search_calculates_battery_replacement_cost() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    results_df = run_economic_grid_search(
        consumption_df=build_consumption_dataframe(),
        solar_peak_powers_kw=[0.0],
        battery_capacities_kwh=[5.0],
        battery_efficiency=0.90,
        max_charge_power_kw=1.0,
        max_discharge_power_kw=1.0,
        initial_battery_state_kwh=0.0,
        fixed_installation_cost=0.0,
        solar_cost_per_kw=0.0,
        battery_cost_per_kwh=500.0,
        price_model=price_model,
        simulation_days=1,
        pvgis_df=None,
        financial_assumptions=(
            build_test_financial_assumptions(
                battery_replacement_year=10,
                battery_replacement_cost_fraction=0.70,
            )
        ),
    )

    expected_replacement_cost = 5.0 * 500.0 * 0.70

    assert results_df.loc[
        0,
        "battery_replacement_cost_eur",
    ] == pytest.approx(expected_replacement_cost)


def test_battery_replacement_cost_reduces_net_present_value() -> None:
    price_model = FixedPriceModel(
        fixed_price_eur_per_kwh=0.20,
        surplus_compensation_price=0.0,
        contracted_power_kw=0.0,
        power_price_eur_per_kw_year=0.0,
    )

    common_arguments = {
        "consumption_df": build_consumption_dataframe(),
        "solar_peak_powers_kw": [1.0],
        "battery_capacities_kwh": [2.0],
        "battery_efficiency": 0.90,
        "max_charge_power_kw": 1.0,
        "max_discharge_power_kw": 1.0,
        "initial_battery_state_kwh": 0.0,
        "fixed_installation_cost": 0.0,
        "solar_cost_per_kw": 100.0,
        "battery_cost_per_kwh": 500.0,
        "price_model": price_model,
        "simulation_days": 1,
        "pvgis_df": None,
    }

    without_replacement_df = run_economic_grid_search(
        **common_arguments,
        financial_assumptions=(build_test_financial_assumptions()),
    )

    with_replacement_df = run_economic_grid_search(
        **common_arguments,
        financial_assumptions=(
            build_test_financial_assumptions(
                battery_replacement_year=10,
                battery_replacement_cost_fraction=0.70,
            )
        ),
    )

    assert (
        with_replacement_df.loc[
            0,
            "net_present_value_eur",
        ]
        < without_replacement_df.loc[
            0,
            "net_present_value_eur",
        ]
    )


def test_get_best_scenario_by_net_present_value() -> None:
    results_df = pd.DataFrame(
        {
            "solar_peak_power_kw": [
                1.0,
                2.0,
                3.0,
            ],
            "battery_capacity_kwh": [
                0.0,
                1.0,
                2.0,
            ],
            "net_present_value_eur": [
                1000.0,
                3500.0,
                2200.0,
            ],
        }
    )

    best_scenario = get_best_scenario_by_net_present_value(results_df)

    assert best_scenario["solar_peak_power_kw"] == pytest.approx(2.0)

    assert best_scenario["battery_capacity_kwh"] == pytest.approx(1.0)

    assert best_scenario["net_present_value_eur"] == pytest.approx(3500.0)


def test_get_best_scenario_by_net_present_value_rejects_empty_values() -> None:
    results_df = pd.DataFrame(
        {
            "net_present_value_eur": [
                None,
                None,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="No valid net present value",
    ):
        get_best_scenario_by_net_present_value(results_df)


def test_best_scenarios_dataframe_includes_net_present_value_criterion() -> None:
    scenario = pd.Series(
        {
            "solar_peak_power_kw": 3.0,
            "battery_capacity_kwh": 2.0,
            "net_present_value_eur": 5000.0,
        }
    )

    result_df = build_best_scenarios_dataframe(
        best_payback_scenario=scenario,
        best_self_sufficiency_scenario=scenario,
        best_net_present_value_scenario=(scenario),
    )

    assert result_df["criterion"].tolist() == [
        "best_payback",
        "best_self_sufficiency",
        "best_net_present_value",
    ]

    assert result_df.loc[
        2,
        "net_present_value_eur",
    ] == pytest.approx(5000.0)


def test_optional_financial_metric_formatters() -> None:
    assert format_optional_currency(1234.567) == "1234.57 EUR"

    assert format_optional_currency(None) == "Not available"

    assert format_optional_years(8.456) == "8.46 years"

    assert format_optional_years(None) == "Not achieved"

    assert format_optional_percentage(0.125) == "12.50%"

    assert format_optional_percentage(None) == "Not available"


def test_build_scenario_financial_summary_text() -> None:
    scenario = pd.Series(
        {
            "solar_peak_power_kw": 3.0,
            "battery_capacity_kwh": 2.0,
            "investment_cost_eur": 4500.0,
            "battery_replacement_cost_eur": 700.0,
            "annual_savings_eur": 800.0,
            "payback_years": 5.625,
            "net_present_value_eur": 4200.0,
            "discounted_payback_years": 7.25,
            "internal_rate_of_return": 0.14,
            "self_sufficiency": 0.72,
            "grid_import_kwh": 1200.0,
            "solar_surplus_kwh": 450.0,
        }
    )

    summary = build_scenario_financial_summary_text(
        title="Test scenario",
        scenario=scenario,
    )

    assert "Test scenario:" in summary
    assert "Battery replacement cost: 700.00 EUR" in summary
    assert "Net present value: 4200.00 EUR" in summary
    assert "Discounted payback: 7.25 years" in summary
    assert "Internal rate of return: 14.00%" in summary
