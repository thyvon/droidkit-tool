"""Ed25519 license signatures.

Public key is embedded (or loaded from package data).
Private key NEVER ships — only used on your license server / CLI.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from droidkit.licensing.models import LicensePayload

# Ed25519 public key (base64 raw 32 bytes). Private key stays out of the app.
DEFAULT_PUBLIC_KEY_B64 = "LUPYz0z36wiqB61NxfQO+6F9f7VFUWdnnim3BnIvDZk="


class LicenseCryptoError(ValueError):
    pass


def load_public_key(pem_or_b64: str | None = None) -> Ed25519PublicKey:
    raw = (pem_or_b64 or DEFAULT_PUBLIC_KEY_B64).strip()
    if raw.startswith("-----BEGIN"):
        return serialization.load_pem_public_key(raw.encode())  # type: ignore[return-value]
    import base64

    try:
        data = base64.b64decode(raw, validate=True)
    except Exception as exc:
        raise LicenseCryptoError(f"Invalid public key encoding: {exc}") from exc
    if len(data) != 32:
        raise LicenseCryptoError(f"Ed25519 public key must be 32 bytes, got {len(data)}")
    return Ed25519PublicKey.from_public_bytes(data)


def sign_license(private_pem: str | bytes, payload: dict[str, Any]) -> bytes:
    key = serialization.load_pem_private_key(
        private_pem if isinstance(private_pem, bytes) else private_pem.encode(),
        password=None,
    )
    if not isinstance(key, Ed25519PrivateKey):
        raise LicenseCryptoError("Expected Ed25519 private key")
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return key.sign(body)


def verify_and_parse(
    body: bytes,
    signature: bytes,
    *,
    public_key_b64: str | None = None,
) -> LicensePayload:
    pub = load_public_key(public_key_b64)
    try:
        pub.verify(signature, body)
    except InvalidSignature as exc:
        raise LicenseCryptoError("License signature verification failed") from exc
    data = json.loads(body)
    return _payload_from_dict(data)


def _payload_from_dict(data: dict[str, Any]) -> LicensePayload:
    def _dt(key: str) -> datetime | None:
        val = data.get(key)
        if not val:
            return None
        dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)

    return LicensePayload(
        key_id=str(data.get("key_id", "")),
        plan=str(data.get("plan", "standard")),
        hwid=str(data.get("hwid", "")),
        issued_at=_dt("issued_at") or datetime.now(UTC),
        expires_at=_dt("expires_at"),
        features=tuple(data.get("features") or ()),
    )


def issue_license(
    private_pem: str | bytes,
    *,
    key_id: str,
    plan: str,
    hwid: str,
    days: int | None = 365,
    features: list[str] | None = None,
) -> tuple[bytes, bytes]:
    """Return (body_json, signature) — write both to disk or base64-encode."""
    now = datetime.now(UTC)
    expires = None if days is None else now.timestamp() + days * 86400
    payload: dict[str, Any] = {
        "key_id": key_id,
        "plan": plan,
        "hwid": hwid,
        "issued_at": now.isoformat(),
        "expires_at": None if expires is None else datetime.fromtimestamp(expires, UTC).isoformat(),
        "features": features or [],
    }
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return body, sign_license(private_pem, payload)


def save_license(directory: Path, body: bytes, signature: bytes) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "license.bin"
    # simple container: 4-byte sig len + sig + body
    path.write_bytes(len(signature).to_bytes(4, "big") + signature + body)
    return path


def load_license(path: Path, *, public_key_b64: str | None = None) -> LicensePayload:
    raw = path.read_bytes()
    if len(raw) < 4:
        raise LicenseCryptoError("License file truncated")
    sig_len = int.from_bytes(raw[:4], "big")
    sig, body = raw[4 : 4 + sig_len], raw[4 + sig_len :]
    return verify_and_parse(body, sig, public_key_b64=public_key_b64)
