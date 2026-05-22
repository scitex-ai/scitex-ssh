"""End-to-end smoke: every Python example under examples/ runs to completion.

Lives in tests/integration/ (not tests/examples/) because it cross-cuts every
example with a single glob; the per-example syntax-check smokes in
tests/examples/ provide finer-grained PS303 coverage.

Implementation note — TQ007 (one assert per test) splits the original
combined "examples exist AND each example exits zero" check into two
discrete tests: one for the discovery contract, one parametrized per
example for the actual run.
"""

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(Path(__file__).resolve().parents[2].joinpath("examples").glob("*.py"))


def test_examples_directory_discovers_at_least_one_script() -> None:
    """Catch the silent-empty failure mode where `examples/` is wiped or
    misnamed: parametrized per-example tests below would all skip-silent."""
    # Arrange
    # Act
    discovered = list(EXAMPLES)
    # Assert
    assert discovered, "No example scripts found under examples/"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_example_script_runs_with_zero_exit_code(example: Path, tmp_path: Path) -> None:
    """Each example script must run to completion. Real subprocess against
    the live interpreter — exit code is the load-bearing signal."""
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
