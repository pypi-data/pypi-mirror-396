"""
Rate Limiter - Usage Tracking and Quota Enforcement

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

Tracks queries per hour and per day to enforce tier limits.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict

from .paths import get_quota_path, get_logs_dir
from .license import LicenseInfo, get_license_manager
from .security import get_contextual_logger

# Module logger
_logger = None


def _get_logger():
    """Get or create the rate limiter logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.quota", log_file=str(log_file))
    return _logger


@dataclass
class QuotaStatus:
    """Current quota status for a user."""

    # Current usage
    queries_today: int
    queries_this_hour: int

    # Limits from tier
    limit_per_day: int
    limit_per_hour: int

    # Computed
    remaining_today: int = field(init=False)
    remaining_this_hour: int = field(init=False)
    is_limited: bool = field(init=False)
    limit_reason: Optional[str] = field(default=None)

    def __post_init__(self):
        self.remaining_today = max(0, self.limit_per_day - self.queries_today)
        self.remaining_this_hour = max(0, self.limit_per_hour - self.queries_this_hour)
        self.is_limited = self.remaining_today == 0 or self.remaining_this_hour == 0

        if self.remaining_today == 0:
            self.limit_reason = "Daily query limit reached"
        elif self.remaining_this_hour == 0:
            self.limit_reason = "Hourly query limit reached"


@dataclass
class UsageRecord:
    """Usage tracking data for a user."""

    user_id: str
    tier: str

    # Usage by date and hour
    # Format: {"2025-01-15": {"total": 10, "by_hour": {"14": 5, "15": 5}}}
    usage: dict = field(default_factory=dict)

    last_query_at: Optional[str] = None

    def record_query(self) -> None:
        """Record a new query."""
        now = datetime.now(timezone.utc)
        date_key = now.strftime("%Y-%m-%d")
        hour_key = str(now.hour)

        if date_key not in self.usage:
            self.usage[date_key] = {"total": 0, "by_hour": defaultdict(int)}

        self.usage[date_key]["total"] += 1
        if isinstance(self.usage[date_key]["by_hour"], dict):
            self.usage[date_key]["by_hour"][hour_key] = \
                self.usage[date_key]["by_hour"].get(hour_key, 0) + 1

        self.last_query_at = now.isoformat()

    def get_usage_today(self) -> int:
        """Get total queries today."""
        date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.usage.get(date_key, {}).get("total", 0)

    def get_usage_this_hour(self) -> int:
        """Get queries in current hour."""
        now = datetime.now(timezone.utc)
        date_key = now.strftime("%Y-%m-%d")
        hour_key = str(now.hour)

        day_usage = self.usage.get(date_key, {})
        by_hour = day_usage.get("by_hour", {})
        return by_hour.get(hour_key, 0)

    def cleanup_old_data(self, keep_days: int = 30) -> None:
        """Remove usage data older than keep_days."""
        now = datetime.now(timezone.utc)
        cutoff = now.strftime("%Y-%m-%d")

        # Simple approach: keep only recent dates
        dates_to_remove = []
        for date_key in self.usage.keys():
            try:
                date = datetime.strptime(date_key, "%Y-%m-%d")
                if (now - date.replace(tzinfo=timezone.utc)).days > keep_days:
                    dates_to_remove.append(date_key)
            except ValueError:
                dates_to_remove.append(date_key)

        for date_key in dates_to_remove:
            del self.usage[date_key]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "tier": self.tier,
            "usage": self.usage,
            "last_query_at": self.last_query_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UsageRecord":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            tier=data["tier"],
            usage=data.get("usage", {}),
            last_query_at=data.get("last_query_at"),
        )


