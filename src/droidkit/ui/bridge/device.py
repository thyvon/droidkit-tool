"""DeviceBridge — all device operations exposed to QML.

Heavy work runs off the GUI thread via QThreadPool + QRunnable
so the UI never freezes on adb.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import (
    Property,
    QObject,
    QRunnable,
    QThreadPool,
    Signal,
    Slot,
)

from droidkit.core.adb import Adb, AdbError
from droidkit.core.apps import AppService
from droidkit.core.device import DeviceService
from droidkit.core.fastboot import Fastboot, FastbootError
from droidkit.core.files import FileService
from droidkit.core.screenshot import ScreenshotService
from droidkit.core.tools import ToolNotFoundError


class _Job(QRunnable):
    class _Signals(QObject):
        done = Signal(object)
        failed = Signal(str)

    def __init__(self, fn: Callable[[], Any]) -> None:
        super().__init__()
        self.setAutoDelete(True)
        self.fn = fn
        self.signals = self._Signals()

    def run(self) -> None:
        try:
            result = self.fn()
        except (AdbError, FastbootError, ToolNotFoundError, OSError, RuntimeError) as exc:
            self.signals.failed.emit(str(exc))
            return
        except Exception as exc:
            self.signals.failed.emit(f"Unexpected error: {exc}")
            return
        self.signals.done.emit(result)


class DeviceBridge(QObject):
    devicesChanged = Signal()
    infoChanged = Signal()
    appsChanged = Signal()
    filesChanged = Signal()
    logLine = Signal(str)
    busyChanged = Signal()
    errorChanged = Signal()
    screenshotReady = Signal(str)
    fastbootChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool.globalInstance()
        # Tools are resolved lazily so the app still starts without platform-tools;
        # ToolNotFoundError then surfaces via the error strip / failed signal.
        self._adb: Adb | None = None
        self._fb: Fastboot | None = None
        self._device_svc: DeviceService | None = None
        self._app_svc: AppService | None = None
        self._file_svc: FileService | None = None
        self._shot_svc: ScreenshotService | None = None
        self._serial = ""
        self._busy = False
        self._error = ""
        self._info: dict[str, str] = {}
        self._apps: list[dict[str, str]] = []
        self._files: list[dict[str, Any]] = []
        self._cwd = "/sdcard"
        self._fb_devices: list[str] = []
        self._devices: list[dict[str, str]] = []

    # --- lazy tool accessors ---------------------------------------

    @property
    def adb(self) -> Adb:
        if self._adb is None:
            self._adb = Adb()
        return self._adb

    @property
    def fb(self) -> Fastboot:
        if self._fb is None:
            self._fb = Fastboot()
        return self._fb

    @property
    def device_svc(self) -> DeviceService:
        if self._device_svc is None:
            self._device_svc = DeviceService(self.adb)
        return self._device_svc

    @property
    def app_svc(self) -> AppService:
        if self._app_svc is None:
            self._app_svc = AppService(self.adb)
        return self._app_svc

    @property
    def file_svc(self) -> FileService:
        if self._file_svc is None:
            self._file_svc = FileService(self.adb)
        return self._file_svc

    @property
    def shot_svc(self) -> ScreenshotService:
        if self._shot_svc is None:
            self._shot_svc = ScreenshotService(self.adb)
        return self._shot_svc

    @Property(list, notify=devicesChanged)
    def devices(self) -> list[dict[str, str]]:
        return self._devices

    # --- properties -------------------------------------------------

    @Property(str, notify=infoChanged)
    def serial(self) -> str:
        return self._serial

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=errorChanged)
    def errorMessage(self) -> str:
        return self._error

    @Property(dict, notify=infoChanged)
    def info(self) -> dict[str, str]:
        return self._info

    @Property(list, notify=appsChanged)
    def apps(self) -> list[dict[str, str]]:
        return self._apps

    @Property(list, notify=filesChanged)
    def files(self) -> list[dict[str, Any]]:
        return self._files

    @Property(str, notify=filesChanged)
    def cwd(self) -> str:
        return self._cwd

    @Property(list, notify=fastbootChanged)
    def fastbootDevices(self) -> list[str]:
        return self._fb_devices

    # --- helpers ----------------------------------------------------

    def _set_busy(self, value: bool) -> None:
        self._busy = value
        self.busyChanged.emit()

    def _set_error(self, msg: str) -> None:
        self._error = msg
        self.errorChanged.emit()

    def _submit(self, fn: Callable[[], Any], on_ok: Callable[[Any], None]) -> None:
        job = _Job(fn)
        job.signals.done.connect(on_ok)
        job.signals.failed.connect(self._set_error)
        self._set_busy(True)
        self._set_error("")

        def _finish(*_a: object) -> None:
            self._set_busy(False)

        job.signals.done.connect(_finish)
        job.signals.failed.connect(_finish)
        self._pool.start(job)

    # --- slots ------------------------------------------------------

    @Slot()
    def refreshDevices(self) -> None:
        def work() -> list[dict[str, str]]:
            return self.device_svc.list_devices()

        def ok(devs: object) -> None:
            devices: list[dict[str, str]] = list(devs) if isinstance(devs, list) else []
            self._devices = devices
            self.devicesChanged.emit()
            online = [d for d in devices if d.get("state") == "device"]
            serials = {d.get("serial") for d in devices}
            if online and self._serial not in serials:
                self._serial = online[0].get("serial", "")
                self.refreshInfo()
                self.refreshApps()
            elif not online:
                self._serial = ""
                self._info = {}
                self._apps = []
                self.infoChanged.emit()
                self.appsChanged.emit()

        self._submit(work, ok)

    @Slot()
    def refreshInfo(self) -> None:
        if not self._serial:
            self._info = {}
            self.infoChanged.emit()
            return
        serial = self._serial

        def work() -> dict[str, str]:
            return self.device_svc.info(serial).to_dict()

        def ok(data: object) -> None:
            self._info = data or {}  # type: ignore[assignment]
            self.infoChanged.emit()

        self._submit(work, ok)

    @Slot(str)
    def selectDevice(self, serial: str) -> None:
        self._serial = serial
        self.infoChanged.emit()
        self.refreshInfo()
        self.refreshApps()
        self.refreshFiles(self._cwd)

    @Slot()
    def refreshApps(self) -> None:
        if not self._serial:
            return
        serial = self._serial

        def work() -> list[dict[str, str]]:
            entries = self.app_svc.list_packages(serial, third_party_only=False)
            return [{"package": e.package, "system": str(e.system)} for e in entries]

        def ok(apps: object) -> None:
            self._apps = apps or []  # type: ignore[assignment]
            self.appsChanged.emit()

        self._submit(work, ok)

    @Slot(str)
    def uninstallApp(self, package: str) -> None:
        if not self._serial:
            return
        serial = self._serial

        def work() -> bool:
            return self.app_svc.uninstall(serial, package)

        def ok(success: object) -> None:
            if success:
                self.refreshApps()
            else:
                self._set_error(f"Uninstall failed: {package}")

        self._submit(work, ok)

    @Slot(str)
    def refreshFiles(self, path: str) -> None:
        if not self._serial:
            return
        serial = self._serial
        target = path or "/sdcard"

        def work() -> list[dict[str, Any]]:
            items = self.file_svc.list_dir(serial, target)
            return [
                {"name": f.name, "path": f.path, "isDir": f.is_dir, "size": f.size} for f in items
            ]

        def ok(items: object) -> None:
            self._files = list(items) if isinstance(items, list) else []
            self._cwd = target
            self.filesChanged.emit()

        self._submit(work, ok)

    @Slot(str)
    def goUp(self) -> None:
        cur = self._cwd.rstrip("/")
        parent = str(Path(cur).parent).replace("\\", "/")
        if not parent or parent == ".":
            parent = "/"
        self.refreshFiles(parent)

    @Slot(str, str)
    def pullFile(self, remote: str, local_dir: str) -> None:
        if not self._serial:
            return
        serial = self._serial
        dest = Path(local_dir) / Path(remote).name

        def work() -> str:
            self.file_svc.pull(serial, remote, dest)
            return str(dest)

        def ok(path: object) -> None:
            self._set_error(f"Pulled → {path}")

        self._submit(work, ok)

    @Slot(str, str)
    def pushFile(self, local_path: str, remote_dir: str) -> None:
        if not self._serial:
            return
        serial = self._serial

        def work() -> None:
            self.file_svc.push(serial, Path(local_path), remote_dir)

        def ok(_: object) -> None:
            self.refreshFiles(remote_dir)

        self._submit(work, ok)

    @Slot(result=str)
    def screenshot(self) -> str:
        if not self._serial:
            self._set_error("No device")
            return ""
        serial = self._serial
        dest = Path.home() / "Pictures" / "DroidKit" / f"shot_{serial}.png"

        def work() -> str:
            return str(self.shot_svc.capture(serial, dest))

        def ok(path: object) -> None:
            self.screenshotReady.emit(str(path))

        self._submit(work, ok)
        return str(dest)

    @Slot()
    def refreshFastboot(self) -> None:
        def work() -> list[str]:
            return self.fb.devices()

        def ok(devs: object) -> None:
            self._fb_devices = devs or []  # type: ignore[assignment]
            self.fastbootChanged.emit()

        self._submit(work, ok)

    @Slot()
    def fbRebootSystem(self) -> None:
        def work() -> str:
            res = self.fb.reboot_system()
            return res.stdout or res.stderr

        self._submit(work, lambda _: self.refreshFastboot())

    @Slot()
    def fbRebootBootloader(self) -> None:
        def work() -> str:
            res = self.fb.reboot_bootloader()
            return res.stdout or res.stderr

        self._submit(work, lambda _: self.refreshFastboot())

    @Slot(result=str)
    def shellSync(self, command: str) -> str:
        """Simple sync shell for the Shell page (small commands only)."""
        if not self._serial:
            return ""
        try:
            res = self.adb.shell(command, serial=self._serial, timeout=15)
            return (res.stdout + res.stderr).strip()
        except (AdbError, RuntimeError, OSError) as exc:
            self._set_error(str(exc))
            return ""
