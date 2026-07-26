import pytest

from financial_assumptions import FinancialAssumptions
from financial_sensitivity import (
    FINANCIAL_SENSITIVITY_COLUMNS,
    FinancialSensitivityCase,
    build_sensitivity_replacement_costs,
    calculate_battery_replacement_cost,
    evaluate_financial_sensitivity_case,
    financial_sensitivity_results_to_dataframe,
    run_financial_sensitivity_analysis,
)


def build_assumptions(
    *,
    discount_rate: float = 0.05,
    electricity_price_growth_rate: float = 0.02,
    replacement_year: int | None = 10,
    replacement_cost_fraction: float = 0.70,
) -> FinancialAssumptions:
    return FinancialAssumptions(
        project_lifetime_years=20,
        discount_rate=discount_rate,
        annual_operating_cost_eur=100.0,
        annual_solar_degradation_rate=0.005,
        annual_electricity_price_growth_rate=(electricity_price_growth_rate),
        annual_operating_cost_growth_rate=0.02,
        battery_replacement_year=replacement_year,
        battery_replacement_cost_fraction=(replacement_cost_fraction),
    )


def test_financial_sensitivity_case_stores_values() -> None:
    assumptions = build_assumptions()

    case = FinancialSensitivityCase(
        name="base",
        assumptions=assumptions,
    )

    assert case.name == "base"
    assert case.assumptions == assumptions


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "   ",
    ],
)
def test_financial_sensitivity_case_rejects_empty_name(
    name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):
        FinancialSensitivityCase(
            name=name,
            assumptions=build_assumptions(),
        )


def test_calculate_battery_replacement_cost() -> None:
    replacement_cost = calculate_battery_replacement_cost(
        battery_capacity_kwh=5.0,
        battery_cost_per_kwh=600.0,
        replacement_cost_fraction=0.70,
    )

    assert replacement_cost == pytest.approx(2100.0)


