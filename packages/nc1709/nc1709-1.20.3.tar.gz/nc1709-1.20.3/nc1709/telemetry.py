"""
NC1709 Telemetry Module

Lightweight, non-blocking telemetry for tracking CLI usage.
All data is anonymous and users can opt-out via config.

Design principles:
- Fire-and-forget: Never blocks the main thread
- Fail silently: Network errors don't affect CLI
- Privacy-first: No PII, hashed machine IDs
- Opt-out: Users can disable via NC1709_TELEMETRY=false
"""

import hashlib
import os
import platform
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError
import json

# Telemetry endpoint - points to nc1709 server
TELEMETRY_ENDPOINT = "https://nc1709.lafzusa.com/nc1709/telemetry"

# Cache file for machine ID persistence
TELEMETRY_CACHE_FILE = Path.home() / ".nc1709" / ".telemetry_id"


def _get_machine_id() -> str:
    """
    Get a persistent, anonymous machine identifier.
    Creates a random UUID on first run and caches it.
    """
    try:
        if TELEMETRY_CACHE_FILE.exists():
            return TELEMETRY_CACHE_FILE.read_text().strip()

        # Generate new ID
        machine_id = str(uuid.uuid4())

        # Cache it
        TELEMETRY_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        TELEMETRY_CACHE_FILE.write_text(machine_id)

        return machine_id
    except Exception:
        # Fallback: hash of hostname + username (still anonymous)
        raw = f"{platform.node()}-{os.getenv('USER', 'unknown')}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled via environment or config."""
    # Environment variable takes precedence
    env_val = os.getenv("NC1709_TELEMETRY", "").lower()
    if env_val in ("false", "0", "no", "off", "disabled"):
        return False
    if env_val in ("true", "1", "yes", "on", "enabled"):
        return True

    # Check config file
    config_file = Path.home() / ".nc1709" / "config.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            return config.get("telemetry_enabled", True)
        except Exception:
            pass

    # Default: enabled
    return True


def _get_system_info() -> dict:
    """Collect anonymous system information."""
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "arch": platform.machine(),
    }


def _send_telemetry_sync(event_type: str, data: dict, timeout: float = 2.0) -> bool:
    """
    Send telemetry event synchronously.
    Returns True if successful, False otherwise.
    """
    try:
        from nc1709 import __version__
    except ImportError:
        __version__ = "unknown"

    payload = {
        "machine_id": _get_machine_id(),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": __version__,
        "system": _get_system_info(),
        "data": data,
    }

    try:
        request = Request(
            TELEMETRY_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"nc1709/{__version__}",
            },
            method="POST",
        )

        with urlopen(request, timeout=timeout) as response:
            return response.status == 200
    except (URLError, TimeoutError, Exception):
        # Fail silently - telemetry should never break the CLI
        return False


def _send_async(event_type: str, data: dict):
    """Fire-and-forget telemetry in a daemon thread."""
    if not _is_telemetry_enabled():
        return

    thread = threading.Thread(
        target=_send_telemetry_sync,
        args=(event_type, data),
        daemon=True,  # Won't block program exit
    )
    thread.start()


# ============================================================================
# Public API
# ============================================================================

class Telemetry:
    """
    Telemetry client for NC1709.

    Usage:
        from nc1709.telemetry import telemetry

        # Track CLI startup
        telemetry.track_startup()

        # Track session
        telemetry.track_session(duration=120, messages=5, model="qwen2.5-coder:7b")

        # Track feature usage
        telemetry.track_feature("plan_mode")

        # Track errors (anonymous)
        telemetry.track_error("ConnectionError", "Failed to connect to Ollama")
    """

    _instance = None
    _session_start: Optional[float] = None
    _message_count: int = 0
    _tool_calls: dict = {}
    _errors: list = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def enabled(self) -> bool:
        """Check if telemetry is enabled."""
        return _is_telemetry_enabled()

    @property
    def machine_id(self) -> str:
        """Get the anonymous machine ID."""
        return _get_machine_id()

    def track_startup(self, mode: str = "cli"):
        """
        Track CLI startup event.
        Called once when nc1709 starts.
        """
        self._session_start = time.time()
        self._message_count = 0
        self._tool_calls = {}
        self._errors = []

        _send_async("startup", {
            "mode": mode,  # cli, server, remote
        })

    def track_session_end(self, model: Optional[str] = None):
        """
        Track session end with aggregated stats.
        Called when nc1709 exits.
        """
        duration = 0
        if self._session_start:
            duration = int(time.time() - self._session_start)

        _send_async("session_end", {
            "duration_seconds": duration,
            "message_count": self._message_count,
            "model": model or "unknown",
            "tool_usage": self._tool_calls,
            "error_count": len(self._errors),
        })

    def track_message(self):
        """Track a user message (just increment counter)."""
        self._message_count += 1

    def track_tool_call(self, tool_name: str):
        """Track tool usage (aggregate counts)."""
        self._tool_calls[tool_name] = self._tool_calls.get(tool_name, 0) + 1

    def track_feature(self, feature_name: str, metadata: Optional[dict] = None):
        """
        Track feature usage.

        Examples:
            telemetry.track_feature("plan_mode")
            telemetry.track_feature("mcp_server", {"server": "filesystem"})
        """
        _send_async("feature", {
            "feature": feature_name,
            "metadata": metadata or {},
        })

    def track_error(self, error_type: str, message: str = ""):
        """
        Track errors anonymously.
        Only stores error type and sanitized message (no stack traces with paths).
        """
        # Sanitize message - remove potential PII
        sanitized = message[:100] if message else ""
        # Remove file paths
        import re
        sanitized = re.sub(r'/[^\s]+', '[PATH]', sanitized)
        sanitized = re.sub(r'C:\\[^\s]+', '[PATH]', sanitized)

        self._errors.append(error_type)

        _send_async("error", {
            "error_type": error_type,
            "message": sanitized,
        })

    def track_install(self):
        """
        Track first-time installation.
        Called once per machine.
        """
        install_marker = Path.home() / ".nc1709" / ".install_tracked"

        if install_marker.exists():
            return  # Already tracked

        _send_async("install", {
            "source": os.getenv("NC1709_INSTALL_SOURCE", "pip"),
        })

        try:
            install_marker.parent.mkdir(parents=True, exist_ok=True)
            install_marker.touch()
        except Exception:
            pass

    def track_upgrade(self, from_version: str, to_version: str):
        """Track version upgrades."""
        _send_async("upgrade", {
            "from_version": from_version,
            "to_version": to_version,
        })


# Singleton instance
telemetry = Telemetry()


# ============================================================================
# Convenience functions
# ============================================================================

def disable_telemetry():
    """Disable telemetry by setting config."""
    config_file = Path.home() / ".nc1709" / "config.json"

    try:
        config = {}
        if config_file.exists():
            config = json.loads(config_file.read_text())

        config["telemetry_enabled"] = False

        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps(config, indent=2))

        return True
    except Exception:
        return False


def enable_telemetry():
    """Enable telemetry by setting config."""
    config_file = Path.home() / ".nc1709" / "config.json"

    try:
        config = {}
        if config_file.exists():
            config = json.loads(config_file.read_text())

        config["telemetry_enabled"] = True

        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps(config, indent=2))

        return True
    except Exception:
        return False


def get_telemetry_status() -> dict:
    """Get current telemetry status for debugging."""
    return {
        "enabled": _is_telemetry_enabled(),
        "machine_id": _get_machine_id(),
        "endpoint": TELEMETRY_ENDPOINT,
    }
