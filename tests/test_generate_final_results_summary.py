import pandas as pd
import pytest


from scripts.generate_final_results_summary import (
    build_final_results_summary,
    get_scenario,
    format_percent,
    format_years,
    format_eur,
    format_eur_per_year,
    format_kwh_per_year,
)


def build_sample_comparison_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "optimization_type": "historical",
                "scenario": "best_payback",
                "solar_peak_power_kw": 3.0,
                "battery_capacity_kwh": 0.0,
                "investment_cost_eur": 3500.0,
                "annual_savings_eur": 684.83,
                "payback_years": 5.11,
                "self_sufficiency": 0.3158,
                "annual_grid_import_kwh": 6457.20,
            },
            {
                "optimization_type": "historical",
                "scenario": "best_self_sufficiency",
                "solar_peak_power_kw": 3.0,
                "battery_capacity_kwh": 5.0,
                "investment_cost_eur": 6000.0,
                "annual_savings_eur": 819.44,
                "payback_years": 7.32,
                "self_sufficiency": 0.4398,
                "annual_grid_import_kwh": 5286.51,
            },
            {
                "optimization_type": "forecast_based",
                "scenario": "best_payback",
                "solar_peak_power_kw": 2.0,
                "battery_capacity_kwh": 0.0,
                "investment_cost_eur": 2600.0,
                "annual_savings_eur": 551.64,
                "payback_years": 4.71,
                "self_sufficiency": 0.3046,
                "annual_grid_import_kwh": 6160.30,
            },
            {
                "optimization_type": "forecast_based",
                "scenario": "best_self_sufficiency",
                "solar_peak_power_kw": 3.0,
                "battery_capacity_kwh": 5.0,
                "investment_cost_eur": 6000.0,
                "annual_savings_eur": 865.36,
                "payback_years": 6.93,
                "self_sufficiency": 0.4996,
                "annual_grid_import_kwh": 4432.61,
            },
        ]
    )


def test_format_helpers():
    assert format_percent(0.3158) == "31.58%"
    assert format_years(5.11) == "5.11 years"
    assert format_eur(3500.0) == "3500.00 EUR"
    assert format_eur_per_year(684.83) == "684.83 EUR/year"
    assert format_kwh_per_year(6457.2) == "6457.20 kWh/year"


def test_get_scenario_returns_expected_row():
    comparison_df = build_sample_comparison_df()

    scenario = get_scenario(comparison_df, "forecast_based", "best_payback")

    assert scenario["optimization_type"] == "forecast_based"
    assert scenario["scenario"] == "best_payback"
    assert scenario["solar_peak_power_kw"] == 2.0
    assert scenario["battery_capacity_kwh"] == 0.0


def test_get_scenario_raises_error_when_missing():
    comparison_df = build_sample_comparison_df()

    with pytest.raises(ValueError):
        get_scenario(comparison_df, "historical", "missing_scenario")


def test_build_final_results_summary_contains_main_sections():
    comparison_df = build_sample_comparison_df()

    summary = build_final_results_summary(comparison_df)

    assert "# Final Results Summary" in summary
    assert "## Best historical economic scenario" in summary
    assert "## Best historical self-sufficiency scenario" in summary
    assert "## Best forecast-based economic scenario" in summary
    assert "## Best forecast-based self-sufficiency scenario" in summary
    assert "## Main conclusion" in summary


def test_build_final_results_summary_contains_key_values():
    comparison_df = build_sample_comparison_df()

    summary = build_final_results_summary(comparison_df)

    assert "3.00 kW" in summary
    assert "2.00 kW" in summary
    assert "5.00 kWh" in summary
    assert "3500.00 EUR" in summary
    assert "6000.00 EUR" in summary
    assert "684.83 EUR/year" in summary
    assert "865.36 EUR/year" in summary
    assert "31.58%" in summary
    assert "49.96%" in summary
