"""Tests for systemctl_runner module."""

import getpass
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest
from typer.testing import CliRunner

from jps_systemctl_utils.systemctl_runner import app, build_default_paths


runner = CliRunner()


@pytest.fixture
def temp_infile(tmp_path):
    """Create a temporary input file with service names."""
    infile = tmp_path / "services.txt"
    infile.write_text("nginx\napache2\nmysql\n")
    return infile


@pytest.fixture
def temp_infile_with_comments(tmp_path):
    """Create a temporary input file with comments and blank lines."""
    infile = tmp_path / "services_with_comments.txt"
    infile.write_text("# This is a comment\nnginx\n\napache2\n# Another comment\nmysql\n\n")
    return infile


@pytest.fixture
def temp_outdir(tmp_path):
    """Create a temporary output directory."""
    return tmp_path / "output"


# ============================================================
# Tests for build_default_paths
# ============================================================

def test_build_default_paths_creates_timestamped_directory():
    """Test that build_default_paths creates a timestamped directory."""
    script_path = Path("/usr/local/bin/systemctl_runner.py")
    user = "testuser"
    
    outdir, report, logfile = build_default_paths(script_path, user)
    
    assert "/tmp/testuser/systemctl_runner/" in str(outdir)
    # Check that timestamp is in the path (format: YYYY-MM-DD-HHMMSS)
    assert len(outdir.parts[-1]) == 17  # YYYY-MM-DD-HHMMSS length


def test_build_default_paths_uses_script_stem():
    """Test that build_default_paths uses script stem in paths."""
    script_path = Path("/usr/local/bin/my_script.py")
    user = "testuser"
    
    outdir, report, logfile = build_default_paths(script_path, user)
    
    assert "my_script" in str(outdir)
    assert "my_script_report.txt" == report.name
    assert "my_script.log" == logfile.name


def test_build_default_paths_uses_username():
    """Test that build_default_paths uses username in path."""
    script_path = Path("/usr/local/bin/test.py")
    user = "myuser"
    
    outdir, report, logfile = build_default_paths(script_path, user)
    
    assert "/tmp/myuser/" in str(outdir)


def test_build_default_paths_report_in_outdir():
    """Test that report file is in the output directory."""
    script_path = Path("/usr/local/bin/test.py")
    user = "testuser"
    
    outdir, report, logfile = build_default_paths(script_path, user)
    
    assert report.parent == outdir


def test_build_default_paths_logfile_in_outdir():
    """Test that logfile is in the output directory."""
    script_path = Path("/usr/local/bin/test.py")
    user = "testuser"
    
    outdir, report, logfile = build_default_paths(script_path, user)
    
    assert logfile.parent == outdir


@patch('jps_systemctl_utils.systemctl_runner.datetime')
def test_build_default_paths_timestamp_format(mock_datetime):
    """Test that build_default_paths uses correct timestamp format."""
    mock_now = MagicMock()
    mock_now.strftime.return_value = "2025-12-13-143000"
    mock_datetime.now.return_value = mock_now
    
    script_path = Path("/usr/local/bin/test.py")
    user = "testuser"
    
    outdir, report, logfile = build_default_paths(script_path, user)
    
    assert "2025-12-13-143000" in str(outdir)
    mock_now.strftime.assert_called_once_with("%Y-%m-%d-%H%M%S")


# ============================================================
# Tests for main CLI function
# ============================================================

