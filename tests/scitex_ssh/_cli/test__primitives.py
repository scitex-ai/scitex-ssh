#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._primitives — exec/copy/attach CLI commands.

No mocks. Pure helpers are tested directly; exec/copy invoke the real
`exec_remote`/`copy_to`/`copy_from` against a fake ssh/scp on $PATH
(subprocess_shim); attach runs the real CLI as a subprocess so its
`os.execvp` replaces the child, not pytest.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from click.testing import CliRunner

from scitex_ssh._cli._primitives import (
    _split_host_path,
    _split_opts,
    attach_cmd,
    copy_cmd,
    exec_cmd,
    probe_cmd,
    sync_cmd,
)


class TestSplitOpts:
    def test_none_returns_empty_list(self):
        # Arrange
        # Act
        result = _split_opts(None)
        # Assert
        assert result == []

    def test_empty_string_returns_empty_list(self):
        # Arrange
        # Act
        result = _split_opts("")
        # Assert
        assert result == []

    def test_shell_quoted_string_splits_into_tokens(self):
        # Arrange
        # Act
        result = _split_opts("-A -o StrictHostKeyChecking=no")
        # Assert
        assert result == ["-A", "-o", "StrictHostKeyChecking=no"]


class TestSplitHostPath:
    def test_remote_host_path_splits_into_host_and_path(self):
        # Arrange
        # Act
        result = _split_host_path("myhost:/tmp/file")
        # Assert
        assert result == ("myhost", "/tmp/file")

    def test_absolute_local_path_has_no_host(self):
        # Arrange
        # Act
        result = _split_host_path("/tmp/file")
        # Assert
        assert result == (None, "/tmp/file")

    def test_relative_local_path_has_no_host(self):
        # Arrange
        # Act
        result = _split_host_path("./file")
        # Assert
        assert result == (None, "./file")

    def test_bare_local_filename_has_no_host(self):
        # Arrange — no colon → local.
        # Act
        result = _split_host_path("file.txt")
        # Assert
        assert result == (None, "file.txt")

    def test_host_containing_slash_is_treated_as_local(self):
        # Arrange — a "host" with `/` is not a real host (fallback safety net).
        # Act
        result = _split_host_path("foo/bar:baz")
        # Assert
        assert result == (None, "foo/bar:baz")


class TestExecCmd:
    def test_dry_run_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Assert
        assert result.exit_code == 0

    def test_dry_run_output_announces_dry_run(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Assert
        assert "DRY RUN" in result.output

    def test_dry_run_output_names_the_host(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Assert
        assert "myhost" in result.output

    def test_exec_against_fake_ssh_exits_zero(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=0, stdout="ok\n")
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a"])
        # Assert
        assert result.exit_code == 0

    def test_exec_streams_remote_stdout_to_output(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=0, stdout="ok\n")
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a"])
        # Assert
        assert "ok" in result.output

    def test_exec_propagates_nonzero_returncode(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=7, stderr="boom\n")
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "false"])
        # Assert
        assert result.exit_code == 7

    def test_exec_streams_remote_stderr_to_output(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=7, stderr="boom\n")
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "false"])
        # Assert
        assert "boom" in result.output


