from __future__ import annotations

import json
from pathlib import Path

import pytest
from gwf.exceptions import GWFError

from gwf_utilization.main import load_tracked_jobs, pretty_size, pretty_time


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0, "00:00:00"), (65, "00:01:05"), (90061, "1-01:01:01")],
)
def test_pretty_time(seconds: int, expected: str) -> None:
    assert pretty_time(seconds) == expected


@pytest.mark.parametrize(
    ("size", "expected"),
    [(0, "0 B"), (1024, "1.0 KB"), (3 * 1024**2, "3.0 MB")],
)
def test_pretty_size(size: int, expected: str) -> None:
    assert pretty_size(size) == expected


def test_load_tracked_jobs_returns_empty_mapping_when_state_file_is_missing(
    tmp_path: Path,
) -> None:
    assert load_tracked_jobs(tmp_path) == {}


def test_load_tracked_jobs_reads_valid_state_file(tmp_path: Path) -> None:
    state_directory = tmp_path / ".gwf"
    state_directory.mkdir()
    (state_directory / "slurm-backend-tracked.json").write_text(
        json.dumps({"align": "12345"}), encoding="utf-8"
    )

    assert load_tracked_jobs(tmp_path) == {"align": "12345"}


def test_load_tracked_jobs_rejects_invalid_state_file(tmp_path: Path) -> None:
    state_directory = tmp_path / ".gwf"
    state_directory.mkdir()
    (state_directory / "slurm-backend-tracked.json").write_text(
        json.dumps(["12345"]), encoding="utf-8"
    )

    with pytest.raises(GWFError, match="Invalid tracked-job state file"):
        load_tracked_jobs(tmp_path)
