import click
import math

from texttable import Texttable

from gwf.core import graph_from_config
from gwf.exceptions import GWFError
from gwf.filtering import filter_names
from gwf.backends import backend_from_config
from gwf.backends.slurm import SlurmBackend

from gwf_utilization.accounting import get_jobs


def pretty_time(time_in_seconds):
    minutes, seconds = divmod(time_in_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    result = '%02d:%02d:%02d' % (hours, minutes, seconds)
    if days:
        result = '%d-' % days + result
    return result


def pretty_size(size_in_bytes):
    if size_in_bytes == 0:
        return '0 B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    exponent = int(math.floor(math.log(size_in_bytes, 1024)))
    multiplier = math.pow(1024, exponent)
    result = round(size_in_bytes / multiplier, 2)
    return '%s %s' % (result, size_name[exponent])


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

    target_column_width = max([len(target.name) for target in matches]) + 1

    rows = [['Target', 'Allocated Memory', 'Memory Used', 'Allocated CPU Time', 'Used CPU Time', 'Memory Utilization', 'CPU Utilization']]
    for target, job in zip(matches, get_jobs(job_ids)):
        rows.append([target.name,
                     pretty_size(job.allocated_memory),
                     pretty_size(job.used_memory),
                     pretty_time(job.allocated_cpu_time),
                     pretty_time(job.used_cpu_time),
                     '{:.0%}'.format(job.memory_utilization),
                     '{:.0%}'.format(job.cpu_utilization)])

    table = Texttable()

    table.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)

    ncols = len(rows[0])

    table.set_max_width(0)
    table.set_header_align('l' * ncols)
    table.set_cols_align(['l'] + (ncols - 1) * ['r'])

    table.add_rows(rows)

    print(table.draw())
