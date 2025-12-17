"""This module defines the logger configuration."""

import logging
from enum import Enum
from logging import Handler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any
from warnings import warn

from rich.logging import RichHandler

from voraus_logging_lib.constants import RICH_DEFAULT_KWARGS


class LogLevel(str, Enum):
    """Enum for log levels for typer."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    def __str__(self) -> str:
        """String representation of the log level.

        Returns:
            The log level as string.
        """
        return self.value


def file_handler_namer_fn(name: str) -> str:
    """The default file handler log rotation file name function.

    The names of `TimedRotatingFileHandler` do not have a `*.log` suffix but a `*.log.<TIMESTAMP>` suffix.

    Args:
        name: The input log file name.

    Returns:
        The patched log file name.
    """
    return name.replace(".log", "") + ".log"


def configure_logger(  # noqa: PLR0913
    *,
    log_level: int | str,
    log_format: str = "%(message)s",
    log_file_name: str | None = None,
    log_file_retention_days: int | None = None,
    log_file_directory: Path | None = None,
    log_file_format: str | None = None,
    rich_tracebacks: bool | None = None,
    rich_kwargs: dict[str, Any] | None = None,
) -> None:
    """Configures the logger according to `Python Coding Guides <https://yuandarobotics.atlassian.net/l/cp/0W7rLj5C>`_.

    Note: Logging to a file is optional but as soon as one of the log file related variables is given, all other
    variables must be set, too.

    Args:
        log_level: The log level as string or integer.
        log_format: The log format for the rich handler. Defaults to "%(message)s".
        log_file_name: The name of the log file. Defaults to None.
        log_file_retention_days: The number of old log files to keep before deleting the oldest ones. Defaults to None.
        log_file_directory: The directory to write the log file to. Defaults to None.
        log_file_format: The log file format. Defaults to None.
        rich_tracebacks: Whether to use `rich` tracebacks or not. Defaults to None. This argument is deprecated.
        rich_kwargs: See `rich.logging.RichHandler <https://rich.readthedocs.io/en/stable/reference/logging.html>`_.

    Raises:
        ValueError: As soon as the `log_file_directory` is given but one of
                    [`log_file_name`, `log_file_retention_days`, `log_file_format`] is None.
    """
    requested_rich_kwargs = rich_kwargs or {}
    effective_rich_kwargs = RICH_DEFAULT_KWARGS.copy()

    if rich_tracebacks is not None:
        warn(
            "The rich_tracebacks argument is deprecated, please use rich_kwargs instead!",
            DeprecationWarning,
            stacklevel=2,
        )
        requested_rich_kwargs["rich_tracebacks"] = rich_tracebacks

    effective_rich_kwargs.update(requested_rich_kwargs)

    rich_handler = RichHandler(**effective_rich_kwargs)

    rich_handler.setFormatter(logging.Formatter(log_format))

    handlers: list[Handler] = [rich_handler]

    if log_file_directory:
        if log_file_name is None:
            msg = "The log filename must not be None as soon as the log file directory is given"
            raise ValueError(msg)
        if log_file_retention_days is None:
            msg = "The log file retention days must not be None as soon as the log file directory is given"
            raise ValueError(msg)
        if log_file_format is None:
            msg = "The log file format must not be None as soon as the log file directory is given"
            raise ValueError(msg)

        log_file_path = log_file_directory / log_file_name

        log_file_directory.mkdir(parents=True, exist_ok=True)

        file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", backupCount=log_file_retention_days)
        file_handler.setFormatter(logging.Formatter(log_file_format))

        file_handler.namer = file_handler_namer_fn
        handlers.append(file_handler)

    # Get the root logger
    logger = logging.getLogger()

    # Remove and close all existing handlers from root logger
    for handler in logger.handlers:
        logger.removeHandler(handler)
        handler.close()

    logger.handlers = handlers
    logger.setLevel(log_level)
