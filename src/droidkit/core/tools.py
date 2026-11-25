"""Locate and validate Android platform-tools binaries."""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# Official Google platform-tools (linux/windows) — update when you bump the bundle.
# Verify against https://dl.google.com/android/repository/platform-tools-latest-windows.zip
KNOWN_SHA256: dict[str, str] = {
    # Example — replace with hashes of the exact build you ship.
    # "adb.exe": "B4A6B455...",
}


class ToolNotFoundError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ToolPaths:
    adb: Path
    fastboot: Path

    def sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest().upper()


def _bundle_dirs() -> list[Path]:
    """Dirs where a shipped platform-tools bundle may live (first match wins)."""
    dirs: list[Path] = []
    if getattr(sys, "frozen", False):  # PyInstaller
        exe_dir = Path(sys.executable).resolve().parent
        dirs += [exe_dir / "platform-tools", exe_dir]
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(Path(meipass) / "platform-tools")
    # Dev checkout: ./platform-tools next to the repo root
    dirs.append(Path(__file__).resolve().parents[3] / "platform-tools")
    return dirs


def _find_bundled(name: str) -> Path | None:
    for d in _bundle_dirs():
        for candidate in (d / name, d / f"{name}.exe"):
            if candidate.is_file():
                return candidate
    return None


def _resolve(name: str, env_var: str) -> Path:
    override = os.environ.get(env_var)
    if override:
        p = Path(override).expanduser()
        if p.is_file():
            return p
        raise ToolNotFoundError(f"{env_var} points to missing file: {p}")

    bundled = _find_bundled(name)
    if bundled:
        return bundled

    found = shutil.which(name) or shutil.which(f"{name}.exe")
    if not found:
        raise ToolNotFoundError(
            f"'{name}' not found on PATH. Install Android platform-tools or set {env_var}."
        )
    return Path(found)


def resolve_tools() -> ToolPaths:
    return ToolPaths(
        adb=_resolve("adb", "DROIDKIT_ADB"),
        fastboot=_resolve("fastboot", "DROIDKIT_FASTBOOT"),
    )
