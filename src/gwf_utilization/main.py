import click

from gwf.core import graph_from_config
from gwf.exceptions import GWFError
from gwf.filtering import filter_names
from gwf.backends import backend_from_config
from gwf.backends.slurm import SlurmBackend

from gwf_utilization.accounting import get_jobs


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

    column_names = ['Name',
                    'Time Limit', 'Time Used',
                    'Memory Alloc', 'Memory Used']

    rows = [
        (
            target.name,
            job.allocated_time, job.used_time,
            job.allocated_memory, job.used_memory
        )
        for target, job in zip(matches, get_jobs(job_ids))
    ]

    column_widths = []
    for column_number, title in enumerate(column_names):
        column_entries = [title] + [str(row[column_number]) for row in rows]
        column_widths.append(max([len(entry) for entry in column_entries]))

    column_types = ['s', 'd', 'd', 'd', 'd']
    column_alignments = ['<', '>', '>', '>', '>']

    row_format = '\t'.join([f'{{:{a}{w}{t}}}' for a, w, t in zip(column_alignments, column_widths, column_types)])

    header_types = ['s', 's', 's', 's', 's']
    header_alignments = ['<', '<', '<', '<', '<']

    header_format = '\t'.join([f'{{:{a}{w}{t}}}' for a, w, t in zip(header_alignments, column_widths, header_types)])

    print(header_format.format(*column_names))
    for row in rows:
        print(row_format.format(*row))
