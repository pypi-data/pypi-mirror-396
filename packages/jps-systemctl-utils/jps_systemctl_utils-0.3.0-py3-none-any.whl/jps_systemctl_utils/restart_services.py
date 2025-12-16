#!/usr/bin/env python3
"""
restart_services.py

Utility to manage systemd services with safety checks:
  - Read service configurations from a YAML file
  - For each service: run safety checks, then status → stop → start → status
  - Write output to a report file
  - Log events
  - Support --dryrun (no systemctl commands executed)
  - Show one simple Rich progress bar

YAML Format:
  service_name.service:
    - safety_check_command_1
    - safety_check_command_2

Safety checks: If any safety check command returns output, the service restart is skipped.
"""

from __future__ import annotations
import getpass
import yaml

from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, List

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
    infile: Path = typer.Option(..., help="YAML file with service configurations and safety checks."),
    outdir: Path = typer.Option(None, help="Output directory for logs/reports."),
    report_file: Path = typer.Option(None, help="Path for the report file."),
    logfile: Path = typer.Option(None, help="Path for logfile."),
    dryrun: bool = typer.Option(False, "--dryrun", help="If set, no systemctl commands are executed."),
):
    """Run systemctl status/stop/start/status for each service with optional safety checks."""

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
    # Load YAML service configuration
    # ------------------------------------------------------------
    try:
        with infile.open("r", encoding="utf-8") as f:
            services = yaml.safe_load(f)
            
        if services is None:
            services = {}
        elif not isinstance(services, dict):
            raise ValueError(f"Invalid YAML format: expected a dictionary, got {type(services).__name__}")
        
        # Validate YAML structure
        validated_services = {}
        for svc_name, safety_cmds in services.items():
            if safety_cmds is None:
                validated_services[svc_name] = []
            elif isinstance(safety_cmds, list):
                validated_services[svc_name] = safety_cmds
            else:
                raise ValueError(f"Invalid format for service {svc_name}: expected list or null, got {type(safety_cmds).__name__}")
        
        services = validated_services
        typer.echo(f"📋 Loaded {len(services)} services from YAML configuration")
            
    except yaml.YAMLError as e:
        append_file(report_file, f"# ERROR parsing YAML file {infile}: {e}")
        typer.echo(f"❌ Error parsing YAML file: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        append_file(report_file, f"# ERROR reading infile {infile}: {e}")
        typer.echo(f"❌ Error reading input file: {e}", err=True)
        raise typer.Exit(code=1)

    # ------------------------------------------------------------
    # Execute service operations (sequential)
    # ------------------------------------------------------------
    process_services(services, report=report_file, dryrun=dryrun)

    typer.echo(f"✅ Wrote report file {report_file}")
    typer.echo(f"✅ Wrote log file {logfile}")


if __name__ == "__main__":
    app()
