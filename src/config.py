import os

from financial_assumptions import (
    FinancialAssumptions,
)
from output_paths import build_scenario_output_paths
from scenario_registry import (
    DEFAULT_PROJECT_SCENARIO_NAME,
    get_project_scenario,
)


# Active reproducible project scenario
ACTIVE_PROJECT_SCENARIO_NAME = os.getenv(
    "PROJECT_SCENARIO",
    DEFAULT_PROJECT_SCENARIO_NAME,
)

ACTIVE_PROJECT_SCENARIO = get_project_scenario(ACTIVE_PROJECT_SCENARIO_NAME)

OUTPUT_PATHS = build_scenario_output_paths(ACTIVE_PROJECT_SCENARIO_NAME)


# Input files
CONSUMPTION_DATA_PATH = ACTIVE_PROJECT_SCENARIO.consumption_data_path


# Solar data source
USE_PVGIS_SOLAR_DATA = ACTIVE_PROJECT_SCENARIO.use_pvgis_solar_data

PVGIS_SOLAR_DATA_PATH = ACTIVE_PROJECT_SCENARIO.pvgis_solar_data_path


# Scenario-specific output files
GRID_SEARCH_RESULTS_PATH = OUTPUT_PATHS.grid_search_results

BEST_SCENARIOS_PATH = OUTPUT_PATHS.best_scenarios

SUMMARY_REPORT_PATH = OUTPUT_PATHS.summary_report

PAYBACK_PLOT_PATH = OUTPUT_PATHS.payback_plot

SELF_SUFFICIENCY_PLOT_PATH = OUTPUT_PATHS.self_sufficiency_plot

BEST_SCENARIOS_COMPARISON_PLOT_PATH = OUTPUT_PATHS.best_scenarios_comparison_plot

BEST_SCENARIO_TIMESERIES_PLOT_PATH = OUTPUT_PATHS.best_scenario_timeseries_plot

BEST_SCENARIO_TIMESERIES_PATH = OUTPUT_PATHS.best_scenario_timeseries

BEST_SCENARIO_BATTERY_STATE_PLOT_PATH = OUTPUT_PATHS.best_scenario_battery_state_plot

BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH = (
    OUTPUT_PATHS.best_scenario_cumulative_energy_plot
)

OUTPUTS_INDEX_PATH = OUTPUT_PATHS.outputs_index

RUN_MANIFEST_PATH = OUTPUT_PATHS.run_manifest


# Simulation settings
DAYS_PER_YEAR = 365


# Grid search parameters
SOLAR_PEAK_POWERS_KW = [
    0.5,
    1.0,
    1.5,
    2.0,
    3.0,
]

BATTERY_CAPACITIES_KWH = [
    0,
    0.5,
    1.0,
    2.0,
    3.0,
    5.0,
]


# Battery model parameters
BATTERY_EFFICIENCY = 0.90
MAX_CHARGE_POWER_KW = 1.0
MAX_DISCHARGE_POWER_KW = 1.0
INITIAL_BATTERY_STATE_KWH = 0.0


# Economic assumptions
FIXED_INSTALLATION_COST_EUR = 800.0
SOLAR_COST_EUR_PER_KW = 900.0
BATTERY_COST_EUR_PER_KWH = 500.0


# Financial assumptions
FINANCIAL_PROFILES = {
    "residential_standard": FinancialAssumptions(
        project_lifetime_years=25,
        discount_rate=0.05,
        annual_operating_cost_eur=100.0,
        annual_solar_degradation_rate=0.005,
        annual_electricity_price_growth_rate=0.02,
        annual_operating_cost_growth_rate=0.02,
    ),
}

ACTIVE_FINANCIAL_PROFILE_NAME = "residential_standard"


def get_active_financial_assumptions() -> FinancialAssumptions:
    try:
        return FINANCIAL_PROFILES[ACTIVE_FINANCIAL_PROFILE_NAME]
    except KeyError as error:
        available_profiles = ", ".join(sorted(FINANCIAL_PROFILES))

        raise ValueError(
            "Unknown active financial profile: "
            f"{ACTIVE_FINANCIAL_PROFILE_NAME}. "
            "Available profiles: "
            f"{available_profiles}"
        ) from error


# Tariff assumptions
#
# These values are illustrative and can be replaced
# with values from a real electricity contract.
TARIFF_PROFILES = {
    "flat_price": {
        "peak_price_eur_per_kwh": 0.20,
        "flat_price_eur_per_kwh": 0.20,
        "off_peak_price_eur_per_kwh": 0.20,
        "surplus_compensation_eur_per_kwh": 0.07,
        "contracted_power_kw": 4.6,
        "power_price_eur_per_kw_year": 35.0,
    },
    "spanish_2_0td_example": {
        "peak_price_eur_per_kwh": 0.25,
        "flat_price_eur_per_kwh": 0.18,
        "off_peak_price_eur_per_kwh": 0.12,
        "surplus_compensation_eur_per_kwh": 0.07,
        "contracted_power_kw": 4.6,
        "power_price_eur_per_kw_year": 35.0,
    },
}


# Active tariff profile
ACTIVE_TARIFF_PROFILE = ACTIVE_PROJECT_SCENARIO.tariff_profile_name


# Hourly electricity price data
USE_HOURLY_PRICE_DATA = ACTIVE_PROJECT_SCENARIO.uses_hourly_prices

HOURLY_PRICE_DATA_PATH = ACTIVE_PROJECT_SCENARIO.hourly_price_data_path

ALLOW_NEGATIVE_HOURLY_PRICES = ACTIVE_PROJECT_SCENARIO.allow_negative_hourly_prices


# Forecast settings
FORECAST_MODE = ACTIVE_PROJECT_SCENARIO.forecast_mode

FORECAST_TEST_SIZE_RATIO = ACTIVE_PROJECT_SCENARIO.forecast_test_size_ratio

RANDOM_SEED = ACTIVE_PROJECT_SCENARIO.random_seed


def get_active_tariff_profile() -> dict:
    try:
        return TARIFF_PROFILES[ACTIVE_TARIFF_PROFILE]
    except KeyError as error:
        available_profiles = ", ".join(sorted(TARIFF_PROFILES))

        raise ValueError(
            "Unknown active tariff profile: "
            f"{ACTIVE_TARIFF_PROFILE}. "
            "Available profiles: "
            f"{available_profiles}"
        ) from error
