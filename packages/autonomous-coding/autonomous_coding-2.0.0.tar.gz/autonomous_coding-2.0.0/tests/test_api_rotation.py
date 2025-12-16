"""
Unit tests for API rotation and quota detection.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from utils.api_rotation import (
    APIRotationState,
    QuotaType,
    detect_quota_exhaustion,
    load_api_credentials,
)


class TestQuotaDetection:
    """Test quota exhaustion detection."""

    def test_http_429_detected_as_rate_limit(self):
        """HTTP 429 should be detected as rate limit."""
        is_quota, quota_type = detect_quota_exhaustion(429, "Rate limit exceeded")
        assert is_quota is True
        assert quota_type == QuotaType.RATE_LIMIT

    def test_http_401_with_session_keywords(self):
        """HTTP 401 with session keywords should be detected as session expiry."""
        is_quota, quota_type = detect_quota_exhaustion(
            401, "Authentication failed: session expired"
        )
        assert is_quota is True
        assert quota_type == QuotaType.SESSION_EXPIRY

    def test_http_403_with_invalid_token(self):
        """HTTP 403 with invalid token should be detected as session expiry."""
        is_quota, quota_type = detect_quota_exhaustion(403, "Invalid token provided")
        assert is_quota is True
        assert quota_type == QuotaType.SESSION_EXPIRY

    def test_daily_quota_in_error_message(self):
        """Daily quota keywords in error message should be detected."""
        is_quota, quota_type = detect_quota_exhaustion(
            400, "You have exceeded your daily quota limit"
        )
        assert is_quota is True
        assert quota_type == QuotaType.DAILY_QUOTA

    def test_weekly_quota_in_error_message(self):
        """Weekly quota keywords in error message should be detected."""
        is_quota, quota_type = detect_quota_exhaustion(
            400, "Weekly limit reached, resets on Monday"
        )
        assert is_quota is True
        assert quota_type == QuotaType.WEEKLY_QUOTA

    def test_non_quota_error(self):
        """Non-quota errors should not be detected as quota exhaustion."""
        is_quota, quota_type = detect_quota_exhaustion(500, "Internal server error")
        assert is_quota is False
        assert quota_type is None

    def test_none_status_code(self):
        """None status code should still check error message."""
        is_quota, quota_type = detect_quota_exhaustion(None, "rate limit exceeded")
        assert is_quota is True
        assert quota_type == QuotaType.RATE_LIMIT


class TestLoadAPICredentials:
    """Test loading API credentials from environment variables."""

    def test_load_numbered_credentials(self):
        """Should load numbered API key/endpoint pairs."""
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY_1": "key1",
                "ANTHROPIC_BASE_URL_1": "https://api1.example.com",
                "ANTHROPIC_API_KEY_2": "key2",
                "ANTHROPIC_BASE_URL_2": "https://api2.example.com",
                "ANTHROPIC_API_KEY_3": "key3",
                # No BASE_URL_3, should default
            },
            clear=True,
        ):
            pairs = load_api_credentials()
            assert len(pairs) == 3
            assert pairs[0] == ("key1", "https://api1.example.com", None)
            assert pairs[1] == ("key2", "https://api2.example.com", None)
            assert pairs[2] == ("key3", "https://api.anthropic.com", None)

    def test_fallback_to_single_credential(self):
        """Should fallback to single ANTHROPIC_API_KEY if no numbered pairs."""
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "single-key",
                "ANTHROPIC_BASE_URL": "https://custom.example.com",
            },
            clear=True,
        ):
            pairs = load_api_credentials()
            assert len(pairs) == 1
            assert pairs[0] == ("single-key", "https://custom.example.com", None)

    def test_fallback_to_single_credential_default_url(self):
        """Should use default URL if ANTHROPIC_BASE_URL not set."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "single-key"}, clear=True):
            pairs = load_api_credentials()
            assert len(pairs) == 1
            assert pairs[0] == ("single-key", "https://api.anthropic.com", None)

    def test_no_credentials_returns_empty(self):
        """Should return empty list if no credentials found."""
        with patch.dict(os.environ, {}, clear=True):
            pairs = load_api_credentials()
            assert len(pairs) == 0


