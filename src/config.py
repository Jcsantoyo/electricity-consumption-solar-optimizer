from scenario_registry import get_project_scenario


# Active reproducible project scenario
ACTIVE_PROJECT_SCENARIO_NAME = "uci_omie_june_2026"

ACTIVE_PROJECT_SCENARIO = get_project_scenario(
    ACTIVE_PROJECT_SCENARIO_NAME
)


# Input files
CONSUMPTION_DATA_PATH = (
    ACTIVE_PROJECT_SCENARIO.consumption_data_path
)


# Solar data source
USE_PVGIS_SOLAR_DATA = (
    ACTIVE_PROJECT_SCENARIO.use_pvgis_solar_data
)

PVGIS_SOLAR_DATA_PATH = (
    ACTIVE_PROJECT_SCENARIO.pvgis_solar_data_path
)


# Output files
GRID_SEARCH_RESULTS_PATH = "reports/grid_search_results.csv"
BEST_SCENARIOS_PATH = "reports/best_scenarios.csv"
SUMMARY_REPORT_PATH = "reports/summary.txt"

PAYBACK_PLOT_PATH = "images/main_payback_grid_search.png"
SELF_SUFFICIENCY_PLOT_PATH = (
    "images/main_self_sufficiency_grid_search.png"
)
BEST_SCENARIOS_COMPARISON_PLOT_PATH = (
    "images/best_scenarios_comparison.png"
)
BEST_SCENARIO_TIMESERIES_PLOT_PATH = (
    "images/best_scenario_timeseries.png"
)
BEST_SCENARIO_TIMESERIES_PATH = (
    "reports/best_scenario_timeseries.csv"
)
BEST_SCENARIO_BATTERY_STATE_PLOT_PATH = (
    "images/best_scenario_battery_state.png"
)
BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH = (
    "images/best_scenario_cumulative_energy.png"
)
OUTPUTS_INDEX_PATH = "reports/outputs_index.md"

RUN_MANIFEST_PATH = "reports/run_manifest.json"


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


# Tariff assumptions
#
# These values are illustrative and can be replaced with values
# from a real electricity contract.

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
ACTIVE_TARIFF_PROFILE = (
    ACTIVE_PROJECT_SCENARIO.tariff_profile_name
)


# Hourly electricity price data
USE_HOURLY_PRICE_DATA = (
    ACTIVE_PROJECT_SCENARIO.uses_hourly_prices
)

HOURLY_PRICE_DATA_PATH = (
    ACTIVE_PROJECT_SCENARIO.hourly_price_data_path
)

ALLOW_NEGATIVE_HOURLY_PRICES = (
    ACTIVE_PROJECT_SCENARIO.allow_negative_hourly_prices
)


# Forecast settings
FORECAST_MODE = (
    ACTIVE_PROJECT_SCENARIO.forecast_mode
)

FORECAST_TEST_SIZE_RATIO = (
    ACTIVE_PROJECT_SCENARIO.forecast_test_size_ratio
)

RANDOM_SEED = (
    ACTIVE_PROJECT_SCENARIO.random_seed
)


def get_active_tariff_profile() -> dict:
    try:
        return TARIFF_PROFILES[
            ACTIVE_TARIFF_PROFILE
        ]
    except KeyError as error:
        available_profiles = ", ".join(
            sorted(TARIFF_PROFILES)
        )

        raise ValueError(
            "Unknown active tariff profile: "
            f"{ACTIVE_TARIFF_PROFILE}. "
            "Available profiles: "
            f"{available_profiles}"
        ) from error