# Input files
CONSUMPTION_DATA_PATH = "data/processed/uci_household_power_hourly.csv"

# Solar data source
USE_PVGIS_SOLAR_DATA = True
PVGIS_SOLAR_DATA_PATH = "data/raw/pvgis_hourly_linares_1kw_2020.csv"

# Output files
GRID_SEARCH_RESULTS_PATH = "reports/grid_search_results.csv"
BEST_SCENARIOS_PATH = "reports/best_scenarios.csv"
SUMMARY_REPORT_PATH = "reports/summary.txt"

PAYBACK_PLOT_PATH = "images/main_payback_grid_search.png"
SELF_SUFFICIENCY_PLOT_PATH = "images/main_self_sufficency_grid_search.png"
BEST_SCENARIOS_COMPARISON_PLOT_PATH = "images/best_scenarios_comparison.png"
BEST_SCENARIO_TIMESERIES_PLOT_PATH = "images/best_scenario_timeseries.png"
BEST_SCENARIO_TIMESERIES_PATH = "reports/best_scenario_timeseries.csv"
BEST_SCENARIO_BATTERY_STATE_PLOT_PATH = "images/best_scenario_battery_state.png"
BEST_SCENARIO_CUMULATIVE_ENERGY_PLOT_PATH = "images/best_scenario_cumulative_energy.png"
OUTPUTS_INDEX_PATH = "reports/outputs_index.md"

# Simulation settings
DAYS_PER_YEAR = 365

# Grid search parameters
SOLAR_PEAK_POWERS_KW = [0.5, 1.0, 1.5, 2.0, 3.0]
BATTERY_CAPACITIES_KWH = [0, 0.5, 1.0, 2.0, 3.0, 5.0]

# Battery model parameters
BATTERY_EFFICIENCY = 0.90
MAX_CHARGE_POWER_KW = 1.0
MAX_DISCHARGE_POWER_KW = 1.0
INITIAL_BATTERY_STATE_KWH = 0.0

# Economic assumptions
ELECTRICITY_PRICE_EUR_PER_KWH = 0.20
SURPLUS_COMPENSATION_EUR_PER_KWH = 0.07

FIXED_INSTALLATION_COST_EUR = 800.0
SOLAR_COST_EUR_PER_KW = 900.0
BATTERY_COST_EUR_PER_KWH = 500.0

# Tariff assumptions.
# These values are illustrative and can be replaced by prices
# from a specific electricity contract or by PVPC hourly prices.

ACTIVE_TARIFF_PROFILE = "spanish_2_0td_example"

TARIFF_PROFILES = {
    "flat_price": {
        "peak_price_eur_per_kwh": 0.20,
        "flat_price_eur_per_kwh": 0.20,
        "off_peak_price_eur_per_kwh": 0.20,
        "surplus_compensation_eur_per_kwh": 0.07,
        "contracted_power_kw": 4.6,
        "power_price_eur_per_kw_year": 35.0
    },
    "spanish_2_0td_example": {
        "peak_price_eur_per_kwh": 0.25,
        "flat_price_eur_per_kwh": 0.18,
        "off_peak_price_eur_per_kwh": 0.12,
        "surplus_compensation_eur_per_kwh": 0.07,
        "contracted_power_kw": 4.6,
        "power_price_eur_per_kw_year": 35.0
    }
}


def get_active_tariff_profile() -> dict:
    return TARIFF_PROFILES[ACTIVE_TARIFF_PROFILE]

