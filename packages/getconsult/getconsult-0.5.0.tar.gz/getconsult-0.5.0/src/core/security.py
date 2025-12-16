"""
Security Utilities - API Key Redaction

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

CRITICAL: API keys must NEVER appear in:
- Log files
- Session files
- Output files
- Error messages
- Stack traces
"""

import re
import logging
from functools import wraps
from typing import Any, Callable, TypeVar

# Patterns to detect and redact API keys
API_KEY_PATTERNS = [
    (r'sk-ant-api03-[a-zA-Z0-9-_]{90,}', 'Anthropic'),  # Anthropic API key (new format)
    (r'sk-ant-[a-zA-Z0-9-_]{20,}', 'Anthropic'),  # Anthropic API key (older format)
    (r'sk-proj-[a-zA-Z0-9-_]{20,}', 'OpenAI'),  # OpenAI project API key
    (r'sk-[a-zA-Z0-9]{48,}', 'OpenAI'),  # OpenAI API key (standard)
    (r'AIza[a-zA-Z0-9_-]{35,}', 'Google'),  # Google API key
    (r'[a-zA-Z0-9_-]{39}', 'Generic'),  # Generic long keys (fallback, more conservative)
]

# Compiled patterns for performance
_COMPILED_PATTERNS = [(re.compile(pattern), name) for pattern, name in API_KEY_PATTERNS]


def redact_secrets(text: str) -> str:
    """Redact any API keys from text before logging/saving.

    Args:
        text: Text that may contain API keys

    Returns:
        Text with all detected API keys replaced with [REDACTED]

    Example:
        >>> redact_secrets("Using key sk-ant-api03-abc123...")
        "Using key [REDACTED]..."
    """
    if not isinstance(text, str):
        return text

    result = text
    for pattern, provider in _COMPILED_PATTERNS:
        result = pattern.sub(f'[REDACTED-{provider}]', result)

    return result


def redact_dict(data: dict) -> dict:
    """Recursively redact secrets from a dictionary.

    Args:
        data: Dictionary that may contain API keys in values

    Returns:
        New dictionary with all string values redacted
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = redact_secrets(value)
        elif isinstance(value, dict):
            result[key] = redact_dict(value)
        elif isinstance(value, list):
            result[key] = [
                redact_secrets(item) if isinstance(item, str)
                else redact_dict(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            result[key] = value

    return result


F = TypeVar('F', bound=Callable[..., Any])


def safe_log(func: F) -> F:
    """Decorator to ensure logged data has secrets redacted.

    Use on logging functions to automatically redact any API keys
    from log messages.

    Example:
        @safe_log
        def log_message(msg: str):
            print(msg)

        log_message("Key is sk-ant-api03-abc123")
        # Output: "Key is [REDACTED-Anthropic]"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Redact all string args
        safe_args = tuple(
            redact_secrets(a) if isinstance(a, str) else a
            for a in args
        )
        # Redact all string kwargs
        safe_kwargs = {
            k: redact_secrets(v) if isinstance(v, str) else v
            for k, v in kwargs.items()
        }
        return func(*safe_args, **safe_kwargs)
    return wrapper  # type: ignore


class SafeFormatter(logging.Formatter):
    """Logging formatter that redacts secrets from all log messages.

    Use this formatter on any handler to ensure API keys never appear in logs.

    Example:
        handler = logging.StreamHandler()
        handler.setFormatter(SafeFormatter(LOG_FORMAT))
        logger.addHandler(handler)
    """

    def format(self, record: logging.LogRecord) -> str:
        # Redact message
        record.msg = redact_secrets(str(record.msg))

        # Redact args if present
        if record.args:
            record.args = tuple(
                redact_secrets(str(a)) if isinstance(a, str) else a
                for a in record.args
            )

        # Redact exception info if present
        if record.exc_text:
            record.exc_text = redact_secrets(record.exc_text)

        return super().format(record)


def contains_api_key(text: str) -> bool:
    """Check if text contains what looks like an API key.

    Useful for validation before writing to files.

    Args:
        text: Text to check

    Returns:
        True if text contains a potential API key pattern
    """
    if not isinstance(text, str):
        return False

    for pattern, _ in _COMPILED_PATTERNS:
        if pattern.search(text):
            return True

    return False


