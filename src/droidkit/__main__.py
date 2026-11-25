"""Make package importable when run as python -m droidkit from src layout."""

from droidkit.app import main

if __name__ == "__main__":
    raise SystemExit(main())
