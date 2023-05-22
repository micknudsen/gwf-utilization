import math
import click
import os.path
import json

from texttable import Texttable

from gwf import Workflow
from gwf.core import CachedFilesystem, Graph, pass_context
from gwf.exceptions import GWFError
from gwf.filtering import filter_names

from gwf_utilization.accounting import get_jobs


def pretty_time(time_in_seconds):
    minutes, seconds = divmod(time_in_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    result = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    if days:
        result = f"{days}-{result}"
    return result


def pretty_size(size_in_bytes):
    if size_in_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    exponent = int(math.floor(math.log(size_in_bytes, 1024)))
    multiplier = math.pow(1024, exponent)
    result = round(size_in_bytes / multiplier, 2)
    return f"{result} {size_name[exponent]}"


def load_tracked_jobs(working_dir):
    try:
        with open(
            os.path.join(working_dir, ".gwf", "slurm-backend-tracked.json")
        ) as state_file:
            return json.load(state_file)
    except FileNotFoundError:
        return {}


@click.command()
@click.argument("targets", nargs=-1)
@pass_context
def utilization(ctx, targets):
    # This plugin only works for the slurm backend.
    if ctx.backend != "slurm":
        raise GWFError("Utilization plugin only works for Slurm backend!")

    workflow = Workflow.from_context(ctx)
    graph = Graph.from_targets(workflow.targets, fs=CachedFilesystem())

    # If user specified list of targets, only report utilization for these.
    # Otherwise, report utilization for all targets.
    matches = graph.targets.values()
    if targets:
        matches = filter_names(matches, targets)

    tracked_jobs = load_tracked_jobs(ctx.working_dir)
    job_ids = [
        tracked_jobs[target.name]
        for target in matches
        if tracked_jobs.get(target.name) is not None
    ]

    rows = [
        [
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
        ]
    ]
    for job in get_jobs(job_ids):
        rows.append(
            (
                job.name,
                job.allocated_cores,
                pretty_time(job.allocated_time_per_core),
                pretty_time(job.used_walltime),
                pretty_size(job.allocated_memory),
                pretty_size(job.used_memory),
                pretty_time(job.allocated_cpu_time),
                pretty_time(job.used_cpu_time),
                str(format(job.walltime_utilization, ".1f")),
                format(job.memory_utilization, ".1f"),
                format(job.cpu_utilization, ".1f"),
            )
        )

    table = Texttable()

    table.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)

    ncols = len(rows[0])

    table.set_max_width(0)
    table.set_header_align("l" * ncols)
    table.set_cols_align(["l"] + (ncols - 1) * ["r"])
    table.set_cols_dtype(["t"] * ncols)

    table.add_rows(rows)

    print(table.draw())
