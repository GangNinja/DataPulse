"""Centralized logging configuration for DataPulse."""

import logging
import sys


LOG_FORMAT = "%(levelname)s %(message)s"


def get_logger(name: str) -> logging.Logger:
    """
    Create or return a configured logger.

    Args:
        name: Name of the logger, usually ``__name__``.

    Returns:
        logging.Logger: Logger configured for console output.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger
