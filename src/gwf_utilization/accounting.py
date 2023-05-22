import re
import subprocess
from collections import OrderedDict


SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR

EXPONENTS = OrderedDict(
    [("P", 50), ("T", 40), ("G", 30), ("M", 20), ("K", 10), ("", 0)]
)

SLURM_SACCT_COLS = (
    "JobName",
    "JobID",
    "State",
    "NCPUS",
    "Elapsed",
    "TotalCPU",
    "Timelimit",
    "ReqMem",
    "MaxRSS",
    "NNodes",
)


def _iterpairs(itr):
    for i in range(0, len(itr) - 1, 2):
        yield itr[i], itr[i + 1]


def _seconds(time_string):
    """Converts time string on the form [[[days-]hours:]minutes:]seconds[.milliseconds] to seconds"""

    # Remove milliseconds
    time_string = time_string.split(".")[0]

    if "-" in time_string:
        days, time_string = time_string.split("-")
    else:
        days = None

    parts = time_string.split(":")[::-1]

    try:
        seconds = parts[0]
    except IndexError:
        seconds = 0

    try:
        minutes = parts[1]
    except IndexError:
        minutes = 0

    try:
        hours = parts[2]
    except IndexError:
        hours = 0

    result = int(seconds)
    result += SECONDS_PER_MINUTE * int(minutes)
    result += SECONDS_PER_HOUR * int(hours)

    if days:
        result += SECONDS_PER_DAY * int(days)

    return result


def _parse_memory_string(memory_string, cores, nodes):
    """Returns number of bytes in memory_string"""

    # If job is very tiny, SLURM may not report used memory at all.
    if not memory_string:
        return 0

    memory_regexp = r"([0-9]+)([KMGTP]?)([cn]?)"
    scalar, prefix, multiplier = re.match(memory_regexp, memory_string).groups()

    raw_result = int(scalar) * 2 ** EXPONENTS[prefix]
    if multiplier == "c":
        raw_result *= cores
    elif multiplier == "n":
        raw_result *= nodes
    return raw_result


def _call_sacct(job_id, include_header=False):
    proc = subprocess.Popen(
        [
            "sacct",
            "--format=" + ",".join(SLURM_SACCT_COLS),
            "--parsable2",
            "--jobs",
            job_id,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, _ = proc.communicate()
    if include_header:
        return stdout
    # Skip first line (the header).
    return "\n".join(stdout.split("\n")[1:])


def _call_sacct_batch(job_ids):
    if not job_ids:
        return ""
    result = _call_sacct(job_ids[0], include_header=True)
    for job_id in job_ids[1:]:
        result += _call_sacct(job_id)
    return result


def get_jobs_from_string(sacct_output):
    """Yield jobs given a string of sacct output."""
    sacct_output_rows = [line.split("|") for line in sacct_output.splitlines()]
    columns = sacct_output_rows[0]
    data = [
        row
        for row in sacct_output_rows
        if "COMPLETED" in row and re.match(r"[0-9]+(\.batch)?$", row[1])
    ]

    assert tuple(columns) == SLURM_SACCT_COLS

    for entry, entry_batch in _iterpairs(data):
        dct = dict(zip(columns, entry))

        if "_" in dct["JobID"]:
            continue

        dct_batch = dict(zip(columns, entry_batch))
        assert dct_batch["JobID"] == dct["JobID"] + ".batch"

        cores = int(dct["NCPUS"])
        nodes = int(dct["NNodes"])

        yield Job(
            name=dct["JobName"],
            cores=cores,
            nodes=nodes,
            used_walltime=_seconds(dct["Elapsed"]),
            allocated_time_per_core=_seconds(dct["Timelimit"]),
            used_cpu_time=_seconds(dct["TotalCPU"]),
            allocated_memory=_parse_memory_string(dct["ReqMem"], cores, nodes),
            used_memory=_parse_memory_string(dct_batch["MaxRSS"], cores, nodes),
        )


def get_jobs(job_ids):
    """Returns an iterator of Job objects."""
    sacct_output = _call_sacct_batch(job_ids)
    if not sacct_output:
        return iter([])
    return get_jobs_from_string(sacct_output)


class Job:
    """Representation of a job and its used and allocated resources.

    :param name str:
        Name of the job.
    :param cores int:
        Number of cores allocated on each node.
    :param nodes int:
        Number of nodes allocated.
    :param allocated_time_per_core int:
        Time per core allocated for the job in seconds.
    :param used_walltime
        Walltime used by the job in seconds.
    :param used_cpu_time int:
        CPU time used by the job in seconds.
    :param allocated_memory int:
        Memory allocated for the job in bytes.
    :param used_memory int:
        Memory used by the job in bytes.
    """

    def __init__(
        self,
        name,
        cores,
        nodes,
        allocated_time_per_core,
        used_walltime,
        used_cpu_time,
        allocated_memory,
        used_memory,
    ):
        self.name = name
        self.allocated_time_per_core = allocated_time_per_core
        self.used_walltime = used_walltime
        self.allocated_cores = cores * nodes
        self.allocated_cpu_time = allocated_time_per_core * cores
        self.used_cpu_time = used_cpu_time
        self.allocated_memory = allocated_memory
        self.used_memory = used_memory

    @property
    def walltime_utilization(self):
        return self.used_walltime / self.allocated_time_per_core * 100

    @property
    def cpu_utilization(self):
        return self.used_cpu_time / self.allocated_cpu_time * 100

    @property
    def memory_utilization(self):
        return self.used_memory / self.allocated_memory * 100