@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_requires_infile(mock_setup, mock_write, mock_process):
    """Test that main requires --infile parameter."""
    result = runner.invoke(app, [])
    
    assert result.exit_code != 0
    # Typer outputs error messages to stdout or stderr via the result output
    output = result.stdout + result.stderr
    assert "Missing option" in output or "required" in output.lower() or result.exit_code == 2


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_with_infile_only(mock_setup, mock_write, mock_process, temp_infile):
    """Test main with only infile parameter (uses defaults)."""
    result = runner.invoke(app, ["--infile", str(temp_infile)])
    
    assert result.exit_code == 0
    mock_setup.assert_called_once()
    mock_write.assert_called_once()
    mock_process.assert_called_once()


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_with_custom_outdir(mock_setup, mock_write, mock_process, temp_infile, temp_outdir):
    """Test main with custom output directory."""
    result = runner.invoke(app, ["--infile", str(temp_infile), "--outdir", str(temp_outdir)])
    
    assert result.exit_code == 0
    assert temp_outdir.exists()


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_with_custom_report_file(mock_setup, mock_write, mock_process, temp_infile, tmp_path):
    """Test main with custom report file."""
    custom_report = tmp_path / "my_report.txt"
    
    result = runner.invoke(app, [
        "--infile", str(temp_infile),
        "--report-file", str(custom_report)
    ])
    
    assert result.exit_code == 0
    # Check that write_header was called with custom report path
    call_args = mock_write.call_args[0]
    assert call_args[0] == custom_report


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_with_custom_logfile(mock_setup, mock_write, mock_process, temp_infile, tmp_path):
    """Test main with custom logfile."""
    custom_log = tmp_path / "my_log.log"
    
    result = runner.invoke(app, [
        "--infile", str(temp_infile),
        "--logfile", str(custom_log)
    ])
    
    assert result.exit_code == 0
    # Check that setup_logging was called with custom logfile
    mock_setup.assert_called_once_with(custom_log)


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_with_dryrun_flag(mock_setup, mock_write, mock_process, temp_infile):
    """Test main with dryrun flag."""
    result = runner.invoke(app, ["--infile", str(temp_infile), "--dryrun"])
    
    assert result.exit_code == 0
    # Check that process_services was called with dryrun=True
    call_kwargs = mock_process.call_args[1]
    assert call_kwargs['dryrun'] is True


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_without_dryrun_flag(mock_setup, mock_write, mock_process, temp_infile):
    """Test main without dryrun flag (default is False)."""
    result = runner.invoke(app, ["--infile", str(temp_infile)])
    
    assert result.exit_code == 0
    # Check that process_services was called with dryrun=False
    call_kwargs = mock_process.call_args[1]
    assert call_kwargs['dryrun'] is False


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_reads_services_from_infile(mock_setup, mock_write, mock_process, temp_infile):
    """Test that main reads services from infile."""
    result = runner.invoke(app, ["--infile", str(temp_infile)])
    
    assert result.exit_code == 0
    # Check that process_services was called with correct service list
    call_args = mock_process.call_args[0]
    services = call_args[0]
    assert "nginx" in services
    assert "apache2" in services
    assert "mysql" in services


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_skips_comments_and_blank_lines(mock_setup, mock_write, mock_process, temp_infile_with_comments):
    """Test that main skips comments and blank lines."""
    result = runner.invoke(app, ["--infile", str(temp_infile_with_comments)])
    
    assert result.exit_code == 0
    # Check that process_services was called with only valid services
    call_args = mock_process.call_args[0]
    services = call_args[0]
    assert len(services) == 3
    assert "nginx" in services
    assert "apache2" in services
    assert "mysql" in services
    # No comments should be in the list
    assert not any(s.startswith("#") for s in services)


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_handles_nonexistent_infile(mock_setup, mock_write, mock_process, tmp_path):
    """Test that main handles nonexistent input file gracefully."""
    nonexistent = tmp_path / "nonexistent.txt"
    
    result = runner.invoke(app, ["--infile", str(nonexistent)])
    
    assert result.exit_code == 1


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_calls_setup_logging(mock_setup, mock_write, mock_process, temp_infile):
    """Test that main calls setup_logging."""
    result = runner.invoke(app, ["--infile", str(temp_infile)])
    
    assert result.exit_code == 0
    mock_setup.assert_called_once()


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_calls_write_header(mock_setup, mock_write, mock_process, temp_infile):
    """Test that main calls write_header."""
    result = runner.invoke(app, ["--infile", str(temp_infile)])
    
    assert result.exit_code == 0
    mock_write.assert_called_once()


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_calls_process_services(mock_setup, mock_write, mock_process, temp_infile):
    """Test that main calls process_services."""
    result = runner.invoke(app, ["--infile", str(temp_infile)])
    
    assert result.exit_code == 0
    mock_process.assert_called_once()


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_with_outdir_creates_report_in_outdir(mock_setup, mock_write, mock_process, temp_infile, temp_outdir):
    """Test that when outdir is specified, report file is created inside it."""
    result = runner.invoke(app, ["--infile", str(temp_infile), "--outdir", str(temp_outdir)])
    
    assert result.exit_code == 0
    # Check write_header was called with report inside outdir
    call_args = mock_write.call_args[0]
    report_path = call_args[0]
    assert report_path.parent == temp_outdir


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_with_outdir_creates_logfile_in_outdir(mock_setup, mock_write, mock_process, temp_infile, temp_outdir):
    """Test that when outdir is specified, logfile is created inside it."""
    result = runner.invoke(app, ["--infile", str(temp_infile), "--outdir", str(temp_outdir)])
    
    assert result.exit_code == 0
    # Check setup_logging was called with logfile inside outdir
    logfile_path = mock_setup.call_args[0][0]
    assert logfile_path.parent == temp_outdir


@patch('jps_systemctl_utils.systemctl_runner.process_services')
@patch('jps_systemctl_utils.systemctl_runner.write_header')
@patch('jps_systemctl_utils.systemctl_runner.setup_logging')
def test_main_preserves_explicit_report_file_with_outdir(mock_setup, mock_write, mock_process, temp_infile, temp_outdir, tmp_path):
    """Test that explicit report-file is preserved even when outdir is set."""
    custom_report = tmp_path / "custom_location" / "my_report.txt"
    
    result = runner.invoke(app, [
        "--infile", str(temp_infile),
        "--outdir", str(temp_outdir),
        "--report-file", str(custom_report)
    ])
    
    # When both outdir and report-file are specified, outdir is created but report-file path is used
    assert result.exit_code == 0
    call_args = mock_write.call_args[0]
    # The report file should NOT be in outdir, but in the custom location
    assert call_args[0] == custom_report


@patch('jps_systemctl_utils.systemctl_runner.getpass.getuser')
def test_main_uses_current_user(mock_getuser, temp_infile):
    """Test that main uses current user for default paths."""
    mock_getuser.return_value = "testuser"
    
    with patch('jps_systemctl_utils.systemctl_runner.setup_logging'), \
         patch('jps_systemctl_utils.systemctl_runner.write_header'), \
         patch('jps_systemctl_utils.systemctl_runner.process_services'):
        
        result = runner.invoke(app, ["--infile", str(temp_infile)])
        
        assert result.exit_code == 0
        mock_getuser.assert_called()
