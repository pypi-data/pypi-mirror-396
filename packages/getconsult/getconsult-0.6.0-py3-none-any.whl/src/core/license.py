"""
License and Tier Management

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

Tier System:
- FREE_BYOK: $0/month, 3 queries/day, user provides API keys
- PRO_BYOK: $9 USD/month, 100 queries/day, user provides API keys
- PRO_PREMIUM: Deferred (bundled API credits, too expensive with SOTA models)
- ENTERPRISE: Deferred (Docker, SSO/SAML support)

License Key Formats:

  CSL1 (v1 - legacy, still supported):
    CSL1_{tier}_{issued_ts}_{expires_ts}_{nonce}_{checksum}

  CSL2 (v2 - current, with customer tracking):
    CSL2_{tier}_{issued_ts}_{expires_ts}_{customer_hash}_{nonce}_{checksum}

  Fields:
  - CSL1/CSL2: Version prefix
  - tier: pro, free, ent, or prem
  - issued_ts: Unix timestamp when key was generated
  - expires_ts: Unix timestamp when key expires (0 = never)
  - customer_hash: (CSL2 only) First 8 chars of SHA256(stripe_customer_id)
  - nonce: 8-char random hex string (prevents guessing)
  - checksum: First 12 chars of HMAC-SHA256(secret, payload)

Validation:
  - Reconstruct payload from components
  - Compute HMAC and compare checksums
  - Verify not expired
  - No server roundtrip required (offline-first)
  - Optional: check revocation list if online
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Tuple
import json
import os
import hmac
import hashlib
import secrets
import time

from .paths import get_license_path, get_license_cache_path, get_logs_dir
from .identity import get_user_id
from .security import get_contextual_logger

# Module logger
_logger = None


def _get_logger():
    """Get or create the license logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.license", log_file=str(log_file))
    return _logger


# =============================================================================
# LICENSE KEY CRYPTOGRAPHY
# =============================================================================

# Signing secret - embedded for offline validation.
# Yes, extractable via reverse engineering. That's acceptable because:
# 1. At $9/mo, effort to crack > cost to pay
# 2. BYOK users already trust us with their API keys
# 3. Anyone who extracts this wasn't going to pay anyway
# 4. Real value is the tool, not the DRM
_SIGNING_SECRET = b"csl_k7m2v9x4p1n8q5w3r6t0y2u4i8o1a3s5d7f9g2h4j6"

# License version prefixes
_LICENSE_VERSION_V1 = "CSL1"
_LICENSE_VERSION_V2 = "CSL2"
_SUPPORTED_VERSIONS = {_LICENSE_VERSION_V1, _LICENSE_VERSION_V2}

# Tier codes (short for compact keys)
_TIER_CODES = {
    "pro": "pro_byok",
    "free": "free_byok",
    "ent": "enterprise",
    "prem": "pro_premium",
}
_TIER_TO_CODE = {v: k for k, v in _TIER_CODES.items()}


