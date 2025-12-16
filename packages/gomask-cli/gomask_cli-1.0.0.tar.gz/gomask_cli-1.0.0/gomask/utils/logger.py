"""
Logging configuration for GoMask CLI
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.logging import RichHandler


# Create logger instance
logger = logging.getLogger("gomask")


def setup_logging(debug: bool = False, log_file: Optional[Path] = None) -> None:
    """
    Setup logging configuration for the CLI

    Args:
        debug: Enable debug level logging
        log_file: Optional log file path
    """
    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO

    # Clear existing handlers
    logger.handlers.clear()

    # Configure root logger
    logger.setLevel(log_level)

    # Add rich console handler
    console_handler = RichHandler(
        show_time=debug,
        show_path=debug,
        markup=True,
        rich_tracebacks=True
    )
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    if debug:
        logger.debug("Debug logging enabled")