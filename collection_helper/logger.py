"""Logging configuration."""

import sys
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

    # Add file handler for persistent logs
    logger.add(
        "logs/collection_helper.log",
        rotation="10 MB",
        retention="7 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )


def get_logger():
    """Get the configured logger instance."""
    return logger
