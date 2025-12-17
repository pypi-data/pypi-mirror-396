"""HTTP client for sending logs to the API."""

import time

import httpx

from navigator_sdk.config import Config
from navigator_sdk.retry import RetryPolicy, calculate_backoff, is_retryable_error


class Client:
    """Synchronous HTTP client for sending logs.

    Args:
        config: Configuration object containing API key, endpoint, etc.
        retry_policy: Retry policy configuration. If None, uses default RetryPolicy()

    Example:
        >>> config = Config(api_key="pk_live_xxx", domain="my-domain",
        ...                 service="my-service", env="production")
        >>> client = Client(config)
        >>> log_data = {"domain": "my-domain", "service": "my-service",
        ...             "log_level": "INFO", "message": "test"}
        >>> success = client.send_log(log_data)
    """

    def __init__(self, config: Config, retry_policy: RetryPolicy | None = None):
        """Initialize HTTP client."""
        self.config = config
        self.retry_policy = retry_policy or RetryPolicy(
            max_attempts=config.max_retries + 1,  # Convert retries to total attempts
            base_delay=config.retry_base_delay,
            max_delay=config.retry_max_delay,
        )
        self.http_client = httpx.Client(timeout=config.timeout)
        self.endpoint = f"{config.base_url}/v1/ingest/"

        # Statistics tracking
        self.stats = {
            "success": 0,
            "failure": 0,
            "retries": 0,
        }

    def send_log(self, log_data: dict) -> bool:
        """Send a single log to the API with retry logic.

        Args:
            log_data: Log data in API format (dict with domain, service,
                     log_level, message, timestamp, env, etc.)

        Returns:
            True if log was sent successfully (202 status), False otherwise

        Example:
            >>> log_data = {
            ...     "domain": "payment-platform",
            ...     "service": "checkout-service",
            ...     "log_level": "ERROR",
            ...     "message": "Payment failed",
            ...     "timestamp": "2024-01-15T12:34:56.789Z",
            ...     "env": "production"
            ... }
            >>> success = client.send_log(log_data)
        """
        for attempt in range(self.retry_policy.max_attempts):
            try:
                response = self.http_client.post(
                    self.endpoint,
                    json=log_data,
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json",
                    },
                )

                # API returns 202 Accepted on success
                if response.status_code == 202:
                    self.stats["success"] += 1
                    return True

                # Check if error is retryable
                if not is_retryable_error(response.status_code, None):
                    # Non-retryable error (400, 401, 403, 404, etc.) - fail fast
                    self.stats["failure"] += 1
                    return False

                # Error is retryable (429, 500+), will retry on next iteration

            except (httpx.HTTPError, httpx.ConnectError, httpx.TimeoutException) as e:
                # Check if exception is retryable
                if not is_retryable_error(None, e):
                    # Non-retryable exception - fail fast
                    self.stats["failure"] += 1
                    return False

                # Exception is retryable, will retry on next iteration

            # If we get here, error is retryable and we may have attempts remaining
            if attempt < self.retry_policy.max_attempts - 1:
                # Calculate backoff delay and sleep before next attempt
                delay = calculate_backoff(attempt, self.retry_policy)
                self.stats["retries"] += 1
                time.sleep(delay)

        # All attempts exhausted without success
        self.stats["failure"] += 1
        return False

    def get_stats(self) -> dict:
        """Get client statistics.

        Returns:
            Dictionary with success, failure, and retry counts

        Example:
            >>> client.send_log(log_data)
            >>> stats = client.get_stats()
            >>> stats
            {'success': 1, 'failure': 0, 'retries': 0}
        """
        return self.stats.copy()

    def close(self):
        """Close the HTTP client and release resources."""
        self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
