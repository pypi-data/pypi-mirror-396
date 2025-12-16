"""Structured logging utilities for AI Profiler."""

import logging
import sys
from typing import Any, Optional


# Configure structured logging
def setup_logging(level: str = "INFO", use_json: bool = False) -> logging.Logger:
    """
    Set up structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (for production)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("aiprofile")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    logger.handlers = []

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Create formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="[%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        import json

        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_data.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def log_execution_start(
    logger: logging.Logger, script_path: str, script_args: list, timeout: Optional[int] = None
) -> None:
    """Log script execution start."""
    extra = {
        "extra_data": {
            "script_path": script_path,
            "script_args": script_args,
            "timeout_seconds": timeout,
            "event": "execution_start",
        }
    }
    logger.info(f"Starting execution of {script_path}", extra=extra)


def log_execution_end(
    logger: logging.Logger,
    script_path: str,
    exit_code: int,
    duration: float,
    success: bool,
) -> None:
    """Log script execution end."""
    extra = {
        "extra_data": {
            "script_path": script_path,
            "exit_code": exit_code,
            "duration_seconds": duration,
            "success": success,
            "event": "execution_end",
        }
    }
    level = "info" if success else "error"
    getattr(logger, level)(
        f"Execution {'completed' if success else 'failed'}: {script_path}",
        extra=extra,
    )


def log_profiling_start(logger: logging.Logger, profiler_type: str) -> None:
    """Log profiling start."""
    extra = {"extra_data": {"profiler_type": profiler_type, "event": "profiling_start"}}
    logger.info(f"Starting profiling with {profiler_type}", extra=extra)


def log_profiling_end(
    logger: logging.Logger, profiler_type: str, duration: float, success: bool
) -> None:
    """Log profiling end."""
    extra = {
        "extra_data": {
            "profiler_type": profiler_type,
            "duration_seconds": duration,
            "success": success,
            "event": "profiling_end",
        }
    }
    level = "info" if success else "error"
    getattr(logger, level)(
        f"Profiling {'completed' if success else 'failed'} ({profiler_type})",
        extra=extra,
    )


def log_analysis_start(logger: logging.Logger, analyzer_type: str) -> None:
    """Log analysis start."""
    extra = {"extra_data": {"analyzer_type": analyzer_type, "event": "analysis_start"}}
    logger.info(f"Starting analysis with {analyzer_type}", extra=extra)


def log_analysis_end(
    logger: logging.Logger, analyzer_type: str, duration: float, success: bool
) -> None:
    """Log analysis end."""
    extra = {
        "extra_data": {
            "analyzer_type": analyzer_type,
            "duration_seconds": duration,
            "success": success,
            "event": "analysis_end",
        }
    }
    level = "info" if success else "error"
    getattr(logger, level)(
        f"Analysis {'completed' if success else 'failed'} ({analyzer_type})",
        extra=extra,
    )


def log_error(
    logger: logging.Logger, error_type: str, message: str, details: Optional[dict[str, Any]] = None
) -> None:
    """Log an error with details."""
    extra = {"extra_data": {"error_type": error_type, "event": "error"}}
    if details:
        extra["extra_data"].update(details)
    logger.error(f"{error_type}: {message}", extra=extra)