class TestAPIRotationState:
    """Test API rotation state management."""

    def test_initialization_with_multiple_pairs(self):
        """Should initialize with multiple API key/endpoint pairs."""
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY_1": "key1",
                "ANTHROPIC_API_KEY_2": "key2",
                "ANTHROPIC_API_KEY_3": "key3",
            },
            clear=True,
        ):
            state = APIRotationState()
            assert len(state.pairs) == 3
            assert state.current_index == 0
            assert len(state.exhausted) == 0

    def test_initialization_raises_if_no_credentials(self):
        """Should raise ValueError if no credentials found."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(ValueError, match="No API credentials found"),
        ):
            APIRotationState()

    def test_mark_exhausted_records_quota_type(self):
        """Should record quota type and timestamp when marking exhausted."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY_1": "key1", "ANTHROPIC_API_KEY_2": "key2"},
            clear=True,
        ):
            state = APIRotationState()
            before = time.time()
            state.mark_exhausted(0, QuotaType.RATE_LIMIT)
            after = time.time()

            assert 0 in state.exhausted
            quota_type, timestamp = state.exhausted[0]
            assert quota_type == QuotaType.RATE_LIMIT
            assert before <= timestamp <= after

    def test_get_next_available_pair_returns_first_available(self):
        """Should return first non-exhausted pair."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY_1": "key1", "ANTHROPIC_API_KEY_2": "key2"},
            clear=True,
        ):
            state = APIRotationState()
            index, key, url, model = state.get_next_available_pair()
            assert index == 0
            assert key == "key1"
            assert url == "https://api.anthropic.com"
            assert model is None

    def test_get_next_available_pair_skips_exhausted(self):
        """Should skip exhausted pairs and return next available."""
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY_1": "key1",
                "ANTHROPIC_API_KEY_2": "key2",
                "ANTHROPIC_API_KEY_3": "key3",
            },
            clear=True,
        ):
            state = APIRotationState()
            # Mark first pair as exhausted
            state.mark_exhausted(0, QuotaType.RATE_LIMIT)

            # Should get second pair
            index, key, url, model = state.get_next_available_pair()
            assert index == 1
            assert key == "key2"
            assert model is None

    def test_get_next_available_pair_returns_none_if_all_exhausted(self):
        """Should return None if all pairs are exhausted."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY_1": "key1", "ANTHROPIC_API_KEY_2": "key2"},
            clear=True,
        ):
            state = APIRotationState()
            # Mark both pairs as exhausted
            state.mark_exhausted(0, QuotaType.RATE_LIMIT)
            state.mark_exhausted(1, QuotaType.RATE_LIMIT)

            result = state.get_next_available_pair()
            assert result is None

    def test_cooling_period_rate_limit(self):
        """Rate limit should cool off after 60 seconds."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY_1": "key1", "ANTHROPIC_API_KEY_2": "key2"},
            clear=True,
        ):
            state = APIRotationState()

            # Mark as exhausted 61 seconds ago
            past_time = time.time() - 61
            state.exhausted[0] = (QuotaType.RATE_LIMIT, past_time)

            # Should be available again
            index, key, url, model = state.get_next_available_pair()
            assert index == 0
            assert model is None
            assert 0 not in state.exhausted  # Should be removed from exhausted list

    def test_cooling_period_session_expiry(self):
        """Session expiry should cool off after 4 hours."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY_1": "key1", "ANTHROPIC_API_KEY_2": "key2"},
            clear=True,
        ):
            state = APIRotationState()

            # Mark as exhausted 4.1 hours ago
            past_time = time.time() - (4 * 3600 + 360)
            state.exhausted[0] = (QuotaType.SESSION_EXPIRY, past_time)

            # Should be available again
            index, key, url, model = state.get_next_available_pair()
            assert index == 0
            assert model is None
            assert 0 not in state.exhausted

    def test_cooling_period_daily_quota(self):
        """Daily quota should cool off after day changes."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY_1": "key1", "ANTHROPIC_API_KEY_2": "key2"},
            clear=True,
        ):
            state = APIRotationState()

            # Mark as exhausted yesterday
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            state.exhausted[0] = (QuotaType.DAILY_QUOTA, yesterday.timestamp())

            # Should be available again (new day)
            index, key, url, model = state.get_next_available_pair()
            assert index == 0
            assert model is None
            assert 0 not in state.exhausted

    def test_round_robin_rotation(self):
        """Should rotate through pairs in round-robin fashion."""
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY_1": "key1",
                "ANTHROPIC_API_KEY_2": "key2",
                "ANTHROPIC_API_KEY_3": "key3",
            },
            clear=True,
        ):
            state = APIRotationState()

            # Get first pair
            index1, _, _, _ = state.get_next_available_pair()
            assert index1 == 0

            # Get second pair
            index2, _, _, _ = state.get_next_available_pair()
            assert index2 == 1

            # Get third pair
            index3, _, _, _ = state.get_next_available_pair()
            assert index3 == 2

            # Should wrap around to first
            index4, _, _, _ = state.get_next_available_pair()
            assert index4 == 0


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_full_rotation_on_rate_limits(self):
        """Test full rotation cycle when hitting rate limits."""
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY_1": "key1",
                "ANTHROPIC_API_KEY_2": "key2",
                "ANTHROPIC_API_KEY_3": "key3",
            },
            clear=True,
        ):
            state = APIRotationState()

            # Simulate hitting rate limit on each key
            for i in range(3):
                index, key, url, model = state.get_next_available_pair()
                assert index == i
                # Simulate rate limit
                state.mark_exhausted(index, QuotaType.RATE_LIMIT)

            # All exhausted - should return None
            result = state.get_next_available_pair()
            assert result is None

    def test_recovery_after_cooling_period(self):
        """Test that keys become available after cooling period."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY_1": "key1", "ANTHROPIC_API_KEY_2": "key2"},
            clear=True,
        ):
            state = APIRotationState()

            # Mark both as exhausted with rate limits
            current_time = time.time()
            state.exhausted[0] = (QuotaType.RATE_LIMIT, current_time - 61)  # Cooled off
            state.exhausted[1] = (QuotaType.RATE_LIMIT, current_time - 30)  # Still hot

            # Should get first pair (cooled off)
            index, key, url, model = state.get_next_available_pair()
            assert index == 0
            assert model is None

            # After using index 0, current_index advances to 1
            # Second call wraps around to 0 again (round robin)
            index2, key2, url2, model2 = state.get_next_available_pair()
            assert index2 == 0  # Wraps around after exhausted list check
            assert model2 is None
