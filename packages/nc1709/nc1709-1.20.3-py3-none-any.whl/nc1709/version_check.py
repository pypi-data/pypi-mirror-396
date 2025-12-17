"""
Version Check - Automatic update notification for NC1709

Checks PyPI for newer versions and notifies users on startup.
Caches the check result to avoid repeated API calls.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Tuple
from packaging import version

# Cache settings
CACHE_DIR = Path.home() / ".nc1709"
CACHE_FILE = CACHE_DIR / "version_cache.json"
CACHE_TTL = 3600  # Check once per hour (reduced from 24h for faster update notifications)


def get_current_version() -> str:
    """Get the currently installed version."""
    from . import __version__
    return __version__


def get_latest_version_from_pypi() -> Optional[str]:
    """Fetch the latest version from PyPI.

    Returns:
        Latest version string or None if fetch fails
    """
    try:
        import urllib.request
        import urllib.error

        url = "https://pypi.org/pypi/nc1709/json"

        # Set a short timeout to not delay startup
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json"}
        )

        with urllib.request.urlopen(request, timeout=3) as response:
            data = json.loads(response.read().decode())
            return data.get("info", {}).get("version")
    except Exception:
        # Silently fail - don't interrupt the user experience
        return None


def load_cache() -> dict:
    """Load the version check cache."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_cache(cache: dict) -> None:
    """Save the version check cache."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass


def check_for_update(force: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
    """Check if a newer version is available.

    Args:
        force: If True, bypass cache and check PyPI directly

    Returns:
        Tuple of (update_available, current_version, latest_version)
    """
    current = get_current_version()

    # Check cache first (unless forced)
    if not force:
        cache = load_cache()
        cache_time = cache.get("timestamp", 0)
        cached_current = cache.get("current_version", "")

        # Invalidate cache if installed version changed (user upgraded/downgraded)
        if cached_current != current:
            force = True
        elif time.time() - cache_time < CACHE_TTL:
            # Use cached result
            latest = cache.get("latest_version")
            if latest:
                try:
                    update_available = version.parse(latest) > version.parse(current)
                    return (update_available, current, latest)
                except Exception:
                    pass

    # Fetch from PyPI
    latest = get_latest_version_from_pypi()

    if latest:
        # Update cache
        save_cache({
            "timestamp": time.time(),
            "latest_version": latest,
            "current_version": current
        })

        try:
            update_available = version.parse(latest) > version.parse(current)
            return (update_available, current, latest)
        except Exception:
            return (False, current, latest)

    return (False, current, None)


def get_update_message(current: str, latest: str) -> str:
    """Generate a user-friendly update message.

    Args:
        current: Current installed version
        latest: Latest available version

    Returns:
        Formatted update message
    """
    return f"""
╭─────────────────────────────────────────────────────────────╮
│  🆕 NC1709 Update Available!                                │
│                                                             │
│  Current version: {current:<10}                              │
│  Latest version:  {latest:<10}                              │
│                                                             │
│  Run to update:  pip install --upgrade nc1709               │
╰─────────────────────────────────────────────────────────────╯
"""


def check_and_notify(quiet: bool = False) -> Optional[str]:
    """Check for updates and return notification message if available.

    This is the main function to call on CLI startup.

    Args:
        quiet: If True, return None even if update available

    Returns:
        Update message string if update available, None otherwise
    """
    if quiet:
        return None

    try:
        update_available, current, latest = check_for_update()

        if update_available and current and latest:
            return get_update_message(current, latest)
    except Exception:
        # Never crash the CLI due to version check
        pass

    return None


def print_update_notification() -> None:
    """Print update notification if available.

    Call this at CLI startup for automatic notifications.
    """
    from .cli_ui import Color

    message = check_and_notify()
    if message:
        print(f"{Color.YELLOW}{message}{Color.RESET}")