class RateLimiter:
    """Track and enforce rate limits."""

    def __init__(self, license_info: Optional[LicenseInfo] = None):
        """Initialize rate limiter.

        Args:
            license_info: License info to use for limits.
                         If None, will fetch from license manager.
        """
        self._license_info = license_info
        self._usage_record: Optional[UsageRecord] = None

    @property
    def license_info(self) -> LicenseInfo:
        """Get license info, fetching if needed."""
        if self._license_info is None:
            self._license_info = get_license_manager().check_license()
        return self._license_info

    @property
    def usage_record(self) -> UsageRecord:
        """Get usage record, loading from disk if needed."""
        if self._usage_record is None:
            self._usage_record = self._load_usage()
        return self._usage_record

    def _get_quota_path(self):
        """Get path to quota file for current user."""
        return get_quota_path(self.license_info.user_id)

    def _load_usage(self) -> UsageRecord:
        """Load usage record from disk."""
        quota_path = self._get_quota_path()

        if quota_path.exists():
            try:
                data = json.loads(quota_path.read_text())
                record = UsageRecord.from_dict(data)
                # Update tier in case it changed
                record.tier = self.license_info.tier.value
                return record
            except Exception:
                pass

        # Create new record
        return UsageRecord(
            user_id=self.license_info.user_id,
            tier=self.license_info.tier.value,
        )

    def _save_usage(self) -> None:
        """Save usage record to disk."""
        if self._usage_record is None:
            return

        try:
            # Cleanup old data before saving
            self._usage_record.cleanup_old_data()

            quota_path = self._get_quota_path()
            quota_path.write_text(json.dumps(
                self._usage_record.to_dict(),
                indent=2,
            ))
        except Exception:
            pass  # Don't fail on save errors

    def check_quota(self) -> QuotaStatus:
        """Check current quota status.

        Returns:
            QuotaStatus with current usage and limits
        """
        limits = self.license_info.limits

        return QuotaStatus(
            queries_today=self.usage_record.get_usage_today(),
            queries_this_hour=self.usage_record.get_usage_this_hour(),
            limit_per_day=limits.queries_per_day,
            limit_per_hour=limits.queries_per_hour,
        )

    def can_query(self) -> tuple[bool, Optional[str]]:
        """Check if user can make a query.

        Returns:
            Tuple of (can_query, error_message)
        """
        logger = _get_logger()
        status = self.check_quota()

        if status.is_limited:
            logger.warning(f"Quota BLOCKED | reason='{status.limit_reason}' | "
                          f"today={status.queries_today}/{status.limit_per_day} | "
                          f"hour={status.queries_this_hour}/{status.limit_per_hour}")
            return False, status.limit_reason

        logger.debug(f"Quota OK | today={status.queries_today}/{status.limit_per_day} | "
                    f"hour={status.queries_this_hour}/{status.limit_per_hour}")
        return True, None

    def record_query(self) -> QuotaStatus:
        """Record a new query and return updated status.

        Call this AFTER successfully completing a query.

        Returns:
            Updated QuotaStatus
        """
        logger = _get_logger()
        self.usage_record.record_query()
        self._save_usage()
        status = self.check_quota()
        logger.info(f"Query recorded | remaining: {status.remaining_today} today, {status.remaining_this_hour} this hour")
        return status

    def get_remaining(self) -> dict:
        """Get remaining queries.

        Returns:
            Dict with 'hour' and 'day' remaining counts
        """
        status = self.check_quota()
        return {
            "hour": status.remaining_this_hour,
            "day": status.remaining_today,
        }

    def format_quota_message(self) -> str:
        """Format quota status for display.

        Returns:
            Human-readable quota status string
        """
        status = self.check_quota()

        if status.is_limited:
            return f"Limit reached: {status.limit_reason}"

        return (
            f"Queries remaining: {status.remaining_today}/{status.limit_per_day} today, "
            f"{status.remaining_this_hour}/{status.limit_per_hour} this hour"
        )

    def show_quota_warning(self) -> Optional[str]:
        """Get warning message if approaching limits.

        Returns:
            Warning message if near limit, None otherwise
        """
        logger = _get_logger()
        status = self.check_quota()

        # Warn at 20% remaining
        day_threshold = max(1, status.limit_per_day // 5)
        hour_threshold = max(1, status.limit_per_hour // 5)

        if status.remaining_today <= day_threshold:
            msg = f"Approaching daily limit: {status.remaining_today} queries remaining today"
            logger.warning(f"Quota WARNING | {msg}")
            return msg

        if status.remaining_this_hour <= hour_threshold:
            msg = f"Approaching hourly limit: {status.remaining_this_hour} queries remaining this hour"
            logger.warning(f"Quota WARNING | {msg}")
            return msg

        return None


# Singleton instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def check_can_query() -> tuple[bool, Optional[str]]:
    """Convenience function to check if query is allowed."""
    return get_rate_limiter().can_query()


def record_query() -> QuotaStatus:
    """Convenience function to record a query."""
    return get_rate_limiter().record_query()


def get_quota_status() -> QuotaStatus:
    """Convenience function to get quota status."""
    return get_rate_limiter().check_quota()
