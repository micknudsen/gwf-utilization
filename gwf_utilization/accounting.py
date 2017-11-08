import re

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400


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


class Accountant:

    def __init__(self, jobs):
        self.jobs = jobs

    @classmethod
    def from_sacct_output(cls, sacct_output):
        sacct_columns, *sacct_data = [line.split('|') for line in sacct_output.splitlines()]
        return cls(jobs=[Job.from_sacct_data_dict(dict(zip(sacct_columns, entry))) for entry in sacct_data])


class Job:

    def __init__(self, slurm_id, name, state, cpus, cpu_time, wall_time):
        self.slurm_id = slurm_id
        self.name = name
        self.state = state
        self.cpus = cpus
        self._cpu_time = cpu_time
        self._wall_time = wall_time

    @classmethod
    def from_sacct_data_dict(cls, sacct_data_dict):
        return cls(slurm_id=sacct_data_dict['JobID'],
                   name=sacct_data_dict['JobName'],
                   state=sacct_data_dict['State'],
                   cpus=sacct_data_dict['NCPUS'],
                   cpu_time=sacct_data_dict['CPUTime'],
                   wall_time=sacct_data_dict['Timelimit'])

    def cpu_time(self, raw=False):
        return seconds(self._cpu_time) if raw else self._cpu_time

    def wall_time(self, raw=False):
        return seconds(self._wall_time) if raw else self._cpu_time
