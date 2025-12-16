import logging

import subprocess

from pathlib import Path
from typing import List, Tuple
from rich.progress import Progress

logger = logging.getLogger("systemctl_runner")

def process_services(services: List[str], report: Path, *, dryrun: bool) -> None:

    with Progress() as progress:
        task = progress.add_task("Processing services...", total=len(services))

        for svc in services:
            svc = svc.strip()
            if not svc:
                continue

            logger.info("Processing service: %s", svc)
            append_file(report, f"# Service: {svc}")

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

