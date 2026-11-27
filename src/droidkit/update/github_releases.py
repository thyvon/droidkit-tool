"""Check GitHub Releases for a newer version."""

from __future__ import annotations

import sys
from typing import Any

import httpx
from packaging.version import InvalidVersion, Version

from droidkit.update.models import ReleaseInfo

API_TIMEOUT = 10.0
DOWNLOAD_TIMEOUT = 300.0


def pick_installer(assets: list[dict[str, Any]]) -> tuple[str, str]:
    """Choose the best download asset for this platform.

    Returns (browser_download_url, name). Prefers the Windows setup.exe when
    running on Windows, the portable zip elsewhere; falls back to any .exe.
    """
    exe = next(
        (a for a in assets if str(a.get("name", "")).lower().endswith(".exe")),
        None,
    )
    zip_asset = next(
        (a for a in assets if str(a.get("name", "")).lower().endswith(".zip")),
        None,
    )
    chosen = None
    if sys.platform == "win32":
        chosen = exe or zip_asset
    else:
        chosen = zip_asset or exe
    if not chosen:
        return "", ""
    return str(chosen.get("browser_download_url", "")), str(chosen.get("name", ""))


class UpdateChecker:
    def __init__(self, repo: str, *, timeout: float = API_TIMEOUT) -> None:
        """repo: 'owner/name' e.g. 'thyvon/droidkit-tool'."""
        self._repo = repo.strip("/")
        self._timeout = timeout

    def latest(self) -> ReleaseInfo | None:
        url = f"https://api.github.com/repos/{self._repo}/releases/latest"
        try:
            resp = httpx.get(
                url,
                timeout=self._timeout,
                headers={"Accept": "application/vnd.github+json"},
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        except (httpx.HTTPError, ValueError):
            return None
        assets = data.get("assets") or []
        installer_url, installer_name = pick_installer(assets)
        return ReleaseInfo(
            tag=str(data.get("tag_name", "")),
            name=str(data.get("name") or data.get("tag_name") or ""),
            url=str(data.get("html_url") or url),
            body=str(data.get("body") or ""),
            installer_url=installer_url,
            installer_name=installer_name,
        )

    @staticmethod
    def is_newer(current: str, latest_tag: str) -> bool:
        try:
            return Version(latest_tag.lstrip("v")) > Version(current)
        except InvalidVersion:
            return False
