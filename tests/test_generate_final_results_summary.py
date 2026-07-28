import pandas as pd
import pytest


from scripts.generate_final_results_summary import (
    build_final_results_summary,
    build_financial_sensitivity_interpretation,
    build_financial_sensitivity_section,
    build_financial_sensitivity_table,
    build_optimization_conclusion,
    format_cost_breakdown_lines,
    format_eur,
    format_eur_per_year,
    format_extended_financial_lines,
    format_kwh_per_year,
    format_optional_percent,
    format_optional_years,
    format_percent,
    format_scenario_section,
    format_years,
    get_scenario,
    get_sensitivity_case,
    has_cost_breakdown,
    has_extended_financial_metrics,
    scenarios_use_same_configuration,
    validate_financial_sensitivity_dataframe,
    build_scenario_comparison_section,
    build_scenario_comparison_table,
    get_scenario_display_name,
    validate_scenario_comparison_dataframe,
    build_financial_scenario_sections,
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
                "battery_replacement_cost_eur": 0.0,
                "net_present_value_eur": 5000.0,
                "discounted_payback_years": 6.0,
                "internal_rate_of_return": 0.18,
                "self_sufficiency": 0.3158,
                "annual_grid_import_kwh": 6457.20,
            },
            {
                "optimization_type": "historical",
                "scenario": "best_net_present_value",
                "solar_peak_power_kw": 3.0,
                "battery_capacity_kwh": 0.0,
                "investment_cost_eur": 3500.0,
                "annual_savings_eur": 684.83,
                "payback_years": 5.11,
                "battery_replacement_cost_eur": 0.0,
                "net_present_value_eur": 5200.0,
                "discounted_payback_years": 5.8,
                "internal_rate_of_return": 0.19,
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
                "battery_replacement_cost_eur": 1750.0,
                "net_present_value_eur": 4200.0,
                "discounted_payback_years": 8.5,
                "internal_rate_of_return": None,
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
                "battery_replacement_cost_eur": 0.0,
                "net_present_value_eur": 6100.0,
                "discounted_payback_years": 5.4,
                "internal_rate_of_return": 0.21,
                "self_sufficiency": 0.3046,
                "annual_grid_import_kwh": 6160.30,
            },
            {
                "optimization_type": "forecast_based",
                "scenario": "best_net_present_value",
                "solar_peak_power_kw": 3.0,
                "battery_capacity_kwh": 3.0,
                "investment_cost_eur": 5000.0,
                "annual_savings_eur": 720.00,
                "payback_years": 6.94,
                "battery_replacement_cost_eur": 1050.0,
                "net_present_value_eur": 7100.0,
                "discounted_payback_years": 7.25,
                "internal_rate_of_return": 0.154,
                "self_sufficiency": 0.4020,
                "annual_grid_import_kwh": 5100.00,
            },
            {
                "optimization_type": "forecast_based",
                "scenario": "best_self_sufficiency",
                "solar_peak_power_kw": 3.0,
                "battery_capacity_kwh": 5.0,
                "investment_cost_eur": 6000.0,
                "annual_savings_eur": 865.36,
                "payback_years": 6.93,
                "battery_replacement_cost_eur": 1750.0,
                "net_present_value_eur": 6800.0,
                "discounted_payback_years": 8.10,
                "internal_rate_of_return": None,
                "self_sufficiency": 0.4996,
                "annual_grid_import_kwh": 4432.61,
            },
        ]
    )


