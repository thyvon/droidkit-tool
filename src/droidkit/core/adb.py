"""ADB command runner (sync + async-friendly)."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from droidkit.core.tools import ToolPaths, resolve_tools


class AdbError(RuntimeError):
    def __init__(self, returncode: int, cmd: Sequence[str], stderr: str) -> None:
        self.returncode = returncode
        self.cmd = list(cmd)
        self.stderr = stderr
        super().__init__(f"adb failed ({returncode}): {' '.join(cmd)}\n{stderr.strip()}")


@dataclass(frozen=True, slots=True)
class AdbResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class Adb:
    def __init__(self, tools: ToolPaths | None = None, timeout: float = 30.0) -> None:
        self._tools = tools or resolve_tools()
        self._timeout = timeout

    @property
    def path(self) -> Path:
        return self._tools.adb

    def run(
        self,
        *args: str,
        serial: str | None = None,
        timeout: float | None = None,
        check: bool = False,
    ) -> AdbResult:
        cmd: list[str] = [str(self._tools.adb)]
        if serial:
            cmd += ["-s", serial]
        cmd += list(args)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout if timeout is not None else self._timeout,
        )
        result = AdbResult(proc.returncode, proc.stdout, proc.stderr)
        if check and not result.ok:
            raise AdbError(proc.returncode, cmd, proc.stderr)
        return result

    def shell(
        self,
        command: str,
        *,
        serial: str | None = None,
        check: bool = False,
        timeout: float | None = None,
    ) -> AdbResult:
        return self.run("shell", command, serial=serial, check=check, timeout=timeout)

    def devices(self) -> list[dict[str, str]]:
        res = self.run("devices", "-l")
        out: list[dict[str, str]] = []
        for line in res.stdout.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            info: dict[str, str] = {"serial": parts[0], "state": parts[1]}
            for extra in parts[2:]:
                if ":" in extra:
                    k, _, v = extra.partition(":")
                    info[k] = v
            out.append(info)
        return out

    def first_device_serial(self) -> str | None:
        for d in self.devices():
            if d.get("state") == "device":
                return d["serial"]
        return None
