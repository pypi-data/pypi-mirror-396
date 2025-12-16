"""Logging utilities for Hayagriva."""
import logging
from typing import Optional


LOGGER_NAME = "hayagriva"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger.

    Parameters
    ----------
    name: Optional[str]
        Name for the logger. Defaults to the package-wide name.
    """

    logger = logging.getLogger(name or LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
