"""Contains all application utility functions."""

import pytest

from voraus_logging_lib import get_app_name, get_app_version


def test_get_app_name() -> None:
    assert get_app_name() == "voraus-logging-lib"


def test_get_app_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("voraus_logging_lib.__version__", "42.0.0")
    assert get_app_version() == "42.0.0"
