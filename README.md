# DroidKit

Modern Android device toolkit built with **Python 3.12 + PySide6 (Qt Quick/QML)**.

## Features (v0.2.1)

| Module | What it does |
|---|---|
| **Dashboard** | Device info, battery health/temp/voltage, storage, reboot to System/Bootloader/Recovery/Sideload, screenshot |
| **Apps** | List / backup APK / install / uninstall / disable / re-enable packages (system badge + disabled badge) |
| **Shell** | Sync shell commands, **live Logcat** stream, screenshot |
| **Files** | Browse device storage, push / pull |
| **Fastboot** | Device list, reboot system/bootloader (flashing helpers later) |
| **License** | HWID-bound offline license (`license.bin` activation) |
| **Payments** | Bakong KHQR checkout (`bakong-khqr`, MIT) |
| **Updates** | One-click in-app update — downloads the new installer and runs it |
| **i18n** | English + Khmer |

Built for **phone repair benches**: one installer, adb bundled, bloatware disable/enable,
APK backup before uninstall, recovery/sideload reboot without memorizing commands.

## Why better than legacy tools

- **Declarative QML UI** — dark theme, responsive layout, not 20-year-old widgets
- **Typed, tested core** — `core/` is pure Python, no UI imports; easy unit tests
- **Official platform-tools only** — verify SHA256, never ship mystery `adb.exe`
- **Open payments stack** — MIT `bakong-khqr`, no reverse-engineered clients
- **Signed releases** — GitHub Actions build + optional code signing
- **No mystery telemetry** — license checks are explicit and documented

## Quick start

```bash
cd droidkit
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
droidkit
# or: python -m droidkit
```

You need Android **platform-tools** on `PATH`, or set:

```bash
export DROIDKIT_ADB=/path/to/adb
export DROIDKIT_FASTBOOT=/path/to/fastboot
```

## Project layout

```
src/droidkit/
  app.py           # QApplication entry
  core/            # adb, fastboot, device, apps, files, logcat, screenshot
  licensing/       # HWID + signed license
  payments/        # Bakong KHQR wrapper
  update/          # GitHub Releases checker
  i18n/            # en + km translators
  ui/qml/          # Qt Quick UI (pages + components)
```

## Development

```bash
ruff check .
ruff format .
mypy
pytest
```

## Client install (Windows)

1. Download **`DroidKit-Setup-<version>.exe`** from [Releases](https://github.com/thyvon/droidkit-tool/releases)
2. Run it → Next → Next → Finish (creates Desktop + Start Menu shortcuts)
3. Launch **DroidKit** — adb/fastboot are bundled, no extra installs needed
4. Get your `license.bin` from the vendor, then in-app: **License → Select license.bin**

Portable alternative: download `DroidKit-windows-x64.zip`, extract, run `DroidKit.exe`.

> Unsigned builds may show a Windows SmartScreen warning: **More info → Run anyway**.

## Build release (Windows)

```powershell
./scripts/build_windows.ps1
# → dist\DroidKit\ (portable) + dist\DroidKit-Setup-<version>.exe (installer)
```

CI: `.github/workflows/release.yml` builds both on tag push (`v*`).

## License

MIT — do not reuse another product’s name, icon, or closed source.
