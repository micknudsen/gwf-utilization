from gwf.backends.slurm import _call_generic


def call_sacct(job_ids):
   return _call_generic('sacct', '--noheader', '--long', '--parsable2', '--allocations', '--jobs', ','.join(job_ids))
