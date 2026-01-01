"""Logging configuration."""

import sys
import os
from pathlib import Path
from loguru import logger
from collection_helper.config import get_settings


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()

    # Remove default handler
    logger.remove()

    # Add console handler with formatted output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    # Add file handler for persistent logs (only if logs directory is writable)
    logs_dir = Path("logs")
    try:
        logs_dir.mkdir(exist_ok=True)
        logger.add(
            logs_dir / "collection_helper.log",
            rotation="10 MB",
            retention="7 days",
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
    except (PermissionError, OSError) as e:
        # If we can't write to logs directory, just skip file logging
        logger.warning(f"Could not set up file logging: {e}")
        logger.info("File logging disabled - using console output only")


def get_logger():
    """Get the configured logger instance."""
    return logger