@pytest.mark.parametrize(
    (
        "battery_capacity_kwh",
        "battery_cost_per_kwh",
        "replacement_cost_fraction",
    ),
    [
        (-1.0, 600.0, 0.70),
        (5.0, -1.0, 0.70),
        (5.0, 600.0, -0.01),
    ],
)
def test_calculate_battery_replacement_cost_rejects_negative_values(
    battery_capacity_kwh: float,
    battery_cost_per_kwh: float,
    replacement_cost_fraction: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        calculate_battery_replacement_cost(
            battery_capacity_kwh=battery_capacity_kwh,
            battery_cost_per_kwh=battery_cost_per_kwh,
            replacement_cost_fraction=replacement_cost_fraction,
        )


def test_build_sensitivity_replacement_costs_creates_replacement() -> None:
    assumptions = build_assumptions(
        replacement_year=10,
        replacement_cost_fraction=0.70,
    )

    replacements, replacement_cost_eur = build_sensitivity_replacement_costs(
        battery_capacity_kwh=5.0,
        battery_cost_per_kwh=600.0,
        assumptions=assumptions,
    )

    assert len(replacements) == 1
    assert replacements[0].year == 10
    assert replacements[0].cost_eur == pytest.approx(2100.0)
    assert replacement_cost_eur == pytest.approx(2100.0)


def test_build_sensitivity_replacement_costs_skips_zero_capacity() -> None:
    replacements, replacement_cost_eur = build_sensitivity_replacement_costs(
        battery_capacity_kwh=0.0,
        battery_cost_per_kwh=600.0,
        assumptions=build_assumptions(),
    )

    assert replacements == []
    assert replacement_cost_eur == pytest.approx(0.0)


def test_build_sensitivity_replacement_costs_skips_missing_year() -> None:
    replacements, replacement_cost_eur = build_sensitivity_replacement_costs(
        battery_capacity_kwh=5.0,
        battery_cost_per_kwh=600.0,
        assumptions=build_assumptions(
            replacement_year=None,
        ),
    )

    assert replacements == []
    assert replacement_cost_eur == pytest.approx(0.0)


def test_evaluate_financial_sensitivity_case_returns_metrics() -> None:
    result = evaluate_financial_sensitivity_case(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=900.0,
        battery_capacity_kwh=5.0,
        battery_cost_per_kwh=600.0,
        case=FinancialSensitivityCase(
            name="base",
            assumptions=build_assumptions(),
        ),
    )

    assert result.case_name == "base"
    assert result.project_lifetime_years == 20
    assert result.discount_rate == pytest.approx(0.05)
    assert result.battery_replacement_year == 10
    assert result.battery_replacement_cost_eur == pytest.approx(2100.0)
    assert isinstance(result.net_present_value_eur, float)


def test_evaluate_case_without_battery_has_no_replacement_cost() -> None:
    result = evaluate_financial_sensitivity_case(
        initial_investment_cost_eur=4500.0,
        first_year_energy_savings_eur=800.0,
        battery_capacity_kwh=0.0,
        battery_cost_per_kwh=600.0,
        case=FinancialSensitivityCase(
            name="solar-only",
            assumptions=build_assumptions(),
        ),
    )

    assert result.battery_replacement_cost_eur == pytest.approx(0.0)


def test_evaluate_case_rejects_negative_initial_investment() -> None:
    with pytest.raises(
        ValueError,
        match="Initial investment cost cannot be negative",
    ):
        evaluate_financial_sensitivity_case(
            initial_investment_cost_eur=-1.0,
            first_year_energy_savings_eur=800.0,
            battery_capacity_kwh=0.0,
            battery_cost_per_kwh=600.0,
            case=FinancialSensitivityCase(
                name="base",
                assumptions=build_assumptions(),
            ),
        )


def test_run_financial_sensitivity_analysis_preserves_case_order() -> None:
    cases = [
        FinancialSensitivityCase(
            name="pessimistic",
            assumptions=build_assumptions(
                discount_rate=0.07,
                electricity_price_growth_rate=0.00,
            ),
        ),
        FinancialSensitivityCase(
            name="base",
            assumptions=build_assumptions(
                discount_rate=0.05,
                electricity_price_growth_rate=0.02,
            ),
        ),
        FinancialSensitivityCase(
            name="optimistic",
            assumptions=build_assumptions(
                discount_rate=0.03,
                electricity_price_growth_rate=0.04,
            ),
        ),
    ]

    results = run_financial_sensitivity_analysis(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=900.0,
        battery_capacity_kwh=5.0,
        battery_cost_per_kwh=600.0,
        cases=cases,
    )

    assert [result.case_name for result in results] == [
        "pessimistic",
        "base",
        "optimistic",
    ]


def test_more_favourable_case_has_higher_npv() -> None:
    cases = [
        FinancialSensitivityCase(
            name="pessimistic",
            assumptions=build_assumptions(
                discount_rate=0.08,
                electricity_price_growth_rate=0.00,
            ),
        ),
        FinancialSensitivityCase(
            name="optimistic",
            assumptions=build_assumptions(
                discount_rate=0.03,
                electricity_price_growth_rate=0.04,
            ),
        ),
    ]

    results = run_financial_sensitivity_analysis(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=900.0,
        battery_capacity_kwh=0.0,
        battery_cost_per_kwh=600.0,
        cases=cases,
    )

    pessimistic_result = results[0]
    optimistic_result = results[1]

    assert (
        optimistic_result.net_present_value_eur
        > pessimistic_result.net_present_value_eur
    )


def test_run_financial_sensitivity_analysis_rejects_empty_cases() -> None:
    with pytest.raises(
        ValueError,
        match="at least one case",
    ):
        run_financial_sensitivity_analysis(
            initial_investment_cost_eur=6000.0,
            first_year_energy_savings_eur=900.0,
            battery_capacity_kwh=5.0,
            battery_cost_per_kwh=600.0,
            cases=[],
        )


def test_run_financial_sensitivity_analysis_rejects_duplicate_names() -> None:
    cases = [
        FinancialSensitivityCase(
            name="base",
            assumptions=build_assumptions(),
        ),
        FinancialSensitivityCase(
            name="base",
            assumptions=build_assumptions(
                discount_rate=0.06,
            ),
        ),
    ]

    with pytest.raises(
        ValueError,
        match="names must be unique",
    ):
        run_financial_sensitivity_analysis(
            initial_investment_cost_eur=6000.0,
            first_year_energy_savings_eur=900.0,
            battery_capacity_kwh=5.0,
            battery_cost_per_kwh=600.0,
            cases=cases,
        )


def test_results_to_dataframe_preserves_columns_and_values() -> None:
    results = run_financial_sensitivity_analysis(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=900.0,
        battery_capacity_kwh=5.0,
        battery_cost_per_kwh=600.0,
        cases=[
            FinancialSensitivityCase(
                name="base",
                assumptions=build_assumptions(),
            )
        ],
    )

    dataframe = financial_sensitivity_results_to_dataframe(results)

    assert dataframe.columns.tolist() == FINANCIAL_SENSITIVITY_COLUMNS
    assert len(dataframe) == 1
    assert dataframe.loc[0, "case_name"] == "base"
    assert dataframe.loc[0, "discount_rate"] == pytest.approx(0.05)
    assert dataframe.loc[
        0,
        "battery_replacement_cost_eur",
    ] == pytest.approx(2100.0)


def test_results_to_dataframe_preserves_result_order() -> None:
    cases = [
        FinancialSensitivityCase(
            name="pessimistic",
            assumptions=build_assumptions(
                discount_rate=0.07,
            ),
        ),
        FinancialSensitivityCase(
            name="base",
            assumptions=build_assumptions(
                discount_rate=0.05,
            ),
        ),
        FinancialSensitivityCase(
            name="optimistic",
            assumptions=build_assumptions(
                discount_rate=0.03,
            ),
        ),
    ]

    results = run_financial_sensitivity_analysis(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=900.0,
        battery_capacity_kwh=0.0,
        battery_cost_per_kwh=600.0,
        cases=cases,
    )

    dataframe = financial_sensitivity_results_to_dataframe(results)

    assert dataframe["case_name"].tolist() == [
        "pessimistic",
        "base",
        "optimistic",
    ]


def test_results_to_dataframe_supports_empty_results() -> None:
    dataframe = financial_sensitivity_results_to_dataframe([])

    assert dataframe.empty
    assert dataframe.columns.tolist() == FINANCIAL_SENSITIVITY_COLUMNS
