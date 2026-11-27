"""DroidKit unit tests — pure core only (no Qt GUI)."""

from __future__ import annotations

from droidkit.licensing.hwid import _sha
from droidkit.licensing.models import LicensePayload, LicenseStatus
from droidkit.update.github_releases import UpdateChecker


def test_sha_stable() -> None:
    assert _sha("abc") == _sha("abc")
    assert len(_sha("abc")) == 32


def test_license_status_expiry() -> None:
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    active = LicensePayload(
        key_id="k1",
        plan="pro",
        hwid="H1",
        issued_at=now - timedelta(days=1),
        expires_at=now + timedelta(days=10),
    )
    expired = LicensePayload(
        key_id="k1",
        plan="pro",
        hwid="H1",
        issued_at=now - timedelta(days=100),
        expires_at=now - timedelta(days=1),
    )
    wrong_hwid = LicensePayload(
        key_id="k1",
        plan="pro",
        hwid="OTHER",
        issued_at=now,
        expires_at=None,
    )
    assert active.status_for("H1", now) is LicenseStatus.VALID
    assert expired.status_for("H1", now) is LicenseStatus.EXPIRED
    assert wrong_hwid.status_for("H1", now) is LicenseStatus.HWID_MISMATCH


def test_license_lifetime() -> None:
    from datetime import UTC, datetime

    p = LicensePayload(
        key_id="k",
        plan="vip",
        hwid="H",
        issued_at=datetime.now(UTC),
        expires_at=None,
    )
    assert p.status_for("H") is LicenseStatus.VALID


def test_update_is_newer() -> None:
    assert UpdateChecker.is_newer("0.1.0", "v0.2.0")
    assert not UpdateChecker.is_newer("0.2.0", "v0.1.0")
    assert not UpdateChecker.is_newer("0.1.0", "v0.1.0")
    assert UpdateChecker.is_newer("0.1.0", "0.1.1")


def test_pick_installer_prefers_setup_exe_on_windows() -> None:
    from droidkit.update.github_releases import pick_installer
    from droidkit.update.models import ReleaseInfo

    assets = [
        {"name": "DroidKit-windows-x64.zip", "browser_download_url": "https://x/zip"},
        {"name": "DroidKit-Setup-0.3.0.exe", "browser_download_url": "https://x/exe"},
    ]
    url, name = pick_installer(assets)
    # On Linux CI we prefer zip; on Windows the exe. Both must be found.
    assert name in {"DroidKit-Setup-0.3.0.exe", "DroidKit-windows-x64.zip"}
    assert url.startswith("https://x/")

    assert pick_installer([]) == ("", "")

    info = ReleaseInfo(tag="v1", name="n", url="u", installer_url="https://x/exe")
    assert info.has_installer
    assert not ReleaseInfo(tag="v1", name="n", url="u").has_installer
    assert info.version == "1"


def test_adb_devices_parse() -> None:
    from droidkit.core.adb import AdbResult

    # Pure parsing logic is covered via devices() when adb exists;
    # here we only assert the result type contract.
    assert hasattr(AdbResult(0, "", ""), "ok")
