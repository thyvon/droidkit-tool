"""File push / pull and simple directory listing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from droidkit.core.adb import Adb


@dataclass(frozen=True, slots=True)
class RemoteFile:
    name: str
    path: str
    is_dir: bool
    size: str = ""
    perms: str = ""


class FileService:
    def __init__(self, adb: Adb | None = None) -> None:
        self._adb = adb or Adb()

    def list_dir(self, serial: str, remote_path: str = "/sdcard") -> list[RemoteFile]:
        # ls -la is busybox/toybox friendly enough across API levels
        res = self._adb.shell(f"ls -la {remote_path}", serial=serial)
        out: list[RemoteFile] = []
        for line in res.stdout.splitlines():
            line = line.rstrip()
            if not line or line.startswith("total "):
                continue
            parts = line.split(None, 8)
            if len(parts) < 9:
                # some devices omit link count etc.
                parts = line.split(None, 7)
                if len(parts) < 8:
                    continue
                perms, name = parts[0], parts[-1]
                size = ""
            else:
                perms, size, name = parts[0], parts[4], parts[8]
            if name in (".", ".."):
                continue
            # strip "-> target"
            if " -> " in name:
                name = name.split(" -> ", 1)[0]
            is_dir = perms.startswith("d") or perms.startswith("l")
            # only keep real dirs for navigation; treat links carefully
            is_dir = perms.startswith("d")
            path = remote_path.rstrip("/") + "/" + name
            out.append(RemoteFile(name=name, path=path, is_dir=is_dir, size=size, perms=perms))
        return sorted(out, key=lambda f: (not f.is_dir, f.name.lower()))

    def push(self, serial: str, local: Path, remote: str) -> None:
        self._adb.run("push", str(local), remote, serial=serial, check=True, timeout=300)

    def pull(self, serial: str, remote: str, local: Path) -> None:
        local.parent.mkdir(parents=True, exist_ok=True)
        self._adb.run("pull", remote, str(local), serial=serial, check=True, timeout=300)
