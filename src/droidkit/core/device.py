"""Device info aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from droidkit.core.adb import Adb


@dataclass(frozen=True, slots=True)
class DeviceInfo:
    serial: str
    state: str
    model: str = ""
    brand: str = ""
    device: str = ""
    android_version: str = ""
    sdk: str = ""
    battery_level: str = ""
    battery_status: str = ""
    battery_health: str = ""
    battery_temp: str = ""
    battery_voltage: str = ""
    total_storage: str = ""
    free_storage: str = ""
    screen: str = ""
    abi: str = ""

    def to_dict(self) -> dict[str, str]:
        return {k: str(v) for k, v in asdict(self).items()}


#: dumpsys battery `health:` codes → human text (repairers read this daily).
_BATTERY_HEALTH = {
    "1": "Unknown",
    "2": "Good",
    "3": "Overheat",
    "4": "Dead",
    "5": "Over voltage",
    "6": "Cold",
    "7": "Watchdog timer",
    "8": "Safety timer",
}

_BATTERY_STATUS = {
    "1": "Unknown",
    "2": "Charging",
    "3": "Discharging",
    "4": "Not charging",
    "5": "Full",
}


class DeviceService:
    def __init__(self, adb: Adb | None = None) -> None:
        self._adb = adb or Adb()

    def list_devices(self) -> list[dict[str, str]]:
        return self._adb.devices()

    def info(self, serial: str) -> DeviceInfo:
        adb = self._adb
        raw = next((d for d in adb.devices() if d["serial"] == serial), {})
        props = adb.shell(
            "getprop ro.product.model; getprop ro.product.brand; "
            "getprop ro.product.device; getprop ro.build.version.release; "
            "getprop ro.build.version.sdk; getprop ro.product.cpu.abi",
            serial=serial,
        ).stdout.splitlines()
        while len(props) < 6:
            props.append("")
        battery = adb.shell("dumpsys battery", serial=serial).stdout
        level, status, health, temp_c, voltage = _parse_battery(battery)
        df = adb.shell("df /data | tail -1", serial=serial).stdout.split()
        total = df[1] if len(df) > 1 else ""
        free = df[3] if len(df) > 3 else ""
        size = adb.shell("wm size", serial=serial).stdout.strip()

        return DeviceInfo(
            serial=serial,
            state=raw.get("state", "device"),
            model=props[0].strip(),
            brand=props[1].strip(),
            device=props[2].strip(),
            android_version=props[3].strip(),
            sdk=props[4].strip(),
            battery_level=level,
            battery_status=status,
            battery_health=health,
            battery_temp=temp_c,
            battery_voltage=voltage,
            total_storage=total,
            free_storage=free,
            screen=size.replace("Physical size: ", ""),
            abi=props[5].strip(),
        )


def _parse_battery(dumpsys: str) -> tuple[str, str, str, str, str]:
    """Return (level, status, health, temp_c, voltage_mv)."""
    level = status = health = temp_c = voltage = ""
    for line in dumpsys.splitlines():
        line = line.strip()
        if line.startswith("level:"):
            level = line.split(":", 1)[1].strip()
        elif line.startswith("status:"):
            code = line.split(":", 1)[1].strip()
            status = _BATTERY_STATUS.get(code, code)
        elif line.startswith("health:"):
            code = line.split(":", 1)[1].strip()
            health = _BATTERY_HEALTH.get(code, code)
        elif line.startswith("temperature:"):
            raw = line.split(":", 1)[1].strip()
            if raw.isdigit():
                temp_c = f"{int(raw) / 10:.1f} °C"
        elif line.startswith("voltage:"):
            raw = line.split(":", 1)[1].strip()
            if raw.isdigit():
                voltage = f"{int(raw)} mV"
    return level, status, health, temp_c, voltage
