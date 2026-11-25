"""Qt facade for licensing — the ONLY licensing import for QML/UI."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from droidkit.licensing.hwid import get_hwid
from droidkit.licensing.models import LicenseStatus, LicenseView
from droidkit.licensing.store import LicenseStore


class LicenseApi(QObject):
    """Expose license state to QML via context property `LicenseApi`."""

    changed = Signal()
    statusMessageChanged = Signal()

    def __init__(self, store: LicenseStore | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._store = store or LicenseStore()
        self._view: LicenseView = self._store.view()
        self._busy = False

    # --- properties -------------------------------------------------

    @Property(str, constant=True)
    def hwid(self) -> str:
        return get_hwid()

    @Property(str, notify=changed)
    def status(self) -> str:
        return str(self._view.status.value)

    @Property(str, notify=changed)
    def plan(self) -> str:
        return self._view.plan or "—"

    @Property(str, notify=changed)
    def expiresLabel(self) -> str:
        return self._view.expires_label()

    @Property(str, notify=statusMessageChanged)
    def statusMessage(self) -> str:
        return self._view.message

    @Property(bool, notify=changed)
    def isActive(self) -> bool:
        return self._view.is_active

    @Property(bool, notify=changed)
    def busy(self) -> bool:
        return self._busy

    # --- slots ------------------------------------------------------

    @Slot()
    def refresh(self) -> None:
        self._view = self._store.view()
        self.changed.emit()
        self.statusMessageChanged.emit()

    @Slot(str, result=bool)
    def activateFromFile(self, path: str) -> bool:
        """Install a license.bin the user selected."""
        from pathlib import Path

        src = Path(path)
        if not src.is_file():
            return False
        try:
            dest = self._store.path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
        except OSError:
            return False
        self.refresh()
        return self._view.is_active

    @Slot()
    def clear(self) -> None:
        self._store.clear()
        self.refresh()

    @Slot(str, result=str)
    def checkOnline(self, license_key: str) -> str:
        """Online check — wire base_url from your settings/config."""
        import os

        base = os.environ.get("DROIDKIT_LICENSE_URL", "")
        if not base:
            return "License server not configured."
        from droidkit.licensing.client import LicenseClient

        self._busy = True
        self.changed.emit()
        try:
            view = LicenseClient(base).check(license_key)
        finally:
            self._busy = False
        self._view = view
        self.changed.emit()
        self.statusMessageChanged.emit()
        return view.message

    @Slot(result=str)
    def copyHwid(self) -> str:
        return get_hwid()


# Re-export for convenience
__all__ = ["LicenseApi", "LicenseStatus", "LicenseView"]
