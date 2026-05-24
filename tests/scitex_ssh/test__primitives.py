#!/usr/bin/env python3
"""Tests for scitex_ssh._primitives — real ssh/scp argv via subprocess shim.

These exercise the production `subprocess.run(["ssh"/"scp", ...])` codepath
end to end: a fake `ssh`/`scp` on `$PATH` records the argv the production
code built, and we assert on it. No mocks — if the argv shape changes, the
test fails honestly.
"""

from __future__ import annotations

import pytest

from scitex_ssh import SSHResult, copy_from, copy_to, exec_remote


def test_exec_remote_builds_plain_ssh_argv_from_host_and_command(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="hi")
    # Act
    exec_remote("spartan", "hostname")
    # Assert
    assert subprocess_shim.argv("ssh") == ["spartan", "hostname"]


def test_exec_remote_returns_sshresult_instance(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="hi")
    # Act
    result = exec_remote("spartan", "hostname")
    # Assert
    assert isinstance(result, SSHResult)


def test_exec_remote_marks_zero_exit_as_success(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="hi")
    # Act
    result = exec_remote("spartan", "hostname")
    # Assert
    assert result.success is True


def test_exec_remote_captures_remote_stdout(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="hi")
    # Act
    result = exec_remote("spartan", "hostname")
    # Assert
    assert result.stdout == "hi"


def test_exec_remote_passes_ssh_opts_through_verbatim(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0)
    # Act
    exec_remote("h", "cmd", ssh_opts=["-A", "-o", "StrictHostKeyChecking=no"])
    # Assert
    assert subprocess_shim.argv("ssh") == [
        "-A",
        "-o",
        "StrictHostKeyChecking=no",
        "h",
        "cmd",
    ]


def test_exec_remote_raises_runtimeerror_when_check_and_nonzero_exit(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=1, stderr="boom")
    # Act
    ctx = pytest.raises(RuntimeError)
    # Assert
    with ctx:
        exec_remote("h", "cmd", check=True)


def test_copy_to_recursive_drops_basic_flags_and_keeps_o_and_i_opts(subprocess_shim):
    # Arrange
    subprocess_shim.install("scp", rc=0)
    # Act
    copy_to(
        "h",
        "/local/dir",
        "~/dest",
        recursive=True,
        ssh_opts=["-A", "-o", "K=V", "-i", "/key"],
    )
    # Assert — -A dropped (not relevant for scp); -o K=V and -i /key kept
    assert subprocess_shim.argv("scp") == [
        "-r",
        "-o",
        "K=V",
        "-i",
        "/key",
        "/local/dir",
        "h:~/dest",
    ]


def test_copy_from_constructs_remote_source_argv(subprocess_shim):
    # Arrange
    subprocess_shim.install("scp", rc=0)
    # Act
    copy_from("h", "~/src", "/local/dest")
    # Assert
    assert subprocess_shim.argv("scp") == ["h:~/src", "/local/dest"]


# EOF
