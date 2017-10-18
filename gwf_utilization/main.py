import click

from gwf.core import graph_from_config
from gwf.backends import backend_from_config
from gwf.backends.slurm import SlurmBackend
from gwf.exceptions import GWFError


@click.command()
@click.pass_obj
def utilization(obj):
    # This plugin only works for SlurmBackend
    if not issubclass(backend_from_config(obj), SlurmBackend):
        raise GWFError('Utilization plugin only works for Slurm backend!')
