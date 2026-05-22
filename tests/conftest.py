"""Pytest fixtures and rootdir marker for this package.

An empty conftest.py at tests/ is the canonical SciTeX
convention (audit-project PS208) — it pins the pytest
rootdir and gives downstream fixtures a home.

Also wires subprocess coverage: see
05_development_06_subprocess-coverage.md. `os.environ.setdefault`
would be a no-op because pytest-cov has already set
COVERAGE_FILE by the time conftest is loaded.

Shared test fakes (no-mocks discipline — 02_package_12_no-mocks.md):
- ``FakeRunner`` — hand-rolled ``subprocess.run`` stand-in that
  records every call and returns a configurable
  ``subprocess.CompletedProcess``. Replaces every
  ``unittest.mock.patch('subprocess.run')`` idiom that previously
  haunted the test tree.
- ``env_save_restore`` — yield-based fixture that snapshots and
  restores ``os.environ`` mutations across a test. Replaces
  ``monkeypatch.setenv``.
"""

from __future__ import annotations

import os
import subprocess
import sysconfig
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

os.environ["COVERAGE_PROCESS_START"] = str(_PROJECT_ROOT / "pyproject.toml")
os.environ["COVERAGE_FILE"] = str(_PROJECT_ROOT / ".coverage")


def _ensure_subprocess_coverage_shim() -> None:
    """Drop an idempotent `.pth` file in site-packages that auto-starts
    coverage in every child Python interpreter via
    `coverage.process_startup()`.
    """
    purelib = Path(sysconfig.get_paths()["purelib"])
    pth = purelib / "_scitex_ssh_subprocess_coverage.pth"
    shim = (
        "import os, coverage\n"
        "if os.environ.get('COVERAGE_PROCESS_START'):\n"
        "    coverage.process_startup()\n"
    )
    try:
        if not pth.exists() or pth.read_text() != shim:
            pth.write_text(shim)
    except OSError:
        # site-packages may be read-only (e.g. system Python); silently
        # skip — local dev venvs are writable and that's where this matters.
        pass


_ensure_subprocess_coverage_shim()


# ---------------------------------------------------------------------
# Shared no-mocks fakes
# ---------------------------------------------------------------------


@dataclass
class FakeRunner:
    """Hand-rolled stand-in for ``subprocess.run``.

    Records every call (positional ``cmd`` plus kwargs) so tests can
    observe what production *actually* invoked, and returns a
    configurable ``subprocess.CompletedProcess`` so tests can stage
    success / failure paths. Real, honest, mock-free.
    """

    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    side_effect: Exception | None = None
    calls: list[tuple[list[str], dict[str, Any]]] = field(default_factory=list)

    def __call__(self, cmd, **kwargs) -> subprocess.CompletedProcess:
        # Coerce cmd to a plain list so test assertions don't have to
        # care whether production passed a tuple or a list.
        self.calls.append((list(cmd), dict(kwargs)))
        if self.side_effect is not None:
            raise self.side_effect
        return subprocess.CompletedProcess(
            args=list(cmd),
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def last_cmd(self) -> list[str]:
        assert self.calls, "FakeRunner was never called"
        return self.calls[-1][0]


@pytest.fixture
def fake_runner() -> FakeRunner:
    """Per-test ``FakeRunner`` with a default success result."""
    return FakeRunner()


@pytest.fixture
def env_save_restore():
    """Yield-based snapshot/restore of ``os.environ`` mutations.

    Replaces ``monkeypatch.setenv`` — tests mutate ``os.environ``
    inside the ``with``-block and the original mapping is restored
    on teardown, regardless of test outcome.
    """
    saved = dict(os.environ)
    try:
        yield os.environ
    finally:
        os.environ.clear()
        os.environ.update(saved)
