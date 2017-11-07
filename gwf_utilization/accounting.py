import re


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

    def __init__(self, jobs):
        self.jobs = jobs

    @classmethod
    def from_sacct_output(cls, sacct_output):
        sacct_columns ,*sacct_data = [line.split('|') for line in sacct_output.splitlines()]
        return cls(jobs=[dict(zip(sacct_columns, entry)) for entry in sacct_data])
