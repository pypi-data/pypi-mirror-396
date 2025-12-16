"""
Identity Management - User ID, Session ID, Timestamps

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

Every piece of data must be traceable to:
1. User ID - From license key (hash of key, not the key itself)
2. Session ID - UUID generated per session
3. Timestamp - ISO format, UTC

File naming convention:
    {prefix}_{timestamp}_u{user_id}_s{session_id}_{slug}

Examples:
    session_20250115_143022_u8f3a2b1c_s9d4e5f6.json
    output_20250115_143022_u8f3a2b1c_s9d4e5f6_chat-app-design.md
"""

import hashlib
import uuid
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional


@dataclass
class IdentityContext:
    """Context for tracking user and session identity."""
    user_id: str
    session_id: str
    created_at: datetime

    @classmethod
    def create(cls, license_key: Optional[str] = None) -> "IdentityContext":
        """Create a new identity context.

        Args:
            license_key: License key to derive user ID from.
                        If None, uses "anonymous" as user ID.

        Returns:
            New IdentityContext with generated session ID and current timestamp.
        """
        user_id = get_user_id(license_key) if license_key else "anonymous"
        return cls(
            user_id=user_id,
            session_id=generate_session_id(),
            created_at=datetime.now(timezone.utc),
        )


def get_user_id(license_key: str) -> str:
    """Generate user ID from license key (hash, not the key itself).

    Uses first 12 characters of SHA256 hash for brevity while maintaining
    sufficient uniqueness.

    Args:
        license_key: The license key to hash

    Returns:
        12-character hexadecimal user ID

    Example:
        >>> get_user_id("my-license-key-123")
        "8f3a2b1c4d5e"
    """
    if not license_key:
        return "anonymous"

    return hashlib.sha256(license_key.encode()).hexdigest()[:12]


def generate_session_id() -> str:
    """Generate unique session ID.

    Uses first 8 characters of UUID4 hex for brevity.

    Returns:
        8-character hexadecimal session ID

    Example:
        >>> generate_session_id()
        "9d4e5f6a"
    """
    return uuid.uuid4().hex[:8]


def get_timestamp() -> str:
    """Get ISO timestamp for filenames (UTC).

    Format: YYYYMMDD_HHMMSS

    Returns:
        Timestamp string suitable for filenames

    Example:
        >>> get_timestamp()
        "20250115_143022"
    """
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def get_iso_timestamp() -> str:
    """Get full ISO 8601 timestamp (UTC).

    Returns:
        Full ISO timestamp with timezone

    Example:
        >>> get_iso_timestamp()
        "2025-01-15T14:30:22Z"
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text: str, max_length: int = 30) -> str:
    """Convert text to filename-safe slug.

    Args:
        text: Text to convert
        max_length: Maximum length of resulting slug

    Returns:
        Lowercase, hyphenated slug safe for filenames

    Example:
        >>> slugify("Design a Chat Application Database!")
        "design-a-chat-application-dat"
    """
    if not text:
        return ""

    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars except hyphens
    slug = re.sub(r'[\s_]+', '-', slug)  # Replace spaces/underscores with hyphens
    slug = re.sub(r'-+', '-', slug)  # Collapse multiple hyphens
    slug = slug.strip('-')  # Remove leading/trailing hyphens

    return slug[:max_length]


def make_filename(
    prefix: str,
    user_id: str,
    session_id: str,
    suffix: str = "",
    extension: str = ""
) -> str:
    """Generate traceable filename with identity context.

    Format: {prefix}_{timestamp}_u{user_id}_s{session_id}_{slug}.{ext}

    Args:
        prefix: File type prefix (e.g., "session", "output", "quota")
        user_id: User ID (12-char hash)
        session_id: Session ID (8-char UUID)
        suffix: Optional descriptive suffix (will be slugified)
        extension: File extension without dot (e.g., "json", "md")

    Returns:
        Full filename with traceability info

    Example:
        >>> make_filename("output", "8f3a2b1c4d5e", "9d4e5f6a",
        ...               suffix="chat app design", extension="md")
        "output_20250115_143022_u8f3a2b1c4d5e_s9d4e5f6a_chat-app-design.md"
    """
    ts = get_timestamp()
    parts = [prefix, ts, f"u{user_id}", f"s{session_id}"]

    if suffix:
        slug = slugify(suffix)
        if slug:
            parts.append(slug)

    filename = "_".join(parts)

    if extension:
        filename = f"{filename}.{extension.lstrip('.')}"

    return filename


def make_session_filename(user_id: str, session_id: str) -> str:
    """Generate session filename.

    Args:
        user_id: User ID
        session_id: Session ID

    Returns:
        Session filename (JSON)
    """
    return make_filename("session", user_id, session_id, extension="json")


def make_output_filename(user_id: str, session_id: str, query: str) -> str:
    """Generate output filename for markdown export.

    Args:
        user_id: User ID
        session_id: Session ID
        query: The problem/query text (will be slugified)

    Returns:
        Output filename (Markdown)
    """
    return make_filename("output", user_id, session_id, suffix=query, extension="md")


def make_log_filename() -> str:
    """Generate daily log filename.

    Returns:
        Log filename for today (e.g., "consult_20250115.log")
    """
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"consult_{date}.log"


def parse_filename_identity(filename: str) -> Optional[dict]:
    """Extract identity info from a traceable filename.

    Args:
        filename: Filename to parse

    Returns:
        Dict with user_id, session_id, timestamp if parseable, else None

    Example:
        >>> parse_filename_identity("output_20250115_143022_u8f3a2b1c_s9d4e5f6_slug.md")
        {"timestamp": "20250115_143022", "user_id": "8f3a2b1c", "session_id": "9d4e5f6"}
    """
    pattern = r'.*_(\d{8}_\d{6})_u([a-f0-9]+)_s([a-f0-9]+)'
    match = re.match(pattern, filename)

    if match:
        return {
            "timestamp": match.group(1),
            "user_id": match.group(2),
            "session_id": match.group(3),
        }

    return None
