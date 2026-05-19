#!/usr/bin/env python3
"""Tests for scitex_ssh._primitives (mocked subprocess)."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from scitex_ssh import SSHResult, copy_from, copy_to, exec_remote


def _fake_completed(rc=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=[], returncode=rc, stdout=stdout, stderr=stderr
    )


def test_exec_remote_basic_command_args_equals_ssh_spartan_hostname():
    # Arrange
    # Arrange
    with patch(
        "scitex_ssh._primitives.subprocess.run",
        return_value=_fake_completed(0, "hi", ""),
    ) as m:
        r = exec_remote("spartan", "hostname")
    # Act
    args = m.call_args[0][0]
    # Act
    # Assert
    # Assert
    assert args == ["ssh", "spartan", "hostname"]


def test_exec_remote_basic_command_r_is_sshresult():
    # Arrange
    # Arrange
    with patch(
        "scitex_ssh._primitives.subprocess.run",
        return_value=_fake_completed(0, "hi", ""),
    ) as m:
        r = exec_remote("spartan", "hostname")
    # Act
    args = m.call_args[0][0]
    # Act
    # Assert
    # Assert
    assert isinstance(r, SSHResult)


def test_exec_remote_basic_command_r_success_and_r_stdout_hi():
    # Arrange
    # Arrange
    with patch(
        "scitex_ssh._primitives.subprocess.run",
        return_value=_fake_completed(0, "hi", ""),
    ) as m:
        r = exec_remote("spartan", "hostname")
    # Act
    args = m.call_args[0][0]
    # Act
    # Assert
    # Assert
    assert r.success and r.stdout == "hi"




def test_exec_remote_with_ssh_opts():
    # Arrange
    # Arrange
    with patch(
        "scitex_ssh._primitives.subprocess.run", return_value=_fake_completed()
    ) as m:
        exec_remote("h", "cmd", ssh_opts=["-A", "-o", "StrictHostKeyChecking=no"])
    # Act
    # Act
    args = m.call_args[0][0]
    # Assert
    # Assert
    assert args == ["ssh", "-A", "-o", "StrictHostKeyChecking=no", "h", "cmd"]


def test_exec_remote_check_raises_on_failure():
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    with patch(
        "scitex_ssh._primitives.subprocess.run",
        return_value=_fake_completed(1, "", "boom"),
    ):
        with pytest.raises(RuntimeError):
            exec_remote("h", "cmd", check=True)


def test_copy_to_recursive_and_opts():
    # Arrange
    # Arrange
    with patch(
        "scitex_ssh._primitives.subprocess.run", return_value=_fake_completed()
    ) as m:
        copy_to(
            "h",
            "/local/dir",
            "~/dest",
            recursive=True,
            ssh_opts=["-A", "-o", "K=V", "-i", "/key"],
        )
    # Act
    # Act
    args = m.call_args[0][0]
    # -A is dropped (not relevant for scp); -o K=V and -i /key kept
    # Assert
    # Assert
    assert args == ["scp", "-r", "-o", "K=V", "-i", "/key", "/local/dir", "h:~/dest"]


def test_copy_from_constructs_remote_source():
    # Arrange
    # Arrange
    with patch(
        "scitex_ssh._primitives.subprocess.run", return_value=_fake_completed()
    ) as m:
        copy_from("h", "~/src", "/local/dest")
    # Act
    # Act
    args = m.call_args[0][0]
    # Assert
    # Assert
    assert args == ["scp", "h:~/src", "/local/dest"]


# EOF
