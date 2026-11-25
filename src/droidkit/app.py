"""Application entrypoint."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from droidkit import __app_name__, __version__
from droidkit.i18n import Translator
from droidkit.licensing.api import LicenseApi
from droidkit.payments.api import PaymentsApi
from droidkit.ui.bridge import DeviceBridge
from droidkit.update.api import UpdateApi


def _qml_dir() -> Path:
    return Path(__file__).resolve().parent / "ui" / "qml"


def main(argv: list[str] | None = None) -> int:
    # Must be set before Qt initializes (WSLg / X11 without GPU)
    os.environ.setdefault("QT_QUICK_BACKEND", "software")

    argv = list(sys.argv if argv is None else argv)
    QGuiApplication.setApplicationName(__app_name__)
    QGuiApplication.setApplicationVersion(__version__)
    QGuiApplication.setOrganizationName("DroidKit")

    app = QGuiApplication(argv)

    translator = Translator(app)

    engine = QQmlApplicationEngine()
    ctx = engine.rootContext()
    ctx.setContextProperty("AppVersion", __version__)
    ctx.setContextProperty("AppName", __app_name__)
    ctx.setContextProperty("Translator", translator)
    # Keep Python references — PySide does not keep context-property objects alive.
    device_bridge = DeviceBridge()
    license_api = LicenseApi()
    payments_api = PaymentsApi()
    update_api = UpdateApi()
    ctx.setContextProperty("DeviceBridge", device_bridge)
    ctx.setContextProperty("LicenseApi", license_api)
    ctx.setContextProperty("PaymentsApi", payments_api)
    ctx.setContextProperty("UpdateApi", update_api)

    qml = _qml_dir() / "Main.qml"
    qml_url = QUrl.fromLocalFile(str(qml))

    # QML bindings that call Translator.tr() have no property dependency on
    # the language, so they never re-evaluate. Recreate the UI instead.
    def _reload_qml() -> None:
        old_roots = engine.rootObjects()
        engine.load(qml_url)
        for obj in old_roots:
            obj.setProperty("visible", False)
            obj.deleteLater()

    translator.languageChanged.connect(lambda: QTimer.singleShot(0, _reload_qml))

    engine.load(qml_url)
    if not engine.rootObjects():
        print(f"Failed to load QML: {qml}", file=sys.stderr)
        return 1
    code = app.exec()
    # Tear down QML while context-property objects are still alive;
    # otherwise their bindings fire during GC and hang shutdown.
    for obj in engine.rootObjects():
        obj.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    return code
