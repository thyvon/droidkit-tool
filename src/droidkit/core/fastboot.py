"""Fastboot command runner."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from droidkit.core.tools import ToolPaths, resolve_tools


class FastbootError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FastbootResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class Fastboot:
    def __init__(self, tools: ToolPaths | None = None, timeout: float = 60.0) -> None:
        self._tools = tools or resolve_tools()
        self._timeout = timeout

    def run(self, *args: str, timeout: float | None = None, check: bool = False) -> FastbootResult:
        cmd = [str(self._tools.fastboot), *args]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout if timeout is not None else self._timeout,
        )
        result = FastbootResult(proc.returncode, proc.stdout, proc.stderr)
        if check and not result.ok:
            raise FastbootError(f"fastboot failed: {' '.join(cmd)}\n{proc.stderr}")
        return result

    def devices(self) -> list[str]:
        res = self.run("devices")
        out: list[str] = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if line and "\t" in line:
                serial, state = line.split("\t", 1)
                if state.strip() == "fastboot":
                    out.append(serial)
        return out

    def reboot_bootloader(self, serial: str | None = None) -> FastbootResult:
        args = ["reboot", "bootloader"]
        if serial:
            args = ["-s", serial, *args]
        return self.run(*args)

    def reboot_system(self, serial: str | None = None) -> FastbootResult:
        args = ["reboot"]
        if serial:
            args = ["-s", serial, *args]
        return self.run(*args)

    def getvar(self, variable: str, serial: str | None = None) -> str:
        args = ["getvar", variable]
        if serial:
            args = ["-s", serial, *args]
        res = self.run(*args, timeout=10)
        # fastboot writes getvar to stderr
        text = (res.stderr or res.stdout).strip()
        for line in text.splitlines():
            if ":" in line:
                _, _, val = line.partition(":")
                return val.strip()
        return text
