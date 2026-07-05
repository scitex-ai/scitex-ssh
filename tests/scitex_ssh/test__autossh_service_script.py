#!/usr/bin/env python3
"""Tests for the bundled setup-autossh-service.sh reverse-tunnel unit.

No mocks: asserts directly on the shipped script text (resolved the same way
production does, via ``scitex_ssh._SCRIPTS_DIR``). Locks in the keepalive /
ExitOnForwardFailure options that keep a reverse -R tunnel from silently
sitting on a dead forward after a network blip.
"""

from __future__ import annotations

import os

import scitex_ssh


def _execstart_line() -> str:
    """Return the ExecStart line of the bundled autossh service script."""
    path = os.path.join(scitex_ssh._SCRIPTS_DIR, "setup-autossh-service.sh")
    with open(path) as fh:
        for line in fh:
            if line.lstrip().startswith("ExecStart="):
                return line.strip()
    raise AssertionError("no ExecStart line found in setup-autossh-service.sh")


class TestAutosshExecStart:
    def test_sets_server_alive_interval(self):
        # Arrange
        line = _execstart_line()
        # Act
        # Assert
        assert "ServerAliveInterval=15" in line

    def test_sets_server_alive_count_max(self):
        # Arrange
        line = _execstart_line()
        # Act
        # Assert
        assert "ServerAliveCountMax=3" in line

    def test_sets_exit_on_forward_failure(self):
        # Arrange
        line = _execstart_line()
        # Act
        # Assert
        assert "ExitOnForwardFailure=yes" in line

    def test_still_defines_reverse_forward(self):
        # Arrange
        line = _execstart_line()
        # Act
        # Assert
        assert "-R ${PORT}:localhost:22" in line

    def test_keeps_autossh_monitor_port_disabled(self):
        # Arrange — -M 0 delegates liveness to ssh's ServerAlive (regression guard).
        line = _execstart_line()
        # Act
        # Assert
        assert "-M 0" in line


# EOF
