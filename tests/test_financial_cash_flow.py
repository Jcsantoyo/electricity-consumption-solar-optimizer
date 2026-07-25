import pytest

from financial_cash_flow import (
    AnnualCashFlow,
    ReplacementCost,
    build_annual_cash_flows,
    build_projected_annual_cash_flows,
)


def test_annual_cash_flow_stores_values() -> None:
    cash_flow = AnnualCashFlow(
        year=1,
        energy_savings_eur=1000.0,
        operating_cost_eur=100.0,
        replacement_cost_eur=200.0,
        investment_cost_eur=0.0,
        net_cash_flow_eur=700.0,
    )

    assert cash_flow.year == 1
    assert cash_flow.energy_savings_eur == pytest.approx(1000.0)
    assert cash_flow.operating_cost_eur == pytest.approx(100.0)
    assert cash_flow.replacement_cost_eur == pytest.approx(200.0)
    assert cash_flow.investment_cost_eur == pytest.approx(0.0)
    assert cash_flow.net_cash_flow_eur == pytest.approx(700.0)


def test_annual_cash_flow_allows_negative_energy_savings() -> None:
    cash_flow = AnnualCashFlow(
        year=1,
        energy_savings_eur=-100.0,
        operating_cost_eur=20.0,
        replacement_cost_eur=0.0,
        investment_cost_eur=0.0,
        net_cash_flow_eur=-120.0,
    )

    assert cash_flow.energy_savings_eur == pytest.approx(-100.0)
    assert cash_flow.net_cash_flow_eur == pytest.approx(-120.0)


def test_annual_cash_flow_rejects_negative_year() -> None:
    with pytest.raises(
        ValueError,
        match="Cash flow year cannot be negative",
    ):
        AnnualCashFlow(
            year=-1,
            energy_savings_eur=1000.0,
            operating_cost_eur=0.0,
            replacement_cost_eur=0.0,
            investment_cost_eur=0.0,
            net_cash_flow_eur=1000.0,
        )


@pytest.mark.parametrize(
    (
        "operating_cost_eur",
        "replacement_cost_eur",
        "investment_cost_eur",
    ),
    [
        (-1.0, 0.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, -1.0),
    ],
)
def test_annual_cash_flow_rejects_negative_costs(
    operating_cost_eur: float,
    replacement_cost_eur: float,
    investment_cost_eur: float,
) -> None:
    net_cash_flow_eur = (
        1000.0 - operating_cost_eur - replacement_cost_eur - investment_cost_eur
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        AnnualCashFlow(
            year=1,
            energy_savings_eur=1000.0,
            operating_cost_eur=operating_cost_eur,
            replacement_cost_eur=replacement_cost_eur,
            investment_cost_eur=investment_cost_eur,
            net_cash_flow_eur=net_cash_flow_eur,
        )


def test_annual_cash_flow_rejects_inconsistent_net_cash_flow() -> None:
    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        AnnualCashFlow(
            year=1,
            energy_savings_eur=1000.0,
            operating_cost_eur=100.0,
            replacement_cost_eur=200.0,
            investment_cost_eur=0.0,
            net_cash_flow_eur=999.0,
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


def test_build_annual_cash_flows_creates_initial_investment() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        annual_energy_savings_eur=1000.0,
        project_lifetime_years=3,
    )

    initial_cash_flow = cash_flows[0]

    assert initial_cash_flow.year == 0
    assert initial_cash_flow.energy_savings_eur == pytest.approx(0.0)
    assert initial_cash_flow.operating_cost_eur == pytest.approx(0.0)
    assert initial_cash_flow.replacement_cost_eur == pytest.approx(0.0)
    assert initial_cash_flow.investment_cost_eur == pytest.approx(5000.0)
    assert initial_cash_flow.net_cash_flow_eur == pytest.approx(-5000.0)


def test_build_annual_cash_flows_creates_one_flow_per_project_year() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        annual_energy_savings_eur=1000.0,
        project_lifetime_years=3,
    )

    assert len(cash_flows) == 4
    assert [cash_flow.year for cash_flow in cash_flows] == [0, 1, 2, 3]


def test_build_annual_cash_flows_uses_constant_annual_values() -> None:
    cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        annual_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=100.0,
    )

    for cash_flow in cash_flows[1:]:
        assert cash_flow.energy_savings_eur == pytest.approx(1000.0)
        assert cash_flow.operating_cost_eur == pytest.approx(100.0)
        assert cash_flow.replacement_cost_eur == pytest.approx(0.0)
        assert cash_flow.investment_cost_eur == pytest.approx(0.0)
        assert cash_flow.net_cash_flow_eur == pytest.approx(900.0)


@pytest.mark.parametrize(
    (
        "initial_investment_cost_eur",
        "project_lifetime_years",
        "annual_operating_cost_eur",
    ),
    [
        (-1.0, 20, 0.0),
        (5000.0, 0, 0.0),
        (5000.0, -1, 0.0),
        (5000.0, 20, -1.0),
    ],
)
def test_build_annual_cash_flows_rejects_invalid_values(
    initial_investment_cost_eur: float,
    project_lifetime_years: int,
    annual_operating_cost_eur: float,
) -> None:
    with pytest.raises(ValueError):
        build_annual_cash_flows(
            initial_investment_cost_eur=initial_investment_cost_eur,
            annual_energy_savings_eur=1000.0,
            project_lifetime_years=project_lifetime_years,
            annual_operating_cost_eur=annual_operating_cost_eur,
        )


