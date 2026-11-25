"""Auto-update package.

update/
  api.py              Qt facade
  github_releases.py  GitHub Releases check (httpx)
  models.py           ReleaseInfo
"""

from droidkit.update.api import UpdateApi

__all__ = ["UpdateApi"]
