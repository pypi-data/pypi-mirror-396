import logging

import subprocess
import sys

from pathlib import Path
from typing import List, Tuple, Dict
from rich.progress import Progress

logger = logging.getLogger("systemctl_runner")


def process_services(services: Dict[str, List[str]], report: Path, *, dryrun: bool) -> None:
    """Process services with optional safety checks.
    
    Args:
        services: Dict mapping service names to lists of safety check commands.
        report: Path to the report file.
        dryrun: If True, commands are not executed.
    """
    with Progress() as progress:
        task = progress.add_task("Processing services...", total=len(services))

        for svc, safety_commands in services.items():
            svc = svc.strip()
            if not svc:
                continue

            logger.info("Processing service: %s", svc)
            append_file(report, f"# Service: {svc}")

            # Run safety checks if provided
            if safety_commands:
                safe_to_restart = check_safety(svc, safety_commands, report, dryrun=dryrun)
                if not safe_to_restart:
                    msg = f"⚠️  SKIPPING {svc}: Safety check failed - jobs are still running"
                    logger.warning(msg)
                    print(msg, file=sys.stdout)
                    append_file(report, f"\n{msg}\n")
                    progress.update(task, advance=1)
                    continue

            # Run systemctl commands
            commands = [
                ["systemctl", "status", svc],
                ["systemctl", "stop", svc],
                ["systemctl", "start", svc],
                ["systemctl", "status", svc],
            ]

            for cmd in commands:
                cmd_str = " ".join(cmd)
                rc, out, err = run_cmd(cmd, dryrun=dryrun)
                append_file(report, f"$ {cmd_str}\n{out}{err}(exit: {rc})\n")

            progress.update(task, advance=1)


def check_safety(service: str, safety_commands: List[str], report: Path, *, dryrun: bool) -> bool:
    """Check if it's safe to restart a service by running safety check commands.
    
    Args:
        service: Service name.
        safety_commands: List of shell commands to check if service can be restarted.
        report: Path to the report file.
        dryrun: If True, safety checks are bypassed.
    
    Returns:
        True if safe to restart (no output from safety commands), False otherwise.
    """
    if dryrun:
        append_file(report, "# DRYRUN: Skipping safety checks\n")
        return True
    
    append_file(report, f"# Running safety checks for {service}:")
    
    for cmd_str in safety_commands:
        logger.info("Running safety check: %s", cmd_str)
        append_file(report, f"$ {cmd_str}")
        
        # Run the command through shell to support pipes
        rc, out, err = run_shell_cmd(cmd_str, dryrun=False)
        append_file(report, f"{out}{err}(exit: {rc})")
        
        # If the command returns any output, it's not safe to restart
        if out.strip():
            append_file(report, f"# Safety check FAILED: Output detected, service has active jobs\n")
            return False
    
    append_file(report, f"# Safety checks PASSED: Safe to restart {service}\n")
    return True


def append_file(path: Path, text: str) -> None:
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open("a", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")


def run_cmd(cmd: List[str], *, dryrun: bool) -> Tuple[int, str, str]:
    """
    Execute a command unless dryrun=True.

    Args:
        cmd: Command and arguments as a list.
        dryrun: If True, do not execute the command.

    Returns:
        (exit_code, stdout, stderr).
    """
    if dryrun:
        return 0, f"DRYRUN: {' '.join(cmd)} not executed.\n", ""

    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr


def run_shell_cmd(cmd_str: str, *, dryrun: bool) -> Tuple[int, str, str]:
    """
    Execute a shell command string (supports pipes and redirects).

    Args:
        cmd_str: Command string to execute via shell.
        dryrun: If True, do not execute the command.

    Returns:
        (exit_code, stdout, stderr).
    """
    if dryrun:
        return 0, f"DRYRUN: {cmd_str} not executed.\n", ""

    proc = subprocess.run(cmd_str, shell=True, text=True, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr

