"""CLI helper: issue a license.bin (run offline on your machine).

python scripts/issue_license.py --key-id ABC --plan vip --hwid <HWID> --days 365
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running without install
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from droidkit.licensing.crypto import issue_license, save_license


def main() -> int:
    p = argparse.ArgumentParser(description="Issue a DroidKit license")
    p.add_argument("--private-key", default="private.pem", type=Path)
    p.add_argument("--key-id", required=True)
    p.add_argument("--plan", default="standard")
    p.add_argument("--hwid", required=True)
    p.add_argument("--days", type=int, default=365, help="0 = lifetime")
    p.add_argument("--out", type=Path, default=Path("license.bin"))
    args = p.parse_args()

    if not args.private_key.is_file():
        print(f"Missing private key: {args.private_key}", file=sys.stderr)
        return 1

    body, sig = issue_license(
        args.private_key.read_bytes(),
        key_id=args.key_id,
        plan=args.plan,
        hwid=args.hwid,
        days=None if args.days == 0 else args.days,
    )
    path = save_license(args.out.parent, body, sig)
    # save_license always writes license.bin — rename if custom out
    if args.out.name != "license.bin":
        target = args.out
        path.replace(target)
        path = target
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
