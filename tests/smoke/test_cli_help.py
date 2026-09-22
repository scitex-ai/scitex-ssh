"""Smoke: the CLI launches and answers ``--help`` (PS-211).

Subprocess-driven via the real ``scitex-ssh`` console script (resolved
from ``sys.executable`` so this proves the installed entry point
resolves — an in-process call would not; note ``python -m scitex_ssh``
exposes a subset without the ``skills`` group, so the console script is
the faithful target). Hermetic: no network, no credentials, no writes
outside tmp dirs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke

CONSOLE_SCRIPT = str(Path(sys.executable).parent / "scitex-ssh")


def test_console_script_answers_help() -> None:
    # Arrange
    argv = [CONSOLE_SCRIPT, "--help"]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)

    # Assert
    assert (completed.returncode, "Usage:" in completed.stdout) == (0, True)


def test_skills_list_runs_offline() -> None:
    # Arrange
    argv = [CONSOLE_SCRIPT, "skills", "list"]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)

    # Assert
    assert (completed.returncode, "01_installation" in completed.stdout) == (0, True)
