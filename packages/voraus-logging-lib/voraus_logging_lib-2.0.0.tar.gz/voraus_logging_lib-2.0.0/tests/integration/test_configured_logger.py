"""Contains an integration test for a configured logger."""

import re
from io import StringIO
from logging import getLogger

from rich.console import Console

from voraus_logging_lib.logging import LogLevel, configure_logger


def test_configured_logger() -> None:
    """Tests that the logger can be configured without errors."""
    console_log = StringIO()
    console_width = 80
    console = Console(file=console_log, width=console_width)
    configure_logger(log_level="DEBUG", rich_kwargs={"console": console})
    logger = getLogger()
    for level in LogLevel.__members__.values():
        log_method = getattr(logger, level.value.lower())
        log_method(f"This is a {level.value} message.")
    logged_output = console_log.getvalue().splitlines()

    # E.g. "[12/12/25 09:29:02] DEBUG    This is a DEBUG message."
    expected_log_pattern = (
        r"^(?P<date_time>\[(\d{2}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2})\])?\s+(?P<level>[A-Z]+)\s+(?P<message>[^\n]+)$"
    )
    for line in logged_output:
        assert len(line) == console_width
        match = re.match(expected_log_pattern, line)
        assert match is not None, f"Log line does not match expected pattern: {line}"
        log_level = match.group("level")
        log_message = match.group("message")
        assert log_level in LogLevel.__members__
        assert log_message.rstrip() == f"This is a {log_level} message."
