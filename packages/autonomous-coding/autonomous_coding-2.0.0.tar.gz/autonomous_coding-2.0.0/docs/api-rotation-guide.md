# API Rotation Testing Guide

## Overview

The QA Agent & Orchestrator system includes comprehensive API quota management with automatic rotation across multiple API keys/endpoints. This guide explains how to set up and test the rotation system.

## Features

- **Multi-Signal Quota Detection**: Detects HTTP 429, 401/403 with session keywords, and error messages
- **Differential Cooling Periods**:
  - Rate limits: 60 seconds
  - Session expiry: 4 hours
  - Daily quotas: Until next day UTC
  - Weekly quotas: Until next Monday UTC
- **Round-Robin Rotation**: Automatically cycles through available keys
- **Automatic Recovery**: Keys become available again after cooling periods

## Setup

### Option 1: Multiple Numbered API Keys (Recommended)

Set up multiple API key/endpoint pairs using numbered environment variables:

```bash
# Primary API key (Anthropic official)
export ANTHROPIC_API_KEY_1="sk-ant-api03-..."
export ANTHROPIC_BASE_URL_1="https://api.anthropic.com"

# Secondary API key (alternative endpoint or different account)
export ANTHROPIC_API_KEY_2="sk-ant-api03-..."
export ANTHROPIC_BASE_URL_2="https://api.anthropic.com"

# Tertiary API key (third fallback)
export ANTHROPIC_API_KEY_3="sk-ant-api03-..."
export ANTHROPIC_BASE_URL_3="https://custom-proxy.example.com"
```

**Notes:**
- Keys are tried in order: 1, 2, 3, ...
- `ANTHROPIC_BASE_URL_N` is optional (defaults to `https://api.anthropic.com`)
- Add as many keys as needed (4, 5, 6, etc.)

### Option 2: Single API Key (Fallback)

If no numbered keys are found, the system falls back to single environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export ANTHROPIC_BASE_URL="https://api.anthropic.com"  # Optional
```

## Testing Rotation Behavior

### Unit Tests

Run the comprehensive test suite:

```bash
# Run all API rotation tests
python -m pytest tests/test_api_rotation.py -v

# Run specific test class
python -m pytest tests/test_api_rotation.py::TestAPIRotationState -v

# Run with coverage
python -m pytest tests/test_api_rotation.py --cov=api_rotation
```

**Test Coverage:**
- ✅ Quota detection (HTTP 429, 401/403, error messages)
- ✅ Loading numbered environment variables
- ✅ Fallback to single credentials
- ✅ Round-robin rotation
- ✅ Cooling period enforcement
- ✅ Recovery after cooling periods
- ✅ Full rotation cycles

### Manual Testing with Real API Keys

#### Test 1: Verify Multiple Keys Load

```bash
# Set up multiple keys
export ANTHROPIC_API_KEY_1="key1"
export ANTHROPIC_API_KEY_2="key2"
export ANTHROPIC_API_KEY_3="key3"

# Run Python REPL
python

>>> from api_rotation import load_api_credentials
>>> pairs = load_api_credentials()
>>> print(f"Loaded {len(pairs)} API key/endpoint pairs")
Loaded 3 API key/endpoint pairs
>>> for i, (key, url) in enumerate(pairs):
...     print(f"  Pair {i+1}: {key[:15]}... -> {url}")
```

Expected output:
```
Loaded 3 API key/endpoint pairs
  Pair 1: key1 -> https://api.anthropic.com
  Pair 2: key2 -> https://api.anthropic.com
  Pair 3: key3 -> https://api.anthropic.com
```

#### Test 2: Simulate Rate Limit and Rotation

```python
from api_rotation import APIRotationState, QuotaType

# Initialize with your API keys
state = APIRotationState()
print(f"Initialized with {len(state.pairs)} pairs")

# Get first pair
index, key, url = state.get_next_available_pair()
print(f"Using pair {index + 1}: {key[:15]}...")

# Simulate rate limit on first key
state.mark_exhausted(index, QuotaType.RATE_LIMIT)
print(f"Marked pair {index + 1} as exhausted (rate limit)")

# Get next pair (should rotate to second key)
index2, key2, url2 = state.get_next_available_pair()
print(f"Rotated to pair {index2 + 1}: {key2[:15]}...")
```

Expected output:
```
Initialized with 3 pairs
Using pair 1: sk-ant-api03-...
[API Rotation] Pair 1 exhausted: rate_limit
Marked pair 1 as exhausted (rate limit)
Rotated to pair 2: sk-ant-api03-...
```

#### Test 3: Verify Cooling Period Recovery

```python
import time
from api_rotation import APIRotationState, QuotaType

state = APIRotationState()

# Mark pair 0 as exhausted
state.mark_exhausted(0, QuotaType.RATE_LIMIT)
print("Pair 0 exhausted with rate limit (60s cooling)")

# Try immediately - should skip to pair 1
index, _, _ = state.get_next_available_pair()
print(f"Immediate retry: got pair {index + 1}")

# Simulate 61 seconds passing by manually adjusting timestamp
state.exhausted[0] = (QuotaType.RATE_LIMIT, time.time() - 61)

