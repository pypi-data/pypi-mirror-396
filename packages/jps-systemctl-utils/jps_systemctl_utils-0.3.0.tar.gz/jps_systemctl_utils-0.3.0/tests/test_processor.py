"""Tests for processor module."""

import logging
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

from jps_systemctl_utils.processor import process_services, append_file, run_cmd, run_shell_cmd, check_safety


@pytest.fixture
def temp_report_file(tmp_path):
    """Create a temporary report file path."""
    return tmp_path / "reports" / "test_report.txt"


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return MagicMock(spec=logging.Logger)


# ============================================================
# Tests for append_file
# ============================================================

def test_append_file_creates_directory(temp_report_file):
    """Test that append_file creates parent directory if it doesn't exist."""
    assert not temp_report_file.parent.exists()
    
    append_file(temp_report_file, "Test content")
    
    assert temp_report_file.parent.exists()


def test_append_file_creates_file(temp_report_file):
    """Test that append_file creates the file."""
    append_file(temp_report_file, "Test content")
    
    assert temp_report_file.exists()


def test_append_file_writes_content(temp_report_file):
    """Test that append_file writes the content."""
    content = "Test content"
    append_file(temp_report_file, content)
    
    assert temp_report_file.read_text() == content + "\n"


def test_append_file_adds_newline_if_missing(temp_report_file):
    """Test that append_file adds newline if text doesn't end with one."""
    append_file(temp_report_file, "Line 1")
    
    content = temp_report_file.read_text()
    assert content.endswith("\n")


def test_append_file_preserves_existing_newline(temp_report_file):
    """Test that append_file doesn't add extra newline if text already ends with one."""
    append_file(temp_report_file, "Line 1\n")
    
    content = temp_report_file.read_text()
    assert content == "Line 1\n"
    assert not content.endswith("\n\n")


def test_append_file_appends_to_existing_content(temp_report_file):
    """Test that append_file appends to existing content."""
    temp_report_file.parent.mkdir(parents=True, exist_ok=True)
    temp_report_file.write_text("Line 1\n")
    
    append_file(temp_report_file, "Line 2")
    
    content = temp_report_file.read_text()
    assert content == "Line 1\nLine 2\n"


def test_append_file_handles_multiline_text(temp_report_file):
    """Test that append_file handles multiline text."""
    multiline = "Line 1\nLine 2\nLine 3"
    append_file(temp_report_file, multiline)
    
    content = temp_report_file.read_text()
    assert content == multiline + "\n"


# ============================================================
# Tests for run_cmd
# ============================================================

def test_run_cmd_dryrun_mode():
    """Test that run_cmd doesn't execute command in dryrun mode."""
    cmd = ["systemctl", "status", "nginx"]
    
    rc, out, err = run_cmd(cmd, dryrun=True)
    
    assert rc == 0
    assert "DRYRUN" in out
    assert "systemctl status nginx" in out
    assert "not executed" in out
    assert err == ""


def test_run_cmd_dryrun_returns_zero_exit_code():
    """Test that dryrun always returns exit code 0."""
    cmd = ["false"]  # Command that would normally fail
    
    rc, out, err = run_cmd(cmd, dryrun=True)
    
    assert rc == 0


@patch('jps_systemctl_utils.processor.subprocess.run')
def test_run_cmd_executes_command(mock_run):
    """Test that run_cmd executes the command."""
    cmd = ["echo", "test"]
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "test output\n"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc
    
    rc, out, err = run_cmd(cmd, dryrun=False)
    
    mock_run.assert_called_once_with(cmd, text=True, capture_output=True)
    assert rc == 0
    assert out == "test output\n"
    assert err == ""


@patch('jps_systemctl_utils.processor.subprocess.run')
def test_run_cmd_captures_stdout(mock_run):
    """Test that run_cmd captures stdout."""
    cmd = ["echo", "Hello"]
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "Hello\n"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc
    
    rc, out, err = run_cmd(cmd, dryrun=False)
    
    assert out == "Hello\n"


@patch('jps_systemctl_utils.processor.subprocess.run')
def test_run_cmd_captures_stderr(mock_run):
    """Test that run_cmd captures stderr."""
    cmd = ["ls", "/nonexistent"]
    mock_proc = MagicMock()
    mock_proc.returncode = 2
    mock_proc.stdout = ""
    mock_proc.stderr = "ls: cannot access '/nonexistent': No such file or directory\n"
    mock_run.return_value = mock_proc
    
    rc, out, err = run_cmd(cmd, dryrun=False)
    
    assert rc == 2
    assert err == "ls: cannot access '/nonexistent': No such file or directory\n"


