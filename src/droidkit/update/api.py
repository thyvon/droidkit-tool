"""Qt facade for updates — context property `UpdateApi`.

Flow: check() → updateAvailable → downloadUpdate() streams the installer
with progress → runs it (Windows) → app quits so the installer can replace
files. On other platforms we fall back to opening the release page.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path

import httpx
from PySide6.QtCore import Property, QCoreApplication, QObject, QThread, Signal, Slot

from droidkit import __version__
from droidkit.update.github_releases import DOWNLOAD_TIMEOUT, UpdateChecker
from droidkit.update.models import ReleaseInfo


class _CheckThread(QThread):
    finished_with = Signal(object)  # ReleaseInfo | None

    def __init__(self, repo: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._repo = repo

    def run(self) -> None:
        info = UpdateChecker(self._repo).latest()
        self.finished_with.emit(info)


class _DownloadThread(QThread):
    """Streams the installer to a temp file, reporting percent progress."""

    progressed = Signal(int)  # 0-100
    finished_with = Signal(str, str)  # (local_path, error) — error "" on success

    def __init__(self, url: str, dest_dir: Path, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._url = url
        self._dest_dir = dest_dir

    def run(self) -> None:
        try:
            dest = self._dest_dir / Path(self._url).name
            last_pct = -1
            with httpx.stream(
                "GET",
                self._url,
                timeout=DOWNLOAD_TIMEOUT,
                follow_redirects=True,
            ) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length") or 0)
                done = 0
                with dest.open("wb") as fh:
                    for chunk in resp.iter_bytes(chunk_size=1 << 16):
                        fh.write(chunk)
                        done += len(chunk)
                        if total:
                            pct = min(99, int(done * 100 / total))
                            if pct != last_pct:
                                last_pct = pct
                                self.progressed.emit(pct)
            self.progressed.emit(100)
            self.finished_with.emit(str(dest), "")
        except (httpx.HTTPError, OSError) as exc:
            self.finished_with.emit("", str(exc))


class UpdateApi(QObject):
    statusChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._repo = os.environ.get("DROIDKIT_UPDATE_REPO", "thyvon/droidkit-tool")
        self._latest: ReleaseInfo | None = None
        self._checking = False
        self._downloading = False
        self._progress = 0
        self._error = ""
        self._thread: _CheckThread | None = None
        self._dl: _DownloadThread | None = None

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

    @Property(bool, notify=statusChanged)
    def downloading(self) -> bool:
        return self._downloading

    @Property(int, notify=statusChanged)
    def progress(self) -> int:
        return self._progress

    @Property(str, notify=statusChanged)
    def errorMessage(self) -> str:
        return self._error

    @Slot()
    def check(self) -> None:
        if self._checking or self._downloading:
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

    @Slot()
    def downloadUpdate(self) -> None:
        """One-click update: download installer → run it → quit this app."""
        if self._downloading or not self._latest or not self._latest.has_installer:
            return
        self._downloading = True
        self._progress = 0
        self._error = ""
        self.statusChanged.emit()
        dest_dir = Path(tempfile.gettempdir()) / "DroidKit"
        dest_dir.mkdir(parents=True, exist_ok=True)
        self._dl = _DownloadThread(self._latest.installer_url, dest_dir, self)
        self._dl.progressed.connect(self._on_progress)
        self._dl.finished_with.connect(self._on_downloaded)
        self._dl.start()

    def _on_progress(self, pct: int) -> None:
        self._progress = pct
        self.statusChanged.emit()

    def _on_downloaded(self, path: str, error: str) -> None:
        self._downloading = False
        if error:
            self._error = error
            self.statusChanged.emit()
            return
        self._progress = 100
        self.statusChanged.emit()
        self._launch_installer(path)

    def _launch_installer(self, path: str) -> None:
        if sys.platform == "win32" and path.lower().endswith(".exe"):
            try:
                # Start the installer, then quit so it can replace our files
                # (Popen returns immediately; the wizard takes seconds to load).
                subprocess.Popen([path])
                QCoreApplication.quit()
                return
            except OSError as exc:
                self._error = f"Could not start installer: {exc}"
                self.statusChanged.emit()
                return
        # Non-Windows (or unexpected asset): fall back to the release page.
        self.openReleasePage()


__all__ = ["UpdateApi"]
