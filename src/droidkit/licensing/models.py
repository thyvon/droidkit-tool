"""License domain models — no I/O, no Qt."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class LicenseStatus(StrEnum):
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    UNLICENSED = "unlicensed"
    HWID_MISMATCH = "hwid_mismatch"
    NETWORK_ERROR = "network_error"


@dataclass(frozen=True, slots=True)
class LicenseView:
    """Immutable snapshot for UI / logging."""

    status: LicenseStatus
    key_id: str = ""
    plan: str = ""
    expires_at: datetime | None = None
    hwid: str = ""
    message: str = ""

    @property
    def is_active(self) -> bool:
        return self.status is LicenseStatus.VALID

    @property
    def is_lifetime(self) -> bool:
        return self.expires_at is None and self.is_active

    def expires_label(self) -> str:
        if self.is_lifetime:
            return "Lifetime"
        if self.expires_at is None:
            return "—"
        return self.expires_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


@dataclass(frozen=True, slots=True)
class LicensePayload:
    """What a signed license file actually contains."""

    key_id: str
    plan: str
    hwid: str
    issued_at: datetime
    expires_at: datetime | None  # None = lifetime
    features: tuple[str, ...] = ()

    def status_for(self, current_hwid: str, now: datetime | None = None) -> LicenseStatus:
        now = now or datetime.now(UTC)
        if self.hwid and current_hwid and self.hwid != current_hwid:
            return LicenseStatus.HWID_MISMATCH
        if self.expires_at is not None and now > self.expires_at:
            return LicenseStatus.EXPIRED
        return LicenseStatus.VALID
