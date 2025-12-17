"""Configuration for Navigator SDK."""

import os
from typing import Any


class Config:
    """Configuration for Navigator SDK.

    Args:
        api_key: API key (must start with pk_live_)
        domain: Logical domain (e.g., "payment-platform")
        service: Service name (e.g., "checkout-service")
        env: Environment (e.g., "production", "staging")
        base_url: Base URL of the API (default: http://localhost:8000)
        component: Optional default component name
        timeout: HTTP request timeout in seconds (default: 10)
        trace_id: Optional default trace ID for correlating logs
        max_retries: Maximum number of retries after initial attempt (default: 3 means 1 initial + 3 retries = 4 total attempts)
        retry_base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        retry_max_delay: Maximum delay cap in seconds (default: 60.0)

    Raises:
        ValueError: If API key doesn't start with pk_live_ or required fields are missing
    """

    def __init__(
        self,
        api_key: str,
        domain: str,
        service: str,
        env: str,
        base_url: str = "http://localhost:8000",
        component: str | None = None,
        timeout: int = 10,
        trace_id: str | None = None,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        retry_max_delay: float = 60.0,
    ):
        """Initialize configuration."""
        # Validate API key format
        if not api_key.startswith("pk_live_"):
            raise ValueError("API key must start with 'pk_live_'")

        # Validate required fields
        if not domain:
            raise ValueError("domain is required")
        if not service:
            raise ValueError("service is required")
        if not env:
            raise ValueError("env is required")

        self.api_key = api_key
        self.domain = domain
        self.service = service
        self.env = env
        self.base_url = base_url.rstrip("/")
        self.component = component
        self.timeout = timeout
        self.trace_id = trace_id
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay

    @classmethod
    def from_env(cls, **overrides: Any) -> "Config":
        """Create configuration from environment variables.

        Environment variables:
            NAVIGATOR_API_KEY: API key
            NAVIGATOR_DOMAIN: Domain name
            NAVIGATOR_SERVICE: Service name
            NAVIGATOR_ENVIRONMENT or ENVIRONMENT: Environment
            NAVIGATOR_API_URL: Base URL (optional)
            NAVIGATOR_COMPONENT: Component name (optional)
            NAVIGATOR_TIMEOUT: Timeout in seconds (optional)
            NAVIGATOR_TRACE_ID: Default trace ID for correlating logs (optional)
            NAVIGATOR_MAX_RETRIES: Maximum retries after initial attempt (optional, default: 3)
            NAVIGATOR_RETRY_BASE_DELAY: Base retry delay in seconds (optional, default: 1.0)
            NAVIGATOR_RETRY_MAX_DELAY: Max retry delay in seconds (optional, default: 60.0)

        Args:
            **overrides: Override specific config values

        Returns:
            Config instance

        Raises:
            ValueError: If required environment variables are missing
        """
        config = {
            "api_key": os.getenv("NAVIGATOR_API_KEY"),
            "domain": os.getenv("NAVIGATOR_DOMAIN"),
            "service": os.getenv("NAVIGATOR_SERVICE"),
            "env": os.getenv("NAVIGATOR_ENVIRONMENT")
            or os.getenv("ENVIRONMENT", "production"),
            "base_url": os.getenv("NAVIGATOR_API_URL", "http://localhost:8000"),
            "component": os.getenv("NAVIGATOR_COMPONENT"),
            "timeout": int(os.getenv("NAVIGATOR_TIMEOUT", "10")),
            "trace_id": os.getenv("NAVIGATOR_TRACE_ID"),
            "max_retries": int(os.getenv("NAVIGATOR_MAX_RETRIES", "3")),
            "retry_base_delay": float(os.getenv("NAVIGATOR_RETRY_BASE_DELAY", "1.0")),
            "retry_max_delay": float(os.getenv("NAVIGATOR_RETRY_MAX_DELAY", "60.0")),
        }

        # Apply overrides
        config.update({k: v for k, v in overrides.items() if v is not None})

        # Validate required fields
        required = ["api_key", "domain", "service"]
        missing = [k for k in required if not config.get(k)]
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Provide via environment variables or explicit arguments."
            )

        return cls(**config)