class TestCopyCmd:
    def test_dry_run_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            copy_cmd, ["local.txt", "myhost:/tmp/local.txt", "--dry-run"]
        )
        # Assert
        assert result.exit_code == 0

    def test_dry_run_output_announces_dry_run(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            copy_cmd, ["local.txt", "myhost:/tmp/local.txt", "--dry-run"]
        )
        # Assert
        assert "DRY RUN" in result.output

    def test_local_to_local_copy_exits_two(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["./a", "./b"])
        # Assert
        assert result.exit_code == 2

    def test_local_to_local_copy_reports_host_path_required(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["./a", "./b"])
        # Assert
        assert "must be HOST:PATH" in result.output

    def test_remote_to_remote_copy_exits_two(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["host1:/a", "host2:/b"])
        # Assert
        assert result.exit_code == 2

    def test_remote_to_remote_copy_reports_unsupported(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["host1:/a", "host2:/b"])
        # Assert
        assert "remote-to-remote" in result.output

    def test_copy_to_remote_exits_zero(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("scp", rc=0)
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["./local.txt", "myhost:/tmp/local.txt"])
        # Assert
        assert result.exit_code == 0

    def test_copy_to_remote_invokes_scp_once(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("scp", rc=0)
        runner = CliRunner()
        # Act
        runner.invoke(copy_cmd, ["./local.txt", "myhost:/tmp/local.txt"])
        # Assert
        assert subprocess_shim.call_count("scp") == 1

    def test_copy_from_remote_exits_zero(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("scp", rc=0)
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["myhost:/etc/hostname", "./hostname"])
        # Assert
        assert result.exit_code == 0

    def test_copy_from_remote_builds_remote_source_argv(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("scp", rc=0)
        runner = CliRunner()
        # Act
        runner.invoke(copy_cmd, ["myhost:/etc/hostname", "./hostname"])
        # Assert
        assert subprocess_shim.argv("scp") == ["myhost:/etc/hostname", "./hostname"]


class TestSyncCmd:
    def test_dry_run_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            sync_cmd, ["./lib/", "spartan:~/lib/", "--dry-run"]
        )
        # Assert
        assert result.exit_code == 0

    def test_dry_run_announces_push_direction(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            sync_cmd, ["./lib/", "spartan:~/lib/", "--dry-run"]
        )
        # Assert
        assert "push" in result.output

    def test_local_to_local_sync_exits_two(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(sync_cmd, ["./a/", "./b/"])
        # Assert
        assert result.exit_code == 2

    def test_remote_to_remote_sync_reports_unsupported(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(sync_cmd, ["h1:/a/", "h2:/b/"])
        # Assert
        assert "remote-to-remote" in result.output

    def test_push_invokes_rsync_once(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("rsync", rc=0)
        runner = CliRunner()
        # Act
        runner.invoke(sync_cmd, ["./lib/", "spartan:~/lib/"])
        # Assert
        assert subprocess_shim.call_count("rsync") == 1

    def test_push_builds_remote_dest_argv(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("rsync", rc=0)
        runner = CliRunner()
        # Act
        runner.invoke(sync_cmd, ["./lib/", "spartan:~/lib/"])
        # Assert
        argv = subprocess_shim.argv("rsync")
        assert argv[-2:] == ["./lib/", "spartan:~/lib/"]

    def test_exclude_options_reach_rsync(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("rsync", rc=0)
        runner = CliRunner()
        # Act
        runner.invoke(
            sync_cmd,
            ["./lib/", "spartan:~/lib/", "--exclude", "index.db", "--exclude", "*.db-wal"],
        )
        # Assert
        argv = subprocess_shim.argv("rsync")
        assert "--exclude=index.db" in argv and "--exclude=*.db-wal" in argv

    def test_propagates_nonzero_returncode(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("rsync", rc=23, stderr="partial\n")
        runner = CliRunner()
        # Act
        result = runner.invoke(sync_cmd, ["./lib/", "spartan:~/lib/"])
        # Assert
        assert result.exit_code == 23


class TestProbeCmd:
    def test_reachable_no_requirements_exits_zero(self, subprocess_shim):
        # Arrange
        subprocess_shim.install(
            "ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\n"
        )
        runner = CliRunner()
        # Act
        result = runner.invoke(probe_cmd, ["spartan"])
        # Assert
        assert result.exit_code == 0

    def test_unreachable_exits_two(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=255, stderr="Connection refused")
        runner = CliRunner()
        # Act
        result = runner.invoke(probe_cmd, ["deadhost"])
        # Assert
        assert result.exit_code == 2

    def test_unreachable_reports_host_on_stderr(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=255, stderr="Connection refused")
        runner = CliRunner()
        # Act
        result = runner.invoke(probe_cmd, ["deadhost"])
        # Assert
        assert "deadhost" in result.output

    def test_missing_capability_exits_one(self, subprocess_shim):
        # Arrange
        subprocess_shim.install(
            "ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nno\n"
        )
        runner = CliRunner()
        # Act
        result = runner.invoke(probe_cmd, ["spartan", "--requires", "apptainer"])
        # Assert
        assert result.exit_code == 1

    def test_present_capability_reported_in_output(self, subprocess_shim):
        # Arrange
        subprocess_shim.install(
            "ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nyes\n"
        )
        runner = CliRunner()
        # Act
        result = runner.invoke(probe_cmd, ["spartan", "--requires", "apptainer"])
        # Assert
        assert "apptainer" in result.output and "present" in result.output

    def test_json_output_is_valid_json_with_expected_keys(self, subprocess_shim):
        # Arrange
        subprocess_shim.install(
            "ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nyes\n"
        )
        runner = CliRunner()
        # Act
        result = runner.invoke(
            probe_cmd, ["spartan", "--requires", "apptainer", "--json"]
        )
        # Assert
        payload = json.loads(result.output)
        assert payload == {
            "host": "spartan",
            "reachable": True,
            "capabilities": {"apptainer": True},
            "ok": True,
        }

    def test_requires_option_reaches_ssh_argv(self, subprocess_shim):
        # Arrange
        subprocess_shim.install(
            "ssh", rc=0, stdout="__SCITEX_SSH_PROBE_REACHABLE__\nno\n"
        )
        runner = CliRunner()
        # Act
        runner.invoke(probe_cmd, ["spartan", "--requires", "apptainer"])
        # Assert
        assert "apptainer" in subprocess_shim.argv("ssh")[1]


def _run_attach(host, *, bin_dir):
    """Run `python -m scitex_ssh attach <host>` as a real subprocess.

    attach() calls os.execvp(["ssh", "-t", host]) which replaces the
    child process — running in-process via CliRunner would replace
    pytest itself. A real subprocess with a fake `ssh` on $PATH lets the
    execvp succeed against the fake and surfaces the fake's exit code.
    """
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        [sys.executable, "-m", "scitex_ssh", "attach", host],
        capture_output=True,
        text=True,
        env=env,
    )


class TestAttachCmd:
    def test_attach_execs_into_ssh_and_returns_its_exit_code(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=0)
        # Act
        proc = _run_attach("myhost", bin_dir=subprocess_shim.bin_dir)
        # Assert
        assert proc.returncode == 0

    def test_attach_passes_host_to_ssh_argv(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("ssh", rc=0)
        # Act
        _run_attach("myhost", bin_dir=subprocess_shim.bin_dir)
        # Assert
        assert subprocess_shim.argv("ssh") == ["-t", "myhost"]


# EOF