def validate_no_secrets(text: str, context: str = "data") -> None:
    """Raise an error if text contains API keys.

    Use as a safety check before writing to files.

    Args:
        text: Text to validate
        context: Description of what's being validated (for error message)

    Raises:
        ValueError: If text contains API key patterns
    """
    if contains_api_key(text):
        raise ValueError(
            f"Security violation: {context} contains API key patterns. "
            "Use redact_secrets() before saving."
        )


def set_secure_file_permissions(path) -> None:
    """Set file permissions to user-read-only (600).

    Use for files containing sensitive data like .env.

    Args:
        path: Path to the file (str or Path)
    """
    import os
    from pathlib import Path

    path = Path(path)
    if path.exists():
        os.chmod(path, 0o600)  # -rw-------


def configure_secure_logging(
    logger: logging.Logger,
    level: int = logging.INFO,
    log_file: str = None
) -> None:
    """Configure a logger with automatic secret redaction.

    All log messages will have API keys automatically redacted.

    Args:
        logger: Logger instance to configure
        level: Logging level (default: INFO)
        log_file: Optional file path for file handler

    Example:
        logger = logging.getLogger("consult")
        configure_secure_logging(logger, log_file="~/.consult/logs/consult.log")
    """
    logger.setLevel(level)

    # Console handler with redaction
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(SafeFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(console_handler)

    # File handler with redaction (if specified)
    if log_file:
        from pathlib import Path
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(SafeFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(file_handler)


def get_secure_logger(name: str, log_file: str = None) -> logging.Logger:
    """Get a logger configured with automatic secret redaction.

    Convenience function for creating loggers that automatically
    redact API keys from all log messages.

    Args:
        name: Logger name
        log_file: Optional file path for file handler

    Returns:
        Configured logger instance

    Example:
        logger = get_secure_logger("consult.workflow")
        logger.info(f"Using key {api_key}")  # Key will be redacted
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        configure_secure_logging(logger, log_file=log_file)

    return logger


# Session context for structured logging
_session_context = {
    "user_id": None,
    "session_id": None,
    "query_id": None,
}


def set_session_context(user_id: str = None, session_id: str = None) -> None:
    """Set global session context for all log messages.

    Call this once at startup (CLI or TUI) to tag all subsequent logs
    with user and session identifiers for easy filtering.

    Args:
        user_id: 12-char user ID from license key hash
        session_id: 8-char session ID from UUID4

    Example:
        set_session_context(user_id="a1b2c3d4e5f6", session_id="12345678")
        # All logs now include: [u:a1b2c3d4e5f6 s:12345678]
    """
    if user_id:
        _session_context["user_id"] = user_id
    if session_id:
        _session_context["session_id"] = session_id


def set_query_id(query_id: str) -> None:
    """Set query ID for current workflow execution.

    Call this at the start of each query to distinguish between
    multiple queries in the same session.

    Args:
        query_id: 6-char unique ID for this query (from UUID4[:6])

    Example:
        set_query_id("ab12cd")
        # All logs now include: [u:xxx s:xxx q:ab12cd]
    """
    _session_context["query_id"] = query_id


def clear_query_id() -> None:
    """Clear query ID after workflow completes."""
    _session_context["query_id"] = None


def get_session_context() -> dict:
    """Get current session context."""
    return _session_context.copy()


class ContextualFormatter(SafeFormatter):
    """Formatter that adds user/session/query context to every log line.

    Output format:
        2025-12-11 15:30:01 - consult.workflow - INFO - [u:a1b2c3 s:12345678 q:ab12cd] Message here
    """

    def format(self, record: logging.LogRecord) -> str:
        # Build context prefix
        parts = []
        if _session_context.get("user_id"):
            parts.append(f"u:{_session_context['user_id']}")
        if _session_context.get("session_id"):
            parts.append(f"s:{_session_context['session_id']}")
        if _session_context.get("query_id"):
            parts.append(f"q:{_session_context['query_id']}")

        if parts:
            context_prefix = f"[{' '.join(parts)}] "
        else:
            context_prefix = ""

        # Prepend context to message
        original_msg = record.msg
        record.msg = f"{context_prefix}{original_msg}"

        # Call parent format (which handles redaction)
        result = super().format(record)

        # Restore original message
        record.msg = original_msg

        return result


class SamplingFilter(logging.Filter):
    """Filter that samples DEBUG messages to reduce log volume.

    In high-volume scenarios (many API calls), DEBUG logging can cause
    excessive disk I/O. This filter samples DEBUG messages at a configurable
    rate while letting all INFO+ messages through.

    Controlled via CONSULT_DEBUG_SAMPLE_RATE env var (0.0-1.0, default 1.0 = no sampling).
    """

    def __init__(self, sample_rate: float = 1.0):
        super().__init__()
        import random
        self._random = random
        self._sample_rate = sample_rate
        self._debug_count = 0
        self._debug_sampled = 0

    def filter(self, record: logging.LogRecord) -> bool:
        # Always let INFO and above through
        if record.levelno >= logging.INFO:
            return True

        # Sample DEBUG messages
        self._debug_count += 1
        if self._random.random() < self._sample_rate:
            self._debug_sampled += 1
            return True
        return False


class JSONFormatter(logging.Formatter):
    """Formatter that outputs logs as JSON for log aggregation services.

    Output format:
        {"timestamp": "2025-12-11T15:30:01.123", "level": "INFO", "logger": "consult.workflow",
         "user_id": "a1b2c3", "session_id": "12345678", "query_id": "ab12cd", "message": "Workflow started"}
    """

    def format(self, record: logging.LogRecord) -> str:
        import json as json_module
        from datetime import datetime

        # Redact secrets from message
        message = redact_secrets(str(record.getMessage()))

        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
        }

        # Add context if available
        if _session_context.get("user_id"):
            log_entry["user_id"] = _session_context["user_id"]
        if _session_context.get("session_id"):
            log_entry["session_id"] = _session_context["session_id"]
        if _session_context.get("query_id"):
            log_entry["query_id"] = _session_context["query_id"]

        # Add exception info if present
        if record.exc_info:
            import traceback
            log_entry["exception"] = ''.join(traceback.format_exception(*record.exc_info))

        return json_module.dumps(log_entry)


def get_contextual_logger(name: str, log_file: str = None) -> logging.Logger:
    """Get a logger with user/session context and secret redaction.

    Use this instead of get_secure_logger() for structured logging
    that includes user_id and session_id in every line.

    Must call set_session_context() first to populate the context.

    Features:
    - Automatic log rotation (10MB max, keeps 5 backups)
    - Configurable level via CONSULT_LOG_LEVEL env var (DEBUG, INFO, WARNING, ERROR)
    - User/session/query context in every line
    - JSON format via CONSULT_LOG_FORMAT=json env var (for log aggregation)
    - DEBUG sampling via CONSULT_DEBUG_SAMPLE_RATE env var (0.0-1.0, default 1.0)

    Args:
        name: Logger name
        log_file: Optional file path for file handler

    Returns:
        Configured logger with contextual formatting

    Example:
        set_session_context(user_id="abc123", session_id="xyz789")
        logger = get_contextual_logger("consult.workflow", log_file=log_path)
        logger.info("Workflow started")
        # Output: 2025-12-11 15:30:01 - consult.workflow - INFO - [u:abc123 s:xyz789] Workflow started

        # For JSON output (for ELK/Datadog/CloudWatch):
        # CONSULT_LOG_FORMAT=json consult -p "query"
        # Output: {"timestamp": "...", "level": "INFO", "user_id": "abc123", ...}

        # For DEBUG sampling (reduce volume in high-traffic scenarios):
        # CONSULT_DEBUG_SAMPLE_RATE=0.1 consult -p "query"  # Only 10% of DEBUG messages
    """
    import os
    from logging.handlers import RotatingFileHandler

    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Configurable log level via environment variable
        log_level_str = os.environ.get("CONSULT_LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        logger.setLevel(log_level)

        # File handler with rotation and contextual formatting
        if log_file:
            from pathlib import Path
            log_path = Path(log_file).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Rotating file handler: 10MB max, keep 5 backups
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # Capture debug in file

            # Choose formatter based on environment variable
            log_format = os.environ.get("CONSULT_LOG_FORMAT", "text").lower()
            if log_format == "json":
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(ContextualFormatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ))

            # Add DEBUG sampling filter if configured
            sample_rate_str = os.environ.get("CONSULT_DEBUG_SAMPLE_RATE", "1.0")
            try:
                sample_rate = float(sample_rate_str)
                if 0.0 <= sample_rate < 1.0:
                    file_handler.addFilter(SamplingFilter(sample_rate))
            except ValueError:
                pass  # Invalid sample rate, skip sampling

            logger.addHandler(file_handler)

        # No console handler - logs only to file for production

    return logger
