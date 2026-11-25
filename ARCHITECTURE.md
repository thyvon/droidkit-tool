# DroidKit architecture (keep this short — update when structure changes)

## Layers

```
ui/qml/*          →  presentation only
ui/bridge/*       →  QObject facades (the only Qt ↔ domain glue)
licensing|payments|update  →  domain services (httpx, crypto, etc.)
core/*            →  ADB / fastboot / device logic (no Qt)
i18n/*            →  strings
```

Rules:
1. **QML never imports `core`, `licensing`, `payments`, `update`.**
2. **`core` never imports Qt** — keep it unit-testable.
3. New feature = new module under the right package + one bridge method if QML needs it.
4. Secrets / tokens only via env (`DROIDKIT_*`) or user settings — never commit.
5. Prefer small pure functions; I/O at the edges.

## Naming

- Files: `snake_case.py`
- QML: `camelCase.qml`, pages end with `Page.qml`, `objectName` = nav key
- Signals: `pastTenseChanged` (`devicesChanged`)
- Slots for QML: `camelCase`

## Env vars

| Var | Purpose |
|---|---|
| `DROIDKIT_ADB` | Override adb path |
| `DROIDKIT_FASTBOOT` | Override fastboot path |
| `DROIDKIT_LICENSE_URL` | Your license API base |
| `DROIDKIT_BAKONG_TOKEN` | Bakong / relay token |
| `DROIDKIT_BAKONG_BASE_URL` | Custom relay base URL |
| `DROIDKIT_UPDATE_REPO` | `owner/repo` for releases |

## Adding UI text

Add key to **both** `en` and `km` in `i18n/translations.py`, then `Translator.tr("key")` in QML.
