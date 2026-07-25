from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def _extract_version(path: Path, pattern: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text, flags=re.MULTILINE)
    assert match is not None, f"Could not find version in {path}"
    return match.group(1)


def test_version_is_synced_across_code_and_packaging() -> None:
    versions = {
        "pyproject": _extract_version(
            ROOT / "pyproject.toml",
            r'^version\s*=\s*"([^"]+)"$',
        ),
        "conda_recipe": _extract_version(
            ROOT / "conda-recipe" / "meta.yaml",
            r'^\{\%\s*set\s+version\s*=\s*"([^"]+)"\s*\%\}$',
        ),
        "package_code": _extract_version(
            ROOT / "src" / "gwf_utilization" / "__init__.py",
            r'^__version__\s*=\s*"([^"]+)"$',
        ),
    }

    assert len(set(versions.values())) == 1, f"Version mismatch: {versions}"
