"""Logcat streaming."""

from __future__ import annotations

import subprocess
from collections.abc import Iterator

from droidkit.core.tools import resolve_tools


class LogcatStream:
    def __init__(self, serial: str | None = None, filterspec: str | None = None) -> None:
        self._tools = resolve_tools()
        self._serial = serial
        self._filterspec = filterspec
        self._proc: subprocess.Popen[str] | None = None

    def start(self) -> None:
        if self._proc and self._proc.poll() is None:
            return
        cmd = [str(self._tools.adb)]
        if self._serial:
            cmd += ["-s", self._serial]
        cmd += ["logcat", "-v", "time"]
        if self._filterspec:
            cmd += self._filterspec.split()
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

    def lines(self) -> Iterator[str]:
        if not self._proc or not self._proc.stdout:
            return
        for line in self._proc.stdout:
            yield line.rstrip("\n")

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None

    def __enter__(self) -> LogcatStream:
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()
