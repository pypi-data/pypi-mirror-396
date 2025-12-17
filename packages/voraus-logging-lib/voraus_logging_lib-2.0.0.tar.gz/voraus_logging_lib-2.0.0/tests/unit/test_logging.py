"""Contains all unit tests for the `logging` module."""

import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voraus_logging_lib.constants import RICH_DEFAULT_KWARGS
from voraus_logging_lib.logging import LogLevel, configure_logger, file_handler_namer_fn


@pytest.mark.parametrize(
    ("input_name", "expected_output_name"), [("name.log", "name.log"), ("name.log.foo", "name.foo.log")]
)
def test_file_handler_namer_fn(input_name: str, expected_output_name: str) -> None:
    assert expected_output_name == file_handler_namer_fn(input_name)


@pytest.mark.parametrize(
    ("missing_field", "expected_error_message"),
    [
        ("log_file_name", "The log filename must not be None as soon as the log file directory is given"),
        (
            "log_file_retention_days",
            "The log file retention days must not be None as soon as the log file directory is given",
        ),
        ("log_file_format", "The log file format must not be None as soon as the log file directory is given"),
    ],
)
def test_configure_logger_all_or_nothing_items(missing_field: str, expected_error_message: str, tmp_path: Path) -> None:
    data = {
        "log_file_name": "voraus-component",
        "log_file_retention_days": 1,
        "log_file_directory": tmp_path,
        "log_file_format": "%(message)s",
    }
    del data[missing_field]

    with pytest.raises(ValueError, match=expected_error_message):
        configure_logger(log_level="INFO", **data)  # type: ignore[arg-type]


@patch("voraus_logging_lib.logging.logging")
@patch("voraus_logging_lib.logging.RichHandler")
def test_configure_logger_without_file_log(rich_handler_class_mock: MagicMock, logging_module_mock: MagicMock) -> None:
    rich_handler_mock = MagicMock()
    root_logger_mock = MagicMock()
    logging_module_mock.getLogger.return_value = root_logger_mock
    rich_handler_class_mock.return_value = rich_handler_mock

    configure_logger(log_level="INFO")
    rich_handler_class_mock.assert_called_once_with(**RICH_DEFAULT_KWARGS)
    rich_handler_mock.setFormatter.assert_called_once_with(logging_module_mock.Formatter("%(message)s"))

    assert [rich_handler_mock] == root_logger_mock.handlers
    root_logger_mock.setLevel.assert_called_once_with("INFO")


@patch("voraus_logging_lib.logging.TimedRotatingFileHandler")
@patch("voraus_logging_lib.logging.logging")
@patch("voraus_logging_lib.logging.RichHandler")
def test_configure_logger_with_file_log(
    rich_handler_class_mock: MagicMock,
    logging_module_mock: MagicMock,
    timed_rotating_file_handler_class_mock: MagicMock,
    tmp_path: Path,
) -> None:
    rich_handler_mock = MagicMock()
    file_handler_mock = MagicMock()
    root_logger_mock = MagicMock()
    logging_module_mock.getLogger.return_value = root_logger_mock
    rich_handler_class_mock.return_value = rich_handler_mock
    timed_rotating_file_handler_class_mock.return_value = file_handler_mock
    configure_logger(
        log_level="INFO",
        log_file_name="dummy",
        log_file_directory=tmp_path,
        log_file_format="%(message)s",
        log_file_retention_days=42,
    )
    rich_handler_class_mock.assert_called_once_with(**RICH_DEFAULT_KWARGS)
    rich_handler_mock.setFormatter.assert_called_once_with(logging_module_mock.Formatter("%(message)s"))

    timed_rotating_file_handler_class_mock.assert_called_once_with(tmp_path / "dummy", when="midnight", backupCount=42)
    file_handler_mock.setFormatter.assert_called_once_with(logging_module_mock.Formatter("%(message)s"))

    assert file_handler_namer_fn == file_handler_mock.namer  # pylint: disable=comparison-with-callable

    assert [rich_handler_mock, file_handler_mock] == root_logger_mock.handlers
    root_logger_mock.setLevel.assert_called_once_with("INFO")


def test_log_level_to_str() -> None:
    assert str(LogLevel.DEBUG) == "DEBUG"


@patch("voraus_logging_lib.logging.RichHandler")
def test_configure_logger_rich_kwargs(rich_handler_class_mock: MagicMock) -> None:
    rich_handler_kwargs = {"show_time": True}
    configure_logger(log_level="INFO", rich_kwargs=rich_handler_kwargs)

    rich_handler_class_mock.assert_called_once_with(**RICH_DEFAULT_KWARGS, show_time=True)


@patch("voraus_logging_lib.logging.RichHandler")
def test_configure_logger_rich_kwargs_with_rich_traceback(rich_handler_class_mock: MagicMock) -> None:
    rich_handler_kwargs = {
        "show_time": True,
        "rich_tracebacks": False,
    }
    configure_logger(log_level="INFO", rich_kwargs=rich_handler_kwargs)

    rich_handler_class_mock.assert_called_once_with(rich_tracebacks=False, show_path=False, show_time=True)


@patch("voraus_logging_lib.logging.RichHandler")
def test_configure_logger_without_deprecated_call(rich_handler_class_mock: MagicMock) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        configure_logger(log_level="INFO")

    rich_handler_class_mock.assert_called_once_with(**RICH_DEFAULT_KWARGS)


@patch("voraus_logging_lib.logging.RichHandler")
def test_configure_logger_with_deprecated_rich_tracebacks_false(rich_handler_class_mock: MagicMock) -> None:
    with pytest.deprecated_call():
        configure_logger(log_level="INFO", rich_tracebacks=False)
        rich_handler_class_mock.assert_called_once_with(rich_tracebacks=False, show_path=False)


@patch("voraus_logging_lib.logging.RichHandler")
def test_configure_logger_with_deprecated_rich_tracebacks_true(rich_handler_class_mock: MagicMock) -> None:
    with pytest.deprecated_call():
        configure_logger(log_level="INFO", rich_tracebacks=True)
        rich_handler_class_mock.assert_called_once_with(rich_tracebacks=True, show_path=False)
