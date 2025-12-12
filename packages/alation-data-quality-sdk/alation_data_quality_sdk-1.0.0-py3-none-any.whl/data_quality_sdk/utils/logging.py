"""Logging configuration for the Data Quality SDK."""

import logging
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO", logger_name: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration for the SDK.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Optional logger name, defaults to 'data_quality_sdk'

    Returns:
        Configured logger instance
    """
    logger_name = logger_name or "data_quality_sdk"
    logger = logging.getLogger(logger_name)

    # Only configure if no handlers exist (avoid duplicate configuration)
    if not logger.handlers:
        # Set level
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")

        logger.setLevel(numeric_level)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name, defaults to 'data_quality_sdk'

    Returns:
        Logger instance
    """
    logger_name = name or "data_quality_sdk"
    return logging.getLogger(logger_name)


def log_api_request(logger: logging.Logger, method: str, url: str, status_code: int = None):
    """Log API request details.

    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        url: Request URL (sensitive parts will be masked)
        status_code: Response status code (optional)
    """
    # Mask sensitive information in URL
    masked_url = mask_sensitive_url_parts(url)

    if status_code:
        logger.info(f"{method} {masked_url} -> {status_code}")
    else:
        logger.info(f"{method} {masked_url}")


def log_scan_progress(logger: logging.Logger, message: str, check_count: int = None):
    """Log Soda scan progress.

    Args:
        logger: Logger instance
        message: Progress message
        check_count: Number of checks (optional)
    """
    if check_count is not None:
        logger.info(f"Soda Scan: {message} (checks: {check_count})")
    else:
        logger.info(f"Soda Scan: {message}")


def mask_sensitive_url_parts(url: str) -> str:
    """Mask sensitive parts of URLs for logging.

    Args:
        url: URL to mask

    Returns:
        URL with sensitive parts masked
    """
    import re

    # Mask API keys and tokens in query parameters
    url = re.sub(r"([?&](?:api_key|token|key)=)[^&]*", r"\1***", url)

    # Mask credentials in URLs (basic auth)
    url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)

    return url
