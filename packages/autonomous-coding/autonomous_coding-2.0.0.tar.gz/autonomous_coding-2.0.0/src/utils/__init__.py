"""
Utilities module for the autonomous coding system.

Contains:
- api_rotation: API key rotation and quota management
- token_tracker: API token consumption tracking and reporting
- logger: Dev-friendly logging with timestamps
"""

from utils.api_rotation import (
    APIRotationState,
    QuotaExhaustedError,
    QuotaType,
    detect_quota_exhaustion,
    load_api_credentials,
)
from utils.logger import (
    Logger,
    LogLevel,
    get_logger,
    log_agent,
    log_api,
    log_debug,
    log_error,
    log_info,
    log_section,
    log_success,
    log_tool,
    log_warn,
    set_log_level,
)
from utils.token_tracker import (
    APICallRecord,
    ProjectTokenReport,
    SessionStats,
    TokenTracker,
    create_tracker,
)

__all__ = [
    # API Rotation
    "QuotaType",
    "QuotaExhaustedError",
    "detect_quota_exhaustion",
    "load_api_credentials",
    "APIRotationState",
    # Token Tracking
    "TokenTracker",
    "APICallRecord",
    "SessionStats",
    "ProjectTokenReport",
    "create_tracker",
    # Logger
    "Logger",
    "LogLevel",
    "get_logger",
    "set_log_level",
    "log_debug",
    "log_info",
    "log_warn",
    "log_error",
    "log_success",
    "log_section",
    "log_tool",
    "log_api",
    "log_agent",
]
