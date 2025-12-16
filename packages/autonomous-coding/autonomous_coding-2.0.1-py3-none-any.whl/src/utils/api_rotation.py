"""
API Quota Detection and Rotation
=================================

Multi-signal quota detection (HTTP 429, 401/403, error messages) and
automatic rotation through numbered environment variables with
differential cooling periods.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from enum import Enum


class QuotaType(Enum):
    """Types of API quota exhaustion with different cooling periods."""

    RATE_LIMIT = "rate_limit"  # 60s cooling
    SESSION_EXPIRY = "session_expiry"  # 4h cooling
    DAILY_QUOTA = "daily_quota"  # Wait until daily reset
    WEEKLY_QUOTA = "weekly_quota"  # Wait until weekly reset


class QuotaExhaustedError(Exception):
    """Raised when all API key/endpoint pairs are exhausted."""

    pass


def detect_quota_exhaustion(
    status_code: int | None, error_text: str
) -> tuple[bool, QuotaType | None]:
    """
    Detect quota type from HTTP response and error message.

    Args:
        status_code: HTTP status code (None if not HTTP error)
        error_text: Error message text

    Returns:
        (is_quota_error, quota_type)
    """
    # HTTP 429 = rate limit
    if status_code == 429:
        return (True, QuotaType.RATE_LIMIT)

    # HTTP 401/403 with session keywords = session expiry
    if status_code in [401, 403]:
        session_keywords = ["session", "expired", "invalid token", "authentication"]
        if any(keyword in error_text.lower() for keyword in session_keywords):
            return (True, QuotaType.SESSION_EXPIRY)

    # Parse error message for quota keywords
    error_lower = error_text.lower()

    # Check specific quota patterns FIRST (before generic patterns)
    # Daily quota patterns
    if "daily quota" in error_lower or "daily limit" in error_lower:
        return (True, QuotaType.DAILY_QUOTA)

    # Weekly quota patterns
    if "weekly quota" in error_lower or "weekly limit" in error_lower:
        return (True, QuotaType.WEEKLY_QUOTA)

    # Rate limit patterns (more generic, check last)
    rate_limit_patterns = [
        "rate limit",
        "too many requests",
        "usage limit",  # Z.ai uses this
        "limit reached",
        "throttl",  # throttle, throttling, throttled
        "429",  # HTTP status code in error message
    ]
    if any(pattern in error_lower for pattern in rate_limit_patterns):
        return (True, QuotaType.RATE_LIMIT)

    # Credit/balance exhaustion patterns
    credit_patterns = [
        ("credit", ["low", "insufficient", "balance", "exhausted"]),
        ("balance", ["low", "empty", "zero", "negative", "insufficient"]),
    ]
    for key, indicators in credit_patterns:
        if key in error_lower and any(ind in error_lower for ind in indicators):
            return (True, QuotaType.DAILY_QUOTA)

    # Billing/payment issues
    billing_patterns = ["billing", "payment", "subscription", "api_error"]
    if (
        any(pattern in error_lower for pattern in billing_patterns)
        and "insufficient" in error_lower
    ):
        return (True, QuotaType.DAILY_QUOTA)

    return (False, None)


def load_api_credentials() -> list[tuple[str, str, str | None]]:
    """
    Load API key/endpoint/model triplets from numbered environment variables.

    Loads triplets from:
      ANTHROPIC_API_KEY_1 + ANTHROPIC_BASE_URL_1 + ANTHROPIC_MODEL_1
      ANTHROPIC_API_KEY_2 + ANTHROPIC_BASE_URL_2 + ANTHROPIC_MODEL_2
      etc.

    Falls back to single ANTHROPIC_API_KEY + ANTHROPIC_BASE_URL + ANTHROPIC_MODEL
    if no numbered pairs found.

    Returns:
        List of (api_key, base_url, model_override) tuples.
        model_override is None if not specified (use default model from CLI).
    """
    pairs = []
    index = 1

    while True:
        key = os.environ.get(f"ANTHROPIC_API_KEY_{index}")
        if not key:
            break

        base_url = os.environ.get(f"ANTHROPIC_BASE_URL_{index}", "https://api.anthropic.com")
        model = os.environ.get(f"ANTHROPIC_MODEL_{index}")  # Optional model override
        pairs.append((key, base_url, model))
        index += 1

    # Fallback to single env vars if no numbered pairs found
    if not pairs:
        key = os.environ.get("ANTHROPIC_API_KEY")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        model = os.environ.get("ANTHROPIC_MODEL")
        if key:
            pairs.append((key, base_url, model))

    return pairs


class APIRotationState:
    """
    Manages API key/endpoint/model rotation with quota tracking.

    Tracks exhaustion status per pair with differential cooling periods:
    - RATE_LIMIT: 60 seconds
    - SESSION_EXPIRY: 4 hours
    - DAILY_QUOTA: Until next day UTC
    - WEEKLY_QUOTA: Until next Monday UTC
    """

    def __init__(self):
        """Initialize rotation state with API credentials."""
        self.pairs = load_api_credentials()
        if not self.pairs:
            raise ValueError(
                "No API credentials found. Set ANTHROPIC_API_KEY or numbered pairs "
                "(ANTHROPIC_API_KEY_1, ANTHROPIC_API_KEY_2, ...)"
            )

        # Track exhaustion: {pair_index: (quota_type, exhausted_at_timestamp)}
        self.exhausted: dict[int, tuple[QuotaType, float]] = {}
        self.current_index = 0

    def mark_exhausted(self, pair_index: int, quota_type: QuotaType) -> None:
        """
        Mark an API key/endpoint pair as exhausted.

        Args:
            pair_index: Index of the pair in self.pairs
            quota_type: Type of quota exhaustion
        """
        self.exhausted[pair_index] = (quota_type, time.time())
        print(f"[API Rotation] Pair {pair_index + 1} exhausted: {quota_type.value}")

    def get_next_available_pair(self) -> tuple[int, str, str, str | None] | None:
        """
        Get the next available API key/endpoint/model triplet.

        Returns:
            (pair_index, api_key, base_url, model_override) or None if all exhausted.
            model_override is None if not specified for this pair.
        """
        current_time = time.time()

        # Try all pairs starting from current_index
        for offset in range(len(self.pairs)):
            index = (self.current_index + offset) % len(self.pairs)

            # Check if this pair is exhausted
            if index in self.exhausted:
                quota_type, exhausted_at = self.exhausted[index]

                # Calculate if cooling period has elapsed
                if self._is_cooled_off(quota_type, exhausted_at, current_time):
                    # Cooling period complete - remove from exhausted list
                    del self.exhausted[index]
                    print(f"[API Rotation] Pair {index + 1} cooling period complete")
                else:
                    # Still cooling off - try next pair
                    continue

            # Pair is available - use it
            self.current_index = (index + 1) % len(self.pairs)
            api_key, base_url, model = self.pairs[index]
            return (index, api_key, base_url, model)

        # All pairs exhausted
        return None

    def _is_cooled_off(
        self, quota_type: QuotaType, exhausted_at: float, current_time: float
    ) -> bool:
        """
        Check if cooling period has elapsed for a quota type.

        Args:
            quota_type: Type of quota exhaustion
            exhausted_at: Unix timestamp when exhausted
            current_time: Current Unix timestamp

        Returns:
            True if cooling period complete
        """
        if quota_type == QuotaType.RATE_LIMIT:
            # 60 second cooling
            return current_time - exhausted_at >= 60

        elif quota_type == QuotaType.SESSION_EXPIRY:
            # 4 hour cooling
            return current_time - exhausted_at >= 4 * 3600

        elif quota_type == QuotaType.DAILY_QUOTA:
            # Wait until next day UTC
            exhausted_dt = datetime.fromtimestamp(exhausted_at, tz=timezone.utc)
            current_dt = datetime.fromtimestamp(current_time, tz=timezone.utc)
            return current_dt.date() > exhausted_dt.date()

        elif quota_type == QuotaType.WEEKLY_QUOTA:
            # Wait until next Monday UTC
            exhausted_dt = datetime.fromtimestamp(exhausted_at, tz=timezone.utc)
            current_dt = datetime.fromtimestamp(current_time, tz=timezone.utc)

            # Calculate next Monday after exhausted_at
            days_until_monday = (7 - exhausted_dt.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_monday = exhausted_dt.date() + timedelta(days=days_until_monday)

            return current_dt.date() >= next_monday

        return False
