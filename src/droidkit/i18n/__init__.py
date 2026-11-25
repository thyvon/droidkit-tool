"""i18n — English + Khmer.

Adding a language:
  1. Add a key table in `translations.py`
  2. Append the locale code to `Translator.SUPPORTED`
"""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from droidkit.i18n.translations import STRINGS


class Translator(QObject):
    """Context property `Translator` — QML calls `Translator.tr(key)`."""

    languageChanged = Signal()

    SUPPORTED: tuple[str, ...] = ("en", "km")

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._lang = "en"

    @Property(str, notify=languageChanged)
    def language(self) -> str:
        return self._lang

    @Property(list, notify=languageChanged)
    def supported(self) -> list[str]:
        return list(self.SUPPORTED)

    @Slot(str)
    def setLanguage(self, lang: str) -> None:
        if lang not in self.SUPPORTED or lang == self._lang:
            return
        self._lang = lang
        self.languageChanged.emit()

    @Slot(str, result=str)
    def tr(self, key: str) -> str:  # type: ignore[override]
        table = STRINGS.get(self._lang) or STRINGS["en"]
        return table.get(key, STRINGS["en"].get(key, key))


__all__ = ["Translator"]
