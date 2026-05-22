#!/usr/bin/env python3
"""Tests for scitex_ssh._primitives — exec_remote / copy_to / copy_from.

Uses the production ``runner`` injection kwarg with a hand-rolled
``FakeRunner`` (from ``tests/conftest.py``) so each test exercises the
real production codepath without ``unittest.mock``.
"""

from __future__ import annotations

import pytest

from scitex_ssh import SSHResult, copy_from, copy_to, exec_remote


# ---------------------------------------------------------------------
# exec_remote
# ---------------------------------------------------------------------


def test_exec_remote_basic_command_invokes_ssh_with_host_and_command(fake_runner):
    # Arrange
    fake_runner.stdout = "hi"
    # Act
    exec_remote("spartan", "hostname", runner=fake_runner)
    # Assert
    assert fake_runner.last_cmd == ["ssh", "spartan", "hostname"]


def test_exec_remote_basic_command_returns_sshresult_instance(fake_runner):
    # Arrange
    fake_runner.stdout = "hi"
    # Act
    result = exec_remote("spartan", "hostname", runner=fake_runner)
    # Assert
    assert isinstance(result, SSHResult)


def test_exec_remote_basic_command_propagates_stdout_into_result(fake_runner):
    # Arrange
    fake_runner.stdout = "hi"
    # Act
    result = exec_remote("spartan", "hostname", runner=fake_runner)
    # Assert
    assert result.stdout == "hi"


def test_exec_remote_basic_command_marks_zero_returncode_as_success(fake_runner):
    # Arrange
    fake_runner.returncode = 0
    # Act
    result = exec_remote("spartan", "hostname", runner=fake_runner)
    # Assert
    assert result.success is True


def test_exec_remote_with_ssh_opts_passes_them_through_verbatim(fake_runner):
    # Arrange
    opts = ["-A", "-o", "StrictHostKeyChecking=no"]
    # Act
    exec_remote("h", "cmd", ssh_opts=opts, runner=fake_runner)
    # Assert
    assert fake_runner.last_cmd == ["ssh", *opts, "h", "cmd"]


def test_exec_remote_check_raises_runtimeerror_on_nonzero_returncode(fake_runner):
    # Arrange
    fake_runner.returncode = 1
    fake_runner.stderr = "boom"
    # Act
    ctx = pytest.raises(RuntimeError)
    # Assert
    with ctx:
        exec_remote("h", "cmd", check=True, runner=fake_runner)


# ---------------------------------------------------------------------
# copy_to
# ---------------------------------------------------------------------


def test_copy_to_recursive_with_opts_builds_expected_scp_argv(fake_runner):
    # Arrange
    opts = ["-A", "-o", "K=V", "-i", "/key"]
    # Act
    copy_to(
        "h",
        "/local/dir",
        "~/dest",
        recursive=True,
        ssh_opts=opts,
        runner=fake_runner,
    )
    # Assert
    # `-A` is irrelevant to scp and dropped; `-o K=V` and `-i /key` survive.
    assert fake_runner.last_cmd == [
        "scp",
        "-r",
        "-o",
        "K=V",
        "-i",
        "/key",
        "/local/dir",
        "h:~/dest",
    ]


# ---------------------------------------------------------------------
# copy_from
# ---------------------------------------------------------------------


def test_copy_from_constructs_host_prefixed_remote_source(fake_runner):
    # Arrange
    # Act
    copy_from("h", "~/src", "/local/dest", runner=fake_runner)
    # Assert
    assert fake_runner.last_cmd == ["scp", "h:~/src", "/local/dest"]


# EOF
