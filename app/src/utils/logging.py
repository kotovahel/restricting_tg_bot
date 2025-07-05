"""Configuring logging."""

import logging
import logging.handlers

from datetime import datetime, UTC
from pathlib import Path

from .constants import DATETIME_FMT, UPDATE_TIME, UPDATE_INTERVAL, LOG_FMT, LOG_LEVEL


def logger_init(log_dir=None):

    # Get logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # File handler
    if log_dir:
        if isinstance(log_dir, str):
            log_dir = Path(log_dir).resolve()
        log_dir.mkdir(parents=True, exist_ok=True)

        log_filename = datetime.now(UTC).strftime(DATETIME_FMT) + '.log'
        file = logging.handlers.TimedRotatingFileHandler(
            log_dir.joinpath(log_filename),
            when=UPDATE_TIME,
            interval=UPDATE_INTERVAL
        )
        file_format = logging.Formatter(LOG_FMT)
        file.setLevel(LOG_LEVEL)
        file.setFormatter(file_format)

        # Adding all handlers to the logs
        logger.addHandler(file)

    # Stream handler
    stream = logging.StreamHandler()
    stream_format = logging.Formatter(LOG_FMT)
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(stream_format)

    # Adding all handlers to the logs
    logger.addHandler(stream)
