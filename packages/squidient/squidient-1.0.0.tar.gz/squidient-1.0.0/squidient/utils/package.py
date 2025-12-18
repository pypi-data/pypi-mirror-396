from __future__ import annotations

from importlib.metadata import version, PackageNotFoundError
from packaging.version import Version

import json
import urllib.request
from typing import Optional


_INDEXES = {
    "pypi": "https://pypi.org/pypi",
    "testpypi": "https://test.pypi.org/pypi",
}


def _fetch_latest(
    package: str,
    base_url: str,
    timeout: int = 5
) -> Optional[str]:
    url = f"{base_url}/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.load(r)
        return data["info"]["version"]
    except Exception:
        return None


def check_latest_package_any_index(
    package_name: str,
    timeout: int = 5,
) -> dict:
    """
    Check installed package version against PyPI and TestPyPI.

    Returns a dict with:
        {
            "installed": str,
            "latest": str | None,
            "latest_index": "pypi" | "testpypi" | None,
            "up_to_date": bool,
            "checked": { "pypi": str | None, "testpypi": str | None }
        }
    """
    try:
        installed = version(package_name)
    except PackageNotFoundError:
        raise

    installed_v = Version(installed)

    results = {}
    for name, base in _INDEXES.items():
        results[name] = _fetch_latest(package_name, base, timeout)

    # Determine newest available version across indexes
    latest = None
    latest_index = None

    for idx, ver in results.items():
        if ver is None:
            continue
        v = Version(ver)
        if latest is None or v > latest:
            latest = v
            latest_index = idx

    if latest is None:
        return {
            "installed": installed,
            "latest": None,
            "latest_index": None,
            "up_to_date": True,  # offline-safe
            "checked": results,
        }

    return {
        "installed": installed,
        "latest": str(latest),
        "latest_index": latest_index,
        "up_to_date": installed_v >= latest,
        "checked": results,
    }
