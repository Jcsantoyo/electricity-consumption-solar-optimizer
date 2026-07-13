import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

import config
from price_mode import build_electricity_price_mode_description

def format_list(values: list) -> str:
    return ", ".join(str(value) for value in values)


def build_configuration_summary() -> str:
    active_tariff = config.get_active_tariff_profile()

    electricity_price_mode = build_electricity_price_mode_description(
        use_hourly_price_data=config.USE_HOURLY_PRICE_DATA,
        hourly_price_data_path=config.HOURLY_PRICE_DATA_PATH,
        tariff_profile_name=config.ACTIVE_TARIFF_PROFILE,
    )

    lines = [
        "# Project Configuration Summary",
        "",
        "This file summarizes the configuration used by the project pipeline.",
        "",
        "## Input data",
        "",
        f"- Consumption data path: `{config.CONSUMPTION_DATA_PATH}`",
        f"- Use PVGIS solar data: `{config.USE_PVGIS_SOLAR_DATA}`",
        f"- PVGIS solar data path: `{config.PVGIS_SOLAR_DATA_PATH}`",
        "",
        "## Electricity price data",
        "",
        f"- Use hourly electricity prices: `{config.USE_HOURLY_PRICE_DATA}`",
        f"- Hourly price data path: `{config.HOURLY_PRICE_DATA_PATH}`",
        (
            "- Allow negative hourly prices: "
            f"`{config.ALLOW_NEGATIVE_HOURLY_PRICES}`"
        ),
        f"- Electricity price mode: {electricity_price_mode}",
        "",
        "## Simulation settings",
        "",
        f"- Days per year: `{config.DAYS_PER_YEAR}`",
        "",
        "## Grid search parameters",
        "",
        "- Solar peak powers tested:",
        "",
        f"```text\n{format_list(config.SOLAR_PEAK_POWERS_KW)} kW\n```",
        "",
        "- Battery capacities tested:",
        "",
        f"```text\n{format_list(config.BATTERY_CAPACITIES_KWH)} kWh\n```",
        "",
        "## Battery model",
        "",
        f"- Battery efficiency: `{config.BATTERY_EFFICIENCY}`",
        f"- Maximum charge power: `{config.MAX_CHARGE_POWER_KW}` kW",
        f"- Maximum discharge power: `{config.MAX_DISCHARGE_POWER_KW}` kW",
        f"- Initial battery state: `{config.INITIAL_BATTERY_STATE_KWH}` kWh",
        "",
        "## Economic assumptions",
        "",
        f"- Fixed installation cost: `{config.FIXED_INSTALLATION_COST_EUR}` EUR",
        f"- Solar cost: `{config.SOLAR_COST_EUR_PER_KW}` EUR/kW",
        f"- Battery cost: `{config.BATTERY_COST_EUR_PER_KWH}` EUR/kWh",
        "",
        "## Active tariff profile",
        "",
        f"- Active tariff profile: `{config.ACTIVE_TARIFF_PROFILE}`",
        "",
        "### Active tariff values",
        "",
        f"- Peak price: `{active_tariff['peak_price_eur_per_kwh']}` EUR/kWh",
        f"- Flat price: `{active_tariff['flat_price_eur_per_kwh']}` EUR/kWh",
        f"- Off-peak price: `{active_tariff['off_peak_price_eur_per_kwh']}` EUR/kWh",
        (
            "- Surplus compensation: "
            f"`{active_tariff['surplus_compensation_eur_per_kwh']}` EUR/kWh"
        ),
        f"- Contracted power: `{active_tariff['contracted_power_kw']}` kW",
        (
            "- Power price: "
            f"`{active_tariff['power_price_eur_per_kw_year']}` EUR/kW/year"
        ),
        "",
        "## Available tariff profiles",
        "",
    ]

    for profile_name in config.TARIFF_PROFILES:
        lines.append(f"- `{profile_name}`")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "The tariff profile values are illustrative assumptions.",
            "When hourly prices are enabled, they replace the tariff profile prices",
            "for the variable cost of imported electricity.",
            "The tariff profile still provides fixed power costs and surplus compensation.",
            "OMIE prices represent wholesale market prices, not a complete household",
            "retail electricity tariff.",
            "",
        ]
    )

    return "\n".join(lines)

def main() -> None:
    output_path = "reports/configuration_summary.md"

    os.makedirs("reports", exist_ok=True)

    summary = build_configuration_summary()

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(summary)

    print("\nConfiguration summary generated")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
