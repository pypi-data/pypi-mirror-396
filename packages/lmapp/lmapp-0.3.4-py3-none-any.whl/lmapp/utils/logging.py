#!/usr/bin/env python3
"""
Logging Configuration
Unified logging system using loguru for all lmapp components
"""

import sys
import os
from pathlib import Path
from loguru import logger as _logger

# Remove default handler
_logger.remove()

# Determine log level
DEBUG_MODE = os.getenv("LMAPP_DEBUG", "0") == "1"
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"

# Create logs directory
LOG_DIR = Path.home() / ".local" / "share" / "lmapp" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "lmapp.log"

# Configure format
FORMAT = (
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Console handler ID
_console_handler_id = None

# Add console handler (INFO and above, or DEBUG if enabled)
_console_handler_id = _logger.add(
    sys.stderr,
    format=FORMAT,
    level=LOG_LEVEL,
    colorize=True,
)

# Add file handler (DEBUG always, to file)
_logger.add(
    str(LOG_FILE),
    format=FORMAT,
    level="DEBUG",
    rotation="10 MB",  # Rotate when file reaches 10MB
    retention="7 days",  # Keep 7 days of logs
)

# Export configured logger
logger = _logger


def enable_debug():
    """Enable debug mode by lowering console log level to DEBUG"""
    global _console_handler_id
    try:
        logger.remove(_console_handler_id)
        _console_handler_id = logger.add(
            sys.stderr,
            format=FORMAT,
            level="DEBUG",
            colorize=True,
        )
        logger.debug("Debug mode enabled")
    except Exception as e:
        logger.error(f"Failed to enable debug: {e}")


def disable_debug():
    """Disable debug mode by raising console log level to INFO"""
    global _console_handler_id
    try:
        logger.remove(_console_handler_id)
        _console_handler_id = logger.add(
            sys.stderr,
            format=FORMAT,
            level="INFO",
            colorize=True,
        )
        logger.debug("Debug mode disabled")
    except Exception as e:
        logger.error(f"Failed to disable debug: {e}")


# Log startup
if DEBUG_MODE:
    logger.debug("Debug mode enabled via LMAPP_DEBUG environment variable")
    logger.debug(f"Log file: {LOG_FILE}")
