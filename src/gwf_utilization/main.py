import click
from texttable import Texttable

from gwf.core import graph_from_config
from gwf.exceptions import GWFError
from gwf.filtering import filter_names
from gwf.backends import backend_from_config
from gwf.backends.slurm import SlurmBackend, _call_generic

from gwf_utilization.accounting import get_jobs


OUTPUT_HEADER = [
    'JobID', 'Name', 'Time Limit',
    'Time Used', 'Memory Alloc', 'Memory Used'
]


@click.command()
@click.argument('targets', nargs=-1)
@click.pass_obj
def utilization(obj, targets):
    # This plugin only works for SlurmBackend
    backend_cls = backend_from_config(obj)
    if not issubclass(backend_cls, SlurmBackend):
        raise GWFError('Utilization plugin only works for Slurm backend!')

    graph = graph_from_config(obj)

    # If user specified list of targets, only report utilization for these.
    # Otherwise, report utilization for all targets.
    matches = graph.targets.values()
    if targets:
        matches = filter_names(matches, targets)

    with backend_cls() as backend:
        job_ids = [backend.get_job_id(target) for target in matches]

    # Run sacct and parse output.
    rows = [
        (
            job.slurm_id, job.name, job.time_limit(), job.cpu_time,
            job.req_mem, job.max_rss()
        )
        for job in get_jobs(job_ids)
    ]

    table = Texttable()
    table.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)
    table.set_cols_dtype(['i', 't', 't', 't', 't', 't'])
    table.set_cols_align(['r', 'l', 'r', 'r', 'r', 'r'])
    table.add_rows(rows)
    table.set_cols_width([12, 50, 12, 12, 12, 12])
    print(table.draw())
