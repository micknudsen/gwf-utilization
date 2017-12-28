import pytest

from gwf_utilization.accounting import Job, get_jobs_from_string


def test_get_jobs_from_string():
    output = (
        "JobID|JobName|State|NCPUS|CPUTime|Timelimit|ReqMem|MaxRSS|NNodes\n"
        "4280398|R|COMPLETED|1|00:06:10|06:00:00|8Gn||1\n"
        "4280398.batch|batch|COMPLETED|1|00:06:10||8Gn|3324536K|1\n"
        "4302760|python|COMPLETED|4|00:00:30|2-00:00:00|4Gn||2\n"
        "4302760.batch|batch|COMPLETED|4|00:00:30||4Gn|115180K|2\n"
    )

    jobs = list(get_jobs_from_string(output))
    assert len(jobs) == 2


def test_job_utilization():
    job = Job(
        cores=1,
        nodes=1,
        allocated_time=60,
        used_time=30,
        allocated_memory=512,
        used_memory=256
    )

    assert job.cpu_utilization == 0.5
    assert job.memory_utilization == 0.5

    job = Job(
        cores=16,
        nodes=1,
        allocated_time=60,
        used_time=480,
        allocated_memory=512,
        used_memory=128
    )

    assert job.cpu_utilization == 0.5
    assert job.memory_utilization == 0.25


