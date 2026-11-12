"""Regression tests for the subprocess-coverage `.pth` shim in conftest.

The shim is executed by EVERY interpreter started from the venv it is
installed into, so two properties are load-bearing:

1. It must be a single `import`-prefixed line — `.pth` files execute only
   lines starting with `import`; anything else is read as a sys.path entry.
   A multi-line `if` block is silently dead code.
2. It must not import `coverage` unless coverage is actually starting, or
   every process in a coverage-less venv dumps a traceback to stderr.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _load_conftest():
    """Import the tests/ conftest by path — `tests/` is not a package, so a
    plain `import conftest` is not resolvable under every rootdir."""
    path = Path(__file__).resolve().parent.parent / "conftest.py"
    spec = importlib.util.spec_from_file_location("_ssh_tests_conftest", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CONFTEST = _load_conftest()
_SUBPROCESS_COVERAGE_SHIM = _CONFTEST._SUBPROCESS_COVERAGE_SHIM


def test_shim_is_not_installed_outside_the_project_venv(tmp_path):
    # Arrange
    foreign = tmp_path / "opt" / "shared-venv" / "site-packages"
    foreign.mkdir(parents=True)

    # Act
    _CONFTEST._ensure_subprocess_coverage_shim(purelib=foreign)

    # Assert
    assert list(foreign.iterdir()) == []


def test_shim_is_a_single_line():
    # Arrange
    lines = [ln for ln in _SUBPROCESS_COVERAGE_SHIM.splitlines() if ln.strip()]

    # Act
    count = len(lines)

    # Assert
    assert count == 1


def test_shim_line_is_executed_by_pth_loader():
    # Arrange
    (line,) = [ln for ln in _SUBPROCESS_COVERAGE_SHIM.splitlines() if ln.strip()]

    # Act
    executed = line.startswith("import")

    # Assert
    assert executed


def test_shim_is_silent_without_coverage_env(tmp_path):
    # Arrange
    script = tmp_path / "run_shim.py"
    script.write_text(_SUBPROCESS_COVERAGE_SHIM)
    env = {"PATH": "/usr/bin:/bin"}

    # Act
    proc = subprocess.run(
        [sys.executable, "-S", str(script)],
        capture_output=True,
        text=True,
        env=env,
    )

    # Assert
    assert proc.stderr == ""
