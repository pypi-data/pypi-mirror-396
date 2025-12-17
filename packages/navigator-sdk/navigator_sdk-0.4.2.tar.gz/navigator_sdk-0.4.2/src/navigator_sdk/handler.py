"""Logging handler for Navigator SDK."""

import logging
from datetime import datetime, timezone
from typing import Any

from navigator_sdk.client import Client
from navigator_sdk.config import Config


class Handler(logging.Handler):
    """Custom logging handler that sends logs to Navigator API.

    Integrates with Python's standard logging module to automatically
    send logs to the Navigator API.

    Args:
        config: Configuration object with API credentials and settings

    Example:
        >>> import logging
        >>> config = Config(api_key="pk_live_xxx", domain="my-domain",
        ...                 service="my-service", env="production")
        >>> handler = Handler(config)
        >>> logger = logging.getLogger()
        >>> logger.addHandler(handler)
        >>> logger.info("Hello world")
    """

    # Map Python log levels to Navigator API log levels
    LEVEL_MAPPING = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    def __init__(self, config: Config):
        """Initialize the handler."""
        super().__init__()
        self.config = config
        self.client = Client(config)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Navigator API.

        This method is called by the logging module whenever a log is emitted.

        Args:
            record: LogRecord object from Python's logging module

        Note:
            This method never raises exceptions - failures are handled
            gracefully to avoid crashing the application.
        """
        # Prevent recursion: ignore logs from httpx and httpcore
        # (these are internal HTTP client logs that would create a loop)
        if record.name.startswith(("httpx", "httpcore")):
            return

        try:
            log_data = self._format_log(record)
            self.client.send_log(log_data)
        except Exception:
            # Don't crash the application if logging fails
            # Use Python's built-in error handling for logging
            self.handleError(record)

    def _format_log(self, record: logging.LogRecord) -> dict[str, Any]:
        """Format a LogRecord into Navigator API format.

        Args:
            record: Python LogRecord object

        Returns:
            Dictionary with log data in Navigator API format

        The log data includes:
            - Required fields: domain, service, log_level, message, timestamp, env
            - Optional fields: component, operation, trace_id, metadata
        """
        # Base required fields
        log_data = {
            "domain": self.config.domain,
            "service": self.config.service,
            "log_level": self.LEVEL_MAPPING.get(record.levelno, "INFO"),
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "env": self.config.env,
        }

        # Add component from config if available
        if self.config.component:
            log_data["component"] = self.config.component

        # Add trace_id from config if available
        if self.config.trace_id:
            log_data["trace_id"] = self.config.trace_id

        # Extract optional fields from record's extra data
        # Users can pass these via: logging.info("msg", extra={"trace_id": "..."})
        # Note: record fields override config defaults
        for field in ["component", "operation", "trace_id", "metadata"]:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        return log_data

    def close(self) -> None:
        """Close the handler and release resources."""
        self.client.close()
        super().close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
