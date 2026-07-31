from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pip_dependencies_do_not_require_conda_only_gwf() -> None:
    metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    dependencies = re.search(
        r"dependencies\s*=\s*\[(?P<dependencies>.*?)\]", metadata, flags=re.DOTALL
    )

    assert dependencies is not None
    assert '"gwf' not in dependencies["dependencies"].lower()


def test_conda_environment_provides_supported_gwf() -> None:
    environment = (ROOT / "environment.yml").read_text(encoding="utf-8")

    assert "- gwf >=2" in environment
