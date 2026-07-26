import pytest

from financial_assumptions import FinancialAssumptions


def build_valid_financial_assumptions(
    **overrides: object,
) -> FinancialAssumptions:
    values: dict[str, object] = {
        "project_lifetime_years": 25,
        "discount_rate": 0.05,
        "annual_operating_cost_eur": 100.0,
        "annual_solar_degradation_rate": 0.005,
        "annual_electricity_price_growth_rate": 0.02,
        "annual_operating_cost_growth_rate": 0.02,
        "battery_replacement_year": 12,
        "battery_replacement_cost_fraction": 0.70,
    }

    values.update(overrides)

    return FinancialAssumptions(**values)


def test_financial_assumptions_stores_values() -> None:
    assumptions = build_valid_financial_assumptions()

    assert assumptions.project_lifetime_years == 25
    assert assumptions.discount_rate == pytest.approx(0.05)
    assert assumptions.annual_operating_cost_eur == pytest.approx(100.0)
    assert assumptions.annual_solar_degradation_rate == pytest.approx(0.005)
    assert assumptions.annual_electricity_price_growth_rate == pytest.approx(0.02)
    assert assumptions.annual_operating_cost_growth_rate == pytest.approx(0.02)
    assert assumptions.battery_replacement_year == 12
    assert assumptions.battery_replacement_cost_fraction == pytest.approx(0.70)


def test_financial_assumptions_allows_no_battery_replacement() -> None:
    assumptions = build_valid_financial_assumptions(
        battery_replacement_year=None,
    )

    assert assumptions.battery_replacement_year is None


@pytest.mark.parametrize(
    "project_lifetime_years",
    [
        0,
        -1,
    ],
)
def test_financial_assumptions_rejects_invalid_project_lifetime(
    project_lifetime_years: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="Project lifetime must be greater than zero",
    ):
        build_valid_financial_assumptions(
            project_lifetime_years=project_lifetime_years,
        )


def test_financial_assumptions_rejects_negative_discount_rate() -> None:
    with pytest.raises(
        ValueError,
        match="Discount rate cannot be negative",
    ):
        build_valid_financial_assumptions(
            discount_rate=-0.01,
        )


def test_financial_assumptions_rejects_negative_operating_cost() -> None:
    with pytest.raises(
        ValueError,
        match="Annual operating cost cannot be negative",
    ):
        build_valid_financial_assumptions(
            annual_operating_cost_eur=-1.0,
        )


@pytest.mark.parametrize(
    "solar_degradation_rate",
    [
        -0.001,
        -1.0,
        1.0,
        1.5,
    ],
)
def test_financial_assumptions_rejects_invalid_solar_degradation(
    solar_degradation_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="between zero and one",
    ):
        build_valid_financial_assumptions(
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
def test_financial_assumptions_rejects_invalid_growth_rates(
    electricity_price_growth_rate: float,
    operating_cost_growth_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="must be greater than -1",
    ):
        build_valid_financial_assumptions(
            annual_electricity_price_growth_rate=(electricity_price_growth_rate),
            annual_operating_cost_growth_rate=(operating_cost_growth_rate),
        )


@pytest.mark.parametrize(
    "replacement_year",
    [
        0,
        -1,
        26,
    ],
)
def test_financial_assumptions_rejects_invalid_replacement_year(
    replacement_year: int,
) -> None:
    with pytest.raises(ValueError):
        build_valid_financial_assumptions(
            battery_replacement_year=replacement_year,
        )


def test_financial_assumptions_accepts_replacement_at_project_end() -> None:
    assumptions = build_valid_financial_assumptions(
        battery_replacement_year=25,
    )

    assert assumptions.battery_replacement_year == 25


def test_financial_assumptions_rejects_negative_replacement_fraction() -> None:
    with pytest.raises(
        ValueError,
        match="fraction cannot be negative",
    ):
        build_valid_financial_assumptions(
            battery_replacement_cost_fraction=-0.1,
        )


def test_standard_financial_profile_is_valid() -> None:
    import config

    assumptions = config.get_active_financial_assumptions()

    assert isinstance(
        assumptions,
        FinancialAssumptions,
    )
    assert assumptions.project_lifetime_years == 25
    assert assumptions.discount_rate == pytest.approx(0.05)


def test_active_financial_assumptions_match_scenario_profile() -> None:
    import config

    assumptions = config.get_active_financial_assumptions()

    expected_assumptions = config.FINANCIAL_PROFILES[
        config.ACTIVE_PROJECT_SCENARIO.financial_profile_name
    ]

    assert assumptions == expected_assumptions


def test_financial_sensitivity_profiles_are_valid() -> None:
    import config

    assert set(config.FINANCIAL_SENSITIVITY_PROFILES) == {
        "pessimistic",
        "base",
        "optimistic",
    }

    assert all(
        isinstance(assumptions, FinancialAssumptions)
        for assumptions in config.FINANCIAL_SENSITIVITY_PROFILES.values()
    )


def test_get_financial_sensitivity_cases_preserves_expected_order() -> None:
    import config

    cases = config.get_financial_sensitivity_cases()

    assert [case.name for case in cases] == [
        "pessimistic",
        "base",
        "optimistic",
    ]


def test_base_sensitivity_profile_matches_standard_profile() -> None:
    import config

    assert (
        config.FINANCIAL_SENSITIVITY_PROFILES["base"]
        == config.FINANCIAL_PROFILES["residential_standard"]
    )


def test_sensitivity_profiles_have_expected_relative_assumptions() -> None:
    import config

    pessimistic = config.FINANCIAL_SENSITIVITY_PROFILES["pessimistic"]
    base = config.FINANCIAL_SENSITIVITY_PROFILES["base"]
    optimistic = config.FINANCIAL_SENSITIVITY_PROFILES["optimistic"]

    assert pessimistic.discount_rate > base.discount_rate
    assert base.discount_rate > optimistic.discount_rate

    assert (
        pessimistic.annual_electricity_price_growth_rate
        < base.annual_electricity_price_growth_rate
    )
    assert (
        base.annual_electricity_price_growth_rate
        < optimistic.annual_electricity_price_growth_rate
    )
