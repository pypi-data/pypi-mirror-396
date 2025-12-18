"""
Logging configuration for TokenVault SDK.

Provides structured logging with context enrichment for observability.
"""

import logging
import sys
from typing import Any, Dict, Optional


class ContextFilter(logging.Filter):
    """
    Logging filter that adds context fields to log records.
    
    This filter enriches log records with SDK-specific context like
    organization_id, user_id, profile_id, etc.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context fields to log record.
        
        Args:
            record: Log record to enrich
            
        Returns:
            True to allow the record to be logged
        """
        # Ensure extra dict exists
        if not hasattr(record, 'organization_id'):
            record.organization_id = None
        if not hasattr(record, 'user_id'):
            record.user_id = None
        if not hasattr(record, 'profile_id'):
            record.profile_id = None
        if not hasattr(record, 'balance'):
            record.balance = None
        if not hasattr(record, 'cached'):
            record.cached = None
        if not hasattr(record, 'latency_ms'):
            record.latency_ms = None
        
        return True


class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs structured log messages.
    
    Includes timestamp, level, logger name, message, and context fields.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured message.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log message
        """
        # Build base message
        parts = [
            f"[{self.formatTime(record, self.datefmt)}]",
            f"[{record.levelname}]",
            f"[{record.name}]",
            record.getMessage(),
        ]
        
        # Add context fields if present
        context_fields = []
        
        if hasattr(record, 'organization_id') and record.organization_id:
            context_fields.append(f"org_id={record.organization_id}")
        
        if hasattr(record, 'user_id') and record.user_id:
            context_fields.append(f"user_id={record.user_id}")
        
        if hasattr(record, 'profile_id') and record.profile_id:
            context_fields.append(f"profile_id={record.profile_id}")
        
        if hasattr(record, 'balance') and record.balance is not None:
            context_fields.append(f"balance={record.balance}")
        
        if hasattr(record, 'cached') and record.cached is not None:
            context_fields.append(f"cached={record.cached}")
        
        if hasattr(record, 'latency_ms') and record.latency_ms is not None:
            context_fields.append(f"latency_ms={record.latency_ms:.2f}")
        
        if hasattr(record, 'model') and record.model:
            context_fields.append(f"model={record.model}")
        
        if hasattr(record, 'total_tokens') and record.total_tokens is not None:
            context_fields.append(f"tokens={record.total_tokens}")
        
        if context_fields:
            parts.append(f"[{', '.join(context_fields)}]")
        
        # Add exception info if present
        if record.exc_info:
            parts.append("\n" + self.formatException(record.exc_info))
        
        return " ".join(parts)


def configure_logging(
    level: str = "INFO",
    format_style: str = "structured",
    stream: Any = None,
) -> None:
    """
    Configure logging for TokenVault SDK.
    
    Sets up structured logging with appropriate handlers and formatters.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_style: Format style ("structured" or "simple")
        stream: Output stream (default: sys.stdout)
    """
    if stream is None:
        stream = sys.stdout
    
    # Get SDK logger
    logger = logging.getLogger("tokenvault_sdk")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(stream)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Set formatter
    if format_style == "structured":
        formatter = StructuredFormatter(
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    handler.setFormatter(formatter)
    
    # Add context filter
    handler.addFilter(ContextFilter())
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the SDK.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"tokenvault_sdk.{name}")
