import click

from gwf.core import graph_from_config
from gwf.exceptions import GWFError
from gwf.backends import backend_from_config
from gwf.backends.slurm import SlurmBackend, _call_generic


def call_sacct(job_ids):
   return _call_generic('sacct', '--noheader', '--long', '--parsable2', '--allocations', '--jobs', ','.join(job_ids))

@click.command()
@click.pass_obj
def utilization(obj):
    # This plugin only works for SlurmBackend
    backend_cls = backend_from_config(obj)
    if not issubclass(backend_cls, SlurmBackend):
        raise GWFError('Utilization plugin only works for Slurm backend!')

    graph = graph_from_config(obj)

    with backend_cls() as backend:
        job_ids = [backend.get_job_id(target) for target in graph.targets.values()]
        print(call_sacct(job_ids))
