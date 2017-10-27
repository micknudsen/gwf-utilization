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

        sacct_output = _call_generic('sacct', '--long', '--parsable2', '--allocations', '--jobs', ','.join(job_ids))
        columns, *data = [line.split('|') for line in sacct_output.splitlines()]
