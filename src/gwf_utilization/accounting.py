"""Read resource-accounting information from Slurm's :command:`sacct`."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR

MEMORY_EXPONENTS = {"": 0, "K": 10, "M": 20, "G": 30, "T": 40, "P": 50}
MEMORY_PATTERN = re.compile(r"(?P<amount>\d+)(?P<unit>[KMGTP]?)(?P<scope>[cn]?)$")
JOB_ID_PATTERN = re.compile(r"\d+(?:\.batch)?$")

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


@dataclass(frozen=True, slots=True)
class Job:
    """Resource allocation and observed usage for one completed Slurm job."""

    name: str
    cores: int
    nodes: int
    allocated_time_per_core: int
    used_walltime: int
    used_cpu_time: int
    allocated_memory: int
    used_memory: int

    @property
    def allocated_cores(self) -> int:
        """Return the number of CPU cores allocated across all nodes."""
        return self.cores * self.nodes

    @property
    def allocated_cpu_time(self) -> int:
        """Return the total CPU time allocated for the job, in seconds."""
        return self.allocated_time_per_core * self.cores

    @property
    def walltime_utilization(self) -> float:
        """Return used walltime as a percentage of allocated walltime."""
        return _percentage(self.used_walltime, self.allocated_time_per_core)

    @property
    def cpu_utilization(self) -> float:
        """Return used CPU time as a percentage of allocated CPU time."""
        return _percentage(self.used_cpu_time, self.allocated_cpu_time)

    @property
    def memory_utilization(self) -> float:
        """Return peak memory as a percentage of allocated memory."""
        return _percentage(self.used_memory, self.allocated_memory)


def _percentage(used: int, allocated: int) -> float:
    """Calculate a utilization percentage without failing for zero allocations."""
    return used / allocated * 100 if allocated else 0.0


def _seconds(time_string: str) -> int:
    """Convert Slurm's ``[[days-]hours:]minutes:]seconds`` format to seconds."""
    value = time_string.split(".", maxsplit=1)[0]
    days, separator, clock = value.partition("-")
    if not separator:
        clock = days
        days = "0"

    try:
        fields = [int(field) for field in clock.split(":")]
    except ValueError as error:
        raise ValueError(f"Invalid Slurm duration: {time_string!r}") from error

    if not 1 <= len(fields) <= 3 or any(field < 0 for field in fields):
        raise ValueError(f"Invalid Slurm duration: {time_string!r}")

    seconds, minutes, hours = (fields[::-1] + [0, 0])[:3]
    try:
        return (
            int(days) * SECONDS_PER_DAY
            + hours * SECONDS_PER_HOUR
            + minutes * SECONDS_PER_MINUTE
            + seconds
        )
    except ValueError as error:
        raise ValueError(f"Invalid Slurm duration: {time_string!r}") from error


def _parse_memory_string(memory_string: str, cores: int, nodes: int) -> int:
    """Return the number of bytes represented by a Slurm memory field."""
    if not memory_string:
        return 0

    match = MEMORY_PATTERN.fullmatch(memory_string)
    if match is None:
        raise ValueError(f"Invalid Slurm memory value: {memory_string!r}")

    result = int(match["amount"]) * 2 ** MEMORY_EXPONENTS[match["unit"]]
    if match["scope"] == "c":
        return result * cores
    if match["scope"] == "n":
        return result * nodes
    return result


def _call_sacct(job_id: str, *, include_header: bool = False) -> str:
    """Run ``sacct`` for one job and return its parsable output."""
    result = subprocess.run(
        [
            "sacct",
            f"--format={','.join(SLURM_SACCT_COLS)}",
            "--parsable2",
            "--jobs",
            job_id,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    if include_header:
        return result.stdout
    return "\n".join(result.stdout.splitlines()[1:])


def _call_sacct_batch(job_ids: Sequence[str]) -> str:
    """Return combined ``sacct`` output for the supplied job IDs."""
    if not job_ids:
        return ""

    outputs = [_call_sacct(job_ids[0], include_header=True)]
    outputs.extend(_call_sacct(job_id) for job_id in job_ids[1:])
    return "\n".join(line for output in outputs for line in output.splitlines())


def get_jobs_from_string(sacct_output: str) -> Iterator[Job]:
    """Yield completed primary jobs with their corresponding ``.batch`` records.

    Slurm can emit additional step records (such as ``.extern``); those are
    ignored. Array-task records retain the previous behaviour and are skipped.
    """
    rows = [line.split("|") for line in sacct_output.splitlines() if line]
    if not rows:
        return

    columns = tuple(rows[0])
    if columns != SLURM_SACCT_COLS:
        raise ValueError(
            f"Unexpected sacct columns: {columns!r}; expected {SLURM_SACCT_COLS!r}"
        )

    records: dict[str, dict[str, str]] = {}
    for row in rows[1:]:
        if len(row) != len(columns):
            raise ValueError(f"Malformed sacct row with {len(row)} columns: {row!r}")
        record = dict(zip(columns, row, strict=True))
        job_id = record["JobID"]
        if record["State"] == "COMPLETED" and JOB_ID_PATTERN.fullmatch(job_id):
            records[job_id] = record

    for job_id, record in records.items():
        if job_id.endswith(".batch"):
            continue
        batch_record = records.get(f"{job_id}.batch")
        if batch_record is None:
            continue

        cores = int(record["NCPUS"])
        nodes = int(record["NNodes"])
        yield Job(
            name=record["JobName"],
            cores=cores,
            nodes=nodes,
            used_walltime=_seconds(record["Elapsed"]),
            allocated_time_per_core=_seconds(record["Timelimit"]),
            used_cpu_time=_seconds(record["TotalCPU"]),
            allocated_memory=_parse_memory_string(record["ReqMem"], cores, nodes),
            used_memory=_parse_memory_string(batch_record["MaxRSS"], cores, nodes),
        )


def get_jobs(job_ids: Iterable[str]) -> Iterator[Job]:
    """Return completed accounting records for the supplied Slurm job IDs."""
    job_id_list = list(job_ids)
    if not job_id_list:
        return iter(())
    return get_jobs_from_string(_call_sacct_batch(job_id_list))
