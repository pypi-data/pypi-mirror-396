"""
Auto-update module for LMAPP
Checks for new versions and provides update notifications
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import requests
from loguru import logger


class VersionChecker:
    """Check for LMAPP updates on PyPI"""

    PYPI_URL = "https://pypi.org/pypi/lmapp/json"
    CACHE_DIR = Path.home() / ".lmapp" / "cache"
    VERSION_CACHE_FILE = CACHE_DIR / "version_check.json"
    CACHE_DURATION = timedelta(hours=24)  # Check daily

    def __init__(self):
        self.cache_dir = self.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_latest_version(self) -> Optional[str]:
        """Fetch latest LMAPP version from PyPI"""
        try:
            response = requests.get(self.PYPI_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data["info"]["version"]
        except Exception as e:
            logger.debug(f"Failed to fetch latest version: {e}")
            return None

    def get_cached_version(self) -> Optional[dict]:
        """Get cached version check data"""
        if not self.VERSION_CACHE_FILE.exists():
            return None

        try:
            with open(self.VERSION_CACHE_FILE) as f:
                data = json.load(f)

            # Check if cache is still valid
            check_time = datetime.fromisoformat(data.get("checked_at", ""))
            if datetime.now() - check_time < self.CACHE_DURATION:
                return data

            return None
        except Exception as e:
            logger.debug(f"Failed to read version cache: {e}")
            return None

    def save_version_cache(self, latest_version: str):
        """Save version check to cache"""
        try:
            cache_data = {
                "latest_version": latest_version,
                "checked_at": datetime.now().isoformat(),
                "notified": False,
            }
            with open(self.VERSION_CACHE_FILE, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.debug(f"Failed to save version cache: {e}")

    def check_for_updates(self, current_version: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an update is available

        Returns:
            Tuple of (update_available, latest_version)
        """
        # Check cache first
        cached = self.get_cached_version()
        if cached and not cached.get("notified"):
            latest = cached["latest_version"]
        else:
            latest = self.get_latest_version()
            if latest:
                self.save_version_cache(latest)

        if not latest:
            return False, None

        return self._compare_versions(current_version, latest), latest

    @staticmethod
    def _compare_versions(current: str, latest: str) -> bool:
        """Compare version strings (simple semver comparison)"""
        try:
            curr_parts = [int(x) for x in current.split(".")]
            latest_parts = [int(x) for x in latest.split(".")]

            # Pad to same length
            while len(curr_parts) < len(latest_parts):
                curr_parts.append(0)
            while len(latest_parts) < len(curr_parts):
                latest_parts.append(0)

            return tuple(latest_parts) > tuple(curr_parts)
        except (ValueError, AttributeError):
            return False


class AutoUpdater:
    """Handle automatic updates for LMAPP"""

    def __init__(self, current_version: str):
        self.current_version = current_version
        self.checker = VersionChecker()

    def check_and_notify(self) -> bool:
        """
        Check for updates and notify user if available

        Returns:
            True if update is available, False otherwise
        """
        update_available, latest = self.checker.check_for_updates(self.current_version)

        if update_available and latest:
            self._show_update_prompt(latest)
            return True

        return False

    @staticmethod
    def _show_update_prompt(latest_version: str):
        """Display update notification to user"""
        from rich.console import Console

        console = Console()
        console.print(f"\n[bold yellow]⬆️  Update available: LMAPP {latest_version}[/]")
        console.print("[dim]To update, run:[/] [bold]pip install --upgrade lmapp[/]\n")


def check_for_updates(current_version: str) -> None:
    """Convenience function to check and notify about updates"""
    updater = AutoUpdater(current_version)
    updater.check_and_notify()


__all__ = ["VersionChecker", "AutoUpdater", "check_for_updates"]
