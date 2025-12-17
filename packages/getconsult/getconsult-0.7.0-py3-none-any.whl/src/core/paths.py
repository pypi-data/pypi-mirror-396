"""
Consult Home Directory Management

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

All Consult data lives in ~/.consult/ by default:

~/.consult/
    config.yaml              # User preferences (NO secrets here)
    license                  # License key only (no API keys)
    .env                     # API keys (BYOK) - 600 permissions
    sessions/                # Session persistence
    outputs/                 # Markdown exports with full traceability
    cache/                   # Rate limit tracking, license cache
    logs/                    # Debug logs (NEVER contains API keys)
"""

from pathlib import Path
import os


def get_consult_home() -> Path:
    """Get Consult home directory, creating if needed.

    Can be overridden with CONSULT_HOME environment variable.
    Default: ~/.consult
    """
    home = Path(os.getenv("CONSULT_HOME", Path.home() / ".consult"))
    home.mkdir(parents=True, exist_ok=True)
    return home


def get_config_path() -> Path:
    """Get path to user config file (~/.consult/config.yaml)."""
    return get_consult_home() / "config.yaml"


def get_license_path() -> Path:
    """Get path to license key file (~/.consult/license)."""
    return get_consult_home() / "license"


def get_env_path() -> Path:
    """Get path to .env file in Consult home (~/.consult/.env).

    This is a fallback location for API keys when not found in project directory.
    File should have 600 permissions (user read/write only).
    """
    return get_consult_home() / ".env"


def get_sessions_dir() -> Path:
    """Get sessions directory (~/.consult/sessions/), creating if needed."""
    path = get_consult_home() / "sessions"
    path.mkdir(exist_ok=True)
    return path


def get_outputs_dir() -> Path:
    """Get outputs directory (~/.consult/outputs/), creating if needed.

    Markdown exports go here with full traceability metadata.
    """
    path = get_consult_home() / "outputs"
    path.mkdir(exist_ok=True)
    return path


def get_cache_dir() -> Path:
    """Get cache directory (~/.consult/cache/), creating if needed.

    Stores rate limit tracking and license cache.
    """
    path = get_consult_home() / "cache"
    path.mkdir(exist_ok=True)
    return path


def get_logs_dir() -> Path:
    """Get logs directory (~/.consult/logs/), creating if needed.

    Debug logs go here. NEVER contains API keys (redacted).
    """
    path = get_consult_home() / "logs"
    path.mkdir(exist_ok=True)
    return path


def ensure_consult_structure() -> Path:
    """Ensure full Consult directory structure exists.

    Call this on first run to set up ~/.consult with all subdirectories.
    Returns the Consult home path.
    """
    home = get_consult_home()
    get_sessions_dir()
    get_outputs_dir()
    get_cache_dir()
    get_logs_dir()
    return home


def get_quota_path(user_id: str) -> Path:
    """Get path to user's quota tracking file."""
    return get_cache_dir() / f"quota_{user_id}.json"


def get_license_cache_path() -> Path:
    """Get path to license cache file."""
    return get_cache_dir() / "license_cache.json"
