from __future__ import annotations

import subprocess
from unittest.mock import Mock, patch

import pytest

from gwf_utilization.accounting import (
    Job,
    _call_sacct,
    _parse_memory_string,
    _seconds,
    get_jobs,
    get_jobs_from_string,
)

SACCT_HEADER = (
    "JobName|JobID|State|NCPUS|Elapsed|TotalCPU|Timelimit|ReqMem|MaxRSS|NNodes"
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("05", 5),
        ("05.123", 5),
        ("02:11", 131),
        ("02:11.456", 131),
        ("03:12:07", 11527),
        ("03:12:07.890", 11527),
        ("4-07:19:59", 371999),
        ("4-07:19:59.793", 371999),
    ],
)
def test_seconds(value: str, expected: int) -> None:
    assert _seconds(value) == expected


@pytest.mark.parametrize("value", ["", "1:2:3:4", "a:01", "1-day"])
def test_seconds_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid Slurm duration"):
        _seconds(value)


@pytest.mark.parametrize(
    ("value", "cores", "nodes", "expected"),
    [
        ("1024", 2, 3, 1024),
        ("1K", 2, 3, 1024),
        ("2Mc", 4, 3, 8 * 1024**2),
        ("2Gn", 4, 3, 6 * 1024**3),
        ("", 2, 3, 0),
    ],
)
def test_parse_memory_string(value: str, cores: int, nodes: int, expected: int) -> None:
    assert _parse_memory_string(value, cores, nodes) == expected


def test_parse_memory_string_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="Invalid Slurm memory"):
        _parse_memory_string("1XB", cores=1, nodes=1)


def test_job_utilization() -> None:
    job = Job(
        name="foo",
        cores=1,
        nodes=1,
        used_walltime=12,
        allocated_time_per_core=60,
        used_cpu_time=30,
        allocated_memory=512,
        used_memory=256,
    )

    assert job.walltime_utilization == 20
    assert job.cpu_utilization == 50
    assert job.memory_utilization == 50


def test_job_utilization_handles_zero_allocations() -> None:
    job = Job(
        name="foo",
        cores=0,
        nodes=1,
        used_walltime=12,
        allocated_time_per_core=0,
        used_cpu_time=30,
        allocated_memory=0,
        used_memory=256,
    )

    assert job.walltime_utilization == 0
    assert job.cpu_utilization == 0
    assert job.memory_utilization == 0


def test_get_jobs_from_string_ignores_non_batch_steps() -> None:
    output = "\n".join(
        [
            SACCT_HEADER,
            "foo|1|COMPLETED|1|00:02:00|00:06:10|06:00:00|8Gn||1",
            "batch|1.batch|COMPLETED|1|00:02:00|00:06:10||8Gn|3324536K|1",
            "extern|1.extern|COMPLETED|1|00:01:06|00:00:00||8Gn|816K|1",
            "foo|1_1|COMPLETED|1|00:02:00|00:06:10|06:00:00|8Gn||1",
            "batch|1_1.batch|COMPLETED|1|00:02:00|00:06:10||8Gn|3324536K|1",
            "bar|2|COMPLETED|4|00:00:10|00:00:30|2-00:00:00|4Gn||2",
            "batch|2.batch|COMPLETED|4|00:00:10|00:00:30||4Gn|115180K|2",
        ]
    )

    jobs = list(get_jobs_from_string(output))

    assert [job.name for job in jobs] == ["foo", "bar"]
    assert jobs[0].used_memory == 3324536 * 1024
    assert jobs[1].allocated_memory == 8 * 1024**3


def test_get_jobs_from_string_rejects_unexpected_columns() -> None:
    with pytest.raises(ValueError, match="Unexpected sacct columns"):
        list(get_jobs_from_string("JobID|JobName\n"))


def test_get_jobs_with_no_job_ids_returns_empty_iterator() -> None:
    assert list(get_jobs([])) == []


@patch("gwf_utilization.accounting.subprocess.run")
def test_call_sacct_uses_checked_text_mode(run: Mock) -> None:
    run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=f"{SACCT_HEADER}\nfoo|1|COMPLETED\n", stderr=""
    )

    assert _call_sacct("42") == "foo|1|COMPLETED"
    run.assert_called_once_with(
        [
            "sacct",
            "--format=JobName,JobID,State,NCPUS,Elapsed,TotalCPU,Timelimit,ReqMem,MaxRSS,NNodes",
            "--parsable2",
            "--jobs",
            "42",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
