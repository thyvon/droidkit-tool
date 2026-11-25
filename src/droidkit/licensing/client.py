"""Optional online license / trial check.

Point `base_url` at YOUR API — do not hardcode third-party endpoints.
All network I/O goes through this module only.
"""

from __future__ import annotations

from typing import Any

import httpx

from droidkit.licensing.hwid import get_hwid
from droidkit.licensing.models import LicenseStatus, LicenseView

DEFAULT_TIMEOUT = 10.0


class LicenseClient:
    def __init__(self, base_url: str, *, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    def check(self, license_key: str, *, hwid: str | None = None) -> LicenseView:
        hwid = hwid or get_hwid()
        try:
            resp = httpx.post(
                f"{self._base}/v1/license/check",
                json={"key": license_key, "hwid": hwid, "product": "droidkit"},
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        except httpx.HTTPError as exc:
            return LicenseView(
                status=LicenseStatus.NETWORK_ERROR,
                hwid=hwid,
                message=f"License server unreachable: {exc}",
            )
        except ValueError:
            return LicenseView(
                status=LicenseStatus.NETWORK_ERROR,
                hwid=hwid,
                message="Invalid response from license server.",
            )

        status_raw = str(data.get("status", "invalid")).lower()
        try:
            status = LicenseStatus(status_raw)
        except ValueError:
            status = LicenseStatus.INVALID

        expires_at = None
        if data.get("expires_at"):
            from datetime import datetime

            expires_at = datetime.fromisoformat(str(data["expires_at"]).replace("Z", "+00:00"))

        return LicenseView(
            status=status,
            key_id=str(data.get("key_id", "")),
            plan=str(data.get("plan", "")),
            expires_at=expires_at,
            hwid=hwid,
            message=str(data.get("message", status.value)),
        )
