"""End-to-end smoke: every Python example under examples/ runs to completion.

Lives in tests/integration/ (not tests/examples/) because it cross-cuts every
example with a single glob; the per-example syntax-check smokes in
tests/examples/ provide finer-grained PS303 coverage.
"""

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(Path(__file__).resolve().parents[2].joinpath("examples").glob("*.py"))


def test_examples_directory_is_not_empty():
    # Arrange
    examples = EXAMPLES
    # Act
    count = len(examples)
    # Assert
    assert count > 0, "No example scripts found under examples/"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_example_runs_to_completion(example, tmp_path):
    # Arrange
    cmd = [sys.executable, str(example)]
    # Act
    result = subprocess.run(
        cmd, cwd=tmp_path, capture_output=True, text=True, timeout=120
    )
    # Assert
    assert result.returncode == 0, (
        f"{example.name} failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
