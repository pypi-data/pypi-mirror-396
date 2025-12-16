"""Logging utilities for PromptSentry."""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.logging import RichHandler


# Default log level
DEFAULT_LOG_LEVEL = logging.INFO

# Log format for file logging
FILE_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(
    name: str = .promptsentry",
    level: int = DEFAULT_LOG_LEVEL,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Get a configured logger for PromptSentry.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path for file logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(level)
        
        # Rich console handler for pretty output
        console_handler = RichHandler(
            show_time=False,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
            logger.addHandler(file_handler)
    
    return logger


def set_log_level(level: int) -> None:
    """
    Set the log level for all PromptSentry loggers.
    
    Args:
        level: New logging level
    """
    logger = logging.getLogger(.promptsentry")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def enable_debug() -> None:
    """Enable debug logging."""
    set_log_level(logging.DEBUG)


def enable_quiet() -> None:
    """Enable quiet mode (only errors)."""
    set_log_level(logging.ERROR)
