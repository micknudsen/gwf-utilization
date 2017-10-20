import pandas as pd

from gwf.backends.slurm import _call_generic


class Accountant:

    def __init__(self, job_ids):

        sacct_output =  _call_generic('sacct', '--long', '--parsable2', '--allocations', '--jobs', ','.join(job_ids))
        columns, *data = [line.split('|') for line in sacct_output.splitlines()]

        self._df = pd.DataFrame(data=data, columns=columns)
