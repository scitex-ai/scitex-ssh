"""End-to-end smoke: every Python example under examples/ runs to completion.

Lives in tests/integration/ (not tests/examples/) because it cross-cuts every
example with a single glob; the per-example syntax-check smokes in
tests/examples/ provide finer-grained PS303 coverage.
"""

import subprocess
import sys
from pathlib import Path

EXAMPLES = sorted(Path(__file__).resolve().parents[2].joinpath("examples").glob("*.py"))


def test_examples_smoke_examples(tmp_path):
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    assert EXAMPLES, "No example scripts found under examples/"
    for ex in EXAMPLES:
        r = subprocess.run(
            [sys.executable, str(ex)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, (
            f"{ex.name} failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
        )