@patch('jps_systemctl_utils.processor.subprocess.run')
def test_run_cmd_returns_nonzero_exit_code(mock_run):
    """Test that run_cmd returns non-zero exit code on failure."""
    cmd = ["false"]
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = ""
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc
    
    rc, out, err = run_cmd(cmd, dryrun=False)
    
    assert rc == 1


@patch('jps_systemctl_utils.processor.subprocess.run')
def test_run_cmd_with_arguments(mock_run):
    """Test that run_cmd passes all arguments correctly."""
    cmd = ["systemctl", "status", "nginx"]
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "active"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc
    
    run_cmd(cmd, dryrun=False)
    
    mock_run.assert_called_once_with(cmd, text=True, capture_output=True)


# ============================================================
# Tests for run_shell_cmd
# ============================================================

@patch('jps_systemctl_utils.processor.subprocess.run')
def test_run_shell_cmd_executes_with_shell(mock_run):
    """Test that run_shell_cmd executes command with shell=True."""
    cmd_str = "echo test | grep test"
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "test\n"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc
    
    rc, out, err = run_shell_cmd(cmd_str, dryrun=False)
    
    mock_run.assert_called_once_with(cmd_str, shell=True, text=True, capture_output=True)
    assert rc == 0
    assert out == "test\n"


def test_run_shell_cmd_dryrun():
    """Test that run_shell_cmd doesn't execute in dryrun mode."""
    cmd_str = "echo test | grep test"
    
    rc, out, err = run_shell_cmd(cmd_str, dryrun=True)
    
    assert rc == 0
    assert "DRYRUN" in out
    assert cmd_str in out


# ============================================================
# Tests for process_services
# ============================================================

@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
@patch('jps_systemctl_utils.processor.logger')
def test_process_services_processes_all_services(mock_logger, mock_append, mock_run, temp_report_file):
    """Test that process_services processes all services in the dict."""
    services = {"nginx": [], "apache2": [], "mysql": []}
    mock_run.return_value = (0, "output", "")
    
    process_services(services, temp_report_file, dryrun=False)
    
    # Each service gets 1 service header + 4 commands
    # logger.info should be called once per service
    assert mock_logger.info.call_count == 3


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_runs_four_commands_per_service(mock_append, mock_run, temp_report_file):
    """Test that process_services runs 4 systemctl commands per service."""
    services = {"nginx": []}
    mock_run.return_value = (0, "output", "")
    
    process_services(services, temp_report_file, dryrun=False)
    
    # 4 systemctl commands per service
    assert mock_run.call_count == 4


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_correct_command_sequence(mock_append, mock_run, temp_report_file):
    """Test that process_services runs commands in correct order."""
    services = {"nginx": []}
    mock_run.return_value = (0, "output", "")
    
    process_services(services, temp_report_file, dryrun=False)
    
    # Verify command sequence
    expected_calls = [
        call(["systemctl", "status", "nginx"], dryrun=False),
        call(["systemctl", "stop", "nginx"], dryrun=False),
        call(["systemctl", "start", "nginx"], dryrun=False),
        call(["systemctl", "status", "nginx"], dryrun=False),
    ]
    
    mock_run.assert_has_calls(expected_calls, any_order=False)


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_writes_service_header(mock_append, mock_run, temp_report_file):
    """Test that process_services writes service header."""
    services = {"nginx": []}
    mock_run.return_value = (0, "output", "")
    
    process_services(services, temp_report_file, dryrun=False)
    
    # Check for service header call
    service_header_calls = [c for c in mock_append.call_args_list if "# Service:" in str(c)]
    assert len(service_header_calls) >= 1


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_writes_command_output(mock_append, mock_run, temp_report_file):
    """Test that process_services writes command output to report."""
    services = {"nginx": []}
    mock_run.return_value = (0, "test output", "test error")
    
    process_services(services, temp_report_file, dryrun=False)
    
    # Check that append_file was called with command output
    output_calls = [c for c in mock_append.call_args_list if "test output" in str(c) or "exit:" in str(c)]
    assert len(output_calls) >= 4  # 4 commands


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_passes_dryrun_flag(mock_append, mock_run, temp_report_file):
    """Test that process_services passes dryrun flag to run_cmd."""
    services = {"nginx": []}
    mock_run.return_value = (0, "DRYRUN: not executed", "")
    
    process_services(services, temp_report_file, dryrun=True)
    
    # Verify all run_cmd calls received dryrun=True
    for call_args in mock_run.call_args_list:
        assert call_args[1]['dryrun'] is True


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
@patch('jps_systemctl_utils.processor.logger')
def test_process_services_logs_each_service(mock_logger, mock_append, mock_run, temp_report_file):
    """Test that process_services logs each service being processed."""
    services = {"nginx": [], "apache2": []}
    mock_run.return_value = (0, "output", "")
    
    process_services(services, temp_report_file, dryrun=False)
    
    # Check that logger.info was called for each service
    log_calls = [str(c) for c in mock_logger.info.call_args_list]
    assert any("nginx" in call for call in log_calls)
    assert any("apache2" in call for call in log_calls)


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_includes_exit_code_in_output(mock_append, mock_run, temp_report_file):
    """Test that process_services includes exit code in report."""
    services = {"nginx": []}
    mock_run.return_value = (42, "output", "error")
    
    process_services(services, temp_report_file, dryrun=False)
    
    # Check that exit code is written
    output_calls = [str(c) for c in mock_append.call_args_list]
    assert any("(exit: 42)" in call for call in output_calls)


