"""Release metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReleaseInfo:
    tag: str
    name: str
    url: str
    body: str = ""
    installer_url: str = ""
    installer_name: str = ""

    @property
    def version(self) -> str:
        return self.tag.lstrip("v")

    @property
    def has_installer(self) -> bool:
        return bool(self.installer_url)
