from scripts.generate_config_summary import build_configuration_summary
import config


def test_configuration_summary_contains_main_sections():
    summary = build_configuration_summary()

    assert "# Project Configuration Summary" in summary
    assert "## Input data" in summary
    assert "## Simulation settings" in summary
    assert "## Grid search parameters" in summary
    assert "## Battery model" in summary
    assert "## Economic assumptions" in summary
    assert "## Active tariff profile" in summary
    assert "## Available tariff profiles" in summary


def test_configuration_summary_contains_current_config_values():
    summary = build_configuration_summary()

    assert config.CONSUMPTION_DATA_PATH in summary
    assert config.PVGIS_SOLAR_DATA_PATH in summary
    assert config.ACTIVE_TARIFF_PROFILE in summary

    solar_power_values = ", ".join(str(value) for value in config.SOLAR_PEAK_POWERS_KW)
    battery_capacity_values = ", ".join(
        str(value) for value in config.BATTERY_CAPACITIES_KWH
    )

    assert f"{solar_power_values} kW" in summary
    assert f"{battery_capacity_values} kWh" in summary


def test_configuration_summary_contains_active_tariff_values():
    summary = build_configuration_summary()
    active_tariff = config.get_active_tariff_profile()

    assert str(active_tariff["peak_price_eur_per_kwh"]) in summary
    assert str(active_tariff["flat_price_eur_per_kwh"]) in summary
    assert str(active_tariff["off_peak_price_eur_per_kwh"]) in summary
    assert str(active_tariff["surplus_compensation_eur_per_kwh"]) in summary
    assert str(active_tariff["contracted_power_kw"]) in summary
    assert str(active_tariff["power_price_eur_per_kw_year"]) in summary