def test_projected_cash_flows_keep_first_year_savings_unchanged() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_solar_degradation_rate=0.01,
        annual_electricity_price_growth_rate=0.03,
    )

    assert cash_flows[1].energy_savings_eur == pytest.approx(1000.0)


def test_projected_cash_flows_apply_degradation_and_price_growth() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_solar_degradation_rate=0.01,
        annual_electricity_price_growth_rate=0.03,
    )

    expected_year_2_savings = 1000.0 * 0.99 * 1.03
    expected_year_3_savings = 1000.0 * (0.99**2) * (1.03**2)

    assert cash_flows[2].energy_savings_eur == pytest.approx(expected_year_2_savings)
    assert cash_flows[3].energy_savings_eur == pytest.approx(expected_year_3_savings)


def test_projected_cash_flows_apply_operating_cost_growth() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
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
        initial_investment_cost_eur=5000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=2,
        annual_operating_cost_eur=100.0,
        annual_operating_cost_growth_rate=0.02,
    )

    assert cash_flows[1].net_cash_flow_eur == pytest.approx(900.0)
    assert cash_flows[2].net_cash_flow_eur == pytest.approx(898.0)


def test_projected_cash_flows_match_constant_builder_with_zero_rates() -> None:
    constant_cash_flows = build_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        annual_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=100.0,
    )

    projected_cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        annual_operating_cost_eur=100.0,
        annual_solar_degradation_rate=0.0,
        annual_electricity_price_growth_rate=0.0,
        annual_operating_cost_growth_rate=0.0,
    )

    assert projected_cash_flows == constant_cash_flows


@pytest.mark.parametrize(
    (
        "initial_investment_cost_eur",
        "project_lifetime_years",
        "annual_operating_cost_eur",
    ),
    [
        (-1.0, 20, 0.0),
        (5000.0, 0, 0.0),
        (5000.0, -1, 0.0),
        (5000.0, 20, -1.0),
    ],
)
def test_projected_cash_flows_reject_invalid_base_values(
    initial_investment_cost_eur: float,
    project_lifetime_years: int,
    annual_operating_cost_eur: float,
) -> None:
    with pytest.raises(ValueError):
        build_projected_annual_cash_flows(
            initial_investment_cost_eur=initial_investment_cost_eur,
            first_year_energy_savings_eur=1000.0,
            project_lifetime_years=project_lifetime_years,
            annual_operating_cost_eur=annual_operating_cost_eur,
        )


@pytest.mark.parametrize(
    "solar_degradation_rate",
    [
        -1.0,
        -1.5,
        -0.001,
        1.0,
        1.5,
    ],
)
def test_projected_cash_flows_reject_invalid_solar_degradation_rate(
    solar_degradation_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="between zero and one",
    ):
        build_projected_annual_cash_flows(
            initial_investment_cost_eur=5000.0,
            first_year_energy_savings_eur=800.0,
            project_lifetime_years=20,
            annual_solar_degradation_rate=solar_degradation_rate,
        )


@pytest.mark.parametrize(
    (
        "electricity_price_growth_rate",
        "operating_cost_growth_rate",
    ),
    [
        (-1.0, 0.0),
        (-1.5, 0.0),
        (0.0, -1.0),
        (0.0, -1.5),
    ],
)
def test_projected_cash_flows_reject_invalid_growth_rates(
    electricity_price_growth_rate: float,
    operating_cost_growth_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="must be greater than -1",
    ):
        build_projected_annual_cash_flows(
            initial_investment_cost_eur=5000.0,
            first_year_energy_savings_eur=800.0,
            project_lifetime_years=20,
            annual_electricity_price_growth_rate=(electricity_price_growth_rate),
            annual_operating_cost_growth_rate=(operating_cost_growth_rate),
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


def test_projected_cash_flows_support_multiple_replacement_years() -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=6000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=15,
        replacement_costs=[
            ReplacementCost(
                year=8,
                cost_eur=1500.0,
            ),
            ReplacementCost(
                year=12,
                cost_eur=900.0,
            ),
        ],
    )

    assert cash_flows[8].replacement_cost_eur == pytest.approx(1500.0)
    assert cash_flows[12].replacement_cost_eur == pytest.approx(900.0)


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


@pytest.mark.parametrize(
    "replacement_costs",
    [
        None,
        [],
    ],
)
def test_projected_cash_flows_without_replacements_have_zero_replacement_costs(
    replacement_costs: list[ReplacementCost] | None,
) -> None:
    cash_flows = build_projected_annual_cash_flows(
        initial_investment_cost_eur=5000.0,
        first_year_energy_savings_eur=1000.0,
        project_lifetime_years=3,
        replacement_costs=replacement_costs,
    )

    assert all(
        cash_flow.replacement_cost_eur == pytest.approx(0.0) for cash_flow in cash_flows
    )