def _compute_checksum(payload: str) -> str:
    """Compute HMAC-SHA256 checksum of payload, return first 12 chars."""
    sig = hmac.new(_SIGNING_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return sig[:12]


def generate_license_key(
    tier: str = "pro",
    expires_days: Optional[int] = 365,
    _secret_override: bytes = None,  # For testing only
) -> str:
    """Generate a signed license key.

    This function is for key generation (run by you, not users).

    Args:
        tier: One of 'pro', 'free', 'ent', 'prem'
        expires_days: Days until expiry (None = never expires)
        _secret_override: Override signing secret (testing only)

    Returns:
        License key string like: CSL1_pro_1702345678_1733881678_x7k2m9p4_a1b2c3d4e5f6
    """
    if tier not in _TIER_CODES:
        raise ValueError(f"Invalid tier: {tier}. Must be one of: {list(_TIER_CODES.keys())}")

    issued_ts = int(time.time())
    expires_ts = int(time.time() + (expires_days * 86400)) if expires_days else 0
    nonce = secrets.token_hex(4)  # 8 chars

    # Payload for signing (everything except checksum)
    payload = f"{_LICENSE_VERSION_V1}_{tier}_{issued_ts}_{expires_ts}_{nonce}"

    # Compute checksum
    secret = _secret_override or _SIGNING_SECRET
    sig = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()[:12]

    return f"{payload}_{sig}"


def validate_license_key(license_key: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate a license key's cryptographic signature and expiry.

    Supports both CSL1 (6 parts) and CSL2 (7 parts) formats.

    Args:
        license_key: The license key to validate

    Returns:
        Tuple of (is_valid, tier_code, error_message)
        - is_valid: True if key is cryptographically valid and not expired
        - tier_code: The tier code ('pro', 'free', etc.) if valid, None otherwise
        - error_message: Description of why validation failed, None if valid
    """
    if not license_key:
        return False, None, "Empty license key"

    parts = license_key.strip().split("_")

    # Determine format by part count
    # CSL1: version_tier_issued_expires_nonce_checksum = 6 parts
    # CSL2: version_tier_issued_expires_customerHash_nonce_checksum = 7 parts
    if len(parts) == 6:
        version, tier, issued_str, expires_str, nonce, provided_checksum = parts
        customer_hash = None
    elif len(parts) == 7:
        version, tier, issued_str, expires_str, customer_hash, nonce, provided_checksum = parts
    else:
        return False, None, "Invalid key format"

    # Check version
    if version not in _SUPPORTED_VERSIONS:
        return False, None, f"Unknown license version: {version}"

    # Validate format matches version
    if version == _LICENSE_VERSION_V1 and len(parts) != 6:
        return False, None, "CSL1 key should have 6 parts"
    if version == _LICENSE_VERSION_V2 and len(parts) != 7:
        return False, None, "CSL2 key should have 7 parts"

    # Check tier code
    if tier not in _TIER_CODES:
        return False, None, f"Unknown tier: {tier}"

    # Validate timestamps are numeric
    try:
        issued_ts = int(issued_str)
        expires_ts = int(expires_str)
    except ValueError:
        return False, None, "Invalid timestamp format"

    # Validate customer_hash format for CSL2 (should be 8 hex chars)
    if customer_hash is not None:
        if len(customer_hash) != 8 or not all(c in "0123456789abcdef" for c in customer_hash.lower()):
            return False, None, "Invalid customer hash format"

    # Validate nonce format (should be 8 hex chars)
    if len(nonce) != 8 or not all(c in "0123456789abcdef" for c in nonce.lower()):
        return False, None, "Invalid nonce format"

    # Reconstruct payload and verify checksum
    if version == _LICENSE_VERSION_V1:
        payload = f"{version}_{tier}_{issued_str}_{expires_str}_{nonce}"
    else:  # CSL2
        payload = f"{version}_{tier}_{issued_str}_{expires_str}_{customer_hash}_{nonce}"

    expected_checksum = _compute_checksum(payload)

    if not hmac.compare_digest(provided_checksum.lower(), expected_checksum.lower()):
        return False, None, "Invalid checksum - key may be forged or corrupted"

    # Check expiry (0 = never expires)
    if expires_ts > 0:
        now = int(time.time())
        if now > expires_ts:
            expired_date = datetime.fromtimestamp(expires_ts, tz=timezone.utc)
            return False, None, f"License expired on {expired_date.strftime('%Y-%m-%d')}"

    # Check if issued date is reasonable (not in future, not before 2024)
    if issued_ts > int(time.time()) + 86400:  # Allow 1 day clock skew
        return False, None, "License issued in the future"
    if issued_ts < 1704067200:  # Jan 1, 2024
        return False, None, "License issued before product launch"

    return True, tier, None


def extract_customer_hash(license_key: str) -> Optional[str]:
    """Extract customer hash from a CSL2 license key.

    Args:
        license_key: The license key to extract from

    Returns:
        Customer hash string if CSL2 format, None otherwise
    """
    if not license_key:
        return None

    parts = license_key.strip().split("_")

    # CSL2 has 7 parts, customer_hash is at index 4
    if len(parts) == 7 and parts[0] == _LICENSE_VERSION_V2:
        return parts[4]

    return None


def get_tier_from_code(tier_code: str) -> Optional[str]:
    """Convert tier code to full tier name."""
    return _TIER_CODES.get(tier_code)


class Tier(Enum):
    """Subscription tiers for Consult."""

    FREE_BYOK = "free_byok"
    PRO_BYOK = "pro_byok"
    PRO_PREMIUM = "pro_premium"  # Deferred
    ENTERPRISE = "enterprise"  # Deferred


@dataclass
class TierLimits:
    """Rate limits and feature flags for a tier."""

    # Rate limits
    queries_per_day: int
    queries_per_hour: int
    max_experts: int  # Max experts per query
    max_iterations: int  # Max consensus iterations

    # Feature flags
    team_mode: bool  # Multi-provider comparison
    tui_enabled: bool  # Terminal UI
    sessions_enabled: bool  # Conversation persistence
    attachments_enabled: bool  # Image/PDF attachments
    export_enabled: bool  # Markdown export
    custom_experts: bool  # Custom expert configurations

    # API keys
    bundled_credits: bool  # True = we provide keys, False = BYOK


# Tier configurations
TIER_LIMITS: dict[Tier, TierLimits] = {
    Tier.FREE_BYOK: TierLimits(
        queries_per_day=3,
        queries_per_hour=2,
        max_experts=2,
        max_iterations=1,
        team_mode=False,
        tui_enabled=False,
        sessions_enabled=False,
        attachments_enabled=False,
        export_enabled=False,
        custom_experts=False,
        bundled_credits=False,
    ),
    Tier.PRO_BYOK: TierLimits(
        queries_per_day=100,
        queries_per_hour=20,
        max_experts=10,  # Effectively unlimited
        max_iterations=5,
        team_mode=True,
        tui_enabled=True,
        sessions_enabled=True,
        attachments_enabled=True,
        export_enabled=True,
        custom_experts=True,
        bundled_credits=False,
    ),
    # Deferred tiers - included for completeness but not active
    Tier.PRO_PREMIUM: TierLimits(
        queries_per_day=50,  # Credit-based in reality
        queries_per_hour=10,
        max_experts=10,
        max_iterations=5,
        team_mode=True,
        tui_enabled=True,
        sessions_enabled=True,
        attachments_enabled=True,
        export_enabled=True,
        custom_experts=True,
        bundled_credits=True,
    ),
    Tier.ENTERPRISE: TierLimits(
        queries_per_day=1000,
        queries_per_hour=100,
        max_experts=10,
        max_iterations=10,
        team_mode=True,
        tui_enabled=True,
        sessions_enabled=True,
        attachments_enabled=True,
        export_enabled=True,
        custom_experts=True,
        bundled_credits=True,
    ),
}


@dataclass
class LicenseInfo:
    """Information about a validated license."""

    tier: Tier
    valid: bool
    user_id: str
    expires: Optional[datetime] = None
    error: Optional[str] = None
    customer_hash: Optional[str] = None  # CSL2 only - for revocation checks

    # Cached limits (derived from tier)
    _limits: Optional[TierLimits] = field(default=None, repr=False)

    @property
    def limits(self) -> TierLimits:
        """Get limits for this license's tier."""
        if self._limits is None:
            self._limits = TIER_LIMITS[self.tier]
        return self._limits

    @property
    def is_expired(self) -> bool:
        """Check if license has expired."""
        if self.expires is None:
            return False
        return datetime.now(timezone.utc) > self.expires

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "tier": self.tier.value,
            "valid": self.valid,
            "user_id": self.user_id,
            "expires": self.expires.isoformat() if self.expires else None,
            "error": self.error,
            "customer_hash": self.customer_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LicenseInfo":
        """Create from dictionary."""
        return cls(
            tier=Tier(data["tier"]),
            valid=data["valid"],
            user_id=data["user_id"],
            expires=datetime.fromisoformat(data["expires"]) if data.get("expires") else None,
            error=data.get("error"),
            customer_hash=data.get("customer_hash"),
        )


class LicenseManager:
    """Manages license validation and tier access."""

    # Environment variable for license key
    LICENSE_KEY_ENV = "CONSULT_LICENSE_KEY"

    def __init__(self):
        self._cached_license: Optional[LicenseInfo] = None

    def get_license_key(self) -> Optional[str]:
        """Get license key from environment or file.

        Checks in order:
        1. CONSULT_LICENSE_KEY environment variable
        2. ~/.consult/license file

        Returns:
            License key string or None if not found
        """
        # Check environment variable first
        key = os.getenv(self.LICENSE_KEY_ENV)
        if key:
            return key.strip()

        # Check license file
        license_path = get_license_path()
        if license_path.exists():
            try:
                return license_path.read_text().strip()
            except Exception:
                pass

        return None

    def check_license(self, force_refresh: bool = False) -> LicenseInfo:
        """Check and validate the current license.

        Args:
            force_refresh: If True, skip cache and re-validate

        Returns:
            LicenseInfo with tier and validity information
        """
        logger = _get_logger()

        # Return cached if available and not forcing refresh
        if self._cached_license and not force_refresh:
            if not self._cached_license.is_expired:
                logger.debug(f"License cache hit | tier={self._cached_license.tier.value}")
                return self._cached_license

        license_key = self.get_license_key()

        if not license_key:
            # No license key - use free tier
            logger.info("No license key found | using free_byok tier")
            self._cached_license = LicenseInfo(
                tier=Tier.FREE_BYOK,
                valid=True,
                user_id="anonymous",
                error=None,
            )
            return self._cached_license

        # Validate the license key
        self._cached_license = self._validate_license(license_key)
        self._save_cache()

        if self._cached_license.valid:
            logger.info(f"License valid | tier={self._cached_license.tier.value} | "
                       f"user_id={self._cached_license.user_id}")
        else:
            logger.warning(f"License INVALID | error='{self._cached_license.error}' | "
                          f"falling back to free_byok")

        return self._cached_license

    def _validate_license(self, license_key: str) -> LicenseInfo:
        """Validate a license key cryptographically.

        Uses HMAC-SHA256 signature verification. No server roundtrip required.

        Args:
            license_key: The license key to validate

        Returns:
            LicenseInfo with validation result
        """
        user_id = get_user_id(license_key)

        # Validate using cryptographic signature
        is_valid, tier_code, error = validate_license_key(license_key)

        if not is_valid:
            # Invalid key - fall back to free tier with error message
            return LicenseInfo(
                tier=Tier.FREE_BYOK,
                valid=False,
                user_id=user_id,
                error=error or "Invalid license key",
            )

        # Map tier code to Tier enum
        tier_map = {
            "pro": Tier.PRO_BYOK,
            "free": Tier.FREE_BYOK,
            "ent": Tier.ENTERPRISE,
            "prem": Tier.PRO_PREMIUM,
        }
        tier = tier_map.get(tier_code, Tier.FREE_BYOK)

        # Extract expiry and customer_hash from key
        parts = license_key.split("_")
        expires = None
        customer_hash = None

        if len(parts) >= 4:
            try:
                expires_ts = int(parts[3])
                if expires_ts > 0:
                    expires = datetime.fromtimestamp(expires_ts, tz=timezone.utc)
            except (ValueError, IndexError):
                pass

        # Extract customer_hash for CSL2 keys
        customer_hash = extract_customer_hash(license_key)

        return LicenseInfo(
            tier=tier,
            valid=True,
            user_id=user_id,
            expires=expires,
            customer_hash=customer_hash,
        )

    def _save_cache(self) -> None:
        """Save license info to cache file."""
        if not self._cached_license:
            return

        try:
            cache_path = get_license_cache_path()
            cache_data = {
                "license": self._cached_license.to_dict(),
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }
            cache_path.write_text(json.dumps(cache_data, indent=2))
        except Exception:
            pass  # Caching is optional, don't fail on errors

    def _load_cache(self) -> Optional[LicenseInfo]:
        """Load license info from cache file."""
        try:
            cache_path = get_license_cache_path()
            if not cache_path.exists():
                return None

            cache_data = json.loads(cache_path.read_text())
            return LicenseInfo.from_dict(cache_data["license"])
        except Exception:
            return None

    def save_license_key(self, license_key: str) -> None:
        """Save license key to file.

        Args:
            license_key: The license key to save
        """
        license_path = get_license_path()
        license_path.write_text(license_key)

        # Set restrictive permissions
        from .security import set_secure_file_permissions
        set_secure_file_permissions(license_path)

    def requires_api_keys(self) -> bool:
        """Check if current license requires user to provide API keys (BYOK)."""
        license_info = self.check_license()
        return not license_info.limits.bundled_credits

    def get_user_id(self) -> str:
        """Get current user ID."""
        license_info = self.check_license()
        return license_info.user_id

    def can_use_feature(self, feature: str) -> bool:
        """Check if a feature is available for current license.

        Args:
            feature: Feature name (team_mode, tui_enabled, sessions_enabled, etc.)

        Returns:
            True if feature is available
        """
        license_info = self.check_license()
        return getattr(license_info.limits, feature, False)


# Singleton instance
_license_manager: Optional[LicenseManager] = None


def get_license_manager() -> LicenseManager:
    """Get the global license manager instance."""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager


def check_feature(feature: str) -> bool:
    """Convenience function to check feature availability."""
    return get_license_manager().can_use_feature(feature)


def get_current_tier() -> Tier:
    """Get the current subscription tier."""
    return get_license_manager().check_license().tier


def get_current_limits() -> TierLimits:
    """Get the current rate limits and feature flags."""
    return get_license_manager().check_license().limits
