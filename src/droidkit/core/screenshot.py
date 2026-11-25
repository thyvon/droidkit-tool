"""Screenshot via screencap."""

from __future__ import annotations

from pathlib import Path

from droidkit.core.adb import Adb


class ScreenshotService:
    def __init__(self, adb: Adb | None = None) -> None:
        self._adb = adb or Adb()

    def capture(self, serial: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        remote = "/sdcard/droidkit_screenshot.png"
        self._adb.shell(f"screencap -p {remote}", serial=serial, check=True)
        try:
            self._adb.run("pull", remote, str(dest), serial=serial, check=True, timeout=60)
        finally:
            self._adb.shell(f"rm -f {remote}", serial=serial)
        return dest
