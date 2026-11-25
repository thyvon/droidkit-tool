"""Package / app management via ADB."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from droidkit.core.adb import Adb


@dataclass(frozen=True, slots=True)
class AppEntry:
    package: str
    path: str = ""
    system: bool = False


class AppService:
    def __init__(self, adb: Adb | None = None) -> None:
        self._adb = adb or Adb()

    def list_packages(self, serial: str, *, third_party_only: bool = True) -> list[AppEntry]:
        flag = "-3" if third_party_only else ""
        res = self._adb.shell(f"pm list packages {flag}".strip(), serial=serial, check=True)
        out: list[AppEntry] = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                pkg = line.removeprefix("package:").strip()
                if pkg:
                    out.append(AppEntry(package=pkg))
        return sorted(out, key=lambda a: a.package)

    def apk_path(self, serial: str, package: str) -> str | None:
        res = self._adb.shell(f"pm path {package}", serial=serial)
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                return line.removeprefix("package:").strip()
        return None

    def backup_apk(self, serial: str, package: str, dest_dir: Path) -> Path | None:
        remote = self.apk_path(serial, package)
        if not remote:
            return None
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{package}.apk"
        self._adb.run("pull", remote, str(dest), serial=serial, check=True)
        return dest

    def uninstall(self, serial: str, package: str, *, keep_data: bool = False) -> bool:
        args = ["uninstall", "-k" if keep_data else "", package]
        res = self._adb.run(*[a for a in args if a], serial=serial)
        return res.ok and "Success" in res.stdout

    def disable(self, serial: str, package: str) -> bool:
        res = self._adb.shell(f"pm disable-user --user 0 {package}", serial=serial)
        return res.ok

    def enable(self, serial: str, package: str) -> bool:
        res = self._adb.shell(f"pm enable {package}", serial=serial)
        return res.ok

    def install(self, serial: str, apk: Path, *, grant_perms: bool = True) -> bool:
        args = ["install", "-r"]
        if grant_perms:
            args.append("-g")
        args.append(str(apk))
        res = self._adb.run(*args, serial=serial, timeout=180)
        return res.ok and "Success" in res.stdout
