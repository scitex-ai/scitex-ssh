#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-ssh/tests/examples/test_03_remove_tunnel.py

"""Smoke test for examples/03_remove_tunnel.sh.

Per scitex-dev audit-project PS303: every example must have a matching
test under tests/examples/. For shell examples, a syntax check (`bash -n`)
proves the script parses cleanly without executing commands.
"""

import os
import subprocess
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "03_remove_tunnel.sh"


def test_example_exists_example_exists():
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    assert EXAMPLE.exists(), f"missing example: {EXAMPLE}"


def test_executable_bit_os_access_example_os_x_ok():
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    assert os.access(EXAMPLE, os.X_OK), f"not executable: {EXAMPLE}"


def test_bash_syntax_r_returncode_equals_n_0():
    # Arrange
    # Act
    # Arrange
    # Act
    _r = subprocess.run(["bash", "-n", str(EXAMPLE)], check=True)
    # Assert
    # Assert
    assert _r.returncode == 0
