"""
Feature Gating - Centralized feature access control with logging

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

Provides clean user messaging and detailed logging for feature access control.
"""

from typing import Optional
from .license import get_license_manager, LicenseInfo, Tier
from .exceptions import FeatureGatedError
from .paths import get_logs_dir
from .security import get_contextual_logger

# Module logger
_logger = None


def _get_logger():
    """Get or create the feature gate logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.feature_gate", log_file=str(log_file))
    return _logger


def check_feature(feature: str, raise_on_denied: bool = True) -> bool:
    """Check if a feature is available for the current user's tier.

    Args:
        feature: Feature flag name (e.g., 'team_mode', 'tui_enabled')
        raise_on_denied: If True, raises FeatureGatedError when denied

    Returns:
        True if feature is available, False otherwise

    Raises:
        FeatureGatedError: If feature is denied and raise_on_denied=True
    """
    logger = _get_logger()
    license_info = get_license_manager().check_license()
    limits = license_info.limits
    tier = license_info.tier.value

    # Check boolean feature flags
    feature_enabled = getattr(limits, feature, None)

    if feature_enabled is None:
        # Unknown feature - log warning but allow
        logger.warning(f"Feature check | feature={feature} | tier={tier} | result=UNKNOWN_FEATURE")
        return True

    if feature_enabled:
        logger.debug(f"Feature check | feature={feature} | tier={tier} | result=ALLOWED")
        return True

    # Feature denied
    logger.warning(f"Feature DENIED | feature={feature} | tier={tier} | required=pro_byok")

    if raise_on_denied:
        raise FeatureGatedError(feature=feature, current_tier=tier)

    return False


def check_limit(limit_name: str, requested_value: int, raise_on_exceeded: bool = True) -> bool:
    """Check if a numeric limit is within the user's tier allowance.

    Args:
        limit_name: Limit name (e.g., 'max_experts', 'max_iterations')
        requested_value: The value being requested
        raise_on_exceeded: If True, raises FeatureGatedError when exceeded

    Returns:
        True if within limits, False otherwise

    Raises:
        FeatureGatedError: If limit exceeded and raise_on_exceeded=True
    """
    logger = _get_logger()
    license_info = get_license_manager().check_license()
    limits = license_info.limits
    tier = license_info.tier.value

    limit_value = getattr(limits, limit_name, None)

    if limit_value is None:
        logger.warning(f"Limit check | limit={limit_name} | tier={tier} | result=UNKNOWN_LIMIT")
        return True

    if requested_value <= limit_value:
        logger.debug(f"Limit check | limit={limit_name} | requested={requested_value} | "
                    f"max={limit_value} | tier={tier} | result=ALLOWED")
        return True

    # Limit exceeded
    logger.warning(f"Limit EXCEEDED | limit={limit_name} | requested={requested_value} | "
                  f"max={limit_value} | tier={tier}")

    if raise_on_exceeded:
        raise FeatureGatedError(
            feature=limit_name,
            current_tier=tier,
            context={"requested": requested_value, "limit": limit_value}
        )

    return False


def require_team_mode() -> None:
    """Require team mode feature. Raises FeatureGatedError if not available."""
    check_feature("team_mode", raise_on_denied=True)


def require_tui() -> None:
    """Require TUI feature. Raises FeatureGatedError if not available."""
    check_feature("tui_enabled", raise_on_denied=True)


def require_sessions() -> None:
    """Require sessions feature. Raises FeatureGatedError if not available."""
    check_feature("sessions_enabled", raise_on_denied=True)


def require_attachments() -> None:
    """Require attachments feature. Raises FeatureGatedError if not available."""
    check_feature("attachments_enabled", raise_on_denied=True)


def require_export() -> None:
    """Require export feature. Raises FeatureGatedError if not available."""
    check_feature("export_enabled", raise_on_denied=True)


def require_custom_experts() -> None:
    """Require custom experts feature. Raises FeatureGatedError if not available."""
    check_feature("custom_experts", raise_on_denied=True)


def check_expert_count(requested: int) -> None:
    """Check if requested expert count is within tier limits."""
    check_limit("max_experts", requested, raise_on_exceeded=True)


def check_iteration_count(requested: int) -> None:
    """Check if requested iteration count is within tier limits."""
    check_limit("max_iterations", requested, raise_on_exceeded=True)


def get_tier_limits_summary() -> str:
    """Get a summary of current tier limits for display."""
    license_info = get_license_manager().check_license()
    limits = license_info.limits
    tier = license_info.tier.value

    lines = [
        f"Current tier: {tier}",
        f"",
        f"Rate limits:",
        f"  • Queries/day: {limits.queries_per_day}",
        f"  • Queries/hour: {limits.queries_per_hour}",
        f"  • Max experts: {limits.max_experts}",
        f"  • Max iterations: {limits.max_iterations}",
        f"",
        f"Features:",
        f"  • Team mode: {'✓' if limits.team_mode else '✗'}",
        f"  • Terminal UI: {'✓' if limits.tui_enabled else '✗'}",
        f"  • Sessions: {'✓' if limits.sessions_enabled else '✗'}",
        f"  • Attachments: {'✓' if limits.attachments_enabled else '✗'}",
        f"  • Export: {'✓' if limits.export_enabled else '✗'}",
        f"  • Custom experts: {'✓' if limits.custom_experts else '✗'}",
    ]

    if tier == "free_byok":
        lines.append("")
        lines.append("Upgrade to Pro: https://getconsult.sysapp.dev")

    return "\n".join(lines)
