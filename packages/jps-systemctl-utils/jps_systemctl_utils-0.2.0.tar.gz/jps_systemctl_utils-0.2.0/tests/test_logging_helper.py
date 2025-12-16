"""Tests for logging_helper module."""

import logging
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from jps_systemctl_utils.logging_helper import setup_logging
from jps_systemctl_utils.constants import LOGGING_FORMAT


@pytest.fixture
def temp_logfile(tmp_path):
    """Create a temporary log file path."""
    return tmp_path / "test.log"


def test_setup_logging_creates_logfile_directory(temp_logfile):
    """Test that setup_logging creates the logfile directory if it doesn't exist."""
    setup_logging(temp_logfile)
    
    assert temp_logfile.parent.exists()


def test_setup_logging_creates_file_handler(temp_logfile):
    """Test that setup_logging creates a file handler."""
    # Clear any existing handlers
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    # Check that handlers were added
    assert len(logger.handlers) == 2
    
    # Check for FileHandler
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
    
    # Clean up
    logger.handlers.clear()


def test_setup_logging_creates_stderr_handler(temp_logfile):
    """Test that setup_logging creates a stderr handler."""
    # Clear any existing handlers
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    # Check for StreamHandler (excluding FileHandler which is also a StreamHandler subclass)
    stream_handlers = [h for h in logger.handlers 
                      if isinstance(h, logging.StreamHandler) 
                      and not isinstance(h, logging.FileHandler)]
    assert len(stream_handlers) == 1
    assert stream_handlers[0].stream == sys.stderr
    
    # Clean up
    logger.handlers.clear()


def test_setup_logging_sets_correct_log_level(temp_logfile):
    """Test that setup_logging sets INFO level for root logger."""
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    assert logger.level == logging.INFO
    
    # Clean up
    logger.handlers.clear()


def test_setup_logging_file_handler_level(temp_logfile):
    """Test that file handler has INFO level."""
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    assert file_handlers[0].level == logging.INFO
    
    # Clean up
    logger.handlers.clear()


def test_setup_logging_stderr_handler_level(temp_logfile):
    """Test that stderr handler has WARNING level."""
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    stream_handlers = [h for h in logger.handlers 
                      if isinstance(h, logging.StreamHandler) 
                      and not isinstance(h, logging.FileHandler)]
    assert stream_handlers[0].level == logging.WARNING
    
    # Clean up
    logger.handlers.clear()


def test_setup_logging_file_handler_formatter(temp_logfile):
    """Test that file handler uses correct format."""
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    formatter = file_handlers[0].formatter
    assert formatter._fmt == LOGGING_FORMAT
    
    # Clean up
    logger.handlers.clear()


def test_setup_logging_stderr_handler_formatter(temp_logfile):
    """Test that stderr handler uses simplified format."""
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    stream_handlers = [h for h in logger.handlers 
                      if isinstance(h, logging.StreamHandler) 
                      and not isinstance(h, logging.FileHandler)]
    formatter = stream_handlers[0].formatter
    assert formatter._fmt == "%(levelname)s: %(message)s"
    
    # Clean up
    logger.handlers.clear()


def test_setup_logging_writes_to_file(temp_logfile):
    """Test that logging actually writes to the file."""
    logger = logging.getLogger()
    logger.handlers.clear()
    
    setup_logging(temp_logfile)
    
    test_message = "Test log message"
    logger.info(test_message)
    
    # Flush and close handlers
    for handler in logger.handlers:
        handler.flush()
        handler.close()
    
    # Check file content
    assert temp_logfile.exists()
    content = temp_logfile.read_text()
    assert test_message in content
    
    # Clean up
    logger.handlers.clear()
