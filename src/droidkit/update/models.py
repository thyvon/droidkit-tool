"""Release metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReleaseInfo:
    tag: str
    name: str
    url: str
    body: str = ""

    @property
    def version(self) -> str:
        return self.tag.lstrip("v")