def build_sample_sensitivity_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "case_name": "pessimistic",
                "discount_rate": 0.07,
                "annual_operating_cost_eur": 125.0,
                "annual_electricity_price_growth_rate": 0.00,
                "battery_replacement_cost_eur": 0.0,
                "net_present_value_eur": -2500.0,
                "discounted_payback_years": None,
                "internal_rate_of_return": None,
            },
            {
                "case_name": "base",
                "discount_rate": 0.05,
                "annual_operating_cost_eur": 100.0,
                "annual_electricity_price_growth_rate": 0.02,
                "battery_replacement_cost_eur": 0.0,
                "net_present_value_eur": -850.0,
                "discounted_payback_years": None,
                "internal_rate_of_return": 0.025,
            },
            {
                "case_name": "optimistic",
                "discount_rate": 0.03,
                "annual_operating_cost_eur": 75.0,
                "annual_electricity_price_growth_rate": 0.04,
                "battery_replacement_cost_eur": 0.0,
                "net_present_value_eur": 2100.0,
                "discounted_payback_years": 16.5,
                "internal_rate_of_return": 0.069,
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

    assert "## Best historical payback and net present value scenario" in summary

    assert "## Best historical self-sufficiency scenario" in summary

    assert "## Best forecast-based payback scenario" in summary

    assert "## Best forecast-based net present value scenario" in summary

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
    assert "Net present value" in summary
    assert "Discounted payback" in summary
    assert "Internal rate of return" in summary
    assert "Battery replacement cost" in summary


def test_has_cost_breakdown_detects_complete_breakdown() -> None:
    scenario = pd.Series(
        {
            "base_variable_energy_cost_eur": 100.0,
            "base_fixed_power_cost_eur": 10.0,
            "base_surplus_compensation_eur": 0.0,
            "base_net_cost_eur": 110.0,
            "scenario_variable_energy_cost_eur": 60.0,
            "scenario_fixed_power_cost_eur": 10.0,
            "scenario_surplus_compensation_eur": 5.0,
            "scenario_net_cost_eur": 65.0,
        }
    )

    assert has_cost_breakdown(scenario)


def test_has_cost_breakdown_rejects_incomplete_breakdown() -> None:
    scenario = pd.Series(
        {
            "base_net_cost_eur": 110.0,
            "scenario_net_cost_eur": 65.0,
        }
    )

    assert not has_cost_breakdown(scenario)


def test_format_cost_breakdown_lines_contains_cost_components() -> None:
    scenario = pd.Series(
        {
            "base_variable_energy_cost_eur": 100.0,
            "base_fixed_power_cost_eur": 10.0,
            "base_surplus_compensation_eur": 0.0,
            "base_net_cost_eur": 110.0,
            "scenario_variable_energy_cost_eur": 60.0,
            "scenario_fixed_power_cost_eur": 10.0,
            "scenario_surplus_compensation_eur": 5.0,
            "scenario_net_cost_eur": 65.0,
        }
    )

    lines = format_cost_breakdown_lines(scenario)

    text = "\n".join(lines)

    assert "Simulation-period electricity cost breakdown" in text
    assert "Baseline variable energy cost" in text
    assert "100.00 EUR" in text
    assert "Baseline net electricity cost" in text
    assert "110.00 EUR" in text
    assert "Optimized surplus compensation" in text
    assert "5.00 EUR" in text
    assert "Optimized net electricity cost" in text
    assert "65.00 EUR" in text


def test_format_scenario_section_supports_legacy_rows() -> None:
    scenario = build_sample_comparison_df().iloc[0]

    section = format_scenario_section(
        "Legacy scenario",
        scenario,
    )

    assert "## Legacy scenario" in section
    assert "3500.00 EUR" in section
    assert "Simulation-period electricity cost breakdown" not in section


def test_optional_financial_format_helpers() -> None:
    assert format_optional_years(None) == "Not achieved"
    assert format_optional_years(float("nan")) == "Not achieved"
    assert format_optional_years(16.5) == "16.50 years"

    assert format_optional_percent(None) == "Not available"
    assert format_optional_percent(float("nan")) == "Not available"
    assert format_optional_percent(0.069) == "6.90%"


def test_validate_financial_sensitivity_dataframe_accepts_valid_data() -> None:
    validate_financial_sensitivity_dataframe(build_sample_sensitivity_df())


def test_validate_financial_sensitivity_dataframe_rejects_missing_columns() -> None:
    dataframe = pd.DataFrame(
        {
            "case_name": ["base"],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        validate_financial_sensitivity_dataframe(dataframe)


def test_get_sensitivity_case_returns_expected_row() -> None:
    sensitivity_df = build_sample_sensitivity_df()

    result = get_sensitivity_case(
        sensitivity_df,
        "optimistic",
    )

    assert result["case_name"] == "optimistic"
    assert result["net_present_value_eur"] == pytest.approx(2100.0)


def test_get_sensitivity_case_rejects_missing_case() -> None:
    with pytest.raises(
        ValueError,
        match="case not found",
    ):
        get_sensitivity_case(
            build_sample_sensitivity_df(),
            "missing",
        )


def test_financial_sensitivity_table_contains_all_cases() -> None:
    table = build_financial_sensitivity_table(build_sample_sensitivity_df())

    assert "| pessimistic |" in table
    assert "| base |" in table
    assert "| optimistic |" in table
    assert "-2500.00 EUR" in table
    assert "2100.00 EUR" in table
    assert "Not achieved" in table
    assert "Not available" in table
    assert "6.90%" in table


def test_financial_sensitivity_interpretation_detects_optimistic_only_case() -> None:
    interpretation = build_financial_sensitivity_interpretation(
        build_sample_sensitivity_df()
    )

    assert "only achieves a positive NPV" in interpretation
    assert "depends strongly" in interpretation


def test_financial_sensitivity_section_contains_table_and_images() -> None:
    section = build_financial_sensitivity_section(
        sensitivity_df=build_sample_sensitivity_df(),
        npv_plot_path="../../images/example/npv.png",
        payback_plot_path="../../images/example/payback.png",
        irr_plot_path="../../images/example/irr.png",
    )

    assert "## Financial sensitivity analysis" in section
    assert "### Interpretation" in section
    assert "../../images/example/npv.png" in section
    assert "../../images/example/payback.png" in section
    assert "../../images/example/irr.png" in section


def test_final_summary_includes_financial_sensitivity_section() -> None:
    summary = build_final_results_summary(
        comparison_df=build_sample_comparison_df(),
        sensitivity_df=build_sample_sensitivity_df(),
        npv_plot_path="../../images/example/npv.png",
        payback_plot_path="../../images/example/payback.png",
        irr_plot_path="../../images/example/irr.png",
    )

    assert "## Financial sensitivity analysis" in summary
    assert "| pessimistic |" in summary
    assert "| base |" in summary
    assert "| optimistic |" in summary
    assert "only achieves a positive NPV" in summary


def test_scenarios_use_same_configuration_returns_true() -> None:
    first = pd.Series(
        {
            "solar_peak_power_kw": 3.0,
            "battery_capacity_kwh": 0.0,
        }
    )
    second = pd.Series(
        {
            "solar_peak_power_kw": 3.0,
            "battery_capacity_kwh": 0.0,
        }
    )

    assert scenarios_use_same_configuration(first, second)


def test_scenarios_use_same_configuration_returns_false() -> None:
    first = pd.Series(
        {
            "solar_peak_power_kw": 3.0,
            "battery_capacity_kwh": 0.0,
        }
    )
    second = pd.Series(
        {
            "solar_peak_power_kw": 3.0,
            "battery_capacity_kwh": 3.0,
        }
    )

    assert not scenarios_use_same_configuration(first, second)


def test_optimization_conclusion_detects_matching_historical_scenarios() -> None:
    comparison_df = build_sample_comparison_df()

    conclusion = build_optimization_conclusion(
        historical_payback=get_scenario(
            comparison_df,
            "historical",
            "best_payback",
        ),
        historical_npv=get_scenario(
            comparison_df,
            "historical",
            "best_net_present_value",
        ),
        historical_self_sufficiency=get_scenario(
            comparison_df,
            "historical",
            "best_self_sufficiency",
        ),
        forecast_payback=get_scenario(
            comparison_df,
            "forecast_based",
            "best_payback",
        ),
        forecast_npv=get_scenario(
            comparison_df,
            "forecast_based",
            "best_net_present_value",
        ),
        forecast_self_sufficiency=get_scenario(
            comparison_df,
            "forecast_based",
            "best_self_sufficiency",
        ),
    )

    assert (
        "historical optimization, the configuration with the "
        "shortest payback also provides the highest net present value" in conclusion
    )

    assert (
        "forecast-based optimization, the configuration with the "
        "shortest payback differs" in conclusion
    )

    assert "trade-off" in conclusion


def test_final_summary_contains_distinct_npv_scenario_values() -> None:
    summary = build_final_results_summary(build_sample_comparison_df())

    assert "## Best forecast-based net present value scenario" in summary
    assert "5000.00 EUR" in summary
    assert "3.00 kWh" in summary
    assert "720.00 EUR/year" in summary


def test_has_extended_financial_metrics_accepts_complete_row() -> None:
    scenario = pd.Series(
        {
            "battery_replacement_cost_eur": 1000.0,
            "net_present_value_eur": 5000.0,
            "discounted_payback_years": 7.5,
            "internal_rate_of_return": 0.15,
        }
    )

    assert has_extended_financial_metrics(scenario)


def test_has_extended_financial_metrics_rejects_incomplete_row() -> None:
    scenario = pd.Series(
        {
            "net_present_value_eur": 5000.0,
        }
    )

    assert not has_extended_financial_metrics(scenario)


def test_format_extended_financial_lines_contains_metrics() -> None:
    scenario = pd.Series(
        {
            "battery_replacement_cost_eur": 1050.0,
            "net_present_value_eur": 7100.0,
            "discounted_payback_years": 7.25,
            "internal_rate_of_return": 0.154,
        }
    )

    lines = format_extended_financial_lines(scenario)
    text = "\n".join(lines)

    assert "Battery replacement cost" in text
    assert "1050.00 EUR" in text
    assert "Net present value" in text
    assert "7100.00 EUR" in text
    assert "Discounted payback" in text
    assert "7.25 years" in text
    assert "Internal rate of return" in text
    assert "15.40%" in text


def test_format_extended_financial_lines_handles_missing_values() -> None:
    scenario = pd.Series(
        {
            "battery_replacement_cost_eur": 1750.0,
            "net_present_value_eur": -800.0,
            "discounted_payback_years": None,
            "internal_rate_of_return": None,
        }
    )

    text = "\n".join(format_extended_financial_lines(scenario))

    assert "Not achieved" in text
    assert "Not available" in text


def test_format_scenario_section_contains_extended_financial_metrics() -> None:
    scenario = build_sample_comparison_df().iloc[0]

    section = format_scenario_section(
        "Extended scenario",
        scenario,
    )

    assert "Simple payback" in section
    assert "Battery replacement cost" in section
    assert "Net present value" in section
    assert "Discounted payback" in section
    assert "Internal rate of return" in section


def test_get_scenario_display_name_returns_expected_name() -> None:
    result = get_scenario_display_name(
        "forecast_based",
        "best_net_present_value",
    )

    assert result == "Forecast · Best NPV"


def test_get_scenario_display_name_rejects_unknown_scenario() -> None:
    with pytest.raises(
        ValueError,
        match="Unknown scenario display name",
    ):
        get_scenario_display_name(
            "historical",
            "missing",
        )


def test_validate_scenario_comparison_dataframe_accepts_valid_data() -> None:
    validate_scenario_comparison_dataframe(build_sample_comparison_df())


def test_validate_scenario_comparison_dataframe_rejects_missing_columns() -> None:
    dataframe = pd.DataFrame(
        {
            "optimization_type": ["historical"],
            "scenario": ["best_payback"],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        validate_scenario_comparison_dataframe(dataframe)


def test_scenario_comparison_table_contains_six_scenarios() -> None:
    table = build_scenario_comparison_table(build_sample_comparison_df())

    assert table.count("Historical · Best payback") == 1
    assert table.count("Historical · Best NPV") == 1
    assert table.count("Historical · Best self-sufficiency") == 1
    assert table.count("Forecast · Best payback") == 1
    assert table.count("Forecast · Best NPV") == 1
    assert table.count("Forecast · Best self-sufficiency") == 1


def test_scenario_comparison_table_contains_key_metrics() -> None:
    table = build_scenario_comparison_table(build_sample_comparison_df())

    assert "5000.00 EUR" in table
    assert "7100.00 EUR" in table
    assert "7.25 years" in table
    assert "15.40%" in table
    assert "49.96%" in table
    assert "Not available" in table


def test_scenario_comparison_section_contains_heading_and_table() -> None:
    section = build_scenario_comparison_section(build_sample_comparison_df())

    assert "## Scenario comparison" in section
    assert "| Scenario | Solar | Battery |" in section
    assert "Historical · Best payback" in section
    assert "Forecast · Best NPV" in section


def test_final_summary_contains_scenario_comparison_table() -> None:
    summary = build_final_results_summary(build_sample_comparison_df())

    assert "## Scenario comparison" in summary
    assert "Historical · Best NPV" in summary
    assert "Forecast · Best NPV" in summary


def test_financial_scenario_sections_combines_matching_scenarios() -> None:
    comparison_df = build_sample_comparison_df()

    sections = build_financial_scenario_sections(
        optimization_label="historical",
        payback_scenario=get_scenario(
            comparison_df,
            "historical",
            "best_payback",
        ),
        npv_scenario=get_scenario(
            comparison_df,
            "historical",
            "best_net_present_value",
        ),
    )

    assert len(sections) == 1

    assert "Best historical payback and net present value scenario" in sections[0]


def test_financial_scenario_sections_keeps_distinct_scenarios() -> None:
    comparison_df = build_sample_comparison_df()

    sections = build_financial_scenario_sections(
        optimization_label="forecast-based",
        payback_scenario=get_scenario(
            comparison_df,
            "forecast_based",
            "best_payback",
        ),
        npv_scenario=get_scenario(
            comparison_df,
            "forecast_based",
            "best_net_present_value",
        ),
    )

    assert len(sections) == 2
    assert "Best forecast-based payback scenario" in sections[0]

    assert "Best forecast-based net present value scenario" in sections[1]


def test_final_summary_avoids_duplicate_historical_financial_block() -> None:
    summary = build_final_results_summary(build_sample_comparison_df())

    assert summary.count("Best historical payback and net present value scenario") == 1

    assert "Best historical payback scenario" not in summary

    assert "Best historical net present value scenario" not in summary


def test_final_summary_keeps_distinct_forecast_financial_blocks() -> None:
    summary = build_final_results_summary(build_sample_comparison_df())

    assert summary.count("Best forecast-based payback scenario") == 1

    assert summary.count("Best forecast-based net present value scenario") == 1
