import pytest

from financial_cash_flow import (
    AnnualCashFlow,
    ReplacementCost,
    build_annual_cash_flows,
    build_projected_annual_cash_flows,
)


def test_annual_cash_flow_stores_components() -> None:
    cash_flow = AnnualCashFlow(
        year=1,
        energy_savings_eur=900.0,
        operating_cost_eur=50.0,
        replacement_cost_eur=0.0,
        investment_cost_eur=0.0,
        net_cash_flow_eur=850.0,
    )

    assert cash_flow.year == 1
    assert cash_flow.energy_savings_eur == pytest.approx(900.0)
    assert cash_flow.operating_cost_eur == pytest.approx(50.0)
    assert cash_flow.net_cash_flow_eur == pytest.approx(850.0)


def test_annual_cash_flow_rejects_negative_year() -> None:
    with pytest.raises(
        ValueError,
        match="year cannot be negative",
    ):
        AnnualCashFlow(
            year=-1,
            energy_savings_eur=900.0,
            operating_cost_eur=50.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=0.0,
            net_cash_flow_eur=850.0,
        )


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("operating_cost_eur", -1.0),
        ("replacement_cost_eur", -1.0),
        ("investment_cost_eur", -1.0),
    ],
)
def test_annual_cash_flow_rejects_negative_costs(
    field_name: str,
    field_value: float,
) -> None:
    values = {
        "year": 1,
        "energy_savings_eur": 900.0,
        "operating_cost_eur": 50.0,
        "replacement_cost_eur": 0.0,
        "investment_cost_eur": 0.0,
        "net_cash_flow_eur": 850.0,
    }

    values[field_name] = field_value

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        AnnualCashFlow(**values)


def test_annual_cash_flow_rejects_inconsistent_total() -> None:
    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        AnnualCashFlow(
            year=1,
            energy_savings_eur=900.0,
            operating_cost_eur=50.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=0.0,
            net_cash_flow_eur=500.0,
        )


def test_build_annual_cash_flows_includes_initial_investment() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        annual_energy_savings_eur=900.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=50.0,
    )

    assert len(cash_flows) == 4

    initial_cash_flow = cash_flows[0]

    assert initial_cash_flow.year == 0
    assert initial_cash_flow.investment_cost_eur == pytest.approx(6000.0)
    assert initial_cash_flow.net_cash_flow_eur == pytest.approx(-6000.0)


def test_build_annual_cash_flows_calculates_operating_years() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        annual_energy_savings_eur=900.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=50.0,
    )

    for year, cash_flow in enumerate(
        cash_flows[1:],
        start=1,
    ):
        assert cash_flow.year == year
        assert cash_flow.energy_savings_eur == pytest.approx(900.0)
        assert cash_flow.operating_cost_eur == pytest.approx(50.0)
        assert cash_flow.net_cash_flow_eur == pytest.approx(850.0)


def test_build_annual_cash_flows_allows_negative_savings() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=1000.0,
        annual_energy_savings_eur=-100.0,
        project_lifetime_years=1,
        annual_operating_cost_eur=20.0,
    )

    assert cash_flows[1].net_cash_flow_eur == pytest.approx(-120.0)


@pytest.mark.parametrize(
    (
        "initial_investment_cost_eur",
        "project_lifetime_years",
        "annual_operating_cost_eur",
    ),
    [
        (-1.0, 20, 50.0),
        (6000.0, 0, 50.0),
        (6000.0, -1, 50.0),
        (6000.0, 20, -1.0),
    ],
)
def test_build_annual_cash_flows_rejects_invalid_parameters(
    initial_investment_cost_eur: float,
    project_lifetime_years: int,
    annual_operating_cost_eur: float,
) -> None:
    with pytest.raises(ValueError):
        build_annual_cash_flows(
            initial_investment_cost_eur=(initial_investment_cost_eur),
            annual_energy_savings_eur=900.0,
            project_lifetime_years=(project_lifetime_years),
            annual_operating_cost_eur=(annual_operating_cost_eur),
        )


def test_projected_cash_flows_keep_first_year_savings() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_solar_degradation_rate=0.01,
        annual_electricity_price_growth_rate=0.03,
    )

    assert cash_flows[1].energy_savings_eur == pytest.approx(1000.0)


