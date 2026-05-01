#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-ssh/tests/examples/test_01_check_status.py

"""Smoke test for examples/01_check_status.sh.

Per scitex-dev audit-project PS303: every example must have a matching
test under tests/examples/. For shell examples, a syntax check (`bash -n`)
proves the script parses cleanly without executing commands.
"""

import os
import subprocess
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "01_check_status.sh"


def test_example_exists():
    assert EXAMPLE.exists(), f"missing example: {EXAMPLE}"


def test_executable_bit():
    assert os.access(EXAMPLE, os.X_OK), f"not executable: {EXAMPLE}"


def test_bash_syntax():
    subprocess.run(["bash", "-n", str(EXAMPLE)], check=True)
