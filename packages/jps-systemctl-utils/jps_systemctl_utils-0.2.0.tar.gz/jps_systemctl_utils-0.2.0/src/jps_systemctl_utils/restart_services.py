#!/usr/bin/env python3
"""
systemctl_runner.py

Simple sequential utility to:
  - Read newline-separated service names from --infile
  - For each service: status → stop → start → status
  - Write output to a report file
  - Log events
  - Support --dryrun (no systemctl commands executed)
  - Show one simple Rich progress bar

This script *does not* parse YAML, update JSON files, modify configuration,
or derive version-tags. It is strictly for running systemctl commands.
"""

from __future__ import annotations
import getpass

from datetime import datetime
from pathlib import Path
from typing import Tuple

import typer

from .logging_helper import setup_logging
from .report_writer import write_header
from .processor import process_services, append_file

app = typer.Typer(add_completion=False)


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def build_default_paths(script_path: Path, user: str) -> Tuple[Path, Path, Path]:
    """Build default timestamped outdir, report file, and logfile."""
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    outdir = Path(f"/tmp/{user}/{script_path.stem}/{ts}")
    report = outdir / f"{script_path.stem}_report.txt"
    logfile = outdir / f"{script_path.stem}.log"
    return outdir, report, logfile


@app.command()
def main(
    infile: Path = typer.Option(..., help="Text file with newline-separated service names."),
    outdir: Path = typer.Option(None, help="Output directory for logs/reports."),
    report_file: Path = typer.Option(None, help="Path for the report file."),
    logfile: Path = typer.Option(None, help="Path for logfile."),
    dryrun: bool = typer.Option(False, "--dryrun", help="If set, no systemctl commands are executed."),
):
    """Run systemctl status/stop/start/status for each service listed in --infile sequentially."""

    script_path = Path(__file__).resolve()
    user = getpass.getuser()

    # ------------------------------------------------------------
    # FIXED PATH RESOLUTION LOGIC
    # ------------------------------------------------------------
    if outdir is not None:
        # User explicitly wants all outputs inside this directory
        outdir.mkdir(parents=True, exist_ok=True)

        if report_file is None:
            report_file = outdir / f"{script_path.stem}_report.txt"

        if logfile is None:
            logfile = outdir / f"{script_path.stem}.log"

    else:
        # No outdir → generate timestamped defaults under /tmp
        default_outdir, default_report, default_log = build_default_paths(script_path, user)
        outdir = default_outdir

        if report_file is None:
            report_file = default_report

        if logfile is None:
            logfile = default_log

    setup_logging(logfile)

    write_header(report_file, script_path, infile, logfile)

    # ------------------------------------------------------------
    # Load service list
    # ------------------------------------------------------------
    try:
        with infile.open("r", encoding="utf-8") as f:
            services = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except Exception as e:
        append_file(report_file, f"# ERROR reading infile {infile}: {e}")
        raise typer.Exit(code=1)

    # ------------------------------------------------------------
    # Execute service operations (sequential)
    # ------------------------------------------------------------
    process_services(services, report=report_file, dryrun=dryrun)

    typer.echo(f"Wrote report file {report_file}")
    typer.echo(f"Wrote log file {logfile}")


if __name__ == "__main__":
    app()
