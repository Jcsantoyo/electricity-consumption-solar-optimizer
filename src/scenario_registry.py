from project_scenario import ProjectScenario


PROJECT_SCENARIOS = {
    "uci_omie_june_2026": ProjectScenario(
        name="uci_omie_june_2026",
        consumption_data_path=("data/processed/uci_consumption_omie_scenario.csv"),
        use_pvgis_solar_data=True,
        pvgis_solar_data_path=("data/raw/pvgis_hourly_linares_1kw_2020.csv"),
        price_mode="wholesale_hourly",
        tariff_profile_name=("spanish_2_0td_example"),
        hourly_price_data_path=("data/processed/omie_hourly_prices.csv"),
        allow_negative_hourly_prices=True,
        forecast_mode="backtest",
        forecast_test_size_ratio=0.20,
        random_seed=42,
    ),
    "uci_fixed_tariff": ProjectScenario(
        name="uci_fixed_tariff",
        consumption_data_path=("data/processed/uci_consumption_omie_scenario.csv"),
        use_pvgis_solar_data=True,
        pvgis_solar_data_path=("data/raw/pvgis_hourly_linares_1kw_2020.csv"),
        price_mode="fixed",
        tariff_profile_name="flat_price",
        hourly_price_data_path=None,
        allow_negative_hourly_prices=False,
        forecast_mode="backtest",
        forecast_test_size_ratio=0.20,
        random_seed=42,
    ),
}


DEFAULT_PROJECT_SCENARIO_NAME = "uci_omie_june_2026"


def get_project_scenario(
    scenario_name: str = DEFAULT_PROJECT_SCENARIO_NAME,
) -> ProjectScenario:
    try:
        scenario = PROJECT_SCENARIOS[scenario_name]
    except KeyError as error:
        available_scenarios = ", ".join(sorted(PROJECT_SCENARIOS))

        raise ValueError(
            f"Unknown project scenario: {scenario_name}. "
            f"Available scenarios: {available_scenarios}"
        ) from error

    scenario.validate()

    return scenario
