from __future__ import annotations
import getpass
from datetime import datetime
from pathlib import Path


def write_header(report: Path, script_path: Path, infile: Path, logfile: Path) -> None:
    
    report.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with report.open("w", encoding="utf-8") as f:
        f.write(f"## method-created: {script_path}\n")
        f.write(f"## date-created: {now}\n")
        f.write(f"## created-by: {getpass.getuser()}\n")
        f.write(f"## logfile: {logfile}\n")
        f.write(f"## infile: {infile}\n\n")
