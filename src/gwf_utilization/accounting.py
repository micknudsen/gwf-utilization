import re
from collections import OrderedDict
from gwf.backends.slurm import SlurmBackend, _call_generic


SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR

EXPONENTS = OrderedDict([
    ('P', 50), ('T', 40), ('G', 30), ('M', 20), ('K', 10), ('', 0)
])

SLURM_SACCT_COLS = (
    'JobID', 'NCPUS', 'CPUTime', 'Timelimit', 'ReqMem', 'MaxRSS', 'NNodes'
)


def _iterpairs(itr):
    for i in range(0, len(itr) - 1, 2):
        yield itr[i], itr[i + 1]


def _seconds(time_string):
    """Converts time string on the form DD-HH:MM:SS to seconds"""

    time_regexp = r'(?:([0-9]+)-)?([0-9]{2}):([0-9]{2}):([0-9]{2})'
    days, hours, minutes, seconds = re.match(time_regexp, time_string).groups()

    result = int(seconds)
    result += SECONDS_PER_MINUTE * int(minutes)
    result += SECONDS_PER_HOUR * int(hours)

    if days:
        result += SECONDS_PER_DAY * int(days)

    return result


def _parse_memory_string(memory_string, cores, nodes):
    """Returns number of bytes in memory_string"""
    memory_regexp = r'([0-9]+)([KMGTP]?)([cn]?)'
    scalar, prefix, multiplier = re.match(memory_regexp, memory_string).groups()

    raw_result = int(scalar) * 2 ** EXPONENTS[prefix]
    if multiplier == 'c':
        raw_result *= cores
    elif multiplier == 'n':
        raw_result *= nodes
    return raw_result


def format_memory(self, memory):
    """Returns memory in pretty form using prefix"""
    # Find largest possible prefix. Uses that EXPONENTS
    # is sorted in decreasing order.
    for prefix, exponent in EXPONENTS.items():
        scalar = memory / 2 ** exponent
        if scalar >= 1:
            return '{scalar:.2g}{prefix}'.format(scalar=scalar, prefix=prefix)
    # Memory is less than 1Kb. Just return number of bytes.
    return memory


def _call_sacct(job_ids):
    return _call_generic(
        'sacct',
        '--format=' + ','.join(SLURM_SACCT_COLS),
        '--parsable2',
        '--state=COMPLETED',
        '--jobs', ','.join(job_ids)
    )


def get_jobs_from_string(sacct_output):
    """Yield jobs given a string of sacct output."""
    columns, *data = [
        line.split('|') for line in sacct_output.splitlines()
    ]

    assert tuple(columns) == SLURM_SACCT_COLS
    for entry, entry_batch in _iterpairs(data):
        dct = dict(zip(columns, entry))
        dct_batch = dict(zip(columns, entry_batch))
        assert dct_batch['JobID'] == dct['JobID'] + '.batch'

        cores = int(dct['NCPUS'])
        nodes = int(dct['NNodes'])

        yield Job(
            cores=cores,
            nodes=nodes,
            allocated_time=_seconds(dct['Timelimit']),
            used_time=_seconds(dct['CPUTime']),
            allocated_memory=_parse_memory_string(dct['ReqMem'], cores, nodes),
            used_memory=_parse_memory_string(dct_batch['MaxRSS'], cores, nodes)
        )


def get_jobs(job_ids):
    return get_jobs_from_string(_call_sacct(job_ids))


class Job:
    """Representation of a job and its used and allocated resources.

    :param cores int:
        Number of cores allocated on each node.
    :param nodes int:
        Number of nodes allocated.
    :param allocated_time int:
        Time allocated for the job in seconds.
    :param used_time int:
        Time used by the job in seconds.
    :param allocated_memory int:
        Memory allocated for the job in bytes.
    :param used_memory int:
        Memory used by the job in bytes.
    """

    def __init__(self, cores, nodes, allocated_time, used_time,
                 allocated_memory, used_memory):
        self.cores = cores
        self.nodes = nodes
        self.allocated_time = allocated_time
        self.used_time = used_time
        self.allocated_memory = allocated_memory
        self.used_memory = used_memory

    @property
    def cpu_utilization(self):
        return self.used_time / (self.cores * self.allocated_time)

    @property
    def memory_utilization(self):
        return self.used_memory / self.allocated_memory
