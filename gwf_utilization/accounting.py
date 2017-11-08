import re

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400


class Accountant:

    def __init__(self, jobs):
        self.jobs = jobs

    @classmethod
    def from_sacct_output(cls, sacct_output):
        sacct_columns, *sacct_data = [line.split('|') for line in sacct_output.splitlines()]
        return cls(jobs=[dict(zip(sacct_columns, entry)) for entry in sacct_data])


class Job:

    def __init__(self):
        pass

    @staticmethod
    def seconds(time_string):
        '''Converts time string on the form DD-HH:MM:SS to seconds'''

        time_regexp = r'(?:([0-9]+)-)?([0-9]{2}):([0-9]{2}):([0-9]{2})'
        days, hours, minutes, seconds = re.match(time_regexp, time_string).groups()

        result = int(seconds)
        result += SECONDS_PER_MINUTE * int(minutes)
        result += SECONDS_PER_HOUR * int(hours)

        if days:
            result += SECONDS_PER_DAY * int(days)

        return result
