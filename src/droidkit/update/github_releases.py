"""Check GitHub Releases for a newer version."""

from __future__ import annotations

from typing import Any

import httpx
from packaging.version import InvalidVersion, Version

from droidkit.update.models import ReleaseInfo

API_TIMEOUT = 10.0


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
        return ReleaseInfo(
            tag=str(data.get("tag_name", "")),
            name=str(data.get("name") or data.get("tag_name") or ""),
            url=str(data.get("html_url") or url),
            body=str(data.get("body") or ""),
        )

    @staticmethod
    def is_newer(current: str, latest_tag: str) -> bool:
        try:
            return Version(latest_tag.lstrip("v")) > Version(current)
        except InvalidVersion:
            return False
