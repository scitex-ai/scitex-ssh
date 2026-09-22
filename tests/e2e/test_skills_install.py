"""E2E: `skills install` copies/links the real skills tree (PS-212).

Full story through the real ``scitex-ssh`` console script in a
subprocess: install the bundled `_skills/scitex-ssh/` tree into a tmp
dir (never the real `~/.scitex`), then check the landed files. No
network, no credentials.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e

CONSOLE_SCRIPT = str(Path(sys.executable).parent / "scitex-ssh")


def test_skills_install_copy_lands_files(tmp_path: Path) -> None:
    # Arrange
    dest = tmp_path / "skills-copy"
    argv = [
        CONSOLE_SCRIPT,
        "skills",
        "install",
        "--no-link",
        "--dest",
        str(dest),
    ]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=60)

    # Assert
    landed = dest / "scitex-ssh"
    assert (
        completed.returncode,
        (landed / "SKILL.md").is_file(),
        (landed / "01_installation.md").is_file(),
    ) == (0, True, True)


def test_skills_install_default_links_tree(tmp_path: Path) -> None:
    # Arrange
    dest = tmp_path / "skills-link"
    argv = [
        CONSOLE_SCRIPT,
        "skills",
        "install",
        "--dest",
        str(dest),
    ]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=60)

    # Assert
    assert (completed.returncode, (dest / "scitex-ssh").is_symlink()) == (0, True)
