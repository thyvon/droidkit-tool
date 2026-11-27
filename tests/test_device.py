"""Core device/app logic tests — pure functions, no Qt, no device."""

from __future__ import annotations

import pytest

from droidkit.core.adb import Adb, AdbError
from droidkit.core.device import _parse_battery

DUMPSYS_BATTERY = """\
Current Battery Service state:
  AC powered: false
  USB powered: true
  Wireless powered: false
  Max charging current: 0
  Max charging voltage: 0
  Charge counter: 0
  status: 2
  health: 2
  present: true
  level: 87
  voltage: 4123
  temperature: 285
  technology: Li-ion
"""


def test_parse_battery_full() -> None:
    level, status, health, temp, voltage = _parse_battery(DUMPSYS_BATTERY)
    assert level == "87"
    assert status == "Charging"
    assert health == "Good"
    assert temp == "28.5 °C"
    assert voltage == "4123 mV"


def test_parse_battery_missing_fields() -> None:
    assert _parse_battery("") == ("", "", "", "", "")


def test_reboot_mode_allowlist() -> None:
    from pathlib import Path

    from droidkit.core.tools import ToolPaths

    adb = Adb(ToolPaths(adb=Path("/bin/true"), fastboot=Path("/bin/true")))
    assert set(adb.REBOOT_MODES) == {"", "bootloader", "recovery", "sideload", "fastboot"}
    # Invalid modes must be rejected before any subprocess runs.
    with pytest.raises(AdbError):
        adb.reboot("definitely-not-a-mode")
