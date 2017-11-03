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

        selected_output = ['JobID', 'JobName', 'CPUTime', 'Timelimit']

        sacct_output = _call_generic('sacct', '--format=' + ','.join(selected_output), '--allocations', '--parsable2', '--jobs', ','.join(job_ids))
        columns, *data = [line.split('|') for line in sacct_output.splitlines()]


class Job:

    def __init__(self):
        pass
