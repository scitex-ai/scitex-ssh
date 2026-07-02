#!/usr/bin/env python3
"""Tests for scitex_ssh._primitives — real ssh/scp argv via subprocess shim.

These exercise the production `subprocess.run(["ssh"/"scp", ...])` codepath
end to end: a fake `ssh`/`scp` on `$PATH` records the argv the production
code built, and we assert on it. No mocks — if the argv shape changes, the
test fails honestly.
"""

from __future__ import annotations

import pytest

from scitex_ssh import SSHResult, copy_from, copy_to, exec_remote, sync_dir


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


def test_sync_dir_push_puts_remote_dest_last(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("spartan", "/local/lib/", "~/lib/")
    # Assert
    assert subprocess_shim.argv("rsync") == [
        "-a",
        "--partial",
        "/local/lib/",
        "spartan:~/lib/",
    ]


def test_sync_dir_pull_puts_remote_src_first(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("spartan", "/local/lib/", "~/lib/", direction="pull")
    # Assert
    assert subprocess_shim.argv("rsync") == [
        "-a",
        "--partial",
        "spartan:~/lib/",
        "/local/lib/",
    ]


def test_sync_dir_renders_each_exclude_as_a_flag(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("h", "/l/", "~/r/", exclude=["index.db", "*.db-wal"])
    # Assert
    argv = subprocess_shim.argv("rsync")
    assert "--exclude=index.db" in argv and "--exclude=*.db-wal" in argv


def test_sync_dir_omits_delete_by_default(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("h", "/l/", "~/r/")
    # Assert
    assert "--delete" not in subprocess_shim.argv("rsync")


def test_sync_dir_adds_delete_when_requested(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("h", "/l/", "~/r/", delete=True)
    # Assert
    assert "--delete" in subprocess_shim.argv("rsync")


def test_sync_dir_wires_ssh_opts_into_e_flag(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("h", "/l/", "~/r/", ssh_opts=["-o", "BatchMode=yes"])
    # Assert
    argv = subprocess_shim.argv("rsync")
    assert argv[argv.index("-e") + 1] == "ssh -o BatchMode=yes"


def test_sync_dir_appends_extra_opts_verbatim(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("h", "/l/", "~/r/", extra_opts=["--checksum", "--mkpath"])
    # Assert
    argv = subprocess_shim.argv("rsync")
    assert "--checksum" in argv and "--mkpath" in argv


def test_sync_dir_returns_sshresult_instance(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0, stdout="sent")
    # Act
    result = sync_dir("h", "/l/", "~/r/")
    # Assert
    assert isinstance(result, SSHResult)


def test_sync_dir_rejects_unknown_direction():
    # Arrange
    # Act
    ctx = pytest.raises(ValueError)
    # Assert
    with ctx:
        sync_dir("h", "/l/", "~/r/", direction="sideways")


# EOF
