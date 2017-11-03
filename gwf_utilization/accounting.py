import re

from gwf.backends.slurm import _call_generic


def seconds(time_string):
    '''Converts time string on the form DD-HH:MM:SS to seconds'''

    r = r'(?:([0-9]+)-)?([0-9]{2}):([0-9]{2}):([0-9]{2})'

    days, hours, minutes, seconds = re.match(r, time_string).groups()

    result = int(seconds)
    result += 60 * int(minutes)
    result += 3600 * int(hours)

    if days:
        result += 86400 * int(days)

    return result


class Accountant:

    def __init__(self, job_ids):

        # Request these outputs from sacct.
        columns = ['JobID', 'JobName', 'NCPUS', 'CPUTime', 'Timelimit']

        # Run sacct and parse output.
        sacct_output = _call_generic('sacct', '--format=' + ','.join(columns), '--allocations', '--parsable2', '--jobs', ','.join(job_ids))
        sacct_columns ,*sacct_data = [line.split('|') for line in sacct_output.splitlines()]

        # Hopefully sacct outputs the right columns in the right order.
        assert sacct_columns == columns

        self.jobs = [Job(columns=columns, data=data) for data in sacct_data]


class Job:

    def __init__(self, columns, data):
        # Store data in dictionary
        self.data = dict(zip(columns, data))
