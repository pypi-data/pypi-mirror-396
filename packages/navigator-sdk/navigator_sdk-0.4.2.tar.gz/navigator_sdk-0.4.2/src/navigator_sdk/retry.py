"""Retry logic and configuration for the Navigator SDK."""

import random

import httpx


class RetryPolicy:
    """Configuration for retry behavior.

    Args:
        max_attempts: Total number of attempts (initial + retries). Default: 3
        base_delay: Initial delay in seconds before first retry. Default: 1.0
        max_delay: Maximum delay cap in seconds. Default: 60.0
        exponential_base: Exponential growth factor for backoff. Default: 2.0
        jitter: Whether to add randomization to delays. Default: True

    Raises:
        ValueError: If validation fails on any parameter

    Example:
        >>> policy = RetryPolicy(max_attempts=3, base_delay=1.0)
        >>> policy.max_attempts
        3
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry policy with validation."""
        # Validate max_attempts
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        # Validate base_delay
        if base_delay <= 0:
            raise ValueError("base_delay must be greater than 0")

        # Validate max_delay
        if max_delay < base_delay:
            raise ValueError("max_delay must be greater than or equal to base_delay")

        # Validate exponential_base
        if exponential_base <= 1:
            raise ValueError("exponential_base must be greater than 1")

        # Assign after validation
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def calculate_backoff(attempt: int, policy: RetryPolicy) -> float:
    """Calculate backoff delay with exponential growth and optional jitter.

    Uses exponential backoff: delay = base_delay * (exponential_base ^ attempt)
    Then applies max_delay cap and optional jitter randomization.

    Args:
        attempt: The attempt number (0-indexed, 0 = first retry)
        policy: RetryPolicy configuration

    Returns:
        Delay in seconds to wait before next retry

    Example:
        >>> policy = RetryPolicy(base_delay=1.0, exponential_base=2.0, jitter=False)
        >>> calculate_backoff(0, policy)  # First retry
        1.0
        >>> calculate_backoff(1, policy)  # Second retry
        2.0
        >>> calculate_backoff(2, policy)  # Third retry
        4.0
    """
    # Calculate exponential delay
    delay = policy.base_delay * (policy.exponential_base**attempt)

    # Apply max delay cap
    delay = min(delay, policy.max_delay)

    # Apply jitter if enabled (random value between 50% and 100% of delay)
    if policy.jitter:
        delay = delay * random.uniform(0.5, 1.0)

    return delay


def is_retryable_error(status_code: int | None, exception: Exception | None) -> bool:
    """Determine if an error should trigger a retry.

    Retryable errors (transient failures):
    - HTTP 429 (Too Many Requests)
    - HTTP 500+ (Server errors: 500, 502, 503, 504, etc.)
    - httpx.ConnectError (connection refused, DNS failure)
    - httpx.TimeoutException (request timeout)
    - Generic httpx.HTTPError without status code

    Non-retryable errors (permanent failures):
    - HTTP 400 (Bad Request - invalid payload)
    - HTTP 401 (Unauthorized - invalid API key)
    - HTTP 403 (Forbidden)
    - HTTP 404 (Not Found)
    - Other 4xx client errors

    Args:
        status_code: HTTP status code from response, or None if network error
        exception: Exception that occurred, or None if HTTP error

    Returns:
        True if error is retryable (transient), False otherwise

    Example:
        >>> is_retryable_error(429, None)  # Rate limit
        True
        >>> is_retryable_error(500, None)  # Server error
        True
        >>> is_retryable_error(400, None)  # Bad request
        False
        >>> is_retryable_error(None, httpx.TimeoutException("timeout"))
        True
    """
    # Check HTTP status codes
    if status_code is not None:
        # Retryable: 429 (rate limit) and 5xx (server errors)
        if status_code == 429 or status_code >= 500:
            return True
        # Non-retryable: All other status codes (including 4xx)
        return False

    # Check exception types
    if exception is not None:
        # Retryable: Network errors and timeouts
        if isinstance(exception, (httpx.ConnectError, httpx.TimeoutException)):
            return True
        # Retryable: Generic HTTP errors (unknown cause, safer to retry)
        if isinstance(exception, httpx.HTTPError):
            return True

    # Default: not retryable
    return False
