"""The ``gwf utilization`` command."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import click
from gwf import Workflow
from gwf.core import CachedFilesystem, Graph, pass_context
from gwf.exceptions import GWFError
from gwf.filtering import filter_names
from texttable import Texttable

from gwf_utilization.accounting import get_jobs


def pretty_time(time_in_seconds: int) -> str:
    """Format a duration in Slurm's human-readable time format."""
    minutes, seconds = divmod(time_in_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    result = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{days}-{result}" if days else result


def pretty_size(size_in_bytes: int) -> str:
    """Format a byte count using binary (1024-based) units."""
    if size_in_bytes == 0:
        return "0 B"

    units = ("B", "KB", "MB", "GB", "TB", "PB")
    exponent = min(int(math.log(size_in_bytes, 1024)), len(units) - 1)
    value = round(size_in_bytes / 1024**exponent, 2)
    return f"{value} {units[exponent]}"


def load_tracked_jobs(working_dir: str | Path) -> dict[str, str]:
    """Load the Slurm job IDs that gwf tracks in a working directory."""
    path = Path(working_dir) / ".gwf" / "slurm-backend-tracked.json"
    try:
        with path.open(encoding="utf-8") as state_file:
            data: Any = json.load(state_file)
    except FileNotFoundError:
        return {}

    if not isinstance(data, dict) or not all(
        isinstance(name, str) and isinstance(job_id, str)
        for name, job_id in data.items()
    ):
        raise GWFError(f"Invalid tracked-job state file: {path}")
    return data


@click.command()
@click.argument("targets", nargs=-1)
@pass_context
def utilization(ctx: Any, targets: tuple[str, ...]) -> None:
    """Report allocated and used Slurm resources for workflow TARGETS."""
    if ctx.backend != "slurm":
        raise GWFError("Utilization plugin only works for Slurm backend!")

    workflow = Workflow.from_context(ctx)
    graph = Graph.from_targets(workflow.targets, fs=CachedFilesystem())
    matches = graph.targets.values()
    if targets:
        matches = filter_names(matches, targets)

    tracked_jobs = load_tracked_jobs(ctx.working_dir)
    job_ids = [
        tracked_jobs[target.name] for target in matches if target.name in tracked_jobs
    ]
    rows: list[tuple[str, ...]] = [
        (
            "Target",
            "Cores",
            "Walltime Alloc",
            "Walltime Used",
            "Memory Alloc",
            "Memory Used",
            "CPU Time Alloc",
            "CPU Time Used",
            "Walltime %",
            "Memory %",
            "CPU %",
        )
    ]
    rows.extend(
        (
            job.name,
            str(job.allocated_cores),
            pretty_time(job.allocated_time_per_core),
            pretty_time(job.used_walltime),
            pretty_size(job.allocated_memory),
            pretty_size(job.used_memory),
            pretty_time(job.allocated_cpu_time),
            pretty_time(job.used_cpu_time),
            f"{job.walltime_utilization:.1f}",
            f"{job.memory_utilization:.1f}",
            f"{job.cpu_utilization:.1f}",
        )
        for job in get_jobs(job_ids)
    )

    table = Texttable()
    table.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)
    table.set_max_width(0)
    table.set_header_align("l" * len(rows[0]))
    table.set_cols_align(["l", *("r" for _ in rows[0][1:])])
    table.set_cols_dtype(["t"] * len(rows[0]))
    table.add_rows(rows)
    click.echo(table.draw())
