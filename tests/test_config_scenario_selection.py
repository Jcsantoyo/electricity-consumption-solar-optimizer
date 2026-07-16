import os
import subprocess
import sys


def run_config_check(
    scenario_name: str,
) -> str:
    environment = os.environ.copy()

    environment["PROJECT_SCENARIO"] = (
        scenario_name
    )

    environment["PYTHONPATH"] = "src"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import config; "
                "print(config.ACTIVE_PROJECT_SCENARIO_NAME); "
                "print(config.ACTIVE_PROJECT_SCENARIO.price_mode); "
                "print(config.USE_HOURLY_PRICE_DATA)"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    return result.stdout


def test_config_loads_omie_scenario_from_environment() -> None:
    output = run_config_check(
        "uci_omie_june_2026"
    )

    assert "uci_omie_june_2026" in output
    assert "wholesale_hourly" in output
    assert "True" in output


def test_config_loads_fixed_scenario_from_environment() -> None:
    output = run_config_check(
        "uci_fixed_tariff"
    )

    assert "uci_fixed_tariff" in output
    assert "fixed" in output
    assert "False" in output