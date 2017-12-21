import re
from collections import OrderedDict


SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400

EXPONENTS = OrderedDict([('P', 50), ('T', 40), ('G', 30), ('M', 20), ('K', 10), ('', 0)])


def iterpairs(itr):
    for i in range(0, len(itr) - 1, 2):
        yield itr[i], itr[i + 1]


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


def bytes(scalar, exponent):
    '''Converts a memory string to bytes'''
    return int(scalar) * 2 ** EXPONENTS[exponent]


def get_jobs(sacct_output):

    result = []

    sacct_columns, *sacct_data = [line.split('|') for line in sacct_output.splitlines()]

    for entry, entry_batch in iterpairs(sacct_data):

        sacct_data_dict = dict(zip(sacct_columns, entry))
        sacct_data_dict_batch = dict(zip(sacct_columns, entry_batch))

        assert sacct_data_dict_batch['JobID'] == sacct_data_dict['JobID'] + '.batch'

        result.append(Job(slurm_id=sacct_data_dict['JobID'],
                          name=sacct_data_dict['JobName'],
                          state=sacct_data_dict['State'],
                          cores=int(sacct_data_dict['NCPUS']),
                          nodes=int(sacct_data_dict['NNodes']),
                          cpu_time=sacct_data_dict['CPUTime'],
                          wall_time=sacct_data_dict['Timelimit'],
                          req_mem=sacct_data_dict['ReqMem'],
                          max_rss=sacct_data_dict_batch['MaxRSS']))
    return result


class Job:

    def __init__(self, slurm_id, name, state, cores, nodes, cpu_time, wall_time, req_mem, max_rss):
        self.slurm_id = slurm_id
        self.name = name
        self.state = state
        self.cores = cores
        self.nodes = nodes
        self._cpu_time = cpu_time
        self._wall_time = wall_time
        self._req_mem = req_mem
        self._max_rss = max_rss

    def cpu_time(self, raw=False):
        return seconds(self._cpu_time) if raw else self._cpu_time

    def wall_time(self, raw=False):
        return seconds(self._wall_time) if raw else self._cpu_time

    def time_utilization(self):
        used_time = self.cpu_time(raw=True)
        allocated_time = self.cpus * self.wall_time(raw=True)
        return used_time / allocated_time

    def allocated_memory(self, raw=False):
        memory_regexp = r'([0-9]+)([KMGTP]?)([cn]?)'
        scalar, exponent, multiplier = re.match(memory_regexp, self._req_mem).groups()

        raw_result = bytes(scalar=scalar, exponent=exponent)
        if multiplier == 'c':
            raw_result *= self.cores
        elif multiplier == 'n':
            raw_result *= self.nodes

        if raw:
            return raw_result

        for prefix, exponent in EXPONENTS.items():
            scalar = raw_result / 2 ** exponent
            if scalar >= 1:
                return f'{scalar}{prefix}'
