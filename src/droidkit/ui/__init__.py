"""Qt bridge layer.

Rule: QML never imports `core.*` / `licensing.*` directly —
only these QObject facades. Keeps QML thin and Python testable.
"""

from droidkit.ui.bridge.device import DeviceBridge

__all__ = ["DeviceBridge"]
