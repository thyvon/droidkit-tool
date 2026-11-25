#!/usr/bin/env bash
# Local release build (Linux or WSL). Windows: scripts/build_windows.ps1
set -euo pipefail
cd "$(dirname "$0")/.."

python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"

ruff check src tests
ruff format --check src tests || ruff format src tests
mypy src || true
pytest -q

# Bundle official platform-tools (adb + fastboot)
python scripts/fetch_platform_tools.py --os linux --out platform-tools

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name DroidKit \
  --collect-all PySide6 \
  --collect-all droidkit \
  --paths src \
  --add-data "platform-tools:platform-tools" \
  src/droidkit/app.py

echo "Build complete → dist/DroidKit"
