"""Basic usage of the voraus_logging_lib library."""

import logging

from voraus_logging_lib.logging import LogLevel, configure_logger

_logger = logging.getLogger(__name__)


def main() -> None:
    """Main function."""
    configure_logger(log_level=LogLevel.DEBUG)
    _logger.info("This is an info message.")


if __name__ == "__main__":
    main()
