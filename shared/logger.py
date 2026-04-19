"""
shared/logger.py — Centralised structured logger (loguru)
"""
import os
import sys
from loguru import logger as _logger

_configured = False


def get_logger(name: str):
    """Return a logger bound with the service name."""
    global _configured
    if not _configured:
        level = os.environ.get("LOG_LEVEL", "INFO").upper()
        _logger.remove()
        # Console
        _logger.add(
            sys.stdout,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{extra[service]}</cyan> | "
                   "{message}",
            colorize=True,
        )
        # File
        _logger.add(
            f"/app/logs/{name}.log",
            level=level,
            rotation="00:00",
            retention="30 days",
            compression="gz",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[service]} | {message}",
        )
        _configured = True
    return _logger.bind(service=name)
