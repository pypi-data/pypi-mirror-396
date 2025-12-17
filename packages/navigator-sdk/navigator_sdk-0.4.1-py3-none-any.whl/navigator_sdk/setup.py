"""Setup utilities for Navigator SDK."""

import logging

from navigator_sdk.config import Config
from navigator_sdk.handler import Handler


def setup_logger(
    api_key: str | None = None,
    domain: str | None = None,
    service: str | None = None,
    env: str | None = None,
    base_url: str | None = None,
    component: str | None = None,
    timeout: int | None = None,
    trace_id: str | None = None,
    level: str = "INFO",
    logger_name: str | None = None,
):
    """Set up a logger that sends logs to Navigator.

    This function automatically loads configuration from environment variables
    and allows you to override specific values.

    Environment variables:
        NAVIGATOR_API_KEY: API key (required if not provided as argument)
        NAVIGATOR_DOMAIN: Domain name (required if not provided as argument)
        NAVIGATOR_SERVICE: Service name (required if not provided as argument)
        NAVIGATOR_ENVIRONMENT or ENVIRONMENT: Environment (default: "production")
        NAVIGATOR_API_URL: Base URL (default: "http://localhost:8000")
        NAVIGATOR_COMPONENT: Component name (optional)
        NAVIGATOR_TIMEOUT: Timeout in seconds (default: 10)
        NAVIGATOR_TRACE_ID: Default trace ID for correlating logs (optional)

    Args:
        api_key: API key (overrides NAVIGATOR_API_KEY)
        domain: Domain name (overrides NAVIGATOR_DOMAIN)
        service: Service name (overrides NAVIGATOR_SERVICE)
        env: Environment (overrides NAVIGATOR_ENVIRONMENT)
        base_url: Base URL (overrides NAVIGATOR_API_URL)
        component: Component name (overrides NAVIGATOR_COMPONENT)
        timeout: Timeout in seconds (overrides NAVIGATOR_TIMEOUT)
        trace_id: Default trace ID (overrides NAVIGATOR_TRACE_ID)
        level: Minimum log level (default: "INFO")
        logger_name: Logger name (default: root logger)

    Returns:
        Configured logger instance

    Raises:
        ValueError: If required configuration is missing or invalid

    Example:
        >>> from navigator_sdk import setup_logger
        >>> logger = setup_logger()  # Uses env vars
        >>> logger.info("Hello world")

        >>> # Or with explicit config
        >>> logger = setup_logger(
        ...     api_key="pk_live_xxx",
        ...     domain="my-domain",
        ...     service="my-service",
        ...     env="production"
        ... )
        >>> logger.info("Hello world")
    """
    # Build override dict (only include non-None values)
    overrides = {}
    if api_key is not None:
        overrides["api_key"] = api_key
    if domain is not None:
        overrides["domain"] = domain
    if service is not None:
        overrides["service"] = service
    if env is not None:
        overrides["env"] = env
    if base_url is not None:
        overrides["base_url"] = base_url
    if component is not None:
        overrides["component"] = component
    if timeout is not None:
        overrides["timeout"] = timeout
    if trace_id is not None:
        overrides["trace_id"] = trace_id

    # Create config (validates everything)
    config = Config.from_env(**overrides)

    # Create handler
    handler = Handler(config)

    # Map string level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = level_map.get(level.upper(), logging.INFO)
    handler.setLevel(log_level)

    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger
