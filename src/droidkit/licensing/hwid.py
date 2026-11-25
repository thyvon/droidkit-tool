"""Stable hardware fingerprint for license binding.

Design goals:
  * Stable across reboots for the same machine
  * Cheap to compute (no admin required on Windows)
  * Easy to replace: implement `HwidProvider` and inject

Windows: MachineGuid + CPU ID + disk serial (via PowerShell once, cached).
Linux:   /etc/machine-id + hostname hash.
"""

from __future__ import annotations

import hashlib
import platform
import subprocess
from functools import lru_cache
from typing import Protocol


class HwidProvider(Protocol):
    def compute(self) -> str: ...


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32].upper()


def _windows_hwid() -> str:
    ps = (
        "$m=(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Cryptography' "
        "-Name MachineGuid -ErrorAction SilentlyContinue).MachineGuid; "
        "$b=(Get-CimInstance Win32_BIOS).SerialNumber; "
        "$c=(Get-CimInstance Win32_Processor).ProcessorId; "
        'Write-Output "$m|$b|$c"'
    )
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        ).stdout.strip()
        if out:
            return _sha(out)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return _sha(f"{platform.node()}|fallback|{platform.processor()}")


def _linux_hwid() -> str:
    parts: list[str] = []
    for path in ("/etc/machine-id", "/etc/dbus/machine-id"):
        try:
            parts.append(_read_text(path))
            break
        except OSError:
            continue
    parts.append(platform.node())
    parts.append(platform.processor())
    return _sha("|".join(parts))


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


class DefaultHwidProvider:
    def compute(self) -> str:
        if platform.system() == "Windows":
            return _windows_hwid()
        if platform.system() == "Linux":
            return _linux_hwid()
        return _sha(f"{platform.node()}|{platform.processor()}")


@lru_cache(maxsize=1)
def get_hwid(provider: HwidProvider | None = None) -> str:
    return (provider or DefaultHwidProvider()).compute()
