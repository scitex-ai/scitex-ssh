#!/usr/bin/env python3
"""Tests for scitex_ssh._primitives — real ssh/scp argv via subprocess shim.

These exercise the production `subprocess.run(["ssh"/"scp", ...])` codepath
end to end: a fake `ssh`/`scp` on `$PATH` records the argv the production
code built, and we assert on it. No mocks — if the argv shape changes, the
test fails honestly.
"""

from __future__ import annotations

import shlex

import pytest

from scitex_ssh import (
    ProbeResult,
    SSHResult,
    copy_from,
    copy_to,
    exec_remote,
    probe_remote,
    sync_dir,
)


SAFE_TRANSPORT_DEFAULTS = [
    "-o",
    "ControlMaster=no",
    "-o",
    "ControlPath=none",
    "-o",
    "ClearAllForwardings=yes",
]


def test_exec_remote_builds_plain_ssh_argv_from_host_and_command(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="hi")
    # Act
    exec_remote("spartan", "hostname")
    # Assert
    assert subprocess_shim.argv("ssh") == [
        *SAFE_TRANSPORT_DEFAULTS,
        "spartan",
        "hostname",
    ]


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
    # Assert — caller opts are appended after the safe transport defaults,
    # since neither sets ControlMaster/ControlPath/ClearAllForwardings.
    assert subprocess_shim.argv("ssh") == [
        *SAFE_TRANSPORT_DEFAULTS,
        "-A",
        "-o",
        "StrictHostKeyChecking=no",
        "h",
        "cmd",
    ]


