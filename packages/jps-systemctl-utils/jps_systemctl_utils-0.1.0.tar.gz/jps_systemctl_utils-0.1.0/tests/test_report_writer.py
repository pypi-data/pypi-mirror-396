"""Tests for report_writer module."""

import getpass
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from jps_systemctl_utils.report_writer import write_header


@pytest.fixture
def temp_report_file(tmp_path):
    """Create a temporary report file path."""
    return tmp_path / "reports" / "test_report.txt"


@pytest.fixture
def mock_script_path(tmp_path):
    """Create a mock script path."""
    return tmp_path / "scripts" / "systemctl_runner.py"


@pytest.fixture
def mock_infile(tmp_path):
    """Create a mock input file path."""
    return tmp_path / "input" / "services.txt"


@pytest.fixture
def mock_logfile(tmp_path):
    """Create a mock logfile path."""
    return tmp_path / "logs" / "test.log"


def test_write_header_creates_directory(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that write_header creates the report directory if it doesn't exist."""
    assert not temp_report_file.parent.exists()
    
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    assert temp_report_file.parent.exists()


def test_write_header_creates_file(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that write_header creates the report file."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    assert temp_report_file.exists()


def test_write_header_contains_method_created(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that header contains method-created line."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert "## method-created:" in content
    assert str(mock_script_path) in content


def test_write_header_contains_date_created(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that header contains date-created line."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert "## date-created:" in content
    # Verify it has a timestamp format
    assert any(char.isdigit() for char in content)


def test_write_header_contains_created_by(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that header contains created-by line."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert "## created-by:" in content
    assert getpass.getuser() in content


def test_write_header_contains_logfile(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that header contains logfile line."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert "## logfile:" in content
    assert str(mock_logfile) in content


def test_write_header_contains_infile(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that header contains infile line."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert "## infile:" in content
    assert str(mock_infile) in content


def test_write_header_has_blank_line_at_end(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that header ends with a blank line."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert content.endswith("\n\n")


def test_write_header_overwrites_existing_file(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that write_header overwrites an existing file."""
    # Create file with existing content
    temp_report_file.parent.mkdir(parents=True, exist_ok=True)
    temp_report_file.write_text("Old content\n")
    
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert "Old content" not in content
    assert "## method-created:" in content


@patch('jps_systemctl_utils.report_writer.datetime')
def test_write_header_uses_current_datetime(mock_datetime, temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that write_header uses current datetime."""
    mock_now = MagicMock()
    mock_now.strftime.return_value = "2025-12-13 14:30:00"
    mock_datetime.now.return_value = mock_now
    
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    assert "2025-12-13 14:30:00" in content
    mock_datetime.now.assert_called_once()


def test_write_header_all_lines_present(temp_report_file, mock_script_path, mock_infile, mock_logfile):
    """Test that all expected header lines are present in order."""
    write_header(temp_report_file, mock_script_path, mock_infile, mock_logfile)
    
    content = temp_report_file.read_text()
    lines = content.strip().split('\n')
    
    # Should have 5 header lines
    assert len(lines) >= 5
    assert lines[0].startswith("## method-created:")
    assert lines[1].startswith("## date-created:")
    assert lines[2].startswith("## created-by:")
    assert lines[3].startswith("## logfile:")
    assert lines[4].startswith("## infile:")
