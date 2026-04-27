"""Smoke test: every example script under examples/ runs to completion."""

import subprocess
import sys
from pathlib import Path

EXAMPLES = sorted(Path(__file__).parent.parent.joinpath("examples").glob("*.py"))


def test_examples_smoke(tmp_path):
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
