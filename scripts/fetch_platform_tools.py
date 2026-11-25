"""Download official Google platform-tools into ./platform-tools (for bundling).

Usage:
  python scripts/fetch_platform_tools.py            # windows zip when on Windows
  python scripts/fetch_platform_tools.py --os linux # force a platform

Only the files needed by DroidKit are kept: adb, fastboot and Windows DLLs.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

URLS = {
    "windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
    "linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
    "darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
}

KEEP = {
    "adb",
    "adb.exe",
    "fastboot",
    "fastboot.exe",
    "AdbWinApi.dll",
    "AdbWinUsbApi.dll",
    "NOTICE.txt",
}


def _default_os() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "darwin"
    return "linux"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--os", choices=sorted(URLS), default=_default_os())
    p.add_argument("--out", type=Path, default=Path("platform-tools"))
    p.add_argument(
        "--sha256", default="", help="expected sha256 of the zip (uppercase or lowercase)"
    )
    args = p.parse_args()

    url = URLS[args.os]
    print(f"Downloading {url} ...")
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = resp.read()

    digest = hashlib.sha256(data).hexdigest().upper()
    print(f"zip sha256: {digest}")
    if args.sha256 and digest != args.sha256.upper():
        print("ERROR: sha256 mismatch", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            name = Path(info.filename).name
            if info.is_dir() or name not in KEEP:
                continue
            target = args.out / name
            target.write_bytes(zf.read(info))
            target.chmod(0o755 if name in {"adb", "fastboot"} else 0o644)
            print(f"  extracted {target}")

    print(f"Done → {args.out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