def test_exec_remote_respects_caller_controlmaster_override(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0)
    # Act
    exec_remote("h", "cmd", ssh_opts=["-o", "ControlMaster=auto"])
    # Assert — caller's explicit ControlMaster is kept, ours is not added
    argv = subprocess_shim.argv("ssh")
    assert argv.count("ControlMaster=auto") == 1 and "ControlMaster=no" not in argv


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
    # Assert — -A dropped (not relevant for scp); safe defaults prepended
    # (all -o pairs, so they survive the scp filter); -o K=V and -i /key kept
    assert subprocess_shim.argv("scp") == [
        "-r",
        *SAFE_TRANSPORT_DEFAULTS,
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
    assert subprocess_shim.argv("scp") == [
        *SAFE_TRANSPORT_DEFAULTS,
        "h:~/src",
        "/local/dest",
    ]


def test_sync_dir_push_puts_remote_dest_last(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("spartan", "/local/lib/", "~/lib/")
    # Assert
    assert subprocess_shim.argv("rsync") == [
        "-a",
        "--partial",
        "-e",
        "ssh " + " ".join(SAFE_TRANSPORT_DEFAULTS),
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
        "-e",
        "ssh " + " ".join(SAFE_TRANSPORT_DEFAULTS),
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
    # Assert — caller ssh_opts appended after the safe transport defaults
    argv = subprocess_shim.argv("rsync")
    expected = "ssh " + " ".join([*SAFE_TRANSPORT_DEFAULTS, "-o", "BatchMode=yes"])
    assert argv[argv.index("-e") + 1] == expected


def test_sync_dir_always_passes_e_flag_even_with_no_caller_ssh_opts(subprocess_shim):
    # Arrange
    subprocess_shim.install("rsync", rc=0)
    # Act
    sync_dir("h", "/l/", "~/r/")
    # Assert — the safe defaults mean -e is never omitted, unlike before
    assert "-e" in subprocess_shim.argv("rsync")


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


def test_probe_remote_targets_host_as_second_to_last_ssh_arg(subprocess_shim):
    # Arrange — safe transport defaults precede host/remote_cmd now
    subprocess_shim.install("ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\n")
    # Act
    probe_remote("spartan")
    # Assert
    assert subprocess_shim.argv("ssh")[-2] == "spartan"


def test_probe_remote_remote_command_echoes_the_marker(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\n")
    # Act
    probe_remote("spartan")
    # Assert
    assert "echo __SCITEX_SSH_PROBE_REACHABLE__" in subprocess_shim.argv("ssh")[-1]


def test_probe_remote_includes_safe_transport_defaults(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\n")
    # Act
    probe_remote("spartan")
    # Assert
    argv = subprocess_shim.argv("ssh")
    assert argv[: len(SAFE_TRANSPORT_DEFAULTS)] == SAFE_TRANSPORT_DEFAULTS


def test_probe_remote_marks_unreachable_on_nonzero_exit(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=255, stderr="Connection refused")
    # Act
    result = probe_remote("deadhost")
    # Assert
    assert result.reachable is False


def test_probe_remote_returns_empty_capabilities_when_unreachable(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=255, stderr="Connection refused")
    # Act
    result = probe_remote("deadhost", requires=["apptainer"])
    # Assert
    assert result.capabilities == {}


def test_probe_remote_marks_reachable_on_zero_exit_with_marker(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\n")
    # Act
    result = probe_remote("spartan")
    # Assert
    assert result.reachable is True


def test_probe_remote_parses_present_capability_by_order(subprocess_shim):
    # Arrange
    subprocess_shim.install(
        "ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nyes\n"
    )
    # Act
    result = probe_remote("spartan", requires=["apptainer"])
    # Assert
    assert result.capabilities == {"apptainer": True}


def test_probe_remote_parses_missing_capability_by_order(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nno\n")
    # Act
    result = probe_remote("spartan", requires=["apptainer"])
    # Assert
    assert result.capabilities == {"apptainer": False}


def test_probe_remote_tolerates_motd_noise_before_marker(subprocess_shim):
    # Arrange
    subprocess_shim.install(
        "ssh",
        rc=0,
        stdout="Welcome to Spartan\nMOTD line 2\n__SCITEX_SSH_PROBE_REACHABLE__\nyes\n",
    )
    # Act
    result = probe_remote("spartan", requires=["rsync"])
    # Assert
    assert result.reachable is True and result.capabilities == {"rsync": True}


def test_probe_remote_maps_multiple_requires_in_order(subprocess_shim):
    # Arrange
    subprocess_shim.install(
        "ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nyes\nno\n"
    )
    # Act
    result = probe_remote("spartan", requires=["rsync", "apptainer"])
    # Assert
    assert result.capabilities == {"rsync": True, "apptainer": False}


def test_probe_remote_shell_quotes_requirement_names(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nno\n")
    dangerous = "some tool; rm -rf /"
    # Act
    probe_remote("spartan", requires=[dangerous])
    # Assert — the requirement round-trips as ONE shell token, proving it
    # was quoted rather than word-split/executed as separate commands.
    remote_cmd = subprocess_shim.argv("ssh")[-1]
    assert dangerous in shlex.split(remote_cmd)


def test_probe_remote_returns_probeResult_instance(subprocess_shim):
    # Arrange
    subprocess_shim.install("ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\n")
    # Act
    result = probe_remote("spartan")
    # Assert
    assert isinstance(result, ProbeResult)


def test_probe_result_ok_true_when_reachable_and_no_requirements():
    # Arrange
    result = ProbeResult(reachable=True, capabilities={})
    # Act
    # Assert
    assert result.ok is True


def test_probe_result_ok_false_when_unreachable():
    # Arrange
    result = ProbeResult(reachable=False, capabilities={})
    # Act
    # Assert
    assert result.ok is False


def test_probe_result_ok_false_when_a_capability_is_missing():
    # Arrange
    result = ProbeResult(reachable=True, capabilities={"apptainer": False})
    # Act
    # Assert
    assert result.ok is False


def test_probe_result_has_reads_capability_by_name():
    # Arrange
    result = ProbeResult(reachable=True, capabilities={"apptainer": True})
    # Act
    # Assert
    assert result.has("apptainer") is True


def test_probe_result_has_defaults_to_false_for_unknown_name():
    # Arrange
    result = ProbeResult(reachable=True, capabilities={})
    # Act
    # Assert
    assert result.has("nope") is False


# EOF
