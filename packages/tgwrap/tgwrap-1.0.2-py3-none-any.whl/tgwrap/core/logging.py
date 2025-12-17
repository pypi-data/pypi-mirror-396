"""Structured logging for tgwrap."""

import json
import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .security import SecurityValidator


class LogLevel(Enum):
    """Log levels for tgwrap."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class StructuredLogger:
    """Structured logger with security-aware output."""

    def __init__(self, name: str = "tgwrap", level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))

        # Create console handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(getattr(logging, level.value))

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def _create_log_entry(
        self,
        level: LogLevel,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a structured log entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.value,
            "message": SecurityValidator.sanitize_for_logging(message),
            "component": "tgwrap"
        }

        # Add sanitized extra fields
        for key, value in kwargs.items():
            if isinstance(value, str):
                entry[key] = SecurityValidator.sanitize_for_logging(value)
            else:
                entry[key] = value

        return entry

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        entry = self._create_log_entry(LogLevel.DEBUG, message, **kwargs)
        self.logger.debug(json.dumps(entry) if kwargs else message)

    def info(self, message: str, **kwargs):
        """Log info message."""
        entry = self._create_log_entry(LogLevel.INFO, message, **kwargs)
        self.logger.info(json.dumps(entry) if kwargs else message)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        entry = self._create_log_entry(LogLevel.WARNING, message, **kwargs)
        self.logger.warning(json.dumps(entry) if kwargs else message)

    def error(self, message: str, **kwargs):
        """Log error message."""
        entry = self._create_log_entry(LogLevel.ERROR, message, **kwargs)
        self.logger.error(json.dumps(entry) if kwargs else message)

    def log_command_execution(
        self,
        command: str,
        working_dir: Optional[str] = None,
        return_code: Optional[int] = None,
        duration: Optional[float] = None
    ):
        """Log command execution details."""
        sanitized_command = SecurityValidator.sanitize_for_logging(command)

        self.info(
            "Command executed",
            command=sanitized_command[:100] + "..." if len(sanitized_command) > 100 else sanitized_command,
            working_dir=working_dir,
            return_code=return_code,
            duration_seconds=duration
        )

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events."""
        self.warning(
            f"Security event: {event_type}",
            event_type=event_type,
            **details
        )


# Global logger instance
logger = StructuredLogger()
