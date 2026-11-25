"""Qt facade for updates — context property `UpdateApi`."""

from __future__ import annotations

import os
import webbrowser

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from droidkit import __version__
from droidkit.update.github_releases import UpdateChecker
from droidkit.update.models import ReleaseInfo


class _CheckThread(QThread):
    finished_with = Signal(object)  # ReleaseInfo | None

    def __init__(self, repo: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._repo = repo

    def run(self) -> None:
        info = UpdateChecker(self._repo).latest()
        self.finished_with.emit(info)


class UpdateApi(QObject):
    statusChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._repo = os.environ.get("DROIDKIT_UPDATE_REPO", "thyvon/droidkit-tool")
        self._latest: ReleaseInfo | None = None
        self._checking = False
        self._error = ""
        self._thread: _CheckThread | None = None

    @Property(str, notify=statusChanged)
    def currentVersion(self) -> str:
        return __version__

    @Property(str, notify=statusChanged)
    def latestVersion(self) -> str:
        return self._latest.version if self._latest else ""

    @Property(str, notify=statusChanged)
    def releaseUrl(self) -> str:
        return self._latest.url if self._latest else ""

    @Property(str, notify=statusChanged)
    def releaseNotes(self) -> str:
        return self._latest.body if self._latest else ""

    @Property(bool, notify=statusChanged)
    def updateAvailable(self) -> bool:
        if not self._latest:
            return False
        return UpdateChecker.is_newer(__version__, self._latest.tag)

    @Property(bool, notify=statusChanged)
    def checking(self) -> bool:
        return self._checking

    @Property(str, notify=statusChanged)
    def errorMessage(self) -> str:
        return self._error

    @Slot()
    def check(self) -> None:
        if self._checking:
            return
        self._checking = True
        self._error = ""
        self.statusChanged.emit()
        self._thread = _CheckThread(self._repo, self)
        self._thread.finished_with.connect(self._on_done)
        self._thread.start()

    def _on_done(self, info: object) -> None:
        self._checking = False
        if info is None:
            self._error = "Could not reach update server."
        else:
            self._latest = info  # type: ignore[assignment]
        self.statusChanged.emit()

    @Slot()
    def openReleasePage(self) -> None:
        if self._latest:
            webbrowser.open(self._latest.url)


__all__ = ["UpdateApi"]
