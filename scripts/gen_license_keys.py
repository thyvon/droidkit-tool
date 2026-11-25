"""Generate an Ed25519 keypair for licensing.

Usage:
  python scripts/gen_license_keys.py
  # prints public key → paste into licensing/crypto.py DEFAULT_PUBLIC_KEY_B64
  # keeps private.pem OUT of git (already in .gitignore patterns)
"""

from __future__ import annotations

import base64
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> int:
    key = Ed25519PrivateKey.generate()
    priv = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_raw = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    out = Path("private.pem")
    if out.exists():
        print("private.pem already exists — not overwriting.")
    else:
        out.write_bytes(priv)
        print(f"Wrote {out.resolve()}  (DO NOT COMMIT)")

    print("\nPublic key (paste into src/droidkit/licensing/crypto.py):")
    print(base64.b64encode(pub_raw).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
