"""
Core module for Consult

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.
"""

from .exceptions import (
    ConsultError,
    WorkflowError, ConsensusTimeoutError, WorkflowInitializationError, OrchestratorError,
    AgentCommunicationError, AgentResponseError, AgentTimeoutError, MultimodalProcessingError,
    ConfigurationError, MissingAPIKeyError, InvalidProviderError, InvalidExpertConfigError,
    MemoryError, MemoryStorageError, MemoryRetrievalError,
    ResourceError, ResourceExhaustionError, ResourceCleanupError,
    FeatureGatedError,
)

from .paths import (
    get_consult_home,
    get_config_path,
    get_license_path,
    get_env_path,
    get_sessions_dir,
    get_outputs_dir,
    get_cache_dir,
    get_logs_dir,
    ensure_consult_structure,
)

from .security import (
    redact_secrets,
    redact_dict,
    safe_log,
    SafeFormatter,
    contains_api_key,
    validate_no_secrets,
    set_secure_file_permissions,
    configure_secure_logging,
    get_secure_logger,
)

from .identity import (
    IdentityContext,
    get_user_id,
    generate_session_id,
    get_timestamp,
    get_iso_timestamp,
    slugify,
    make_filename,
    make_session_filename,
    make_output_filename,
    make_log_filename,
)

from .license import (
    Tier,
    TierLimits,
    LicenseInfo,
    LicenseManager,
    get_license_manager,
    check_feature,
    get_current_tier,
    get_current_limits,
    generate_license_key,
    validate_license_key,
)

from .rate_limiter import (
    QuotaStatus,
    RateLimiter,
    get_rate_limiter,
    check_can_query,
    record_query,
    get_quota_status,
)

from .feature_gate import (
    check_feature as gate_check_feature,
    check_limit,
    require_team_mode,
    require_tui,
    require_sessions,
    require_attachments,
    require_export,
    require_custom_experts,
    check_expert_count,
    check_iteration_count,
    get_tier_limits_summary,
)

__all__ = [
    # Base exceptions
    "ConsultError",

    # Workflow exceptions
    "WorkflowError", "ConsensusTimeoutError", "WorkflowInitializationError", "OrchestratorError",

    # Agent communication exceptions
    "AgentCommunicationError", "AgentResponseError", "AgentTimeoutError", "MultimodalProcessingError",

    # Configuration exceptions
    "ConfigurationError", "MissingAPIKeyError", "InvalidProviderError", "InvalidExpertConfigError",

    # Memory exceptions
    "MemoryError", "MemoryStorageError", "MemoryRetrievalError",

    # Resource exceptions
    "ResourceError", "ResourceExhaustionError", "ResourceCleanupError",

    # Paths
    "get_consult_home",
    "get_config_path", "get_license_path", "get_env_path",
    "get_sessions_dir", "get_outputs_dir", "get_cache_dir", "get_logs_dir",
    "ensure_consult_structure",

    # Security
    "redact_secrets", "redact_dict", "safe_log", "SafeFormatter",
    "contains_api_key", "validate_no_secrets", "set_secure_file_permissions",
    "configure_secure_logging", "get_secure_logger",

    # Identity
    "IdentityContext", "get_user_id", "generate_session_id",
    "get_timestamp", "get_iso_timestamp", "slugify",
    "make_filename", "make_session_filename", "make_output_filename", "make_log_filename",

    # License
    "Tier", "TierLimits", "LicenseInfo", "LicenseManager",
    "get_license_manager", "check_feature", "get_current_tier", "get_current_limits",
    "generate_license_key", "validate_license_key",

    # Rate limiting
    "QuotaStatus", "RateLimiter", "get_rate_limiter",
    "check_can_query", "record_query", "get_quota_status",

    # Feature gating
    "FeatureGatedError",
    "gate_check_feature", "check_limit",
    "require_team_mode", "require_tui", "require_sessions",
    "require_attachments", "require_export", "require_custom_experts",
    "check_expert_count", "check_iteration_count", "get_tier_limits_summary",
]