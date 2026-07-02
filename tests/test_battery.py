import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))

from battery import simulate_battery


def test_battery_charges_with_solar_surplus() -> None:
    consumption_kwh = [1.0]
    solar_generation_kwh = [2.0]

    results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh=2.0,
        battery_efficiency=1.0,
        max_charge_power_kw=None,
        max_discharge_power_kw=None,
        initial_battery_state_kwh=0.0
    )

    assert results["self_consumed_kwh"] == [1.0]
    assert results["battery_charge_kwh"] == [1.0]
    assert results["battery_state_kwh"] == [1.0]
    assert results["grid_import_kwh"] == [0.0]
    assert results["solar_surplus_kwh"] == [0.0]


def test_battery_discharges_when_consumption_exceeds_solar() -> None:
    consumption_kwh = [2.0]
    solar_generation_kwh = [0.5]

    results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh=2.0,
        battery_efficiency=1.0,
        max_charge_power_kw=None,
        max_discharge_power_kw=None,
        initial_battery_state_kwh=1.0
    )

    assert results["self_consumed_kwh"] == [0.5]
    assert results["battery_discharge_kwh"] == [1.0]
    assert results["battery_state_kwh"] == [0.0]
    assert results["grid_import_kwh"] == [0.5]


def test_battery_does_not_exceed_capacity() -> None:
    consumption_kwh = [0.0]
    solar_generation_kwh = [10.0]

    results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh=2.0,
        battery_efficiency=1.0,
        max_charge_power_kw=None,
        max_discharge_power_kw=None,
        initial_battery_state_kwh=0.0
    )

    assert results["battery_state_kwh"] == [2.0]
    assert results["battery_charge_kwh"] == [2.0]
    assert results["solar_surplus_kwh"] == [8.0]


def test_battery_does_not_go_below_zero() -> None:
    consumption_kwh = [5.0]
    solar_generation_kwh = [0.0]

    results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh=2.0,
        battery_efficiency=1.0,
        max_charge_power_kw=None,
        max_discharge_power_kw=None,
        initial_battery_state_kwh=1.0
    )

    assert results["battery_discharge_kwh"] == [1.0]
    assert results["battery_state_kwh"] == [0.0]
    assert results["grid_import_kwh"] == [4.0]


def test_charge_power_limit_is_respected() -> None:
    consumption_kwh = [0.0]
    solar_generation_kwh = [5.0]

    results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh=5.0,
        battery_efficiency=1.0,
        max_charge_power_kw=1.5,
        max_discharge_power_kw=None,
        initial_battery_state_kwh=0.0
    )

    assert results["battery_charge_kwh"] == [1.5]
    assert results["battery_state_kwh"] == [1.5]
    assert results["solar_surplus_kwh"] == [3.5]


def test_discharge_power_limit_is_respected() -> None:
    consumption_kwh = [5.0]
    solar_generation_kwh = [0.0]

    results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh=5.0,
        battery_efficiency=1.0,
        max_charge_power_kw=None,
        max_discharge_power_kw=2.0,
        initial_battery_state_kwh=5.0
    )

    assert results["battery_discharge_kwh"] == [2.0]
    assert results["battery_state_kwh"] == [3.0]
    assert results["grid_import_kwh"] == [3.0]


def test_battery_efficiency_reduces_stored_energy() -> None:
    consumption_kwh = [0.0]
    solar_generation_kwh = [2.0]

    results = simulate_battery(
        consumption_kwh,
        solar_generation_kwh,
        battery_capacity_kwh=2.0,
        battery_efficiency=0.90,
        max_charge_power_kw=None,
        max_discharge_power_kw=None,
        initial_battery_state_kwh=0.0
    )

    assert results["battery_charge_kwh"] == [2.0]
    assert results["battery_state_kwh"] == [1.8]
    assert results["solar_surplus_kwh"] == [0.0]