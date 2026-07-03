"""Centralized logging configuration for DataPulse."""

import logging
from pathlib import Path
import sys


LOG_FORMAT = "%(levelname)s %(message)s"
LOG_DIRECTORY = Path("logs")
LOG_FILE = LOG_DIRECTORY / "datapulse.log"


def get_logger(name: str) -> logging.Logger:
    """
    Create or return a configured logger.

    Args:
        name: Name of the logger, usually ``__name__``.

    Returns:
        logging.Logger: Logger configured for console and file output.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    LOG_DIRECTORY.mkdir(exist_ok=True)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
