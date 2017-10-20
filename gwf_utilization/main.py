import click

from gwf.core import graph_from_config
from gwf.exceptions import GWFError
from gwf.filtering import filter_names
from gwf.backends import backend_from_config
from gwf.backends.slurm import SlurmBackend

from gwf_utilization.accounting import ReportGenerator


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

    # Generate utilization report from Slurm job ids.
    with backend_cls() as backend:
        report_generator = ReportGenerator(job_ids=[backend.get_job_id(target) for target in matches])