# ============================================================
# Tests for check_safety
# ============================================================

@patch('jps_systemctl_utils.processor.run_shell_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_check_safety_returns_true_when_no_output(mock_append, mock_shell, temp_report_file):
    """Test that check_safety returns True when commands return no output."""
    mock_shell.return_value = (0, "", "")
    
    result = check_safety("nginx", ["squeue | grep nginx"], temp_report_file, dryrun=False)
    
    assert result is True


@patch('jps_systemctl_utils.processor.run_shell_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_check_safety_returns_false_when_output_detected(mock_append, mock_shell, temp_report_file):
    """Test that check_safety returns False when commands return output."""
    mock_shell.return_value = (0, "job-123 running\n", "")
    
    result = check_safety("nginx", ["squeue | grep nginx"], temp_report_file, dryrun=False)
    
    assert result is False


@patch('jps_systemctl_utils.processor.append_file')
def test_check_safety_bypasses_checks_in_dryrun(mock_append, temp_report_file):
    """Test that check_safety bypasses checks in dryrun mode."""
    result = check_safety("nginx", ["squeue | grep nginx"], temp_report_file, dryrun=True)
    
    assert result is True


@patch('jps_systemctl_utils.processor.run_shell_cmd')
@patch('jps_systemctl_utils.processor.append_file')
def test_check_safety_checks_multiple_commands(mock_append, mock_shell, temp_report_file):
    """Test that check_safety runs all safety commands."""
    mock_shell.return_value = (0, "", "")
    commands = ["cmd1", "cmd2", "cmd3"]
    
    check_safety("nginx", commands, temp_report_file, dryrun=False)
    
    assert mock_shell.call_count == 3


# ============================================================
# Tests for process_services with dict input
# ============================================================

@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.check_safety')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_handles_dict_input(mock_append, mock_safety, mock_run, temp_report_file):
    """Test that process_services handles dict input with safety commands."""
    services = {"nginx": ["squeue | grep nginx"]}
    mock_safety.return_value = True
    mock_run.return_value = (0, "output", "")
    
    process_services(services, temp_report_file, dryrun=False)
    
    mock_safety.assert_called_once()
    assert mock_run.call_count == 4  # 4 systemctl commands


@patch('jps_systemctl_utils.processor.run_cmd')
@patch('jps_systemctl_utils.processor.check_safety')
@patch('jps_systemctl_utils.processor.append_file')
def test_process_services_skips_service_when_unsafe(mock_append, mock_safety, mock_run, temp_report_file):
    """Test that process_services skips service when safety check fails."""
    services = {"nginx": ["squeue | grep nginx"]}
    mock_safety.return_value = False
    
    process_services(services, temp_report_file, dryrun=False)
    
    mock_safety.assert_called_once()
    # Should not run systemctl commands
    assert mock_run.call_count == 0