def test_projected_cash_flows_apply_degradation_and_price_growth() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_solar_degradation_rate=0.01,
        annual_electricity_price_growth_rate=0.03,
    )

    assert cash_flows[2].energy_savings_eur == pytest.approx(1000.0 * 0.99 * 1.03)

    assert cash_flows[3].energy_savings_eur == pytest.approx(
        1000.0 * (0.99**2) * (1.03**2)
    )


def test_projected_cash_flows_apply_operating_cost_growth() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=100.0,
        annual_operating_cost_growth_rate=0.02,
    )

    assert cash_flows[1].operating_cost_eur == pytest.approx(100.0)

    assert cash_flows[2].operating_cost_eur == pytest.approx(102.0)

    assert cash_flows[3].operating_cost_eur == pytest.approx(104.04)


def test_projected_cash_flows_calculate_net_cash_flow() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=2,
        annual_operating_cost_eur=100.0,
        annual_solar_degradation_rate=0.01,
        annual_electricity_price_growth_rate=0.03,
        annual_operating_cost_growth_rate=0.02,
    )

    second_year = cash_flows[2]

    expected_savings = 1000.0 * 0.99 * 1.03
    expected_operating_cost = 100.0 * 1.02

    assert second_year.net_cash_flow_eur == pytest.approx(
        expected_savings - expected_operating_cost
    )


def test_projected_cash_flows_match_constant_model_with_zero_rates() -> None:
    constant_cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        annual_energy_savings_eur=900.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=50.0,
    )

    projected_cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=900.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=50.0,
    )

    assert projected_cash_flows == (constant_cash_flows)


@pytest.mark.parametrize(
    (
        "solar_degradation_rate",
        "electricity_price_growth_rate",
        "operating_cost_growth_rate",
    ),
    [
        (-1.0, 0.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, -1.0),
        (-1.5, 0.0, 0.0),
    ],
)
def test_projected_cash_flows_reject_invalid_rates(
    solar_degradation_rate: float,
    electricity_price_growth_rate: float,
    operating_cost_growth_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="must be greater than -1",
    ):
        build_projected_annual_cash_flows(
            initial_investment_cost_eur=6000.0,
            first_year_energy_savings_eur=900.0,
            project_lifetime_years=20,
            annual_solar_degradation_rate=(solar_degradation_rate),
            annual_electricity_price_growth_rate=(electricity_price_growth_rate),
            annual_operating_cost_growth_rate=(operating_cost_growth_rate),
        )


def test_replacement_cost_stores_values() -> None:
    replacement = ReplacementCost(
        year=10,
        cost_eur=2500.0,
    )

    assert replacement.year == 10
    assert replacement.cost_eur == pytest.approx(2500.0)


@pytest.mark.parametrize(
    ("year", "cost_eur"),
    [
        (0, 1000.0),
        (-1, 1000.0),
        (10, -1.0),
    ],
)
def test_replacement_cost_rejects_invalid_values(
    year: int,
    cost_eur: float,
) -> None:
    with pytest.raises(ValueError):
        ReplacementCost(
            year=year,
            cost_eur=cost_eur,
        )


def test_projected_cash_flows_apply_replacement_cost() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=12,
        annual_operating_cost_eur=100.0,
        replacement_costs=[
            ReplacementCost(
                year=10,
                cost_eur=2500.0,
            )
        ],
    )

    replacement_year = cash_flows[10]

    assert replacement_year.replacement_cost_eur == pytest.approx(2500.0)

    assert replacement_year.net_cash_flow_eur == pytest.approx(1000.0 - 100.0 - 2500.0)


def test_projected_cash_flows_combine_replacements_in_same_year() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=12,
        replacement_costs=[
            ReplacementCost(
                year=10,
                cost_eur=2000.0,
            ),
            ReplacementCost(
                year=10,
                cost_eur=800.0,
            ),
        ],
    )

    assert cash_flows[10].replacement_cost_eur == pytest.approx(2800.0)

    assert cash_flows[10].net_cash_flow_eur == pytest.approx(-1800.0)


def test_projected_cash_flows_reject_replacement_after_project_lifetime() -> None:
    with pytest.raises(
        ValueError,
        match="cannot exceed project lifetime",
    ):
        build_projected_annual_cash_flows(
            initial_investment_cost_eur=6000.0,
            first_year_energy_savings_eur=1000.0,
            project_lifetime_years=20,
            replacement_costs=[
                ReplacementCost(
                    year=21,
                    cost_eur=2500.0,
                )
            ],
        )
