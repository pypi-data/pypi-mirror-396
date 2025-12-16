"""Tests for constants module."""

import pytest
from jps_systemctl_utils.constants import LOGGING_FORMAT


def test_logging_format_exists():
    """Test that LOGGING_FORMAT constant is defined."""
    assert LOGGING_FORMAT is not None
    assert isinstance(LOGGING_FORMAT, str)


def test_logging_format_contains_expected_fields():
    """Test that LOGGING_FORMAT contains standard logging fields."""
    expected_fields = [
        "%(levelname)s",
        "%(asctime)s",
        "%(pathname)s",
        "%(lineno)d",
        "%(message)s",
    ]
    
    for field in expected_fields:
        assert field in LOGGING_FORMAT, f"Expected field {field} not found in LOGGING_FORMAT"


def test_logging_format_structure():
    """Test that LOGGING_FORMAT has correct structure."""
    assert " : " in LOGGING_FORMAT
    assert LOGGING_FORMAT.count(":") >= 4  # At least 4 separators