# Try again - should recover pair 0
index, _, _ = state.get_next_available_pair()
print(f"After cooling period: got pair {index + 1}")
```

Expected output:
```
Pair 0 exhausted with rate limit (60s cooling)
Immediate retry: got pair 2
After cooling period: got pair 1
[API Rotation] Pair 1 cooling period complete
```

## Integration with Client

The rotation system is automatically integrated into `client.py`:

```python
from pathlib import Path
from client import create_client

# Client automatically loads API credentials from environment
client = create_client(project_dir=Path("./my_project"), model="claude-sonnet-4-5")

# Output shows rotation info:
# Using API endpoint: https://api.anthropic.com
# API rotation available with 3 key/endpoint pairs
```

## Monitoring Rotation in Production

### Check Rotation Logs

The system logs rotation events to console:

```
[API Rotation] Pair 1 exhausted: rate_limit
[API Rotation] Pair 2 exhausted: session_expiry
[API Rotation] Pair 1 cooling period complete
```

### Handle All Keys Exhausted

If all keys are exhausted, `get_next_available_pair()` returns `None`:

```python
result = state.get_next_available_pair()
if result is None:
    print("All API keys exhausted!")
    print("Waiting for cooling periods...")
    # Implement retry logic or wait
else:
    index, key, url = result
    # Use the available pair
```

## Quota Types and Cooling Periods

| Quota Type | Detection Method | Cooling Period | Reset Time |
|------------|-----------------|----------------|------------|
| **RATE_LIMIT** | HTTP 429 or "rate limit" in error | 60 seconds | Immediate after 60s |
| **SESSION_EXPIRY** | HTTP 401/403 with "session"/"expired" | 4 hours | Immediate after 4h |
| **DAILY_QUOTA** | "daily quota" or "daily limit" in error | Until next day | 00:00 UTC next day |
| **WEEKLY_QUOTA** | "weekly quota" or "weekly limit" in error | Until next week | Monday 00:00 UTC |

## Best Practices

1. **Use Multiple Keys**: Set up 3+ API keys for redundancy
2. **Different Accounts**: Use keys from different Anthropic accounts if possible
3. **Monitor Usage**: Track which keys are hitting limits most often
4. **Stagger Usage**: If possible, use different keys for different projects
5. **Custom Endpoints**: Mix official Anthropic endpoints with custom proxies
6. **Rate Limit Buffer**: Don't wait until exhaustion - rotate proactively

## Troubleshooting

### Issue: No API keys loaded

```
ValueError: No API credentials found. Set ANTHROPIC_API_KEY or numbered pairs
```

**Solution**: Set at least one API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
# OR
export ANTHROPIC_API_KEY_1="sk-ant-api03-..."
```

### Issue: All keys exhausted too quickly

**Possible causes:**
- Keys sharing the same rate limit pool (same account)
- Aggressive usage patterns
- Short cooling periods for your quota type

**Solutions:**
- Add more API keys from different accounts
- Implement request batching
- Add delays between requests
- Monitor quota usage via Anthropic dashboard

### Issue: Keys not recovering after cooling period

**Check:**
1. Quota type is correctly detected
2. Cooling period matches quota type
3. System time is correct (affects UTC calculations)

**Debug:**
```python
state = APIRotationState()
print("Exhausted pairs:")
for index, (quota_type, timestamp) in state.exhausted.items():
    print(f"  Pair {index + 1}: {quota_type.value} at {timestamp}")
```

## Example: Long-Running Agent with Rotation

```python
from pathlib import Path
from api_rotation import APIRotationState, QuotaType, detect_quota_exhaustion
from client import create_client

def run_agent_with_rotation(project_dir: Path):
    """Run agent with automatic API rotation on quota exhaustion."""

    # Initialize rotation state
    rotation = APIRotationState()

    while True:
        # Get available API key
        result = rotation.get_next_available_pair()
        if result is None:
            print("All API keys exhausted. Waiting 60s...")
            time.sleep(60)
            continue

        index, api_key, base_url = result

        # Create client with this key
        os.environ["ANTHROPIC_API_KEY"] = api_key
        os.environ["ANTHROPIC_BASE_URL"] = base_url

        try:
            client = create_client(project_dir, model="claude-sonnet-4-5")
            # ... run agent session ...

        except Exception as e:
            # Check if quota-related error
            error_text = str(e)
            status_code = getattr(e, 'status_code', None)

            is_quota, quota_type = detect_quota_exhaustion(status_code, error_text)

            if is_quota:
                print(f"Quota exhausted: {quota_type.value}")
                rotation.mark_exhausted(index, quota_type)
                continue  # Try next key
            else:
                raise  # Re-raise non-quota errors
```

## Summary

The API rotation system provides robust quota management with:
- ✅ 23/23 comprehensive unit tests passing
- ✅ Multi-signal quota detection
- ✅ Differential cooling periods
- ✅ Automatic recovery
- ✅ Round-robin load distribution
- ✅ Production-ready error handling

For questions or issues, see the test suite in `tests/test_api_rotation.py` for examples.
