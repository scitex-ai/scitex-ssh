"""The installed CLI vocabulary must retain its canonical source bytes."""

import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def vocabulary_artifacts(tmp_path):
    """Build the real wheel from its sdist using the package's Hatch config."""
    root = Path(__file__).resolve().parents[2]
    workspace = tmp_path
    source = workspace / "source"
    source.mkdir()
    shutil.copytree(
        root / "src", source / "src", ignore=shutil.ignore_patterns("__pycache__")
    )
    for name in ["pyproject.toml", "README.md"]:
        shutil.copy2(root / name, source / name)
    dictionary = source / ".scitex/dev/cli-audit-dict.yaml"
    dictionary.parent.mkdir(parents=True)
    shutil.copy2(root / ".scitex/dev/cli-audit-dict.yaml", dictionary)
    destination = workspace / "dist"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--outdir",
            str(destination),
            str(source),
        ],
        check=True,
    )
    return (
        dictionary.read_bytes(),
        next(destination.glob("*.whl")),
        next(destination.glob("*.tar.gz")),
    )


def test_sdist_rebuilt_wheel_contains_the_exact_canonical_cli_vocabulary(
    vocabulary_artifacts,
):
    # Arrange
    canonical, wheel, _ = vocabulary_artifacts
    # Act
    with zipfile.ZipFile(wheel) as archive:
        observed = archive.read("scitex_ssh/_cli_audit_dict.yaml")
    # Assert
    assert observed == canonical


def test_sdist_contains_the_canonical_dictionary_for_future_rebuilds(
    vocabulary_artifacts,
):
    # Arrange
    canonical, _, sdist = vocabulary_artifacts
    # Act
    with tarfile.open(sdist) as archive:
        member = next(
            m
            for m in archive.getmembers()
            if m.name.endswith("/.scitex/dev/cli-audit-dict.yaml")
        )
        observed = archive.extractfile(member).read()
    # Assert
    assert observed == canonical


def test_ssh_protocol_is_declared_as_a_namespace_noun():
    # Arrange
    dictionary = Path(__file__).resolve().parents[2] / ".scitex/dev/cli-audit-dict.yaml"
    # Act
    nouns = yaml.safe_load(dictionary.read_text()).get("nouns", [])
    # Assert
    assert "ssh" in nouns
