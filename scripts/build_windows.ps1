# Windows release build → dist\DroidKit\ + dist\DroidKit-Setup-<version>.exe
# Usage: powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"

ruff check src tests
ruff format src tests
mypy src
pytest -q

# Bundle official platform-tools (adb.exe + DLLs + fastboot)
python scripts\fetch_platform_tools.py --os windows --out platform-tools

pyinstaller `
    --noconfirm --clean --windowed `
    --name DroidKit `
    --collect-all PySide6 `
    --collect-all droidkit `
    --paths src `
    --add-data "platform-tools;platform-tools" `
    src\droidkit\app.py

# Inno Setup installer (single setup.exe for the client)
$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $iscc) {
    $isccPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (Test-Path $isccPath) { $iscc = $isccPath }
}
if ($iscc) {
    $version = (Select-String -Path pyproject.toml -Pattern 'version = "(.+)"').Matches[0].Groups[1].Value
    & $iscc "/DMyAppVersion=$version" "/DMyAppExeDir=$root\dist\DroidKit" installer\droidkit.iss
    Write-Host "Installer → dist\DroidKit-Setup-$version.exe"
} else {
    Write-Warning "Inno Setup (iscc.exe) not found — skipping installer. Install from https://jrsoftware.org/"
}

Write-Host "Build complete → dist\DroidKit\"
