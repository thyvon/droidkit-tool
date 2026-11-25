"""License persistence under platformdirs user data dir."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_data_dir

from droidkit.licensing.crypto import (
    LicenseCryptoError,
    load_license,
    save_license,
)
from droidkit.licensing.hwid import get_hwid
from droidkit.licensing.models import LicensePayload, LicenseStatus, LicenseView

APP_NAME = "DroidKit"
APP_AUTHOR = "DroidKit"


def data_dir() -> Path:
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def license_path() -> Path:
    return data_dir() / "license.bin"


class LicenseStore:
    """Load / save / evaluate the local license file."""

    def __init__(self, path: Path | None = None, *, public_key_b64: str | None = None) -> None:
        self._path = path or license_path()
        self._public_key = public_key_b64
        self._cached: LicensePayload | None = None

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.is_file()

    def load(self) -> LicensePayload | None:
        if not self.exists():
            self._cached = None
            return None
        try:
            self._cached = load_license(self._path, public_key_b64=self._public_key)
        except (LicenseCryptoError, OSError, ValueError):
            self._cached = None
        return self._cached

    def save(self, body: bytes, signature: bytes) -> Path:
        path = save_license(self._path.parent, body, signature)
        self.load()
        return path

    def clear(self) -> None:
        if self._path.exists():
            self._path.unlink()
        self._cached = None

    def view(self) -> LicenseView:
        hwid = get_hwid()
        payload = self.load()
        if payload is None:
            return LicenseView(
                status=LicenseStatus.UNLICENSED,
                hwid=hwid,
                message="No license installed.",
            )
        status = payload.status_for(hwid)
        return LicenseView(
            status=status,
            key_id=payload.key_id,
            plan=payload.plan,
            expires_at=payload.expires_at,
            hwid=hwid,
            message=status.value.replace("_", " ").title(),
        )
