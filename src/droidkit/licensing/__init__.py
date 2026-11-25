"""Licensing package.

Layers (dependency direction: ui -> api -> services -> pure helpers):

    licensing/
      api.py        Qt-facing facade (QObject) — only file UI imports
      models.py     dataclasses / enums (pure)
      hwid.py       machine fingerprint (pure, testable)
      crypto.py     Ed25519 verify/sign helpers (pure)
      store.py      %APPDATA% persistence
      client.py     optional online check (httpx)
"""

from droidkit.licensing.api import LicenseApi
from droidkit.licensing.models import LicenseStatus, LicenseView

__all__ = ["LicenseApi", "LicenseStatus", "LicenseView"]
